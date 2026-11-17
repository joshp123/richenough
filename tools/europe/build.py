# /// script
# requires-python = ">=3.12"
# dependencies = ["pandas>=2.2", "openpyxl", "xlrd", "odfpy", "pyxlsb", "pdfplumber", "lxml", "requests"]
# ///
"""Rebuild Europe's tables from the raw sources: `uv run tools/europe/build.py [component ...]`.

Downloads go to cache/<source_id>/ once; delete a folder there to fetch it again.
Writes data/tables/<component>.europe.csv and this area's rows of data/sources.csv.
"""

from __future__ import annotations

import csv
import importlib
import math
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import common  # noqa: E402

RENT_COUNTRIES = ["al", "at", "be", "bg", "ch", "cy", "cz", "de", "dk", "ee", "es", "fi", "fr", "gb", "gr", "hr", "hu",
                  "ie", "is", "it", "li", "lt", "lu", "lv", "me", "mk", "mt", "nl", "no", "pl", "pt", "ro", "rs", "se",
                  "si", "sk", "tr", "ua", "xk"]

COMPONENTS = {
    "rent-two-bedroom": [f"rent.{cc}" for cc in RENT_COUNTRIES],
    "price-level-everyday": ["price_level"],
    "car": ["car"],
    "housekeeper-wage": ["housekeeper"],
    "health-cover": ["health"],
}


def load_modules(names: list[str]):
    for name in names:
        try:
            yield name, importlib.import_module(name)
        except ModuleNotFoundError as error:
            if error.name == name:
                print(f"  missing module {name}", file=sys.stderr)
                continue
            raise


def check(component: str, rows: list[dict], module: str) -> list[dict]:
    known = set(common.nuts_regions()["nuts"].map(common.place)) | set(common.nuts_regions()["iso"])
    good = []
    for r in rows:
        problems = []
        if r["place_code"] not in known:
            problems.append(f"unknown place {r['place_code']}")
        if not isinstance(r["amount"], (int, float)) or math.isnan(r["amount"]) or r["amount"] < 0:
            problems.append(f"bad amount {r['amount']}")
        if not r["source_id"] or not r["measured_for"] or not r["period"]:
            problems.append("empty source_id, measured_for or period")
        if problems:
            print(f"  {module}: dropped {r['place_code']}: {'; '.join(problems)}", file=sys.stderr)
        else:
            good.append(r)
    return good


def main(selected: list[str]) -> int:
    common.TABLES.mkdir(parents=True, exist_ok=True)
    sources: dict[str, dict] = {}
    failed = False
    for component, modules in COMPONENTS.items():
        if selected and component not in selected:
            continue
        rows: list[dict] = []
        for name, module in load_modules(modules):
            try:
                module_rows = check(component, list(module.rows()), name)
            except Exception:
                failed = True
                print(f"  {name} failed:\n{traceback.format_exc()}", file=sys.stderr)
                continue
            rows += module_rows
            for s in getattr(module, "SOURCES", []):
                sources[s["source_id"]] = s
            print(f"  {name}: {len(module_rows)} rows", file=sys.stderr)
        seen = set()
        for r in rows:
            if r["place_code"] in seen:
                print(f"  {component}: duplicate {r['place_code']}", file=sys.stderr)
                failed = True
            seen.add(r["place_code"])
        rows.sort(key=lambda r: r["place_code"])
        for r in rows:
            r["amount"] = round(r["amount"], 4 if r["unit"].startswith("index") else 2)
        out = common.TABLES / f"{component}.europe.csv"
        with out.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=common.COLUMNS, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        print(f"{component}: {len(rows)} rows -> {out.relative_to(common.ROOT)}", file=sys.stderr)
    write_sources(sources)
    return 1 if failed else 0


def write_sources(mine: dict[str, dict]) -> None:
    """Replace this area's rows in data/sources.csv, keeping every other agent's rows as they are."""
    path = common.ROOT / "data" / "sources.csv"
    with path.open(newline="") as f:
        existing = list(csv.DictReader(f))
    kept = [r for r in existing if r["source_id"] not in mine]
    merged = kept + sorted(mine.values(), key=lambda r: r["source_id"])
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=common.SOURCE_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(merged)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
