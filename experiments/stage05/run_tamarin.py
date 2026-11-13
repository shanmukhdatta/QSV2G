"""E5 Tamarin gate: report missing binary or unreviewed proof log honestly.

A zero process exit status means the command returned, NOT all lemmas are proved.
Never claim any property as PROVED until the output is independently reviewed.
"""
import argparse
import json
import shutil
import subprocess
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
MODEL=ROOT/'formal/qsv2g_classical_consent.spthy'


def run(out,timeout=180):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    exe=shutil.which('tamarin-prover')
    result={'utc':datetime.now(timezone.utc).isoformat(),'model':str(MODEL),
        'scope':'classical A/B consent and signatures; QSS gate assumed, not proven',
        'prover':'Tamarin','parse_status':'NOT_EXECUTED','proof_status':'UNRESOLVED'}
    if not exe:
        result['reason']='Tamarin binary not found; install Tamarin and Maude externally'
    else:
        try:
            version=subprocess.run([exe,'--version'],capture_output=True,text=True,timeout=15)
            result['version']=(version.stdout or version.stderr).strip()[:800]
            parse=subprocess.run([exe,'--parse-only',str(MODEL)],capture_output=True,text=True,timeout=timeout)
            (out/'e5_parse_log.txt').write_text(parse.stdout+'\n'+parse.stderr)
            result['parse_status']='PASSED' if parse.returncode==0 else 'FAILED'
            if parse.returncode==0:
                run=subprocess.run([exe,'--prove',str(MODEL)],capture_output=True,text=True,timeout=timeout)
                (out/'e5_proof_log.txt').write_text(run.stdout+'\n'+run.stderr)
                result['prover_returncode']=run.returncode
                result['proof_status']='OUTPUT_REQUIRES_INDEPENDENT_LEMMA_REVIEW' if run.returncode==0 else 'UNRESOLVED'
        except subprocess.TimeoutExpired:
            result['proof_status']='UNRESOLVED';result['reason']='Tamarin timeout'
    (out/'e5_status.json').write_text(json.dumps(result,indent=2))
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,default=Path('results/stage05/e5'))
    parser.add_argument('--timeout',type=int,default=180)
    args=parser.parse_args();print(json.dumps(run(args.out,args.timeout),indent=2))
