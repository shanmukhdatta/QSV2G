# QSV2G independent stage audits

| Stage | Evaluation | Review | Raw evidence |
|---|---|---|---|
| 01 | Baseline reproducibility | [Stage 01 audit](STAGE01_AUDIT.md) | [`results/stage01/`](../../results/stage01/) |
| 02 | Security attack/fault evaluation | [Stage 02 audit](STAGE02_AUDIT.md) | [`results/stage02/`](../../results/stage02/) |
| 03 | Quantum noise and QSS reliability | [Stage 03 audit](STAGE03_AUDIT.md) | [`results/stage03/`](../../results/stage03/) |
| 04 | Computational performance and authorization microbenchmarks | [Stage 04 audit](STAGE04_AUDIT.md) | [`results/stage04/`](../../results/stage04/) |

Audits are **inspection of user-supplied result archives**, not independent verification of the Kaggle execution identity or formal security proof. Each `*.zip` is stored unchanged; extracted files provide convenience for faculty review. All reported cryptographic and quantum claims are limited to the specified software test environment and assumptions.

Stages 03 and 04 were reviewed from user-submitted ZIP outputs. Their saved notebook-generated logs are preserved, but immutable Kaggle run URLs, original complete cloud job logs and saved cloud-executed notebook revisions were not supplied.
