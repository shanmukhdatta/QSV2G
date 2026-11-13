"""Optional Kaggle/Linux E5 binary installer with upstream SHA-256 pinning.

Uses official Tamarin 1.12.0 and Maude 3.5.1 x86_64 release archives.
No sudo/apt, no source builds, no changes outside --tools-dir/--out.
Installation success DOES NOT imply any theorem proved.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import tarfile
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ASSETS = {
    'tamarin-prover': (
        'https://github.com/tamarin-prover/tamarin-prover/releases/download/1.12.0/tamarin-prover-1.12.0-linux64-ubuntu.tar.gz',
        '201be06f469e47cff554df6ca93db8366fc2c69d70c61fcbd1370a1074b469c6'),
    'maude': (
        'https://github.com/maude-lang/Maude/releases/download/Maude3.5.1/Maude-3.5.1-linux-x86_64.zip',
        '72ed1ca87e3b3d0dfc6ee1436baf154bf04c45ff97d521bec040c5e8dfc8f92c'),
}

def _checked_download(url, expected, path):
    request=urllib.request.Request(url, headers={'User-Agent':'QSV2G-E5-research-setup/1.0'})
    with urllib.request.urlopen(request, timeout=90) as src, open(path, 'wb') as dst:
        sha=hashlib.sha256()
        while True:
            chunk=src.read(1024*1024)
            if not chunk:break
            dst.write(chunk);sha.update(chunk)
    observed=sha.hexdigest()
    if observed!=expected:
        path.unlink(missing_ok=True)
        raise RuntimeError(f'Upstream archive SHA-256 mismatch for {url}: expected {expected}, got {observed}')
    return observed

def _safe_extract_tar(archive, dest):
    # Only regular files and directories; never follow paths/symlinks out of dest.
    with tarfile.open(archive,'r:gz') as tf:
        for member in tf.getmembers():
            p=Path(member.name)
            if p.is_absolute() or '..' in p.parts or not (member.isfile() or member.isdir()):
                raise RuntimeError('Unsafe upstream tar entry: '+member.name)
        tf.extractall(dest, filter='data')

def _safe_extract_zip(archive, dest):
    with zipfile.ZipFile(archive) as z:
        for member in z.infolist():
            p=Path(member.filename)
            if p.is_absolute() or '..' in p.parts:
                raise RuntimeError('Unsafe upstream zip entry: '+member.filename)
        z.extractall(dest)

def _locate(root, names):
    for name in names:
        found=[p for p in root.rglob(name) if p.is_file()]
        if found:return found[0]
    raise RuntimeError('Expected executable or dependency not present: '+str(names))

def install(tools_dir, status_file):
    tools_dir=Path(tools_dir).resolve(); status_file=Path(status_file).resolve()
    tools_dir.mkdir(parents=True,exist_ok=True); status_file.parent.mkdir(parents=True,exist_ok=True)
    info={'utc':datetime.now(timezone.utc).isoformat(),'platform':platform.platform(),
          'architecture':platform.machine(),'source':'official GitHub release assets',
          'status':'UNRESOLVED','tools_dir':str(tools_dir),'archives':{}}
    try:
        if platform.system()!='Linux' or platform.machine() not in ('x86_64','AMD64'):
            raise RuntimeError('Installer only supports Linux x86_64; use official Tamarin instructions otherwise')
        bin_dir=tools_dir/'bin';bin_dir.mkdir(exist_ok=True)
        for name,(url,digest) in ASSETS.items():
            extension='.tar.gz' if name=='tamarin-prover' else '.zip'
            archive=tools_dir/(name+extension)
            observed=_checked_download(url,digest,archive)
            info['archives'][name]={'url':url,'sha256':observed,'bytes':archive.stat().st_size}
            dest=tools_dir/(name+'_extracted')
            dest.mkdir(exist_ok=True)
            if extension=='.zip':_safe_extract_zip(archive,dest)
            else:_safe_extract_tar(archive,dest)
            binary=_locate(dest, (name,))
            # Maude must find prelude.maude in its binary's directory.
            shutil.copy2(binary, bin_dir/name)
            (bin_dir/name).chmod(0o755)
            if name=='maude':
                prelude=_locate(dest,('prelude.maude',))
                shutil.copy2(prelude,bin_dir/'prelude.maude')
        env=os.environ.copy();env['PATH']=str(bin_dir)+os.pathsep+env.get('PATH','')
        versions={}
        for name in ASSETS:
            proc=subprocess.run([str(bin_dir/name),'--version'],capture_output=True,text=True,timeout=25,env=env,cwd=bin_dir)
            versions[name]={'returncode':proc.returncode,'stdout':proc.stdout[-800:],'stderr':proc.stderr[-800:]}
            if proc.returncode!=0:
                raise RuntimeError(f'{name} failed --version ({proc.returncode}); inspect install_status.json')
        info['versions']=versions
        info['status']='AVAILABLE_NOT_PROVEN'
    except Exception as exc:
        info['reason']=str(exc)
    finally:
        status_file.write_text(json.dumps(info,indent=2))
    return info

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--tools-dir',type=Path,required=True)
    p.add_argument('--status',type=Path,required=True)
    args=p.parse_args()
    print(json.dumps(install(args.tools_dir,args.status),indent=2))
