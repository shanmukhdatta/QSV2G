# Symbolic analysis

- `classical_consent.spthy`: two-authority consent and signature abstraction.
- `compromise_analysis.spthy`: key-compromise test including an existence lemma
  showing acceptance without reconstruction under a powerful attacker.

Both assume ideal quantum reconstruction and do not represent actual quantum
hardware, the complete ML-KEM/ML-DSA implementation or malicious-secure QSS.
A Tamarin lemma named `bypass_possible...` being **verified** means a modeled
bypass is reachable; it is not a positive security guarantee.

Run from repository root after installing Tamarin and Maude:

    python scripts/run_formal.py --model consent
    python scripts/run_formal.py --model compromise

Original full logs remain in the user-submitted full-result ZIPs and selected
archival text records under `results/raw/`.
