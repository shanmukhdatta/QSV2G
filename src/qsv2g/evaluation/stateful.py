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
from hypothesis.stateful import RuleBasedStateMachine, invariant, rule, run_state_machine_as_test

ROOT=Path(__file__).resolve().parents[3]
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
    """Protocol-aware generated sequences, without filtering phase-invalid rules.

    A single always-enabled Hypothesis rule advances the *current* state. This is
    deliberate: the old design had eleven mostly-disabled rules, and Hypothesis
    failed its filter_too_much health check after discarding 50 inputs. Choices
    still vary operation, selected authority pair and tampering point/type.
    """
    def __init__(self):
        super().__init__()
        self.p=QSV2G(crypto=TestOnlyPQC(),L=1)
        self.original_intent=None
        self.successful_execution=False
        self.stopped=False
        self.mutated=False
        self.attack_rejected=False
        self.steps_executed=0

    def _tamper_and_check(self,change,pair):
        """Try progressing to endpoint after a station-side mutation.

        A safe intermediate abort is acceptable; a mutated permission reaching
        EV_ACCEPTED is a failure. Do not simply stop after tampering without
        exercising the downstream checks.
        """
        if change=='op':
            self.p.op='DISCHARGE' if self.p.op=='CHARGE' else 'CHARGE'
        elif change=='limit':
            self.p.limit={'type':'ENERGY','max':99999,'unit':'mWh'}
        elif change=='vld':
            self.p.vld=(1,2)
        elif change=='ac':
            self.p.ac=b'Z'*32
        else:
            raise AssertionError(f'unknown mutation: {change}')
        self.mutated=True
        self.stopped=True
        try:
            # Advance through real protocol checks instead of assuming an attack
            # is rejected merely because an early check happened to pass.
            while self.p.stage in ('CONTEXT','APPROVED','RECONSTRUCTED','TOKEN'):
                if self.p.stage=='CONTEXT':
                    self.p.authority_verify()
                elif self.p.stage=='APPROVED':
                    self.p.threshold_reconstruct(pair=pair)
                elif self.p.stage=='RECONSTRUCTED':
                    self.p.issue_token()
                else:
                    self.p.protected_response()
        except ProtocolAbort:
            self.attack_rejected=True
        else:
            raise AssertionError('station-side tampering reached EV acceptance')
        assert self.p.stage != 'EV_ACCEPTED'

    @rule(op=st.sampled_from(('CHARGE','DISCHARGE')),
          pair=st.sampled_from((('A','B'),('A','C'),('B','C'))),
          mutation=st.sampled_from((None,None,None,None,'op','limit','vld','ac')))
    def next_protocol_action(self,op,pair,mutation):
        """One enabled rule; variation occurs *inside* valid state transitions."""
        self.steps_executed+=1
        if self.stopped or self.p.stage=='TERMINATED':
            # Deliberate terminal action: no invalid-rule filtering, no
            # additional authorization or resource reuse after completion.
            return
        stage=self.p.stage
        if stage in ('CONTEXT','APPROVED','RECONSTRUCTED','TOKEN') and mutation is not None:
            self._tamper_and_check(mutation,pair)
        elif stage=='NEW':
            self.p.register()
        elif stage=='REGISTERED':
            self.p.authenticate(op=op)
        elif stage=='AUTHENTICATED':
            self.p.establish_session()
        elif stage=='SESSION':
            if self.original_intent is None:
                self.p.set_ev_intent(op=self.p.op)
                self.original_intent=self.p.ev_state.intent
            else:
                self.p.authorization_context(op=self.original_intent.op)
        elif stage=='CONTEXT':
            self.p.authority_verify()
        elif stage=='APPROVED':
            self.p.threshold_reconstruct(pair=pair)
        elif stage=='RECONSTRUCTED':
            self.p.issue_token()
        elif stage=='TOKEN':
            self.p.protected_response()
        elif stage=='EV_ACCEPTED':
            self.p.execute()
            self.successful_execution=True
        elif stage=='EXECUTED':
            self.p.terminate()
            self.stopped=True
        else:
            raise AssertionError(f'unhandled protocol state {stage!r}')

    @invariant()
    def original_ev_state_retained(self):
        if self.original_intent is not None:
            assert self.p.ev_state.intent==self.original_intent
            assert self.p.op==self.original_intent.op or self.mutated
        if self.successful_execution:
            assert not self.mutated
            assert self.p.stage in ('EXECUTED','TERMINATED')
            assert len(self.p.executed)==1
        if self.mutated:
            assert self.stopped and self.attack_rejected
            assert self.p.stage!='EV_ACCEPTED'

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
