# Reproducing the reported results

## Verified results

The fixed dataset, six frozen output sets and evaluation materials are available in [release `data-v1.0.0`](https://github.com/misora-sugiyama/WISP/releases/tag/data-v1.0.0).

Re-scoring all six sets with the unchanged scorer and public fixed metadata produced zero errors across 13,200 images. All 39,600 Auto-Strict, Auto-Loose and native-format decisions match the stored results by model and item ID, with no row or metadata mismatches. Each system covers 11 tasks × 50 problems × four conditions.

The [verification report](https://github.com/misora-sugiyama/WISP/releases/download/data-v1.0.0/fresh_reproduction_report.json) records scorer, metadata and score-file hashes, wrapper completion, ID coverage and row comparisons without private paths. The [headline CSV](https://github.com/misora-sugiyama/WISP/releases/download/data-v1.0.0/fresh_reproduction_headlines.csv) contains exact counts.

All entries below are **pass counts out of 2,200**, not percentages:

| System | Auto-Strict | Auto-Loose | Native format |
|---|---:|---:|---:|
| Nano Banana Pro | 1,071 | 1,407 | 2,199 |
| Qwen-Image-Edit | 294 | 449 | 2,200 |
| FLUX.2 Klein 4B API | 252 | 482 | 2,200 |
| FLUX.2 Klein 4B open-weight | 248 | 479 | 2,200 |
| InstructPix2Pix | 0 | 122 | 0 |
| OCR+Gemini plan-render | 770 | 1,275 | 2,200 |

Nano Banana's 2,199/2,200 native-format passes (approximately 99.9545%) round to 100.0%, but are not an exact 100%. Native format means original width/height equality, not answer correctness. OCR+Gemini is a structured-plan diagnostic with a different response interface.

Verified inputs to the fresh evaluation:

- Frozen scorer SHA-256: `fc83bfb88a9557cd9d1d37a0b6aefaa587870c99f246fae89111430a8813025b`.
- Public fixed metadata SHA-256: `856e3a2a1296dc07265d2da5da541f7eb788fecfb8034f8f8fae0aabaf346654`.
- Evaluation-wrapper SHA-256: `7e934070b04eb2ca7db237adcae8b48d621461685429b2490b7b413d6a0c8229`.
- Stored-reference CSV SHA-256: `5693b4d1b3f225597d2fb169d09f49999956fa860f3b835a83b71f69ae3247c9`.

Archive READMEs describe earlier packaging checks; the report above records subsequent image-level re-scoring. No images were regenerated or model APIs called. This verifies automatic-score reproduction, not human validation of model correctness.

## Code and development self-checks

Use Python 3.10 or later, install `requirements.txt`, and run from the code repository root:

```bash
python scripts/verify_release.py
python scripts/run_smoke_test.py
```

`verify_release.py` checks code checksums, including the scorer. The smoke test checks 44 canonical GT decisions, unchanged inputs and missing-candidate rejection. GT mode sets preservation to 1 when candidate and GT paths match; it is a self-check. Ordinary unchanged-input candidates must fail active tasks and pass suppression controls.

## Frozen shared images

Download the ZIPs in [DATA.md](DATA.md) into `downloads/` under the repository. For Nano Banana Pro:

```bash
python -m zipfile -e downloads/WISP_fixed_shared_v0_v3_v1.0.0.zip data
python -m zipfile -e downloads/WISP_outputs_nano_banana_pro_v1.0.0.zip data
python data/WISP_fixed_shared_v0_v3_v1.0.0/verify_package.py --strict-files
python data/WISP_outputs_nano_banana_pro_v1.0.0/verify_package.py --strict-files
```

Check ZIP hashes against the release-level `SHA256SUMS.txt` before extraction. Package helpers check extracted files; `--strict-files` also rejects unlisted files. Run these checks before adding local results.

Evaluate the existing frozen candidates with the released wrapper:

```bash
python scripts/evaluate.py --metadata data/WISP_fixed_shared_v0_v3_v1.0.0/items.jsonl --candidates-dir data/WISP_outputs_nano_banana_pro_v1.0.0/candidates --out outputs/nano_banana_pro.csv
python scripts/summarize_scores.py --scores outputs/nano_banana_pro.csv --model nano_banana_pro --out outputs/nano_banana_pro_summary.json
```

For other systems, use `qwen_image_edit`, `flux_api`, `flux_open_weight`, `instruct_pix2pix`, or `ocr_gemini_plan_render`. Output ZIPs are named `WISP_outputs_<model_id>_v1.0.0.zip` and contain `candidates/`.

Use new result filenames: the wrapper and aggregator refuse overwrites. New API generations are separate experiments and may differ from the frozen results.

Each output archive contains one `<item-id>.png` for each of the 2,200 fixed IDs. The wrapper rejects missing or ambiguous candidates and image errors. Use `items.jsonl` for scoring; `output_manifest.csv` is only an image inventory.

The summarizer compares one-decimal rates with [reported_shared_v0_v3.csv](../results/reported_shared_v0_v3.csv). To verify exact reproduction, also join by model and item ID and compare individual decisions and integer pass counts.

## Re-aggregate historical shared scores

```bash
python -m zipfile -e downloads/WISP_shared_stored_scores_v1.0.0.zip data
python data/WISP_shared_stored_scores_v1.0.0/verify_shared_scores.py
python data/WISP_shared_stored_scores_v1.0.0/verify_shared_scores.py --rebuild outputs/shared_stored_tables
```

This standard-library helper checks 13,200 saved labels, model/task/condition coverage, released aggregates, 12 headline rates and 30 family-bar values. It rebuilds pooled, task, condition, task–condition and family tables without loading images or invoking the scorer. `stored_format` requires native width/height equality, not merely matching aspect ratio or a correct answer.

## Re-aggregate FLUX V0–V7 light results

```bash
python -m zipfile -e downloads/WISP_FLUX_V0-V7_LIGHT_v1.0.0.zip data
python data/WISP_FLUX_V0-V7_LIGHT_v1.0.0/verify_flux_light.py
python data/WISP_FLUX_V0-V7_LIGHT_v1.0.0/verify_flux_light.py --rebuild outputs/flux_v0v7_tables
```

The helper checks 35,200 stored rows, 176 heatmap cells, summary means and item/task condition-oracle aggregates. The oracle tests whether any of eight conditions passes, using all outcomes; it is not a deployable selection policy. The full 35,200 images are absent and cannot be replaced by the 2,200 shared FLUX images.

## Check human-evaluation aggregate materials

```bash
python -m zipfile -e downloads/WISP_human_evaluation_aggregates_v1.0.1.zip data
python data/WISP_human_evaluation_aggregates_v1.0.1/verify_package.py
```

Download the updated human package from [data-v1.0.1](https://github.com/misora-sugiyama/WISP/releases/tag/data-v1.0.1). The helper checks hashes, schemas, confusion counts and pooled vote arithmetic, including unanimity and Fleiss’ κ. Source matching, individual judgments and pairwise coefficients cannot be reconstructed without private records; see [ADDITIONAL.md](ADDITIONAL.md).

## Check selected additional diagnostic aggregates

```bash
python -m zipfile -e downloads/WISP_additional_aggregates_v1.0.2.zip data
python data/WISP_additional_aggregates_v1.0.2/verify_package.py
```

Download the additional package with the corrected D-series task description from [data-v1.0.2](https://github.com/misora-sugiyama/WISP/releases/tag/data-v1.0.2). Its aggregate tables and verification code are unchanged from v1.0.1. This standard-library helper checks hashes, count/rate bounds, weighted reference summaries, D/L/P totals, duplicate removal and reasoning aggregates for 398 distinct outputs. It checks the recorded Sudoku answer/color observations separately from proxy scores. It does not run inference or image scoring; raw additional images remain outside this package.

## Scoring conventions

Wrappers validate inputs without changing scorer decisions. Threshold YAML files are descriptive; the scorer uses constants in its code. Complete reproduction requires no missing images or scoring errors. See [SCORING.md](SCORING.md) for task-specific proxies and limits.
