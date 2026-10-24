# Available run logs

- [`kaggle/quantum_validation_download.txt`](kaggle/quantum_validation_download.txt) — **user-supplied Kaggle quantum-validation console-log extract**, preserved as provided. See [the Kaggle-log README](kaggle/README.md) for its assertions and limitations.
- [`local_executed/`](local_executed/) — notebook outputs extracted from three **locally executed** notebook snapshots; these are not Kaggle runtime logs.
- [`../results/`](../results/) — structured CSV and JSON reports, manifests, and protocol execution traces.

**Provenance note:** The quantum console extract contains a `/kaggle/working/` output path and successful tool checks, but it does not include a verifiable Kaggle run ID, revision URL, or the complete logs of the other two notebook families. Do not treat locally executed notebook outputs as Kaggle evidence.
