# QSV2G — Stage 01 Baseline Reproducibility Audit

Audit date: 2026-10-26 (based on uploaded record and analysis).

## Examined evidence

- User-uploaded results: `qsv2g_stage01_baseline_results.zip`
- ZIP size: 10247 bytes
- ZIP SHA-256: `1f6ae90f215ae5f74518d4b007a6cca469e8dbdde0ea1ac8d82956d2aaddf202`
- Complete ZIP checksum check: PASS; 16 ZIP entries; all 15 manifest entries match stored byte lengths and SHA-256 digests.
- Reported run interval: `2026-10-26T17:27:31.487307+00:00` to `2026-10-26T17:27:34.458133+00:00`.
- Reported environment flag: `kaggle_path_detected` (path indicator, **not** independent verification of a Kaggle run/revision).
- Reported Python: 3.13.15, Linux; NumPy 2.1.3; pqcrypto 1.0.0, cryptography 50.0.1.
- Cryptographic backend: native `pqcrypto` ML-KEM-768 + ML-DSA-65.

## Findings

| Check | Verified observation |
|---|---|
| Overall suite status | PASS in summary, and supporting CSVs consistent |
| Functional cases | 31 cases with expected results |
| Deliberate limitation cases | 4 cases matched known limitations (not security guarantees) |
| Availability boundary cases | 3 cases reproduced (UC-A offline rejects; UC-B offline rejects; UC-C offline accepts) |
| All case outcomes | 38/38 matched expected outcomes |
| Earlier archive comparison | 38/38 cases matched archived expected/observed/type categories |
| Ideal three-qutrit QSS | 720/720 correct (240 AB, 240 AC, 240 BC) |
| CHARGE/DISCHARGE | 6/6 accepted and terminated, all three pairs for each operation |
| Equation-to-code label checks | 22 labels and code symbols found; **19 implemented, 3 classified partial** |
| Artifact manifest | 15/15 hashes and sizes match |

Earlier-submitted `qsv2g_final_validation_results.zip` is SHA-256 `f05cbc3eb70e3425438a22cae25d292ce3ce78787052c1b8e1e7d375d3462030` and matches the reference archive hash in `source_hashes.json`.
The validation case CSV, ideal QSS CSV and equation-to-code mapping CSV are byte-identical to the archived outputs, consistent with deterministic output for those components.

## Source/version binding

- Implementation SHA-256: `2c86ca9eecbc5925100722119f061e640df03f993e14909b30758`.
- Tested Section IV LaTeX SHA-256: `4ca43b1f6debd2e2bf314ff9adf74f0ad08ba1702e1055eca1943b9533290ef2`.
- These identify an **earlier Section IV revision**. Correspondence with the latest figure-enhanced manuscript/Overleaf is not proven by this notebook.

## Three *partial* mapping entries

- `eq:qss_state_consistency`: `qss_consistency` — ideal stabilizer checks do not establish malicious-verifiable QSS.
- `eq:qsv2g_authority_decision`: `QSV2G.authority_verify` — simple authority policies and revocation flags, not deployed policy infrastructure.
- `eq:qsv2g_execution_states`: `QSV2G.execute` — in-memory execution state, no crash-persistent ledger.

## Reproduced known limitations

1. A malicious dealer substituting both a valid code state and matching commitment is accepted.
2. Stabilizer checks do not distinguish encoded logical values.
3. Two colluding authenticated signers can produce a token accepted by endpoints without proving quantum reconstruction (two corrupt signers exceeds a one-authority-compromise assumption).
4. Reinstantiating AEAD traffic using the same key can repeat the nonce when the counter resets.

## Other implementation boundaries

Trusted inter-authority channels are modeled in-process. Quantum network noise, quantum memories and detectors are not physically implemented. EV does not independently verify the quantum reconstruction. UC-A and UC-B remain required online in the current full protocol, despite 2-of-3 QSS reconstruction. The energy-execution trace reports `10000.002 mWh`; its nominal energy-limit enforcement and numerical tolerance require review rather than treating the value as automatically compliant.

## Interpretation

**Stage 01: PASS within the reproducibility checks exercised.** Do not treat this as a formal cryptographic security proof or as verification that all lines of the latest manuscript were implemented. No statistically independent security confidence is inferred from a PASS count. Original Kaggle run URL, full cloud log and executed notebook were not supplied with this ZIP.

## Next stage

Proceed to Notebook 02 — Security Analysis: test SPR1–SPR13, including context tampering, replay, authority-role compromise, QSS deviations, crash/restart and transaction lifecycle. Preserve successful, failed and limitation demonstrations separately. Export a scenario-to-security-requirement evidence matrix suitable for Section V.
