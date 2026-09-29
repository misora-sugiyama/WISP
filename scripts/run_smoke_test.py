"""Exercise frozen examples, actual no-edit candidates, and missing-output rejection."""
import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from evaluate import ROOT, run_evaluation
from summarize_scores import summarize


def main():
    metadata = ROOT / "examples" / "generated_sample" / "items.jsonl"
    items = [json.loads(line) for line in metadata.read_text().splitlines() if line.strip()]
    if len(items) != 44:
        raise AssertionError("Bundled smoke sample must contain 44 records")
    with TemporaryDirectory(prefix="wisp-smoke-") as temporary:
        temp = Path(temporary)
        gt_scores = temp / "gt.csv"
        subprocess.run([sys.executable, str(ROOT / "evaluator" / "score_wisrd.py"),
                        "--metadata", str(metadata), "--use-gt-as-candidates", "--out", str(gt_scores)], check=True)
        gt = summarize(gt_scores)
        if (gt["auto_strict_passes"], gt["auto_loose_passes"]) != (44, 44):
            raise AssertionError("Canonical GT self-check failed")
        candidates = temp / "no_edit"
        candidates.mkdir()
        for item in items:
            shutil.copyfile(metadata.parent / item["input_path"], candidates / (item["id"] + ".png"))
        scores = temp / "no_edit.csv"
        run_evaluation(metadata, candidates, scores)
        with scores.open(newline="") as stream:
            rows = list(csv.DictReader(stream))
        controls = {"circled_letter_blank", "circled_letter_blankcircle"}
        for row in rows:
            expected = row["task"] in controls
            if (row["auto_strict"] == "True") != expected or (row["auto_loose"] == "True") != expected:
                raise AssertionError(f"Unexpected no-edit decision: {row['id']}")
        (candidates / (items[0]["id"] + ".png")).unlink()
        try:
            run_evaluation(metadata, candidates, temp / "missing.csv")
        except ValueError:
            pass
        else:
            raise AssertionError("Missing candidate was not rejected")
    print("PASS: 44 GT self-checks, 44 actual no-edit decisions, missing-candidate rejection")
    print("This is a software check, not reproduction of the 13,200 frozen model outputs.")


if __name__ == "__main__":
    main()
