"""Run the supported published study families; defaults to a bounded preflight."""
import subprocess,sys
from pathlib import Path
if __name__=='__main__':
 args=[sys.executable,str(Path(__file__).parent/'run_experiment.py'),'--study','all',*sys.argv[1:]]
 raise SystemExit(subprocess.call(args))
