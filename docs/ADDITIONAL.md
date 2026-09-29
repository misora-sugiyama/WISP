# Additional experiments

These analyses accompany the main frozen V0–V3 comparison. Their full artifacts are not bundled in this small code repository; public data packages are listed in [DATA.md](DATA.md).

| Analysis | Purpose / scope |
|---|---|
| Reference, CREF, O1–O2 | Reference-conditioned editing, conflicting-reference and oracle-information diagnostics |
| D/L/P instruction probes | Instruction position/appearance, wording/semantics, and lexical versus rendered color effects |
| Reasoning stress | Sequential operations, abstract analogy, conditional selection, and consistency detection; supplementary probes rather than additional core tasks |
| Full FLUX V0–V7 | Task/condition heatmaps and condition-oracle summaries from stored scores; image re-scoring additionally needs the heavy image package |
| Frozen-output decomposition | 13,200 outputs = six systems × 2,200; target, preservation, and native-format stages, with unchanged final decisions |

## Human studies are distinct

| Study | Unit and size | Interpretation |
|---|---|---|
| Solve-only check | Four adults × 110 problems = 440 responses | 96.1% Solve-Strict, 99.8% Solve-Loose; click/type interface, not a human image-editing baseline |
| Independent proxy validation | Three raters judging the same 440 model outputs: 11 tasks × four conditions × two items × five editors | Majority comparison and inter-rater agreement; not 440 human solves |
| Earlier FLUX audit | 2,200 FLUX API outputs, one rater | Descriptive failure analysis; not independent validation of the cross-model ranking |

The three-rater study reports 95.5% Strict automatic–human agreement and Fleiss' κ = 0.894. Annotation codebooks and anonymized labels should be associated with the correct study when the additional package is released. Files from the older single-rater audit must not be described as the three-rater validation.

The code repository currently contains no human-level records or reviewer correspondence. No raw human-data completeness or independent reproduction claim is made here.
