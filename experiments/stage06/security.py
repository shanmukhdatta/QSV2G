"""QSV2G Stage 06 P0/P1: honest controls, compromised-role probes, exact QSS/classical comparison.

This is an adversarial *single-process laboratory*, not a network attacker emulator.
A successful conditional forgery with privileged station-state insertion shows lack
of independent EV proof-of-reconstruction, NOT a remote authorization exploit.
No physical qutrit channel, maliciously secure VQSS, or deployed key isolation.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import os
import platform
import secrets
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
sys.path.insert(0,str(ROOT/'experiments/stage05'))
from qsv2g_core import (AUTHORITIES, H, QSV2G, PQCrypto, ProtocolAbort, SLOT,
                         encode, qss_state, reduced_density, new_qss_resource)
from runner import ClassicalResource, PAIRS

VARIANTS=('QSS','CLASSICAL_SHARING')
STAGES=('honest_control','one_approval','share_only_tamper',
        'dealer_replaces_secret_and_commitment','one_signer_fake_digest',
        'two_signers_fake_digest','two_signers_skip_reconstruction',
        'two_signers_cross_context')


def save_csv(path,rows):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    if not rows:raise ValueError('No observations')
    columns=list(rows[0])
    with path.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=columns,extrasaction='raise')
        writer.writeheader();writer.writerows(rows)


def initial_protocol(variant,crypto,L,pair,op,seed,approvals=None):
    factory=(lambda n,rng:ClassicalResource.prepare(n)) if variant=='CLASSICAL_SHARING' else None
    p=QSV2G(crypto=crypto,L=L,seed=seed,resource_factory=factory)
    p.register();p.authenticate(op=op);p.establish_session()
    p.set_ev_intent(op=op)
    p.authorization_context(op=op)
    p.authority_verify(approvals=pair if approvals is None else approvals)
    assert p.stage=='APPROVED' and p.resource.state=='UNUSED'
    return p


def forged_token(p,pair,digest,available_signers):
    """Attack harness signs arbitrary digest ONLY with explicitly compromised signing keys.

    Missing signature uses random invalid bytes. Underlying core continues to do
    ML-DSA verification; never use a fake crypto backend for experimental P0.
    """
    statement=('QSV2G-AUTHZ',p.ac,p.sid,p.resource.nu,*pair,digest,p.vld,'ACCEPT')
    message=encode(*statement)
    signatures={a:(p.pqc.sign(p.sigkeys[a][1],message) if a in available_signers
                  else secrets.token_bytes(32)) for a in pair}
    return {'statement':statement,'signatures':signatures}


def try_ev_response(p,token,pair,force_station_token_state=False):
    """Submit attacker token via normal AEAD protected_response EV checks.

    If `force_station_token_state`, compromised CS *replaces its internal stage*
    in the experiment. This is privileged process-local intervention, not a
    remote protocol message. This MUST be reported with each result.
    """
    if force_station_token_state:
        p.stage='TOKEN'  # adversary controls station logic; not an on-wire exploit
    p.pair=tuple(pair)
    p.token=token
    p.protected_response()  # ordinary EV token checks and real ML-DSA verification
    return p.stage=='EV_ACCEPTED'


def change_dealer_secret_with_matching_commitment(resource,variant):
    """Dishonest dealer jointly replaces a secret and the *unanchored* commitment.

    Strong capability: dealer controls own distribution data and its commitment
    before an independent authenticated anchor exists. Cannot generalize to an
    authenticated, independently anchored VQSS design.
    """
    original=resource.dealer_secrets['A'][0]
    changed=(original+1)%3
    resource.dealer_secrets['A'][0]=changed
    if variant=='QSS':
        resource.states['A'][0]=qss_state(changed)
    elif variant=='CLASSICAL_SHARING':
        old=resource.shares['A'][0];r=old[0]
        resource.shares['A'][0]=(r,(r+changed)%3,(r+2*changed)%3)
    else:raise ValueError(variant)
    resource.commitments['A']=H('QSV2G-QSS-COM','A',resource.nu,resource.dealer_secrets['A'])
    return original,changed


def execute_probe(variant,scenario,crypto,L,pair,op,seed):
    t0=time.perf_counter();p=None
    # One-approval negative control is initialized with exactly one approval.
    # Keep its comparator variant unchanged, including resource preparation.
    if scenario!='one_approval':
        p=initial_protocol(variant,crypto,L,pair,op,seed)
    expected={'honest_control':'EV_ACCEPTED',
        'one_approval':'REJECTED',
        'share_only_tamper':'REJECTED',
        'dealer_replaces_secret_and_commitment':'RECONSTRUCTED_CHANGED_SECRET',
        'one_signer_fake_digest':'REJECTED',
        'two_signers_fake_digest':'EV_ACCEPTED_FAKE_DIGEST',
        'two_signers_skip_reconstruction':'EV_ACCEPTED_NO_RECONSTRUCTION',
        'two_signers_cross_context':'REJECTED'}[scenario]
    observed='UNEXPECTED';detail='';notes='';
    cs_privileged=scenario in ('one_signer_fake_digest','two_signers_fake_digest',
                               'two_signers_skip_reconstruction','two_signers_cross_context')
    reconstruction_before_response=False
    original_digest=None
    if scenario=='honest_control':
        p.threshold_reconstruct(pair=pair);reconstruction_before_response=True
        p.issue_token();p.protected_response()
        observed='EV_ACCEPTED' if p.stage=='EV_ACCEPTED' else 'UNEXPECTED'
    elif scenario=='one_approval':
        # A single approval must abort, for both QSS and classical variants.
        try:
            initial_protocol(variant,crypto,L,pair,op,seed,approvals=(pair[0],))
            observed='UNEXPECTED'
        except ProtocolAbort as exc:
            observed='REJECTED';detail=str(exc)
    elif scenario=='share_only_tamper':
        try:
            p.threshold_reconstruct(pair=pair,tamper_share=True)
            observed='UNEXPECTED'
        except ProtocolAbort as exc:
            observed='REJECTED';detail=str(exc)
        assert p.resource.state=='CONSUMED','A failed reconstruction must consume resource'
    elif scenario=='dealer_replaces_secret_and_commitment':
        old,new=change_dealer_secret_with_matching_commitment(p.resource,variant)
        assert old!=new
        p.threshold_reconstruct(pair=pair)
        reconstruction_before_response=True
        p.issue_token();p.protected_response()
        observed=('RECONSTRUCTED_CHANGED_SECRET' if p.stage=='EV_ACCEPTED'
                  else 'UNEXPECTED')
        detail='dealer replaced its secret and commitment; no independent old-secret anchor'
        notes='requires dealer control of commitment and resource before external anchoring'
    else:
        # For all forged-token probes, allow legitimate consent but no unauthorized
        # change of operation. Test conditional bypass of QSS gate, not EV consent.
        if scenario!='two_signers_skip_reconstruction':
            p.threshold_reconstruct(pair=pair);reconstruction_before_response=True
            p.issue_token()
            original_digest=p.token['statement'][6]
        fake_digest=secrets.token_bytes(32)
        assert fake_digest!=original_digest
        forged=forged_token(p,pair,fake_digest,
            available_signers=(pair[:1] if scenario=='one_signer_fake_digest' else pair))
        if scenario=='two_signers_cross_context':
            # Sign a false context with two real compromised keys. EV must check AC.
            statement=list(forged['statement']);statement[1]=secrets.token_bytes(32)
            forged=forged_token(p,pair,fake_digest,available_signers=pair)
            altered=tuple(statement);msg=encode(*altered)
            forged={'statement':altered,
                    'signatures':{a:crypto.sign(p.sigkeys[a][1],msg) for a in pair}}
        try:
            accepted=try_ev_response(p,forged,pair,force_station_token_state=True)
            if not accepted:observed='UNEXPECTED'
            elif scenario=='two_signers_skip_reconstruction':
                observed='EV_ACCEPTED_NO_RECONSTRUCTION'
            elif scenario=='two_signers_fake_digest':
                observed='EV_ACCEPTED_FAKE_DIGEST'
            else:observed='UNEXPECTED'
        except (ProtocolAbort,KeyError) as exc:
            observed='REJECTED';detail=str(exc)
        if scenario=='two_signers_skip_reconstruction':
            assert p.resource.state=='UNUSED', 'Attack requires no prior QSS/classical reconstruction'
        notes='compromised selected signer keys AND CS-internal token-stage control'
    return dict(variant=variant,scenario=scenario,pair=''.join(pair),op=op,L=L,
        outcome=observed,expected=expected,match=(observed==expected),
        qss_or_classical_resource_state=(p.resource.state if p is not None else 'ABORT_BEFORE_APPROVAL'),
        reconstructed_before_ev_response=reconstruction_before_response,
        compromised_signer_keys=(1 if scenario=='one_signer_fake_digest' else
            2 if cs_privileged else 0),
        compromised_cs_in_test_harness=cs_privileged,
        pure_network_adversary=False if cs_privileged else None,
        actual_ev_operation_changed=False,
        note=notes,detail=detail,elapsed_ms=round((time.perf_counter()-t0)*1000,3),
        crypto_backend=crypto.kind)


def phase_p0_p1(out,L=9,smoke=False,seed=2026):
    crypto=PQCrypto()  # no silent classical substitute
    rows=[]
    pairs=(PAIRS[:1] if smoke else PAIRS)
    ops=('CHARGE',) if smoke else ('CHARGE','DISCHARGE')
    for variant in VARIANTS:
        for pair in pairs:
            for op in ops:
                for i,scenario in enumerate(STAGES):
                    row=execute_probe(variant,scenario,crypto,L,pair,op,seed+i)
                    rows.append(row)
    save_csv(out/'p0_p1_attack_matrix.csv',rows)
    failures=[r for r in rows if not r['match']]
    (out/'p0_p1_summary.json').write_text(json.dumps({
        'total_cases':len(rows), 'unexpected_outcomes':len(failures),
        'conditional_ev_acceptance_of_fake_signed_digest':sum(
            r['outcome']=='EV_ACCEPTED_FAKE_DIGEST' for r in rows),
        'conditional_ev_acceptance_without_reconstruction':sum(
            r['outcome']=='EV_ACCEPTED_NO_RECONSTRUCTION' for r in rows),
        'signed_forgery_requires':['two exposed signing keys','CS internal/token-stage control'],
        'interpretation':'conditional trust-boundary exposure, NOT a proven network-only exploit',
        'backend':crypto.kind,'examples':rows[:2],
        'limitations':['Single process, simulated roles',
          'Signing keys co-resident in CS simulator; deployed key custody unspecified',
          'No physical QSS channels',
          'Compromised authority scenarios may be outside original threshold trust model',
          'Attack stages modeled by explicit privileged experiment harness'],
    },indent=2,default=str))
    if failures:raise AssertionError('Unexpected attack outcomes: '+repr(failures[:3]))
    return rows


def marginal_and_pair_distributions():
    """Exact comparison on computational-basis interface, not on all quantum protocols.

    Classical share distribution: r uniformly in {0,1,2};
    shares (r, r+s, r+2s) mod 3. Quantum |psi_s> has amplitude 1/sqrt(3)
    at exactly the same three basis triples. Pair outcomes have identical laws.
    """
    rows=[]
    for s in range(3):
        psi=qss_state(s); probs=np.abs(psi)**2
        classical=np.zeros((3,3,3))
        for r in range(3):classical[r,(r+s)%3,(r+2*s)%3]+=1/3
        assert np.isclose(probs.sum(),1) and np.isclose(classical.sum(),1)
        for pair in PAIRS:
            unused=tuple(k for k in range(3) if k not in tuple(SLOT[a] for a in pair))
            quantum=np.sum(probs,axis=unused)
            classical_m=np.sum(classical,axis=unused)
            tv=0.5*np.abs(quantum-classical_m).sum()
            for authority in AUTHORITIES:
                sigma=reduced_density(psi,SLOT[authority])
                trace=np.linalg.norm(sigma-np.eye(3)/3)
                if trace>1e-12:raise AssertionError('One QSS share leaked classical secret')
            rows.append(dict(secret=s,pair=''.join(pair),
                computational_basis_total_variation=float(tv),
                qss_single_share_distance_to_uniform=float(max(np.linalg.norm(
                    reduced_density(psi,SLOT[a])-np.eye(3)/3) for a in AUTHORITIES)),
                exact_classical_secrecy=True,
                tested_interface='classical computational-basis measurement',
                no_quantum_advantage_established=(tv<1e-12)))
    return rows


def write_manifest(out,L,smoke,seed):
    try:rev=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True,stderr=subprocess.DEVNULL).strip()
    except Exception:rev='NOT_IN_GIT_CHECKOUT'
    paths=['src/qsv2g_core.py','experiments/stage05/runner.py','experiments/stage06/security.py']
    hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}
    info=dict(stage='06',tasks=['P0','P1'], utc=datetime.now(timezone.utc).isoformat(),
        git_head=rev,sha256=hashes,L=L,smoke=smoke,seed=seed,
        python=sys.version,platform=platform.platform(),
        threat_boundary='Selected signer private keys + privileged simulated CS state unless otherwise noted',
        rigorous_claim='Software conditional vulnerability; exact basis-distribution equivalence; no hardware advantage proven')
    (out/'manifest.json').write_text(json.dumps(info,indent=2))


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--L',type=int,default=9)
    p.add_argument('--seed',type=int,default=2026)
    p.add_argument('--smoke',action='store_true')
    args=p.parse_args(argv)
    if not 1<=args.L<=1000:raise ValueError('L must be between 1 and 1000')
    args.out.mkdir(parents=True,exist_ok=True)
    exact=marginal_and_pair_distributions()
    save_csv(args.out/'p1_exact_distributions.csv',exact)
    rows=phase_p0_p1(args.out,args.L,args.smoke,args.seed)
    write_manifest(args.out,args.L,args.smoke,args.seed)
    print(json.dumps({'status':'COMPLETED','case_count':len(rows),
                      'matched':sum(r['match'] for r in rows),
                      'conditional_no_reconstruction_acceptances':sum(
                       r['outcome']=='EV_ACCEPTED_NO_RECONSTRUCTION' for r in rows),
                      'exact_distribution_pairs':len(exact),'out':str(args.out)},indent=2))

if __name__=='__main__':main()
