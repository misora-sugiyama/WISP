# Reproducing the reported results

## What can be checked immediately

```bash
python scripts/verify_release.py
python scripts/run_smoke_test.py
```

The first command verifies distribution checksums, including the exact final scorer. The second checks 44 canonical GT decisions, actual unchanged-input candidates, and rejection of missing candidates. The canonical GT mode explicitly forces preservation values to 1 when the candidate path is the GT path. Therefore it is a self-check, not model evaluation. The unchanged-input cases exercise the ordinary candidate path and verify that active tasks fail while suppression controls pass.

## Fixed shared V0–V3 comparison

The final comparison needs the fixed inputs/GT/metadata and the original 2,200 outputs for the chosen system. Download availability is tracked in [DATA.md](DATA.md). New API generations may differ and must be reported as new experiments.

1. Verify the downloaded data manifest and image checksums. The author handoff has its own `VERIFY_HANDOFF.py`; retain that original verifier and manifest with the bundle.
2. Confirm 2,200 unique item IDs, 11 tasks, V0–V3, and 50 records per task/condition cell. Confirm that these are the corrected frozen items; do not run historical replacement steps again.
3. Use `evaluator/score_wisrd.py` with SHA-256 `fc83bfb88a9557cd9d1d37a0b6aefaa587870c99f246fae89111430a8813025b`.
4. Run the validation wrapper and compare the rounded aggregate to the paper.

For example, after placing the fixed metadata at `data/shared/items.jsonl` and Nano Banana Pro candidates at `data/outputs/nano_banana_pro/`:

```bash
python scripts/evaluate.py --metadata data/shared/items.jsonl --candidates-dir data/outputs/nano_banana_pro --out outputs/nano_banana_pro.csv
python scripts/summarize_scores.py --scores outputs/nano_banana_pro.csv --model nano_banana_pro --out outputs/nano_banana_pro_summary.json
```

Replace the paths with the actual downloaded layout. Each candidate must be named with its full item ID, including the condition. The wrapper rejects missing and multiple candidate files for an ID; it does not silently choose a duplicate extension. Existing result files are not overwritten.

Model IDs for the comparison are `nano_banana_pro`, `qwen_image_edit`, `flux_api`, `flux_open_weight`, `instruct_pix2pix`, and `ocr_gemini_plan_render`. Expected results are in [reported_shared_v0_v3.csv](../results/reported_shared_v0_v3.csv).

The comparison checks unique IDs, balanced task/condition counts, and one-decimal percentage agreement. **It does not itself prove frozen-data identity**; that requires the original data manifest. Matching rounded percentages does not prove every individual decision is identical.

## Scoring conventions

The final scorer is deliberately unchanged. The repository's wrapper adds input validation without changing pass/fail decisions. Threshold configuration is descriptive: the frozen scorer implements its constants in code and does not load a YAML configuration at runtime.

Image loading failures and absent outputs must be resolved before claiming complete reproduction. The raw scorer records these as error rows; the wrapper and aggregator reject them. See [SCORING.md](SCORING.md) for the task-specific proxy definitions.
