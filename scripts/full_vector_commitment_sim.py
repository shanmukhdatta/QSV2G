"""Reproducible, software-only full-vector QSS commitment-gate experiment.

Model: computational-basis measurements of the ideal 3-qutrit codeword;
independent qutrit-X faults on the SECOND selected share with probability p.
Every one of three dealer vectors of length L must reconstruct its precommitted
value to be eligible for a token. This is NOT a network, hardware, full-protocol,
or cross-channel noise benchmark, and it does not imply authorization security.

Examples:
 python scripts/full_vector_commitment_sim.py --lengths 9 27 --p 0 0.05 --trials 100 --seed 2026
"""
from __future__ import annotations
import argparse
import csv
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from qsv2g_core import AUTHORITIES, H, qss_state, measure_pair, recover_symbol


def experiment(L, p, trials, pair=('A','B'), seed=2026):
    if not isinstance(L,int) or L<1 or not isinstance(trials,int) or trials<1:
        raise ValueError('length and trials must be positive integers')
    if not 0<=p<=1: raise ValueError('p must be between 0 and 1')
    if len(pair)!=2 or len(set(pair))!=2 or not set(pair)<=set(AUTHORITIES):
        raise ValueError('pair must contain two distinct authorities')
    rng=np.random.default_rng(seed)
    accepted=0; faulty=0; total_symbols=0
    for _ in range(trials):
        nu='0'*24  # public resource ID: fixed for this independent experiment only
        commitments={}; recovered={}
        for dealer in AUTHORITIES:
            vector=list(map(int,rng.integers(0,3,size=L)))
            commitments[dealer]=H('QSV2G-QSS-COM',dealer,nu,vector)
            reconstructed=[]
            for s in vector:
                error=bool(rng.random()<p)
                faulty+=int(error); total_symbols+=1
                xu,xv=measure_pair(qss_state(s),pair,rng,x_fault=error)
                reconstructed.append(recover_symbol(pair,xu,xv))
            recovered[dealer]=reconstructed
        # The gate checks all three dealer commitments before token eligibility.
        if all(H('QSV2G-QSS-COM',a,nu,recovered[a])==commitments[a] for a in AUTHORITIES):
            accepted+=1
    return dict(L=L,p=p,trials=trials,accepted=accepted,
                commitment_rejects=trials-accepted,accepted_rate=accepted/trials,
                injected_x_errors=faulty,injected_symbol_trials=total_symbols,
                pair=''.join(pair),seed=seed)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lengths',nargs='+',type=int,default=[9,27,81,162])
    parser.add_argument('--p',nargs='+',type=float,default=[0,0.01,0.05])
    parser.add_argument('--trials',type=int,default=100)
    parser.add_argument('--seed',type=int,default=2026)
    parser.add_argument('--pair',nargs=2,default=['A','B'])
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    rows=[experiment(L,p,args.trials,tuple(args.pair),args.seed+1000*i+j)
          for i,L in enumerate(args.lengths) for j,p in enumerate(args.p)]
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        handle=args.output.open('w',newline='',encoding='utf-8')
    else: handle=sys.stdout
    try:
        writer=csv.DictWriter(handle,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)
    finally:
        if args.output: handle.close()


if __name__=='__main__': main()
