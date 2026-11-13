# QSV2G Stage 05 implementation readiness

The Stage 05 code supports four software experiments (E1–E4) plus a candidate Tamarin symbolic model (E5). It does not establish a quantum advantage, physical charging enforcement, maliciously secure verifiable quantum secret sharing, or unbounded security.

**Changes relative to the 13 November QSV2G review-fix commit:**
- Core checks selected-authority availability before threshold reconstruction and again before signature issuance. These reject mid-stage authority loss rather than signing with a modeled offline authority's key. Existing historical traces are not regenerated.
- Matched real-PQC software reference comparator, distinct-process E1 timing, and measured selected classical packet bytes with analytical quantum counts.
- E2 real-PQC scenario checks and separate optional generated stateful test engine (test-only synthetic signatures, never cryptographic evidence).
- E3 full-dealer vector commitment outcomes with explicit channel parameters; E3 Tier B verifies issued signatures and EV token response using actual PQC for successful reconstructions; distinguish gate eligibility from token acceptance.
- E4 stage-specific authority outage/resource-contention outcomes, including successful UC-C absence only with UC-A/B present.
- E5 explicit ideal-QSS-assumption Tamarin model plus parse/proof-status script. Proof completion must be checked independently.

**Pre-publication blockers:**
1. Manuscript `micro.tex` authenticates fewer KEM-EV fields than `src/qsv2g_core.py`. Author must approve a single specification and reconcile the paper.
2. E1 does not include physical quantum distribution or network latency, and classical quorum is not fully functionality-matched. Cost numbers cannot demonstrate quantum advantage.
3. E2 current production source is a single-process simulated protocol. Hypothesis subtests use fake signing for event generation, with clear labeling.
4. E3 optimizes ideal computational-basis outcome sampling. It does NOT simulate quantum coherence/fidelity or realistic correlated memory/channel faults.
5. E4 no crash-durable reservation, full utility compromise, networked actors or re-routing policy.
6. E5 Tamarin theory is a candidate. Without a recorded parser/prover run and reviewer audit, **all proof claims are unresolved**. Its A/B ideal-gate assumption does not verify QSS or model attacker compromise.

**Provenance:** archive Stage 01–04 outputs untouched. Kaggle notebook should pin the implementation commit. Every paper number must trace to raw trial rows, environment, parameters and source SHA. No commit implies that the final experiments were performed.
