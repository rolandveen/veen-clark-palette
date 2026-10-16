"""Compare scientific CSV/JSON data, allowing small floating-point differences."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path


def equivalent(left, right, location: str) -> None:
    if isinstance(left, dict) and isinstance(right, dict):
        if left.keys() != right.keys():
            raise ValueError(f"Different fields: {location}")
        for key in left:
            equivalent(left[key], right[key], f"{location}/{key}")
    elif isinstance(left, list) and isinstance(right, list):
        if len(left) != len(right):
            raise ValueError(f"Different row counts: {location}")
        for index, (first, second) in enumerate(zip(left, right)):
            equivalent(first, second, f"{location}/{index}")
    elif left != right:
        try:
            matches = math.isclose(float(left), float(right), rel_tol=1e-9, abs_tol=1e-9)
        except (TypeError, ValueError):
            matches = False
        if not matches:
            raise ValueError(f"Different data at {location}: {left!r} != {right!r}")


def compare(baseline: Path, current: Path) -> None:
    def inventory(root: Path) -> set[Path]:
        return {path.relative_to(root) for path in root.glob("*/data/*")
                if path.suffix in (".csv", ".json")}
    paths = inventory(baseline)
    if not paths or paths != inventory(current):
        raise ValueError("Scientific data file inventories differ or are empty")
    for path in sorted(paths):
        if path.suffix == ".csv":
            with (baseline / path).open(newline="", encoding="utf-8") as stream:
                left = list(csv.DictReader(stream))
            with (current / path).open(newline="", encoding="utf-8") as stream:
                right = list(csv.DictReader(stream))
        else:
            left = json.loads((baseline / path).read_text(encoding="utf-8"))
            right = json.loads((current / path).read_text(encoding="utf-8"))
        equivalent(left, right, str(path))
    print(f"All {len(paths)} scientific data files agree (tolerance 1e-9).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("current", type=Path)
    args = parser.parse_args()
    compare(args.baseline, args.current)
