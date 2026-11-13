"""One genuine OpenSSL/pqcrypto software backend smoke test when available.

This test uses ML-KEM-768 and ML-DSA-65 implementations. It does not exercise
quantum networking, real EVs, hardware charging, or cryptographic proofs.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from qsv2g_core import PQCrypto, run_demo


def test_real_pqc_backend_charge_and_discharge():
    try:
        crypto=PQCrypto()
    except RuntimeError as exc:
        pytest.skip(f'standardized PQC backend unavailable: {exc}')
    assert 'ML-KEM-768' in crypto.kind and 'ML-DSA-65' in crypto.kind
    for op in ('CHARGE','DISCHARGE'):
        p=run_demo(crypto=crypto, L=3, op=op)
        assert p.stage=='TERMINATED',p.log
        assert p.ev_state.intent.op==op
        assert p.resource.state=='CONSUMED'
    p=run_demo(crypto=crypto, L=3, tamper_ev_kem=True)
    assert p.log[-1]['status']=='REJECTED'
    assert 'KEM public key not authenticated' in p.log[-1]['reason']
