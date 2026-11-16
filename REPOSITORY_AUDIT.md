# QSV2G repository verification — 16 November 2026

## Outcome and scope

The repository now provides a tested route from preserved raw observations to the paper's principal plots, and from the maintained implementation to fresh experiments. This is reproducibility engineering and bounded scientific verification, not certification of protocol security or conference acceptance. The approved seven-page manuscript and its structure were preserved. Its evidence-availability wording needs the corrections in [PAPER_EVIDENCE_NOTES.md](PAPER_EVIDENCE_NOTES.md).

Base revision: `642e9b0cfa6fe792c3d7368300411ff253f1c3e7`. Published code revision: `4ea9854bd4e4ee4b0d79a6361400d6aa684e63de`, tree `d29f3077bd9c13e61169377933c77ad06fa16e32`. Changes are on [PR 1](https://github.com/shanmukhdatta/QSV2G/pull/1); main was not merged. Execution manifests retain their actual revision, dirty state and individual source hashes. Early experiments started before the code commit; their metadata was not rewritten to pretend otherwise. Later documentation changes do not alter experiment code.

## Corrections applied

- Forwarded the requested seed to validation; documented the separate OS-random cryptographic and Hypothesis randomness scopes.
- Added exclusive output-directory creation, timestamp defaults, failed-run records, actual dependency versions, commands, source hashes and output hashes. A concurrent-output race found in independent review was reproduced, fixed with atomic directory creation, and regression-tested.
- Fixed aggregation of named study output directories; empty unsupported input now fails instead of returning a misleading empty success.
- Included the compatibility import module in built wheels and verified installation outside the checkout.
- Added archive-backed raw-data verification and reproducible PDF/SVG plotting, pinned tested dependencies, nine-study smoke CI, and clear implementation/protocol maps.
- Kept all 28 original core classes/functions AST-identical. No protocol operation or historical result was changed.

## Verification evidence

| Check | Result | Meaning / boundary |
|---|---|---|
| Regression tests | 147 passed (baseline 138) | Local run has one third-party pytest deprecation warning; no test failures. |
| Hosted CI | Code revision passed all steps | [Run 43795793978](https://github.com/shanmukhdatta/QSV2G/actions/runs/43795793978): 147 tests, nine smoke studies, parity, archives and raw reaggregation. |
| Core migration parity | 28/28 exact AST bodies | Preservation, not proof of correctness. |
| Original archives | 6/6 SHA-256 and CRC checks pass | Stage05: 31 internal hashes; Stage06: 16. Checksums do not authenticate cloud account/job identity. |
| Wheel | Built, installed and imported outside checkout | Includes qsv2g_core compatibility module and evaluation code. |
| Historical noise | 315,000 events, 315 configurations checked | Five channels; erasures treated as failures. |
| Original Stage03 replay | All 10 code cells executed | Only output locations relocated; 315,000 decompressed CSV event rows byte-identical to the archive. |
| Historical timing | 18,000 trials, 12 conditions, five blocks | All twelve rounded inclusive medians reproduced directly from raw records. |
| Historical full-vector / endpoint | 300,000 / 6,000 rows checked | Counts agree with archived summary; distinct from single-trit cohort. |
| Formal consent | 4 lemmas freshly verified | Restricted symbolic model, ideal reconstruction gate. |
| Formal compromise | 3 lemmas freshly verified | Includes attack-existence lemma, not seven resistance claims. |

The Stage03 decompressed CSV SHA-256 is `fe0f390dcafdd3623dd4ff422be6ed9c0aa8f493feb74e81670882e992589f72` for both original and fresh replay. Code-cell replay is not a claim that the source notebook was saved with execution counters. The results bundle contains the replay, source identity, logs and comparison.

Historical p=.30 single-trit probabilities are 70.07%, 100.00%, 80.28%, 70.38%, 59.01% in the archived channel order. Historical vector outcomes are 191,736 eligible, 81,400 commitment rejection and 26,864 erasure abort; endpoint outcomes are 3,854 accepted, 1,606 commitment rejection and 540 erasure abort. These are separate cohorts and must not be summed as independent security tests.

## Fresh maintained-code studies

All nine smoke commands and all nine full-budget commands completed successfully. All 18 execution records and their 66 recorded output hashes were verified. Full-study outcomes and checked manifest hashes are recorded in `results/reviewer_audit_2026_11_16/full_verification.json`. The complete new raw records are delivered separately in the dated reproducibility-results ZIP rather than enlarging the repository with duplicated generated data.

| Study | Full budget | Scope |
|---|---|---|
| validation | 720 ideal recoveries; six complete workflows | 720/720 and 6/6; CHARGE and DISCHARGE checks. |
| performance | 18,000 transactions, five blocks | Genuine PQC; CHARGE workload; new host timings. |
| security | 36 fixed cases | Expected outcomes, not 36 universally prevented attacks. |
| noise | 300,000 vector and 6,000 endpoint trials | Five channels, four lengths; genuine-PQC endpoints. |
| availability | 11 cases | Process-local state and availability behavior. |
| noise-vector | 4,000 trials | Bounded X-only study; not a substitute for all channels. |
| security-stateful | 1,000 examples, up to 50 steps | Explicit test-only crypto substitute. |
| security-adversarial | 96 controls and nine exact distributions | Zero unexpected control outcomes; preserves known privileged bypasses. |
| reliability | 400 configurations × 2,500 repetitions | Independent-attempt retry model, not deployed retry latency. |

New inclusive timing medians (milliseconds; actual measurements, not replacements for paper values):

| L | Classical sharing | QSS | Signature quorum |
|---:|---:|---:|---:|
| 9 | 55.462 | 56.912 | 55.117 |
| 27 | 56.516 | 60.347 | 55.931 |
| 81 | 58.944 | 69.851 | 57.590 |
| 162 | 57.616 | 77.259 | 55.590 |

The archived paper medians at L=162 remain 64.81 ms classical and 88.41 ms QSS. Different hosts, package versions, system load and OS-random operations preclude identical wall-clock values. This review uses Python 3.12.14; historical cohorts record different environments. No invented confidence intervals or replacement measurements were inserted into the manuscript.

Fresh full-vector counts equal the historical 191,736/81,400/26,864 counts. Fresh endpoint outcomes are **3,859 accepted, 1,601 commitment rejections and 540 erasure aborts**, with no token-verification or other unexpected aborts. They differ from the historical 3,854/1,606/540 cohort and are not substituted into the paper. Simulation/work-order seeding does not make all endpoint inputs or cryptographic secrets deterministic. The analysis script additionally emits explicitly labeled descriptive Wilson intervals and five-block bootstrap summaries for the new campaign; these are not newly asserted historical-paper error bars.

## The approximately ten implementations

[IMPLEMENTATIONS.md](IMPLEMENTATIONS.md) identifies nine primary notebooks plus the maintained modular package: ten main software artifacts. Seven additional notebook files are local execution/preflight copies. They are not seventeen independently implemented protocols. The nine primary notebooks store no execution counters; six local copies have completed cells without stored errors. The remaining Stage04 local attempt has 7/12 executed code cells and a stored KeyboardInterrupt. It is explicitly unfinished; an archived result set is a separate evidence source.

Fresh runs cover the current nine studies, both symbolic models, and the original Stage03 code cells. Optional Qiskit/PennyLane equivalence, the older 38-/80-case suites and the older 270-microbenchmark campaign were not independently rerun. Their archival evidence is retained and distinguished from new execution.

## Independent review and scientific limits

A separate reviewer inspected changed code, documentation, focused tests, twelve then-completed output manifests, formal status records and wheel contents. The output race was the only important reported finding and was fixed with a failing-then-passing regression test. The reviewer did not independently repeat the expensive full campaigns or hosted CI. Review confidence was 0.93; this audit's overall confidence is 0.95 for the documented engineering checks, not for universal protocol security.

The cryptographic implementation uses genuine ML-KEM-768 and ML-DSA-65 in protocol campaigns. Its single-process role simulation and co-resident signing keys do not establish independent authority custody. Two exposed signer keys plus privileged CS state produce accepted attestations without reconstruction in the designated tests. Endpoints verify signatures/context, not a proof of quantum recovery. The fresh compromise model also admits the corresponding abstract attack trace.

Quantum channels are simulated. There is no malicious-secure VQSS, composable end-to-end proof, physical charging enforcement, deployed quantum advantage, crash-durable nonce/replay/resource store, or demonstrated independent multi-host trust separation. Small-secret commitment enumeration and malicious replacement limitations remain. The protocol core was preserved rather than silently strengthened to make tests look favorable.

Before submission, correct manuscript statements that raw data/models were unavailable; see PAPER_EVIDENCE_NOTES.md. Author license selection and venue-specific artifact/anonymity requirements remain unresolved. The public repository and historical ZIPs already expose author/source information, including a reference LaTeX document in old archives. This audit did not delete or rewrite immutable historical evidence. No specific A* venue was supplied, so compliance with a particular artifact policy cannot be certified.

## Acceptance checklist

- [x] Approved manuscript structure/ZIP preserved.
- [x] Inventory and status of the approximately ten main software artifacts documented.
- [x] Reproducibility bugs fixed without changing scientific core or historical outputs.
- [x] Regression tests, source parity, original archive integrity and installed wheel checked.
- [x] Historical headline values recalculated from actual raw records; plots regenerated.
- [x] Original 315k single-trit experiment freshly reproduced exactly.
- [x] Both symbolic models rerun with scoped interpretation and bypass preserved.
- [x] All nine current studies rerun at full budgets; commands, dependencies and provenance documented.
- [x] Reviewable GitHub changes and dated results/report deliverables prepared.
- [ ] Every historical notebook/backend freshly executed — explicitly incomplete as detailed above.
- [ ] Venue-specific acceptance/anonymity certification — no named venue and no such guarantee.
- [ ] Strong deployed or composable protocol security — outside demonstrated evidence.

Use REPRODUCIBILITY.md for execution commands; use the dated results bundle for complete new raw outputs and logs. Confidence: **0.95**, scoped to the verified repository work and stated evidence.
