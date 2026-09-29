"""Aggregate scorer rows, optionally checking the shared paper result."""
import argparse
import csv
import json
import sys
from collections import Counter
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASKS = {"line_intersections", "line_midpoint_mark", "fill_target_shape", "circled_letter_base",
         "circled_letter_allA", "circled_letter_blank", "circled_letter_blankcircle",
         "circled_letter_copy_single", "count_dots_digit", "count_dots_visual", "overlapping_shapes"}


def boolean(value):
    if value.lower() in {"true", "1"}:
        return True
    if value.lower() in {"false", "0"}:
        return False
    raise ValueError(f"Expected a boolean score, got {value!r}")


def summarize(path, model=None):
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    if not rows or len({row["id"] for row in rows}) != len(rows):
        raise ValueError("Score file is empty or contains duplicate IDs")
    if any(row.get("error", "").strip() for row in rows):
        raise ValueError("Score file contains image errors; repair coverage before aggregation")
    result = {"n": len(rows)}
    rates = {}
    for metric in ("auto_strict", "auto_loose"):
        passed = sum(boolean(row[metric]) for row in rows)
        rate = Decimal(passed) * 100 / Decimal(len(rows))
        rates[metric] = rate.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
        result[metric + "_passes"] = passed
        result[metric + "_percent"] = float(rate)
        result[metric + "_reported_precision"] = str(rates[metric])
    if model:
        counts = Counter((row["task"], row["var_id"]) for row in rows)
        expected_counts = Counter({(task, variant): 50 for task in TASKS for variant in ("V0", "V1", "V2", "V3")})
        if counts != expected_counts:
            raise ValueError("Paper comparison requires 2,200 rows: 50 in every one of 11 × 4 task/condition cells")
        with (ROOT / "results" / "reported_shared_v0_v3.csv").open(newline="") as stream:
            expected = {row["model_id"]: row for row in csv.DictReader(stream)}
        if model not in expected:
            raise ValueError("Unknown model ID; see results/reported_shared_v0_v3.csv")
        matches = all(rates[metric] == Decimal(expected[model][metric + "_percent"]) for metric in rates)
        result.update(model_id=model, matches_reported_rounded_values=matches)
        if not matches:
            raise ValueError(f"Paper-value mismatch: {json.dumps(result)}")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scores", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--model", help="Check the shared subset against this reported model ID")
    args = parser.parse_args()
    result = summarize(args.scores, args.model)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError) as error:
        sys.exit(str(error))
