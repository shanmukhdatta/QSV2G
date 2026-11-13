"""QSV2G Stage 05 software-only experiment runner (E1--E4).

Usage: python experiments/stage05/runner.py --experiment all --smoke --out /tmp/qsv2g-stage05
No physical quantum hardware, networking or V2G charger is emulated. Experiments
produce observations, NOT a security proof or established quantum advantage.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import importlib.metadata
import json
import math
import os
import platform
import random
import secrets
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from qsv2g_core import (QSV2G, PQCrypto, ProtocolAbort, QSSResource, AUTHORITIES,
                        SLOT, H, recover_symbol, run_demo)

PAIRS=(('A','B'),('A','C'),('B','C'))
CHANNELS=('x','dephase','depolarize','erasure','combined')


def dump_rows(path, rows, columns=None):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    rows=list(rows)
    columns=columns or (list(rows[0]) if rows else ['empty'])
    with path.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=columns,extrasaction='ignore');writer.writeheader();writer.writerows(rows)


def manifest(out,experiment,params):
    try: revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,stderr=subprocess.DEVNULL,text=True).strip()
    except (OSError,subprocess.CalledProcessError):revision='UNAVAILABLE: supply pinned git SHA manually'
    try:corehash=hashlib.sha256((ROOT/'src/qsv2g_core.py').read_bytes()).hexdigest()
    except OSError:corehash=None
    meta=dict(utc=datetime.now(timezone.utc).isoformat(),experiment=experiment,
        git_revision=revision,core_sha256=corehash,python=sys.version,platform=platform.platform(),
        processor=platform.processor(),cpu_count=os.cpu_count(),params=params,
        limitations=['single Python process','ideal statevector/analytical channel model',
            'no real quantum network or EV hardware','no cryptographic security proof'])
    (Path(out)/'manifest.json').write_text(json.dumps(meta,indent=2,default=str))


@dataclass
class ClassicalResource:
    """Same 3-dealer/2-holder affine mod-3 secret sharing and commitments as QSS outcomes.

    Independent dealer secrets and masks are sampled with secrets, not benchmark seeds.
    No quantum states. Preparation work is offline by construction.
    """
    nu:str
    dealer_secrets:dict
    shares:dict
    commitments:dict
    state:str='UNUSED'
    lock:tuple|None=None
    mutex:object=field(default_factory=threading.Lock,repr=False)

    @classmethod
    def prepare(cls,L):
        nu=secrets.token_hex(12)
        vectors={a:[secrets.randbelow(3) for _ in range(L)] for a in AUTHORITIES}
        shares={a:[] for a in AUTHORITIES}
        for dealer in AUTHORITIES:
            for s in vectors[dealer]:
                r=secrets.randbelow(3)
                shares[dealer].append((r,(r+s)%3,(r+2*s)%3))
        commitments={a:H('QSV2G-QSS-COM',a,nu,vectors[a]) for a in AUTHORITIES}
        return cls(nu,vectors,shares,commitments)

    def reserve(self,ac,pair):
        with self.mutex:
            if self.state!='UNUSED': raise ProtocolAbort('classical shares already reserved')
            if len(pair)!=2 or len(set(pair))!=2 or not set(pair)<=set(AUTHORITIES):
                raise ProtocolAbort('invalid authority pair')
            self.state='RESERVED';self.lock=(ac,tuple(pair))

    def reconstruct(self,ac,pair,rng,tamper=False):
        with self.mutex:
            if self.state!='RESERVED' or self.lock!=(ac,tuple(pair)):
                raise ProtocolAbort('classical reservation mismatch')
            self.state='MEASURING'
        try:
            reconstructed={}
            for dealer in AUTHORITIES:
                vals=[]
                for index,triplet in enumerate(self.shares[dealer]):
                    x,y=(triplet[SLOT[a]] for a in pair)
                    if tamper and dealer=='A' and index==0:y=(y+1)%3
                    vals.append(recover_symbol(pair,x,y))
                if H('QSV2G-QSS-COM',dealer,self.nu,vals)!=self.commitments[dealer]:
                    raise ProtocolAbort('classical sharing commitment mismatch')
                reconstructed[dealer]=vals
            return [sum(reconstructed[a][i] for a in AUTHORITIES)%3
                    for i in range(len(reconstructed['A']))]
        finally:
            with self.mutex:
                self.state='CONSUMED';self.shares.clear();self.dealer_secrets.clear()


class QuorumResource:
    """Distinct two-signature quorum without a share-reconstruction requirement.

    This comparator is NOT security-equivalent to either sharing variant.
    """
    def __init__(self):
        self.nu=secrets.token_hex(12);self.state='UNUSED';self.lock=None
        self.commitments={};self.dealer_secrets={};self.states={}
        self.mutex=threading.Lock()

    def reserve(self,ac,pair):
        with self.mutex:
            if self.state!='UNUSED' or len(set(pair))!=2 or not set(pair)<=set(AUTHORITIES):
                raise ProtocolAbort('invalid quorum reservation')
            self.state='RESERVED';self.lock=(ac,tuple(pair))

    def reconstruct(self,ac,pair,rng,tamper=False):
        with self.mutex:
            if self.state!='RESERVED' or self.lock!=(ac,tuple(pair)):
                raise ProtocolAbort('quorum state mismatch')
            self.state='CONSUMED'
        if tamper: raise ProtocolAbort('quorum has no shares to tamper')
        # Explicitly a quorum attestation marker, not simulated secret recovery.
        return ['NO_SECRET_RECOVERY']


def make_protocol(variant,crypto,L,seed,pair):
    t0=time.perf_counter();p=QSV2G(crypto=crypto,L=L,seed=seed)
    if variant=='CLASSICAL_SHARING':p.resource=ClassicalResource.prepare(L)
    elif variant=='QUORUM':p.resource=QuorumResource()
    elif variant!='QSS':raise ValueError(variant)
    return p,(time.perf_counter()-t0)*1000


def full_transaction(variant,crypto,L,pair,seed):
    p,pre_ms=make_protocol(variant,crypto,L,seed,pair)
    start=time.perf_counter()
    p.register();p.authenticate();p.establish_session();p.set_ev_intent()
    p.authorization_context();p.authority_verify(approvals=pair)
    online_start=time.perf_counter()
    p.threshold_reconstruct(pair=pair);p.issue_token();p.protected_response()
    online_ms=(time.perf_counter()-online_start)*1000
    p.execute();p.terminate()
    total_ms=(time.perf_counter()-start)*1000
    if p.stage!='TERMINATED':raise AssertionError(p.stage)
    return dict(variant=variant,pair=''.join(pair),L=L,status=p.stage,
        preparation_ms=pre_ms,authorization_ms=online_ms,full_software_ms=total_ms,
        selected_packet_bytes=sum(p.wire_bytes.values()),
        signature_count=2,analytical_qutrit_storage=(9*L if variant=='QSS' else 0),
        analytical_remote_qutrits=(6*L if variant=='QSS' else 0),
        resource_consumed=p.resource.state)


def e1_worker(out,smoke=False,seed=2026,block=0):
    """One independent Python process per block; fresh PQC backend and interpreter."""
    crypto=PQCrypto()
    variants=('QUORUM','CLASSICAL_SHARING','QSS')
    lengths=(9,) if smoke else (9,27,81,162)
    repeats=2 if smoke else 100
    order=random.Random(seed+block)
    rows=[]
    for L in lengths:
        work=[(variant,pair,k) for k in range(repeats)
              for pair in PAIRS for variant in variants]
        order.shuffle(work)
        for variant,pair,k in work:
            try:record=full_transaction(variant,crypto,L,pair,seed+block*10000+k)
            except ProtocolAbort as exc:
                record=dict(variant=variant,pair=''.join(pair),L=L,status='REJECTED',reason=str(exc))
            record.update(block=block,trial=k,process_pid=os.getpid())
            rows.append(record)
    dump_rows(Path(out)/f'block_{block:02d}.csv',rows)
    return rows


def e1(out,smoke=False,seed=2026):
    """Orchestrate distinct processes; preserve block IDs for clustered statistics."""
    blocks=1 if smoke else 5
    rows=[]
    for block in range(blocks):
        proc=subprocess.run([sys.executable,str(Path(__file__).resolve()),
            '--experiment','e1-worker','--out',str(out),'--seed',str(seed),
            '--block',str(block)]+(['--smoke'] if smoke else []),
            capture_output=True,text=True)
        if proc.returncode:
            raise RuntimeError(f'E1 worker {block} failed: {proc.stderr[-3000:]}')
        with (Path(out)/f'block_{block:02d}.csv').open(newline='',encoding='utf-8') as f:
            rows.extend(csv.DictReader(f))
    dump_rows(Path(out)/'e1_trials.csv',rows)
    manifest(out,'E1',dict(smoke=smoke,seed=seed,blocks=blocks,
        repeats_per_pair=(2 if smoke else 100),lengths=((9,) if smoke else (9,27,81,162)),
        backend='Genuine PQCrypto; each block from a separate Python process',
        variants=('QUORUM','CLASSICAL_SHARING','QSS')))
    return rows


def build_to_token(crypto=None,L=3,pair=('A','B')):
    p=QSV2G(crypto=crypto or PQCrypto(),L=L)
    p.register();p.authenticate();p.establish_session();p.set_ev_intent()
    p.authorization_context();p.authority_verify();p.threshold_reconstruct(pair=pair);p.issue_token()
    return p


def e2(out,smoke=False,seed=2026):
    """Deterministic adversarial traces using genuine backend; Hypothesis separate tests.

    Classify each outcome; a rejected attack is NOT an empirical forgery probability.
    """
    crypto=PQCrypto();rows=[]
    scenarios=('consent_operation','consent_limit','consent_expiry','token_ac',
               'token_signature','token_replay','invalid_pair','wrong_resource',
               'expired_token','tampered_kem','legitimate_charge','legitimate_discharge')
    for pair in PAIRS:
        for name in scenarios:
            p=None
            try:
                if name in ('consent_operation','consent_limit','consent_expiry'):
                    kwargs={'ev_intent_op':'DISCHARGE'} if name=='consent_operation' else (
                        {'ev_intent_limit_mwh':9999} if name=='consent_limit' else {'ev_intent_lifetime_sec':300})
                    p=run_demo(crypto=crypto,L=3,pair=pair,**kwargs)
                elif name=='tampered_kem':p=run_demo(crypto=crypto,L=3,pair=pair,tamper_ev_kem=True)
                elif name=='legitimate_charge':p=run_demo(crypto=crypto,L=3,pair=pair,op='CHARGE')
                elif name=='legitimate_discharge':p=run_demo(crypto=crypto,L=3,pair=pair,op='DISCHARGE')
                elif name=='invalid_pair':
                    p=QSV2G(crypto=crypto,L=3);p.register();p.authenticate();p.establish_session();
                    p.set_ev_intent();p.authorization_context();p.authority_verify();p.threshold_reconstruct(pair=('A','A'))
                elif name=='wrong_resource':
                    p=QSV2G(crypto=crypto,L=3);p.register();p.authenticate();p.establish_session();
                    p.set_ev_intent();p.authorization_context();p.authority_verify();p.proposed_nu='forged';p.threshold_reconstruct(pair=pair)
                else:
                    p=build_to_token(crypto=crypto,L=3,pair=pair)
                    if name=='token_ac':p.ac=b'X'*32
                    if name=='token_signature':
                        signer=pair[0];s=p.token['signatures'][signer]
                        p.token['signatures'][signer]=bytes([s[0]^1])+s[1:]
                    if name=='expired_token':
                        import unittest.mock
                        with unittest.mock.patch('qsv2g_core.time.time',return_value=p.ev_state.intent.validity[1]+1):
                            p.protected_response()
                    else:p.protected_response()
                    if name=='token_replay':
                        p.stage='TOKEN';p.protected_response()
                outcome='ACCEPTED' if p.stage in ('TERMINATED','EV_ACCEPTED') else 'REJECTED'
                why=p.log[-1].get('reason','') if p and p.log else ''
            except ProtocolAbort as exc:
                outcome='REJECTED';why=str(exc)
            expected='ACCEPTED' if name.startswith('legitimate_') else 'REJECTED'
            rows.append(dict(pair=''.join(pair),scenario=name,expected=expected,
                outcome=outcome,match=(outcome==expected),reason=why,
                backend=crypto.kind))
    dump_rows(Path(out)/'e2_cases.csv',rows)
    manifest(out,'E2',dict(smoke=smoke,seed=seed,crypto=crypto.kind,scenario_count=len(rows),
        limitation='Hand-selected scenarios; Hypothesis generated sequences in separate test file'))
    return rows


def error_symbol(s,pair,channel,p,rng):
    """Return sampled reconstruction or None for erasure under ideal code measurement.

    X is a +1 shift of the second selected holder, dephasing changes phases
    only, depolarizing replaces that holder by uniform trit with probability p.
    Combined: independent X and depolarizing maps on the same selected holder.
    Ideal pair outcomes use a common uniform r; quantum coherence/fidelity is
    NOT simulated by this optimized classical measurement sampler.
    """
    r=int(rng.integers(0,3)); v=[(r+SLOT[a]*s)%3 for a in AUTHORITIES]
    first=v[SLOT[pair[0]]]; second=v[SLOT[pair[1]]]
    if channel=='erasure' and rng.random()<p:return None
    if channel=='x' and rng.random()<p:second=(second+1)%3
    if channel=='depolarize' and rng.random()<p:second=int(rng.integers(0,3))
    if channel=='combined':
        if rng.random()<p:second=(second+1)%3
        if rng.random()<p:second=int(rng.integers(0,3))
    return recover_symbol(pair,first,second)


def q_probability(channel,p):
    if channel in ('x','erasure'):return 1-p
    if channel=='dephase':return 1.0
    if channel=='depolarize':return 1-2*p/3
    if channel=='combined':return (1-p)**2+p/3
    raise ValueError(channel)


def vector_trial(L,pair,channel,p,rng):
    # Simulate all three dealer vectors, independently; verify all commitments.
    nu=secrets.token_hex(12)
    recovered={};erased=False
    for dealer in AUTHORITIES:
        original=[int(i) for i in rng.integers(0,3,size=L)]
        commitment=H('QSV2G-QSS-COM',dealer,nu,original)
        result=[]
        for s in original:
            sample=error_symbol(s,pair,channel,p,rng)
            if sample is None:
                erased=True;break
            result.append(sample)
        if erased:break
        recovered[dealer]=(result,H('QSV2G-QSS-COM',dealer,nu,result)==commitment)
    if erased:return 'ERASURE_ABORT'
    if not all(v[1] for v in recovered.values()):return 'COMMITMENT_REJECT'
    return 'COMMITMENT_GATE_ELIGIBLE'


class NoisyResource(QSSResource):
    """Modelled channel injected at actual resource reconstruction in full workflow."""
    def __init__(self,clean,channel,p):
        super().__init__(clean.nu,clean.dealer_secrets,clean.states,clean.commitments)
        self.channel=channel;self.p=p

    def reconstruct(self,ac,pair,rng,tamper=False):
        with self._mutex:
            if self.state!='RESERVED' or self.lock!=(ac,tuple(pair)):
                raise ProtocolAbort('QSS reservation mismatch')
            self.state='MEASURING'
        try:
            recovered={}
            for dealer in AUTHORITIES:
                vals=[]
                for secret in self.dealer_secrets[dealer]:
                    s=error_symbol(secret,pair,self.channel,self.p,rng)
                    if s is None:raise ProtocolAbort('flagged erasure')
                    vals.append(s)
                if H('QSV2G-QSS-COM',dealer,self.nu,vals)!=self.commitments[dealer]:
                    raise ProtocolAbort('QSS reconstructed commitment mismatch')
                recovered[dealer]=vals
            return [sum(recovered[a][i] for a in AUTHORITIES)%3 for i in range(len(recovered['A']))]
        finally:
            with self._mutex:
                self.state='CONSUMED';self.states.clear();self.dealer_secrets.clear()


def actual_noisy_token_trial(L,pair,channel,p,crypto,seed):
    p0=QSV2G(crypto=crypto,L=L,seed=seed)
    p0.resource=NoisyResource(p0.resource,channel,p)
    try:
        p0.register();p0.authenticate();p0.establish_session();p0.set_ev_intent()
        p0.authorization_context();p0.authority_verify(approvals=pair)
        p0.threshold_reconstruct(pair=pair);p0.issue_token();p0.protected_response()
        return 'ACCEPTED_AT_EV'
    except ProtocolAbort as exc:
        if 'erasure' in str(exc):return 'ERASURE_ABORT'
        if 'commitment mismatch' in str(exc):return 'COMMITMENT_REJECT'
        if 'token' in str(exc) or 'signature' in str(exc):return 'TOKEN_VERIFY_REJECT'
        return 'OTHER_ABORT'


def e3(out,smoke=False,seed=2026):
    lengths=(9,) if smoke else (9,27,81,162)
    levels=(0.0,0.01) if smoke else (0.,.001,.005,.01,.03)
    attempts=4 if smoke else 1000
    rng=np.random.default_rng(seed)
    rows=[];summary=[]
    for L in lengths:
        for pair in PAIRS:
            for channel in CHANNELS:
                for p in levels:
                    counts={k:0 for k in ('COMMITMENT_GATE_ELIGIBLE','COMMITMENT_REJECT','ERASURE_ABORT')}
                    for attempt in range(attempts):
                        result=vector_trial(L,pair,channel,p,rng)
                        counts[result]+=1
                        rows.append(dict(L=L,pair=''.join(pair),channel=channel,p=p,
                                         trial=attempt,outcome=result,seed=seed))
                    q=q_probability(channel,p)
                    summary.append(dict(L=L,pair=''.join(pair),channel=channel,p=p,
                        trials=attempts,eligible=counts['COMMITMENT_GATE_ELIGIBLE'],
                        rejected=counts['COMMITMENT_REJECT'],erasure=counts['ERASURE_ABORT'],
                        predicted_eligible=q**(3*L)))
        dump_rows(Path(out)/'e3_vector_trials.csv',rows)
    dump_rows(Path(out)/'e3_vector_trials.csv',rows)
    dump_rows(Path(out)/'e3_summary.csv',summary)
    # Separate genuine endpoint checks with exact per-condition denominators.
    crypto=PQCrypto();token_rows=[]
    trial_count=1 if smoke else 20
    for pair in PAIRS:
        for channel in CHANNELS:
            for p in levels:
                for index in range(trial_count):
                    outcome=actual_noisy_token_trial(lengths[0],pair,channel,p,crypto,seed+index)
                    token_rows.append(dict(L=lengths[0],pair=''.join(pair),channel=channel,p=p,
                        trial=index,outcome=outcome,backend=crypto.kind))
    dump_rows(Path(out)/'e3_token_trials.csv',token_rows)
    manifest(out,'E3',dict(smoke=smoke,seed=seed,lengths=lengths,levels=levels,
        trials_per_vector_condition=attempts,token_trials_per_condition=trial_count,
        token_L=lengths[0],backend=crypto.kind,models=CHANNELS))
    return summary


def staged_protocol(crypto):
    p=QSV2G(crypto=crypto,L=3)
    p.register();p.authenticate();p.establish_session();p.set_ev_intent();p.authorization_context()
    return p


def e4(out,smoke=False,seed=2026):
    crypto=PQCrypto();rows=[]
    cases=('C_OFFLINE_AT_START','A_OFFLINE_AT_START','B_OFFLINE_AT_START',
           'B_OFFLINE_AFTER_APPROVAL','B_OFFLINE_AFTER_RECONSTRUCTION',
           'C_OFFLINE_AFTER_APPROVAL','DUPLICATE_RESERVATION',
           'CONCURRENT_RESERVATION','EXPIRED_BEFORE_EXECUTION','REPEATED_EXECUTION')
    for name in cases:
        p=None;resource_state='NA';fault_injected=True
        try:
            if name.endswith('AT_START'):
                available={'A','B'} if name.startswith('C_') else (
                    {'B','C'} if name.startswith('A_') else {'A','C'})
                p=run_demo(crypto=crypto,L=3,available=available)
                outcome='COMPLETED' if p.stage=='TERMINATED' else 'SAFE_ABORT'
                reason=p.log[-1].get('reason','')
            elif name=='CONCURRENT_RESERVATION':
                from qsv2g_core import new_qss_resource
                resource=new_qss_resource(L=3)
                def task(pair):
                    try:resource.reserve(b'x'*32,pair);return True
                    except ProtocolAbort:return False
                with ThreadPoolExecutor(max_workers=2) as pool:
                    attempts=list(pool.map(task,[('A','B'),('B','C')]))
                outcome='ONE_RESERVATION' if sum(attempts)==1 else 'VIOLATION'
                reason=f'accepted={sum(attempts)}';resource_state=resource.state
            else:
                p=staged_protocol(crypto);p.authority_verify()
                if name=='B_OFFLINE_AFTER_APPROVAL':
                    p.available.remove('B');p.threshold_reconstruct(pair=('A','B'))
                elif name=='B_OFFLINE_AFTER_RECONSTRUCTION':
                    p.threshold_reconstruct(pair=('A','B'));p.available.remove('B');p.issue_token()
                elif name=='C_OFFLINE_AFTER_APPROVAL':
                    p.available.remove('C');p.threshold_reconstruct(pair=('A','B'))
                    p.issue_token();p.protected_response();p.execute();p.terminate()
                elif name=='DUPLICATE_RESERVATION':
                    p.resource.reserve(p.ac,('A','B'));p.resource.reserve(p.ac,('B','C'))
                elif name=='EXPIRED_BEFORE_EXECUTION':
                    p.threshold_reconstruct(pair=('A','B'));p.issue_token();p.protected_response()
                    import unittest.mock
                    with unittest.mock.patch('qsv2g_core.time.time',return_value=p.ev_state.intent.validity[1]+1):p.execute()
                elif name=='REPEATED_EXECUTION':
                    p.threshold_reconstruct(pair=('A','B'));p.issue_token();p.protected_response()
                    p.execute();p.execute()
                outcome='COMPLETED' if p.stage=='TERMINATED' else 'UNEXPECTED_ACCEPT'
                reason=''
            if p:resource_state=p.resource.state
        except ProtocolAbort as exc:
            outcome='SAFE_ABORT';reason=str(exc)
            if p:resource_state=p.resource.state
        rows.append(dict(scenario=name,outcome=outcome,reason=reason,
                         resource_state=resource_state,backend=crypto.kind))
    dump_rows(Path(out)/'e4_failure_matrix.csv',rows)
    manifest(out,'E4',dict(smoke=smoke,seed=seed,scenario_count=len(rows),backend=crypto.kind))
    return rows


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--experiment',choices=('e1','e2','e3','e4','e1-worker','all'),default='all')
    parser.add_argument('--smoke',action='store_true',help='bounded tests before expensive final run')
    parser.add_argument('--seed',type=int,default=2026)
    parser.add_argument('--block',type=int,default=0)
    parser.add_argument('--out',type=Path,default=Path('results/stage05/local'))
    args=parser.parse_args(argv)
    args.out.mkdir(parents=True,exist_ok=True)
    if args.experiment=='e1-worker':
        e1_worker(args.out,args.smoke,args.seed,args.block)
        return
    for experiment in (('e1','e2','e3','e4') if args.experiment=='all' else (args.experiment,)):
        directory=args.out/experiment;directory.mkdir(exist_ok=True)
        result=globals()[experiment](directory,args.smoke,args.seed)
        print(experiment.upper(),'completed',len(result),'records/conditions',str(directory))

if __name__=='__main__':main()
