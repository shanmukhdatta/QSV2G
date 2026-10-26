# Stage 01 / 02 execution evidence map

This index links **which notebook**, **which original archive**, **which individual evidence file**, and **which review** support every quantitative claim.

| Experiment | Source notebook | Submitted ZIP | Raw evidence | Audit |
|---|---|---|---|---|
| Baseline 38/38, QSS 720/720, workflows 6/6 | [Stage 01](../notebooks/stage01/) | [unchanged Stage 01 ZIP](../results/stage01/submitted/qsv2g_stage01_baseline_results.zip) | [Stage 01 extracted](../results/stage01/submitted/extracted/) | [Audit 01](stages/STAGE01_AUDIT.md) |
| Security 80/80 expected observations, 7 exposed limitations | [Stage 02 fixed](../notebooks/stage02/) | [unchanged Stage 02 ZIP](../results/stage02/submitted/qsv2g_stage02_security_results.zip) | [Stage 02 extracted](../results/stage02/submitted/extracted/) | [Audit 02](stages/STAGE02_AUDIT.md) |

**Scientific interpretation:** 80/80 and 38/38 refer to predefined expected outcomes, including intentionally failing security behaviors. They are not rates of successful defense or a formal assurance result. The QSS 720/720 trials are under ideal simulation assumptions.

**Source revision:** both uploaded archives refer to implementation SHA-256 `2c86ca9eecbc5925100722119f061e640df03f993e14909b3078b23406330758` and Section IV revision SHA-256 `4ca43b1f6debd2e2bf314ff9adf74f0ad08ba1702e1055eca1943b9533290ef2`. The current figure-enhanced manuscript may differ and requires a line-level reconciliation before citing complete equivalence.

**Environment provenance:** Stage 01 and Stage 02 submitted ZIPs report Python 3.13.15 and native pqcrypto. Their working-directory indicators do **not** replace the missing Kaggle run URL, version ID, or full original cloud console log.

**Local preflight artifacts** are separately retained for reference and should not be conflated with uploaded Kaggle outputs or aggregated into performance numbers.

**Remaining evidence to request:** exact Kaggle notebook run URLs/revisions, exported original full console logs, and preferably the actual Kaggle-executed notebook snapshots for Stages 01 and 02. Until those are provided, mark provenance as `user-submitted structured output; Kaggle identity not independently authenticated`.

**No new experiment was executed to produce these documents:** all above counts are from uploaded original archives and independent consistency checks.

## Stages 03 and 04

| Experiment | Notebook | Original submitted ZIP | Raw CSVs and logs | Audit |
|---|---|---|---|---|
| Stage 03: five noise models; 315 configurations; 315,000 simulated trials | [Notebook](../notebooks/stage03/) | [Stage 03 ZIP](../results/stage03/submitted/qsv2g_stage03_quantum_noise_results.zip) | [Raw evidence](../results/stage03/submitted/extracted/), [log](../logs/stage03/) | [Audit](stages/STAGE03_AUDIT.md) |
| Stage 04: 120 workflows; 120 scaling runs; 270 authorization microbenchmarks | [Notebook](../notebooks/stage04/) | [Stage 04 ZIP](../results/stage04/submitted/qsv2g_stage04_performance_results.zip) | [Raw evidence](../results/stage04/submitted/extracted/), [log](../logs/stage04/) | [Audit](stages/STAGE04_AUDIT.md) |

Original SHA-256 digests: Stage 03 `b76f05afca3d872ce3bc7b4ea043ec7e10ef3d555e042cdadc0eda8e5f0b0d95`; Stage 04 `9a60827099be191398931b8ddf036c5664b4f19410c0761de54031ad869f11e0`. Both use reference core `2c86ca9eecbc5925100722119f061e640df03f993e14909b3078b23406330758` and revised Section IV `4ca43b1f6debd2e2bf314ff9adf74f0ad08ba1702e1055eca1943b9533290ef2`, not necessarily the latest edited manuscript.

These are user-submitted ZIPs and internal logs, not independently authenticated cloud runs; immutable Kaggle URLs, full execution histories and saved cloud-executed notebooks are absent. Stage 03 covers specified noise on one selected share, not noisy V2G execution. Stage 04 B0/B1/B2 are authorization microbenchmarks, not full security-equivalent alternative systems.
