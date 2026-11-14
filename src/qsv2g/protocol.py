"""QSV2G software state machine; no physical EV, grid, or quantum network."""
from __future__ import annotations
import hashlib, math, secrets, threading, time
import numpy as np
from .crypto import (PQCrypto, Traffic, H, mac, require, ct_eq, encode, decode_fields,
                     canon, parse_canon, hkdf_extract, hkdf_expand, ProtocolAbort)
from .quantum import dense_transport_tag
from .resources import new_qss_resource
from .constants import AUTHORITIES, SLOT, LABEL
from .state import EVIntent, EVState

class QSV2G:
    """Single-session strict reference implementation with explicit trusted authority simulation."""
    def __init__(self,crypto=None, seed=2026,L=162,available=None,resource_factory=None):
        self.pqc=crypto or PQCrypto(); self.rng=np.random.default_rng(seed)
        self.available=set(available if available is not None else AUTHORITIES)
        self.L=L; self.log=[]; self.replay_ev=set(); self.replay_cs=set(); self.executed=set()
        self._execution_mutex=threading.Lock()  # in-process single-use START guard
        self.wire_bytes={}  # Message sizes include ciphertext/tag and 96-bit GCM nonce; exclude implied AAD.
        self.reg_ev=secrets.token_bytes(32); self.reg_cs=secrets.token_bytes(32)
        self.pid_master=secrets.token_bytes(32); self.id_ev='ev_internal_reference_001'
        self.csid='CS_DEMO_01'; self.op='CHARGE'
        self.sigkeys={a:self.pqc.sig_keygen() for a in AUTHORITIES}
        # Inject a baseline-specific resource without first preparing and discarding a
        # QSS state. Default behavior is exactly the existing QSS construction.
        self.resource=(resource_factory(L,self.rng) if resource_factory is not None
                       else new_qss_resource(L,self.rng))
        self.t0=int(time.time()); self.stage='NEW'; self._last_mark=time.perf_counter()
    def mark(self,phase, status='PASS', **details):
        now=time.perf_counter()
        self.log.append({'phase':phase,'status':status,'elapsed_ms':round((now-self._last_mark)*1000,3),**details})
        self._last_mark=now
    def register(self):
        require({'A','B'}<=self.available,'UC-A and UC-B required for online registration')
        rA=secrets.token_bytes(16)
        ev_tag=mac(self.reg_ev,'REG',self.id_ev,rA)
        # 32B tag -> 128 Bell-pair encodings, decoded with 2-qubit simulator
        require(ct_eq(dense_transport_tag(ev_tag), mac(self.reg_ev,'REG',self.id_ev,rA)),'EV Bell verification')
        self.pid=mac(self.pid_master,self.id_ev,secrets.token_bytes(16),self.t0+86400)[:16].hex()
        rB=secrets.token_bytes(16)
        cs_tag=mac(self.reg_cs,'CSREG',self.csid,rB)
        require(ct_eq(dense_transport_tag(cs_tag),mac(self.reg_cs,'CSREG',self.csid,rB)),'CS Bell verification')
        self.stage='REGISTERED'; self.mark('registration', bell_pairs_per_entity=128)
    def authenticate(self, tamper_ev=False, tamper_cs=False, op='CHARGE'):
        require(self.stage=='REGISTERED','register first')
        require({'A','B'}<=self.available,'UC-A and UC-B required for online participant validation')
        require(op in ('CHARGE','DISCHARGE'),'invalid requested operation')
        self.op=op  # authenticate the actual operation, not a default that can change later
        self.ne=secrets.token_bytes(16); self.n_c=secrets.token_bytes(16)
        self.ts_e=self.t0; self.ts_c=self.t0
        self.ev_tag=mac(self.reg_ev,'EV_AUTH',self.pid,self.csid,self.op,self.ne,self.ts_e)
        submitted=self.ev_tag
        if tamper_ev: submitted=bytes([submitted[0]^1])+submitted[1:]
        require(abs(int(time.time())-self.ts_e)<=300,'stale EV timestamp')
        require((self.pid,self.ne) not in self.replay_ev,'EV nonce replay')
        require(ct_eq(submitted,mac(self.reg_ev,'EV_AUTH',self.pid,self.csid,self.op,self.ne,self.ts_e)),'EV proof rejected')
        self.replay_ev.add((self.pid,self.ne))
        cs_tag=mac(self.reg_cs,'CS_AUTH',self.csid,self.pid,self.op,self.ne,self.n_c,self.ts_c)
        if tamper_cs: cs_tag=bytes([cs_tag[0]^1])+cs_tag[1:]
        require(abs(int(time.time())-self.ts_c)<=300,'stale CS timestamp')
        require((self.csid,self.n_c) not in self.replay_cs,'CS nonce replay')
        require(ct_eq(cs_tag,mac(self.reg_cs,'CS_AUTH',self.csid,self.pid,self.op,self.ne,self.n_c,self.ts_c)),'CS proof rejected')
        self.replay_cs.add((self.csid,self.n_c))
        ua_conf=mac(self.reg_ev,'CS_CONF',self.pid,self.csid,self.op,self.ne,self.n_c,self.ts_c,True)
        require(ct_eq(ua_conf, mac(self.reg_ev,'CS_CONF',self.pid,self.csid,self.op,self.ne,self.n_c,self.ts_c,True)),'EV cannot verify station attestation')
        self.stage='AUTHENTICATED'; self.mark('cross_domain_authentication')
    def establish_session(self,tamper_ev_kem=False):
        require(self.stage=='AUTHENTICATED','authenticate first')
        ek,dk=self.pqc.kem_keygen()
        bind=encode(self.pid,self.csid,self.op,self.ne,self.n_c,self.ts_e,self.ts_c,ek)
        proof=mac(self.reg_ev,'KEM-EV',hashlib.sha256(bind).digest())
        if tamper_ev_kem:
            proof=bytes([proof[0]^1])+proof[1:]
        require(ct_eq(proof,mac(self.reg_ev,'KEM-EV',hashlib.sha256(bind).digest())),'KEM public key not authenticated')
        ct,ss_cs=self.pqc.encaps(ek)
        T=encode(self.pid,self.csid,self.op,self.ne,self.n_c,self.ts_e,self.ts_c,ek,ct)
        transcript_hash=hashlib.sha256(T).digest()
        cs_proof=mac(self.reg_cs,'KEM-CS',transcript_hash)
        require(ct_eq(cs_proof,mac(self.reg_cs,'KEM-CS',transcript_hash)),'KEM ciphertext station authentication failed')
        ua_conf=mac(self.reg_ev,'KEM-CONF',transcript_hash,'ACCEPT')
        require(ct_eq(ua_conf,mac(self.reg_ev,'KEM-CONF',transcript_hash,'ACCEPT')),'KEM authority binding mismatch')
        ss_ev=self.pqc.decaps(dk,ct)
        require(ct_eq(ss_ev,ss_cs),'KEM shared secrets mismatch')
        self.sid=H('QSV2G-SID',T)[:16].hex()
        salt=hashlib.sha256(self.ne+self.n_c).digest()
        prk_e=hkdf_extract(salt,ss_ev); prk_c=hkdf_extract(salt,ss_cs)
        def key(prk,label): return hkdf_expand(prk, label.encode()+transcript_hash,32)
        k_e2c=key(prk_e,'QSV2G-E2C'); k_c2e=key(prk_c,'QSV2G-C2E')
        require(k_e2c != k_c2e,'Directional traffic keys unexpectedly identical')
        k_ev_conf=key(prk_e,'KC-EV'); k_cs_conf=key(prk_c,'KC-CS')
        mu_e=mac(k_ev_conf,'EV-FINISHED',self.sid,transcript_hash)
        require(ct_eq(mu_e,mac(key(prk_c,'KC-EV'),'EV-FINISHED',self.sid,transcript_hash)),'EV key confirmation failed')
        mu_c=mac(k_cs_conf,'CS-FINISHED',self.sid,transcript_hash,mu_e)
        require(ct_eq(mu_c,mac(key(prk_e,'KC-CS'),'CS-FINISHED',self.sid,transcript_hash,mu_e)),'CS key confirmation failed')
        self.e2c=Traffic(k_e2c); self.c2e=Traffic(k_c2e)
        self.stage='SESSION'; self.mark('session_establishment', backend=self.pqc.kind, kem_ciphertext_bytes=len(ct), sid_bytes=len(bytes.fromhex(self.sid)))
        # Ephemeral key material references are not kept as instance attributes.
    def set_ev_intent(self,op='CHARGE',limit_mwh=12000,lifetime_sec=600):
        """Record independent EV consent intent BEFORE the station proposes context."""
        require(self.stage=='SESSION','EV intent must be fixed before context offer')
        require(op in ('CHARGE','DISCHARGE'), 'invalid EV intent operation')
        require(op==self.op,'EV intent operation not authenticated in this session')
        require(type(limit_mwh) is int and limit_mwh>0,'invalid EV intent energy limit')
        require(type(lifetime_sec) is int and lifetime_sec>2,'invalid EV intent lifetime')
        self.ev_state=EVState(EVIntent(
            self.pid,self.csid,self.sid,op,self.ne,self.n_c,self.ts_e,self.ts_c,
            limit_mwh,(self.t0-2,self.t0+lifetime_sec)))
    def authorization_context(self, op='CHARGE', limit_mwh=12000, lifetime_sec=600, tamper_ciphertext=False):
        require(self.stage=='SESSION','session not established')
        require(hasattr(self,'ev_state'),'EV intent not established')
        require(op in ('CHARGE','DISCHARGE') and type(limit_mwh) is int and limit_mwh>0,'invalid operation or energy limit')
        require(op==self.op,'station changed authenticated operation')
        require(type(lifetime_sec) is int and lifetime_sec>2,'invalid validity window')
        self.op=op
        self.limit={'type':'ENERGY','max':int(limit_mwh),'unit':'mWh'}
        self.vld=(self.t0-2,self.t0+int(lifetime_sec))
        self.ctx=(self.pid,self.csid,self.sid,self.op,self.ne,self.n_c,self.ts_e,self.ts_c,self.limit,self.vld)
        mctx=encode(*self.ctx)
        ad=encode('QSV2G-CTX',self.sid,self.csid)
        pkt=self.c2e.encrypt(mctx,ad)
        self.wire_bytes['context_offer']=len(pkt['nonce'])+len(pkt['ciphertext'])
        if tamper_ciphertext:
            pkt['ciphertext']=bytes([pkt['ciphertext'][0]^1])+pkt['ciphertext'][1:]
        ev_received=self.c2e.decrypt(pkt,ad)
        ev_fields=decode_fields(ev_received)
        require(ev_fields==self.ev_state.intent.context(), 'EV intent differs from station context')
        require(self.ev_state.intent.validity[0]<=int(time.time())<=self.ev_state.intent.validity[1], 'context expired at EV')
        self.ev_state.accepted_ac=H('QSV2G-AC',ev_received)
        self.ac=H('QSV2G-AC',mctx)
        require(ct_eq(self.ev_state.accepted_ac,self.ac), 'context digest disagreement')
        self.consent=mac(self.reg_ev,'AUTHZ-CONSENT',self.ev_state.accepted_ac)
        ack={'sid':self.sid,'ac':self.ac,'consent':self.consent}
        ack_pkt=self.e2c.encrypt(canon(ack),encode('QSV2G-CTX-ACK',self.sid))
        self.wire_bytes['context_ack']=len(ack_pkt['nonce'])+len(ack_pkt['ciphertext'])
        require(ct_eq(self.e2c.decrypt(ack_pkt,encode('QSV2G-CTX-ACK',self.sid)),canon(ack)),'EV context ack failed')
        self.stage='CONTEXT'; self.mark('context_agreement', context_hash=self.ac.hex())
    def authority_verify(self, approvals=('A','B','C'), revoked=False, bad_consent=False):
        require(self.stage=='CONTEXT','context missing')
        require({'A','B'}<=self.available,'UC-A and UC-B online validation required (full system not arbitrary-one-outage tolerant)')
        require(self.vld[0]<=int(time.time())<=self.vld[1], 'authorization expired')
        consent=self.consent if not bad_consent else bytes([self.consent[0]^1])+self.consent[1:]
        require(ct_eq(consent,mac(self.reg_ev,'AUTHZ-CONSENT',self.ac)),'UC-A rejected EV consent')
        require(not revoked,'EV revoked')
        require(ct_eq(H('QSV2G-AC',encode(*self.ctx)),self.ac),'context mismatch')
        require(self.resource.state=='UNUSED','QSS resource not available for authorization')
        # Proposal order: coordinator selects unused nu -> authorities approve
        # (authority, AC, nu, decision) -> approved pair atomically reserves nu.
        self.proposed_nu=self.resource.nu
        self.decisions={a:(a in approvals and a in self.available) for a in AUTHORITIES}
        self.approval_records={a:(a,self.ac,self.proposed_nu,self.decisions[a]) for a in AUTHORITIES}
        self.accepted=[a for a in AUTHORITIES if self.decisions[a]]
        require(len(self.accepted)>=2,'fewer than two distinct approvals')
        self.stage='APPROVED'; self.mark('authority_validation', approved=','.join(self.accepted))
    def threshold_reconstruct(self,pair=('A','B'),tamper_share=False):
        require(self.stage=='APPROVED','authority approval missing')
        require(len(pair)==2 and pair[0]!=pair[1] and set(pair)<=set(self.accepted),'not an approved distinct authority pair')
        require(self.resource.state=='UNUSED','resource must be unused')
        require(set(pair)<=self.available,'selected authority offline before reconstruction')
        require(self.resource.nu==self.proposed_nu,'QSS resource proposal changed')
        require(all(self.approval_records[a]==(a,self.ac,self.proposed_nu,True) for a in pair), 'resource not approved by chosen pair')
        self.pair=tuple(pair)
        self.resource.reserve(self.ac,self.pair)
        recovered=self.resource.reconstruct(self.ac,self.pair,self.rng,tamper=tamper_share)
        self.reconstruction_hash=H('QSV2G-REC',self.ac,self.resource.nu,recovered)
        self.stage='RECONSTRUCTED'; self.mark('qss_threshold',pair=''.join(pair),recovered=True, consumed=self.resource.state)
    def issue_token(self,tamper_signature=False):
        require(self.stage=='RECONSTRUCTED','QSS reconstruction missing')
        require(set(self.pair)<=self.available,'selected signer offline before token issuance')
        u,v=self.pair
        statement=('QSV2G-AUTHZ',self.ac,self.sid,self.resource.nu,u,v,self.reconstruction_hash,self.vld,'ACCEPT')
        msg=encode(*statement)
        signatures={a:self.pqc.sign(self.sigkeys[a][1],msg) for a in self.pair}
        if tamper_signature:
            signatures[u]=bytes([signatures[u][0]^1])+signatures[u][1:]
        # UC-B verification; all public keys are trusted/bound to authority identities in simulation.
        require(all(self.pqc.verify(self.sigkeys[a][0],msg,signatures[a]) for a in self.pair),'invalid authority signature')
        self.token={'statement':statement,'signatures':signatures}
        self.stage='TOKEN'; self.mark('authorization_token', signer_count=2, signature_bytes=sum(map(len,signatures.values())))
    def protected_response(self,tamper_response=False, tamper_token_after_collector=False):
        require(self.stage=='TOKEN','no accepted authorization proof')
        require(hasattr(self,'ev_state') and self.ev_state.accepted_ac is not None,'EV has not accepted a context')
        token={'statement':self.token['statement'],'signatures':dict(self.token['signatures'])}
        if tamper_token_after_collector:
            signer=self.pair[0]
            sig=token['signatures'][signer]
            token['signatures'][signer]=bytes([sig[0]^1])+sig[1:]
        resp={'sid':self.sid,'pid':self.pid,'csid':self.csid,'ac':self.ac,
              'op':self.op,'ne':self.ne,'nc':self.n_c,'lim':self.limit,
              'vld':self.vld,'decision':True,'auth_token':token}
        ad=encode('QSV2G-RESP',self.sid,self.csid)
        pkt=self.c2e.encrypt(canon(resp),ad)
        self.wire_bytes['authorization_response']=len(pkt['nonce'])+len(pkt['ciphertext'])
        if tamper_response:
            pkt['ciphertext']=pkt['ciphertext'][:-1]+bytes([pkt['ciphertext'][-1]^1])
        received=parse_canon(self.c2e.decrypt(pkt,ad))
        # EV validates independently from received wire bytes, never from a local CS plaintext.
        intent=self.ev_state.intent
        require(received['sid']==intent.sid and received['pid']==intent.pid and received['csid']==intent.csid,'identity/session mismatch')
        require(received['op']==intent.op and received['ne']==intent.ne and received['nc']==intent.nc,'nonce/op mismatch')
        require(received['lim']==intent.context()[8] and received['vld']==intent.validity
                and ct_eq(received['ac'],self.ev_state.accepted_ac),'EV transaction intent mismatch')
        require(intent.validity[0]<=int(time.time())<=intent.validity[1],'authorization expired at EV')
        require(received['decision'] is True,'EV received a reject response')
        wire_token=received['auth_token']
        statement=wire_token['statement']
        require(len(statement)==9 and statement[0]=='QSV2G-AUTHZ','malformed signed authorization statement')
        require(statement[1]==self.ev_state.accepted_ac and statement[2]==intent.sid
                and isinstance(statement[3],str) and len(statement[3])==24,'signed statement context mismatch')
        # The EV cannot calculate or know h_rec; it can only verify the signed attestation.
        require(isinstance(statement[6],bytes) and len(statement[6])==32 and statement[7]==intent.validity and statement[8]=='ACCEPT','signed statement inconsistency')
        wire_pair=(statement[4],statement[5])
        require(len(set(wire_pair))==2 and all(a in AUTHORITIES for a in wire_pair),'invalid token signers')
        msg=encode(*statement)
        require(all(self.pqc.verify(self.sigkeys[a][0],msg,wire_token['signatures'][a]) for a in wire_pair),'EV token signature invalid')
        ev_token_id=(intent.sid,self.ev_state.accepted_ac,statement[3])
        require(ev_token_id not in self.ev_state.seen_tokens,'EV token replay')
        self.ev_state.seen_tokens.add(ev_token_id)
        require(ev_token_id not in self.executed,'token already executed')
        self.stage='EV_ACCEPTED'; self.mark('ev_token_verification', decision='ACCEPT')
    def execute(self,power_w=1200,seconds=30,tick_s=5):
        # Atomically transition out of EV_ACCEPTED before any START is created.
        # This is only a process-local lock; distributed crash-safe ledgers are
        # outside the simulation's implemented security boundary.
        with self._execution_mutex:
            require(self.stage=='EV_ACCEPTED','EV did not accept token')
            require(all(type(x) in (int,float) and math.isfinite(x) and x>0
                        for x in (power_w,seconds,tick_s)),'invalid simulated power or duration')
            require(self.vld[0]<=int(time.time())<self.vld[1],
                    'validity expired before execution')
            tid=(self.sid,self.ac,self.resource.nu)
            require(tid not in self.executed,'repeat authorization execution')
            self.executed.add(tid)
            self.stage='EXECUTING'
        nx=secrets.token_bytes(16)
        req=encode('QSV2G-START',self.sid,self.ac,self.resource.nu,self.op,nx)
        pkt=self.e2c.encrypt(req,encode('QSV2G-START',self.sid))
        self.wire_bytes['execution_start']=len(pkt['nonce'])+len(pkt['ciphertext'])
        require(ct_eq(self.e2c.decrypt(pkt,encode('QSV2G-START',self.sid)),req),'start message rejected')
        require(self.vld[0]<=int(time.time())<self.vld[1],
                'validity expired before execution')
        # Integer micro-Wh units avoid floating-point serialization or rounding ambiguity.
        energy_uwh=0; limit_uwh=self.limit['max']*1000; steps=0
        logical_time=int(time.time())
        # A modeled energy tick must not cross the authorization expiry.
        elapsed=0.0
        while elapsed<seconds and logical_time<self.vld[1] and energy_uwh<limit_uwh:
            dt=min(tick_s,seconds-elapsed,self.vld[1]-logical_time)
            if dt<=0:break
            increment=round(power_w*dt/3600*1_000_000)
            energy_uwh+=min(increment,limit_uwh-energy_uwh)
            steps+=1; elapsed+=dt; logical_time+=dt
        require(energy_uwh<=limit_uwh,'energy ceiling exceeded')
        self.energy_mwh=energy_uwh/1000
        self.stage='EXECUTED'; self.mark('energy_execution', energy_mwh=self.energy_mwh, ticks=steps, op=self.op)
    def terminate(self, interrupted=False):
        require(self.stage=='EXECUTED','no active or completed execution')
        status='INTERRUPTED' if interrupted else 'COMPLETED'
        record={'sid':self.sid,'ac':self.ac,'nu':self.resource.nu,'op':self.op,
                'status':status,'ended_at':int(time.time()), 'metered_uWh':int(round(self.energy_mwh*1000))}
        ad=encode('QSV2G-TERM',self.sid,self.csid)
        pkt=self.c2e.encrypt(canon(record),ad)
        self.wire_bytes['termination']=len(pkt['nonce'])+len(pkt['ciphertext'])
        require(ct_eq(self.c2e.decrypt(pkt,ad),canon(record)),'termination record rejected')
        self.stage='TERMINATED'; self.mark('termination',status=status)
        return record


def run_demo(crypto=None, pair=('A','B'), seed=2026,L=162,**fault):
    p=QSV2G(crypto=crypto,seed=seed,L=L,available=fault.get('available'))
    try:
        p.register()
        p.authenticate(tamper_ev=fault.get('tamper_ev',False),tamper_cs=fault.get('tamper_cs',False),
                       op=fault.get('op','CHARGE'))
        p.establish_session(tamper_ev_kem=fault.get('tamper_ev_kem',False))
        p.set_ev_intent(op=fault.get('ev_intent_op',fault.get('op','CHARGE')),
                        limit_mwh=fault.get('ev_intent_limit_mwh',fault.get('limit_mwh',12000)),
                        lifetime_sec=fault.get('ev_intent_lifetime_sec',fault.get('lifetime_sec',600)))
        p.authorization_context(op=fault.get('op','CHARGE'),limit_mwh=fault.get('limit_mwh',12000),
                                lifetime_sec=fault.get('lifetime_sec',600),tamper_ciphertext=fault.get('tamper_context',False))
        p.authority_verify(approvals=fault.get('approvals',AUTHORITIES),revoked=fault.get('revoked',False),bad_consent=fault.get('bad_consent',False))
        p.threshold_reconstruct(pair=pair,tamper_share=fault.get('tamper_share',False))
        p.issue_token(tamper_signature=fault.get('tamper_signature',False))
        p.protected_response(tamper_response=fault.get('tamper_response',False),tamper_token_after_collector=fault.get('tamper_token_after_collector',False))
        p.execute()
        p.terminate()
        return p
    except ProtocolAbort as e:
        p.mark(p.stage,'REJECTED',reason=str(e))
        return p
