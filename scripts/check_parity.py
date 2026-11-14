"""Check exact AST parity against original historical src/qsv2g_core.py.

Usage: python scripts/check_parity.py [--original /path/to/original_core.py]
Without --original, uses original Git revision through the local git history.
"""
from __future__ import annotations
import argparse,ast,subprocess
from pathlib import Path
ORIGINAL='f981f986f1bc01be5f85624da74ff55c20474339'
def main():
    p=argparse.ArgumentParser();p.add_argument('--original',type=Path)
    a=p.parse_args()
    root=Path(__file__).resolve().parents[1]
    if a.original:
        raw=a.original.read_text()
    else:
        result=subprocess.run(['git','show',ORIGINAL+':src/qsv2g_core.py'],cwd=root,text=True,capture_output=True)
        if result.returncode:
            raise SystemExit('Original revision not present locally; supply --original PATH or fetch the preserved archive branch.')
        raw=result.stdout
    orig={n.name:n for n in ast.parse(raw).body if isinstance(n,(ast.ClassDef,ast.FunctionDef))}
    refactored={}
    for f in (root/'src/qsv2g').glob('*.py'):
        for n in ast.parse(f.read_text()).body:
            if isinstance(n,(ast.ClassDef,ast.FunctionDef)):
                refactored[n.name]=n
    missing=sorted(set(orig)-set(refactored))
    changed=sorted(k for k in orig.keys()&refactored.keys()
                   if ast.dump(orig[k],include_attributes=False)!=ast.dump(refactored[k],include_attributes=False))
    print('Legacy classes/functions:',len(orig),'migrated:',len(orig)-len(missing),'missing:',missing,'changed:',changed)
    if missing or changed:raise SystemExit(1)
    print('PASS: all source functions/classes preserve exact AST bodies')
if __name__=='__main__':main()
