# QSV2G Stage 05 — E3/E5 full-mode remediation (13 November 2026)

**Status:** software changes and local tests completed; large Kaggle experiment execution and Tamarin proof completion **not established**.

## Observed evidence and root cause

The Kaggle Stage 05 smoke ZIP dated 13 Nov 2026 recorded `smoke: true`, 18 E1 transactions, 36 E2 scripted cases plus a passing 20-example Hypothesis campaign, 120 E3 commitment-gate attempts and 30 real-PQC token-path trials all at L=9, and 11 E4 failure cases. E5's `e5_status.json` says `parse_status=NOT_EXECUTED`, `proof_status=UNRESOLVED`, reason `Tamarin binary not found`.

E3 Tier B originally iterated all authority pairs, noise types and probabilities, **but explicitly used `lengths[0]` for L**, so full mode would only have measured real-token endpoint verification at L=9. The correct fix is to iterate L over all lengths in full mode, retain strict per-configuration denominators, and preserve a separate E3 token summary with Wilson intervals. Tier A is still a Monte Carlo computational-basis ideal-state model (not hardware).

E5 was skipped because the original notebook invoked only the detection wrapper; it never installed a Tamarin binary or Maude, which are separate from Python/pip. Official GitHub releases include Tamarin Prover 1.12.0 Linux x86_64 and Maude 3.5.1 Linux x86_64. Their REST asset digest SHA-256 values are pinned in `experiments/stage05/install_tamarin.py`, which refuses mismatched releases and does not require sudo. A Kaggle network/download/ABI failure produces an explicit `UNRESOLVED` result. We **cannot assert** that the binaries will run on every Kaggle image or that proof search will terminate.

The E5 model abstracts only honest classical A/B consent and signatures, assuming an `Assumed_Ideal_QSS_Gate`. It is not formal verification of the quantum resource, arbitrary two-authority resilience, malicious dealers, traffic-key secrecy or full post-quantum protocol.

## Changed paths

- `experiments/stage05/runner.py`: real-PQC E3 endpoint checks for all L=9,27,81,162 in full mode.
- `experiments/stage05/analyze.py`: disaggregated E3 real-token summary, confidence bounds and completeness checks.
- `experiments/stage05/install_tamarin.py`: pinned, SHA-256-verified optional Linux x86_64 binary installer, install status output.
- `experiments/stage05/run_tamarin.py`: explicit version/parse/proof stages; verify all named lemma summaries; record missing/unresolved/counterexample.
- `tests/test_stage05.py`: new E3 ideal L=162 checks, integrity and analysis regressions, E5 status gating.
- `experiments/stage05/README.md`: scope and environment limitations.
- `notebooks/QSV2G_Stage05_Experimental_Evaluation.ipynb`: `SMOKE=False` by default; pinned source; attempted E5 installation after E1–E4; results and logs archived.

## Validation performed

- `pytest -q tests`: **91 passed** on local OpenSSL 3.5.5 ML-KEM-768/ML-DSA-65 backend.
- E3 smoke: **120 Tier A vector attempts, 30 Tier B genuine-token attempts**, **L=9 only**, per the explicit smoke setting; analyzer reports token L coverage and 30 per-configuration rows.
- All AB/AC/BC ideal-channel real-token endpoint checks at L=162 passed in targeted tests.
- Tamarin not present locally; no proof was run; the wrapper correctly reports `UNRESOLVED` without inventing a result.
- Download and executable compatibility for Tamarin/Maude have **not yet been exercised** in local sandbox due to network restrictions.

## Expected full-scale counts and scientific boundaries

- E1: 5 process blocks × 100 trials × 3 pairs × 3 variants × 4 L = **18,000 software transactions**.
- E2: 36 scripted scenarios + 1,000 requested Hypothesis sequences (up to 50 actions each), all outcomes logged.
- E3 Tier A: 4 L × 3 pairs × 5 channels × 5 levels × 1,000 = **300,000 vector commitment attempts**.
- E3 Tier B: same configuration grid × 20 = **6,000 real-PQC EV token-verification attempts**. Compare probabilities separately; 20 samples per cell is insufficient for high-precision reliability claims.
- E4: 11 deterministic stage/failure scenarios. They do not estimate network-outage probabilities.
- E5: conditional parse/proof; verified results may still be unresolved or reveal model counterexamples. The model itself assumes QSS.

**Before manuscript claims:** check run ID and Git SHA; audit raw outputs against manifests; verify E3 token L values; verify E5 proof logs (not just return codes); reconcile `micro.tex` KEM-EV transcript mismatch. A software-only experiment cannot establish quantum-hardware efficiency or a quantum advantage over classical sharing.
