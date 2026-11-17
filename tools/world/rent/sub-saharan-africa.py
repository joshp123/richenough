#!/usr/bin/env python3
"""Build tools/world/rent/sub-saharan-africa.table.csv (not data/tables/: the world-data owner merges) and the sources list for Sub-Saharan Africa plus the island states.

Combines the portal scripts in this folder (each downloads its pages into cache/ if missing) with the hand-read
rows in sub-saharan-africa.curated.csv. Where a country's best figure is for its main city, the same figure is also
written under the country code with a measured_for that says it is the city. Run: python3 -I sub-saharan-africa.py
"""

import csv
import importlib.util
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[2]
COLUMNS = ["place_code", "amount", "currency", "unit", "period", "measured_for", "source_id", "note"]
SOURCE_COLUMNS = ["source_id", "publisher", "title", "url", "licence", "retrieved", "period", "note"]


def load(name: str):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), HERE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# GeoNames city code -> (country ISO code, the city's name for the country row)
MAIN_CITY = {
    "CITY-184745": ("KE", "Nairobi"),
    "CITY-909137": ("ZM", "Lusaka"),
    "CITY-933773": ("BW", "Gaborone"),
    "CITY-1040652": ("MZ", "Maputo"),
    "CITY-1070940": ("MG", "Antananarivo"),
    "CITY-232422": ("UG", "Kampala"),
    "CITY-160263": ("TZ", "Dar es Salaam"),
    "CITY-344979": ("ET", "Addis Ababa"),
    "CITY-2293538": ("CI", "Abidjan"),
    "CITY-2394819": ("BJ", "Cotonou"),
    "CITY-2314302": ("CD", "Kinshasa"),
    "CITY-2232593": ("CM", "Douala"),
    "CITY-2332459": ("NG", "Lagos"),
    "CITY-2253354": ("SN", "Dakar"),
    "CITY-2306104": ("GH", "Accra"),
    "CITY-202061": ("RW", "Kigali"),
}
# Rows kept from the scripts whose pages cover more places than we want.
KEEP_EXPAT = {"CITY-1070940", "CITY-2293538", "CITY-2394819"}
KEEP_AFRICANVESTOR = {"CITY-232422", "CITY-160263", "CITY-344979", "CITY-2314302", "CITY-2232593"}


def collect() -> tuple[list[dict], list[dict]]:
    rows, sources = [], []
    for name, keep in [
        ("sub-saharan-africa-property24", None),
        ("sub-saharan-africa-property24-network", None),
        ("sub-saharan-africa-propertycloud", None),
        ("sub-saharan-africa-expat-com", KEEP_EXPAT),
        ("sub-saharan-africa-africanvestor", KEEP_AFRICANVESTOR),
    ]:
        module = load(name)
        sources += module.SOURCES
        rows += [r for r in module.rows() if keep is None or r["place_code"] in keep]
    with open(HERE / "sub-saharan-africa.curated.csv", encoding="utf-8") as f:
        rows += [{c: r[c] for c in COLUMNS} for r in csv.DictReader(f)]
    with open(HERE / "sub-saharan-africa.sources.csv", encoding="utf-8") as f:
        sources += list(csv.DictReader(f))
    return rows, sources


def with_country_rows(rows: list[dict]) -> list[dict]:
    out = list(rows)
    for r in rows:
        if r["place_code"] in MAIN_CITY:
            iso, city = MAIN_CITY[r["place_code"]]
            out.append({**r, "place_code": iso, "measured_for": f"{r['measured_for']} (main city only: {city}; used as the country's figure)"})
    return out


if __name__ == "__main__":
    rows, sources = collect()
    if "--sources" in sys.argv:
        w = csv.DictWriter(sys.stdout, fieldnames=SOURCE_COLUMNS)
        w.writeheader()
        w.writerows(sources)
        sys.exit()
    rows = with_country_rows(rows)
    target = HERE / "sub-saharan-africa.table.csv"
    with open(target, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} rows to {target}", file=sys.stderr)
