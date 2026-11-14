"""Verify original research ZIP identity, CRC, and full-run internal manifests.

Run at repository root: python scripts/verify_archived_evidence.py
No dependencies beyond the Python standard library. This is integrity/provenance
validation, not verification of a physical experiment or cryptographic proof.
"""
from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "results" / "manifests" / "kaggle_archive_sha256.json"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check_full_software_archive(zf: zipfile.ZipFile) -> int:
    name = "20261113T092554Z/artifact_manifest.json"
    metadata = json.loads(zf.read(name))
    root = name.rsplit("/", 1)[0] + "/"
    files = metadata["files"]
    if len(files) != 31:
        raise ValueError("Unexpected full software archive manifest length")
    for record in files:
        logical = record["path"]
        if logical.startswith("/") or ".." in Path(logical).parts:
            raise ValueError(f"Unsafe entry path in manifest: {logical!r}")
        payload = zf.read(root + logical)
        if digest(payload) != record["sha256"] or len(payload) != record["bytes"]:
            raise ValueError(f"Full software archive member mismatch: {logical}")
    return len(files)


def check_adversarial_archive(zf: zipfile.ZipFile) -> int:
    records = json.loads(zf.read("file_hashes.json"))
    if len(records) != 16:
        raise ValueError("Unexpected adversarial archive manifest length")
    for name, expected in records.items():
        if name.startswith("/") or ".." in Path(name).parts:
            raise ValueError(f"Unsafe entry path in manifest: {name!r}")
        if digest(zf.read(name)) != expected:
            raise ValueError(f"Adversarial archive member mismatch: {name}")
    return len(records)


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    summaries = []
    for entry in manifest["archives"]:
        name = entry["path"]
        file = ROOT / name
        if not file.is_file():
            raise FileNotFoundError(f"Missing original results ZIP: {name}")
        actual = digest(file.read_bytes())
        if actual != entry["sha256"]:
            raise ValueError(f"SHA-256 mismatch: {name} expected {entry['sha256']} got {actual}")
        with zipfile.ZipFile(file) as zf:
            corrupted = zf.testzip()
            if corrupted:
                raise ValueError(f"ZIP CRC failure in {name}: {corrupted}")
            if len(zf.infolist()) < 1:
                raise ValueError(f"Empty ZIP: {name}")
            internal = 0
            if entry["study"] == "full_software_and_formal":
                internal = check_full_software_archive(zf)
                if len(zf.infolist()) != entry["members"]:
                    raise ValueError("Unexpected full software ZIP member count")
            elif entry["study"] == "adversarial_reliability_formal":
                internal = check_adversarial_archive(zf)
                if len(zf.infolist()) != entry["members"]:
                    raise ValueError("Unexpected adversarial ZIP member count")
        summaries.append((name, internal))
        print(f"PASS {name} [SHA-256, CRC, {internal} full-run member hashes]")
    print(f"PASS: {len(summaries)} original experimental archives verified")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (FileNotFoundError, KeyError, ValueError, zipfile.BadZipFile) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        sys.exit(1)
