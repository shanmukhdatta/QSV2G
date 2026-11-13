# QSV2G Stage 06 — Security Evidence and Reliability Trade-off

**Status (2026-11-13):** P0/P1 software probes completed locally with genuine OpenSSL 3.5.5 ML-KEM-768 and ML-DSA-65; P2 analytical/Monte Carlo retry model completed locally. **P3 has an unverified candidate model and runner, but no Stage 06 Tamarin proof has been executed or established.** The earlier four E5 proofs remain limited to the Stage 05 abstract model.

Stage 05 source and results are frozen. Stage 06 adds isolated experiments without editing `src/qsv2g_core.py` or overwriting `results/stage05`.

## Scope and research questions

| Phase | Research question | Evidence | Limit |
| --- | --- | --- | --- |
| P0 | Can signer compromise and dishonest-dealer control bypass intended QSS checks? | Matched single-process adversarial traces using actual ML-DSA signatures and normal EV protected response | Two-signature attack gives adversary **both selected authority private keys AND privileged charging-station internal state**; not a demonstrated network-only exploit |
| P1 | Is there a security distinction from classical 2-of-3 for the tested interface? | Same P0 cases against `ClassicalResource`; exhaustive exact computational-basis laws for 3 secrets × 3 pairs | Does not compare arbitrary quantum measurements, physical quantum-channel interception, no-cloning, VQSS security or hardware deployment |
| P2 | How much could independent fresh-resource retries improve availability? | Analytical `1-(1-a)^R` and reproducible Monte Carlo, modeled resource cost | **Not** a newly implemented authenticated retry protocol, nor experimental PQC retry latency |
| P3 | Can we prove stronger compromise-dependent claims? | Candidate Tamarin model and conservative runner only; **not executed or verified locally** | Stage 05 abstract E5 proof is NOT sufficient for malicious signer or quantum VQSS claims |

## Run from repository root

```bash
python -m pip install -r experiments/stage06/requirements.txt
pytest -q tests/test_stage06.py
python experiments/stage06/security.py --out results/stage06/local_p0_p1 --L 9
python experiments/stage06/reliability.py --out results/stage06/local_p2
```

Default P0/P1 full run: **96 scenario cases** (2 variants × 3 approved pairs × 2 operations × 8 scenarios). Each case creates a fresh session. It uses **real PQC only**, via `PQCrypto` native `pqcrypto` or OpenSSL 3.5+; no classical fallback. Fast tests use `FakePQC` clearly labeled TEST-ONLY and a small real-PQC integration test. Use `--smoke` to restrict to AB/CHARGE and 16 cases.

P0/P1 generated files:
- `p0_p1_attack_matrix.csv` — exact conditions, observer outcomes, expected status, crypto backend, CS/authority-compromise flags, and resource state.
- `p1_exact_distributions.csv` — exhaustive computational-basis pair total-variation distances and QSS one-share reduced-density distances.
- `p0_p1_summary.json` — explicit trust assumptions; conditional positives are deliberately **not** treated as surprising test failures.
- `manifest.json` — source SHA-256 files, mode, seed and platform.

### Attack labels and why they matter

* `one_approval`: refuse a single approval, holding all other assumptions fixed.
* `share_only_tamper`: refuse a corrupt reconstruction share when trusted commitments remain unchanged; consume resource.
* `dealer_replaces_secret_and_commitment`: accept a **dealer-controlled** new resource and matching hash when no independently authenticated pre-existing secret is anchored. This demonstrates a missing binding between original intended dealer secret and locally controlled commitment; it is **not** a maliciously secure VQSS test.
* `one_signer_fake_digest`: reject a forged digest when only one ML-DSA key is available.
* `two_signers_fake_digest`: two corrupted signers attest to an arbitrary digest despite an earlier genuine reconstruction.
* `two_signers_skip_reconstruction`: with BOTH compromised signing keys AND privileged CS-local control, force the simulator to its `TOKEN` stage, send a syntactically valid AEAD-protected response, and observe EV accepting **while the resource remains UNUSED**. This **does not demonstrate an on-wire exploit**; it establishes that public signature verification supplies no independent proof of actual reconstruction.
* `two_signers_cross_context`: reject an independently signed token if it binds a different authorization context, even with both signing keys exposed.

The QSS and classical variants are *identical* in computational-basis distributions for their 2-of-3 affine secret-sharing interface: `(|r,r+s,r+2s> / sqrt(3))` has probability `1/3` at the same triples as uniformly sampled classical `r`. Their one-share measurements disclose no secret; QSS reduced one-share density matrices equal `I/3`. **Do not infer equality under all quantum adversarial measurements or physical quantum-channel assumptions.**

### P2 model

For independent per-trit recovery probability `q` and three dealer vectors of length `L`, the full-vector acceptance gate is `a=q**(3*L)`. If **each retry generates a fresh independent unused resource** with approval and consent checks preserved, a budget of `R` independent attempts yields analytical success `1-(1-a)**R` and average resources consumed `(1-(1-a)**R)/a` (continuous limit `R` for `a=0`). The model separately reports analytical and sampled rates, stored qutrit equivalents (`9L` per attempt), and remote qutrit equivalents (`6L` per attempt). It does **not** implement those retries in the QSV2G protocol.

`reliability.py` outputs 400 model rows by default: 4 lengths × 5 channels × 5 noise rates × 4 budgets, with 2,500 Monte Carlo repetitions per row. No claims about improved cryptographic security or physical quantum hardware are supported.

## Interpretation and gate before protocol changes

1. **Keep the original Stage 05 protocol source unchanged** for direct comparison.
2. Confirm the intended adversarial boundary: key custody, corruption thresholds, station compromise, trusted EV context, commitment anchoring, malicious dealer behavior.
3. Decide what new security property is sought and whether classical threshold authorization can provide it just as well.
4. Only then create a separately versioned protocol design change. The old Stage 05 timings would not automatically apply to that new version.
5. Build and run a separate P3 Tamarin compromise model with honest-run reachability, explicit compromise rules, counterexample traces and proof logs. Never label its unexecuted draft as verified.

## External methodology

- Tamarin Manual, property specification and compromised-party/reveal semantics: https://tamarin-prover.com/manual/master/book/007_property-specification.html
- Tamarin Manual, sample protocol and network attacker: https://tamarin-prover.com/manual/master/book/003_example.html

Stage 06 is a stress test of the current prototype, not a claim of experimentally demonstrated quantum advantage.

## P3 — Extended formal candidate (not a verified result)

`formal/qsv2g_stage06_compromise_candidate.spthy` is a **new, unverified** Tamarin model for AB only. It explicitly includes revelation of UC-A, UC-B, and CS keys, signed reconstruction-hash statements, an ideal honest QSS-gate event, and EV verification of both signatures plus a modeled station MAC. It proposes lemmas for honest reachability, one-time acceptance, and a compromised-key acceptance trace without reconstruction. It was written against Tamarin's documented `signing` built-in and `Eq` restriction but **could not be parsed or proved locally because the Tamarin binary was unavailable**.

Run when Tamarin and Maude are installed:

```bash
python experiments/stage06/run_formal.py --out results/stage06/p3
```

Use `--tamarin-bin /path/to/tamarin-prover` for non-PATH installs. The wrapper saves parse/proof logs and only reports `PROVED_ABSTRACT_MODEL` when the prover successfully reports every named lemma as `verified`. A parse error, timeout, or failed lemma must be corrected and rerun before any formal claim. This P3 candidate does **not** establish actual physical quantum-secret-sharing security, compromise tolerance beyond AB, or an implementation-refinement theorem.
