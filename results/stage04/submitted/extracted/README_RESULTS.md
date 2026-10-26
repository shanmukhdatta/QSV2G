# Stage 04 results (QSV2G)

- `end_to_end_raw.csv`: unmodified QSV2G `run_demo()` end-to-end wall clock; warmups omitted.
- `phase_latency_raw.csv`: phase durations from the original reference log; do not assume phase-duration sums equal end-to-end timing exactly.
- `qss_resource_scaling_raw.csv`: separate preparation/reconstruction wall time and analytical remote-transmission/subsystem counts.
- `authorization_baselines_raw.csv`: one-signer B0, two-classical-signer B1, original-QSS B2 **post-context microbenchmarks**. Not full baseline V2G protocols.
- `instrumented_aead_packets_raw.csv`: subset of five AEAD packet types, not complete classical V2G communication.
- `pqc_object_sizes.csv`: genuine provider sizes; PEM encoding changes byte lengths when OpenSSL is used.
- `*_statistics.csv`, `figure_*.png`: computed summaries and candidate figures.
- `legacy_*.csv`: original reported eight-run benchmark and AEAD packet data retained for provenance, not pooled with new measurements.
- `environment.json`, `source_hashes.json`, `manifest.json`, `run_log.txt`: reproducibility and validation metadata.

**Important**: No quantum physical channel, real grid meter, energy estimate for cryptography, or end-to-end comparison of independently implemented alternative trust architectures. Source and protocol hashes refer to the verified historical Section IV reference, which must be reconciled with any newer edited paper version.
