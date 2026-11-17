#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = ["openpyxl"]
# ///
"""South Australia: two-bedroom flat/unit rent for a new let, from the state's rental bond records, April-June 2026.

Written by AI on 2026.11.17 by model claude sonnet 5.5 (sub-agent).

Source: "Private Rent Report" (quarterly workbook), South Australian Housing Trust, built from the rental bond data set
of Consumer and Business Services (CBS). Every private tenancy in SA needs a bond lodged with CBS, so the figures count
bonds lodged in the quarter: new tenancies, not sitting tenants.
https://data.sa.gov.au/data/dataset/private-rent-report  (the data.gov.au copy of this dataset lags by two quarters;
this script uses the data.sa.gov.au file.)
Download goes to cache/au-sa-private-rent/ once; delete the folder to fetch again.

What each row measures: the median WEEKLY rent of bonds lodged for two-bedroom "Flats/Units" (houses excluded) in
April-June 2026, converted to a month as weekly x 52 / 12. Bond counts are rounded to the nearest 5; cells of 1 to 5 bonds
are suppressed by the publisher.
  AU-SA          all of South Australia ("Grand Total" row, Region sheet).
  Adelaide       City of Adelaide council area (the CBD and North Adelaide), the central zone, "Adelaide (C) Total" in the
                 SLA sheet. Greater Adelaide ("Metro Total", Region sheet) is in the note.
  Mount Gambier  City of Mount Gambier council area, "Mount Gambier (C) Total" in the SLA sheet.

Run directly to print the rows as CSV.
"""

import csv
import pathlib
import sys
import urllib.request

import openpyxl

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from places import city_code  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[3]
SOURCE_ID = "au-sa-private-rent"
CACHE = REPO / "cache" / SOURCE_ID
FILE = "private-rental-report-2026-06.xlsx"
URL = ("https://data.sa.gov.au/data/dataset/8eb97a72-9919-448b-8de6-fc1530b3f7ec/resource/"
       "b4aa86f1-7efa-4690-9793-bd36df97ad29/download/" + FILE)
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
PERIOD = "2026-Q2"

SOURCES = [{
    "source_id": SOURCE_ID,
    "publisher": "South Australian Housing Trust, from the rental bond data set of Consumer and Business Services (Government of South Australia)",
    "title": "Private Rental Report 2026-06 (bonds lodged 1 April - 30 June 2026), Region and SLA sheets",
    "url": "https://data.sa.gov.au/data/dataset/private-rent-report",
    "licence": "Creative Commons Attribution 3.0 Australia",
    "retrieved": "2026-11-17",
    "period": PERIOD,
    "note": "Median weekly rent of bonds lodged in the quarter (new tenancies) by dwelling type and bedrooms. Excludes cancelled or unlodged bonds. Counts rounded to 5; 1-5 suppressed.",
}]

# column offsets in a sheet row: label, then (count, median) pairs for Flats/Units with 1, 2, 3, 4+ bedrooms
TWO_BED_COUNT, TWO_BED_MEDIAN = 3, 4


def download() -> pathlib.Path:
    path = CACHE / FILE
    if not path.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(URL, headers={"User-Agent": UA})
        path.write_bytes(urllib.request.urlopen(req, timeout=120).read())
    return path


def two_bed(wb, sheet: str, label: str) -> tuple[float, int | str]:
    """Median weekly rent and bond count of two-bedroom flats/units in the row called `label`."""
    for r in wb[sheet].iter_rows(min_row=10, values_only=True):
        if r[0] == label:
            count, median = r[TWO_BED_COUNT], r[TWO_BED_MEDIAN]
            if not isinstance(median, (int, float)):
                raise ValueError(f"{label!r}: no two-bedroom flat median ({r[:5]})")
            return float(median), count
    raise KeyError(f"{label!r} not in sheet {sheet}")


def monthly(weekly: float) -> int:
    return round(weekly * 52 / 12)


def row(code: str, weekly: float, count, measured: str, extra: str = "") -> dict:
    return {
        "place_code": code, "amount": monthly(weekly), "currency": "AUD", "unit": "per_month", "period": PERIOD,
        "measured_for": measured, "source_id": SOURCE_ID,
        "note": (f"Median weekly rent ${weekly:,.2f} x 52 / 12. Based on about {count} two-bedroom flat/unit bonds lodged "
                 f"1 April - 30 June 2026 (new tenancies, counts rounded to 5). SA Private Rental Report 2026-06. {extra}").strip(),
    }


def rows() -> list[dict]:
    wb = openpyxl.load_workbook(download(), data_only=True)
    metro_w, metro_n = two_bed(wb, "Region", "Metro Total")
    out = []
    w, n = two_bed(wb, "Region", "Grand Total")
    out.append(row("AU-SA", w, n, "South Australia, whole state, two-bedroom flats/units, bonds lodged in the quarter (new tenancies)"))
    w, n = two_bed(wb, "SLA", "Adelaide (C) Total")
    out.append(row(city_code("Adelaide", "AU", "05"), w, n,
                   "Adelaide, City of Adelaide council area (CBD and North Adelaide), two-bedroom flats/units, bonds lodged in the quarter (new tenancies)",
                   f"Greater Adelaide (metropolitan Adelaide, four regions) is ${metro_w:,.2f} a week from about {metro_n} bonds."))
    w, n = two_bed(wb, "SLA", "Mount Gambier (C) Total")
    out.append(row(city_code("Mount Gambier", "AU", "05"), w, n,
                   "Mount Gambier, City of Mount Gambier council area, two-bedroom flats/units, bonds lodged in the quarter (new tenancies)"))
    return out


if __name__ == "__main__":
    data = rows()
    w = csv.DictWriter(sys.stdout, fieldnames=list(data[0]))
    w.writeheader()
    w.writerows(data)
