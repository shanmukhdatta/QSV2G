"""Stage 06 P0/P1/P2; fake only for isolated fast property tests; real-PQC in runner."""
import math
import sys
from pathlib import Path

import numpy as np
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'tests')]
from qsv2g.evaluation.adversarial import (STAGES,VARIANTS,PAIRS,execute_probe,marginal_and_pair_distributions,
                      initial_protocol, change_dealer_secret_with_matching_commitment)
from qsv2g.evaluation.retries import prob_one_vector,trial_budget
from test_protocol_regressions import FakePQC
from qsv2g_core import PQCrypto, ProtocolAbort


@pytest.mark.parametrize('variant',VARIANTS)
@pytest.mark.parametrize('scenario',STAGES)
def test_p0_p1_expected_simulated_attacks(variant,scenario):
    record=execute_probe(variant,scenario,FakePQC(),L=3,pair=('A','B'),op='CHARGE',seed=17)
    assert record['match'],record
    assert record['crypto_backend']=='TEST-ONLY-FAKE-PQC'
    if scenario=='two_signers_skip_reconstruction':
        assert record['outcome']=='EV_ACCEPTED_NO_RECONSTRUCTION'
        assert record['qss_or_classical_resource_state']=='UNUSED'
        assert record['compromised_cs_in_test_harness']
    if scenario=='one_signer_fake_digest':
        assert record['outcome']=='REJECTED'
    if scenario=='one_approval':
        assert record['outcome']=='REJECTED'


@pytest.mark.parametrize('variant',VARIANTS)
@pytest.mark.parametrize('pair',PAIRS)
@pytest.mark.parametrize('op',['CHARGE','DISCHARGE'])
def test_pair_and_operation_honest_path(variant,pair,op):
    record=execute_probe(variant,'honest_control',FakePQC(),L=3,pair=pair,op=op,seed=4)
    assert record['match']
    assert record['outcome']=='EV_ACCEPTED'
    assert not record['compromised_cs_in_test_harness']


def test_exact_marginal_and_pair_equivalence():
    rows=marginal_and_pair_distributions()
    assert len(rows)==9
    assert all(x['computational_basis_total_variation']<1e-12 for x in rows)
    assert all(x['qss_single_share_distance_to_uniform']<1e-12 for x in rows)
    assert set(x['pair'] for x in rows)=={'AB','AC','BC'}


@pytest.mark.parametrize('length',[9,27,81,162])
def test_ideal_reliability_and_resource_cost(length):
    for channel in ('x','dephase','depolarize','erasure','combined'):
        z=trial_budget(length,channel,0,30,100,np.random.default_rng(3))
        assert z['analytic_budget_acceptance']==1
        assert z['observed_budget_acceptance']==1
        assert z['observed_mean_attempts']==1
        assert z['analytic_stored_qutrits']==9*length


def test_full_gate_noise_formula():
    expected=0.99**(3*162)
    assert prob_one_vector(162,'x',.01)==pytest.approx(expected)
    values=[trial_budget(162,'x',.01,b,1000,np.random.default_rng(9)) for b in (1,3,10,30)]
    assert all(a['analytic_budget_acceptance']<b['analytic_budget_acceptance'] for a,b in zip(values,values[1:]))
    assert values[0]['analytic_mean_attempts']==pytest.approx(1)
    assert values[-1]['analytic_mean_attempts']>20
    assert values[-1]['analytic_budget_acceptance']<.25


def test_rare_events_model_does_not_claim_observed_improvement():
    z=trial_budget(162,'combined',.03,10,200,np.random.default_rng(1))
    assert z['analytic_budget_acceptance']<.01
    assert z['analytic_budget_acceptance'] < 1e-8
    assert z['observed_budget_acceptance'] == 0


@pytest.mark.parametrize('variant',VARIANTS)
def test_real_pqc_conditional_trust_boundary(variant):
    """Real ML-DSA signature checks, not fake backend, for critical conditional bypass."""
    crypto=PQCrypto()
    a=execute_probe(variant,'one_signer_fake_digest',crypto,3,('A','B'),'CHARGE',1)
    b=execute_probe(variant,'two_signers_skip_reconstruction',crypto,3,('A','B'),'CHARGE',2)
    assert a['match'] and a['outcome']=='REJECTED'
    assert b['match'] and b['outcome']=='EV_ACCEPTED_NO_RECONSTRUCTION'
    assert 'ML-DSA-65' in b['crypto_backend']


def test_p3_wrapper_does_not_invent_proofs_when_missing(tmp_path):
    from run_formal import run
    status=run(tmp_path,bin_path=tmp_path/'intentionally_missing_tamarin')
    assert status['status']=='NOT_EXECUTED'
    assert status['proof_status']=='UNRESOLVED'
    assert (tmp_path/'p3_status.json').exists()


def test_p3_candidate_explicitly_models_compromise_not_quantum_security():
    theory=(ROOT/'docs/formal/compromise_analysis.spthy').read_text()
    assert all(name in theory for name in ('Reveal_UC_A','Reveal_UC_B','Reveal_CS',
                 'Assumed_Honest_QSS_Reconstruction','bypass_possible_with_full_compromise'))
    assert 'NOT YET EXECUTED' in theory
