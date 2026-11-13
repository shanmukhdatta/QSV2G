# QSV2G Stage 05 — Reproducible Software Experiments (E1–E5)

**Status:** executable research-instrumentation implementation; NOT a formally proven or deployed V2G system. Keep the Stage 01–04 archived outputs unchanged. Exact tested commit should be pinned in Kaggle; run ID, environment and errors must be retained.

## Scope

- **E1:** Real ML-KEM-768/ML-DSA-65 software lifecycle with matched context/consent, compare **QUORUM** (two signers, no secret reconstruction; *weaker functionality*), **CLASSICAL_SHARING** (three dealer contributions and 2-of-3 affine mod-3 share recovery), and **QSS** (existing 3-qutrit statevector). All receive the same two-signer token format. Quorum is not a security-equivalent baseline. This does not establish an advantage for QSS. Benchmark blocks run as **separate Python processes**. Qutrit storage/transmission counts are analytical, not physically measured. The selected instrumented packet sizes exclude quantum/network transport and some classical protocol messages.
- **E2:** Actual real-PQC endpoint and context rejection scenarios across AB, AC and BC, plus `stateful_hypothesis.py` to explore event sequences with **TEST-ONLY HMAC stub**. These are separate evidence tiers. EV intent is immutable but actor separation remains within one process. No inference of "attack probability" from test counts.
- **E3:** Tier A optimized classical measurement sampler for an *ideal* 3-qutrit encoded state (not a full density-matrix simulation), with local noise on **second selected share only**. X = +1 shift probability p; dephasing = Z phase channel (no computational-basis recovery effect); depolarizing = replacement with uniform trit probability p; erasure = flagged abort probability p; combined = independent X and depolarize at probability p each. Every dealer's complete vector commitment must pass. Tier B takes the exact same sampler through genuine PQC token issuance and independent EV-side response verification, with separate denominators. These are not physically measured quantum communication channels or a network robustness guarantee.
- **E4:** Explicitly scoped failures of required online authorities, availability rechecks before reconstruction and signing, process-local concurrent reservation, expired and reused authorization. Fail-safe aborts are not equivalent to automatic failover, crash-safe persistence or network simulation.
- **E5:** `formal/qsv2g_classical_consent.spthy` models an **A/B honest-party-only abstraction**, with `Assumed_Ideal_QSS_Gate` explicitly assumed; `run_tamarin.py` preserves parse/proof logs and reports unresolved/unavailable rather than claiming proof. It does **not** cover arbitrary pairs, compromise, full ML-KEM key secrecy, actual QSS physics or installed hardware. The Tamarin theory must be parsed, executed and independently reviewed before citing any formal result.

## P0 known code/manuscript mismatch

`src/qsv2g_core.py` authenticates the KEM-EV digest of canonical `(PID, CSID, OP, N_E, N_C, TS_E, TS_C, ek)` with the domain-separated EV registration key; uploaded `micro.tex` described `(PID, CSID, N_E, ek)`. **Manuscript must be reconciled; these files do not claim parity.** No paper tables/figures were silently edited. This code also adds availability checks before QSS recovery and token signing, which must be specified in the eventual paper. Session expiry, persistent state, full inter-actor independence and malicious VQSS are not proved or deployed.

## Commands

```bash
python -m pip install numpy cryptography pandas matplotlib pytest hypothesis
python -m pytest -q tests
# Requires either pqcrypto with ML-KEM-768/ML-DSA-65 or OpenSSL >= 3.5 with both algorithms:
python experiments/stage05/runner.py --experiment all --smoke --out results/stage05/smoke
python experiments/stage05/stateful_hypothesis.py --examples 20 --steps 15 --output results/stage05/smoke/e2/hypothesis.json
python experiments/stage05/run_tamarin.py --out results/stage05/smoke/e5
python experiments/stage05/analyze.py results/stage05/smoke
# Only after pilot configuration is frozen and adequate runtime is available:
python experiments/stage05/runner.py --experiment all --out results/stage05/final
python experiments/stage05/stateful_hypothesis.py --examples 1000 --steps 50 --output results/stage05/final/e2/hypothesis.json
python experiments/stage05/run_tamarin.py --out results/stage05/final/e5
python experiments/stage05/analyze.py results/stage05/final
```

The complete E1 default is 5 process blocks × 100 transactions × 3 pairs × 3 variants × 4 lengths = **18,000** software transactions, with randomized order per block. E3 full Tier A contains 4 lengths × 3 pairs × 5 channels × 5 noise levels × 1,000 = **300,000** full-vector attempts; Tier B is 3 pairs × 5 channels × 5 levels × 20 = **1,500** genuine-token attempts at **L=9 only**. **Do not report Tier B as L=162**, and adjust sample plan only before examining final comparisons. Error bars are Wilson intervals for independent Tier A outcomes; they do not account for correlated faults. E1 process-block bootstrap needs multiple blocks and is uncertain with only five.

Kaggle main notebook: `notebooks/QSV2G_Stage05_Experimental_Evaluation.ipynb`. Internet is needed for cloning/dependency installation unless packages are already attached as Kaggle inputs. Tamarin is separate, may require Maude and a compatible executable; notebook never quietly pretends to have run a missing prover.

**Sources informing the design:** Tamarin manual, Hypothesis stateful testing documentation, QSKA (IEEE TNSM 2024), Plug-and-Charge authorization verification (IEEE Access 2025), NIST FIPS 203/204. The external papers supply methodological context, not QSV2G results.
