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
