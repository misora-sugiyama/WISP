# Additional experiments and human studies

These analyses accompany the shared V0–V3 comparison. Available materials are in [release `data-v1.0.0`](https://github.com/misora-sugiyama/WISP/releases/tag/data-v1.0.0); package links and contents are listed in [DATA.md](DATA.md).

| Analysis | Purpose | Available materials |
|---|---|---|
| Full FLUX V0–V7 | Task/condition heatmaps and condition-oracle analysis | 35,200 stored scores and aggregate checks; full candidate images pending |
| Human studies | Solve-only check, proxy validation, earlier FLUX audit | Protocols, codebooks and pooled tables; no individual or per-rater records |
| Reference, CREF, O1–O2 | References, conflicting references and oracle information | Archived summaries and protocol notes; no raw images or inference notebooks |
| D/L/P instruction probes | Instruction position/appearance, wording and lexical/displayed color | D 250 / L 176 / P 240 output aggregates; no fresh image re-score |
| Reasoning stress | Sequential operations, analogy, conditional selection and consistency detection | 280-output aggregate subset; long-neighbor 100 and contradiction 20 pending reconciliation |
| Frozen-output decomposition | Target, preservation and native format on six × 2,200 outputs | Decomposition artifacts not supplied; shared scores contain final decisions and native format only |

## Selected nonhuman diagnostic aggregates

`WISP_additional_aggregates_v1.0.0.zip` contains archived tables and a protocol summary. Source hashes match the archived manifest; the public verifier checks counts, rates and weighted arithmetic without running inference or image scoring. Raw outputs, worksheets, references, inference notebooks and human records are excluded.

The reasoning subset covers short-neighbor 100, public RAVEN 70, ordinary Sudoku 10 and expanded Wason 100: 280 of the manuscript's 400 outputs. The long-neighbor 100 and Sudoku-contradiction 20 remain unreconciled and are excluded, as are the earlier 90-item long-neighbor and ten-item Wason pilot summaries.

Reference/oracle summaries overlap; reasoning configuration and operation-count tables subdivide the overall results. Their denominators are not independent samples.

P-series `leakage_auto` and `mean_phrase_added_red` can include red text already present in the input; they do not alone establish new marks or copying. Wason's 99% `proxy_success` measures red-region overlap. Its 49% `cardwise_success` requires exactly the correct card set and is the manuscript's task accuracy.

## Three distinct human studies

| Study | Unit and sample | Public result provenance |
|---|---|---|
| Solve-only task-solvability check | Four adults × the same 110 problems = 440 responses | Overall/task aggregates recomputed from final responses and matched to final tables |
| Independent proxy validation | Three raters × the same 440 outputs: 11 tasks × four conditions × two items × five editors | Protocols and paper-reported summary; raw join and agreement calculations not independently reproduced |
| Earlier FLUX single-rater audit | 11 tasks × 25 base problems × eight conditions V0–V7 = 2,200 outputs, one rater | Overall/task/condition/failure aggregates recomputed from final annotations |

Solve-only yields 423/440 Strict (96.1% rounded) and 439/440 Loose (99.8%) using clicks or typed answers. These responses are distinct from the 440 model outputs in the three-rater study and are not a human image-editing baseline.

The three-rater values—95.5% Strict automatic–human agreement and Fleiss' κ = 0.894—are **paper-reported**, not recomputed in this release. Public checks cover their provenance label and table consistency; reconstructing majority votes or agreement requires private records and correspondence tables.

The single-rater audit has 160/2,200 Audit-Strict and 683/2,200 Audit-Loose passes. This descriptive analysis uses a different sample from the main benchmark's 11 × 50 × four conditions and does not validate the six-system ranking. Its table includes all 2,040 Strict failures, including three cases omitted from an older summary. No judgments were changed during packaging.

## Included and excluded materials

The human archive contains protocols, codebooks, task/label definitions and pooled tables. It excludes individual responses, per-rater labels, per-participant summaries, timestamps, free-text annotations, blind-ID mappings and candidate images. Human-level records remain private. Historical codebooks retain the WISRD name.

`verify_package.py` checks hashes, schemas, counts and aggregate consistency. The solve-only and single-rater source-to-aggregate checks cannot be rerun from this package without the private records. It does not provide complete raw human data or independent three-rater reproduction.

Commands are in [REPRODUCE.md](REPRODUCE.md).
