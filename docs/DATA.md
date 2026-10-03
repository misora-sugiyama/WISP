# Data availability and schema

## Release packages

The fixed dataset, six frozen output sets and supporting evaluation materials are available in [release `data-v1.0.0`](https://github.com/misora-sugiyama/WISP/releases/tag/data-v1.0.0). All 14 release files were checked for public access, exact size and matching SHA-256.

Each ZIP extracts to a directory with the same name minus `.zip`. Download the fixed dataset and the chosen output archive for image-level reproduction. The other archives provide stored-score analyses or pooled study materials with the narrower scopes listed below.

| Package | Exact asset filename | Contents |
|---|---|---|
| Fixed shared V0–V3 data | [`WISP_fixed_shared_v0_v3_v1.0.0.zip`](https://github.com/misora-sugiyama/WISP/releases/download/data-v1.0.0/WISP_fixed_shared_v0_v3_v1.0.0.zip) | 2,200 records; 1,100 input images + 550 GT images; relative-path metadata and checksums |
| Nano Banana Pro outputs | [`WISP_outputs_nano_banana_pro_v1.0.0.zip`](https://github.com/misora-sugiyama/WISP/releases/download/data-v1.0.0/WISP_outputs_nano_banana_pro_v1.0.0.zip) | 2,200 frozen outputs |
| Qwen-Image-Edit outputs | [`WISP_outputs_qwen_image_edit_v1.0.0.zip`](https://github.com/misora-sugiyama/WISP/releases/download/data-v1.0.0/WISP_outputs_qwen_image_edit_v1.0.0.zip) | 2,200 frozen outputs |
| FLUX.2 Klein 4B API outputs | [`WISP_outputs_flux_api_v1.0.0.zip`](https://github.com/misora-sugiyama/WISP/releases/download/data-v1.0.0/WISP_outputs_flux_api_v1.0.0.zip) | 2,200 frozen shared outputs; separate from the full V0–V7 experiment |
| FLUX.2 Klein 4B open-weight outputs | [`WISP_outputs_flux_open_weight_v1.0.0.zip`](https://github.com/misora-sugiyama/WISP/releases/download/data-v1.0.0/WISP_outputs_flux_open_weight_v1.0.0.zip) | 2,200 frozen outputs |
| InstructPix2Pix outputs | [`WISP_outputs_instruct_pix2pix_v1.0.0.zip`](https://github.com/misora-sugiyama/WISP/releases/download/data-v1.0.0/WISP_outputs_instruct_pix2pix_v1.0.0.zip) | 2,200 frozen outputs |
| OCR+Gemini plan-render outputs | [`WISP_outputs_ocr_gemini_plan_render_v1.0.0.zip`](https://github.com/misora-sugiyama/WISP/releases/download/data-v1.0.0/WISP_outputs_ocr_gemini_plan_render_v1.0.0.zip) | 2,200 frozen diagnostic outputs; different response interface |
| Shared stored scores | [`WISP_shared_stored_scores_v1.0.0.zip`](https://github.com/misora-sugiyama/WISP/releases/download/data-v1.0.0/WISP_shared_stored_scores_v1.0.0.zip) | 13,200 saved row decisions; pooled, task, condition, task–condition and family aggregates |
| FLUX V0–V7 light results | [`WISP_FLUX_V0-V7_LIGHT_v1.0.0.zip`](https://github.com/misora-sugiyama/WISP/releases/download/data-v1.0.0/WISP_FLUX_V0-V7_LIGHT_v1.0.0.zip) | 35,200 stored score rows; heatmaps and condition oracles; no candidate images |
| Human-evaluation protocols and aggregates | [`WISP_human_evaluation_aggregates_v1.0.0.zip`](https://github.com/misora-sugiyama/WISP/releases/download/data-v1.0.0/WISP_human_evaluation_aggregates_v1.0.0.zip) | Protocols/codebooks and pooled tables; three-rater figures are paper-reported, not independently recomputed |
| Selected additional diagnostic aggregates | [`WISP_additional_aggregates_v1.0.0.zip`](https://github.com/misora-sugiyama/WISP/releases/download/data-v1.0.0/WISP_additional_aggregates_v1.0.0.zip) | Reference/CREF/O1–O2 and D/L/P tables; reconciled reasoning subset of 280 outputs; protocols and aggregate checks only |

Each archive contains a README, provenance/verification material, a Python verification helper and `SHA256SUMS.txt`. The release also has [release-level checksums](https://github.com/misora-sugiyama/WISP/releases/download/data-v1.0.0/SHA256SUMS.txt), the [fresh image-evaluation report](https://github.com/misora-sugiyama/WISP/releases/download/data-v1.0.0/fresh_reproduction_report.json) and its [exact-count CSV](https://github.com/misora-sugiyama/WISP/releases/download/data-v1.0.0/fresh_reproduction_headlines.csv). These report assets are separate from the eleven ZIPs. Follow the helper commands in [REPRODUCE.md](REPRODUCE.md); helper filenames vary by package.

The full 35,200 FLUX V0–V7 candidate images are **not included** in the light-results archive or in the 2,200-image FLUX shared-output archive. A full heavy-image release is pending.

The additional archive is an **aggregate-and-protocol package**, not the full additional-experiment dataset. It includes archived reference/CREF/O1–O2 summaries, Nano Banana's five-spatial-task V0–V7 table, D-series (250 evaluated outputs), L-series (176), P-series (240), and a reconciled reasoning subset: short-neighbor 100, RAVEN 70, ordinary Sudoku 10 and expanded Wason 100 (280 outputs total). Overlapping summary files must not be counted as independent samples. The long-neighbor 100-output extension and 20 Sudoku-contradiction variants remain unreconciled and are excluded. Raw additional inputs/outputs/references, executable inference notebooks and the separate frozen-output decomposition are not supplied.

## Fixed shared dataset

The fixed dataset contains **2,200 records = 11 tasks × 50 base problems × four conditions V0–V3**. Its **1,650 image files** comprise 1,100 input images and 550 GT images. Input images are reused by two condition records, and GT images by four records. Six separate output archives each contain one candidate image per record.

All original image bytes are preserved. The public `items.jsonl` keeps the corrected rows, order and ID relationships, and removes only the historical `original_input_path` and `original_gt_path` fields. Its `input_path` and `gt_path` values resolve relative to the extracted fixed-data directory. The package records original-source hashes and the public metadata transformation.

Some corrected `base_id` values differ from the index embedded in `id` and `idx`, including the corrected index-zero rows. Preserve these relationships. Do not regenerate, reindex, or rerun historical replacement steps.

The original fixed handoff has no standalone mask files or `answer_mask_path` field. The frozen scorer derives target/red masks and answer regions from the GT images, and preservation masks from the inputs. The separate masks in the 44 development examples are not part of the fixed paper dataset.

## Historical scores and study materials

The shared stored-score archive contains 13,200 **historical** decisions. Their source files and every exported label were checked, and their aggregates match the saved final headline results and 30 family-bar values. The packaging step is not a new image-level evaluation. Current image re-scoring status is tracked in [REPRODUCE.md](REPRODUCE.md).

FLUX light results support re-aggregation of stored scores: 11 tasks × 400 base problems × eight conditions = 35,200 records. They cannot support image-level re-scoring without their matching input/GT and candidate images.

The human-evaluation package contains protocols, codebooks and pooled tables. It excludes individual responses, per-rater labels, per-participant summaries, timestamps, free-text notes and correspondence tables. The three-rater summary is explicitly labeled as reported in the paper; the raw join, majority vote and agreement coefficients were not independently reproduced in this release. See [ADDITIONAL.md](ADDITIONAL.md) for the three distinct study designs and verification limits.

Additional diagnostic tables were checked against their archived source hashes and aggregate arithmetic. Their release does not represent a fresh image re-score or inference run. P-series legacy red-signal fields can respond to red text already present in an input; they do not by themselves establish newly introduced marks or leakage. See [ADDITIONAL.md](ADDITIONAL.md) for the supported interpretations and remaining gaps.

## Development examples and metadata

`examples/generated_sample/` contains 44 item–condition records: one base problem for each of 11 tasks under V0–V3. These earlier development examples include input images, canonical answers, binary answer masks, metadata and reference assets. They are not a verified slice of the corrected paper freeze.

The renderer generates new development inputs, answers, masks, references and metadata. A seed alone does not establish identity with the paper dataset: fonts, rendering versions and historical corrections matter.

Each `items.jsonl` record uses these fields where applicable:

| Field | Meaning |
|---|---|
| `id` | Unique item–condition ID; candidate image filename stem |
| `base_id` | Original problem identity shared across conditions; preserve corrected values |
| `task` | Stable implementation ID from [BENCHMARK.md](BENCHMARK.md) |
| `idx` | Fixed comparison index; do not infer `base_id` from it |
| `var_id` | Information condition; the shared freeze uses V0–V3 |
| `input_path`, `gt_path` | Image paths relative to the public JSONL file |
| `answer_mask_path` | Development-example field; absent from the original shared freeze |
| `prompt` | Complete external prompt |
| `ref_paths` | References for REF conditions; null for the shared V0–V3 freeze |
| `meta` | Task-specific generation parameters; some coordinates use the internal rendering scale |

The renderer honors `WISP_FONT_PATH`, then checks common TrueType font locations. Different fonts can change pixels. Use the released fixed dataset for paper reproduction; a fresh `--n-per-task 50` run creates development data.

## License scope

The repository retains its MIT source-code notice and CC BY 4.0 notice for author-created synthetic data and cleaned aggregate tables. Candidate output archives do not grant a new license to model-system outputs; applicable original model/provider terms remain separate. Their included code notice covers the verification helper only. Human-level records and model weights are not distributed.
