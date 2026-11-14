# Reproducible research evidence

- `raw/`: preserved original CSV/JSON observations, indexed by scientific task.
- `summaries/`: condensed statistics and interpretation, not substitutes for raw data.
- `figures/`: previously reported figures and selected derived plots.
- `logs/`: recorded terminal and Tamarin proof outputs.
- `manifests/`: source SHA-256, environment and artifact-provenance evidence.

All original archived Kaggle ZIPs and exact historical notebooks remain reachable
via the archive branch. Original numerical evidence must retain the version of
code it was recorded under; do not silently pool different runtimes.

Modern default command runs produce bounded preflight data. Use `--full` explicitly
for the documented full-scope simulations and benchmarks.
