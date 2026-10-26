# QSV2G — Stage 03 Uploaded Results Audit

**Input:** `qsv2g_stage03_quantum_noise_results.zip` (user-supplied).

## 1. Artifact integrity and traceability

- ZIP opened successfully: **20 files**, with no CRC errors.
- Artifact manifest lists **19 other files** (self-excluding): **19/19 file sizes and SHA-256 digests matched**.
- Exact reference Python source SHA-256: `2c86ca9eecbc5925100722119f061e640df03f993e14909b3078b23406330758`.
- Exact reference Section IV LaTeX SHA-256: `4ca43b1f6debd2e2bf314ff9adf74f0ad08ba1702e1055eca1943b9533290ef2`.
- Original historical Pauli-X CSV SHA-256: `b55b31f50c15b8cf3d9dea2336bbaef873947041042163763ca9a77fd053bfaa`.
- Source hashes match the established QSV2G reference revision. This does **not** establish identity with the latest manually edited manuscript.
- Archive reports Kaggle detected, Python 3.13.15, NumPy 2.1.3 and pandas 2.3.3. The embedded console extract is **not a complete native Kaggle run history**. The original executed Kaggle notebook URL/revision remains outstanding.

## 2. Independent data audit

- **315 distinct configurations**: five models × three authority pairs × three encoded trits × seven channel probabilities.
- **315,000 raw trial events**: exactly 1,000 trials per configuration, no duplicate `(config_id, trial)` keys.
- Raw event `correct/wrong/abort` counts agree **exactly** with all 315 aggregate rows, all 35 model-by-p summary rows, and the per-model totals.
- Per-configuration counts total 1,000, probabilities are in range, and observed success rates fall inside their recorded Wilson 95% intervals.
- Model-derived theoretical correct probabilities agree with the exact density-matrix values recorded for all 315 configurations.
- **307/315** reported Wilson 95% intervals contain the corresponding exact-model success probability (allowing 1e-12 for CSV floating precision); eight intervals miss due to observed sampling variation, not necessarily an error.
- Maximum absolute sample-to-theory deviation is **2.90 percentage points** in one 1,000-shot configuration.
- The raw event results contain **no wrong decoded trits for dephasing** and **no incorrectly decoded trits in flagged-erasure cases**; erasure instead records aborts.

## 3. Main quantitative finding (p = 0.30)

The following figures are **sampled single-trit recovery probabilities pooled across three pairs and three trits**, with 9,000 attempts per noise model at this p. The channel acts on **the second share of the selected pair only**, and the p values are model parameters, not physical network measurements.

| Model | Correct classical-trit recovery | Wrong | Abort | Exact-model expectation | Encoded-state fidelity |
|---|---:|---:|---:|---:|---:|
| Pauli-X | 70.07% | 29.93% | 0.00% | 70.00% | 70.00% |
| Dephasing | 100.00% | 0.00% | 0.00% | 100.00% | 80.00% |
| Depolarizing | 80.28% | 19.72% | 0.00% | 80.00% | 73.33% |
| Flagged erasure | 70.38% | 0.00% | 29.62% | 70.00% | N/A (erasure flag; conditional fidelity 1.00) |
| Combined | 59.01% | 40.99% | 0.00% | 59.00% | 42.53% |

Dephasing retains 100% computational-basis trit recovery in this model while reducing ideal-state fidelity to 80%. Therefore a statement of robustness to dephasing must be restricted to this **classical measurement criterion**, not coherent quantum-state preservation.

## 4. Review of supplied figures

1. `noise_model_reconstruction.png` — **Recommended for main paper Section VI.B**; clearly shows correct classical-trit recovery vs noise. Caption must specify 9,000 aggregate attempts per p per model, local second-share channels, and that flagged erasures count as unsuccessful attempts.
2. `quantum_state_fidelity.png` — **Useful but requires a plotting correction**: the existing y-axis begins at **0.45**, clipping the combined-noise fidelity at p=0.30 (**0.4253**). A corrected plot with a 0–1 scale is provided separately as `QSV2G_Stage03_Fidelity_Figure_Corrected.png` (generated from the saved CSV; original output unchanged).
3. `legacy_vs_new_pauli_x.png` — Useful to demonstrate repeatability, but preferably in an appendix/supplement to avoid spending a main-page figure on two batches of the same X-model.
4. `qss_codespace_probability.png` — Scientifically informative for **limitations/interpretation**: membership in the ideal code subspace does not prove the intended logical secret was encoded. Use if paper space permits.
5. `resource_length_theoretical_reliability.png` — **Analytical extrapolation only** using the i.i.d. product `P(single trit success)^L`; not a measured end-to-end result. Label explicitly in the caption if used.

## 5. Limitations that must remain explicit

- 315,000 events are seeded **Monte Carlo samples from exact density-matrix outcome distributions**, not 315,000 independently simulated end-to-end QSV2G transactions or physically executed quantum circuits.
- These noise channels affect one selected share. Realistic correlated multi-share channel loss, quantum memories, hardware gates, network effects, and rerouting to alternate authority pairs are **not measured**.
- `diagnostic_mismatch` compares recovered symbols to a known experimental label. **No production commitment false-acceptance tests were run in Stage 03** (`commitment_false_acceptance_tested=False` for all 315 aggregate records).
- The erasure model aborts the selected pair rather than simulating an actual recovery using another authority pair. Its surviving-branch fidelity is 1; the **extended-space erasure fidelity** is 1-p, and these two figures must not be conflated.
- The `resource_length_independence_extrapolation.csv` is a mathematical product model, **not** experimental measurement of whole-vector authorization reliability.
- The original Stage 03 ZIP records a notebook-generated console summary. For precise Kaggle provenance, also preserve an executed `.ipynb`, Kaggle notebook version URL/run ID, and platform console output when available.
- Summary `PASS_WITH_MODEL_LIMITATIONS` means the configured experiment completed consistently, **not** that QSV2G has been proven secure in realistic noisy conditions.

## 6. Paper recommendation and next action

**Stage 03: accepted as internally consistent modeled quantum-noise evidence**, subject to precise scope disclosure and corrected fidelity plot. Use the first and corrected second figures, with the underlying numeric CSVs available in the reproducibility repository. This evidence supports **Section VI.B: Quantum Reconstruction and Noise Analysis**, not the claimed soundness of malicious-secure QSS or entire charging transactions in quantum-network conditions.

**Next:** Stage 04 — Computational and Communication Performance with controlled classical baselines; preserve a fixed platform and backend, repeat timings, and account for quantum transmissions separately. No GitHub commit has been performed as part of this audit.
