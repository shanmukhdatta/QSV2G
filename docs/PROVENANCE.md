# Artifact provenance and validation mapping

The files under `results/archives/` are byte-for-byte copies of available supplied ZIPs. Their environment information is **reported by the archive**; a saved manifest alone does not authenticate where it was executed. Retain the source ZIP if exact provenance must be established.

| Archive | Internal environment/evidence | Notes |
|---|---|---|
| `full_protocol_openssl_reported.zip` | Python 3.13.5, Linux, OpenSSL 3.5+ ML-KEM/ML-DSA backend | Native/OpenSSL result set; different wall-clock timing |
| `full_protocol_pqcrypto_reported.zip` | Python 3.13.15, Linux, native `pqcrypto` backend | Distinct execution environment; do not average with OpenSSL |
| `quantum_validation_variant_A.zip` | 500 shots per symbol / pair, ideal model | Variant A plot differs from variant B; same tabular quantum checks |
| `quantum_validation_variant_B.zip` | 500 shots per symbol / pair, ideal model | Variant B plot differs from variant A; no environment field |
| `final_validation_submitted.zip` | Python 3.13.15, native `pqcrypto`, 38 matches, 720 ideal recoveries | Submitted final validation; no signed Kaggle execution metadata |

Key identifiers:

- `src/qsv2g_core.py` SHA-256: `2c86ca9eecbc5925100722119f061e640df03f993e14909b3078b23406330758`.
- `protocol/QSV2G_main8_SectionIV_Revised.tex` SHA-256: `4ca43b1f6debd2e2bf314ff9adf74f0ad08ba1702e1055eca1943b9533290ef2`.
- The `full_protocol` and `final_validation` archive manifests refer to the above protocol source digest; the final suite additionally references the implementation digest.
- These digests identify the **earlier revised Section IV source**, not automatically the latest manually edited figure-enhanced PDF/Overleaf revision.
- `protocol/historical/` is retained for history, **not** the normative current implementation specification.

Available logs: notebook-embedded local text output plus structured result CSVs. Original complete Kaggle cell logs, raw download metadata, immutable environment lockfiles, and original source-control run commit IDs were **not present** in the provided artifacts. Do not label these files as available.

This archive is a reproducibility aid. Equation mapping is curated traceability, not mathematical/formal proof.
