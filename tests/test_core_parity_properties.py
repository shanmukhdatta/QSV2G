"""Mathematical and lifecycle invariants after source extraction."""
import numpy as np
import pytest
from qsv2g import qss_state, recover_symbol, QSV2G, ProtocolAbort
from qsv2g.evaluation.workflows import ClassicalResource, q_probability, vector_trial
from test_protocol_regressions import FakePQC
@pytest.mark.parametrize('secret',[0,1,2])
def test_each_qutrit_state_has_one_third_pair_basis_law(secret):
    psi=qss_state(secret)
    assert np.sum(np.abs(psi)**2)==pytest.approx(1)
    nz=np.flatnonzero(np.abs(psi).reshape(-1)>1e-14)
    assert len(nz)==3
    assert np.allclose(np.abs(psi).reshape(-1)[nz]**2,1/3)
@pytest.mark.parametrize('pair',[('A','B'),('A','C'),('B','C')])
def test_classical_share_recovery_matches_code_basis(pair):
    res=ClassicalResource.prepare(3)
    original=[sum(res.dealer_secrets[a][j] for a in ('A','B','C'))%3 for j in range(3)]
    res.reserve(b'ctx',pair)
    assert res.reconstruct(b'ctx',pair,np.random.default_rng(1))==original
def test_noise_formula_at_zero():
    for model in ['x','dephase','depolarize','erasure','combined']:
        assert q_probability(model,0)==1
        assert vector_trial(9,('A','B'),model,0,np.random.default_rng(1))=='COMMITMENT_GATE_ELIGIBLE'
def test_replay_after_first_accepted_state():
    p=QSV2G(crypto=FakePQC(),L=3)
    p.register();p.authenticate();p.establish_session();p.set_ev_intent();p.authorization_context()
    p.authority_verify();p.threshold_reconstruct();p.issue_token();p.protected_response()
    with pytest.raises(ProtocolAbort):p.protected_response()
