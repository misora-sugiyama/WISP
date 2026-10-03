# WISP: Worksheet Image-Space Problem Solving

Code, frozen-data release documentation, and development examples for **Image-Space Rule Discovery**, accepted at ACCV 2026.

**Misora Sugiyama · Toya Oyama · Hirokatsu Kataoka**

WISP evaluates whether an image-editing system can solve a worksheet problem by placing the answer on the input image while preserving unrelated content. It covers **11 tasks, five task families, and eight information conditions** on a 1024 × 1024 canvas.

WISP is the benchmark name; the paper retains its registered title. Existing task IDs and `wisrd` filenames are preserved for compatibility with frozen experiments.

| Example input | Canonical answer |
|:--:|:--:|
| ![Line-intersection worksheet](examples/generated_sample/dataset/line_intersections_0000__notext.png) | ![Required red answer](examples/generated_sample/ground_truth/line_intersections_0000__gt.png) |

## Release status

The fixed dataset, six frozen output sets and supporting evaluation materials are available in [release `data-v1.0.0`](https://github.com/misora-sugiyama/WISP/releases/tag/data-v1.0.0). All 14 release files were checked for public access, exact size and matching SHA-256.

The small code repository contains the final reported scorer, a development renderer, 44 example records, configurations, expected headline results, and verification tools. The separate release packages comprise:

- The corrected fixed shared dataset: 2,200 item–condition records referencing 1,100 inputs and 550 GT images.
- Six frozen output archives: 2,200 images per system, 13,200 images in total.
- The 13,200 historical stored row scores and reproducible shared-comparison aggregates.
- FLUX V0–V7 light results: 35,200 stored score rows with heatmap and condition-oracle data, without the 35,200 candidate images.
- Human-evaluation protocols, codebooks and pooled aggregate tables, without individual responses or rater-level records.
- Selected additional diagnostic aggregates and protocol summaries for reference/oracle, D/L/P and a reconciled 280-output reasoning subset. Remaining reasoning records and raw additional images/runners are not supplied.

The 44 development examples and newly rendered samples do not replace the corrected fixed dataset. A fresh run of the unchanged scorer on all 13,200 frozen images reproduced every stored Strict, Loose and native-format decision with zero scoring errors. See [exact package names and scope](docs/DATA.md), [reproduction steps and the fresh evaluation report](docs/REPRODUCE.md), and [human-study provenance](docs/ADDITIONAL.md).

## Quick start

Use Python 3.10 or later. Run commands from the repository root.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/verify_release.py
python scripts/run_smoke_test.py
```

On Windows, activate with `.venv\Scripts\activate`.

The smoke test exercises bundled examples and no-edit controls without calling a model API. It checks the scorer's frozen SHA-256 and verifies that missing candidates cannot silently produce a valid evaluation.

### Generate development samples

```bash
python generator/render_wisrd.py --out outputs/new_sample --n-per-task 1 --variants V0 V1 V2 V3
```

Choose a fresh output directory for each generation. Set `WISP_FONT_PATH` to a TrueType font to control typography. Font and rendering differences can change pixels; exact paper reproduction must use the frozen inputs and outputs.

### Evaluate model outputs

Save each candidate as `<item-id>.png` (JPEG and WebP are also supported), then run:

```bash
python scripts/evaluate.py --metadata examples/generated_sample/items.jsonl --candidates-dir outputs/model --out outputs/scores.csv
python scripts/summarize_scores.py --scores outputs/scores.csv --out outputs/summary.json
```

The evaluation wrapper checks file coverage before invoking the unchanged scorer. It rejects missing or ambiguous candidates, duplicate item IDs, and failed image reads. See [reproduction instructions](docs/REPRODUCE.md) for the fixed shared subset and comparison against paper values.

## Reported shared V0–V3 results

Each system is evaluated on the same 2,200 item–condition pairs. The percentages below are the paper-reported rates; the fresh evaluation of the frozen images reproduced them, as detailed in [REPRODUCE.md](docs/REPRODUCE.md).

| System | Role | Auto-Strict | Auto-Loose |
|---|---|---:|---:|
| Nano Banana Pro | End-to-end editor | 48.7 | 64.0 |
| Qwen-Image-Edit | End-to-end editor | 13.4 | 20.4 |
| FLUX.2 Klein 4B API | End-to-end editor | 11.5 | 21.9 |
| FLUX.2 Klein 4B open-weight | End-to-end editor | 11.3 | 21.8 |
| InstructPix2Pix | End-to-end editor | 0.0 | 5.5 |
| OCR+Gemini plan-render | Structured-plan diagnostic | 35.0 | 58.0 |

Auto-Strict and Auto-Loose are task-specific **proxy pass rates**. In particular, letter/digit scoring does not explicitly recognize glyph identity. Instruction-conditioned success is not evidence of open-ended rule induction. See [scoring and limitations](docs/SCORING.md).

## Documentation

- [Tasks and information conditions](docs/BENCHMARK.md)
- [Data packages, schema, and generation](docs/DATA.md)
- [Frozen-output reproduction](docs/REPRODUCE.md)
- [Scorer definitions and limitations](docs/SCORING.md)
- [Additional experiments and human studies](docs/ADDITIONAL.md)
- [Source provenance and changes](docs/provenance/RELEASE.md)

## Citation and licenses

Please cite **Image-Space Rule Discovery**, Misora Sugiyama, Toya Oyama, and Hirokatsu Kataoka, ACCV 2026. Machine-readable citation metadata is in [CITATION.cff](CITATION.cff); archival identifiers will be added when verified.

The original package's [MIT code license](LICENSE) and [CC BY 4.0 data license](DATA_LICENSE.md) are retained. Third-party model outputs, model weights, and the manuscript are not covered by the repository's data license.
