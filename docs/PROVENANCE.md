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

Available execution evidence:
- A **user-supplied quantum-validation Kaggle console extract** is preserved unchanged at `logs/kaggle/quantum_validation_download.txt` (SHA-256: `a06066f13c7f4bc4a41fbc7388ff31085147920f8b88eedfe52152f6f79602b3`). It reports successful QSS state tests, Qiskit and PennyLane checks, and output archive creation at `/kaggle/working/qsv2g_quantum_results.zip`.
- Notebook-embedded **local** execution output is separately available under `logs/local_executed/`; structured CSV results remain under `results/`.
- Original Kaggle URLs, immutable revision identifiers, full run history for the three notebook families, raw download metadata, and complete environment lockfiles were **not supplied**. The console extract supports reported execution details, but cannot by itself authenticate the run's origin or associate it with an immutable Kaggle revision.

This archive is a reproducibility aid. Equation mapping is curated traceability, not mathematical/formal proof.
