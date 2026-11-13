# QSV2G software remediation — 13 November 2026

**Scope:** Source-level research-simulation corrections and new tests. This is NOT a protocol-security certification, physical quantum/EV/charger deployment, or new validated benchmark of the complete system. The archived Stage 01–04 data and notebooks have not been overwritten.

**Repository parent inspected:** `4b5ee95abcd249e3f5e95e39657b8c0cd2bda87b`. The original `src/qsv2g_core.py` Git blob `9467253363751c65899714cfc91330c92a3f853a` was byte-identical to the uploaded LaTeX ZIP's `data/qsv2g_core_reference.py` (SHA-256 `2c86ca9eecbc5925100722119f061e640df03f993e14909b3078b23406330758`). This provides source identity, not executed-run identity.

## Implemented now

1. **EV-side intent:** `set_ev_intent()` freezes operation, energy bound, validity and authenticated session fields before the station sends the encrypted context. The EV independently decodes the context offer, checks it against that immutable record and retains the accepted context digest; token checks refer to the EV record instead of station-side mutable fields. EV replay state is now logically separate from the station-side execution set. This is *logical separation inside one Python process*, not a distributed deployment.
2. **Authenticated operation / KEM proof:** The requested CHARGE/DISCHARGE operation is bound at authentication and cannot be silently changed afterward. A KEM-EV proof tampering path is exercised. The code retains the historical **larger authenticated KEM-EV tuple**; the manuscript currently describes a smaller tuple and MUST be brought into agreement, with a versioned evidence statement, before claiming paper/code parity.
3. **QSS approval / reservation:** A resource identifier `nu` is proposed before approvals. Each simulated approval records `(authority, AC, nu, decision)`. The chosen approved pair checks those records before reserving. Reservation and consumption use a process-local mutex to block concurrent reuse. Failed measurement attempts consume the resource, and simulated retained dealer secrets are erased from the resource object. Not durable, distributed or malicious-dealer-proof.
4. **AES-256-GCM nonce-reset fault:** Switched from restartable zero-based GCM counters to 96-bit cryptographically random nonces, with per-object duplicate suppression. This prevents *deterministic* nonce repetition on counter reset. As with any randomized scheme, cross-process collision probability is nonzero; long-lived deployment needs a documented rekey/persistence policy.
5. **Expiry and context parsing:** Added canonical length-prefixed field decoding and rejection of malformed/truncated contexts. The simulated execution clock now starts from actual execution time instead of registration time.
6. **Full-vector exploratory experiment:** Added `scripts/full_vector_commitment_sim.py` for software-only independent X faults on one selected share and a gate requiring all three dealer-vector commitments to match. This is NOT a complete quantum-noise channel model, token-issuance benchmark, or end-to-end authorization reliability validation.

## Tests performed locally in this revision

- `python -m py_compile src/qsv2g_core.py`: PASS.
- `pytest -q tests`: **25 passed** (Python 3 environment with NumPy 2.3.5, cryptography 46.0.4, pytest 9.0.2, OpenSSL 3.5.5). Includes fake-PQC isolated state-machine tests and an actual OpenSSL ML-KEM-768 + ML-DSA-65 smoke test. Fake-PQC tests never measure or establish cryptographic security.
- Exploratory full-vector simulation: `python scripts/full_vector_commitment_sim.py --lengths 9 27 81 162 --p 0 0.01 0.05 --trials 50 --seed 2026 --output full_vector_exploratory_50trials.csv`. Only **50 trials per cell**, intended as a smoke/evidence-path demonstration; not sufficient for robust scientific confidence intervals. Exact output archived separately from original Stage 01–04 experiments.

## Manuscript/source items still requiring work

- `micro.tex` KEM-EV description still gives `(PID, CSID, N_E, ek)`, while this code authenticates `SHA256(encode(PID, CSID, OP, N_E, N_C, TS_E, TS_C, ek))` under `K_E^reg` (domain separated `KEM-EV`); explicitly align these.
- Existing notebooks, raw results and Stage 01–04 audit files are historical snapshots. They were NOT rerun with this corrected code. The new tests cannot retroactively validate the existing reported timing or security results.
- A complete adversarial protocol with separate process/actor secrets, authenticated authority-to-authority channels, persisted replay/reservation state, key rotation/revocation, physically enforced charging limits, and crash recovery is **not implemented**.
- The EV verifies ML-DSA signatures over an attestation, not an endpoint-verifiable QSS proof. Two signer collusion remains out of the stated one-corrupt-authorizer threat boundary. Malicious dealer equivocation, alternate codewords and short commitments require precise threat-bound definitions; these changes do not solve them.
- QSS's contribution versus equivalent classical 2-of-3 threshold sharing remains unestablished. A fair functionality-matched comparison is still required for superiority claims.
- Noise under real channels, storage/decoherence, loss and quantum hardware performance remain untested. Software-only measurements cannot establish deployment reliability.
- The six-page manuscript, diagrams, bibliography, author data and controlled performance baselines have not been revised in this code commit. Publication readiness and IEEE policy compliance are NOT claimed.

## How to reproduce

```bash
python -m pip install numpy cryptography pytest
pytest -q tests
python scripts/full_vector_commitment_sim.py --lengths 9 27 81 162 --p 0 0.01 0.05 --trials 50 --seed 2026
```

For the real-PQC smoke test, provide either a compatible `pqcrypto` installation or OpenSSL 3.5+ with ML-KEM-768 and ML-DSA-65; otherwise only that test skips. Historical performance results and cloud-run provenance are not replaced by this smoke test. The unit tests are not a proof of security.
