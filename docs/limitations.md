# Evidence scope and limitations

1. Bell and qutrit quantum primitives are statevector/density or optimized
   computational-basis sampling models, **not quantum hardware**.
2. Standardized PQC, HMAC, HKDF and AES-GCM are genuine software primitives;
   `FakePQC` is used only in labeled isolated regression/property tests.
3. No distinct security advantage over equivalent classical affine 2-of-3
   secret sharing is established by the tested computational-basis interface.
4. The verifier checks authority signatures, not independently verified
   quantum reconstruction. Two compromised signers plus privileged station
   manipulation can bypass modeled reconstruction.
5. A dishonest dealer replacing both secret and its own commitment is outside
   the current authenticated-commitment integrity guarantee.
6. QSS noise simulations use specified local channel models and often assume
   independent per-symbol errors. Long vectors can have low gate acceptance.
7. Retry analysis models fresh resources analytically and via Monte Carlo;
   it does not implement actual authenticated retry flow.
8. Cryptographic state and execution protections are process-local; no crash-
   persistent distributed database, real grid control or EV hardware exists.
9. Formal properties depend on stated Tamarin abstractions and assumptions;
   one compromise lemma establishes an **attack-existence** trace.
10. Historical runtime versions and later refactored source differ.
    Keep original measured results attached to the original source version.
