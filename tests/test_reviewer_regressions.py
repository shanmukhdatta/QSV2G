"""Focused source-level regressions; NOT physical/quantum-hardware validation.

FakePQC exercises protocol orchestration only. It MUST NOT be used to support
ML-KEM/ML-DSA strength, deployment, performance, or cryptographic claims.
"""
import hashlib
import hmac
import secrets
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from qsv2g_core import (
    ProtocolAbort, Traffic, decode_fields, encode, QSV2G, run_demo,
    new_qss_resource, AUTHORITIES,
)


class FakePQC:
    kind = 'TEST-ONLY-FAKE-PQC'

    def kem_keygen(self):
        k = secrets.token_bytes(32)
        return k, k

    def encaps(self, public):
        return b'test-ciphertext', hashlib.sha256(public).digest()

    def decaps(self, secret, ciphertext):
        if ciphertext != b'test-ciphertext':
            raise ProtocolAbort('bad test ciphertext')
        return hashlib.sha256(secret).digest()

    def sig_keygen(self):
        key = secrets.token_bytes(32)
        return key, key

    def sign(self, private, msg):
        return hmac.new(private, msg, 'sha256').digest()

    def verify(self, public, msg, sig):
        return hmac.compare_digest(self.sign(public, msg), sig)


def test_canonical_decoder_roundtrip_and_malformed():
    x = ('CHARGE', b'1234', {'unit': 'mWh', 'max': 10}, (1, 2))
    assert decode_fields(encode(*x)) == x
    with pytest.raises(ProtocolAbort):
        decode_fields(encode(*x)[:-1])


@pytest.mark.parametrize('pair', [('A', 'B'), ('A', 'C'), ('B', 'C')])
def test_full_ideal_workflow_with_each_approved_pair(pair):
    p = run_demo(crypto=FakePQC(), L=3, pair=pair)
    assert p.stage == 'TERMINATED', p.log
    assert p.resource.state == 'CONSUMED'
    assert p.ev_state.intent.op == 'CHARGE'
    assert p.approval_records[pair[0]][2] == p.resource.nu


@pytest.mark.parametrize('override', [
    {'ev_intent_op': 'DISCHARGE'},
    {'ev_intent_limit_mwh': 1000},
    {'ev_intent_lifetime_sec': 500},
])
def test_station_offer_conflicting_with_prior_ev_intent_is_rejected(override):
    p = run_demo(crypto=FakePQC(), L=1, **override)
    assert p.stage == 'SESSION'
    assert p.log[-1]['status'] == 'REJECTED'
    assert 'EV intent' in p.log[-1]['reason']


def test_discharge_operation_is_authenticated_end_to_end():
    p = run_demo(crypto=FakePQC(), L=1, op='DISCHARGE')
    assert p.stage == 'TERMINATED'
    assert p.ev_state.intent.op == 'DISCHARGE'


def test_tampered_kem_ev_proof_is_rejected():
    p = run_demo(crypto=FakePQC(), L=1, tamper_ev_kem=True)
    assert p.stage == 'AUTHENTICATED'
    assert p.log[-1]['status'] == 'REJECTED'
    assert 'KEM public key not authenticated' in p.log[-1]['reason']


def authenticated_token():
    p = QSV2G(crypto=FakePQC(), L=1)
    p.register(); p.authenticate(); p.establish_session()
    p.set_ev_intent(op='CHARGE', limit_mwh=12000, lifetime_sec=600)
    p.authorization_context(); p.authority_verify(); p.threshold_reconstruct()
    p.issue_token()
    return p


@pytest.mark.parametrize('attribute,new_value', [
    ('op', 'DISCHARGE'),
    ('limit', {'type': 'ENERGY', 'max': 99999, 'unit': 'mWh'}),
    ('vld', (1, 2)),
    ('ac', b'x' * 32),
])
def test_cs_mutation_cannot_mutate_prior_ev_intent(attribute, new_value):
    p = authenticated_token()
    original = p.ev_state.intent
    setattr(p, attribute, new_value)
    with pytest.raises(ProtocolAbort):
        p.protected_response()
    assert p.ev_state.intent is original
    assert p.ev_state.intent.op == 'CHARGE'
    assert p.ev_state.intent.limit_mwh == 12000


def test_token_replay_rejected_against_ev_side_seen_set():
    p = authenticated_token()
    p.protected_response()
    p.stage = 'TOKEN'  # Simulate replay delivery to EV, without executing START.
    with pytest.raises(ProtocolAbort, match='EV token replay'):
        p.protected_response()


def test_resource_approval_binds_explicit_proposal():
    p = QSV2G(crypto=FakePQC(), L=1)
    p.register(); p.authenticate(); p.establish_session()
    p.set_ev_intent(); p.authorization_context(); p.authority_verify()
    assert all(r[2] == p.resource.nu for r in p.approval_records.values())
    p.proposed_nu = 'unauthorized-proposal'
    with pytest.raises(ProtocolAbort, match='proposal changed'):
        p.threshold_reconstruct()


def test_resource_single_reservation_and_failed_recovery_consumes():
    r = new_qss_resource(L=1)
    ac = b'a' * 32
    r.reserve(ac, ('A', 'B'))
    with pytest.raises(ProtocolAbort, match='already reserved'):
        r.reserve(ac, ('B', 'C'))
    with pytest.raises(ProtocolAbort, match='reservation mismatch'):
        r.reconstruct(ac, ('B', 'C'), np.random.default_rng(1))
    # A mismatched pair must not consume the authorized pair's reservation.
    assert r.state == 'RESERVED'
    r.commitments['A'] = b'wrong commitment'
    with pytest.raises(ProtocolAbort, match='commitment mismatch'):
        r.reconstruct(ac, ('A', 'B'), np.random.default_rng(1))
    assert r.state == 'CONSUMED'
    with pytest.raises(ProtocolAbort):
        r.reserve(ac, ('A', 'B'))


def test_randomized_gcm_nonces_survive_counter_reset():
    key = secrets.token_bytes(32)
    traffic = Traffic(key)
    pkt1 = traffic.encrypt(b'first', b'ad')
    traffic.send_counter = 0  # Historical counter-reset fault.
    pkt2 = traffic.encrypt(b'second', b'ad')
    assert len(pkt1['nonce']) == len(pkt2['nonce']) == 12
    assert pkt1['nonce'] != pkt2['nonce']
    assert traffic.decrypt(pkt1, b'ad') == b'first'
    assert traffic.decrypt(pkt2, b'ad') == b'second'
    with pytest.raises(ProtocolAbort, match='duplicate'):
        traffic.decrypt(pkt1, b'ad')


def test_short_length_is_not_a_security_claim():
    # L=1 is used only to exercise state machines quickly, not to certify entropy.
    p = run_demo(crypto=FakePQC(), L=1)
    assert p.stage == 'TERMINATED'
    assert p.L == 1
    assert not p.resource.dealer_secrets  # resource secret erased on consumption


def test_only_one_concurrent_reservation_succeeds():
    resource=new_qss_resource(L=1)
    def attempt(pair):
        try:
            resource.reserve(b'a'*32,pair)
            return 'RESERVED'
        except ProtocolAbort:
            return 'REJECTED'
    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes=list(pool.map(attempt,[('A','B'),('B','C')]))
    assert sorted(outcomes)==['REJECTED','RESERVED']


def test_expired_token_is_rejected_at_ev():
    p=authenticated_token()
    with patch('qsv2g_core.time.time',return_value=p.ev_state.intent.validity[1]+1):
        with pytest.raises(ProtocolAbort,match='expired at EV'):
            p.protected_response()


def test_station_cannot_change_operation_after_authentication():
    p=QSV2G(crypto=FakePQC(),L=1)
    p.register();p.authenticate(op='CHARGE');p.establish_session();p.set_ev_intent()
    with pytest.raises(ProtocolAbort,match='changed authenticated operation'):
        p.authorization_context(op='DISCHARGE')
