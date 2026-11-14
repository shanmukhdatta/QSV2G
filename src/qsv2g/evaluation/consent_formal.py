"""E5 Tamarin execution gate with explicit proof/parse evidence boundaries.

A missing/unstartable prover is UNRESOLVED, never a passing security result.
The model assumes ideal QSS and only abstracts classical A/B consent/signatures.
"""
from __future__ import annotations
import argparse
import json
import os
import re
import shutil
import subprocess
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
MODEL=ROOT/'docs/formal/classical_consent.spthy'
LEMMAS=('honest_execution_reachable','execution_requires_same_EV_consent',
        'execution_requires_both_approval_actions','executed_once_per_session')


def parse_lemma_summary(stdout):
    """Only trust explicit Tamarin summary lines, never successful process return alone."""
    found={}
    for line in stdout.splitlines():
        match=re.match(r'^\s*([A-Za-z][A-Za-z_0-9]*)\s*\((all-traces|exists-trace)\)\s*:\s*(verified|falsified|unproven|unknown|sorry)\b',line,re.I)
        if match and match.group(1) in LEMMAS:
            found[match.group(1)]=match.group(3).lower()
    return found


def run(out,timeout=600,tools_dir=None):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    env=os.environ.copy()
    if tools_dir:
        binary_dir=str(Path(tools_dir).resolve()/'bin')
        env['PATH']=binary_dir+os.pathsep+env.get('PATH','')
    exe=shutil.which('tamarin-prover',path=env['PATH'])
    maude=shutil.which('maude',path=env['PATH'])
    result={'utc':datetime.now(timezone.utc).isoformat(),'model':str(MODEL),
        'scope':'abstract classical A/B consent and signatures; QSS gate ASSUMED, not proven',
        'prover':'Tamarin','parse_status':'NOT_EXECUTED','proof_status':'UNRESOLVED',
        'expected_lemmas':list(LEMMAS),'prover_present':bool(exe),'maude_present':bool(maude)}
    if not exe or not maude:
        result['reason']='Tamarin and/or Maude executables absent from PATH; see e5 install_status.json'
    else:
        result['binary_path']=exe; result['maude_path']=maude
        try:
            version=subprocess.run([exe,'--version'],capture_output=True,text=True,timeout=25,env=env)
            result['version']=(version.stdout or version.stderr).strip()[:1000]
            if version.returncode:
                result['reason']=f'Tamarin --version failed with code {version.returncode}'
            else:
                parse=subprocess.run([exe,str(MODEL),'--parse-only'],capture_output=True,text=True,timeout=timeout,env=env)
                (out/'e5_parse_log.txt').write_text(parse.stdout+'\n'+parse.stderr)
                result['parse_returncode']=parse.returncode
                result['parse_status']='PASSED' if parse.returncode==0 else 'FAILED'
                if parse.returncode==0:
                    attempt=subprocess.run([exe,str(MODEL),'--prove'],capture_output=True,text=True,timeout=timeout,env=env)
                    (out/'e5_proof_log.txt').write_text(attempt.stdout+'\n'+attempt.stderr)
                    result['prover_returncode']=attempt.returncode
                    found=parse_lemma_summary(attempt.stdout+'\n'+attempt.stderr)
                    result['lemma_status']=found
                    if (attempt.returncode==0 and len(found)==len(LEMMAS) and
                        all(found.get(x)=='verified' for x in LEMMAS)):
                        result['proof_status']='ALL_LISTED_LEMMAS_VERIFIED_IN_ABSTRACT_MODEL'
                    elif any(x=='falsified' for x in found.values()):
                        result['proof_status']='COUNTEREXAMPLE_REPORTED'
                    else:
                        result['proof_status']='UNRESOLVED'
                        result['reason']='Proof incomplete, unparsed summary, or prover exit nonzero; check logs'
        except (subprocess.TimeoutExpired, OSError) as exc:
            result['proof_status']='UNRESOLVED';result['reason']=str(exc)
    (out/'e5_status.json').write_text(json.dumps(result,indent=2))
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,default=Path('results/stage05/e5'))
    p.add_argument('--timeout',type=int,default=600)
    p.add_argument('--tools-dir',type=Path,default=None)
    a=p.parse_args();print(json.dumps(run(a.out,a.timeout,a.tools_dir),indent=2))
