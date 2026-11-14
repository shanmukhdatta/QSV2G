# QSV2G manuscript-to-experiment evidence map

**Paper:** *QSV2G: Pseudonymous Cross-Domain Authentication and Quantum Secret Sharing-Based Authorization for Vehicle-to-Grid Networks*. The authorship and manuscript framing come from the existing `micro.tex` source; this document does not certify parity between the final manuscript and every historical implementation revision.

This map is organized by **scientific claim**, not the chronological development order. Preserve complete negative and positive observations. The historical zip filenames retain their original identifiers for unambiguous traceability.

## Methods / protocol implementation

| Described mechanism | Executable reference | Evidence boundary |
|---|---|---|
| HMAC-protected registration, pseudonyms and mutual authentication | `src/qsv2g/protocol.py`, `src/qsv2g/crypto.py` | Simulated parties share one process; HMAC and AES-GCM software is genuine |
| ML-KEM-768 session and ML-DSA-65 signed authorization | `src/qsv2g/crypto.py`, `src/qsv2g/protocol.py` | Requires genuine supported post-quantum software backend |
| Ideal three-qutrit 2-of-3 reconstruction, AB/AC/BC | `src/qsv2g/quantum.py`, `src/qsv2g/resources.py` | Quantum computations are numerical simulations, not physical channels |
| Transaction-bound EV intent and two-signature token verification | `src/qsv2g/protocol.py`, `docs/threat_model.md` | Signatures authenticate reconstruction attestations, not an independent physical reconstruction proof |

## Experimental evaluation: evidence available for main paper

| Scientific claim | Original archive | Exact primary internal output | Mandatory scope statement |
|---|---|---|---|
| Ideal threshold correctness across AB/AC/BC | `results/archives/ideal_validation_historical.zip` | `validation/qss_pair_ideal.csv`, `validation/validation_case_results.csv` | 720/720 recovery assumes ideal qutrit simulation; 38/38 expected outcomes include explicit known limitations |
| Controlled security/fault injection | `results/archives/security_scenarios_historical.zip` | `security_attack_results.csv`, `security_limitations.csv`, `security_requirements_matrix.csv` | 80 observations match predefined expectations; 7 expose limitations; not a proof of all security requirements |
| Single-trit reconstruction under five channels | `results/archives/quantum_noise_historical.zip` | `noise_trial_aggregates.csv`, `noise_trial_events.csv.gz`, `quantum_fidelity_codespace.csv` | 315,000 modeled, sampled trials; channels act on selected local share; classical recovery differs from state fidelity |
| Workflow time and QSS scaling | `results/archives/performance_historical.zip` | `end_to_end_raw.csv`, `qss_resource_scaling_raw.csv`, `authorization_baselines_raw.csv`, `instrumented_aead_packets_raw.csv` | 120 workflows, 120 QSS scaling runs, 270 microbenchmarks; packet subset and physical network costs are excluded |
| Matched post-quantum baselines and end-to-end software | `results/archives/qsv2g_stage05_final_20261113T092554Z.zip` | `20261113T092554Z/e1/e1_trials.csv`, `e1/e1_summary.csv`, `analysis_summary.json` | 18,000 successfully completed software transactions; QUORUM is not functionality-equivalent to QSS |
| Endpoint tamper and invalid-context tests | Same full software ZIP | `20261113T092554Z/e2/e2_cases.csv`, `e2/hypothesis.json` | 36 scripted cases; stateful Hypothesis uses a labeled test-only crypto surrogate |
| Full-vector noise and genuine-PQC endpoint check | Same full software ZIP | `20261113T092554Z/e3/e3_vector_trials.csv`, `e3/e3_token_trials.csv`, `e3/e3_summary_with_ci.csv` | 300,000 modeled full-vector attempts, 6,000 real-PQC token attempts; these are different tiers/denominators |
| Fail-safe authority/state behavior | Same full software ZIP | `20261113T092554Z/e4/e4_failure_matrix.csv` | 11 expected software scenarios; no distributed crash-safe recovery or hardware metering |
| Retry availability and qutrit accounting | `results/archives/qsv2g_stage06_full_20261113T111031Z_results.zip` | `p2/p2_retries.csv`, `p2/p2_manifest.json` | 400 modeled settings × 2,500 Monte Carlo repeats; independent retries **not implemented** in the protocol state machine |

## Security analysis: honest properties and counterexamples

| Property / scenario | Original evidence | Correct interpretation |
|---|---|---|
| One-signer forgery, replay and context manipulation rejected in tested cases | Earlier `security_scenarios_historical.zip`; full Stage 05 `e2/e2_cases.csv`; final adversarial ZIP `p0_p1/p0_p1_attack_matrix.csv` | Conditional software evidence for listed adversary actions, not universal resistance |
| Dealer share modified while commitment is unchanged | Final adversarial ZIP `p0_p1/p0_p1_attack_matrix.csv` | Tested alteration is rejected, but a dishonest dealer replacing secret **and** commitment remains a limitation |
| Two selected signing keys and privileged CS control | Final adversarial ZIP `p0_p1/p0_p1_attack_matrix.csv`, `p0_p1/p0_p1_summary.json` | EV acceptance without actual reconstruction can be constructed under *both* compromise capabilities; not remote-only exploit |
| QSS versus classical 2-of-3 interface | Final adversarial ZIP `p0_p1/p1_exact_distributions.csv` | Nine exact computational-basis distributions match numerically; no distinct QSS advantage established by tested interface |
| Symbolic consent and two-authority rules | Full Stage 05 ZIP `e5/e5_proof_log.txt`, `e5/e5_status.json`; `docs/formal/classical_consent.spthy` | Four listed lemmas verified in an **abstract classical A/B model assuming ideal QSS** |
| Compromise-aware symbolic analysis | Final Stage 06 ZIP `p3/p3_proof.log`, `p3/p3_status.json`; `docs/formal/compromise_analysis.spthy` | Three listed lemmas verified in restricted abstract model. One lemma explicitly shows **bypass possible under full compromise**. No full implementation-refinement proof |

## Evidence integrity and versioning

- The six principal ZIP SHA-256 values are in [`results/manifests/kaggle_archive_sha256.json`](../results/manifests/kaggle_archive_sha256.json). Check with `python scripts/verify_archived_evidence.py`.
- The full software ZIP embeds source revision `b463fc758fa28f1853fe06c4130ee2f25173ac0c`. The subsequent attacker/retry ZIP embeds `2860ab3b0137c68e58fe1195a4c71a82a60ce183`.
- The first four ZIPs were produced with an **older** reference implementation; the active modular code is a behavior-preserving refactor of the **later** implementation. Numerical results should be attributed to the matching source version.
- The original Kaggle run URLs and immutable executed notebook revision links are not included for every archive. The archived manifests and SHA hashes support artifact integrity, **not** independently authenticated cloud-run provenance.
- Figures and tables must disclose whether they show single-trit outcomes, full-vector gate eligibility, endpoint acceptance, software-only latency or analytic quantum-resource counts. The denominators differ.
- No physical V2G system, physical quantum communication link, formal malicious-secure VQSS or experimentally established advantage over classical threshold sharing is claimed.
