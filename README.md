# QSV2G — Quantum-assisted V2G authorization research prototype

**Research software, not a deployed EV/charger system or physical quantum network.**

This repository provides a modular **Python** implementation, executable software studies,
formal symbolic abstractions, and preserved result evidence. It includes genuine
ML-KEM-768 / ML-DSA-65 operations, while Bell-state and three-qutrit operations
are simulated mathematically. **A signature over a reconstruction digest is not
an independently verifiable quantum-reconstruction proof.**

## Five-folder layout

- [`src/qsv2g`](src/qsv2g/) — protocol, cryptography, quantum math, resources and evaluation APIs.
- [`scripts`](scripts/) — one-transaction and task-oriented reproducibility commands.
- [`tests`](tests/) — regression, model, integration and parity checks.
- [`results`](results/) — original raw evidence, summary outputs, logs and figures.
- [`docs`](docs/) — methodology, protocol specification, formal theories and limitations.

## Quick start

```bash
python -m pip install -e ".[dev]"
python scripts/run_protocol.py --pair AB --operation CHARGE --length 9
python scripts/run_experiment.py --study validation
python scripts/run_experiment.py --study security --full
python -m pytest -q tests
```

All scripts fail rather than silently replacing ML-KEM/ML-DSA with a classical stub.
The separate hypothesis test uses a clearly labeled TEST-ONLY surrogate and is
**not** a cryptographic-security benchmark.

## Reproducibility and scope

See [`docs/methodology.md`](docs/methodology.md) for experiment definitions and
[`docs/reproducibility.md`](docs/reproducibility.md) for environment/provenance.
See [`docs/threat_model.md`](docs/threat_model.md) and
[`docs/limitations.md`](docs/limitations.md) before making security claims.

Historical development revisions and original notebooks are preserved on
[`archive/pre-modularization-2026-11-14`](https://github.com/shanmukhdatta/QSV2G/tree/archive/pre-modularization-2026-11-14).
The active interface groups experiments by *scientific question*, not chronological notebook stages.

This code has no physical charger, quantum transmission channel, distributed persistence,
malicious-secure VQSS verification, or demonstrated quantum security advantage over
classical threshold sharing. Formal Tamarin results are scoped to the mathematical
models and assumptions stated in the theory files.
