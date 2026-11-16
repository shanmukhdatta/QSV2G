# Evidence updates for the seven-page manuscript

This repository review recovered files that were absent from the earlier manuscript-only input set. The approved seven-page paper structure is unchanged, but the following **evidence-provenance statements need updating before submission**. These corrections do not change the experimental values or strengthen the protocol's security claim.

| Existing limitation statement | Now supported by repository evidence | Required distinction |
|---|---|---|
| Noise graph is only graphically recovered and raw trials unavailable | 315,000 event rows in the original noise archive; `qsv2g.evaluation.evidence` regenerates the plot directly | The evidence command reaggregates archived data. A separate original-notebook code-cell replay in this review also reproduced all 315k event rows byte-for-byte; distinguish the two checks. |
| Timing trial distributions are unavailable | Stage05 ZIP includes 18,000 timing rows and five process-block CSVs | Original inclusive medians remain 88.41/64.81 ms at L=162; do not replace them with new-host rerun medians. |
| Exact formal models/logs unavailable | Both model files in formal/, original logs in archives, and fresh proof logs from this review | Seven restricted lemmas include an attack-existence result; no full protocol/computational security proof. |
| No result-producing commit identified | Stage05 manifest: b463fc758fa28f1853fe06c4130ee2f25173ac0c; Stage06 manifest: 2860ab3b0137c68e58fe1195a4c71a82a60ce183 | Earlier Stage01–04 outputs instead carry source hashes; cloud account/job identity is not authenticated by these manifests. |
| One software environment described for all cohorts | Earlier security/performance metadata reports Python3.13.15; Stage05/06 record Python3.13.18; this review runs Python3.12 | Report environments by cohort; current code/runtime measurements are a separate experiment. |

Suggested concise figure provenance: “Regenerated from archived single-trit event records; erasures count as failures.” For performance: “Inclusive software-time medians recomputed from the archived 18,000-transaction campaign; signature-only quorum omits reconstruction.” Detailed process-block uncertainty needs a clearly specified estimator and should not be invented simply because raw data are now available.

Historical source artifacts and earlier branches are already public; some original archival ZIPs contain a reference LaTeX document. The current branch tracks no new manuscript `.tex` or `.bib` files. Preserve immutable scientific archives, but authors should assess existing public material against their venue's anonymity policy rather than assuming that an extension guard makes Git history or ZIP contents confidential.
