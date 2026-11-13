# QSV2G Stage 05 — Pre-Kaggle source and smoke audit (2026-11-13)

## Verified scope

- Inspected the real GitHub `main` commit originally at `67112080824e353000257ca0e7fea0b45f4021c9` and compared Git blob SHA-1 hashes of all Stage 05 source, code, test, Tamarin, and notebook files against local copies. All selected copies matched.
- Locally reran syntax compilation and the complete regression suite after the cross-check amendments: **45 passing tests** (in this execution environment). Real OpenSSL 3.5.5 ML-KEM-768/ML-DSA-65 smoke flows are covered; fake HMAC cryptography in isolated state-machine tests is labeled non-cryptographic.
- E1–E4 local smoke workflow: E1 18 transactions, E2 36 hand-selected scenarios with zero expected/outcome mismatches, E3 120 complete-vector attempts plus a separate small real-PQC token subset, and E4 11 authority/transaction scenarios including concurrent START. These are tiny pilots, **not final empirical results**.
- E3 local analysis and figure regenerate from the new raw trial files. E1 reporting retains failures explicitly; unmatched E2 and unexpected E4 events now fail the run.
- E5 Tamarin binary and Maude are **absent** in the local environment. No parser, execution, or proof success has been observed; E5 remains an unexecuted candidate. A wrong quoted `true` symbol in the original theory was corrected based on the Tamarin manual, but execution is still mandatory before any security claim.
- Hypothesis is **not installed here**, and container package installation failed due DNS/network isolation. The generated-sequence campaign has therefore not been executed locally. Kaggle must install and run it; the notebook fails explicitly if this stage cannot run.

## Corrective changes made after the first Stage 05 commit

1. Prevent E1 classical baselines from needlessly creating a QSS resource; report inclusive and exclusive preparation timing separately and abort if any timed transaction did not complete.
2. Make E2 generated tests progress through protocol states instead of allowing an always-active no-op; fail expected/outcome mismatches.
3. Fix Tamarin signing verification to use builtin `true` rather than the distinct quoted string `'true'`.
4. Clip the modelled execution tick at authorization expiry, reject invalid power/durations, atomically consume the START permission once, and test concurrent STARTs under real PQC.
5. Add regression coverage for comparator resource initialization, inclusive timing, Tamarin constants, partial-tick expiry, and negative power.

## Scientific limitations / before-publication blockers

- The existing six-page `micro.tex` KEM-EV formula specifies fewer bound fields than the current `src/qsv2g_core.py`; align and freeze the manuscript specification explicitly.
- Complete E1 and E3 full-scale workloads have **not been run** on Kaggle. The intended non-smoke plan is computationally substantial; inspect runtime and split independent final runs when necessary. Figures and summary numbers cannot be copied from pilot data into the paper.
- E1 quorum is functionality-weaker; classical sharing vs QSS is the intended matched recovery comparison. E1 excludes real network/quantum transmission costs. Five process blocks provide limited uncertainty information.
- E2 in-memory actor state is not deployed independent services. Hypothesis action sequences are not uniform random attacker samples or proof of security.
- E3 ideal computational-basis sampler is not a density-matrix coherence study, malicious-dealer VQSS experiment, or physical-noise channel. Real ML-DSA token checks are a smaller separate cohort at `L=9` only.
- E4 mutex protects a single in-process permission; no crash-durable distributed single-use authorization, network fault injection, or charger meter enforcement.
- E5 only models an honest A/B classical flow with an **assumed QSS gate**. Until Tamarin parses the theory and reports all lemmas individually, claims of symbolic proof must remain unresolved. The model does not establish quantum security or arbitrary one-authority compromise resilience.

## Go/no-go decision

**GO** for Kaggle `SMOKE=True` preflight of E1–E4 and attempted E5 execution/status collection. **NO-GO** for claiming full E1–E5 completion, successful E5 proof, hardware validation, manuscript parity, or publication-ready statistics until full run files have been reviewed.

Once Stage 05 is run on Kaggle, preserve: pinned exact source commit and source hashes, `pip_freeze.txt`, experiment CSVs, all statuses (not just successes), analysis/figure outputs, notebook run logs, formal proof/parse logs or explicit unavailability, and `artifact_manifest.json`. Historical Stage 01–04 artifacts remain unchanged.
