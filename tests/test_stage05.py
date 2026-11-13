"""Stage 05 small regression tests with separate cryptographic evidence boundaries."""
import importlib.util
import sys
from pathlib import Path
import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'experiments/stage05'))
sys.path.insert(0,str(ROOT/'src'))
from runner import (ClassicalResource, QuorumResource, q_probability,
                    vector_trial, full_transaction, PQCrypto, ProtocolAbort,
                    PAIRS, CHANNELS, staged_protocol)
from analyze import wilson


@pytest.mark.parametrize('pair',PAIRS)
def test_classical_threshold_ideal_pair(pair):
    resource=ClassicalResource.prepare(27)
    expect=[sum(resource.dealer_secrets[a][j] for a in ('A','B','C'))%3 for j in range(27)]
    resource.reserve(b'context',pair)
    recovered=resource.reconstruct(b'context',pair,np.random.default_rng(2026))
    assert recovered==expect
    assert resource.state=='CONSUMED'
    assert not resource.dealer_secrets and not resource.shares


def test_classical_tamper_consumes():
    resource=ClassicalResource.prepare(9);resource.reserve(b'ctx',('A','B'))
    with pytest.raises(ProtocolAbort,match='commitment mismatch'):
        resource.reconstruct(b'ctx',('A','B'),np.random.default_rng(4),tamper=True)
    assert resource.state=='CONSUMED'


def test_quorum_does_not_recover_shares():
    resource=QuorumResource();resource.reserve(b'ctx',('A','B'))
    assert resource.reconstruct(b'ctx',('A','B'),np.random.default_rng(1))==['NO_SECRET_RECOVERY']


@pytest.mark.parametrize('channel',CHANNELS)
def test_ideal_noise_model_always_eligible(channel):
    for pair in PAIRS:
        for _ in range(5):
            assert vector_trial(9,pair,channel,0.0,np.random.default_rng(13))=='COMMITMENT_GATE_ELIGIBLE'


def test_noise_model_edge_cases():
    for pair in PAIRS:
        assert vector_trial(3,pair,'erasure',1.,np.random.default_rng(1))=='ERASURE_ABORT'
        assert vector_trial(3,pair,'x',1.,np.random.default_rng(1))=='COMMITMENT_REJECT'
    assert q_probability('depolarize',1)==pytest.approx(1/3)
    assert q_probability('combined',.3)==pytest.approx(.59)
    assert wilson(0,10)[0]==0
    assert wilson(10,10)[1]==pytest.approx(1)


def test_authority_offline_rechecks_before_recovery_or_signing():
    try:crypto=PQCrypto()
    except RuntimeError:pytest.skip('actual PQC library not installed')
    p=staged_protocol(crypto)
    p.authority_verify();p.available.remove('B')
    with pytest.raises(ProtocolAbort,match='offline before reconstruction'):
        p.threshold_reconstruct(pair=('A','B'))
    q=staged_protocol(crypto)
    q.authority_verify();q.threshold_reconstruct(pair=('A','B'))
    q.available.remove('B')
    with pytest.raises(ProtocolAbort,match='offline before token issuance'):
        q.issue_token()


@pytest.mark.parametrize('variant',('QUORUM','CLASSICAL_SHARING','QSS'))
def test_real_crypto_comparators_complete(variant):
    try:crypto=PQCrypto()
    except RuntimeError:pytest.skip('actual PQC library not installed')
    row=full_transaction(variant,crypto,L=3,pair=('B','C'),seed=17)
    assert row['status']=='TERMINATED'
    assert row['signature_count']==2
    assert row['resource_consumed']=='CONSUMED'


def test_formal_model_has_explicit_assumption():
    model=(ROOT/'formal/qsv2g_classical_consent.spthy').read_text()
    assert 'Assumed_Ideal_QSS_Gate' in model
    assert 'honest_execution_reachable' in model
    assert 'executed_once_per_session' in model
