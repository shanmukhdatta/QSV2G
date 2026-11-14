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
 if a.model=='consent':
  verified=result.get('proof_status')=='ALL_LISTED_LEMMAS_VERIFIED_IN_ABSTRACT_MODEL'
 else:
  verified=(result.get('status')=='PROVED_ABSTRACT_MODEL' and result.get('proof_status')=='REPORTED_VERIFIED_BY_TAMARIN')
 if not verified:raise SystemExit(2)
if __name__=='__main__':main()
