"""QSS preparation, commitment checks, reservations, and consumption."""
from __future__ import annotations
import secrets, threading
from dataclasses import dataclass, field
import numpy as np
from .crypto import H, require, ct_eq
from .quantum import qss_state, measure_pair, recover_symbol
from .constants import AUTHORITIES, SLOT

@dataclass
class QSSResource:
    nu:str
    dealer_secrets:dict
    states:dict
    commitments:dict
    state:str='UNUSED'
    lock:tuple|None=None
    _mutex:object=field(default_factory=threading.Lock,repr=False,compare=False)
    def reserve(self,ac,pair):
        with self._mutex:
            require(self.state=='UNUSED','QSS resource already reserved or consumed')
            require(len(pair)==2 and len(set(pair))==2 and all(a in AUTHORITIES for a in pair),'pair invalid')
            self.state='RESERVED'; self.lock=(ac,tuple(pair))
    def reconstruct(self,ac,pair,rng,tamper=False):
        with self._mutex:
            require(self.state=='RESERVED' and self.lock==(ac,tuple(pair)),'QSS reservation mismatch')
            self.state='MEASURING'  # prevent a concurrent second reconstruction
        recovered={a:[] for a in AUTHORITIES}
        try:
            for dealer in AUTHORITIES:
                for k,psi in enumerate(self.states[dealer]):
                    xu,xv=measure_pair(psi,pair,rng,x_fault=(tamper and dealer=='A' and k==0))
                    recovered[dealer].append(recover_symbol(pair,xu,xv))
            for dealer in AUTHORITIES:
                expected=H('QSV2G-QSS-COM',dealer,self.nu,recovered[dealer])
                require(ct_eq(expected,self.commitments[dealer]),'QSS reconstructed commitment mismatch')
            combined=[sum(recovered[a][k] for a in AUTHORITIES)%3 for k in range(len(recovered['A']))]
            return combined
        finally:
            with self._mutex:
                self.state='CONSUMED'
                self.states.clear()  # simulated irreversible measurement / erasure
                self.dealer_secrets.clear()  # no post-use dealer secret retained in resource object


def new_qss_resource(L=162,rng=None):
    rng=rng or np.random.default_rng(2026)
    nu=secrets.token_hex(12)
    dealer_secrets={a:[secrets.randbelow(3) for _ in range(L)] for a in AUTHORITIES}
    states={a:[qss_state(s) for s in dealer_secrets[a]] for a in AUTHORITIES}
    commits={a:H('QSV2G-QSS-COM',a,nu,dealer_secrets[a]) for a in AUTHORITIES}
    return QSSResource(nu,dealer_secrets,states,commits)
