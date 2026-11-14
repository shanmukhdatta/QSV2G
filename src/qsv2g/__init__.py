"""QSV2G: quantum-assisted V2G authorization research simulation.

Scope: real standardized post-quantum primitives plus *simulated* Bell and
qutrit operations; not quantum hardware or a malicious-secure VQSS proof.
"""
from .crypto import (ProtocolAbort, PQCrypto, Traffic, H, mac, canon, encode,
                     decode_fields, parse_canon, ct_eq, hkdf_extract, hkdf_expand)
from .quantum import (qss_state, reduced_density, measure_pair, recover_symbol,
                      qss_consistency, dense_encode_decode, dense_transport_tag)
from .resources import (QSSResource, new_qss_resource, AUTHORITIES, SLOT)
from .state import EVIntent, EVState
from .protocol import QSV2G, run_demo

__version__='0.1.0'
