# Frozen automatic scorer

`evaluator/score_wisrd.py` is byte-identical to the final author-handoff scorer. Its hash is recorded in [provenance](provenance/RELEASE.md). Do not substitute the earlier compact evaluator or earlier public-package scorer.

## Image handling

The scorer applies EXIF orientation, loads RGB, and resizes candidate images to the input size for pixel measurements. Native width and height are checked before resizing. Auto-Strict requires native size; Auto-Loose follows its task-specific relaxed rule and **does not impose a universal aspect-ratio gate**. `format_ok` reports native-size equality separately.

Red pixels satisfy `R > 150`, `G < 130`, `B < 130`, `R-G > 35`, and `R-B > 35`. Black and structure masks use mean RGB thresholds of 90 and 225 respectively, excluding red and blue pixels. Red components are 8-connected, with minimum area 8 pixels. Component matching uses the exact frozen greedy procedure.

| Task type | Auto-Strict | Auto-Loose |
|---|---|---|
| Filling | Red Dice ≥ 0.70; black F1 ≥ 0.85; native size | Red Dice ≥ 0.45 |
| Point marking | All target components matched within 18 px; no extras; component-area cap; black F1 ≥ 0.85; native size | All matched within 30 px; at most one extra |
| Dot circling | All target components matched within 22 px; no extras; black F1 ≥ 0.85; native size | All matched within 36 px; at most one extra |
| Letter/digit proxy | Red Dice ≥ 0.35; ≥20 red pixels in padded GT-answer region; ≤250 outside; structure F1 ≥ 0.75; native size | ≥20 red pixels inside; ≤1,000 outside; structure F1 ≥ 0.60 |
| Suppression | ≤25 red pixels; structure F1 ≥ 0.90; native size | ≤150 red pixels; structure F1 ≥ 0.75 |

Point-marking component area is capped at `max(1200, 4 × median GT-component area)` with integer conversion as in the code. The symbol answer region is the bounding box of GT red pixels padded by 12 pixels, not the full printed answer box. The no-red-GT symbol branch uses the suppression-style thresholds.

## Interpretation and limits

These are automatic **proxy pass rates**, not semantic reasoning accuracy. The letter/digit criteria do not explicitly recognize characters; Auto-Loose is especially permissive. Strict and Loose should both be reported with the task and condition distribution. Keeping the worksheet unchanged is correct only for suppression controls.

The paper's decomposition, three-rater validation, and earlier single-rater FLUX audit are different analyses. This release preserves the scorer's original per-item output fields; it does not claim to contain the separate 13,200-output decomposition analysis or human annotation files. See [ADDITIONAL.md](ADDITIONAL.md).
