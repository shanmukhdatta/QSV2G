# QSV2G Stage 06 — Local Audit of P0/P1 and Preliminary P2

**Date:** 2026-11-13 (UTC); local sandbox. **Original Stage 05 code/results were not modified.** Stage 06 results must be independently rerun on the pinned GitHub version for publication-grade provenance. There is no new Tamarin P3 proof in this stage.

## Experimental software and controls

- Real PQC backend: OpenSSL 3.5.5 supporting ML-KEM-768 and ML-DSA-65. No classical cryptographic fallback in `security.py`.
- Baseline: existing `QSV2G` core and Stage 05 `ClassicalResource` with identical intent/signature workflow; only reconstruction resource differs.
- Configurations: 2 variants × 3 authority pairs × 2 authenticated operations × 8 scenarios = **96 P0/P1 observations**. One genuine PQC protocol instance per observation.
- Controls: honest EV acceptance; one approval; share-only tampering; two-signature context substitution. All cases record explicit trust-boundary flags.
- Independent exact calculation: 9 secret/pair distribution comparisons (3 secret values × 3 pairs).

## Observations

| Scenario | QSS cases | Classical-sharing cases | Result per variant |
| --- | ---: | ---: | --- |
| Honest control | 6 | 6 | EV accepts |
| Only one approval | 6 | 6 | Rejected |
| Tamper one share, hold original commitment | 6 | 6 | Rejected |
| Dishonest dealer replaces both secret and commitment | 6 | 6 | Reconstructed and accepted under dealer-control assumption |
| One signer attempts bogus signed reconstruction digest | 6 | 6 | Rejected |
| Two compromised signers attest bogus digest after reconstruction | 6 | 6 | EV accepts bogus digest under compromise assumption |
| Two compromised signers + CS privileged state skip reconstruction | 6 | 6 | EV accepts although resource remains UNUSED |
| Two signers present a signed different context | 6 | 6 | Rejected |

**All 96 outcomes matched the declared expectations.** This is not a claim of the protocol being robust against every adversary. Two-key outcomes are expected under a compromise configuration that may be outside the original security model, and skipping reconstruction requires forcibly advancing the CS simulator's internal stage. The EV's actual ML-DSA signature checks still run. The result shows the EV does not cryptographically verify quantum reconstruction; **it is not a remote-only attack trace**.

The locally stored QSS and classical computational-basis distributions agree at machine precision (maximum total-variation distance below `2e-16`). Individual QSS share reduced density matrices are `I/3` at the same precision. Consequently **no unique QSS security property is demonstrated by these measured computational-basis tests**; this does not rule out every possible quantum-specific construction or adversary.

## P2 — Fresh-resource retry model

400 configurations evaluated: 4 vector lengths × 5 channels × 5 noise parameters × 4 retry budgets, with 2,500 Monte Carlo draws/configuration. The generated data is a **model-level sensitivity analysis** that does not call the live ML-DSA token path and does not implement retries in the current protocol.

For `L=162`, the 1% X-error model has an independent one-resource commitment-gate pass probability of approximately **0.00756**; with retry budgets of 1, 3, 10, 30, the analytical probabilities are approximately 0.76%, 2.25%, 7.31%, and 20.37%. With 30 attempts, the mean attempts consumed per authorization request is approximately 26.93. This is an availability/resource trade-off, not a protocol security improvement.

## Unresolved and decision

- **P3 extended compromise-aware Tamarin proof:** NOT EXECUTED/PROVED in this local run (only a candidate model was prepared). Existing Stage 05 formal proofs are limited to the prior abstract consent model.
- **Physical qutrit channel, dishonest-dealer VQSS, distributed roles/real authority key custody, real retry protocol:** NOT IMPLEMENTED.
- Next research gate: Decide whether the intended claim requires tolerance against two corrupt signers, and who attests to resource reconstruction. If two signers are already the authorization threshold, their collusion may be an assumed catastrophic compromise. If requiring resistance to it, an independently verifiable proof or independent trust root would be needed; signing a hash of an unverified resource is insufficient. Fairly test any proposed improvement against an equally strengthened classical solution.
- Do not change or rerun old Stage 05 results before agreeing on a concrete design change.

## Reproduction

```bash
pytest -q tests/test_stage06.py
python experiments/stage06/security.py --out results/stage06/p0p1 --L 9
python experiments/stage06/reliability.py --out results/stage06/p2
```

Expected output counts: 96 P0/P1 rows, 9 distribution rows, 400 P2 rows. All results are exploratory until a pinned-revision rerun and audit of raw files.

### P3 candidate added after the initial local audit

A new Tamarin **candidate** theory (`formal/qsv2g_stage06_compromise_candidate.spthy`) and conservative proof runner (`experiments/stage06/run_formal.py`) are included in GitHub deliverables. Local tool result: `NOT_EXECUTED` / `UNRESOLVED` because Tamarin is not installed. The candidate has **not** been parsed or proved. It therefore does not change the conclusion that P3's formal evidence is outstanding.
