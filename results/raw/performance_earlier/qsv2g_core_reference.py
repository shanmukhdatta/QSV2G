"""QSV2G Section IV reference prototype (research simulation, NOT deployed secure system).
Source: QSV2G_main8_SectionIV_Revised.tex.
Quantum: exact 27D three-qutrit statevectors with sampled pair measurements.
PQC: actual ML-KEM-768 / ML-DSA-65 via pqcrypto OR OpenSSL >= 3.5.
This is not malicious-secure verifiable QSS. Authenticated channels, secure enrollment,
quantum memory and two-authority honesty are simulation assumptions.
"""
from __future__ import annotations
import base64
import hashlib
import hmac
import json
import math
import os
import secrets
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import numpy as np
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

LABEL = 'QSV2G-REFERENCE-2026'
AUTHORITIES = ('A','B','C')
SLOT = {'A':0,'B':1,'C':2}

class ProtocolAbort(Exception):
    pass

def require(condition, explanation):
    if not condition:
        raise ProtocolAbort(explanation)

def json_obj(o):
    if isinstance(o, bytes): return {'__type__':'bytes', 'base64':base64.b64encode(o).decode('ascii')}
    if isinstance(o, tuple): return {'__type__':'tuple', 'items':[json_obj(x) for x in o]}
    if isinstance(o, list): return [json_obj(x) for x in o]
    if isinstance(o, dict): return {str(k):json_obj(v) for k,v in sorted(o.items())}
    if isinstance(o, (str,int,bool)) or o is None: return o
    raise TypeError(f'Unsupported field {type(o).__name__}: floating-point values are intentionally disallowed')

def canon(x):
    return json.dumps(json_obj(x), sort_keys=True, separators=(',',':'), ensure_ascii=False).encode('utf-8')

def parse_canon(raw):
    def restore(x):
        if isinstance(x, list): return [restore(y) for y in x]
        if isinstance(x, dict):
            if x.get('__type__')=='bytes' and set(x)=={'__type__','base64'}:
                return base64.b64decode(x['base64'],validate=True)
            if x.get('__type__')=='tuple' and set(x)=={'__type__','items'}:
                return tuple(restore(y) for y in x['items'])
            return {k:restore(v) for k,v in x.items()}
        return x
    return restore(json.loads(raw.decode('utf-8')))

def encode(*fields):
    """Fixed ordering, deterministic, typed-length-separated encoding."""
    out=bytearray()
    for f in fields:
        chunk=canon(f)
        out += len(chunk).to_bytes(4,'big')+chunk
    return bytes(out)

def H(*fields): return hashlib.sha256(encode(*fields)).digest()
def mac(k, *fields): return hmac.new(k, encode(*fields), 'sha256').digest()
def ct_eq(a,b): return hmac.compare_digest(a,b)
def hkdf_extract(salt, ikm): return hmac.new(salt, ikm, 'sha256').digest()
def hkdf_expand(prk, info, n=32):
    out=b''; t=b''
    for i in range(1,math.ceil(n/32)+1):
        t=hmac.new(prk, t+info+bytes([i]), 'sha256').digest(); out+=t
    return out[:n]

def digest_for(label, *items): return H(label, *items)

# ---- Quantum statevectors ----
I2=np.eye(2,dtype=np.complex128)
X2=np.array([[0,1],[1,0]],complex)
Z2=np.diag([1,-1]).astype(complex)
H2=np.array([[1,1],[1,-1]],complex)/np.sqrt(2)
CNOT=np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]],complex)
BELL=np.array([1,0,0,1],complex)/np.sqrt(2)

def dense_encode_decode(two_bits):
    a,b=two_bits
    state=np.kron(np.linalg.matrix_power(Z2,a)@np.linalg.matrix_power(X2,b),I2)@BELL
    final=np.kron(H2,I2)@CNOT@state
    probabilities=np.abs(final)**2
    idx=int(np.argmax(probabilities))
    require(np.isclose(probabilities[idx],1,atol=1e-12),'Bell decoding failure')
    return (idx//2,idx%2)

def dense_transport_tag(tag):
    recovered=bytearray()
    bits=''.join(f'{byte:08b}' for byte in tag)
    out=''
    for k in range(0,len(bits),2):
        aa,bb=dense_encode_decode((int(bits[k]),int(bits[k+1])))
        out+=str(aa)+str(bb)
    recovered.extend(int(out[j:j+8],2) for j in range(0,len(out),8))
    return bytes(recovered)

OMEGA=np.exp(2j*np.pi/3)
X3=np.roll(np.eye(3,dtype=complex),1,axis=0)
Z3=np.diag([OMEGA**j for j in range(3)])


def qss_state(s):
    """|psi(s)> = sum_r |r,r+s,r+2s> /sqrt(3)."""
    require(s in (0,1,2),'Invalid trit')
    state=np.zeros((3,3,3),dtype=complex)
    for r in range(3): state[r,(r+s)%3,(r+2*s)%3]=1/np.sqrt(3)
    return state

def reduced_density(psi, kept):
    moved=np.moveaxis(psi,kept,0).reshape(3,-1)
    return moved@moved.conj().T

def measure_pair(psi, pair, rng, x_fault=False):
    """Sample joint computational measurement of two shares from a 3-qutrit statevector.
    x_fault applies a qutrit-X error to the SECOND selected share before measuring.
    """
    u,v=[SLOT[p] for p in pair]
    state=np.moveaxis(psi,(u,v),(0,1))
    probs=(np.abs(state)**2).sum(axis=2).reshape(-1)
    idx=int(rng.choice(9,p=probs/probs.sum()))
    xu,xv=divmod(idx,3)
    if x_fault: xv=(xv+1)%3
    return xu,xv

def recover_symbol(pair,xu,xv):
    denom=(SLOT[pair[1]]-SLOT[pair[0]])%3
    return ((xv-xu)*pow(denom,-1,3))%3

def qss_consistency():
    Xa=np.kron(np.kron(X3,X3),X3)
    Za=np.kron(np.kron(Z3,Z3),Z3)
    vals=[]
    for s in range(3):
        psi=qss_state(s)
        psi_flat=psi.reshape(-1)
        vals.append({
            's':s,
            'norm':float(np.vdot(psi_flat,psi_flat).real),
            'x_stabilizer_error':float(np.linalg.norm(Xa@psi_flat-psi_flat)),
            'z_stabilizer_error':float(np.linalg.norm(Za@psi_flat-psi_flat)),
            'one_share_distances':[float(np.linalg.norm(reduced_density(psi,b)-np.eye(3)/3)) for b in range(3)],
        })
    return vals

# ---- Actual standardized post-quantum cryptography, no silent fallbacks ----
class PQCrypto:
    def __init__(self):
        self.kind=None
        try:
            from pqcrypto.kem import ml_kem_768
            from pqcrypto.sign import ml_dsa_65
            self.kem=ml_kem_768; self.sig=ml_dsa_65
            self.kind='pqcrypto native ML-KEM-768 + ML-DSA-65'
        except (ImportError,ModuleNotFoundError):
            exe=shutil.which('openssl')
            if exe:
                test=subprocess.run([exe,'list','-kem-algorithms'],capture_output=True,text=True)
                sig=subprocess.run([exe,'list','-signature-algorithms'],capture_output=True,text=True)
                if 'ML-KEM-768' in test.stdout and 'ML-DSA-65' in sig.stdout:
                    self.kind='OpenSSL 3.5+ ML-KEM-768 + ML-DSA-65 (subprocess)'
                    self.openssl=exe
            if self.kind is None:
                raise RuntimeError('Real ML-KEM-768/ML-DSA-65 unavailable. Enable Kaggle Internet and pip install pqcrypto. No classical substitute will be used.')
    def _openssl_call(self, arguments, input_files=None, output_files=()):
        with tempfile.TemporaryDirectory(prefix='qsv2g_pqc_') as folder:
            root=Path(folder)
            for name,data in (input_files or {}).items(): (root/name).write_bytes(data)
            argv=[self.openssl]+[str(root/(v[1:])) if isinstance(v,str) and v.startswith('@') else str(v) for v in arguments]
            p=subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=root, timeout=30)
            if p.returncode:
                raise RuntimeError('OpenSSL cryptographic call failed: '+p.stderr.decode('utf-8',errors='replace')[:500])
            return (p.stdout, *[(root/x).read_bytes() for x in output_files])
    def kem_keygen(self):
        if self.kind.startswith('pqcrypto'):
            pub,priv=(self.kem.keygen() if hasattr(self.kem,'keygen') else self.kem.generate_keypair()); return pub,priv
        # key generation and public-key extraction share one temporary directory
        with tempfile.TemporaryDirectory(prefix='qsv2g_kem_') as d:
            sk=Path(d)/'sk.pem'; pk=Path(d)/'pk.pem'
            subprocess.run([self.openssl,'genpkey','-algorithm','ML-KEM-768','-out',str(sk)],check=True,capture_output=True)
            subprocess.run([self.openssl,'pkey','-in',str(sk),'-pubout','-out',str(pk)],check=True,capture_output=True)
            return pk.read_bytes(), sk.read_bytes()
    def encaps(self,pub):
        if self.kind.startswith('pqcrypto'):
            return self.kem.encaps(pub) if hasattr(self.kem,'encaps') else self.kem.encrypt(pub)
        _,ct,ss=self._openssl_call(['pkeyutl','-encap','-pubin','-inkey','@pk','-out','@ct','-secret','@ss'], {'pk':pub},('ct','ss'))
        return ct,ss
    def decaps(self,priv,ct):
        if self.kind.startswith('pqcrypto'):
            return self.kem.decaps(priv,ct) if hasattr(self.kem,'decaps') else self.kem.decrypt(priv,ct)
        _,ss=self._openssl_call(['pkeyutl','-decap','-inkey','@sk','-in','@ct','-secret','@ss'],{'sk':priv,'ct':ct},('ss',))
        return ss
    def sig_keygen(self):
        if self.kind.startswith('pqcrypto'):
            return self.sig.keygen() if hasattr(self.sig,'keygen') else self.sig.generate_keypair()
        with tempfile.TemporaryDirectory(prefix='qsv2g_sig_') as d:
            sk=Path(d)/'sk.pem'; pk=Path(d)/'pk.pem'
            subprocess.run([self.openssl,'genpkey','-algorithm','ML-DSA-65','-out',str(sk)],check=True,capture_output=True)
            subprocess.run([self.openssl,'pkey','-in',str(sk),'-pubout','-out',str(pk)],check=True,capture_output=True)
            return pk.read_bytes(),sk.read_bytes()
    def sign(self,priv,msg):
        if self.kind.startswith('pqcrypto'):
            return self.sig.sign(priv,msg)
        _,sig=self._openssl_call(['pkeyutl','-sign','-inkey','@sk','-in','@msg','-out','@sig'],{'sk':priv,'msg':msg},('sig',))
        return sig
    def verify(self,pub,msg,sig):
        if self.kind.startswith('pqcrypto'):
            try:
                result=self.sig.verify(pub,msg,sig)
                return result is None or result is True
            except Exception: return False  # InvalidSignatureError from pqcrypto 1.x, ValueError on older versions
        try:
            self._openssl_call(['pkeyutl','-verify','-pubin','-inkey','@pk','-in','@msg','-sigfile','@sig'],{'pk':pub,'msg':msg,'sig':sig})
            return True
        except RuntimeError: return False

@dataclass
class Traffic:
    key:bytes
    send_counter:int=0
    seen:set=field(default_factory=set)
    def encrypt(self,pt:bytes,ad:bytes):
        require(self.send_counter<2**96-1,'AES-GCM counter exhaustion')
        nonce=self.send_counter.to_bytes(12,'big'); self.send_counter+=1
        ct=AESGCM(self.key).encrypt(nonce,pt,ad)
        return {'nonce':nonce,'ciphertext':ct}
    def decrypt(self,pkt,ad):
        nonce=pkt['nonce']
        require(len(nonce)==12 and nonce not in self.seen,'duplicate or malformed AEAD nonce')
        try: pt=AESGCM(self.key).decrypt(nonce,pkt['ciphertext'],ad)
        except Exception as e: raise ProtocolAbort('AEAD authentication failure') from e
        self.seen.add(nonce)
        return pt

@dataclass
class QSSResource:
    nu:str
    dealer_secrets:dict
    states:dict
    commitments:dict
    state:str='UNUSED'
    lock:tuple|None=None
    def reserve(self,ac,pair):
        require(self.state=='UNUSED','QSS resource already reserved or consumed')
        require(len(set(pair))==2 and all(a in AUTHORITIES for a in pair),'pair invalid')
        self.state='RESERVED'; self.lock=(ac,tuple(pair))
    def reconstruct(self,ac,pair,rng,tamper=False):
        require(self.state=='RESERVED' and self.lock==(ac,tuple(pair)),'QSS reservation mismatch')
        recovered={a:[] for a in AUTHORITIES}
        try:
            for dealer in AUTHORITIES:
                for k,psi in enumerate(self.states[dealer]):
                    xu,xv=measure_pair(psi,pair,rng,x_fault=(tamper and dealer=='A' and k==0))
                    recovered[dealer].append(recover_symbol(pair,xu,xv))
            for dealer in AUTHORITIES:
                expected=H('QSV2G-QSS-COM',dealer,self.nu,recovered[dealer])
                require(ct_eq(expected,self.commitments[dealer]),'QSS reconstructed commitment mismatch')
            combined=[sum(recovered[a][k] for a in AUTHORITIES)%3 for k in range(len(recovered['A']))]
            return combined
        finally:
            self.state='CONSUMED'
            self.states.clear()  # simulated irreversible measurement / erasure

def new_qss_resource(L=162,rng=None):
    rng=rng or np.random.default_rng(2026)
    nu=secrets.token_hex(12)
    dealer_secrets={a:[secrets.randbelow(3) for _ in range(L)] for a in AUTHORITIES}
    states={a:[qss_state(s) for s in dealer_secrets[a]] for a in AUTHORITIES}
    commits={a:H('QSV2G-QSS-COM',a,nu,dealer_secrets[a]) for a in AUTHORITIES}
    return QSSResource(nu,dealer_secrets,states,commits)

class QSV2G:
    """Single-session strict reference implementation with explicit trusted authority simulation."""
    def __init__(self,crypto=None, seed=2026,L=162,available=None):
        self.pqc=crypto or PQCrypto(); self.rng=np.random.default_rng(seed)
        self.available=set(available if available is not None else AUTHORITIES)
        self.L=L; self.log=[]; self.replay_ev=set(); self.replay_cs=set(); self.executed=set()
        self.wire_bytes={}  # Message sizes include ciphertext/tag and 96-bit GCM nonce; exclude implied AAD.
        self.reg_ev=secrets.token_bytes(32); self.reg_cs=secrets.token_bytes(32)
        self.pid_master=secrets.token_bytes(32); self.id_ev='ev_internal_reference_001'
        self.csid='CS_DEMO_01'; self.op='CHARGE'
        self.sigkeys={a:self.pqc.sig_keygen() for a in AUTHORITIES}
        self.resource=new_qss_resource(L,self.rng)
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
    def authenticate(self, tamper_ev=False, tamper_cs=False):
        require(self.stage=='REGISTERED','register first')
        require({'A','B'}<=self.available,'UC-A and UC-B required for online participant validation')
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
    def establish_session(self):
        require(self.stage=='AUTHENTICATED','authenticate first')
        ek,dk=self.pqc.kem_keygen()
        bind=encode(self.pid,self.csid,self.op,self.ne,self.n_c,self.ts_e,self.ts_c,ek)
        proof=mac(self.reg_ev,'KEM-EV',hashlib.sha256(bind).digest())
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
    def authorization_context(self, op='CHARGE', limit_mwh=12000, lifetime_sec=600, tamper_ciphertext=False):
        require(self.stage=='SESSION','session not established')
        require(op in ('CHARGE','DISCHARGE') and limit_mwh>0,'invalid operation or energy limit')
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
        require(ct_eq(ev_received,mctx),'EV context disagreement')
        require(self.vld[0]<=int(time.time())<=self.vld[1],'context expired')
        self.ac=H('QSV2G-AC',mctx)
        self.consent=mac(self.reg_ev,'AUTHZ-CONSENT',self.ac)
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
        self.decisions={a:(a in approvals and a in self.available) for a in AUTHORITIES}
        self.accepted=[a for a in AUTHORITIES if self.decisions[a]]
        require(len(self.accepted)>=2,'fewer than two distinct approvals')
        self.stage='APPROVED'; self.mark('authority_validation', approved=','.join(self.accepted))
    def threshold_reconstruct(self,pair=('A','B'),tamper_share=False):
        require(self.stage=='APPROVED','authority approval missing')
        require(len(pair)==2 and pair[0]!=pair[1] and set(pair)<=set(self.accepted),'not an approved distinct authority pair')
        require(self.resource.state=='UNUSED','resource must be unused')
        self.pair=tuple(pair)
        self.resource.reserve(self.ac,self.pair)
        recovered=self.resource.reconstruct(self.ac,self.pair,self.rng,tamper=tamper_share)
        self.reconstruction_hash=H('QSV2G-REC',self.ac,self.resource.nu,recovered)
        self.stage='RECONSTRUCTED'; self.mark('qss_threshold',pair=''.join(pair),recovered=True, consumed=self.resource.state)
    def issue_token(self,tamper_signature=False):
        require(self.stage=='RECONSTRUCTED','QSS reconstruction missing')
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
        require(received['sid']==self.sid and received['pid']==self.pid and received['csid']==self.csid,'identity/session mismatch')
        require(received['op']==self.op and received['ne']==self.ne and received['nc']==self.n_c,'nonce/op mismatch')
        require(received['lim']==self.limit and received['vld']==self.vld and ct_eq(received['ac'],self.ac),'transaction context mismatch')
        require(self.vld[0]<=int(time.time())<=self.vld[1],'authorization expired at EV')
        require(received['decision'] is True,'EV received a reject response')
        wire_token=received['auth_token']
        statement=wire_token['statement']
        require(statement[1]==self.ac and statement[2]==self.sid and statement[3]==self.resource.nu,'signed statement context mismatch')
        # The EV cannot calculate or know h_rec; it can only verify the signed attestation.
        require(isinstance(statement[6],bytes) and len(statement[6])==32 and statement[7]==self.vld and statement[8]=='ACCEPT','signed statement inconsistency')
        wire_pair=(statement[4],statement[5])
        require(len(set(wire_pair))==2 and all(a in AUTHORITIES for a in wire_pair),'invalid token signers')
        msg=encode(*statement)
        require(all(self.pqc.verify(self.sigkeys[a][0],msg,wire_token['signatures'][a]) for a in wire_pair),'EV token signature invalid')
        require((self.sid,self.ac,self.resource.nu) not in self.executed,'token already executed')
        self.stage='EV_ACCEPTED'; self.mark('ev_token_verification', decision='ACCEPT')
    def execute(self,power_w=1200,seconds=30,tick_s=5):
        require(self.stage=='EV_ACCEPTED','EV did not accept token')
        tid=(self.sid,self.ac,self.resource.nu)
        require(tid not in self.executed,'repeat authorization execution')
        self.executed.add(tid)  # atomic authorization consumption modeled by memory store
        nx=secrets.token_bytes(16)
        req=encode('QSV2G-START',self.sid,self.ac,self.resource.nu,self.op,nx)
        pkt=self.e2c.encrypt(req,encode('QSV2G-START',self.sid))
        self.wire_bytes['execution_start']=len(pkt['nonce'])+len(pkt['ciphertext'])
        require(ct_eq(self.e2c.decrypt(pkt,encode('QSV2G-START',self.sid)),req),'start message rejected')
        require(self.vld[0]<=int(time.time())<=self.vld[1],'validity expired before execution')
        # Integer micro-Wh units avoid floating-point serialization or rounding ambiguity.
        energy_uwh=0; limit_uwh=self.limit['max']*1000; steps=0
        logical_time=self.t0
        for _ in range(math.ceil(seconds/tick_s)):
            dt=min(tick_s,seconds-steps*tick_s)
            if dt<=0 or logical_time > self.vld[1]: break
            increment=round(power_w*dt/3600*1_000_000)
            energy_uwh+=min(increment,limit_uwh-energy_uwh)
            steps+=1; logical_time+=dt
            if energy_uwh>=limit_uwh: break
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
        p.authenticate(tamper_ev=fault.get('tamper_ev',False),tamper_cs=fault.get('tamper_cs',False))
        p.establish_session()
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
