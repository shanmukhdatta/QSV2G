"""Independent ideal QSS correctness and real-PQC workflow smoke tests."""
from __future__ import annotations
import argparse, csv, json
from pathlib import Path
import numpy as np
from qsv2g import (AUTHORITIES, QSV2G, PQCrypto, run_demo, qss_consistency,
                   measure_pair, qss_state, recover_symbol)

PAIRS=(('A','B'),('A','C'),('B','C'))

def validate(out,shots=10,seed=2026,L=3):
 out=Path(out);out.mkdir(parents=True,exist_ok=True)
 if shots<1 or L<1:raise ValueError('shots and L must be positive')
 rng=np.random.default_rng(seed)
 rows=[]
 for s in range(3):
  psi=qss_state(s)
  for pair in PAIRS:
   for trial in range(shots):
    x,y=measure_pair(psi,pair,rng)
    recovered=recover_symbol(pair,x,y)
    rows.append({'secret':s,'pair':''.join(pair),'trial':trial,'recovered':recovered,'correct':recovered==s})
 with (out/'ideal_qss.csv').open('w',newline='') as f:
  wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
 backend=PQCrypto();flows=[]
 for pair in PAIRS:
  for op in ('CHARGE','DISCHARGE'):
   result=run_demo(crypto=backend,L=L,pair=pair,op=op,seed=seed)
   flows.append({'pair':''.join(pair),'operation':op,'result':result.stage,'resource':result.resource.state})
 with (out/'workflows.csv').open('w',newline='') as f:
  wr=csv.DictWriter(f,fieldnames=list(flows[0]));wr.writeheader();wr.writerows(flows)
 summary={'ideal_trials':len(rows),'correct':sum(x['correct'] for x in rows),
          'workflows':len(flows),'completed':sum(x['result']=='TERMINATED' for x in flows),
          'crypto_backend':backend.kind,'quantum_state_checks':qss_consistency(),
          'scope':'ideal simulated quantum states, genuine PQC, no physical V2G hardware'}
 (out/'summary.json').write_text(json.dumps(summary,indent=2))
 if summary['correct']!=len(rows) or summary['completed']!=6:raise RuntimeError('Validation failed')
 return summary

def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True)
 p.add_argument('--shots',type=int,default=10);p.add_argument('--L',type=int,default=3)
 a=p.parse_args();print(json.dumps(validate(a.out,a.shots,L=a.L),indent=2))
if __name__=='__main__':main()
