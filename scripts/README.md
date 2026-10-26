# Verification scripts

Run `python scripts/verify_artifacts.py` from the repository root to check SHA-256-linked reference implementation, attached LaTeX revision, ZIP integrity, summary counts and extracted-file equivalence. This is an **artifact consistency check**, not a fresh notebook rerun or security proof.
## Stage 01 / 02 verifier

Run `python scripts/verify_stage01_stage02.py` from the repository root for ZIP checksum, member integrity, raw-extract byte matching, and test-count consistency. It does not run the cryptographic protocol or verify Kaggle identity.

## Stage 03 / 04 verification

Run `python scripts/verify_stage03_stage04.py` from repository root. It checks 19/19 Stage 03 and 27/27 Stage 04 internal SHA-256 members, all extracted-file/log byte matches, and 315,000 / 120+120+270 raw record counts. Standard library only. This is artifact verification, not a cloud-execution attestation or cryptographic security proof.
