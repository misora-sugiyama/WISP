"""Validate dataset/candidate coverage and run the unchanged frozen scorer."""
import argparse
import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCORER_SHA256 = "fc83bfb88a9557cd9d1d37a0b6aefaa587870c99f246fae89111430a8813025b"
EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def read_items(metadata):
    items = [json.loads(line) for line in metadata.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not items:
        raise ValueError("Metadata has no records")
    ids = [item["id"] for item in items]
    if len(ids) != len(set(ids)):
        raise ValueError("Metadata contains duplicate item IDs")
    for item in items:
        if Path(item["id"]).name != item["id"] or item["id"] in {".", ".."}:
            raise ValueError("Each item ID must be a filename stem")
        for key in ("input_path", "gt_path"):
            path = Path(item[key])
            path = path if path.is_absolute() else metadata.parent / path
            if not path.is_file():
                raise FileNotFoundError(f"{item['id']}: missing {key}: {path}")
    return items


def check_candidates(items, directory):
    index = {}
    for path in directory.iterdir():
        if path.is_file() and path.suffix.lower() in EXTENSIONS:
            index.setdefault(path.stem, []).append(path)
    for item in items:
        matches = index.get(item["id"], [])
        if len(matches) != 1:
            raise ValueError(f"{item['id']}: expected one candidate, found {len(matches)}")


def run_evaluation(metadata, candidates, out):
    scorer = ROOT / "evaluator" / "score_wisrd.py"
    if hashlib.sha256(scorer.read_bytes()).hexdigest() != SCORER_SHA256:
        raise ValueError("Frozen scorer hash differs; restore the reported scorer before evaluation")
    items = read_items(metadata)
    check_candidates(items, candidates)
    if out.exists():
        raise FileExistsError(f"Choose a new result filename; refusing to overwrite {out}")
    subprocess.run([sys.executable, str(scorer), "--metadata", str(metadata),
                    "--candidates-dir", str(candidates), "--out", str(out)], check=True)
    with out.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    if [row["id"] for row in rows] != [item["id"] for item in items]:
        raise ValueError("Scored row IDs differ from the metadata")
    errors = [row for row in rows if row.get("error", "").strip()]
    if errors:
        raise ValueError(f"{len(errors)} image scoring errors; inspect {out}")
    print(f"Validated {len(rows)} scored records")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--candidates-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    run_evaluation(args.metadata, args.candidates_dir, args.out)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError) as error:
        sys.exit(str(error))
