"""Immutable EV transaction intent and EV-side acceptance state."""
from __future__ import annotations
from dataclasses import dataclass, field
from .crypto import H

@dataclass(frozen=True)
class EVIntent:
    """Immutable EV-side session/transaction intent, set before CS offers context."""
    pid:str
    csid:str
    sid:str
    op:str
    ne:bytes
    nc:bytes
    ts_e:int
    ts_c:int
    limit_mwh:int
    validity:tuple

    def context(self):
        return (self.pid,self.csid,self.sid,self.op,self.ne,self.nc,
                self.ts_e,self.ts_c,
                {'type':'ENERGY','max':self.limit_mwh,'unit':'mWh'},
                self.validity)


@dataclass
class EVState:
    intent:EVIntent
    accepted_ac:bytes|None=None
    seen_tokens:set=field(default_factory=set)
