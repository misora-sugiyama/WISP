# Additional experiments and human studies

These analyses accompany the shared V0–V3 comparison. Original materials are in [data-v1.0.0](https://github.com/misora-sugiyama/WISP/releases/tag/data-v1.0.0), with corrected aggregates in [data-v1.0.1](https://github.com/misora-sugiyama/WISP/releases/tag/data-v1.0.1). Package links and contents are listed in [DATA.md](DATA.md).

| Analysis | Purpose | Available materials |
|---|---|---|
| Full FLUX V0–V7 | Task/condition heatmaps and condition-oracle analysis | 35,200 stored scores and aggregate checks; full candidate images pending |
| Human studies | Solve-only check, proxy validation, earlier FLUX audit | Protocols, codebooks and pooled tables; no individual or per-rater records |
| Reference, CREF, O1–O2 | References, conflicting references and oracle information | Archived summaries and protocol notes; no raw images or inference notebooks |
| D/L/P instruction probes | Instruction position/appearance, wording and lexical/displayed color | D 250 / L 176 / P 240 output aggregates; no fresh image re-score |
| Reasoning stress | Sequential operations, analogy, conditional selection and consistency detection | 398 distinct outputs represented; long-neighbor deduplicated and contradiction variants reconciled |
| Frozen-output decomposition | Target, preservation and native format on six × 2,200 outputs | Decomposition artifacts not supplied; shared scores contain final decisions and native format only |

## Selected nonhuman diagnostic aggregates

`WISP_additional_aggregates_v1.0.1.zip` contains archived tables, corrected extension aggregates and a protocol summary. Source hashes match the archived manifest; the public verifier checks counts, rates and weighted arithmetic without running inference or image scoring. Raw outputs, worksheets, references, inference notebooks and human records are excluded.

The reasoning aggregates cover 398 distinct outputs: short-neighbor 100, long-neighbor 98, public RAVEN 70, ordinary Sudoku 10, expanded Wason 100 and contradiction Sudoku 20. The long-neighbor archive reused one replacement output three times; removing two duplicates gives 90/98 task passes (91.8%), 97/98 native-format passes (99.0%) and 90/98 passing both. Its 200-operation level has eight distinct outputs; each other level has ten. The earlier long-neighbor and Wason pilot summaries remain excluded.

All 118 distinct extension images matched archived sizes and SHA-256 hashes. Inspection of the 20 contradiction images confirmed ten NONE answers when explicitly requested (eight red, two black), versus no NONE answers without that instruction (nine digits, one empty answer box). The geometric proxy's 50% pass rate on the latter set is not semantic NONE accuracy. The package includes sanitized source rows, image hashes and a helper to reproduce the corrected aggregates; it does not include these images.

Reference/oracle summaries overlap; reasoning configuration and operation-count tables subdivide the overall results. Their denominators are not independent samples.

P-series `leakage_auto` and `mean_phrase_added_red` can include red text already present in the input; they do not alone establish new marks or copying. Wason's 99% `proxy_success` measures red-region overlap. Its 49% `cardwise_success` requires exactly the correct card set and is the manuscript's task accuracy.

## Three distinct human studies

| Study | Unit and sample | Public result provenance |
|---|---|---|
| Solve-only task-solvability check | Four adults × the same 110 problems = 440 responses | Overall/task aggregates recomputed from final responses and matched to final tables |
| Independent proxy validation | Three raters × the same 440 outputs: 11 tasks × four conditions × two items × five editors | Protocols and overall/task/model/family aggregates recomputed from final labels after identifier and frozen-image verification |
| Earlier FLUX single-rater audit | 11 tasks × 25 base problems × eight conditions V0–V7 = 2,200 outputs, one rater | Overall/task/condition/failure aggregates recomputed from final annotations |

Solve-only yields 423/440 Strict (96.1% rounded) and 439/440 Loose (99.8%) using clicks or typed answers. These responses are distinct from the 440 model outputs in the three-rater study and are not a human image-editing baseline.

The three raters had computer-science backgrounds; one was an author and none was compensated. Version 1.0.1 recomputes their final explicit judgments without changing labels. Strict automatic–human agreement remains 95.5% and Fleiss’ κ remains 0.894. Loose unanimity is corrected from 89.1% to **88.9% (391/440)** and Loose Fleiss’ κ from 0.787 to **0.783**. The original release is retained.

The single-rater audit has 160/2,200 Audit-Strict and 683/2,200 Audit-Loose passes. This descriptive analysis uses a different sample from the main benchmark's 11 × 50 × four conditions and does not validate the six-system ranking. Its table includes all 2,040 Strict failures, including three cases omitted from an older summary. No judgments were changed during packaging.

## Included and excluded materials

The human archive contains protocols, codebooks, task/label definitions, pooled tables and four unchanged input/GT/candidate examples with majority decisions. Individual responses, per-rater labels, per-participant summaries, timestamps, free-text annotations, blind-ID mappings and the complete item-level majority table remain private. Historical codebooks retain the WISRD name.

`verify_package.py` checks hashes, schemas, counts, confusion tables and pooled vote arithmetic, including unanimity and Fleiss’ κ. Source-to-aggregate matching and pairwise coefficients require private records; the package does not expose them.

Commands are in [REPRODUCE.md](REPRODUCE.md).
