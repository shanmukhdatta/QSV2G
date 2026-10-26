# Stage 04 — Performance and Baseline Evaluation

The [original user-submitted archive](submitted/qsv2g_stage04_performance_results.zip) is stored unchanged, SHA-256 `9a60827099be191398931b8ddf036c5664b4f19410c0761de54031ad869f11e0`.
Its exact contents are exposed under [submitted/extracted/](submitted/extracted/) for inspection and direct CSV/JSON access. The ZIP's internal manifest is preserved and checked by [`scripts/verify_stage03_stage04.py`](../../scripts/verify_stage03_stage04.py).

- [Run notebook](../../notebooks/stage04/) — original Kaggle-ready `.ipynb` source; not a saved executed Kaggle revision.
- [Separate local preflight archive](local_preflight/QSV2G_Stage04_Short_Local_Preflight_Results.zip) — **different local execution**; not interchangeable with user-submitted results.
- [Saved notebook-produced log](../../logs/stage04/submitted_notebook_log.txt) — taken from the original ZIP, not an authenticated complete Kaggle console log.
- [Audit](../../docs/stages/STAGE04_AUDIT.md) — technical consistency checks and limitations.
- [Plots](../../figures/experimental/stage04/original/) — byte-for-byte copies of the original PNGs, not redrawn figures.

**Evidence scope:** 120 full software-workflow samples, 120 QSS scaling samples, 270 post-context authorization microbenchmarks. B0/B1 are constructed microbenchmarks, not complete alternative V2G protocols.

**Provenance:** The archive is user-submitted and reports a Kaggle path/environment; the immutable Kaggle notebook revision and original full cloud console transcript were not supplied. Do not claim independent authentication of the Kaggle run.
