# /// script
# requires-python = ">=3.11"
# dependencies = ["openpyxl", "pdfplumber"]
# ///
"""All MENA and Eurasia rent rows in one table, and one sources list.

Written by AI on 2026.11.17 by model claude sonnet 5.5, for the Enough site.

Joins the curated rows and every script in this folder. Where two sources give the same place, the
earlier one in PRIORITY wins (the others stay in the notes as cross-checks).

Run: uv run tools/world/rent/mena-eurasia-build.py > rent-two-bedroom.mena-eurasia.csv
     uv run tools/world/rent/mena-eurasia-build.py --sources > sources.mena-eurasia.csv
"""

import csv
import importlib.util
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
COLUMNS = ["place_code", "amount", "currency", "unit", "period", "measured_for", "source_id", "note"]
SOURCE_COLUMNS = ["source_id", "publisher", "title", "url", "licence", "retrieved", "period", "note"]
PRIORITY = ["mena-eurasia-il-cbs", "mena-eurasia-rosstat", "mena-eurasia-mubawab", "mena-eurasia-realtby", "mena-eurasia-opensooq"]


def load(name: str):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), HERE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    curated = list(csv.DictReader(open(HERE / "mena-eurasia.curated.csv", encoding="utf-8")))
    modules = [load(name) for name in PRIORITY]
    if "--sources" in sys.argv:
        out = csv.DictWriter(sys.stdout, fieldnames=SOURCE_COLUMNS)
        out.writeheader()
        out.writerows(csv.DictReader(open(HERE / "mena-eurasia.sources.csv", encoding="utf-8")))
        for module in modules:
            out.writerows(module.SOURCES)
        return
    seen, rows = set(), []
    for row in curated + [r for module in modules for r in module.rows()]:
        if row["place_code"] not in seen:
            seen.add(row["place_code"])
            rows.append({k: row[k] for k in COLUMNS})
    out = csv.DictWriter(sys.stdout, fieldnames=COLUMNS)
    out.writeheader()
    out.writerows(rows)


if __name__ == "__main__":
    main()
