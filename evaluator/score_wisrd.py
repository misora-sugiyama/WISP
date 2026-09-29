"""Exact WISRD scorer used for the final reported cross-model values."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from PIL import Image, ImageOps

POINT_TASKS = {"line_intersections", "line_midpoint_mark", "overlapping_shapes"}
RING_TASK = "count_dots_visual"
ANSWER_TASKS = {
    "circled_letter_base",
    "circled_letter_allA",
    "circled_letter_copy_single",
    "count_dots_digit",
}
BLANK_TASKS = {"circled_letter_blank", "circled_letter_blankcircle"}

POINT_STRICT_DIST = 18.0
POINT_LOOSE_DIST = 30.0
RING_STRICT_DIST = 22.0
RING_LOOSE_DIST = 36.0
MIN_RED_AREA = 8
PRESERVATION_THRESHOLD = 0.85
ANSWER_PADDING_PX = 12


def load_rgb_native(path: Path) -> tuple[np.ndarray, tuple[int, int]]:
    with Image.open(path) as image:
        image = ImageOps.exif_transpose(image).convert("RGB")
        size = image.size
        array = np.asarray(image)
    return array, size


def resize_rgb(array: np.ndarray, size: tuple[int, int]) -> np.ndarray:
    if (array.shape[1], array.shape[0]) == tuple(size):
        return array
    return np.asarray(
        Image.fromarray(array).resize(tuple(size), Image.Resampling.BILINEAR)
    )


def red_mask(array: np.ndarray) -> np.ndarray:
    r = array[:, :, 0].astype(np.int16)
    g = array[:, :, 1].astype(np.int16)
    b = array[:, :, 2].astype(np.int16)
    return (
        (r > 150)
        & (g < 130)
        & (b < 130)
        & ((r - g) > 35)
        & ((r - b) > 35)
    )


def blue_mask(array: np.ndarray) -> np.ndarray:
    r = array[:, :, 0].astype(np.int16)
    g = array[:, :, 1].astype(np.int16)
    b = array[:, :, 2].astype(np.int16)
    return (b > 140) & (r < 130) & (g < 170) & ((b - r) > 35)


def black_mask(array: np.ndarray) -> np.ndarray:
    r = array[:, :, 0].astype(np.int16)
    g = array[:, :, 1].astype(np.int16)
    b = array[:, :, 2].astype(np.int16)
    gray = (r + g + b) / 3.0
    return (gray < 90) & (~red_mask(array)) & (~blue_mask(array))


def structure_mask(array: np.ndarray) -> np.ndarray:
    r = array[:, :, 0].astype(np.int16)
    g = array[:, :, 1].astype(np.int16)
    b = array[:, :, 2].astype(np.int16)
    gray = (r + g + b) / 3.0
    return (gray < 225) & (~red_mask(array)) & (~blue_mask(array))


def mask_f1(first: np.ndarray, second: np.ndarray) -> float:
    first = first.astype(bool)
    second = second.astype(bool)
    tp = np.logical_and(first, second).sum()
    fp = np.logical_and(~first, second).sum()
    fn = np.logical_and(first, ~second).sum()
    denominator = 2 * tp + fp + fn
    return 1.0 if denominator == 0 else float(2 * tp / denominator)


def dice(first: np.ndarray, second: np.ndarray) -> float:
    first = first.astype(bool)
    second = second.astype(bool)
    denominator = first.sum() + second.sum()
    return 1.0 if denominator == 0 else float(
        2 * np.logical_and(first, second).sum() / denominator
    )


def bbox_from_mask(mask: np.ndarray) -> tuple[int, int, int, int] | None:
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


def components_no_scipy(mask: np.ndarray, min_area: int = MIN_RED_AREA) -> list[dict[str, Any]]:
    mask = mask.astype(bool)
    height, width = mask.shape
    visited = np.zeros((height, width), dtype=bool)
    ys, xs = np.where(mask)
    components: list[dict[str, Any]] = []

    for y0, x0 in zip(ys, xs):
        if visited[y0, x0]:
            continue

        stack = [(int(y0), int(x0))]
        visited[y0, x0] = True
        pixel_x: list[int] = []
        pixel_y: list[int] = []

        while stack:
            y, x = stack.pop()
            pixel_x.append(x)
            pixel_y.append(y)

            for dy in (-1, 0, 1):
                ny = y + dy
                if ny < 0 or ny >= height:
                    continue
                for dx in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx = x + dx
                    if nx < 0 or nx >= width:
                        continue
                    if mask[ny, nx] and not visited[ny, nx]:
                        visited[ny, nx] = True
                        stack.append((ny, nx))

        if len(pixel_x) < min_area:
            continue

        px = np.asarray(pixel_x)
        py = np.asarray(pixel_y)
        components.append(
            {
                "cx": float(px.mean()),
                "cy": float(py.mean()),
                "area": int(len(px)),
                "bbox": (
                    int(px.min()),
                    int(py.min()),
                    int(px.max()),
                    int(py.max()),
                ),
            }
        )

    return components


def match_components(
    gt_components: list[dict[str, Any]],
    candidate_components: list[dict[str, Any]],
    distance_threshold: float,
) -> dict[str, Any]:
    used: set[int] = set()
    matched = 0
    distances: list[float] = []

    for gt_component in gt_components:
        best_index = None
        best_distance = float("inf")

        for index, candidate_component in enumerate(candidate_components):
            if index in used:
                continue
            distance = math.hypot(
                gt_component["cx"] - candidate_component["cx"],
                gt_component["cy"] - candidate_component["cy"],
            )
            if distance < best_distance:
                best_index = index
                best_distance = distance

        if best_index is not None and best_distance <= distance_threshold:
            used.add(best_index)
            matched += 1
            distances.append(best_distance)

    return {
        "matched": matched,
        "missed": len(gt_components) - matched,
        "extra": len(candidate_components) - len(used),
        "distances": distances,
    }


def resolve_path(metadata_path: Path, raw_path: str) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path
    return metadata_path.parent / path


def resolve_candidate(item: dict[str, Any], directory: Path) -> Path | None:
    item_id = str(item["id"])
    for extension in (".png", ".jpg", ".jpeg", ".webp"):
        candidate = directory / f"{item_id}{extension}"
        if candidate.exists():
            return candidate

    matches = [
        path
        for path in directory.glob(f"{item_id}.*")
        if path.is_file() and path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
    ]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        raise RuntimeError(
            f"Ambiguous candidates for {item_id}: "
            + ", ".join(str(path) for path in matches)
        )
    return None


def score_item(item: dict[str, Any], metadata_path: Path, candidate_path: Path) -> dict[str, Any]:
    input_path = resolve_path(metadata_path, str(item["input_path"]))
    gt_path = resolve_path(metadata_path, str(item["gt_path"]))

    input_array, input_size = load_rgb_native(input_path)
    gt_array, gt_size = load_rgb_native(gt_path)
    candidate_native, candidate_size = load_rgb_native(candidate_path)

    if gt_size != input_size:
        gt_array = resize_rgb(gt_array, input_size)
    candidate_array = resize_rgb(candidate_native, input_size)

    canvas_size_ok = bool(candidate_size == input_size)
    aspect_ratio_ok = bool(
        abs(
            (candidate_size[0] / candidate_size[1])
            - (input_size[0] / input_size[1])
        )
        < 1e-6
    )

    gt_red = red_mask(gt_array)
    candidate_red = red_mask(candidate_array)
    is_gt_smoke_test = candidate_path.resolve() == gt_path.resolve()
    black_f1_value = (
        1.0
        if is_gt_smoke_test
        else mask_f1(black_mask(input_array), black_mask(candidate_array))
    )
    structure_f1_value = (
        1.0
        if is_gt_smoke_test
        else mask_f1(structure_mask(input_array), structure_mask(candidate_array))
    )

    result: dict[str, Any] = {
        "id": item["id"],
        "base_id": item.get("base_id", item["id"]),
        "task": item["task"],
        "idx": item.get("idx"),
        "var_id": item.get("var_id", ""),
        "input_path": str(input_path),
        "gt_path": str(gt_path),
        "candidate_path": str(candidate_path),
        "input_width": input_size[0],
        "input_height": input_size[1],
        "candidate_width": candidate_size[0],
        "candidate_height": candidate_size[1],
        "canvas_size_ok": canvas_size_ok,
        "aspect_ratio_ok": aspect_ratio_ok,
        "format_ok": canvas_size_ok,
        "gt_red_pixels": int(gt_red.sum()),
        "candidate_red_pixels": int(candidate_red.sum()),
        "red_dice": dice(gt_red, candidate_red),
        "black_f1": black_f1_value,
        "structure_f1": structure_f1_value,
        "n_gt_components": np.nan,
        "n_candidate_components": np.nan,
        "matched_strict": np.nan,
        "missed_strict": np.nan,
        "extra_strict": np.nan,
        "mean_distance_strict": np.nan,
        "matched_loose": np.nan,
        "missed_loose": np.nan,
        "extra_loose": np.nan,
        "mean_distance_loose": np.nan,
        "answer_region_red_pixels": np.nan,
        "outside_answer_red_pixels": np.nan,
        "core_strict": np.nan,
        "core_loose": np.nan,
        "strict_preserved": np.nan,
        "strict_full": np.nan,
        "loose_ok": np.nan,
        "proxy_strict": np.nan,
        "proxy_loose": np.nan,
        "auto_strict": False,
        "auto_loose": False,
        "error": "",
    }

    task = str(item["task"])

    if task == "fill_target_shape":
        core_strict = result["red_dice"] >= 0.70
        core_loose = result["red_dice"] >= 0.45
        result.update(
            {
                "eval_type": "fill",
                "core_strict": bool(core_strict),
                "core_loose": bool(core_loose),
                "strict_preserved": bool(
                    core_strict and result["black_f1"] >= PRESERVATION_THRESHOLD
                ),
                "strict_full": bool(
                    core_strict
                    and result["black_f1"] >= PRESERVATION_THRESHOLD
                    and canvas_size_ok
                ),
                "loose_ok": bool(core_loose),
            }
        )

    elif task in POINT_TASKS:
        gt_components = components_no_scipy(gt_red)
        candidate_components = components_no_scipy(candidate_red)
        strict_match = match_components(
            gt_components, candidate_components, POINT_STRICT_DIST
        )
        loose_match = match_components(
            gt_components, candidate_components, POINT_LOOSE_DIST
        )
        gt_areas = [component["area"] for component in gt_components]
        adaptive_max_area = max(
            1200,
            int(4 * np.median(gt_areas)) if gt_areas else 1200,
        )
        max_candidate_area = max(
            [component["area"] for component in candidate_components],
            default=0,
        )
        core_strict = (
            len(gt_components) > 0
            and strict_match["missed"] == 0
            and strict_match["extra"] == 0
            and max_candidate_area <= adaptive_max_area
        )
        core_loose = (
            len(gt_components) > 0
            and loose_match["missed"] == 0
            and loose_match["extra"] <= 1
        )
        result.update(
            {
                "eval_type": "point_components",
                "n_gt_components": len(gt_components),
                "n_candidate_components": len(candidate_components),
                "matched_strict": strict_match["matched"],
                "missed_strict": strict_match["missed"],
                "extra_strict": strict_match["extra"],
                "mean_distance_strict": float(np.mean(strict_match["distances"]))
                if strict_match["distances"]
                else np.nan,
                "matched_loose": loose_match["matched"],
                "missed_loose": loose_match["missed"],
                "extra_loose": loose_match["extra"],
                "mean_distance_loose": float(np.mean(loose_match["distances"]))
                if loose_match["distances"]
                else np.nan,
                "core_strict": bool(core_strict),
                "core_loose": bool(core_loose),
                "strict_preserved": bool(
                    core_strict and result["black_f1"] >= PRESERVATION_THRESHOLD
                ),
                "strict_full": bool(
                    core_strict
                    and result["black_f1"] >= PRESERVATION_THRESHOLD
                    and canvas_size_ok
                ),
                "loose_ok": bool(core_loose),
                "adaptive_max_area": adaptive_max_area,
                "max_candidate_component_area": max_candidate_area,
            }
        )

    elif task == RING_TASK:
        gt_components = components_no_scipy(gt_red)
        candidate_components = components_no_scipy(candidate_red)
        strict_match = match_components(
            gt_components, candidate_components, RING_STRICT_DIST
        )
        loose_match = match_components(
            gt_components, candidate_components, RING_LOOSE_DIST
        )
        core_strict = (
            len(gt_components) > 0
            and strict_match["missed"] == 0
            and strict_match["extra"] == 0
        )
        core_loose = (
            len(gt_components) > 0
            and loose_match["missed"] == 0
            and loose_match["extra"] <= 1
        )
        result.update(
            {
                "eval_type": "ring_components",
                "n_gt_components": len(gt_components),
                "n_candidate_components": len(candidate_components),
                "matched_strict": strict_match["matched"],
                "missed_strict": strict_match["missed"],
                "extra_strict": strict_match["extra"],
                "mean_distance_strict": float(np.mean(strict_match["distances"]))
                if strict_match["distances"]
                else np.nan,
                "matched_loose": loose_match["matched"],
                "missed_loose": loose_match["missed"],
                "extra_loose": loose_match["extra"],
                "mean_distance_loose": float(np.mean(loose_match["distances"]))
                if loose_match["distances"]
                else np.nan,
                "core_strict": bool(core_strict),
                "core_loose": bool(core_loose),
                "strict_preserved": bool(
                    core_strict and result["black_f1"] >= PRESERVATION_THRESHOLD
                ),
                "strict_full": bool(
                    core_strict
                    and result["black_f1"] >= PRESERVATION_THRESHOLD
                    and canvas_size_ok
                ),
                "loose_ok": bool(core_loose),
            }
        )

    elif task in BLANK_TASKS:
        strict_control = (
            result["candidate_red_pixels"] <= 25
            and result["structure_f1"] >= 0.90
        )
        loose_control = (
            result["candidate_red_pixels"] <= 150
            and result["structure_f1"] >= 0.75
        )
        result.update(
            {
                "eval_type": "no_edit_control",
                "core_strict": bool(result["candidate_red_pixels"] <= 25),
                "core_loose": bool(result["candidate_red_pixels"] <= 150),
                "strict_preserved": bool(strict_control),
                "strict_full": bool(strict_control and canvas_size_ok),
                "loose_ok": bool(loose_control),
            }
        )

    elif task in ANSWER_TASKS:
        gt_bbox = bbox_from_mask(gt_red)

        if gt_bbox is None:
            inside_red = 0
            outside_red = int(candidate_red.sum())
            proxy_strict = (
                outside_red <= 25
                and result["structure_f1"] >= 0.90
                and canvas_size_ok
            )
            proxy_loose = (
                outside_red <= 150 and result["structure_f1"] >= 0.75
            )
        else:
            x1, y1, x2, y2 = gt_bbox
            height, width = gt_red.shape
            x_start = max(0, x1 - ANSWER_PADDING_PX)
            y_start = max(0, y1 - ANSWER_PADDING_PX)
            x_end = min(width - 1, x2 + ANSWER_PADDING_PX)
            y_end = min(height - 1, y2 + ANSWER_PADDING_PX)

            answer_region = np.zeros_like(gt_red, dtype=bool)
            answer_region[y_start : y_end + 1, x_start : x_end + 1] = True

            inside_red = int(np.logical_and(candidate_red, answer_region).sum())
            outside_red = int(np.logical_and(candidate_red, ~answer_region).sum())
            proxy_strict = (
                result["red_dice"] >= 0.35
                and inside_red >= 20
                and outside_red <= 250
                and result["structure_f1"] >= 0.75
                and canvas_size_ok
            )
            proxy_loose = (
                inside_red >= 20
                and outside_red <= 1000
                and result["structure_f1"] >= 0.60
            )

        result.update(
            {
                "eval_type": "symbol_proxy",
                "answer_region_red_pixels": inside_red,
                "outside_answer_red_pixels": outside_red,
                "proxy_strict": bool(proxy_strict),
                "proxy_loose": bool(proxy_loose),
            }
        )

    else:
        raise ValueError(f"Unknown WISRD task: {task}")

    proxy_strict = result["proxy_strict"]
    proxy_loose = result["proxy_loose"]
    result["auto_strict"] = bool(
        proxy_strict if not pd.isna(proxy_strict) else result["strict_full"]
    )
    result["auto_loose"] = bool(
        proxy_loose if not pd.isna(proxy_loose) else result["loose_ok"]
    )
    result["format_ok"] = canvas_size_ok
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metadata", type=Path, required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--candidates-dir", type=Path)
    group.add_argument("--use-gt-as-candidates", action="store_true")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    rows: list[dict[str, Any]] = []
    for line in args.metadata.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        candidate_path = (
            resolve_path(args.metadata, str(item["gt_path"]))
            if args.use_gt_as_candidates
            else resolve_candidate(item, args.candidates_dir)
        )
        if candidate_path is None:
            rows.append(
                {
                    "id": item["id"],
                    "task": item["task"],
                    "format_ok": False,
                    "auto_strict": False,
                    "auto_loose": False,
                    "proxy_strict": False,
                    "proxy_loose": False,
                    "error": "candidate_not_found",
                }
            )
            continue
        try:
            rows.append(score_item(item, args.metadata, candidate_path))
        except Exception as exception:
            rows.append(
                {
                    "id": item["id"],
                    "task": item["task"],
                    "candidate_path": str(candidate_path),
                    "format_ok": False,
                    "auto_strict": False,
                    "auto_loose": False,
                    "proxy_strict": False,
                    "proxy_loose": False,
                    "error": f"{type(exception).__name__}: {exception}",
                }
            )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(args.out, index=False)
    print(f"Scored {len(rows)} outputs -> {args.out}")


if __name__ == "__main__":
    main()
