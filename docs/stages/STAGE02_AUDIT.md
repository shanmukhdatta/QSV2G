# QSV2G — Stage 02 Security Analysis: Uploaded Result Audit

**Review date:** 2026-10-26  
**Uploaded archive:** `qsv2g_stage02_security_results.zip`  
**Archive SHA-256:** `be4f42ff39a999e246a54e7e68c75ec16992a1d83dcdcc690e03ac195c2fd7af`  
**Scope:** Evidence review of the provided ZIP; not an independent cloud-runtime attestation or cryptographic security proof.

## 1. Artifact integrity

- ZIP opens successfully and ZIP integrity test reports no corrupt member.
- Seven entries total: 6 files covered by `artifact_manifest.json` plus the manifest itself.
- Every listed member matches the manifest's exact byte size and SHA-256 digest (6/6).
- No executed `.ipynb` or original Kaggle revision URL/run ID is included in the ZIP.
- The submitted environment describes Python 3.13.15 on Linux, native `pqcrypto` 1.0.0 using ML-KEM-768 / ML-DSA-65, NumPy 2.1.3, pandas 2.3.3, and cryptography 50.0.1. Kaggle is reported as a run-location hint; the run ID is marked `NOT_CAPTURED_AUTOMATICALLY`.
- Recorded reference-implementation SHA-256: `2c86ca9eecbc5925100722119f061e640df03f993e14909b3078b23406330758`. It matches the implementation packaged in the earlier repository preview.
- Recorded Section IV LaTeX SHA-256: `4ca43b1f6debd2e2bf314ff9adf74f0ad08ba1702e1055eca1943b9533290ef2`. It matches the earlier revised Section IV source, *not necessarily* the latest figure-enhanced manuscript.

## 2. Case-level checks

| Evidence | Count |
|---|---:|
| Unique case IDs | 80 |
| Expectations matched | 80 |
| Mismatches | 0 |
| Group A: authentication / availability / initial controls | 26 |
| Group B: context binding / AEAD / replay | 20 |
| Group C: QSS consistency / quantum state properties | 23 |
| Group D: signatures / authorization / execution | 11 |
| Cases recording `REJECTED` | 56 |
| Cases recording `ACCEPTED` | 11 |
| Cases recording `EXPOSED` | 7 |
| Other categories: DISTINCT (2), IDEAL_PRIVACY (1), CONSUMED (1), WITHIN_LIMIT (1), INTERRUPTED (1) | 6 |

The 80 expected/observed outcomes also match the independently saved local Stage 02 run. Only the random secret printed in the C20 dishonest-dealer detail differs across the compared runs; this is expected when a random secret is sampled. The submitted archive's environment and manifest legitimately differ from the local run.

### Seven explicit limitation demonstrations

| Case | Boundary shown | Correct interpretation |
|---|---|---|
| B19 | Reusing the same AES-GCM traffic key after nonce-counter reset causes repeated nonces | Crash persistence / rekeying design is missing |
| B20 | An internal mutation of the shared simulator's EV/CS context exposes inadequate independent state tracking | An internal trust-boundary test, not a remote network exploit |
| C20 | Dishonest dealer can change both the encoded secret and its matching commitment | The checks do **not** establish malicious-secure VQSS |
| C21 | Stabilizer checks accept different valid codewords and cannot identify intended logical value | Code-space membership is not semantic/logical authorization |
| C22 | Unsalted L=1 low-entropy commitment can be enumerated | Parameterization warning, not evidence of an attack on default L=162 |
| D02 | Two authorized colluding signers can sign without performing QSS reconstruction | Exceeds a `<=1` corrupt authority threat assumption; signatures attest, do not prove reconstruction |
| D11 | Corrupting shared station protocol state can bypass independently unrecorded EV operation intent | Simulator design gap, not an established network vulnerability |

## 3. Security/privacy requirement coverage

The supplied `security_requirements_matrix.csv` labels all 13 stated requirements as follows:

- **Eight `PARTIALLY_TESTED`:** SPR1, SPR2, SPR5, SPR6, SPR8, SPR9, SPR11, SPR13.
- **Three `LIMITATION_DEMONSTRATED`:** SPR3, SPR4, SPR10.
- **Two `NOT_ESTABLISHED`:** SPR7 (EV identity privacy) and SPR12 (controlled accountability).

These are **research-scoping judgments from the notebook**, not automatically proven security properties. The requirement matrix in the notebook is predefined; successful execution establishes that the recorded cases ran and matched expected outputs, not that all requirements have been formally verified.

## 4. What can be used in Section V

The archive supports a **simulation-based security and fault-injection evaluation** discussing rejection of specific invalid credentials, transaction-binding and AEAD modifications, invalid signatures, replay conditions, and QSS commitment changes. It also supports the *documented counterexamples and availability qualifications* above.

Do not conclude: `(i)` 80/80 security guarantees, `(ii)` full malicious-secure VQSS, `(iii)` unconditional anonymity from I/3 single-share marginals, `(iv)` end-to-end availability of arbitrary two out of three authorities, `(v)` EV-observable proof that quantum reconstruction occurred, or `(vi)` real physical V2G enforcement.

## 5. Research conclusion and next steps

**Stage 02 result: PASS_WITH_DOCUMENTED_LIMITATIONS**, with the qualification that this is a structured result-archive audit. Enough evidence is available to begin writing the attack-test subsection of Section V and to scope the remaining theoretical limitations. A complete formal security proof and the privacy/accountability properties remain unestablished and must be transparently described.

**Proceed to Stage 03** on realistic, clearly specified *simulated* quantum noise: retain existing qutrit-X results; add correctly implemented qutrit phase/dephasing, depolarizing and loss/erasure models; distinguish quantum fidelity from computational-basis classical reconstruction correctness; include uncertainty intervals and randomized seeds. Stage 04 subsequently adds within-environment performance baselines and scalability.

## 6. Reference evidence filenames

- `security_summary.json`
- `security_attack_results.csv`
- `security_limitations.csv`
- `security_requirements_matrix.csv`
- `security_report.md`
- `environment.json`
- `artifact_manifest.json`

Original ZIP and original CSV rows are preserved unchanged. No new results have been generated by this audit.
