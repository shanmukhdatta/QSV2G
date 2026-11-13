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

The complete E1 default is 5 process blocks × 100 transactions × 3 pairs × 3 variants × 4 lengths = **18,000** software transactions, with randomized order per block. E3 full Tier A contains 4 lengths × 3 pairs × 5 channels × 5 noise levels × 1,000 = **300,000** full-vector attempts; Tier B is now 4 lengths × 3 pairs × 5 channels × 5 levels × 20 = **6,000** genuine ML-KEM/ML-DSA endpoint-token attempts across **L=9, 27, 81, 162** in full mode. The small smoke run still tests **L=9 only**. The 20 per-condition endpoint checks are a **consistency pilot with wide intervals**, not a precise rare-event probability estimate. Do not misrepresent these software checks as physical quantum networking or energy transfer. Error bars are Wilson intervals for independent Tier A outcomes; they do not account for correlated faults. E1 process-block bootstrap needs multiple blocks and is uncertain with only five.

Kaggle main notebook: `notebooks/QSV2G_Stage05_Experimental_Evaluation.ipynb`. Internet is needed for cloning/dependency installation unless packages are already attached as Kaggle inputs. Tamarin E5 is optionally bootstrapped inside Kaggle by `install_tamarin.py`, using **official, pinned Linux x86_64 Tamarin 1.12.0 and Maude 3.5.1 archives with SHA-256 integrity checks**; no apt/sudo is needed. Actual installation has **not been verified on Kaggle**. Installation failures and proof timeouts are recorded as **UNRESOLVED**, not passed proofs. The notebook never quietly pretends to have run a missing prover.

**Sources informing the design:** Tamarin manual, Hypothesis stateful testing documentation, QSKA (IEEE TNSM 2024), Plug-and-Charge authorization verification (IEEE Access 2025), NIST FIPS 203/204. The external papers supply methodological context, not QSV2G results.

## Pre-Kaggle cross-check amendments (13 November 2026)

- **Matched preparation:** E1 now constructs exactly one variant-specific resource. The classical controls no longer prepare-and-discard an unused QSS resource. `preparation_ms` includes signing-key generation and offline resource preparation; `full_software_ms` excludes this preparation; `inclusive_software_ms` includes both. These are local software costs, not quantum-link timing. E1 and the analysis fail rather than silently ignore incomplete transactions.
- **Real safety edges:** the process-local execution state now enforces one START at a time, validates simulated power/durations, and clips energy ticks to authorization expiry. E4 adds a `CONCURRENT_START` case and fails on unexpected outcomes. No distributed-persistence or real meter enforcement is claimed.
- **E2 coverage integrity:** the intentionally idle Hypothesis rule is enabled only at terminal/aborted states, so it does not crowd out progress actions. The scenario summary fails on expected/observed mismatches. Hypothesis still requires installation and actual execution in Kaggle for generated-sequence evidence.
- **E5 correctness:** the signature equation uses Tamarin's nullary `true` symbol, not the unrelated quoted public name `'true'`. This was checked against Tamarin's documented signing equational theory, but the `.spthy` theory is still **UNPARSED/UNPROVED** here because Tamarin/Maude are not installed. Kaggle must report such status explicitly.
- **Pilot results only:** local `pytest -q tests` and E1–E4 smoke workflows pass. E3 full-grid and E1 full-scale benchmarks have **not** been run or validated for runtime. Run `SMOKE=True` and inspect counts and mismatch fields before choosing the final budget; Kaggle may require separate saved runs for E1 and E3.
- **Spec alignment:** the exact manuscript `micro.tex` KEM-EV transcript mismatch remains a manuscript correction; do not claim that code and paper are identical until reconciled. Existing Stage 01–04 outputs are not replaced.

## E2 Hypothesis rule-generation correction (13 November 2026)

The first Kaggle-generated campaign found a legitimate DISCHARGE scenario whose context mistakenly defaulted to CHARGE; that **test-harness error** was corrected in `bb49a67`. The subsequent Kaggle smoke run returned `FailedHealthCheck(filter_too_much)` (6 accepted vs 50 filtered inputs), because the original state machine exposed many phase-specific rules with unavailable preconditions. The replacement exposes a **single always-enabled protocol-transition rule** with generated operation, authority pair and mutation choices. No `filter_too_much` health check is suppressed, and mutations are driven through endpoint checks to ensure rejection. Unit tests independently cover both operations, all pairs and mutations at all eligible stages.

These deterministic transition tests are not a substitute for the real Hypothesis campaign on Kaggle. The actual generated campaign must run successfully and its JSON outcome must be preserved. Do not claim a proof or infer attacker probabilities from generated sequences.

## Full-run E3/E5 remediation — 13 November 2026

- **E3 cause:** `runner.py` previously set Tier B `L=lengths[0]`, even though full-mode Tier A included `L=162`. Corrected so every full-mode Tier B configuration now includes all four lengths. The analyzer outputs `e3_token_summary_with_ci.csv`, checks expected lengths against the manifest and reports actual per-cell denominators; no pooled one-number security claim is permitted. `p=0` genuine endpoint failures and unexplained endpoint errors fail analysis. Local smoke (L=9) and direct ideal-path `L=162` endpoint regression checks passed. **Full Kaggle E3 remains not executed.**
- **E5 cause:** earlier notebooks called a wrapper but did not install the Tamarin or Maude executables, so the stage correctly recorded `NOT_EXECUTED`. The new `install_tamarin.py` attempts official downloads with pinned SHA-256 digests, and `run_tamarin.py` only marks model lemmas verified after matching all explicit Tamarin output lines. Version/parse/proof logs are preserved. The abstract `formal/qsv2g_classical_consent.spthy` is **not** a model of QSS quantum physics, anonymous privacy, compromise resistance or physical V2G. It was not parsed/proved in this sandbox because tools were absent; an installed Kaggle run is needed.
- **Full notebook:** `SMOKE=False` by default; full E1 18,000 transactions, E2 Hypothesis 1,000 examples × up to 50 actions, E3 300,000 vector trials plus 6,000 genuine endpoint-token trials, E4 eleven controlled scenarios, E5 conditional install-and-prove. **These counts are planned, not completed results.** Kaggle session limits/network access can prevent completion; archive partial logs instead of claiming success. Historical Stage 01–04 data stays untouched.
- **Installation provenance:** Tamarin 1.12.0 archive sha256 `201be06f469e47cff554df6ca93db8366fc2c69d70c61fcbd1370a1074b469c6`; Maude 3.5.1 archive sha256 `72ed1ca87e3b3d0dfc6ee1436baf154bf04c45ff97d521bec040c5e8dfc8f92c`; see official GitHub releases. Binary compatibility, resource constraints and actual formal proof results remain to be tested in Kaggle.
