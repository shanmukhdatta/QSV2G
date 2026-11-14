"""Canonical serialization, real PQ cryptography, and protected classical channels."""
from __future__ import annotations
import base64, hashlib, hmac, json, math, os, secrets, shutil, subprocess, tempfile, time
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class ProtocolAbort(Exception):
    pass


def require(condition, explanation):
    if not condition:
        raise ProtocolAbort(explanation)


def json_obj(o):
    if isinstance(o, bytes): return {'__type__':'bytes', 'base64':base64.b64encode(o).decode('ascii')}
    if isinstance(o, tuple): return {'__type__':'tuple', 'items':[json_obj(x) for x in o]}
    if isinstance(o, list): return [json_obj(x) for x in o]
    if isinstance(o, dict): return {str(k):json_obj(v) for k,v in sorted(o.items())}
    if isinstance(o, (str,int,bool)) or o is None: return o
    raise TypeError(f'Unsupported field {type(o).__name__}: floating-point values are intentionally disallowed')


def canon(x):
    return json.dumps(json_obj(x), sort_keys=True, separators=(',',':'), ensure_ascii=False).encode('utf-8')


def parse_canon(raw):
    def restore(x):
        if isinstance(x, list): return [restore(y) for y in x]
        if isinstance(x, dict):
            if x.get('__type__')=='bytes' and set(x)=={'__type__','base64'}:
                return base64.b64decode(x['base64'],validate=True)
            if x.get('__type__')=='tuple' and set(x)=={'__type__','items'}:
                return tuple(restore(y) for y in x['items'])
            return {k:restore(v) for k,v in x.items()}
        return x
    return restore(json.loads(raw.decode('utf-8')))


def encode(*fields):
    """Fixed ordering, deterministic, typed-length-separated encoding."""
    out=bytearray()
    for f in fields:
        chunk=canon(f)
        out += len(chunk).to_bytes(4,'big')+chunk
    return bytes(out)


def decode_fields(payload):
    """Decode the canonical, length-prefixed wire fields; reject truncation/noncanonical data."""
    fields=[]; offset=0
    while offset < len(payload):
        require(len(payload)-offset >= 4, 'truncated field length')
        size=int.from_bytes(payload[offset:offset+4], 'big'); offset+=4
        require(size <= len(payload)-offset, 'truncated field')
        raw=payload[offset:offset+size]; offset+=size
        try:
            field_value=parse_canon(raw)
            require(canon(field_value)==raw, 'noncanonical field')
        except (ValueError, UnicodeError, TypeError, KeyError) as e:
            raise ProtocolAbort('malformed canonical field') from e
        fields.append(field_value)
    return tuple(fields)


def H(*fields): return hashlib.sha256(encode(*fields)).digest()


def mac(k, *fields): return hmac.new(k, encode(*fields), 'sha256').digest()


def ct_eq(a,b): return hmac.compare_digest(a,b)


def hkdf_extract(salt, ikm): return hmac.new(salt, ikm, 'sha256').digest()


def hkdf_expand(prk, info, n=32):
    out=b''; t=b''
    for i in range(1,math.ceil(n/32)+1):
        t=hmac.new(prk, t+info+bytes([i]), 'sha256').digest(); out+=t
    return out[:n]


def digest_for(label, *items): return H(label, *items)


class PQCrypto:
    def __init__(self):
        self.kind=None
        try:
            from pqcrypto.kem import ml_kem_768
            from pqcrypto.sign import ml_dsa_65
            self.kem=ml_kem_768; self.sig=ml_dsa_65
            self.kind='pqcrypto native ML-KEM-768 + ML-DSA-65'
        except (ImportError,ModuleNotFoundError):
            exe=shutil.which('openssl')
            if exe:
                test=subprocess.run([exe,'list','-kem-algorithms'],capture_output=True,text=True)
                sig=subprocess.run([exe,'list','-signature-algorithms'],capture_output=True,text=True)
                if 'ML-KEM-768' in test.stdout and 'ML-DSA-65' in sig.stdout:
                    self.kind='OpenSSL 3.5+ ML-KEM-768 + ML-DSA-65 (subprocess)'
                    self.openssl=exe
            if self.kind is None:
                raise RuntimeError('Real ML-KEM-768/ML-DSA-65 unavailable. Enable Kaggle Internet and pip install pqcrypto. No classical substitute will be used.')
    def _openssl_call(self, arguments, input_files=None, output_files=()):
        with tempfile.TemporaryDirectory(prefix='qsv2g_pqc_') as folder:
            root=Path(folder)
            for name,data in (input_files or {}).items(): (root/name).write_bytes(data)
            argv=[self.openssl]+[str(root/(v[1:])) if isinstance(v,str) and v.startswith('@') else str(v) for v in arguments]
            p=subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=root, timeout=30)
            if p.returncode:
                raise RuntimeError('OpenSSL cryptographic call failed: '+p.stderr.decode('utf-8',errors='replace')[:500])
            return (p.stdout, *[(root/x).read_bytes() for x in output_files])
    def kem_keygen(self):
        if self.kind.startswith('pqcrypto'):
            pub,priv=(self.kem.keygen() if hasattr(self.kem,'keygen') else self.kem.generate_keypair()); return pub,priv
        # key generation and public-key extraction share one temporary directory
        with tempfile.TemporaryDirectory(prefix='qsv2g_kem_') as d:
            sk=Path(d)/'sk.pem'; pk=Path(d)/'pk.pem'
            subprocess.run([self.openssl,'genpkey','-algorithm','ML-KEM-768','-out',str(sk)],check=True,capture_output=True)
            subprocess.run([self.openssl,'pkey','-in',str(sk),'-pubout','-out',str(pk)],check=True,capture_output=True)
            return pk.read_bytes(), sk.read_bytes()
    def encaps(self,pub):
        if self.kind.startswith('pqcrypto'):
            return self.kem.encaps(pub) if hasattr(self.kem,'encaps') else self.kem.encrypt(pub)
        _,ct,ss=self._openssl_call(['pkeyutl','-encap','-pubin','-inkey','@pk','-out','@ct','-secret','@ss'], {'pk':pub},('ct','ss'))
        return ct,ss
    def decaps(self,priv,ct):
        if self.kind.startswith('pqcrypto'):
            return self.kem.decaps(priv,ct) if hasattr(self.kem,'decaps') else self.kem.decrypt(priv,ct)
        _,ss=self._openssl_call(['pkeyutl','-decap','-inkey','@sk','-in','@ct','-secret','@ss'],{'sk':priv,'ct':ct},('ss',))
        return ss
    def sig_keygen(self):
        if self.kind.startswith('pqcrypto'):
            return self.sig.keygen() if hasattr(self.sig,'keygen') else self.sig.generate_keypair()
        with tempfile.TemporaryDirectory(prefix='qsv2g_sig_') as d:
            sk=Path(d)/'sk.pem'; pk=Path(d)/'pk.pem'
            subprocess.run([self.openssl,'genpkey','-algorithm','ML-DSA-65','-out',str(sk)],check=True,capture_output=True)
            subprocess.run([self.openssl,'pkey','-in',str(sk),'-pubout','-out',str(pk)],check=True,capture_output=True)
            return pk.read_bytes(),sk.read_bytes()
    def sign(self,priv,msg):
        if self.kind.startswith('pqcrypto'):
            return self.sig.sign(priv,msg)
        _,sig=self._openssl_call(['pkeyutl','-sign','-inkey','@sk','-in','@msg','-out','@sig'],{'sk':priv,'msg':msg},('sig',))
        return sig
    def verify(self,pub,msg,sig):
        if self.kind.startswith('pqcrypto'):
            try:
                result=self.sig.verify(pub,msg,sig)
                return result is None or result is True
            except Exception: return False  # InvalidSignatureError from pqcrypto 1.x, ValueError on older versions
        try:
            self._openssl_call(['pkeyutl','-verify','-pubin','-inkey','@pk','-in','@msg','-sigfile','@sig'],{'pk':pub,'msg':msg,'sig':sig})
            return True
        except RuntimeError: return False


@dataclass
class Traffic:
    key:bytes
    send_counter:int=0
    seen:set=field(default_factory=set)
    sent_nonces:set=field(default_factory=set)
    def encrypt(self,pt:bytes,ad:bytes):
        require(self.send_counter<2**96-1,'AES-GCM counter exhaustion')
        # Random 96-bit nonces avoid deterministic reuse if an in-memory counter
        # is reset with the same key. Collision risk is negligible, not zero;
        # deployed systems additionally require rekeying/durable nonce policy.
        nonce=secrets.token_bytes(12)
        while nonce in self.sent_nonces:
            nonce=secrets.token_bytes(12)
        self.sent_nonces.add(nonce); self.send_counter+=1
        ct=AESGCM(self.key).encrypt(nonce,pt,ad)
        return {'nonce':nonce,'ciphertext':ct}
    def decrypt(self,pkt,ad):
        nonce=pkt['nonce']
        require(len(nonce)==12 and nonce not in self.seen,'duplicate or malformed AEAD nonce')
        try: pt=AESGCM(self.key).decrypt(nonce,pkt['ciphertext'],ad)
        except Exception as e: raise ProtocolAbort('AEAD authentication failure') from e
        self.seen.add(nonce)
        return pt
