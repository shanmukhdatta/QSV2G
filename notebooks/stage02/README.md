# Stage 02 — Security Analysis

- Run **[QSV2G_Stage02_Security_Analysis_Kaggle_Fixed.ipynb](QSV2G_Stage02_Security_Analysis_Kaggle_Fixed.ipynb)** in Kaggle (CPU; turn Internet on for `pqcrypto` installation). This supersedes the earlier draft, which failed if neither supported real cryptographic backend was installed.
- The separately preserved [local preflight execution](local_preflight/QSV2G_Stage02_Fixed_Local_Executed.ipynb) ran with OpenSSL 3.5+. Do not label it as the Kaggle executed notebook.
- Uploaded results, unchanged ZIP and extracted CSV/JSON: [results/stage02/submitted](../../results/stage02/submitted/).
- [Independent audit](../../docs/stages/STAGE02_AUDIT.md) and [local stdout extract](../../logs/stage02/local_preflight_stdout.txt).
- Submitted summary: **80/80 scripted outcomes matched expectations**; 7 deliberate limitation demonstrations; 13 SPR requirements mapped (8 partially tested, 3 limitations demonstrated, 2 not established).
- A matching expected vulnerability is **not** a successful security defense. SPR7 and SPR12 are not established by these tests.
- Reference code and Section IV hashes match Stage 01's earlier tested source revision, not automatically the newest Overleaf manuscript.
- Original Kaggle run URL/revision ID and original cloud console log **were not provided**. The uploaded ZIP names a Kaggle working-directory hint.
