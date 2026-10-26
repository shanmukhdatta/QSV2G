# Notebook guide

Three original experiment notebooks are preserved as runnable `.ipynb` source files.

| Notebook | Purpose | Original outputs |
|---|---|---|
| [Complete protocol](QSV2G_Kaggle_Full_Protocol_Implementation.ipynb) | Registration, ML-KEM session, three-qutrit QSS, two-signature authorization, CHARGE/DISCHARGE, faults and timing | `../results/archives/full_protocol_*_reported.zip` |
| [Independent quantum checks](QSV2G_Kaggle_Quantum_Qiskit_PennyLane_Validation.ipynb) | Pairwise qutrit reconstruction, one-share marginals, stabilizers, X-errors; optional Qiskit/PennyLane embeddings | `../results/archives/quantum_validation_variant_*.zip` |
| [Final protocol validation](QSV2G_Final_Protocol_Validation_Kaggle.ipynb) | 38 expected-outcome cases, including 4 known-limitations demonstrations, 720 ideal trials, provenance mapping | `../results/archives/final_validation_submitted.zip` |

**Execution:** Use a recent Python 3 environment or import each notebook into Kaggle. Run the first dependency cell, then Run All. CPU is sufficient for the documented example settings. Internet may be required for first-time dependency installation. The notebook saves outputs to its runtime-specific output directory. Do not claim running in Kaggle based on a local output file.

`local_executed/` contains existing locally executed snapshots, separate from these source notebooks.
## New experimental stages

- [Stage 01: baseline reproducibility](stage01/README.md)
- [Stage 02: security analysis — corrected Kaggle version](stage02/README.md)
