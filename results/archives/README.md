# Original submitted experimental archives

These ZIPs are research evidence, not generated on the fly from the modular package. Do **not** replace an original archive with a re-exported summary or change its internal filenames. SHA-256 values and original internal manifests distinguish the exact user-submitted results from later re-executions.

| Scientific study | Preserved original ZIP | SHA-256 | Source snapshot / scope |
|---|---|---|---|
| Reference correctness and ideal QSS | [`ideal_validation_historical.zip`](ideal_validation_historical.zip) | `1f6ae90f215ae5f74518d4b007a6cca469e8dbdde0ea1ac8d82956d2aaddf202` | Earlier reference core; 38 expected outcomes including known limits and 720 ideal recoveries |
| Security and adversarial scenarios | [`security_scenarios_historical.zip`](security_scenarios_historical.zip) | `be4f42ff39a999e246a54e7e68c75ec16992a1d83dcdcc690e03ac195c2fd7af` | Earlier reference core; 80 expected outcomes and 7 exposed limitations |
| Five noise-channel models | [`quantum_noise_historical.zip`](quantum_noise_historical.zip) | `b76f05afca3d872ce3bc7b4ea043ec7e10ef3d555e042cdadc0eda8e5f0b0d95` | Earlier reference core; 315,000 Monte Carlo sampled single-trit events |
| Software performance and baselines | [`performance_historical.zip`](performance_historical.zip) | `9a60827099be191398931b8ddf036c5664b4f19410c0761de54031ad869f11e0` | Earlier reference core; 120 complete workflows, 120 scaling, 270 microbenchmarks |
| Matched software evaluation, attacks, vector noise and symbolic consent | [`qsv2g_stage05_final_20261113T092554Z.zip`](qsv2g_stage05_final_20261113T092554Z.zip) | `87418c800c96537b143b7df594eaa79ee4015a05c867303f6239b40097316ee6` | `b463fc758fa28f1853fe06c4130ee2f25173ac0c`; full E1–E5 original Kaggle output, 32 members, 31 manifested |
| Authority-compromise boundary, classical parity, modeled retries and extended symbolic model | [`qsv2g_stage06_full_20261113T111031Z_results.zip`](qsv2g_stage06_full_20261113T111031Z_results.zip) | `5272eee4505b6c7b3be5fe50cca651c8ff4b8a42b36d38685be1983c335b9708` | `2860ab3b0137c68e58fe1195a4c71a82a60ce183`; full P0–P3 original Kaggle output, 17 members, 16 manifested |

Additional pre-existing historical ZIPs (full-protocol backend variants, independent quantum-validation variants and final validation) are retained untouched in this folder. The original notebook sources and independent per-experiment audits remain available through the [historical Git branch](../../tree/archive/pre-modularization-2026-11-14) or [GitHub archive branch](https://github.com/shanmukhdatta/QSV2G/tree/archive/pre-modularization-2026-11-14).

## Validate the archive bytes

```bash
python scripts/verify_archived_evidence.py
```

This script checks exact SHA-256 hashes, ZIP CRCs, and the internal file-level SHA-256 and size manifest entries for the two full-run archives. It does **not** claim that a ZIP manifest independently authenticates the Kaggle account, job URL, code identity or scientific security of a protocol.

## What to cite

See [`docs/PAPER_EVIDENCE_MAP.md`](../../docs/PAPER_EVIDENCE_MAP.md) for scope-specific descriptions of evidence suitable for the methods, experimental evaluation and security analysis. Do not report historical timing values as measurements of the newer modular software version. For Stage 06, the Tamarin lemma `bypass_possible_with_full_compromise` establishes the **existence of an accepted trace under the modeled compromise**, not a protective security theorem.
