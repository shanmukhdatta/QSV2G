"""Run one *simulated* QSV2G transaction with genuine post-quantum primitives."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from qsv2g import PQCrypto, run_demo

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--pair',choices=['AB','AC','BC'],default='AB')
 p.add_argument('--operation',choices=['CHARGE','DISCHARGE'],default='CHARGE')
 p.add_argument('--length',type=int,default=9)
 p.add_argument('--seed',type=int,default=2026)
 p.add_argument('--output',type=Path)
 a=p.parse_args()
 if a.length<1: p.error('length must be positive')
 crypto=PQCrypto()  # fail closed if neither real ML-KEM/ML-DSA provider exists
 s=run_demo(crypto=crypto,pair=tuple(a.pair),seed=a.seed,L=a.length,op=a.operation)
 r={'status':s.stage,'operation':a.operation,'pair':a.pair,'length':a.length,
    'backend':crypto.kind,'resource_state':s.resource.state,
    'energy_mwh':getattr(s,'energy_mwh',None),
    'trace':s.log,'limitations':'simulated actors, energy ticks and ideal quantum states'}
 out=json.dumps(r,indent=2,default=str)
 if a.output:
  a.output.parent.mkdir(parents=True,exist_ok=True)
  a.output.write_text(out)
 print(out)
 if s.stage!='TERMINATED': raise SystemExit(1)

if __name__=='__main__':main()
