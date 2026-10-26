# Experiment-to-evidence index

| Claim or check | Evidence files | Reproduction entry point |
|---|---|---|
| Ideal QSS pair recovery (720/720) | `results/final_validation/qss_pair_ideal.csv`, `validation_summary.json` | `notebooks/QSV2G_Final_Protocol_Validation_Kaggle.ipynb` |
| 38/38 expected outcomes matched | `results/final_validation/validation_case_results.csv`, `validation_summary.json` | Final validation notebook |
| Explicit known limitations (4 cases) | `results/final_validation/validation_case_results.csv` (`type=known_limitation`) | Final validation notebook |
| CHARGE/DISCHARGE across authority pairs | `results/final_validation/authorization_controls.csv`, execution trace | Final validation notebook |
| Quantum state/marginal and stabilizer checks | `results/final_validation/qss_stabilizer_checks.csv` and `results/quantum_validation/` | Independent quantum and final validation notebooks |
| Functional rejection/fault cases | `results/full_protocol_*/qsv2g_failure_tests.csv` | Full protocol notebook |
| Selected phase timing | `results/full_protocol_*/qsv2g_phase_timing.csv` | Full protocol notebook; compare *within* a backend only |
| Selected protocol execution | `results/final_validation/protocol_execution_trace.csv` | Final validation notebook |
| Source-equation traceability | `results/final_validation/equation_to_code_mapping.csv` | Final validation notebook; not a formal proof |
| Local executed-cell text | `logs/local_executed/*.txt` | Embedded outputs in `notebooks/local_executed/` |

**Input archives:** Unchanged original ZIPs in `results/archives/`. Their identity and reported runtime are described in `docs/PROVENANCE.md`. The independent execution provenance of Kaggle (run page/logs/version) has not been supplied.
## Reproducibility stages added 2026-10-26

See [Stage Evidence Index](STAGE_EVIDENCE_INDEX.md) for Stage 01/02 test-to-notebook-to-result-to-audit links, per-stage ZIP hashes, and Kaggle provenance limitations.

## Stage 03 / 04 result mapping

| Study | Primary raw evidence |
|---|---|
| Five QSS noise models and reconstruction | [Stage 03 aggregates](../results/stage03/submitted/extracted/noise_trial_aggregates.csv) |
| 315,000 single-trit events | [Stage 03 compressed events](../results/stage03/submitted/extracted/noise_trial_events.csv.gz) |
| Quantum fidelity and code-space tests | [Stage 03 fidelity CSV](../results/stage03/submitted/extracted/quantum_fidelity_codespace.csv) |
| Software workflow timings | [Stage 04 raw workflows](../results/stage04/submitted/extracted/end_to_end_raw.csv) |
| QSS scaling | [Stage 04 resource raw CSV](../results/stage04/submitted/extracted/qss_resource_scaling_raw.csv) |
| B0/B1/B2 post-context authorization microbenchmarks | [Stage 04 raw baselines](../results/stage04/submitted/extracted/authorization_baselines_raw.csv) |
| Instrumented AEAD packet sizes | [Stage 04 packet sizes](../results/stage04/submitted/extracted/instrumented_aead_packets_raw.csv) |

See [stage-to-evidence traceability](STAGE_EVIDENCE_INDEX.md) for exact ZIP hashes, notebook links, logs and scope.
