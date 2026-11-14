# Experiment methods and implementation map

All evaluations operate on an explicitly versioned Python reference implementation,
not a deployed EV, physical quantum link, or electrical-grid controller.

| Research question | Runnable API | Main observed evidence |
| --- | --- | --- |
| Ideal qutrit/QSS correctness, CHARGE/DISCHARGE | `qsv2g.quantum`, `evaluation.validation` | Ideal pair recoveries, state norms/marginals, six real-PQC workflows |
| Consent/context attack checks | `evaluation.workflows.e2` | Genuine-crypto rejection/acceptance cases |
| Stateful invalid transitions | `evaluation.stateful` | Hypothesis-generated model sequences; TEST-ONLY cryptographic stub |
| Software timing and matched baselines | `evaluation.workflows.e1` | QUORUM, CLASSICAL_SHARING, QSS; 4 lengths, 3 pairs, 5 process blocks in full mode |
| Full-vector quantum noise and endpoint | `evaluation.workflows.e3` | 5 local channel models, complete three-dealer commitments, real-PQC EV checks |
| Qutrit-X gate exploratory run | `evaluation.full_vector` | Original single-channel modeled commitment-gate experiment |
| Authority failure/concurrency | `evaluation.workflows.e4` | Selected offline/replay/single-process contention cases |
| Malicious authority / classical parity | `evaluation.adversarial` | 96 attack scenarios and exact classical-vs-basis QSS distribution comparisons |
| Independent retry reliability | `evaluation.retries` | Analytical and Monte Carlo retry availability/resource cost |
| Symbolic formal analyses | `docs/formal/*.spthy` | Tamarin/ Maude proof logs, with explicit assumptions and attack existence |

## Protocol lifecycle

`register → authenticate → establish_session → set_ev_intent → authorization_context → authority_verify → threshold_reconstruct → issue_token → protected_response → execute → terminate`.

`QSV2G` runs those operations *inside one Python process*. Classical ML-KEM,
ML-DSA, HKDF, HMAC and AES-GCM operations are genuine when real backends exist.
Quantum states and measurements are mathematical simulations. Logical energy
execution is a software state update, not a power-electronics experiment.

## Report results without hiding negatives

- Correct reconstruction in ideal states is not an adversarial QSS proof.
- Correct outcome labels include demonstrations of vulnerable or excluded scenarios.
- The classical threshold-sharing baseline has the same measured computational-basis
  distributions as QSS for the tested affine encoding.
- Two compromised selected signers with privileged CS-state manipulation can
  construct EV-accepted attestation without actual reconstruction; this is not
  an unauthenticated network exploit.
- At high L, independent noise accumulates and full-vector commitment gating
  can be unsuccessful even when individual-trit accuracy is high.
- Retry evaluation assumes fresh independent resources; it does not implement
  a robust multi-session network retry protocol.

Original Kaggle full-run outputs may reference earlier source snapshots;
consult `reproducibility.md` before comparing numerical values.
