# QSV2G — Stage 04 Independent Results Audit

**Input:** User-uploaded `qsv2g_stage04_performance_results.zip` (28 ZIP members).  
**Scope:** Internal consistency and evidence sufficiency of the submitted software performance measurements. This is not an independent rerun, a physical test, or a security proof.

## 1. Artifact integrity and provenance

- ZIP CRC validation: **PASS**.
- Manifest: **27/27 listed files have exactly matching byte sizes and SHA-256 hashes**; `manifest.json` is the 28th member and is excluded from its own manifest by design.
- The reported core source SHA-256 is `2c86ca9eecbc5925100722119f061e640df03f993e14909b3078b23406330758`, consistent with the earlier QSV2G reference implementation.
- The reported Section IV SHA-256 is `4ca43b1f6debd2e2bf314ff9adf74f0ad08ba1702e1055eca1943b9533290ef2`. This identifies the **historical revised Section IV**, not necessarily the latest manuscript edition.
- `environment.json` identifies Python 3.13.15, NumPy 2.1.3, pandas 2.3.3, cryptography 50.0.1, native `pqcrypto 1.0.0` with ML-KEM-768 and ML-DSA-65, and a Kaggle working-directory indication. These are **file-reported environment details**, not independently authenticated cloud-run metadata.
- The ZIP contains a generated `run_log.txt`, but does **not** contain the executed Stage 04 `.ipynb`, Kaggle revision URL/run ID, or complete original Kaggle notebook console transcript. The saved reference core and Section IV hashes do not prove the specific experiment notebook revision that generated the data.

## 2. Trial and statistical consistency (independently recomputed)

- Full reference QSV2G workflow: **120 rows** = 30 trials each for QSS length L = 9, 27, 81, and 162; all `resource_consumed=CONSUMED`.
- QSS preparation and reconstruction microbenchmark: **120 rows**, 30 trials each at the four lengths.
- Post-context authorization baseline microbenchmark: **270 rows**, 30 trials for each of 3 authority pairs × 3 authorization modes.
- Phase timings: **1,200 rows**, 10 named phases for each of the 120 full workflows; 1,080 `PASS` and 120 `COMPLETED` phase status values.
- Measured selected AEAD packets: **600 rows**, five packet types per full workflow; sums match all 120 reported five-packet totals.
- Independently recomputed sample counts, mean, median, sample standard deviation, 95th percentile, minimum and maximum match every recorded group in `end_to_end_statistics.csv`, `phase_statistics.csv`, `qss_scaling_statistics.csv`, and `authorization_baselines_statistics.csv`.
- Independently recomputed AEAD packet summary minima, medians, maxima and sample counts match `instrumented_aead_packets_summary.csv`.

## 3. Reference full-workflow results

| QSS secret-vector length L | Runs | Median end-to-end wall time (ms) | Mean (ms) | Empirical p95 (ms) |
|---:|---:|---:|---:|---:|
| 9 | 30 | 63.007 | 63.896 | 68.107 |
| 27 | 30 | 66.278 | 67.360 | 71.162 |
| 81 | 30 | 75.549 | 75.894 | 78.054 |
| 162 | 30 | 89.775 | 90.161 | 93.586 |

**Interpretation:** Software wall time rises by approximately 26.77 ms (42.5%) between L=9 and L=162 in this particular runtime. **No quantum transmission latency, physical metering, or real charging/grid response** is included. Phase-duration sums differ from full wall time because the phase measurements do not capture all orchestration overhead; these must not be equated.

### QSS component scaling

| L | Median resource preparation (ms) | Median threshold reconstruction (ms) | Stored qutrit subsystems (analytical) | Remote qutrit transmissions (analytical) |
|---:|---:|---:|---:|---:|
| 9 | 0.386 | 1.430 | 81 | 54 |
| 27 | 0.941 | 3.914 | 243 | 162 |
| 81 | 2.641 | 11.337 | 729 | 486 |
| 162 | 5.218 | 23.243 | 1,458 | 972 |

The quantum-resource counts use model-specific formulas `9L` and `6L`. They are **analytical accounting**, not observed physical transmissions. The reference simulation also models 512 Bell-registration qubit transmissions, separately from these qutrit counts.

## 4. Authorization baseline microbenchmarks

| Mode | Samples (all pairs) | Pooled median (ms) | Meaning |
|---|---:|---:|---|
| B0 | 90 | 15.986 | One ML-DSA authority signature with local verification |
| B1 | 90 | 31.648 | Two classical ML-DSA authority signatures with local verification |
| B2 | 90 | 55.429 | Actual simulated QSS reconstruction plus two ML-DSA signatures with local verification |

All three modes begin from a pre-registered, authenticated, session-established and approved reference context. These are **post-context authorization microbenchmarks**, not equal-security alternative V2G protocols, and do not include realistic distributed authority communication or quantum transport. B2 adds approximately **23.78 ms median** over the B1 microbenchmark on this recorded environment; interpreting this as a universal or fully causal QSS overhead would overstate the result. The benchmark source alternates B0/B1 order while B2 is always last; residual measurement-order effects cannot be ruled out.

## 5. Communication and key sizes

- Median sum of the **five instrumented AEAD packets**: **10,902 bytes per simulated workflow** for each tested L. It is not total classical protocol communication.
- Of these selected messages, the authorization-response packet is approximately **9,748 bytes**.
- Provider object sizes include ML-KEM-768 public key 1,184 B, KEM ciphertext 1,088 B, ML-DSA-65 public key 1,952 B, signature 3,309 B. Do not treat private/secret keys as transmitted protocol data.
- B1/B2 contain two 3,309-byte signatures (6,618 bytes); B0 contains one. Microbenchmark serialized-token sizes are **not** measured AEAD wire packets.

## 6. Comparison with the historical benchmark

- Prior recorded run: L=162, 8 samples, median **62.078 ms**; new run: L=162, 30 samples, median **89.775 ms**.
- Both identify native pqcrypto, but execution environment/session conditions differ. **Do not pool or directly claim an implementation regression or improvement** from this difference.

## 7. Evidence-to-manuscript decision

**Accepted:** Stage 04 is a valid internally consistent **software-only performance dataset** suitable for a carefully scoped Section VI. It supplies tested latency/scaling, local authorization-overhead comparisons, instrumented selected packet sizes and analytical quantum-resource counts.

**Not established:** Physical quantum-channel latency/fidelity, end-to-end classical baseline equivalence, complete network communication, cryptographic energy consumption, hardware utilization/energy, malicious-secure VQSS, formal security proof, or independently verified Kaggle run provenance.

**Recommended in-paper figures:** (1) end-to-end latency vs. L; (2) QSS preparation/reconstruction scaling; (3) B0/B1/B2 authorization microbenchmark with a clear baseline-scope caption. Move measured selected-packet sizes and resource accounting to a compact table or supplementary material if page-constrained. Figure error bars on the supplied end-to-end chart show **empirical min/max**, not confidence intervals.

**Research-writing steps:** Reconcile the hashed historical Section IV snapshot against the final paper; include an explicit experimental environment, number of trials, and packet-coverage definition; preserve raw CSV and original ZIP; supply the executed Kaggle notebook/revision link if available. Stage 03 results should be archived alongside these Stage 04 outputs before final paper submission.

**GitHub:** No repository writes were performed during this audit.
