"""E2 optional Hypothesis stateful test runner with a TEST-ONLY PQC substitute.

The property campaign tests Python protocol state transitions, not cryptographic
security. It uses the same QSV2G source under test; genuine ML-KEM/ML-DSA attack
checks are separately exercised by E2 and existing real-backend unit tests.
"""
from __future__ import annotations
import hashlib
import hmac
import json
import secrets
import sys
from pathlib import Path

from hypothesis import HealthCheck, settings, strategies as st
from hypothesis.stateful import RuleBasedStateMachine, initialize, invariant, precondition, rule, run_state_machine_as_test

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from qsv2g_core import QSV2G, ProtocolAbort


class TestOnlyPQC:
    kind='TEST_ONLY_HMAC_STUB_NOT_PQC'
    def kem_keygen(self):
        k=secrets.token_bytes(32);return k,k
    def encaps(self,pk):return b'fake_ct',hashlib.sha256(pk).digest()
    def decaps(self,sk,ct):
        if ct!=b'fake_ct':raise ProtocolAbort('fake KEM mismatch')
        return hashlib.sha256(sk).digest()
    def sig_keygen(self):
        sk=secrets.token_bytes(32);return sk,sk
    def sign(self,sk,msg):return hmac.new(sk,msg,hashlib.sha256).digest()
    def verify(self,pk,msg,sig):return hmac.compare_digest(self.sign(pk,msg),sig)


class ProtocolStateMachine(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        self.p=QSV2G(crypto=TestOnlyPQC(),L=1)
        self.original_intent=None
        self.mutated=False
        self.successful_execution=False
        self.stopped=False

    @precondition(lambda self:not self.stopped and self.p.stage=='NEW')
    @rule()
    def registration(self):self.p.register()

    @precondition(lambda self:not self.stopped and self.p.stage=='REGISTERED')
    @rule(op=st.sampled_from(['CHARGE','DISCHARGE']))
    def authentication(self,op):self.p.authenticate(op=op)

    @precondition(lambda self:not self.stopped and self.p.stage=='AUTHENTICATED')
    @rule()
    def session(self):self.p.establish_session()

    @precondition(lambda self:not self.stopped and self.p.stage=='SESSION' and self.original_intent is None)
    @rule()
    def freeze_intent(self):
        self.p.set_ev_intent(op=self.p.op)
        self.original_intent=self.p.ev_state.intent

    @precondition(lambda self:not self.stopped and self.p.stage=='SESSION' and self.original_intent is not None)
    @rule()
    def context(self):self.p.authorization_context()

    @precondition(lambda self:not self.stopped and self.p.stage=='CONTEXT')
    @rule()
    def approve(self):self.p.authority_verify()

    @precondition(lambda self:not self.stopped and self.p.stage=='APPROVED')
    @rule(pair=st.sampled_from([('A','B'),('A','C'),('B','C')]))
    def recover(self,pair):self.p.threshold_reconstruct(pair=pair)

    @precondition(lambda self:not self.stopped and self.p.stage=='RECONSTRUCTED')
    @rule()
    def sign(self):self.p.issue_token()

    @precondition(lambda self:not self.stopped and self.p.stage=='TOKEN')
    @rule()
    def verify_at_ev(self):
        try:self.p.protected_response()
        except ProtocolAbort:
            # Tampering CS state must not gain EV acceptance.
            if not self.mutated:raise
            self.stopped=True
        else:
            assert not self.mutated

    @precondition(lambda self:not self.stopped and self.p.stage=='EV_ACCEPTED')
    @rule()
    def execute(self):
        self.p.execute();self.successful_execution=True

    @precondition(lambda self:not self.stopped and self.p.stage=='EXECUTED')
    @rule()
    def finish(self):self.p.terminate();self.stopped=True

    @precondition(lambda self:not self.stopped and self.original_intent is not None and self.p.stage in ('CONTEXT','APPROVED','RECONSTRUCTED','TOKEN'))
    @rule(change=st.sampled_from(['op','limit','vld','ac']))
    def station_tamper(self,change):
        if change=='op':self.p.op='DISCHARGE' if self.p.op=='CHARGE' else 'CHARGE'
        elif change=='limit':self.p.limit={'type':'ENERGY','max':99999,'unit':'mWh'}
        elif change=='vld':self.p.vld=(1,2)
        elif change=='ac':self.p.ac=b'Z'*32
        self.mutated=True
        # Future actions may fail early; do not misclassify safe rejection as a test bug.
        self.stopped=True
        try:
            if self.p.stage=='TOKEN':self.p.protected_response()
            elif self.p.stage=='CONTEXT':self.p.authority_verify()
            elif self.p.stage=='APPROVED':self.p.threshold_reconstruct()
            elif self.p.stage=='RECONSTRUCTED':self.p.issue_token()
        except ProtocolAbort:pass
        else:
            if self.p.stage=='EV_ACCEPTED':raise AssertionError('tampered station accepted by EV')

    @rule()
    def idle_after_terminal_or_attack(self):
        # Hypothesis requires at least one enabled rule after a terminal state.
        pass

    @invariant()
    def original_ev_state_retained(self):
        if self.original_intent is not None:
            assert self.p.ev_state.intent==self.original_intent
        if self.successful_execution:
            assert self.p.stage in ('EXECUTED','TERMINATED')
            assert len(self.p.executed)==1


def run_campaign(examples=1000,steps=50):
    run_state_machine_as_test(ProtocolStateMachine,settings=settings(
        max_examples=examples,stateful_step_count=steps,deadline=None,
        derandomize=True,database=None,suppress_health_check=[HealthCheck.too_slow]))
    return dict(examples_requested=examples,steps_requested=steps,status='PASS',
                backend='TEST_ONLY_HMAC_STUB_NOT_PQC',
                caveat='Hypothesis generated state sequences do not prove unbounded security')


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--examples',type=int,default=1000)
    parser.add_argument('--steps',type=int,default=50)
    parser.add_argument('--output',type=Path)
    opts=parser.parse_args()
    result=run_campaign(opts.examples,opts.steps)
    if opts.output:
        opts.output.parent.mkdir(parents=True,exist_ok=True)
        opts.output.write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
