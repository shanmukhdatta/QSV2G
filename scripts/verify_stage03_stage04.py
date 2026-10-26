#!/usr/bin/env python3
"""Verify Stage 03/04 source archive, extracted artifacts and experiment summary.
Runs read-only, no network or additional dependencies. Does not authenticate Kaggle provenance.
"""
from pathlib import Path
import zipfile,hashlib,json,csv,io,gzip,collections,statistics
ROOT=Path(__file__).resolve().parents[1]
def h(b):return hashlib.sha256(b).hexdigest()
def check(stage,archive,manifest_file):
    p=ROOT/'results'/stage/'submitted'/archive
    with zipfile.ZipFile(p) as z:
        assert z.testzip() is None
        manifest=json.loads(z.read(manifest_file))
        rows=manifest['files'];assert len(rows)+1==len(z.namelist())
        for item in rows:
            name=item['path'];b=z.read(name)
            assert len(b)==int(item['bytes']) and h(b)==item['sha256'],name
        for name in z.namelist():
            extracted=(ROOT/'results'/stage/'submitted'/'extracted'/name).read_bytes()
            assert extracted==z.read(name),f'Extract mismatch {stage}:{name}'
        log=('stage03_console_log.txt' if stage=='stage03' else 'run_log.txt')
        assert (ROOT/'logs'/stage/'submitted_notebook_log.txt').read_bytes()==z.read(log)
        return z,manifest
# This verifier reads original artifacts from fixed paths, not from the current network.
with zipfile.ZipFile(ROOT/'results/stage03/submitted/qsv2g_stage03_quantum_noise_results.zip') as z:
    assert z.testzip() is None
    ma=json.loads(z.read('stage03_artifact_manifest.json'))
    assert len(ma['files'])==19
    for r in ma['files']:
        b=z.read(r['path'])
        assert len(b)==r['bytes'] and h(b)==r['sha256'],r['path']
    assert all((ROOT/'results/stage03/submitted/extracted'/n).read_bytes()==z.read(n) for n in z.namelist())
    assert (ROOT/'logs/stage03/submitted_notebook_log.txt').read_bytes()==z.read('stage03_console_log.txt')
    ss=json.loads(z.read('stage03_summary.json'))
    assert ss['configurations']==315 and ss['total_trials']==315000
    agg=list(csv.DictReader(io.StringIO(z.read('noise_trial_aggregates.csv').decode())))
    assert len(agg)==315
    with gzip.open(io.BytesIO(z.read('noise_trial_events.csv.gz')),'rt',newline='') as f:
        reader=csv.DictReader(f)
        count=sum(1 for row in reader)
    assert count==315000,count
with zipfile.ZipFile(ROOT/'results/stage04/submitted/qsv2g_stage04_performance_results.zip') as z:
    assert z.testzip() is None
    ma=json.loads(z.read('manifest.json'));assert len(ma['files'])==27
    for r in ma['files']:
        b=z.read(r['path'])
        assert len(b)==r['bytes'] and h(b)==r['sha256'],r['path']
    assert all((ROOT/'results/stage04/submitted/extracted'/n).read_bytes()==z.read(n) for n in z.namelist())
    assert (ROOT/'logs/stage04/submitted_notebook_log.txt').read_bytes()==z.read('run_log.txt')
    ss=json.loads(z.read('stage04_summary.json'))
    assert (ss['full_workflows'],ss['resource_runs'],ss['authorization_microbenchmark_runs'])==(120,120,270)
    for filename,n in [('end_to_end_raw.csv',120),('qss_resource_scaling_raw.csv',120),('authorization_baselines_raw.csv',270)]:
        assert len(list(csv.DictReader(io.StringIO(z.read(filename).decode()))))==n,filename
assert (ROOT/'src/qsv2g_core.py').is_file(), 'Original reference source required'
core=(ROOT/'src/qsv2g_core.py').read_bytes()
assert h(core)=='2c86ca9eecbc5925100722119f061e640df03f993e14909b3078b23406330758'
print('OK: Stage 03 archive 19/19 SHA-256, 315 configurations and 315,000 trials')
print('OK: Stage 04 archive 27/27 SHA-256, 120+120+270 measurement rows')
print('OK: All extracted files and submitted notebook logs match original ZIPs byte-for-byte')
print('OK: Core source SHA-256 matches archived reference')
print('Scope: artifact-integrity verification only; not cloud-run attestation or security proof')
