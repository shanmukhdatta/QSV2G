"""Conservative Tamarin Stage 06 candidate runner; never equate exit code with proof.

WARNING: the candidate theory has not been locally parsed/proved by Tamarin.
This tool faithfully records NOT_EXECUTED, PARSE_FAILED, UNRESOLVED, or
PROVED_ABSTRACT_MODEL; it never claims software/quantum protocol security.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
THEORY=ROOT/'formal/qsv2g_stage06_compromise_candidate.spthy'
LEMMAS=('honest_accept_reachable','single_use_per_session','bypass_possible_with_full_compromise')


def run(out,timeout=360,bin_path=None):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    theory_sha=hashlib.sha256(THEORY.read_bytes()).hexdigest()
    exe=str(bin_path) if bin_path else shutil.which('tamarin-prover')
    info={'utc':datetime.now(timezone.utc).isoformat(),'theory':str(THEORY),
          'theory_sha256':theory_sha,'expected_lemmas':list(LEMMAS),
          'status':'NOT_EXECUTED','proof_status':'UNRESOLVED',
          'scope':'two-authority AB symbolic signature and CS-MAC compromise boundary; assumed honest QSS gate',
          'limitations':['not the full QSV2G protocol','no physical QSS',
                         'no computational proof for ML-DSA/ML-KEM','only AB pair',
                         'not linked formally to Python state transitions']}
    if not exe or not Path(exe).exists():
        info['reason']='Tamarin binary unavailable'
    else:
        env=os.environ.copy();env['PATH']=str(Path(exe).parent)+os.pathsep+env.get('PATH','')
        try:
            info['tamarin_path']=str(exe)
            version=subprocess.run([exe,'--version'],capture_output=True,text=True,timeout=20,env=env)
            info['tamarin_version']=(version.stdout+version.stderr)[-1500:]
            parsed=subprocess.run([exe,str(THEORY),'--quit-on-warning'],capture_output=True,text=True,timeout=timeout,env=env)
            (out/'p3_parse.log').write_text(parsed.stdout+'\n'+parsed.stderr)
            info['parse_returncode']=parsed.returncode
            if parsed.returncode:
                info['status']='PARSE_FAILED';info['reason']='Tamarin parse/wellformedness check failed; inspect p3_parse.log'
            else:
                info['status']='PARSED_NOT_PROVEN'
                prove=subprocess.run([exe,str(THEORY),'--prove'],capture_output=True,text=True,timeout=timeout,env=env)
                output=prove.stdout+'\n'+prove.stderr
                (out/'p3_proof.log').write_text(output)
                info['prove_returncode']=prove.returncode
                matches=re.findall(r'^\s*([A-Za-z_][A-Za-z_0-9]*)\s*\((?:exists-trace|all-traces)\)\s*:\s*(verified|falsified|analysis incomplete)\b',output,re.M|re.I)
                found={name:status.lower() for name,status in matches}
                info['lemmas']=found
                if (prove.returncode==0 and all(found.get(k)=='verified' for k in LEMMAS)):
                    info['status']='PROVED_ABSTRACT_MODEL';info['proof_status']='REPORTED_VERIFIED_BY_TAMARIN'
                else:
                    info['status']='UNRESOLVED'
                    info['reason']='Missing, falsified, incomplete, or failed lemmas; inspect proof log'
        except subprocess.TimeoutExpired as exc:
            info['status']='TIMEOUT';info['reason']=str(exc)
        except (OSError,ValueError) as exc:
            info['status']='UNRESOLVED';info['reason']=str(exc)
    (out/'p3_status.json').write_text(json.dumps(info,indent=2))
    print(json.dumps({k:info.get(k) for k in ('status','proof_status','reason','lemmas')},indent=2))
    return info


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--tamarin-bin',type=Path)
    p.add_argument('--timeout',type=int,default=360)
    args=p.parse_args();run(args.out,args.timeout,args.tamarin_bin)

if __name__=='__main__':main()
