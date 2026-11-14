"""Exact three-qutrit statevectors and Bell-pair mathematical simulation."""
from __future__ import annotations
import numpy as np
from .crypto import require
from .constants import SLOT

I2=np.eye(2,dtype=np.complex128)
X2=np.array([[0,1],[1,0]],complex)
Z2=np.diag([1,-1]).astype(complex)
H2=np.array([[1,1],[1,-1]],complex)/np.sqrt(2)
CNOT=np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]],complex)
BELL=np.array([1,0,0,1],complex)/np.sqrt(2)
OMEGA=np.exp(2j*np.pi/3)
X3=np.roll(np.eye(3,dtype=complex),1,axis=0)
Z3=np.diag([OMEGA**j for j in range(3)])

def dense_encode_decode(two_bits):
    a,b=two_bits
    state=np.kron(np.linalg.matrix_power(Z2,a)@np.linalg.matrix_power(X2,b),I2)@BELL
    final=np.kron(H2,I2)@CNOT@state
    probabilities=np.abs(final)**2
    idx=int(np.argmax(probabilities))
    require(np.isclose(probabilities[idx],1,atol=1e-12),'Bell decoding failure')
    return (idx//2,idx%2)


def dense_transport_tag(tag):
    recovered=bytearray()
    bits=''.join(f'{byte:08b}' for byte in tag)
    out=''
    for k in range(0,len(bits),2):
        aa,bb=dense_encode_decode((int(bits[k]),int(bits[k+1])))
        out+=str(aa)+str(bb)
    recovered.extend(int(out[j:j+8],2) for j in range(0,len(out),8))
    return bytes(recovered)


def qss_state(s):
    """|psi(s)> = sum_r |r,r+s,r+2s> /sqrt(3)."""
    require(s in (0,1,2),'Invalid trit')
    state=np.zeros((3,3,3),dtype=complex)
    for r in range(3): state[r,(r+s)%3,(r+2*s)%3]=1/np.sqrt(3)
    return state


def reduced_density(psi, kept):
    moved=np.moveaxis(psi,kept,0).reshape(3,-1)
    return moved@moved.conj().T


def measure_pair(psi, pair, rng, x_fault=False):
    """Sample joint computational measurement of two shares from a 3-qutrit statevector.
    x_fault applies a qutrit-X error to the SECOND selected share before measuring.
    """
    u,v=[SLOT[p] for p in pair]
    state=np.moveaxis(psi,(u,v),(0,1))
    probs=(np.abs(state)**2).sum(axis=2).reshape(-1)
    idx=int(rng.choice(9,p=probs/probs.sum()))
    xu,xv=divmod(idx,3)
    if x_fault: xv=(xv+1)%3
    return xu,xv


def recover_symbol(pair,xu,xv):
    denom=(SLOT[pair[1]]-SLOT[pair[0]])%3
    return ((xv-xu)*pow(denom,-1,3))%3


def qss_consistency():
    Xa=np.kron(np.kron(X3,X3),X3)
    Za=np.kron(np.kron(Z3,Z3),Z3)
    vals=[]
    for s in range(3):
        psi=qss_state(s)
        psi_flat=psi.reshape(-1)
        vals.append({
            's':s,
            'norm':float(np.vdot(psi_flat,psi_flat).real),
            'x_stabilizer_error':float(np.linalg.norm(Xa@psi_flat-psi_flat)),
            'z_stabilizer_error':float(np.linalg.norm(Za@psi_flat-psi_flat)),
            'one_share_distances':[float(np.linalg.norm(reduced_density(psi,b)-np.eye(3)/3)) for b in range(3)],
        })
    return vals
