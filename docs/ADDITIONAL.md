# Additional experiments and human studies

The fixed dataset, six frozen output sets and supporting evaluation materials are available in [release `data-v1.0.0`](https://github.com/misora-sugiyama/WISP/releases/tag/data-v1.0.0). All 14 release files were checked for public access, exact size and matching SHA-256.

These analyses accompany the main fixed shared V0–V3 comparison. Exact package links and current scope are listed in [DATA.md](DATA.md).

| Analysis | Purpose | Release preparation status |
|---|---|---|
| Full FLUX V0–V7 | Task/condition heatmaps and condition-oracle analysis | Light package available: 35,200 stored scores and reproducible aggregates; full candidate-image package pending |
| Human studies | Solve-only check, independent proxy validation, earlier FLUX audit | Protocols/codebooks and pooled aggregate package available; no individual or per-rater records |
| Reference, CREF, O1–O2 | Reference-conditioned editing, conflicting references and oracle information | Selected archived summaries and protocol notes available; raw images and inference notebooks not supplied |
| D/L/P instruction probes | Instruction position/appearance, wording and lexical/rendered color effects | D 250 / L 176 / P 240 evaluated-output aggregate tables available; no fresh image re-score |
| Reasoning stress | Sequential operations, analogy, conditional selection and consistency detection | Reconciled 280-output aggregate subset available; long-neighbor 100 and contradiction 20 excluded pending reconciliation |
| Frozen-output decomposition | Target, preservation and native-format stages on six × 2,200 outputs | Separate decomposition artifacts not supplied; the shared-score package supplies final decisions and native format only |

## Selected nonhuman diagnostic aggregates

`WISP_additional_aggregates_v1.0.0.zip` contains archived aggregate tables and a protocol summary. Source hashes were checked against the handoff manifest; public verification checks count/rate bounds and weighted arithmetic. It does not re-run model inference or image scoring. Raw model outputs, worksheets, references, runnable inference notebooks and human records are not included.

The reasoning portion contains short-neighbor 100, public RAVEN 70, ordinary Sudoku 10 and expanded Wason 100: **280 outputs**. The manuscript discusses 400 reasoning outputs. The long-neighbor 100-output extension and 20 Sudoku-contradiction variants remain unreconciled and are excluded; older 90-item long-neighbor and ten-item Wason pilot summaries are also excluded. This archive does not establish that all additional experiments are fully released.

Reference/oracle summaries overlap one another, and reasoning configuration/operation-count tables subdivide their corresponding overall results. Do not sum all file denominators as independent samples.

Two interpretation details matter: P-series `leakage_auto` and `mean_phrase_added_red` preserve a historical instruction-region red-signal measure that may include red already printed in the input; those fields alone do not demonstrate newly introduced marks or copying. In Wason, 99% `proxy_success` measures red-region overlap, while 49% `cardwise_success` requires exactly the correct card set and is the task accuracy used in the manuscript.

## Three distinct human studies

| Study | Unit and sample | Public result provenance |
|---|---|---|
| Solve-only task-solvability check | Four adults each answered the same 110 problems: 440 responses | Overall/task aggregates recomputed from final scored responses and checked against final tables |
| Independent proxy validation | Three raters evaluated the same 440 model outputs: 11 tasks × four conditions × two items × five editors | Protocols and paper-reported summary supplied; raw join and agreement calculations not independently reproduced here |
| Earlier FLUX single-rater audit | 11 tasks × 25 base problems × eight conditions V0–V7: 2,200 outputs, one rater | Overall/task/condition/failure aggregates recomputed from final annotation rows |

The solve-only check gives 423/440 Solve-Strict (96.1% rounded) and 439/440 Solve-Loose (99.8%). It uses a click/type interface, not human image editing. Its 440 responses are distinct from the 440 model outputs judged in the three-rater study.

The three-rater study reports 95.5% Strict automatic–human agreement and Fleiss' κ = 0.894. These values are labeled **reported in the paper**, not newly recomputed in this release. Public verification checks their provenance label and supplied table consistency; it cannot reconstruct majority votes or agreement without the private records and correspondence table.

The earlier single-rater audit has 160/2,200 Audit-Strict and 683/2,200 Audit-Loose passes. It is a descriptive failure analysis on a different sample from the main shared benchmark (which uses 11 × 50 × four conditions). It is not independent validation of the six-system ranking. The pooled failure table includes all 2,040 Strict failures, including three residual cases absent from an older category summary. No new human judgments were assigned during packaging.

## Included and excluded materials

The human-evaluation archive contains study protocols, annotation codebooks, task/label definitions and pooled tables. Individual responses, per-rater labels, per-participant summaries, timestamps, free-text annotations, blind-ID correspondence tables and candidate images are excluded. The original records remain in the private research archive. Historical codebooks retain the WISRD name for traceability.

`verify_package.py` checks package hashes, schemas, total counts and consistency between the public aggregate tables. Source-to-aggregate recomputation was performed during packaging for solve-only and single-rater results, but cannot be rerun from this public package alone because it omits the individual records. No raw human-data completeness or independent three-rater reproduction claim is made.

For command examples, see [REPRODUCE.md](REPRODUCE.md). The repository and public packages do not contain reviewer correspondence.
