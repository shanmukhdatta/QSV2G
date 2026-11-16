# Reproducing QSV2G results

This guide separates **checking archived observations**, **rerunning current software**, and **proving the restricted symbolic models**. None establishes a deployed quantum network or complete protocol security.

## 1. Install and record the revision

Use Python 3.12 on Linux for the tested reviewer environment; the package declares Python >=3.10. Other Python/OS versions require their own validation. Use an isolated environment:

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-repro.txt
python -m pip install -e . --no-deps
git rev-parse HEAD
python -m pytest -q tests
python scripts/check_parity.py
python scripts/verify_archived_evidence.py
```

The parity check requires full Git history; for a source ZIP or shallow clone, fetch the historical revision or pass `--original` as described by that script. It verifies migrated core function bodies, not scientific correctness. Genuine PQC is mandatory for the protocol runs; the Hypothesis state-machine campaign intentionally uses an explicitly labeled test substitute.

## 2. Recalculate the paper's main results from raw records

```sh
python -m qsv2g.evaluation.evidence --out results/generated/paper-evidence
```

This verifies pinned archive SHA-256 values, reads the archived CSVs directly and fails on mismatched counts/medians. It produces a machine-readable claim report, two CSV summaries, and vector PDF/SVG noise and latency figures. It checks:

- 315,000 single-trit events, 315 configurations, 9,000 events per channel/probability.
- Five p=.30 recovery probabilities: 70.07%, 100.00%, 80.28%, 70.38%, 59.01%, with erasures as failures.
- 18,000 completed matched transactions, twelve conditions, 1,500 observations per condition and the twelve rounded inclusive medians.
- 300,000 vector outcomes: 191,736 eligible, 81,400 commitment rejection, 26,864 erasure abort.
- 6,000 genuine-PQC endpoint outcomes: 3,854 accepted, 1,606 commitment rejection, 540 erasure abort.

These are **reaggregations of preserved observations**, not newly executed trials. Historical timings must not be assigned to current code. The timing archive records its own code revision/environment; the emitted report retains them. The plotted signature quorum omits reconstruction. No synthetic uncertainty bands are added.

Unlike the earlier manuscript-only audit, repository inspection has recovered raw noise events, timing trials and formal models/logs. Statements in that earlier audit that these files were unavailable describe its supplied-file scope; they no longer describe this repository. Before submission, update any manuscript caption or sentence saying raw records/models are unavailable. Keep the approved paper structure, and distinguish recovered historical evidence from new reruns.

## 3. Run all nine current-code studies

```sh
python scripts/reproduce_all.py --out results/generated/my-smoke
python -m qsv2g.evaluation.analysis results/generated/my-smoke
```

Choose a new output directory for each run. The runner claims each study directory exclusively and refuses existing directories. It records the command, seed, actual package versions, Git revision/dirty state, source hashes, status and output hashes, including failed commands. The default root contains a UTC timestamp. Scientific seeds control simulations and work order; fresh cryptographic keys/nonces use OS randomness. Hypothesis uses its own deterministic generation settings. Wall-clock timings and cryptographic bytes are not expected to match bit-for-bit.

| `--study` | Smoke workload | `--full` workload / interpretation |
|---|---|---|
| validation | 90 ideal pair trials + 6 workflows | 720 ideal pair trials + 6 workflows; does not replace historical 38-case validation |
| performance | 18 transactions, L=9, one process block | 18,000 transactions, four lengths, five process blocks; timings depend on machine/backend |
| security | 36 genuine-PQC expected controls | 36 controls; same fixed suite, not historical 80-case suite |
| noise | 120 vector trials + 30 endpoint trials | 300,000 vector + 6,000 endpoint trials; five channels/four lengths; distinct from 315k single-trit study |
| availability | 11 state/availability controls | Same 11 controls |
| noise-vector | 20 independent X-only trials | 4,000 X-only trials over L=9/27, p=0/.01, AB; deliberately bounded separate study |
| security-stateful | 20 examples × up to 15 steps | 1,000 examples × up to 50 steps; test-only crypto substitute |
| security-adversarial | Bounded subset, plus exact distribution comparisons | 96 controls plus 9 distribution comparisons; includes expected bypasses |
| reliability | 80 settings × 200 repetitions | 400 settings × 2,500 repetitions; modeled retry budgets, no deployed retry protocol |

For example:

```sh
python scripts/run_experiment.py --study validation --full --seed 2026 --out results/generated/full-check
python scripts/run_experiment.py --study performance --full --out results/generated/full-check
python scripts/run_experiment.py --study noise --full --out results/generated/full-check
python -m qsv2g.evaluation.analysis results/generated/full-check
```

`--full` means the listed budget, **not** every historical notebook or exact stochastic replay. Do not compare independent cohorts as paired trials, add overlapping case counts or call every expected outcome a prevented attack. Analysis now finds both original `e1/e3` directories and named runner paths such as `performance/e1` and `noise/e3`, and rejects an empty input instead of emitting a misleading empty success.

## 4. Rerun both formal models

```sh
python scripts/install_formal_tools.py --tools-dir .tools --status results/generated/formal-install.json
PATH="$PWD/.tools/bin:$PATH" python scripts/run_formal.py --model consent --out results/generated/formal
PATH="$PWD/.tools/bin:$PATH" python scripts/run_formal.py --model compromise --out results/generated/formal
```

Installer checks upstream archive hashes for Tamarin 1.12.0/Maude 3.5.1. Missing tools, parse failure, timeout or absent lemma summaries are not passing proofs. The four consent-model lemmas and three compromise-model lemmas were rerun in this review. `bypass_possible_with_full_compromise` is an **exists-trace result demonstrating a bypass**, not attack resistance. Both models assume an ideal reconstruction gate and abstract classical messages; they do not prove Python/ML-KEM/ML-DSA/quantum implementation equivalence.

## 5. Submission boundaries

This is a single-process software prototype. Authority signing keys are co-resident; EV/CS trust separation is not independently deployed. Resource and replay/nonce state are not crash-durable. Commitments do not supply malicious-dealer VQSS or entropy hiding for small secrets. Two signing keys plus privileged CS state can bypass reconstruction. No physical power control, real quantum channel, composable proof or quantum advantage is established.

Original cloud job URLs are not authenticated by ZIP checksums. A license has not been selected by the authors. The repository is public and names the authors; whether that is compatible with double-blind review depends on the target venue's artifact policy. No venue acceptance, artifact badge or certification is implied.
