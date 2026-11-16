import pandas as pd
import pytest
from qsv2g.evaluation.evidence import checked_counts, checked_medians

def test_unknown_noise_outcome_is_not_ignored():
    with pytest.raises(ValueError):checked_counts(pd.Series(['PASS','UNKNOWN']),{'PASS':1})

def test_counts_require_exact_total():
    with pytest.raises(ValueError):checked_counts(pd.Series(['PASS','PASS']),{'PASS':1})

def test_incomplete_timing_campaign_cannot_certify_medians():
    with pytest.raises(ValueError):checked_medians(pd.DataFrame({'status':['REJECTED']}))
