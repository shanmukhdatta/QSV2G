# Test and validation entry points

The source notebooks contain the original executable test harnesses:

- Main protocol notebook: baseline end-to-end and negative scenarios.
- Independent quantum notebook: correctness and perturbation checks.
- Final validation notebook: 38 named cases; see `../results/final_validation/validation_case_results.csv`.

For **artifact integrity and result consistency**, run `python scripts/verify_artifacts.py` from the repository root. This only checks existing files and output consistency; it does not re-run the cryptographic or quantum simulations.

For a new experiment, execute the source notebook, export its outputs, and compare its generated manifests/CSVs to the reference results. Do not treat the included result ZIPs as evidence that the current machine executed them.
