# Implementation and experiment inventory

There are **nine primary author notebooks** on the preserved pre-modularization branch, plus **seven local execution/preflight copies** (16 notebook files total). They are not sixteen independent protocol implementations. Counting the current modular package separately gives ten main software artifacts, not ten independent protocols. The package exposes nine numerical/security study commands and two symbolic models. Backend and quantum-validation variants are comparisons, not additional independent validations of every paper claim.

Historical source: [archive/pre-modularization-2026-11-14](https://github.com/shanmukhdatta/QSV2G/tree/archive/pre-modularization-2026-11-14/notebooks). The archive branch is retained; files were not copied over current source or silently rerun with changed semantics.

| # | Primary notebook / work | What it covers | Evidence / current status |
|---:|---|---|---|
| 1 | QSV2G_Kaggle_Full_Protocol_Implementation | Initial full protocol, PQCrypto/OpenSSL variants | Historical outputs under results/raw/legacy_workflows; current four-phase protocol runs genuinely use PQC. Backend variants are not separate security proofs. |
| 2 | QSV2G_Kaggle_Quantum_Qiskit_PennyLane_Validation | Independent Bell/qutrit checks and X-error experiments | Historical quantum-validation variants retained; local executed copy has 7/7 executed code cells. Optional framework equivalence was not freshly rerun in this review. |
| 3 | QSV2G_Final_Protocol_Validation_Kaggle | Early end-to-end validation and equation/control mapping | Historical final-validation archive retained; local copy has 8/8 executed cells. Current validation runner is explicitly narrower than all historical cases. |
| 4 | Stage01_Baseline_Reproducibility | 720 ideal recoveries, 6 workflows, 38 expected validation outcomes | Archive integrity checked; current 720/6 rerun passes. Historical 38-case outcomes include known limitations. |
| 5 | Stage02_Security_Analysis_Kaggle_Fixed | 80 expected adversarial observations, 7 limitations | Archive integrity checked; current fixed 36-case suite is separate, not a renamed 80-case rerun. |
| 6 | Stage03_Quantum_Noise_and_Reliability | Five channels, 315k single-trit events | All 315k archived events reaggregated; endpoints verified and vector figure regenerated. All ten original code cells were then replayed with only output paths relocated; the 315,000 decompressed event rows match the historical CSV byte-for-byte. |
| 7 | Stage04_Performance_and_Baselines | Earlier workflows/scaling/authorization microbenchmarks | Historical raw files preserved. The local attempt is explicitly unfinished: 7/12 code cells executed, stored KeyboardInterrupt. It must not be cited as a completed full run; supplied result archive is a separate evidence source. |
| 8 | Stage05_Experimental_Evaluation | E1 matched latency; E2 controls/stateful; E3 full-vector/endpoint noise; E4 availability; E5 formal consent | Raw 18k/300k/6k counts and medians checked; current bounded E1–E4 rerun; all four E5 lemmas freshly verified. A new full 18,000-transaction campaign also completed; its host-specific timings remain separate from the historical medians. |
| 9 | Stage06_Experimental_Evaluation | P0 compromise; P1 exact distributions; P2 modeled retries; P3 formal compromise | Full current 96-control campaign and 9 distributions rerun; 400×2500 retry model rerun; all three formal lemmas freshly verified, including bypass existence. |
| 10 | Current src/qsv2g modular package | Maintained four-phase implementation, nine study runners and two formal models | Core AST parity preserved; fresh regression/CI and full current-study reruns are documented in the repository audit. |

The nine primary notebooks have no stored execution counts; they are source notebooks. Their six completed local counterparts contain executed cells without stored errors; the seventh Stage04 local attempt contains the interruption above. Python code cells without notebook magics parse successfully. Static parsing and stored output inspection do not establish fresh execution. Historical scientific records remain tied to their original source hashes and run manifests, rather than being attributed to the refactored package.

## Four-phase code map

| Protocol phase | Current methods / files | Boundary |
|---|---|---|
| Registration | QSV2G.register; crypto.mac; quantum.dense_transport_tag | Pre-shared secret credential binding; dense coding simulated. Current code also dense-transports the CS registration tag. |
| Authentication/session | authenticate; establish_session; crypto.hkdf_extract/hkdf_expand; Traffic | Genuine ML-KEM, local transcript-bound KDF and Finished; shared process, not independent remote identity verification. |
| Consent/QSS authorization | set_ev_intent; authorization_context; authority_verify; threshold_reconstruct; issue_token; resources.py | Separate EV intent, three dealers, two holders, commitments, two ordinary signatures; no malicious-secure VQSS. |
| Execution/termination | protected_response; execute; terminate | EV checks received token/context; process-local single-use and simulated cap. Current code protects terminal record in the C2E direction; manuscript diagram conservatively left transport unspecified. |

The protocol core function bodies retain exact AST parity with the historical modularization baseline. This review changes reproducibility tooling and documentation, not the protocol or measured historical results. A file-level comparison is stronger evidence of preservation than a claim that a cleaner README makes the protocol secure.
