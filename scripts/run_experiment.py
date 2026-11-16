"""Run bounded current-code studies; --full selects each study's documented budget."""
from __future__ import annotations
import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
COMMANDS={
 'validation':['qsv2g.evaluation.validation'],
 'performance':['qsv2g.evaluation.workflows','--experiment','e1'],
 'security':['qsv2g.evaluation.workflows','--experiment','e2'],
 'noise':['qsv2g.evaluation.workflows','--experiment','e3'],
 'availability':['qsv2g.evaluation.workflows','--experiment','e4'],
 'noise-vector':['qsv2g.evaluation.full_vector'],
 'security-stateful':['qsv2g.evaluation.stateful'],
 'security-adversarial':['qsv2g.evaluation.adversarial'],
 'reliability':['qsv2g.evaluation.retries']}

def build_command(task,full,dest,seed):
 cmd=[sys.executable,'-m',*COMMANDS[task]]
 if task=='noise-vector':
  cmd+=['--lengths']+(['9','27'] if full else ['9'])+['--p','0','0.01','--trials',str(1000 if full else 10),'--seed',str(seed),'--output',str(dest/'trials.csv')]
 elif task=='security-stateful':
  cmd+=['--examples',str(1000 if full else 20),'--steps',str(50 if full else 15),'--output',str(dest/'hypothesis.json')]
 elif task=='validation':
  cmd+=['--out',str(dest),'--shots',str(80 if full else 10),'--seed',str(seed)]
 else:
  cmd+=['--out',str(dest),'--seed',str(seed)]
  if not full:cmd.append('--smoke')
 return cmd

def execute(command):
 return subprocess.run(command,capture_output=True,text=True)

def source_provenance():
 def git(*args):
  p=subprocess.run(['git',*args],cwd=ROOT,capture_output=True,text=True)
  return p.stdout.strip() if p.returncode==0 else None
 paths=sorted({*ROOT.glob('src/**/*.py'),*ROOT.glob('scripts/*.py'),*ROOT.glob('formal/*.spthy'),ROOT/'pyproject.toml'})
 packages={}
 for name in ['numpy','pandas','matplotlib','cryptography','pqcrypto','hypothesis']:
  try:packages[name]=importlib.metadata.version(name)
  except importlib.metadata.PackageNotFoundError:packages[name]=None
 dirty=git('status','--porcelain','--untracked-files=all')
 return {'git_revision':git('rev-parse','HEAD'),'git_dirty':None if dirty is None else bool(dirty),
  'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
  'python':sys.version,'platform':platform.platform(),'cpu_count':os.cpu_count(),'packages':packages}

def run_study(task,full,out,seed):
 dest=Path(out)/task
 if dest.exists() and any(dest.iterdir()):
  raise FileExistsError(f'Refusing to overwrite {dest}; choose a fresh --out directory')
 # Atomic leaf-directory claim: concurrent runs cannot both own this output.
 dest.mkdir(parents=True,exist_ok=False)
 cmd=build_command(task,full,dest,seed)
 record=source_provenance()
 record.update(study=task,command=cmd,utc_started=datetime.now(timezone.utc).isoformat(),
  mode='full' if full else 'smoke',seed=seed,
  randomness_scope='NumPy simulation/work-order seed; cryptographic secrets remain OS-random. Stateful Hypothesis uses derandomize=True, not this seed.',
  returncode=None)
 (dest/'execution.json').write_text(json.dumps(record,indent=2))
 try:
  proc=execute(cmd)
 except OSError as exc:
  proc=subprocess.CompletedProcess(cmd,127,'',str(exc))
 (dest/'console.log').write_text(proc.stdout+'\n'+proc.stderr)
 record.update(returncode=proc.returncode,utc_finished=datetime.now(timezone.utc).isoformat(),
  outputs_sha256={str(p.relative_to(dest)):hashlib.sha256(p.read_bytes()).hexdigest()
   for p in sorted(dest.rglob('*')) if p.is_file() and p.name!='execution.json'})
 (dest/'execution.json').write_text(json.dumps(record,indent=2))
 if proc.returncode:
  raise RuntimeError(f'{task}: exit {proc.returncode}; inspect {dest}/console.log')
 print(proc.stdout[-450:])
 return record

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--study',choices=list(COMMANDS)+['all'],default='validation')
 p.add_argument('--full',action='store_true',help='use larger budgets; not exact replay of every historical experiment')
 p.add_argument('--out',type=Path,default=None,help='fresh run root; default results/generated/<UTC timestamp>')
 p.add_argument('--seed',type=int,default=2026)
 a=p.parse_args();out=a.out or ROOT/'results/generated'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
 tasks=list(COMMANDS) if a.study=='all' else [a.study]
 # Preflight every destination before spending time on any study.
 for task in tasks:
  dest=out/task
  if dest.exists() and any(dest.iterdir()):p.error(f'{dest} contains results; use a fresh --out')
 for task in tasks:
  print('RUN',task,flush=True)
  run_study(task,a.full,out,a.seed)
 print('Completed:',', '.join(tasks),'in',out)

if __name__=='__main__':main()
