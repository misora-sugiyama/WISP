# Source provenance

Sources and changes for the WISP code repository.

## Final scorer

`evaluator/score_wisrd.py` is unchanged from the final author bundle, including legacy WISRD identifiers. SHA-256:

```text
fc83bfb88a9557cd9d1d37a0b6aefaa587870c99f246fae89111430a8813025b
```

Older scorer versions are not used. See [SCORING.md](../SCORING.md) for the released scoring rules.

## Renderer and examples

The renderer, 44 example records, configurations and license notices originate from `WISRD_Public_Repository`.

Updates to the development renderer:

- Font selection through `WISP_FONT_PATH` and platform fallbacks.
- Binary red-answer masks, font information and development-data status in generated metadata.
- Validation of counts, task/condition choices and output paths.

Bundled image pixels and the frozen scorer are unchanged. Newly rendered examples need not match the frozen paper dataset.

## Documentation and results

Task descriptions and headline values follow the camera-ready manuscript. The benchmark is WISP; the paper title is **Image-Space Rule Discovery**.

Wrappers provide input validation, score aggregation and integrity checks. Frozen data and selected aggregate materials are distributed separately; see [DATA.md](../DATA.md) for scope and [REPRODUCE.md](../REPRODUCE.md) for verification results. Individual human records and the full 35,200 FLUX images are not released.

The original MIT and CC BY 4.0 notices are retained; their scope is defined in the license files.
