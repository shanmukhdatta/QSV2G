# Final validation — 38 cases / 720 ideal trials

**Source notebook:** [`../../notebooks/QSV2G_Final_Protocol_Validation_Kaggle.ipynb`](../../notebooks/QSV2G_Final_Protocol_Validation_Kaggle.ipynb)

Key files:

- [`validation_summary.json`](validation_summary.json): totals, backend, manuscript/source hashes.
- [`validation_case_results.csv`](validation_case_results.csv): all 38 cases, expected versus observed behavior, category and interpretation.
- [`qss_pair_ideal.csv`](qss_pair_ideal.csv): 720 individual ideal reconstruction trials.
- [`authorization_controls.csv`](authorization_controls.csv): CHARGE/DISCHARGE and authority-pair end states.
- [`qss_stabilizer_checks.csv`](qss_stabilizer_checks.csv): ideal quantum state consistency measurements.
- [`protocol_execution_trace.csv`](protocol_execution_trace.csv): one recorded phased execution, not a network packet trace.
- [`equation_to_code_mapping.csv`](equation_to_code_mapping.csv): curated equation-to-code traceability, **not** a mathematical proof.
- [`explicit_assumptions.csv`](explicit_assumptions.csv): modeled versus unmodeled system conditions.

**Interpretation:** The 38/38 result means *observed behavior matched the stated expected outcome*, including deliberately demonstrated limitations. It does not mean 38 security guarantees. The 720/720 reconstruction results apply to ideal simulated three-qutrit states, not noisy deployed quantum hardware.
