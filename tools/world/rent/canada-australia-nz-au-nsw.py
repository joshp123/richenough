#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = ["openpyxl"]
# ///
"""New South Wales: median weekly rent of two-bedroom flats/units on NEW bonds, from the NSW Rent and Sales Report.

Written by AI on 2026.11.17 by model claude sonnet 5.5.

Source: NSW Department of Communities and Justice (DCJ), "Rent and Sales Report", rent tables (Excel), sheet "LGA".
https://dcj.nsw.gov.au/about-us/families-and-communities-statistics/housing-rent-and-sales/rent-and-sales-report.html
Built from every new private-market rental bond lodged with NSW Fair Trading in the quarter, by tenancy start. We read
the "Flat/Unit, 2 Bedrooms" rows: the state total (AU-NSW) and one local government area (LGA) for each city.
Median weekly rent for new bonds, converted to monthly by x 52 / 12. An LGA needs 30+ new bonds in the quarter
(the report marks 30 or fewer "s" and 10 or fewer "-").
The page is scraped for the latest "rent-tables-*.xlsx" link; the file is saved in cache/au-nsw-rent-sales/.
"""

import csv
import pathlib
import re
import sys
import urllib.parse
import urllib.request

import openpyxl

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from places import city_code  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[3]
CACHE = REPO / "cache" / "au-nsw-rent-sales"
PAGE = "https://dcj.nsw.gov.au/about-us/families-and-communities-statistics/housing-rent-and-sales/rent-and-sales-report.html"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
SOURCE_ID = "au-nsw-rent-sales"
PERIOD = "2026-Q2"
COLUMNS = ["place_code", "amount", "currency", "unit", "period", "measured_for", "source_id", "note"]

SOURCES = [{
    "source_id": SOURCE_ID,
    "publisher": "NSW Department of Communities and Justice (DCJ)",
    "title": "Rent and Sales Report: rent tables, June 2026 quarter (Table 1, weekly rent statistics by local government area)",
    "url": PAGE,
    "licence": "free to read, no licence stated on the DCJ download page",
    "retrieved": "2026-11-17",
    "period": PERIOD,
    "note": "Median weekly rent of new private bonds, April to June 2026, Flat/Unit with 2 bedrooms, by LGA. Private market only; excludes social housing.",
}]

# GeoNames name (NSW = admin1 02), DCJ local government area, label for measured_for
CITIES = [
    ("Sydney", "Sydney", "City of Sydney local government area (the CBD and inner suburbs)"),
    ("Newcastle", "Newcastle", "City of Newcastle local government area"),
    ("Wollongong", "Wollongong", "City of Wollongong local government area"),
    ("Central Coast", "Central Coast", "Central Coast local government area (Gosford, Wyong and surrounds)"),
    ("Parramatta", "Parramatta", "City of Parramatta local government area"),
    ("Coffs Harbour", "Coffs Harbour", "Coffs Harbour local government area"),
    ("Tamworth", "Tamworth Regional", "Tamworth Regional local government area"),
    ("Port Macquarie", "Port Macquarie-Hastings", "Port Macquarie-Hastings local government area"),
    ("Maitland", "Maitland", "Maitland local government area"),
    ("Orange", "Orange", "Orange local government area"),
    ("Bathurst", "Bathurst Regional", "Bathurst Regional local government area"),
]


def download() -> pathlib.Path:
    CACHE.mkdir(parents=True, exist_ok=True)
    existing = sorted(CACHE.glob("rent-tables-*.xlsx"))
    if existing:
        return existing[-1]
    req = urllib.request.Request(PAGE, headers={"User-Agent": UA})
    page = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")
    m = re.search(r'href="([^"]*/rent-tables-[^"]+\.xlsx)"', page)
    if not m:
        raise RuntimeError("no rent-tables xlsx link on the DCJ page")
    dest = CACHE / pathlib.PurePosixPath(m.group(1)).name
    dest.write_bytes(urllib.request.urlopen(urllib.request.Request(urllib.parse.urljoin(PAGE, m.group(1)), headers={"User-Agent": UA}), timeout=180).read())
    return dest


def flat_two_bed() -> dict[str, tuple[float, int | None]]:
    """LGA name (or 'Total' for the state) -> (median weekly rent, new bonds lodged or None if marked s or -)."""
    wb = openpyxl.load_workbook(download(), data_only=True, read_only=True)
    out = {}
    for r in wb["LGA"].iter_rows(values_only=True):
        if not r or r[4] != "Flat/Unit" or r[5] != "2 Bedrooms" or (r[0], r[1], r[2]) != ("Total", "Total", "Total"):
            continue
        median = str(r[7]).replace(",", "")
        bonds = str(r[9]).replace(",", "")
        if re.fullmatch(r"\d+(\.\d+)?", median):
            out[r[3]] = (float(median), int(bonds) if bonds.isdigit() else None)
    return out


def monthly(weekly: float) -> float:
    return round(weekly * 52 / 12)


def rows() -> list[dict]:
    data = flat_two_bed()
    base = {"currency": "AUD", "unit": "per_month", "period": PERIOD, "source_id": SOURCE_ID}
    out = []
    w, n = data["Total"]
    out.append({**base, "place_code": "AU-NSW", "amount": monthly(w),
                "measured_for": "New South Wales state-wide, two-bedroom flats and units, new private bonds Apr-Jun 2026",
                "note": f"NSW DCJ Rent and Sales Report, June 2026 quarter: median weekly rent for new bonds AUD {w:.0f} from {n} bonds; x 52/12."})
    for gname, lga, label in CITIES:
        if lga not in data or data[lga][1] is None or data[lga][1] < 30:
            print(f"  skipped {gname} ({lga}): {data.get(lga)}", file=sys.stderr)
            continue
        w, n = data[lga]
        try:
            code = city_code(gname, "AU", "02")
        except KeyError:
            print(f"  no GeoNames city {gname}", file=sys.stderr)
            continue
        out.append({**base, "place_code": code, "amount": monthly(w),
                    "measured_for": f"{label}, two-bedroom flats and units, new private bonds Apr-Jun 2026",
                    "note": f"NSW DCJ Rent and Sales Report, June 2026 quarter: median weekly rent for new bonds AUD {w:.0f} from {n} bonds; x 52/12."})
    return out


if __name__ == "__main__":
    data = rows()
    w = csv.DictWriter(sys.stdout, fieldnames=COLUMNS)
    w.writeheader()
    w.writerows(data)
