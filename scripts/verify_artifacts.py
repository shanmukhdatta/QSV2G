#!/usr/bin/env python3
"""Integrity checks for supplied research artifacts. Does not rerun experiments."""
from __future__ import annotations
import hashlib, json, csv, io, zipfile, sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
SRC='2c86ca9eecbc5925100722119f061e640df03f993e14909b3078b23406330758'
TEX='4ca43b1f6debd2e2bf314ff9adf74f0ad08ba1702e1055eca1943b9533290ef2'
errors=[]
def ck(condition,detail):
    if not condition: errors.append(detail)
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
ck(digest(R/'src/qsv2g_core.py')==SRC,'Reference code SHA-256 mismatch')
ck(digest(R/'protocol/QSV2G_main8_SectionIV_Revised.tex')==TEX,'Referenced protocol LaTeX SHA-256 mismatch')
for p in R.glob('notebooks/**/*.ipynb'):
    try:
        n=json.loads(p.read_text()); ck(isinstance(n.get('cells'),list),f'{p}: cells missing')
    except Exception as e: errors.append(f'{p}: invalid notebook: {e}')
for a in sorted((R/'results/archives').glob('*.zip')):
    try:
        with zipfile.ZipFile(a) as z:
            ck(z.testzip() is None, f'{a}: bad compressed member')
            if a.name=='final_validation_submitted.zip':
                s=json.loads(z.read('validation_summary.json'))
                cases=list(csv.DictReader(io.StringIO(z.read('validation_case_results.csv').decode())))
                ck(len(cases)==s['test_count']==38,'Final validation case count mismatch')
                ck(sum(x['pass'].lower()=='true' for x in cases)==s['expected_outcomes_matched']==38,'Expected-outcome count mismatch')
                ck(s['qss_ideal_pair_trials']==s['qss_ideal_correct']==720,'720-trial summary mismatch')
                ck(s['source_implementation_sha256']==SRC,'Source digest in final summary mismatch')
                ck(s['revised_tex_sha256']==TEX,'Protocol digest in final summary mismatch')
            for ent in z.infolist():
                if ent.is_dir(): continue
                path=None
                if ent.filename.endswith('.png'):
                    tag={'full_protocol_openssl_reported.zip':'openssl','full_protocol_pqcrypto_reported.zip':'pqcrypto','quantum_validation_variant_A.zip':'quantum_variant_A','quantum_validation_variant_B.zip':'quantum_variant_B'}.get(a.name)
                    if tag: path=R/'figures/experimental'/tag/Path(ent.filename).name
                elif a.name=='final_validation_submitted.zip': path=R/'results/final_validation'/ent.filename
                elif a.name=='full_protocol_openssl_reported.zip': path=R/'results/full_protocol_openssl'/ent.filename
                elif a.name=='full_protocol_pqcrypto_reported.zip': path=R/'results/full_protocol_pqcrypto'/ent.filename
                elif a.name.startswith('quantum_validation_variant_A'): path=R/'results/quantum_validation'/ent.filename
                if path is not None and (path.suffix.lower() in ('.csv','.json','.txt','.png')):
                    ck(path.exists() and path.read_bytes()==z.read(ent), f'Extracted artifact mismatch: {path.relative_to(R)}')
    except Exception as e: errors.append(f'{a}: {e}')
rows=list(csv.DictReader((R/'results/final_validation/validation_case_results.csv').open()))
ck(len(rows)==38,'Extracted 38-case table malformed')
ck(sum(x['type']=='known_limitation' for x in rows)==4,'Expected 4 documented known-limitation cases')
if errors:
    for error in errors: print('FAIL',error)
    sys.exit(1)
print('PASS: notebook JSON, source/LaTeX hashes, all ZIP CRCs, extracted datasets/plots, 38 cases, 4 known limitations and 720 ideal trials.')
print('Scope: checks provenance and reported output consistency only. Experiments not rerun; no cryptographic security proof.')
