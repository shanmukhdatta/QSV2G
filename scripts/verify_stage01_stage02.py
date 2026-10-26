#!/usr/bin/env python3
"""Read-only checks of Stage 01/02 submitted artifacts; no network/dependencies."""
from pathlib import Path
import csv, io, hashlib, json, zipfile, sys
ROOT=Path(__file__).resolve().parents[1]

def sha256(b):return hashlib.sha256(b).hexdigest()
def check(stage,name,manifest):
    zpath=ROOT/'results'/stage/'submitted'/name
    assert zpath.exists(), zpath
    with zipfile.ZipFile(zpath) as z:
        assert z.testzip() is None
        if manifest.endswith('.csv'):
            records=list(csv.DictReader(io.StringIO(z.read(manifest).decode())))
        else: records=json.loads(z.read(manifest))
        for r in records:
            n=r.get('file') or r.get('filename') or r.get('path')
            data=z.read(n)
            assert sha256(data)==r['sha256'],n
            size=r.get('size_bytes',r.get('bytes',r.get('size')))
            assert len(data)==int(size),n
        for n in z.namelist():
            extracted=ROOT/'results'/stage/'submitted'/'extracted'/n
            assert extracted.exists() and extracted.read_bytes()==z.read(n),n
        if stage=='stage01':
            s=json.loads(z.read('baseline_summary.json'))
            cases=list(csv.DictReader(io.StringIO(z.read('baseline_case_comparison.csv').decode())))
            assert s['software_validation_cases']==38 and s['software_validation_expected_matches']==38
            assert s['ideal_qss_correct']==s['ideal_qss_trials']==720
            assert s['charge_discharge_pair_workflows_terminated']==6
            assert len(cases)==38 and all(c['reproduced'].lower()=='true' for c in cases)
        else:
            s=json.loads(z.read('security_summary.json'))
            rows=list(csv.DictReader(io.StringIO(z.read('security_attack_results.csv').decode())))
            limitations=list(csv.DictReader(io.StringIO(z.read('security_limitations.csv').decode())))
            spr=list(csv.DictReader(io.StringIO(z.read('security_requirements_matrix.csv').decode())))
            assert s['case_count']==s['expectations_matched']==len(rows)==80
            assert len(set(x['case_id'] for x in rows))==80
            assert all(x['matches_expectation'].lower()=='true' for x in rows)
            assert len(limitations)==7 and len(spr)==13
        print(f'{stage}: VERIFIED ({len(records)} manifest members, {len(z.namelist())} ZIP entries)')

if __name__=='__main__':
    check('stage01','qsv2g_stage01_baseline_results.zip','artifact_manifest.csv')
    check('stage02','qsv2g_stage02_security_results.zip','artifact_manifest.json')
    print('Both stage archives match their extracted bytes and recorded counts. This is NOT a security proof or Kaggle run attestation.')
