# Results — navigate by experiment

| Directory | Experiment and files |
|---|---|
| [`final_validation/`](final_validation/) | 38 validation cases, 720 ideal QSS trials, equation mapping, assumptions, execution trace, summary JSON |
| [`full_protocol_openssl/`](full_protocol_openssl/) | Full protocol results reporting the OpenSSL ML-KEM/ML-DSA backend |
| [`full_protocol_pqcrypto/`](full_protocol_pqcrypto/) | Separate full protocol results reporting native `pqcrypto` backend |
| [`quantum_validation/`](quantum_validation/) | Independent qutrit quantum correctness and X-error observations |
| [`archives/`](archives/) | Original untouched source ZIP files for all available result variants |

Original plots are also extracted into [`../figures/experimental/`](../figures/experimental/). **Do not aggregate cross-environment timing measurements.** All results are from software simulation and should be attributed to their source manifests.
## Newly uploaded staged experiments

- [Stage 01: original submitted ZIP and extracted files](stage01/README.md)
- [Stage 02: original submitted ZIP and extracted files](stage02/README.md)

- [Stage 03 simulated quantum-noise evaluation](stage03/) — unchanged original user-submitted ZIP, 315,000 compressed trial records, fidelity and aggregate CSVs, plots and manifest.
- [Stage 04 software performance evaluation](stage04/) — unchanged original user-submitted ZIP, raw workflow/QSS scaling/microbenchmark CSVs, object sizes and manifest.

Run `python scripts/verify_stage03_stage04.py` from the repository root for byte-integrity and recorded counts. Local preflight artifacts are separate.
