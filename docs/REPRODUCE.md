# Reproducing the reported results

## Availability and verification scope

The fixed dataset, six frozen output sets and supporting evaluation materials are available in [release `data-v1.0.0`](https://github.com/misora-sugiyama/WISP/releases/tag/data-v1.0.0). All 14 release files were checked for public access, exact size and matching SHA-256.

**Fresh image-level re-scoring passed.** The unchanged released scorer was run on all six frozen output sets using the public fixed metadata: **13,200 image rows, zero scoring errors**. All **39,600 saved-versus-fresh decisions** (Auto-Strict, Auto-Loose and native-format checks) agree exactly by model and item ID. There are zero mismatching rows or metadata fields; each system has complete 11 × 50 × four-condition coverage. This is stronger than matching rounded headline percentages.

The release includes the [full path-free verification report](https://github.com/misora-sugiyama/WISP/releases/download/data-v1.0.0/fresh_reproduction_report.json) and [exact-count headline CSV](https://github.com/misora-sugiyama/WISP/releases/download/data-v1.0.0/fresh_reproduction_headlines.csv). The report records scorer/metadata hashes, fresh score-file hashes, wrapper completion, ID coverage and row-level comparison results. It summarizes the comparison; it does not expose private input paths.

All entries below are **pass counts out of 2,200**, not percentages:

| System | Auto-Strict | Auto-Loose | Native format |
|---|---:|---:|---:|
| Nano Banana Pro | 1,071 | 1,407 | 2,199 |
| Qwen-Image-Edit | 294 | 449 | 2,200 |
| FLUX.2 Klein 4B API | 252 | 482 | 2,200 |
| FLUX.2 Klein 4B open-weight | 248 | 479 | 2,200 |
| InstructPix2Pix | 0 | 122 | 0 |
| OCR+Gemini plan-render | 770 | 1,275 | 2,200 |

Nano Banana's native-format count is **2,199/2,200 (approximately 99.9545%)**, which rounds to 100.0% at one decimal. It is not an exact 100% pass rate. Native format measures original width/height equality, not answer correctness. OCR+Gemini remains a structured-plan diagnostic with a different response interface.

Verified inputs to the fresh evaluation:

- Frozen scorer SHA-256: `fc83bfb88a9557cd9d1d37a0b6aefaa587870c99f246fae89111430a8813025b`.
- Public fixed metadata SHA-256: `856e3a2a1296dc07265d2da5da541f7eb788fecfb8034f8f8fae0aabaf346654`.
- Evaluation-wrapper SHA-256: `7e934070b04eb2ca7db237adcae8b48d621461685429b2490b7b413d6a0c8229`.
- Stored-reference CSV SHA-256: `5693b4d1b3f225597d2fb169d09f49999956fa860f3b835a83b71f69ae3247c9`.

Some archive READMEs describe package-integrity checks or historical stored-score aggregation and state that their **package builders** did not re-score images. Those statements retain their original scope. This separate report records the subsequent image-level evaluation; no fresh image generations or model API calls were needed. It establishes reproduction with the released automatic proxy scorer, not independent human validation of model correctness.

## Code and development self-checks

Use Python 3.10 or later, install `requirements.txt`, and run from the code repository root:

```bash
python scripts/verify_release.py
python scripts/run_smoke_test.py
```

The first verifies code-distribution checksums, including the final scorer. The smoke test checks 44 canonical GT decisions, unchanged-input candidates and rejection of missing candidates. Canonical GT mode sets preservation values to 1 when the candidate path is the GT path, so it is a self-check. The unchanged-input cases use the ordinary candidate path and test that active tasks fail while suppression controls pass.

## Frozen shared images

Download the ZIPs listed in [DATA.md](DATA.md) into a `downloads/` directory under the code repository. For Nano Banana Pro, extract and verify the exact release folders:

```bash
python -m zipfile -e downloads/WISP_fixed_shared_v0_v3_v1.0.0.zip data
python -m zipfile -e downloads/WISP_outputs_nano_banana_pro_v1.0.0.zip data
python data/WISP_fixed_shared_v0_v3_v1.0.0/verify_package.py --strict-files
python data/WISP_outputs_nano_banana_pro_v1.0.0/verify_package.py --strict-files
```

Check the ZIP against the release-level `SHA256SUMS.txt` before extraction as well. The package helper verifies all extracted checksummed files; `--strict-files` also rejects unlisted files. Run strict checks before adding local results to an extracted package.

Evaluate the existing frozen candidates with the released wrapper:

```bash
python scripts/evaluate.py --metadata data/WISP_fixed_shared_v0_v3_v1.0.0/items.jsonl --candidates-dir data/WISP_outputs_nano_banana_pro_v1.0.0/candidates --out outputs/nano_banana_pro.csv
python scripts/summarize_scores.py --scores outputs/nano_banana_pro.csv --model nano_banana_pro --out outputs/nano_banana_pro_summary.json
```

For another system, substitute its exact output-folder/model ID: `qwen_image_edit`, `flux_api`, `flux_open_weight`, `instruct_pix2pix`, or `ocr_gemini_plan_render`. All output ZIP names follow `WISP_outputs_<model_id>_v1.0.0.zip` and contain `candidates/`. Keep OCR+Gemini's structured-plan diagnostic interpretation separate from the five end-to-end editors.

Use fresh result filenames: the wrapper and aggregator do not overwrite existing outputs. No model API call is needed to score these saved images. New API generations are new experiments and may differ from the frozen results.

The fixed metadata contains 2,200 unique IDs, with 50 records per each of 11 tasks and four conditions. Each output archive contains exactly one `<item-id>.png` per ID. The wrapper rejects missing or ambiguous candidates and image errors. `output_manifest.csv` is an image inventory; use the fixed dataset's `items.jsonl` for scoring.

The unchanged scorer SHA-256 is `fc83bfb88a9557cd9d1d37a0b6aefaa587870c99f246fae89111430a8813025b`. Package provenance verifies frozen-data identity. The summarizer compares one-decimal rates to [reported_shared_v0_v3.csv](../results/reported_shared_v0_v3.csv); agreement after rounding alone does not prove every row decision is identical. A stronger comparison joins by model and item ID and compares Strict/Loose decisions and integer pass counts.

## Re-aggregate historical shared scores

```bash
python -m zipfile -e downloads/WISP_shared_stored_scores_v1.0.0.zip data
python data/WISP_shared_stored_scores_v1.0.0/verify_shared_scores.py
python data/WISP_shared_stored_scores_v1.0.0/verify_shared_scores.py --rebuild outputs/shared_stored_tables
```

This standard-library helper checks 13,200 saved row labels, complete model/task/condition coverage, all released aggregates, 12 historical headline rates and 30 family-bar values. It regenerates pooled, task, condition, task–condition and family tables. It does not load images or invoke the scorer. `stored_format` means native width/height equality with the input; it is not semantic correctness or merely aspect-ratio equality.

## Re-aggregate FLUX V0–V7 light results

```bash
python -m zipfile -e downloads/WISP_FLUX_V0-V7_LIGHT_v1.0.0.zip data
python data/WISP_FLUX_V0-V7_LIGHT_v1.0.0/verify_flux_light.py
python data/WISP_FLUX_V0-V7_LIGHT_v1.0.0/verify_flux_light.py --rebuild outputs/flux_v0v7_tables
```

The helper checks 35,200 stored rows, 176 heatmap cells, the saved summary means, and item/task condition-oracle aggregates. The oracle asks whether any of the eight saved conditions passes; it is an analysis using all outcomes, not a deployable selection policy. The full 35,200 images are not in this archive. The 2,200-image shared FLUX archive is not a replacement for them.

## Check human-evaluation aggregate materials

```bash
python -m zipfile -e downloads/WISP_human_evaluation_aggregates_v1.0.0.zip data
python data/WISP_human_evaluation_aggregates_v1.0.0/verify_package.py
```

This checks public file hashes, schemas, counts and consistency between pooled tables. Individual responses and rater-level data are not released. The public helper cannot independently reproduce individual judgments, three-rater majority labels or agreement coefficients. The three-rater values remain labeled as paper-reported; see [ADDITIONAL.md](ADDITIONAL.md).

## Check selected additional diagnostic aggregates

```bash
python -m zipfile -e downloads/WISP_additional_aggregates_v1.0.0.zip data
python data/WISP_additional_aggregates_v1.0.0/verify_package.py
```

This standard-library helper verifies package hashes, count/rate bounds, weighted reference summaries, D/L/P totals and the included 280-output reasoning subset. It does not run inference, load model images or reproduce image-level judgments. The long-neighbor 100-output extension, 20 Sudoku-contradiction variants and full raw additional experiments remain outside this release. See the package README and [ADDITIONAL.md](ADDITIONAL.md) for precise scope.

## Scoring conventions

The final scorer remains unchanged. Wrappers add validation without changing decisions. Threshold YAML files are descriptive: the scorer implements its constants in code and does not load those files at runtime. Resolve missing images and scoring errors before claiming complete reproduction. See [SCORING.md](SCORING.md) for task-specific proxies and their limits.
