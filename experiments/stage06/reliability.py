"""Stage 06 P2 — fresh-resource retry reliability *model*, not a deployed protocol.

Assumptions: each attempt is a fresh, independent three-dealer QSS vector;
a new unique resource and approval are required for a retry; fail-closed
commitments and EV consent are unchanged. Samples use Bernoulli gate success
with independent per-trit probability imported from Stage 05; they DO NOT
simulate a physical channel or establish security of a retry message flow.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
import sys
from pathlib import Path

import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'experiments/stage05'))
from runner import q_probability,CHANNELS

LENGTHS=(9,27,81,162)
LEVELS=(0.0,0.001,0.005,0.01,0.03)
BUDGETS=(1,3,10,30)


def prob_one_vector(L,channel,p):
    q=q_probability(channel,p)
    if not 0<=q<=1:raise ValueError('Invalid per-trit recovery probability')
    return q**(3*L)


def trial_budget(L,channel,p,budget,repetitions,rng):
    """Geometric attempt count; unused retries do not consume resources."""
    a=prob_one_vector(L,channel,p)
    if a==0:
        used=np.full(repetitions,budget,dtype=np.int64);accept=np.zeros(repetitions,dtype=bool)
    elif a==1:
        used=np.ones(repetitions,dtype=np.int64);accept=np.ones(repetitions,dtype=bool)
    else:
        # Inverse CDF sampling. Use -expm1/log1p for stable rare probabilities.
        u=rng.random(repetitions)
        # geometric draw k with P(T>k)=(1-a)^k
        # floor(log(1-u)/log(1-a))+1; values beyond budget are capped.
        # log(0) is avoided by Generator.random's u<1.
        raw=np.floor(np.log1p(-u)/np.log1p(-a))+1
        accept=raw<=budget
        used=np.minimum(raw,budget).astype(np.int64)
    measured=float(accept.mean())
    expected=-(math.expm1(budget*math.log1p(-a))) if a<1 else 1.0
    exp_used=(1.0 if a==1 else (-math.expm1(budget*math.log1p(-a)))/a if a>0 else float(budget))
    return dict(L=L,channel=channel,p=p,retry_budget=budget,repetitions=repetitions,
        one_attempt_gate_eligible=a,
        analytic_budget_acceptance=expected,
        observed_budget_acceptance=measured,
        analytic_mean_attempts=exp_used,
        observed_mean_attempts=float(used.mean()),
        analytic_stored_qutrits=9*L*exp_used,
        observed_mean_stored_qutrits=float(9*L*used.mean()),
        analytic_remote_qutrits=6*L*exp_used,
        max_qutrits_per_transaction=9*L*budget,
        successes=int(accept.sum()))


def run(out,smoke=False,seed=2026,repetitions=None):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    repetitions=(200 if smoke else 2500) if repetitions is None else repetitions
    if repetitions<=0:raise ValueError('Repetitions must be > 0')
    rng=np.random.default_rng(seed)
    rows=[]
    lengths=(9,162) if smoke else LENGTHS
    levels=(0,0.01) if smoke else LEVELS
    for L in lengths:
        for channel in CHANNELS:
            for p in levels:
                for budget in BUDGETS:
                    rows.append(trial_budget(L,channel,p,budget,repetitions,rng))
    path=out/'p2_retries.csv'
    with path.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=rows[0].keys());writer.writeheader();writer.writerows(rows)
    info=dict(stage='06',phase='P2',mode='SMOKE' if smoke else 'MODEL_FULL',seed=seed,
        configurations=len(rows),repetitions_per_configuration=repetitions,
        assumptions=['independent resource attempts','new independent resource ID per attempt',
            'each attempt repeats authority approval (not implemented as deployed message protocol)',
            'all three dealer vectors require correct recovery for gate eligibility',
            'no network/physical qutrit device and no measured real-PQC retry latency'],
        security_note='Higher availability is NOT stronger cryptographic security; no correction to QSS proof of reconstruction',
        output=str(path))
    (out/'p2_manifest.json').write_text(json.dumps(info,indent=2))
    print(json.dumps({'configurations':len(rows),'repetitions':repetitions,'mode':info['mode']},indent=2))
    return rows


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--smoke',action='store_true')
    p.add_argument('--seed',type=int,default=2026);p.add_argument('--repetitions',type=int)
    args=p.parse_args()
    run(args.out,smoke=args.smoke,seed=args.seed,repetitions=args.repetitions)

if __name__=='__main__':main()
