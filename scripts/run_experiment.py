"""Run experiments by scientific task. Defaults to bounded preflight; --full is expensive."""
from __future__ import annotations
import argparse, json, subprocess, sys
from datetime import datetime,timezone
from pathlib import Path

COMMANDS={
 'validation':['qsv2g.evaluation.validation'],
 'performance':['qsv2g.evaluation.workflows','--experiment','e1'],
 'security':['qsv2g.evaluation.workflows','--experiment','e2'],
 'noise':['qsv2g.evaluation.workflows','--experiment','e3'],
 'availability':['qsv2g.evaluation.workflows','--experiment','e4'],
 'noise-vector':['qsv2g.evaluation.full_vector'],
 'security-stateful':['qsv2g.evaluation.stateful'],
 'security-adversarial':['qsv2g.evaluation.adversarial'],
 'reliability':['qsv2g.evaluation.retries']
}

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--study',choices=list(COMMANDS)+['all'],default='validation')
 p.add_argument('--full',action='store_true',help='run large original trial budgets')
 p.add_argument('--out',type=Path,default=Path('results/generated'))
 p.add_argument('--seed',type=int,default=2026)
 a=p.parse_args()
 tasks=[a.study] if a.study!='all' else ['validation','security','security-stateful','performance','noise','noise-vector','availability','security-adversarial','reliability']
 for task in tasks:
  dest=a.out/task;dest.mkdir(parents=True,exist_ok=True)
  cmd=[sys.executable,'-m',*COMMANDS[task]]
  if task=='noise-vector':
   cmd+=['--lengths']+(['9','27'] if a.full else ['9'])+['--p','0','0.01','--trials',str(1000 if a.full else 10),'--seed',str(a.seed),'--output',str(dest/'trials.csv')]
  elif task=='security-stateful':
   cmd+=['--examples',str(1000 if a.full else 20),'--steps',str(50 if a.full else 15),'--output',str(dest/'hypothesis.json')]
  elif task=='validation':
   cmd+=['--out',str(dest),'--shots',str(80 if a.full else 10)]
  else:
   cmd+=['--out',str(dest),'--seed',str(a.seed)]
   if not a.full:cmd.append('--smoke')
  print('RUN',task,flush=True)
  proc=subprocess.run(cmd,capture_output=True,text=True)
  (dest/'console.log').write_text(proc.stdout+'\n'+proc.stderr)
  if proc.returncode!=0:
   print((proc.stderr or proc.stdout)[-2500:],file=sys.stderr)
   raise SystemExit(f'{task}: command failed (exit {proc.returncode}), see {dest}/console.log')
  record={'study':task,'command':cmd,'utc':datetime.now(timezone.utc).isoformat(),
          'mode':'full' if a.full else 'smoke','returncode':proc.returncode}
  (dest/'execution.json').write_text(json.dumps(record,indent=2))
  print(proc.stdout[-450:])
 print('Completed:',', '.join(tasks))

if __name__=='__main__':main()
