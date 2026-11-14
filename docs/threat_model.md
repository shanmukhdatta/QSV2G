# Threat model and trust boundary

Assume authenticated registration, appropriately protected honest keys,
secure provisioning, and a correctly enforced independent EV transaction intent.
The simulated 2-of-3 authorization requires two distinct approvals; the
full registration workflow still relies on A and B being online. Its
usual threshold-corruption boundary is fewer than two compromised authorizers.

In-scope *software* checks include malformed messages, modified ciphertexts,
replayed tokens, incorrectly bound operations/limits/validities, substituted
shares against fixed commitments, one-key forgery, and process-local double use.

Excluded/not established: malicious dealer replacement of both a secret and
its initial commitment, two corrupted signers plus privileged station control,
physical quantum channels, side channels, distributed crash recovery, hardware
metering and long-term key rotation. Excluding an attack from a specific threat
model does **not** turn an observed bypass into a security success.

The EV verifies ML-DSA signed reconstruction **attestations**, not a
cryptographic proof that quantum reconstruction physically occurred.
