# Scope and known limitations

The final validation deliberately records four expected limitation demonstrations:

1. A dealer changing both the encoded logical value and matching commitment is not caught by the current consistency checks.
2. Stabilizer checks certify code-subspace membership, not the intended encoded logical symbol; they do not establish malicious-secure verifiable QSS.
3. Two colluding valid authority signers can issue a signed token without actually reconstructing the quantum resource, because EV-side verification authenticates attestations, not an independent proof of reconstruction. A two-signer collusion exceeds a one-corrupt-authority threshold assumption; these are different security statements.
4. Restoring the same AEAD traffic key with a reset nonce counter can cause nonce reuse. Production deployments require a safe persistence/rekey design.

Additionally, the complete simulation workflow relies on UC-A and UC-B online, even though the underlying 2-of-3 QSS resource can be reconstructed by any authorized pair. UC-C absence is tolerated in the tested configuration only when UC-A and UC-B remain available and approve.

Other boundaries: no demonstrated physical quantum networking, malicious-secure VQSS, side-channel resistance, persistent crash-safe state machine, real metering calibration, formal quantum-adversary proof, or quantum advantage over classical alternatives. Classical hash commitments can reveal low-entropy secrets if not carefully instantiated. Recorded latency is platform/backend dependent.
