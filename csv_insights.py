#!/usr/bin/env python3
"""Tiny CSV profiler: row counts and numeric column statistics."""
from __future__ import annotations

import argparse
import csv
import statistics
import sys
from pathlib import Path


def numeric(value: str) -> float | None:
    try:
        return float(value.replace(",", "").strip())
    except (ValueError, AttributeError):
        return None


def profile(path: Path) -> tuple[int, int, dict[str, list[float]]]:
    rows = 0
    empty = 0
    columns: dict[str, list[float]] = {}
    with path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            rows += 1
            for key, value in row.items():
                if value is None or not str(value).strip():
                    empty += 1
                    continue
                number = numeric(str(value))
                if number is not None:
                    columns.setdefault(key or "", []).append(number)
    return rows, empty, columns


def main() -> int:
    parser = argparse.ArgumentParser(description="Tiny CSV profiler: row counts and numeric column statistics.")
    parser.add_argument("path", type=Path, help="CSV file to inspect")
    parser.add_argument("--limit", type=int, default=150)
    args = parser.parse_args()
    if not args.path.is_file():
        parser.error(f"no such file: {args.path}")
    rows, empty, columns = profile(args.path)
    print(f"file: {args.path}")
    print(f"rows: {rows} | empty cells: {empty}")
    if not columns:
        print("no numeric columns found")
        return 0
    print(f"{'column':<20}{'count':>8}{'min':>10}{'max':>10}{'mean':>10}")
    for name, values in sorted(columns.items()):
        shown = values[: args.limit]
        print(
            f"{name[:19]:<20}{len(values):>8}"
            f"{min(shown):>10.2f}{max(shown):>10.2f}"
            f"{statistics.fmean(shown):>10.2f}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
