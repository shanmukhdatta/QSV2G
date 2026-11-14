# Reproducible research evidence

- `raw/`: preserved original CSV/JSON observations, indexed by scientific task.
- `summaries/`: condensed statistics and interpretation, not substitutes for raw data.
- `figures/`: previously reported figures and selected derived plots.
- `logs/`: recorded terminal and Tamarin proof outputs.
- `manifests/`: source SHA-256, environment and artifact-provenance evidence.

The six principal original experimental ZIPs are published in `archives/` with their
original hashes; see [`archives/README.md`](archives/README.md) for exact filenames and
[`manifests/kaggle_archive_sha256.json`](manifests/kaggle_archive_sha256.json) for checksums.
Verify locally with `python scripts/verify_archived_evidence.py`. Original historical
notebooks remain reachable via the protected archive branch. Original numerical evidence must retain the version of
code it was recorded under; do not silently pool different runtimes.

Modern default command runs produce bounded preflight data. Use `--full` explicitly
for the documented full-scope simulations and benchmarks.
