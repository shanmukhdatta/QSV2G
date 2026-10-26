# Verification scripts

Run `python scripts/verify_artifacts.py` from the repository root to check SHA-256-linked reference implementation, attached LaTeX revision, ZIP integrity, summary counts and extracted-file equivalence. This is an **artifact consistency check**, not a fresh notebook rerun or security proof.
## Stage 01 / 02 verifier

Run `python scripts/verify_stage01_stage02.py` from the repository root for ZIP checksum, member integrity, raw-extract byte matching, and test-count consistency. It does not run the cryptographic protocol or verify Kaggle identity.
