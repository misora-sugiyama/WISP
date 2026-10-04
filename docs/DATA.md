# Data availability and schema

## Release packages

The fixed dataset, six frozen output sets and evaluation materials are available in [release `data-v1.0.0`](https://github.com/misora-sugiyama/WISP/releases/tag/data-v1.0.0). The original 14 files were checked for public access, size and SHA-256. Corrected human-evaluation aggregates are in [data-v1.0.1](https://github.com/misora-sugiyama/WISP/releases/tag/data-v1.0.1). Additional aggregates with the corrected D-series task description are in [data-v1.0.2](https://github.com/misora-sugiyama/WISP/releases/tag/data-v1.0.2); their table bytes, the fixed data and model outputs are unchanged.

Each ZIP extracts to a directory named after the archive without `.zip`. Image-level reproduction requires the fixed dataset and the chosen output archive. Other packages contain stored-score analyses or pooled study materials.

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
| Human-evaluation protocols and aggregates | [`WISP_human_evaluation_aggregates_v1.0.1.zip`](https://github.com/misora-sugiyama/WISP/releases/download/data-v1.0.1/WISP_human_evaluation_aggregates_v1.0.1.zip) | Protocols/codebooks, recomputed pooled tables and four illustrative output triples; no individual labels |
| Selected additional diagnostic aggregates | [`WISP_additional_aggregates_v1.0.2.zip`](https://github.com/misora-sugiyama/WISP/releases/download/data-v1.0.2/WISP_additional_aggregates_v1.0.2.zip) | Reference/CREF/O1–O2 and D/L/P tables; corrected reasoning aggregates for 398 distinct outputs; protocols and aggregate checks |

Each archive includes a README, provenance, a Python verifier and `SHA256SUMS.txt`. Alongside the eleven ZIPs are [release checksums](https://github.com/misora-sugiyama/WISP/releases/download/data-v1.0.0/SHA256SUMS.txt), the [image-evaluation report](https://github.com/misora-sugiyama/WISP/releases/download/data-v1.0.0/fresh_reproduction_report.json) and [exact-count CSV](https://github.com/misora-sugiyama/WISP/releases/download/data-v1.0.0/fresh_reproduction_headlines.csv). Verifier filenames vary; see [REPRODUCE.md](REPRODUCE.md) for commands.

The full 35,200 FLUX V0–V7 candidate images remain unreleased. Neither the light-results package nor the 2,200-image shared-output archive contains them.

The additional archive contains aggregates and protocols: reference/CREF/O1–O2, Nano Banana's five-spatial-task V0–V7 comparison, D 250 / L 176 / P 240 outputs, and 398 distinct reasoning outputs (short-neighbor 100, long-neighbor 98, RAVEN 70, ordinary Sudoku 10, expanded Wason 100, contradiction Sudoku 20). Two duplicate long-neighbor rows were removed. Overlapping tables are not independent samples. Raw additional inputs/outputs/references, inference notebooks and frozen-output decomposition artifacts are not supplied.

## Fixed shared dataset

The fixed dataset has **2,200 records = 11 tasks × 50 base problems × four conditions V0–V3** and 1,650 image files: 1,100 inputs and 550 GTs. Two condition records share each input; four share each GT. Each of the six output archives has one candidate per record.

Original image bytes, corrected metadata rows, order and ID relationships are preserved. Public `items.jsonl` removes `original_input_path` and `original_gt_path`; `input_path` and `gt_path` resolve relative to its directory. Provenance records source hashes and this metadata transformation.

Some corrected `base_id` indices differ from those in `id` and `idx`, including index-zero rows. Preserve these relationships; do not regenerate, reindex or repeat historical replacements.

The fixed dataset has no standalone masks or `answer_mask_path`. The scorer derives target/red masks and answer regions from GT images and preservation masks from inputs. Masks in the 44 development examples are separate.

## Historical scores and study materials

The shared-score archive contains 13,200 historical row decisions. Source files and exported labels were checked; aggregates match the saved final headlines and 30 family-bar values. Subsequent image re-scoring is documented in [REPRODUCE.md](REPRODUCE.md).

FLUX light results contain 11 tasks × 400 problems × eight conditions = 35,200 stored rows for re-aggregation. Image re-scoring requires the matching input, GT and candidate images.

Human materials contain protocols, codebooks, recomputed pooled tables and four illustrative input/GT/output triples with majority decisions. Individual responses, per-rater labels, per-participant summaries, timestamps, notes and correspondence tables remain private. The final three-rater files were matched using the original identifier formula; all 1,320 images in the available packet matched the frozen images. Pooled vote counts support checking unanimity and Fleiss’ κ without identifying raters. Study designs and limits are in [ADDITIONAL.md](ADDITIONAL.md).

Additional tables were checked against archived hashes and aggregate arithmetic, without new image scoring or inference. P-series red-signal fields can include pre-existing red text and do not alone establish new marks or leakage; see [ADDITIONAL.md](ADDITIONAL.md).

## Development examples and metadata

`examples/generated_sample/` contains 44 records: one base problem per task across 11 tasks and V0–V3, with inputs, canonical answers, binary masks, metadata and references. These are development examples, not a verified slice of the corrected paper dataset.

The renderer produces new inputs, answers, masks, references and metadata. Seeds alone do not reproduce the paper dataset; fonts, renderer versions and historical corrections also matter.

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

The renderer checks `WISP_FONT_PATH`, then common TrueType font locations. Fonts can change pixels. Use the fixed dataset for paper reproduction; `--n-per-task 50` generates new development data.

## License scope

The repository retains its MIT source-code notice and CC BY 4.0 notice for author-created synthetic data and cleaned aggregate tables. Candidate output archives do not grant a new license to model-system outputs; applicable original model/provider terms remain separate. Their included code notice covers the verification helper only. Human-level records and model weights are not distributed.
