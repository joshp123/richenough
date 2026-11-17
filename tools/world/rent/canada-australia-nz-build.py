#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = ["openpyxl", "shapely", "pandas", "xlrd"]
# ///
"""Rebuild the Canada, Australia and New Zealand part of the rent-two-bedroom table from the cache.

Written by AI on 2026.11.17 by model claude sonnet 5.5.

Runs every canada-australia-nz-*.py source script (each downloads its source into cache/ if missing), adds the hand-typed rows
in canada-australia-nz.curated.csv (Pacific countries and Perth), checks them, and writes next to this file:
  canada-australia-nz.table.csv        place_code,amount,currency,unit,period,measured_for,source_id,note
  canada-australia-nz.sources.all.csv  source_id,publisher,title,url,licence,retrieved,period,note
Usage: uv run tools/world/rent/canada-australia-nz-build.py
"""

import csv
import importlib.util
import pathlib
import sys

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
TABLE = ["place_code", "amount", "currency", "unit", "period", "measured_for", "source_id", "note"]
SOURCE = ["source_id", "publisher", "title", "url", "licence", "retrieved", "period", "note"]


def load(path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(path.stem.replace("-", "_"), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    rows, sources = [], []
    for path in sorted(HERE.glob("canada-australia-nz-*.py")):
        if path.name == pathlib.Path(__file__).name:
            continue
        module = load(path)
        got = module.rows()
        print(f"{path.name}: {len(got)} rows", file=sys.stderr)
        rows += got
        sources += module.SOURCES
    with open(HERE / "canada-australia-nz.curated.csv", encoding="utf-8") as f:
        curated = list(csv.DictReader(f))
    print(f"canada-australia-nz.curated.csv: {len(curated)} rows", file=sys.stderr)
    rows += curated
    with open(HERE / "canada-australia-nz.sources.csv", encoding="utf-8") as f:
        sources += list(csv.DictReader(f))

    seen = set()
    for r in rows:
        key = r["place_code"]
        assert key not in seen, f"duplicate place_code {key}"
        seen.add(key)
        assert float(r["amount"]) > 0 and r["currency"] and r["measured_for"] and r["source_id"] and r["period"], r
    known = {s["source_id"] for s in sources}
    missing = {r["source_id"] for r in rows} - known
    assert not missing, f"rows cite sources not listed: {missing}"

    with open(HERE / "canada-australia-nz.table.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=TABLE, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    with open(HERE / "canada-australia-nz.sources.all.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=SOURCE)
        w.writeheader()
        w.writerows(sources)
    print(f"wrote {len(rows)} rows, {len(sources)} sources", file=sys.stderr)


if __name__ == "__main__":
    main()
