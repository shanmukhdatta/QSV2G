"""Run the two symbolic models; logs distinguish verified proofs from attack existence."""
from __future__ import annotations
import argparse, json
from pathlib import Path

def main():
 p=argparse.ArgumentParser();p.add_argument('--model',choices=['consent','compromise'],required=True)
 p.add_argument('--out',type=Path,default=Path('results/logs/formal'))
 p.add_argument('--timeout',type=int,default=360)
 a=p.parse_args()
 if a.model=='consent':
  from qsv2g.evaluation.consent_formal import run
  result=run(a.out/a.model,timeout=a.timeout)
 else:
  from qsv2g.evaluation.compromise_formal import run
  result=run(a.out/a.model,timeout=a.timeout)
 print(json.dumps(result,indent=2))
 if result.get('proof_status') not in ('PROVED_ABSTRACT_MODEL','VERIFIED'):raise SystemExit(2)
if __name__=='__main__':main()
