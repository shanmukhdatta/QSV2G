"""Smoke checks for the separate exploratory vector model, not field validation."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from qsv2g.evaluation.full_vector import experiment


def test_no_noise_accepts_all_vectors():
    result=experiment(9,0.0,10,seed=123)
    assert result['accepted']==10
    assert result['commitment_rejects']==0


def test_certain_x_fault_rejects_all_vectors():
    result=experiment(9,1.0,10,seed=123)
    assert result['accepted']==0
    assert result['commitment_rejects']==10


def test_seeded_results_are_reproducible():
    assert experiment(9,.02,10,seed=17)==experiment(9,.02,10,seed=17)
