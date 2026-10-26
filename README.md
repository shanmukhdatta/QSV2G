# QSV2G — Research simulation and reproducibility archive

QSV2G studies cross-domain electric-vehicle/charging-station authentication and transaction-bound **2-of-3 quantum-secret-sharing (QSS)** based authorization. This repository contains the reference software simulation, quantum correctness checks, validation notebooks, and accompanying result archives.

> **Scope:** Research prototype only. Idealized qutrit quantum-state simulation, not an experimentally demonstrated quantum V2G network or a proof of malicious-secure verifiable QSS. Two distinct authority signatures attest to reconstruction; they do not independently prove to the EV that quantum reconstruction occurred.

## Contents

- `src/qsv2g_core.py`: exact reference implementation extracted from the full protocol notebook.
- `notebooks/`: three source notebooks (complete protocol, independent quantum validation, final 38-case validation).
- `notebooks/local_executed/`: executed notebook snapshots from a **local** runtime; these are not independent proof of a Kaggle run.
- `results/archives/`: original result ZIPs, preserved without modification.
- `results/final_validation/`: extracted 38-case outputs, including 720 ideal QSS reconstruction trials.
- `results/full_protocol_*/`: separate result sets for the reported OpenSSL and native `pqcrypto` backends. **Do not combine cross-environment timing results.**
- `results/quantum_validation/`: quantum state checks and reconstruction results.
- `logs/local_executed/`: stdout/text saved from the local executed notebook files (not original cloud runtime logs).
- `protocol/`: Section IV LaTeX source associated with the manifest hashes, plus a clearly marked earlier Markdown draft.
- `docs/`: provenance, limitations, and verification guide.
- `scripts/verify_artifacts.py`: local integrity/summary consistency checks (not a security proof).

## Reproduction

1. Create a fresh Python environment or use a Kaggle notebook with the packages required in its first setup cell. **Review the dependencies before executing.**
2. Run `notebooks/QSV2G_Kaggle_Full_Protocol_Implementation.ipynb` for the protocol and benchmark scenarios.
3. Run `notebooks/QSV2G_Kaggle_Quantum_Qiskit_PennyLane_Validation.ipynb` for independently implemented ideal quantum-state checks.
4. Run `notebooks/QSV2G_Final_Protocol_Validation_Kaggle.ipynb` for the 38-case test suite.
5. Inspect each run's exported ZIP, `manifest.json` or `validation_summary.json`, and its raw CSVs.
6. Run `python scripts/verify_artifacts.py` from the repository root to check archived-file integrity and expected result-summary counts.

The notebooks select standardized ML-KEM-768 / ML-DSA-65 implementations from the available `pqcrypto` or OpenSSL 3.5+ backend. Their actual installed versions are recorded in the supplied manifest files. Hardware cryptography, authenticated quantum networking, secret provisioning, crash-persistent state, physical energy metering, and formal security proofs are **not** established here.

## Main findings reported by supplied results

- Final suite: **38/38 observed outcomes matched the specified expected outcomes**; this includes tests demonstrating unresolved limitations.
- Ideal quantum secret reconstruction: **720/720 successful trials** (three authorized authority pairs).
- The standalone quantum result archive reports 500/500 samples for each symbol–pair combination (9 combinations).
- The simulation tests CHARGE and DISCHARGE workflows and selected replay/authorization rejection conditions.

Do not interpret these tests as cryptographic security guarantees. See `docs/LIMITATIONS.md`.

## Artifact navigation and provenance

- [Notebook guide](notebooks/README.md) | [Available logs](logs/README.md) | [Results guide](results/README.md) | [Extracted plots](figures/README.md)
- [Experiment-to-evidence lookup](docs/RESULTS_INDEX.md) | [Provenance](docs/PROVENANCE.md) | [Known limitations](docs/LIMITATIONS.md)
- [Reference protocol source](protocol/README.md) | [Environment](environment/README.md) | [Verification scripts](scripts/README.md)

**Disclosure:** The supplied archives do not include independently authenticated Kaggle run history or cloud execution identifiers. Their environment fields are *reported metadata*. Locally executed notebooks are labelled accordingly. The QSKA PDF and full unpublished manuscript are not included. No LICENSE file is provided pending authors' choice of terms.
## Staged experimental evaluations

- **Stage 01 baseline reproducibility:** [notebook](notebooks/stage01/) · [raw submitted results](results/stage01/) · [audit](docs/stages/STAGE01_AUDIT.md). Uploaded outcomes: 38/38 expected; ideal QSS 720/720.
- **Stage 02 security analysis:** [corrected notebook](notebooks/stage02/) · [raw submitted results](results/stage02/) · [audit](docs/stages/STAGE02_AUDIT.md). Uploaded outcomes: 80/80 expected with 7 *demonstrated limitations*.
- [Stage-to-evidence index](docs/STAGE_EVIDENCE_INDEX.md) records the exact source versions and evidence provenance. Original Kaggle console logs and revision URLs for these two stages were not supplied; local preflight logs are labelled explicitly.
