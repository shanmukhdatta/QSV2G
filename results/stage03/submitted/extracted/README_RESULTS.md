# QSV2G Stage 03 — Results and provenance

Quantum noise and classical trit recovery in an exact 27-dimensional three-qutrit density-matrix model.

## Experiment files
- noise_trial_events.csv.gz: 315,000 raw seeded trial events (including explicit erasure aborts).
- noise_trial_aggregates.csv: all 315 configurations, outcome counts, Wilson 95% intervals, analytic expectations.
- quantum_fidelity_codespace.csv: pure-state fidelity, code-space projection, erasure interpretation.
- noise_channel_summary.csv: model-by-p aggregates.
- legacy_qutrit_x_error_trials_original.csv: original 900-shot baseline (unaltered).
- legacy_x_comparison.csv: archive versus newly sampled X results; distinct runs and sizes.
- resource_length_independence_extrapolation.csv: iid mathematical extrapolation, NOT measured complete workflows.
- authority_availability_assumptions.csv: QSS threshold availability versus UC-A/UC-B workflow requirement.
- outcome_totals_by_model.csv: totals.
- five .png plots: measured reconstruction, quantum fidelity, code-space, legacy X, iid resource sensitivity.
- qsv2g_core_reference.py and QSV2G_SectionIV_reference.tex: full previous tested sources, SHA-256 verified.
- stage03_summary.json, stage03_artifact_manifest.json: environment and hashes.
- stage03_console_log.txt: notebook-written scientific progress/summary, NOT original Kaggle platform log.

## Methods
Channels act solely on the second share of the chosen pair. All models are ideal mathematical channels;
flagged share erasure aborts the selected pair attempt. Error p is a local channel parameter.

Recovery is classical computational-basis measurement of two shares. A dephasing channel can
lower fidelity while preserving computational-basis recovery. No formal security proof, real
quantum communication, physical authorization, or malicious-dealer resilience is established.

Previously archived X-error data have 900 trials per pair per p with random secret symbol.
The new Stage03 data have 1000 trials per symbol-pair-p, or 3000 per pair per p, and distinct seeds.

## What to upload
Send the produced ZIP and the Kaggle executed notebook, ideally with the saved Kaggle run URL/revision.
