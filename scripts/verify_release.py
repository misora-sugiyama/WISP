"""Check distribution file hashes and the unchanged reported scorer."""
import hashlib
from pathlib import Path

from evaluate import ROOT, SCORER_SHA256


def main():
    manifest = ROOT / "SHA256SUMS.txt"
    checked = 0
    for line in manifest.read_text(encoding="utf-8").splitlines():
        expected, name = line.split("  ", 1)
        path = ROOT / name
        if not path.resolve().is_relative_to(ROOT.resolve()):
            raise ValueError("Invalid manifest path")
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f"Checksum mismatch: {name}")
        checked += 1
    if hashlib.sha256((ROOT / "evaluator/score_wisrd.py").read_bytes()).hexdigest() != SCORER_SHA256:
        raise ValueError("Scorer does not match the paper freeze")
    print(f"PASS: {checked} distribution hashes and frozen scorer hash")


if __name__ == "__main__":
    main()
