# Reproduce the simulation

Install from the repository root: `python -m pip install -e ".[dev]"`.
The post-quantum crypto backend requires compatible `pqcrypto` or OpenSSL >=3.5.

Examples:

```bash
python scripts/run_protocol.py --pair AC --operation CHARGE --length 9
python scripts/run_experiment.py --study validation
python scripts/run_experiment.py --study security
python scripts/run_experiment.py --study noise
python scripts/run_experiment.py --study performance
python scripts/run_experiment.py --study availability
python scripts/run_experiment.py --study security-adversarial
python scripts/run_experiment.py --study reliability
python scripts/run_formal.py --model consent
python scripts/run_formal.py --model compromise
python scripts/reproduce_all.py
```

Default runs are *smoke* budgets; opt into the expensive datasets with `--full`.
Consecutive executions have different crypto randomness and platform timings.
Old archived result files must not be merged with new experiments as if the same protocol revision were tested.
