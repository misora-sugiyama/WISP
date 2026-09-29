# Data availability and schema

## Available in this repository

`examples/generated_sample/` contains 44 item–condition records: one base problem for each of 11 tasks, under V0–V3. It includes input images, canonical answer images, binary answer masks, metadata, and reference assets. These are development examples carried over from the earlier public package. They are not a verified slice of the final corrected paper freeze.

The renderer can generate new inputs, canonical answers, red-answer masks, references, and item metadata. New generations are development data. A seed alone does not establish identity with the paper dataset; fonts, rendering versions, and the corrected frozen items matter.

## Separate packages

Public download URLs are pending. The internal author handoff is not a public distribution. The following packages should be linked here after their public copies are prepared and checked:

| Package | Intended contents | Availability |
|---|---|---|
| Shared V0–V3 fixed data | 2,200 records = 11 tasks × 50 problems × 4 conditions, inputs, GT, masks, metadata, checksums | Pending public download |
| Frozen shared outputs | 2,200 images per system, five end-to-end editors and one structured-plan diagnostic | Pending public download |
| Additional experiments | Reference/oracle, instruction probes, reasoning-stress, anonymized human evaluation, analysis files | Pending public download |
| Full FLUX V0–V7 light results | Stored row scores, heatmap/condition-oracle summaries and plotting resources | Pending public download |
| Full FLUX V0–V7 candidate images | 35,200 candidate images needed for image-level re-scoring | Separate heavy package; not in the light bundle |

Stored-score aggregation and image-level re-scoring are different reproducibility targets. The FLUX light bundle supports the former; it cannot supply absent candidate images for the latter. Provider output redistribution is separate from the synthetic-data license.

## Metadata

Each line of `items.jsonl` is one JSON record:

| Field | Meaning |
|---|---|
| `id` | Unique item–condition ID; candidate image filename stem |
| `base_id` | Problem ID shared across conditions |
| `task` | Stable task ID from [BENCHMARK.md](BENCHMARK.md) |
| `idx` | Base problem index |
| `var_id` | V0–V7 |
| `input_path` | Input worksheet, resolved relative to this JSONL file unless absolute |
| `gt_path` | Canonical answer image, with the same path rule |
| `answer_mask_path` | Binary red-answer mask in the bundled/development examples |
| `prompt` | Complete external prompt |
| `ref_paths` | Two references for REF conditions, otherwise null |
| `meta` | Task-specific generation parameters; some coordinates use the internal rendering scale |

Preserve task IDs and the corrected frozen rows when relocating a downloaded bundle. If historical absolute paths require remapping, create a separate metadata copy and record the old-to-new prefix mapping. Do not regenerate or reindex the frozen subset.

## Fonts and development generation

The renderer first honors `WISP_FONT_PATH`, then searches common Linux, macOS, and Windows TrueType font locations. It fails clearly when none is available. Its generation record includes the selected font filename. Different fonts can change samples; no cross-platform pixel identity is claimed.

Use the frozen dataset, not a fresh `--n-per-task 50` generation, for paper reproduction. Reference construction and historical corrections also need the frozen artifacts.
