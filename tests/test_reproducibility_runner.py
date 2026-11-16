import importlib.util
import json
import subprocess
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('runner',ROOT/'scripts/run_experiment.py')
runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)

def test_validation_seed_is_forwarded():
    command=runner.build_command('validation',False,Path('out'),73)
    assert command[command.index('--seed')+1]=='73'

def test_run_refuses_existing_results(tmp_path):
    dest=tmp_path/'validation';dest.mkdir();(dest/'important.csv').write_text('old')
    with pytest.raises(FileExistsError):runner.run_study('validation',False,tmp_path,73)
    assert (dest/'important.csv').read_text()=='old'

def test_failed_process_has_provenance(tmp_path,monkeypatch):
    monkeypatch.setattr(runner,'execute',lambda command:subprocess.CompletedProcess(command,7,'','failure'))
    with pytest.raises(RuntimeError):runner.run_study('validation',False,tmp_path,73)
    data=json.loads((tmp_path/'validation/execution.json').read_text())
    assert data['returncode']==7 and data['seed']==73
    assert data['source_sha256'] and data['outputs_sha256']['console.log']

def test_analysis_rejects_no_trials(tmp_path):
    from qsv2g.evaluation.analysis import analyze
    with pytest.raises(ValueError,match='No supported trial'):
        analyze(tmp_path)

def test_analysis_finds_named_runner_directory(tmp_path):
    from qsv2g.evaluation.analysis import analyze
    dest=tmp_path/'security/e2';dest.mkdir(parents=True)
    (dest/'e2_cases.csv').write_text('match\nTrue\nFalse\n')
    with pytest.raises(RuntimeError,match='mismatched'):
        analyze(tmp_path)

def test_run_claims_directory_exclusively(tmp_path,monkeypatch):
    # An existing empty directory may belong to another run between mkdir and metadata write.
    (tmp_path/'validation').mkdir()
    monkeypatch.setattr(runner,'execute',lambda command:subprocess.CompletedProcess(command,0,'',''))
    with pytest.raises(FileExistsError):runner.run_study('validation',False,tmp_path,73)
