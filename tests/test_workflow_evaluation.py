"""Stage 05 small regression tests with separate cryptographic evidence boundaries."""
import importlib.util
import sys
from pathlib import Path
import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from qsv2g.evaluation.workflows import (ClassicalResource, QuorumResource, q_probability,
                    vector_trial, full_transaction, PQCrypto, ProtocolAbort,
                    PAIRS, CHANNELS, staged_protocol, make_protocol)
from qsv2g.evaluation.analysis import wilson
from qsv2g_core import QSV2G


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
    model=(ROOT/'docs/formal/classical_consent.spthy').read_text()
    assert 'Assumed_Ideal_QSS_Gate' in model
    assert 'honest_execution_reachable' in model
    assert 'executed_once_per_session' in model
    # Tamarin's signing builtin reduces verify(...) to the nullary function
    # true, not the unrelated quoted public constant 'true'.
    assert ",true)" in model
    assert ",'true')" not in model


def test_comparator_preparation_does_not_create_discarded_qss(monkeypatch):
    import qsv2g_core
    def forbidden(*args, **kwargs):
        raise AssertionError('Classical baseline must not prepare QSS resource')
    monkeypatch.setattr(qsv2g_core,'new_qss_resource',forbidden)
    from test_protocol_regressions import FakePQC
    for variant in ('CLASSICAL_SHARING','QUORUM'):
        p,pre_ms=make_protocol(variant, FakePQC(),L=3,seed=9,pair=('A','B'))
        assert pre_ms>=0
        assert p.resource.state=='UNUSED'


def test_inclusive_timing_accounts_for_variant_setup():
    from test_protocol_regressions import FakePQC
    r=full_transaction('CLASSICAL_SHARING',FakePQC(),L=3,pair=('A','B'),seed=44)
    assert r['inclusive_software_ms']==pytest.approx(r['preparation_ms']+r['full_software_ms'])


def test_simulated_expiry_clips_partial_tick():
    from test_protocol_regressions import FakePQC
    from unittest.mock import patch
    p=QSV2G(crypto=FakePQC(),L=1)
    p.register();p.authenticate();p.establish_session()
    p.set_ev_intent(lifetime_sec=6)
    p.authorization_context(lifetime_sec=6);p.authority_verify()
    p.threshold_reconstruct();p.issue_token();p.protected_response()
    with patch('qsv2g_core.time.time',return_value=p.t0):
        p.execute(power_w=3600,seconds=20,tick_s=5)
    assert p.energy_mwh==pytest.approx(6000,abs=.01)
    assert p.log[-1]['ticks']==2


def test_simulated_execution_rejects_negative_power():
    from test_protocol_regressions import FakePQC
    p=QSV2G(crypto=FakePQC(),L=1)
    p.register();p.authenticate();p.establish_session();p.set_ev_intent()
    p.authorization_context();p.authority_verify();p.threshold_reconstruct()
    p.issue_token();p.protected_response()
    with pytest.raises(ProtocolAbort,match='invalid simulated power'):
        p.execute(power_w=-100)


@pytest.mark.parametrize('op',('CHARGE','DISCHARGE'))
def test_hypothesis_legitimate_context_tracks_authenticated_op(op):
    """Regression for Hypothesis-discovered DISCHARGE default-to-CHARGE mismatch."""
    from test_protocol_regressions import FakePQC
    p=QSV2G(crypto=FakePQC(),L=1)
    p.register(); p.authenticate(op=op); p.establish_session()
    p.set_ev_intent(op=p.op)
    p.authorization_context(op=p.ev_state.intent.op)
    p.authority_verify()
    p.threshold_reconstruct(pair=('A','C'))
    p.issue_token(); p.protected_response(); p.execute(); p.terminate()
    assert p.stage=='TERMINATED'
    assert p.ev_state.intent.op==op


def test_stateful_generator_has_one_always_enabled_rule():
    # Old many-precondition design triggered Hypothesis.filter_too_much on Kaggle.
    script=(ROOT/'src/qsv2g/evaluation/stateful.py').read_text()
    assert script.count('@rule(')==1
    assert '@precondition(' not in script
    assert 'def next_protocol_action(self,op,pair,mutation)' in script
    assert 'self.p.authorization_context(op=self.original_intent.op)' in script
    assert 'HealthCheck.filter_too_much' not in script


def _load_stateful_machine_without_hypothesis():
    """Exercise actual state transitions without claiming Hypothesis was executed.

    The fake decorators only allow a deterministic test of the machine's
    transition body on machines without Hypothesis installed. Kaggle runs the
    real Hypothesis campaign separately.
    """
    import types
    from unittest.mock import patch
    h=types.ModuleType('hypothesis')
    class HCheck: too_slow='too_slow'
    h.HealthCheck=HCheck
    h.settings=lambda **kwargs:kwargs
    h.strategies=types.SimpleNamespace(sampled_from=lambda x:x)
    stateful=types.ModuleType('hypothesis.stateful')
    stateful.RuleBasedStateMachine=object
    stateful.rule=lambda **kwargs:(lambda f:f)
    stateful.invariant=lambda **kwargs:(lambda f:f)
    stateful.run_state_machine_as_test=lambda *args,**kwargs:None
    spec=importlib.util.spec_from_file_location(
        'qsv2g_stateful_stub_runtime',ROOT/'src/qsv2g/evaluation/stateful.py')
    module=importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules,{'hypothesis':h,'hypothesis.stateful':stateful}):
        spec.loader.exec_module(module)
    return module.ProtocolStateMachine


@pytest.mark.parametrize('op',('CHARGE','DISCHARGE'))
@pytest.mark.parametrize('pair',PAIRS)
def test_stateful_phase_progress_and_legitimate_completion(op,pair):
    machine=_load_stateful_machine_without_hypothesis()()
    for _ in range(15):
        machine.next_protocol_action(op,pair,None)
        machine.original_ev_state_retained()
    assert machine.p.stage=='TERMINATED'
    assert machine.successful_execution and machine.stopped
    assert machine.p.ev_state.intent.op==op


@pytest.mark.parametrize('op',('CHARGE','DISCHARGE'))
@pytest.mark.parametrize('stage',('CONTEXT','APPROVED','RECONSTRUCTED','TOKEN'))
@pytest.mark.parametrize('change',('op','limit','vld','ac'))
def test_stateful_tampering_rejected_on_path_to_ev(op,stage,change):
    machine=_load_stateful_machine_without_hypothesis()()
    for _ in range(20):
        if machine.p.stage==stage:
            break
        machine.next_protocol_action(op,('B','C'),None)
        machine.original_ev_state_retained()
    assert machine.p.stage==stage
    machine.next_protocol_action(op,('B','C'),change)
    machine.original_ev_state_retained()
    assert machine.stopped and machine.mutated and machine.attack_rejected
    assert machine.p.stage!='EV_ACCEPTED'


def test_e3_real_pqc_endpoint_accepts_default_L162_in_ideal_channel():
    from qsv2g.evaluation.workflows import actual_noisy_token_trial
    try:
        crypto=PQCrypto()
    except RuntimeError:
        pytest.skip('real PQC backend unavailable')
    for pair in PAIRS:
        outcome=actual_noisy_token_trial(162,pair,'x',0.,crypto,seed=20261113)
        assert outcome=='ACCEPTED_AT_EV'


def test_formal_prover_lemma_parser_requires_explicit_summary():
    from run_tamarin import LEMMAS,parse_lemma_summary
    lines='\n'.join(f'{x} (all-traces): verified (3 steps)' for x in LEMMAS)
    assert len(parse_lemma_summary(lines))==len(LEMMAS)
    assert all(x=='verified' for x in parse_lemma_summary(lines).values())
    assert parse_lemma_summary('Some output with success but no lemmas')=={}
    assert parse_lemma_summary('honest_execution_reachable (exists-trace): falsified (0 steps)')=={
        'honest_execution_reachable':'falsified'}


def test_e5_run_reports_unavailable_without_claimed_proofs(tmp_path,monkeypatch):
    import run_tamarin
    monkeypatch.setattr(run_tamarin.shutil,'which',lambda *args,**kw:None)
    result=run_tamarin.run(tmp_path,timeout=1)
    assert result['parse_status']=='NOT_EXECUTED'
    assert result['proof_status']=='UNRESOLVED'
    assert result['prover_present'] is False
    assert (tmp_path/'e5_status.json').exists()


def test_release_install_rejects_bad_digest(tmp_path,monkeypatch):
    import install_tamarin
    import io
    monkeypatch.setattr(install_tamarin.urllib.request,'urlopen',lambda *a,**k:io.BytesIO(b'tampered'))
    with pytest.raises(RuntimeError,match='SHA-256 mismatch'):
        install_tamarin._checked_download('https://example.invalid/fake','0'*64,tmp_path/'bad.tar.gz')
    assert not (tmp_path/'bad.tar.gz').exists()


def test_e3_real_pqc_token_summary_covers_lengths(tmp_path):
    import json
    import pandas as pd
    from qsv2g.evaluation.analysis import analyze
    folder=tmp_path/'e3';folder.mkdir()
    pd.DataFrame([{'L':9,'pair':'AB','channel':'x','p':0.,'trial':0,
                   'outcome':'ACCEPTED_AT_EV'},
                  {'L':162,'pair':'AB','channel':'x','p':0.,'trial':0,
                   'outcome':'ACCEPTED_AT_EV'}]).to_csv(folder/'e3_token_trials.csv',index=False)
    (folder/'manifest.json').write_text(json.dumps({'params':{'token_lengths':[9,162]}}))
    s=analyze(tmp_path)
    assert s['e3_token_lengths']==[9,162]
    assert s['e3_real_pqc_token_attempts']==2
    assert (folder/'e3_token_summary_with_ci.csv').exists()
    (folder/'manifest.json').write_text(json.dumps({'params':{'token_lengths':[9,27,162]}}))
    with pytest.raises(RuntimeError,match='coverage incomplete'):
        analyze(tmp_path)
