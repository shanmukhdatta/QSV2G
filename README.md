# QSV2G

<p align="center">
  <img src="assets/qsv2g_architecture.svg" alt="QSV2G logical system architecture: EV, charging station, and three utility authorities" width="100%" />
</p>

## Pseudonymous Cross-Domain Authentication and Quantum Secret Sharing-Based Authorization for Vehicle-to-Grid Networks

<p align="center">
  <img src="https://img.shields.io/badge/Status-Research%20Prototype-334155" alt="Research prototype" />
  <img src="https://img.shields.io/badge/PQC-ML--KEM--768%20%7C%20ML--DSA--65-2563eb" alt="Genuine post-quantum cryptography" />
  <img src="https://img.shields.io/badge/QSS-Software%20Simulation-7c3aed" alt="Simulated QSS" />
  <a href="https://github.com/shanmukhdatta/QSV2G/actions/workflows/refactor-ci.yml"><img src="https://github.com/shanmukhdatta/QSV2G/actions/workflows/refactor-ci.yml/badge.svg" alt="QSV2G CI" /></a>
</p>

<p align="center"><strong>Shanmukh Datta</strong> &nbsp;&middot;&nbsp; <strong>Kumar Prateek</strong></p>
<p align="center">Dr. B. R. Ambedkar National Institute of Technology Jalandhar, Punjab, India</p>

<p align="center">
  <a href="#overview">Overview</a> &nbsp;&middot;&nbsp;
  <a href="#implementation-components">Implementation</a> &nbsp;&middot;&nbsp;
  <a href="#repository-structure">Structure</a> &nbsp;&middot;&nbsp;
  <a href="#reproducibility">Reproducibility</a> &nbsp;&middot;&nbsp;
  <a href="#experimental-evidence">Evidence</a> &nbsp;&middot;&nbsp;
  <a href="CITATION.cff">Citation</a>
</p>

---

## Overview

**QSV2G** is a research implementation of a cross-domain vehicle-to-grid (V2G) authorization protocol. It separates **EV/charging-station authentication** from **EV consent to a specific CHARGE or DISCHARGE transaction**. After authenticated session establishment, two distinct utility authorities approve the terms, perform modeled (2,3) quantum secret sharing (QSS) reconstruction, and issue transaction-bound ML-DSA-65 attestations.

The prototype implements the four phases described in the accompanying seven-page manuscript:

1. **Initialization and registration:** HMAC-backed enrollment, pseudonym handling, and mathematically simulated Bell-state dense-coding checks.
2. **Mutual authentication and post-quantum session establishment:** Utility-checked EV/CS authentication, genuine ML-KEM-768, transcript-bound HKDF-SHA256, key confirmation, and direction-separated AES-256-GCM traffic keys.
3. **Transaction-bound threshold QSS authorization:** EV-retained transaction intent, (2,3) three-qutrit secret-sharing model, commitments, selected-pair recovery, and two ML-DSA-65 signed authorization attestations.
4. **Protected execution and termination:** EV verification of received authorization terms and signatures, process-local one-use controls, and *simulated* energy-transfer/termination records.

**Implementation boundary:** ML-KEM-768, ML-DSA-65, HMAC, HKDF, SHA-256, and AES-256-GCM run in genuine software libraries. Bell states, qutrit states, noise channels, utility actors, and energy transfer are **software simulations/models**; this is not a deployed quantum or electrical-grid system. The EV verifies signed attestations, **not an independently verifiable proof of QSS reconstruction**.

The [architecture diagram](assets/qsv2g_architecture.svg) illustrates logical roles, not independent machines or physical network links.

---

## Implementation Components

| Component | Source | Implementation |
| --- | --- | --- |
| Protocol state machine | [`src/qsv2g/protocol.py`](src/qsv2g/protocol.py) | Registration through termination; context and token checks; process-local replay/execution state |
| Cryptography | [`src/qsv2g/crypto.py`](src/qsv2g/crypto.py) | Genuine ML-KEM-768 / ML-DSA-65 backend, HMAC, HKDF, SHA-256, AES-256-GCM, typed encoding |
| Quantum models | [`src/qsv2g/quantum.py`](src/qsv2g/quantum.py) | Bell-pair mathematical simulation, three-qutrit vectors, reduced density matrices, pair measurements |
| QSS resource management | [`src/qsv2g/resources.py`](src/qsv2g/resources.py) | Dealer vectors, commitments, reservations, reconstruction, resource consumption |
| Evaluation | [`src/qsv2g/evaluation/`](src/qsv2g/evaluation/) | Correctness, noise, classical baselines, stateful/adversarial checks, performance, retry models |
| Automated tests | [`tests/`](tests/) | Protocol regression, genuine-PQC smoke, QSS properties, experiment and evidence checks |
| Symbolic verification | [`formal/`](formal/) | Two restricted Tamarin models: consent and compromise boundary |

**Threat-model distinction:** QSS can be reconstructed by any approved pair from `{AB, AC, BC}`; in the *current registration and authentication flow*, UC-A and UC-B are still required online. A signature-quorum comparator and a modulo-3 classical-sharing comparator are **not** claimed to demonstrate a quantum advantage.

---

## Repository Structure

```text
QSV2G/
├── assets/
│   └── qsv2g_architecture.svg     # Manuscript-aligned logical architecture
├── src/qsv2g/
│   ├── protocol.py                # Four-phase protocol and lifecycle
│   ├── crypto.py                  # PQC and authenticated classical channels
│   ├── quantum.py                 # Bell/qutrit mathematical simulation
│   ├── resources.py               # QSS preparation, recovery and consumption
│   └── evaluation/               # Nine maintained evaluation families
├── scripts/
│   ├── run_protocol.py            # One complete modeled transaction
│   ├── reproduce_all.py           # All nine maintained studies
│   ├── run_experiment.py          # Individual study and workload selection
│   ├── run_formal.py              # Tamarin proof/attack-model execution
│   ├── check_parity.py            # Migration parity against original core
│   └── verify_archived_evidence.py
├── tests/                         # Automated regression and evidence tests
├── formal/                        # Consent and key-compromise .spthy models
├── results/
│   ├── archives/                  # Preserved historical experiment ZIP files
│   ├── raw/                       # Archived measurements and metadata
│   ├── figures/                   # Historical plots
│   ├── manifests/                 # Provenance and SHA-256 records
│   └── reviewer_audit_2026_11_16/
├── requirements-repro.txt         # Pinned tested reviewer environment
├── REPRODUCIBILITY.md             # Full budgets and instructions
├── IMPLEMENTATIONS.md             # Nine notebooks + maintained package
└── CITATION.cff
```

The [original notebooks are preserved on the historical archive branch](https://github.com/shanmukhdatta/QSV2G/tree/archive/pre-modularization-2026-11-14/notebooks). See [IMPLEMENTATIONS.md](IMPLEMENTATIONS.md) for the ten principal software artifacts (**nine historical notebooks plus this modular package**); these are **not ten independently implemented protocols**.

---

## Reproducibility

### Requirements

The audited reproduction environment uses **Linux, Python 3.12**, and the pinned dependencies in [`requirements-repro.txt`](requirements-repro.txt). The package declares Python 3.10+, but other interpreter/OS combinations have not been verified to the same extent. The primary protocol requires a working **genuine ML-KEM-768 and ML-DSA-65 provider**; a missing provider fails closed rather than silently switching to classical cryptography.

```bash
git clone https://github.com/shanmukhdatta/QSV2G.git
cd QSV2G
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-repro.txt
python -m pip install -e . --no-deps
git rev-parse HEAD
```

Record the Git commit in reports. Historical Kaggle runs and newer reviewer reruns used different Python versions/hosts; do not present all measurements as one hardware campaign.

### Step 1 — Run the Complete Protocol (no quantum hardware required)

```bash
python scripts/run_protocol.py --pair AB --operation CHARGE --length 9
python scripts/run_protocol.py --pair AC --operation DISCHARGE --length 9
```

**Expected:** a JSON trace ending with `"status": "TERMINATED"`, a genuine-PQC backend identifier, and a `"resource_state": "CONSUMED"`. The output describes **modeled**, not physical, charging. Secret keys and AES-GCM nonces use OS randomness; identical bytes/timing are not expected on rerun.

### Step 2 — Test the Implementation and Verify Archived Evidence

```bash
python -m pytest -q tests
python scripts/check_parity.py
python scripts/verify_archived_evidence.py
```

The [CI workflow](.github/workflows/refactor-ci.yml) runs regression tests, checks migration parity, verifies preserved archives, recalculates archived paper claims, and executes bounded protocol/experiment smoke tests. The audit recorded **147 passing regression tests** at its tested revision. Passing tests is not a full security proof. `check_parity.py` requires the original historical revision in local Git history.

### Step 3 — Run the Nine Maintained Experimental Studies

```bash
# Quick, bounded smoke runs of every current study
python scripts/reproduce_all.py --out results/generated/reviewer-smoke

# Analyze the new outputs
python -m qsv2g.evaluation.analysis results/generated/reviewer-smoke

# Full documented budgets (substantially more expensive; use a NEW directory)
python scripts/reproduce_all.py --full --out results/generated/reviewer-full
```

The current runners cover **validation, performance, security, noise, availability, noise-vector, security-stateful, security-adversarial, and reliability**. To run one study, use `python scripts/run_experiment.py --study validation` (or another name from [REPRODUCIBILITY.md](REPRODUCIBILITY.md)). New runs record commands, source hashes, package versions, seed, completion status and output hashes.

**Important:** `--full` means the documented current-study budgets, *not* exact replay of every historical notebook. Use fresh output directories; the runners refuse to overwrite existing results. OS-generated cryptographic randomness and host-dependent timing make some outputs non-bit-identical.

### Step 4 — Reproduce the Manuscript's Figures and Main Statistics from Archived Data

```bash
python -m qsv2g.evaluation.evidence \
  --out results/generated/paper-evidence
```

This command verifies the source ZIP hashes and recomputes paper values from **archived raw observations**, without rerunning the original measurement campaigns.

| Manuscript item | Regenerated output |
| --- | --- |
| Fig. 1 — QSV2G architecture | [`assets/qsv2g_architecture.svg`](assets/qsv2g_architecture.svg) |
| Fig. 2 — Single-trit recovery under five noise channels | `results/generated/paper-evidence/noise_from_raw.pdf` (also `.svg`) |
| Fig. 3 — Median inclusive software latency | `results/generated/paper-evidence/latency_from_raw.pdf` (also `.svg`) |
| Fig. 2 source checks | `results/generated/paper-evidence/single_trit_from_raw.csv` |
| Fig. 3 source checks | `results/generated/paper-evidence/inclusive_medians_from_raw.csv` |
| Counts, source hashes, original study revision | `results/generated/paper-evidence/claim_verification.json` |

**Fig. 2** counts flagged erasures as failures in the sampled classical-trit recovery metric. **Fig. 3** measures inclusive **software** latency; quantum transport, charger actuation, and network delays are excluded. The signature-only quorum does not perform share reconstruction, so it is a weaker-function comparator. Graph generation is a **raw-data reaggregation**, not a fresh full experimental rerun.

### Step 5 — Re-run the Scoped Formal Models (Tamarin + Maude)

Install the tools following [formal/README.md](formal/README.md) and [`scripts/install_formal_tools.py`](scripts/install_formal_tools.py), then run:

```bash
python scripts/run_formal.py --model consent --out results/generated/formal
python scripts/run_formal.py --model compromise --out results/generated/formal
```

The recorded proof environment used **Tamarin 1.12.0** and **Maude 3.5.1**. The consent model has **four** verified lemmas; the compromise model has **three**, including **an attack-existence lemma**. Both models assume an ideal QSS gate; a verified bypass trace must **not** be described as resistance to that attack. Tools must be installed and available on `PATH` for the commands to work.

**Full reproduction instructions, trial budgets, and provenance:** [REPRODUCIBILITY.md](REPRODUCIBILITY.md).

---

## Experimental Evidence

The original results and the November 2026 reviewer reruns remain distinct. The repository contains the raw data, archives, proof logs and scripts needed to inspect the scope of each claim.

| Study | Preserved evidence | What is reported |
| --- | --- | --- |
| Ideal recovery and protocol correctness | [`results/raw/validation/`](results/raw/validation/) | 720/720 ideal pair recoveries; separate expected-outcome validation cases |
| Single-trit quantum noise | [`results/raw/noise_earlier/`](results/raw/noise_earlier/) | 315,000 modeled trials, five channels, seven error rates |
| Full-vector reliability and real-PQC endpoint checks | [`results/raw/authorization/e3/`](results/raw/authorization/e3/) | 300,000 modeled vector trials; separate 6,000 endpoint trials |
| Matched classical comparisons | [`results/raw/authorization/e1/`](results/raw/authorization/e1/) | 18,000 complete transactions; QSS, modulo-3 classical sharing, signature quorum |
| Adversarial and stateful analysis | [`results/raw/security_research/`](results/raw/security_research/) | 96 expected controls, compromise-dependent bypasses, modeled retries |
| Symbolic verification | [`formal/`](formal/) and [`results/raw/authorization/e5/`](results/raw/authorization/e5/) | Four consent + three compromise lemmas under documented abstractions |
| Original archives and audit | [`results/archives/`](results/archives/) and [`results/reviewer_audit_2026_11_16/`](results/reviewer_audit_2026_11_16/) | Historical bytes, manifests, recorded execution/verification evidence |

For interpretation and limits, consult [REPOSITORY_AUDIT.md](REPOSITORY_AUDIT.md) and [PAPER_EVIDENCE_NOTES.md](PAPER_EVIDENCE_NOTES.md). Expected security-test outcomes include **known successful attacks under stronger compromise assumptions**; do not total all cohorts as independent attack preventions. At `L=162`, the historical median inclusive latency was **88.41 ms** for QSS versus **64.81 ms** for classical sharing (about **36.4% more time**).

---

## Scope and Limitations

This is an **idealized, single-process research prototype**, not a physical V2G or quantum-network deployment. Authority signing keys are co-resident; distributed key custody, malicious-secure verifiable QSS, crash-durable replay/nonce state, remote quantum communication, independent endpoint proof of reconstruction, and physical energy enforcement are not established. In the documented compromise analysis, **two compromised signing keys plus privileged charging-station control** can yield an accepted attestation without reconstruction.

The code and recorded formal abstractions support specific functional and trust-boundary findings; they do **not** establish universal man-in-the-middle resistance, composable protocol security, a deployed quantum advantage, or equivalent security to a classical threshold baseline.

**Submission note:** The manuscript is maintained separately from this source branch. The public repository, Git history and some original archives may contain author-identifying material; inspect the target venue's anonymity rules before sharing it in a double-blind submission.

---

## Citation

See [`CITATION.cff`](CITATION.cff) for the software citation metadata. No paper acceptance, DOI or independent security certification is asserted here.

## License

**No `LICENSE` file is currently supplied.** Public visibility does not grant unrestricted reuse or redistribution rights. Contact the authors for permissions; do not assume that another project's license applies to QSV2G.
