# Reproducibility and provenance

## Stable historical reference

Original GitHub revision: `f981f986f1bc01be5f85624da74ff55c20474339`.
Preserved branch: `archive/pre-modularization-2026-11-14`.
The historical archive remains the source of truth for original notebooks,
commit history, old figures, raw CSVs, stage-specific audit notes and audits.

Early experiments used a different reference core than the corrected source
used for later benchmarks. Do **not** attribute numerical historical results to
refactored code until a matched controlled parity rerun is available.

## Recommended environment

Python 3.11+ (tested split under Python 3.13); `pip install -e ".[dev]"`.
For real standardized PQC, compatible `pqcrypto` or OpenSSL >=3.5 providing
ML-KEM-768 and ML-DSA-65 is required. No silent fallback.

Tamarin and Maude are separate *system executables*, not Python modules.
Theories are in `docs/formal/`; they model limited classical rules and an
ideal QSS assumption. A successful `--prove` run does not establish hardware,
quantum information, or full implementation security.

## Results naming

- `results/raw/validation/` — independent correctness trials.
- `results/raw/security/` — consent/context and malicious-authority cases.
- `results/raw/noise/` — single-symbol and full-vector model outputs.
- `results/raw/performance/` — measured software latency and selected packets.
- `results/raw/availability/` — process-local failure and reuse cases.
- `results/raw/reliability/` — analytical/sampled fresh-resource retry model.
- `results/logs/formal/` — parser/prover logs.
- `results/manifests/` — source and environment version mapping.

Original Stage 01–04 ZIP evidence is preserved in the archive branch; Stages
05/06 full Kaggle ZIPs were independently audited as user-uploaded archives.
The notebooks and their version pinning remain in historical Git. The result
ZIPs do not independently authenticate a Kaggle account job URL or immutable
cloud execution revision. Do not invent those identifiers.

## Migration boundary

The active task-based CLI reproduces the modularized contemporary experiment algorithms, but
some early exploratory notebook-only scenarios (including the original 80-case campaign and
separate density-matrix fidelity figures) are retained only as historical executable notebooks
on the archival Git branch. Their original results are copied byte-for-byte to `results/raw/`
where applicable; never substitute the newer 36-case scripted campaign for the earlier 80
cases or present the two as equivalent. A full historical notebook re-execution is not asserted.

The modular Kaggle runner pins the complete source SHA `0034712a9509affa1c3c17aa0f6b39a679aa740a`
 rather than a moving branch name; this SHA contains the validated modular Python code and
experiment routines. Newer commits may correct documentation or metadata independently.
