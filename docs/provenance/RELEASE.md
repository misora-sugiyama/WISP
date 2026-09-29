# Source provenance

Prepared 2026-09-28 for the WISP code repository accompanying **Image-Space Rule Discovery**.

## Final scorer

The source was read from `WISRD_REBUTTAL_HANDOFF_FINAL2/03_production_scorer/evaluator/score_wisrd.py`. Its SHA-256 matches the author bundle's `REPRODUCTION_STATUS.json`:

```text
fc83bfb88a9557cd9d1d37a0b6aefaa587870c99f246fae89111430a8813025b
```

The file is unchanged, including its legacy WISRD identifiers. The earlier public-package scorer has hash `98d95b648240d08c877abadb524600fbaef28e36463c2818c18c00a08c553982` and is not used here.

The final scorer's native-size handling, masks, greedy component matching, answer-region selection, and relaxed criteria differ from the older implementation. Documentation has been rewritten from the final source. No older scoring-threshold YAML was copied as an authoritative final configuration.

## Renderer and examples

The development renderer, 44 example records and their assets, prompt and task-generation specifications, and original MIT/CC BY 4.0 notices were carried over from `WISRD_Public_Repository`.

Updates to the development renderer:

- Explicit font selection through `WISP_FONT_PATH`, with platform fallbacks and clear failure when no font is available.
- Binary red-answer masks and mask paths included in newly generated metadata.
- Selected font filename and development-data status recorded.
- Non-positive counts, duplicate task/condition choices, and existing metadata output paths rejected.

These changes do not modify frozen paper inputs or the final scorer. Existing bundled examples retain their original pixels. The renderer is not claimed to regenerate the corrected frozen paper dataset exactly.

## Documentation and results

Names, task descriptions, interpretation, and headline values follow the camera-ready manuscript. The benchmark is named WISP; the paper title remains Image-Space Rule Discovery.

The repository adds input validation, score aggregation, distribution checksums, and meaningful smoke checks. The author's historical verification record is not represented as a new full reproduction. The complete 2,200-item fixed data, 13,200 frozen model outputs, additional analyses, human labels, and 35,200 full FLUX images are not included in this repository.

MIT and CC BY 4.0 notices are preserved from the source package. See the separate code and data license files for their scope.
