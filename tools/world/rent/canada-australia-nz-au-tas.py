#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = ["openpyxl"]
# ///
"""Tasmania: two-bedroom flat/unit rent for a new let, from the state's rental bond records, April-June 2026.

Written by AI on 2026.11.17 by model claude sonnet 5.5 (sub-agent).

Source: "Rental Bond and Rental Data", Department of Justice Tasmania (Consumer, Building and Occupational Services),
one Excel file a month on data.gov.au. Every private tenancy in Tasmania needs a bond lodged with the Residential Tenancy
Commissioner. Each monthly file has an "Active Bonds" sheet that lists one row per bond LODGED IN THAT MONTH (suburb,
postcode, weekly rent, bedrooms, dwelling type, private or community housing) and a "Closed Bonds" sheet (ended tenancies,
ignored here). So the Active sheet is a list of new tenancies and their asking-at-signing rent.
https://data.gov.au/data/dataset/rental-bond-and-rental-data-july-2024-to-june-2025  (series "Rental Bond and Rental Data
July 2025 to June 2026"). Downloads go to cache/au-tas-bond-data/ once; delete the folder to fetch again.

The publisher gives no median. This script computes it. What each row measures: the median WEEKLY rent of all bonds
lodged in April, May and June 2026 for PRIVATE housing (community housing excluded), with 2 bedrooms, and dwelling type
Unit, Apartment or Flat (houses, townhouses, semi-detached and terraces excluded), converted to a month as weekly x 52 / 12.
  AU-TAS     the whole state.
  Hobart     the City of Hobart council area, approximated by postcodes 7000, 7004, 7005, 7007, 7008 (Hobart, North and
             West Hobart, South Hobart, Battery Point, Sandy Bay, Dynnyrne, Mount Nelson, New Town, Lenah Valley). The
             Greater Hobart figure (five councils, postcode approximation, listed below) is in the note.
  Launceston postcodes 7248, 7249, 7250 (the urban area of Launceston).
A postcode can straddle a council boundary, so the council areas are approximate.

Run directly to print the rows as CSV.
"""

import csv
import pathlib
import statistics
import sys
import urllib.request

import openpyxl

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from places import city_code  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[3]
SOURCE_ID = "au-tas-bond-data"
CACHE = REPO / "cache" / SOURCE_ID
BASE = "https://data.gov.au/data/dataset/a5096409-4702-468e-94a7-303951b4173b/resource/"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
PERIOD = "2026-Q2"
FILES = {  # file name -> resource id on data.gov.au
    "abs-report-april-2026.xlsx": "61b9a6be-cc7a-42e1-998b-462c8251bb1d",
    "abs-report-may-2026.xlsx": "b14c5515-5eef-4f76-a6c1-30e2fd68494a",
    "abs-report-june-2026.xlsx": "8badc6fb-4796-444d-b2c2-db516dc79043",
}
FLAT_TYPES = {"Unit", "Apartment", "Flat"}

HOBART_COUNCIL = {"7000", "7004", "7005", "7007", "7008"}
# Councils of Hobart, Glenorchy, Clarence, Kingborough and Brighton, by postcode (approximate)
GREATER_HOBART = HOBART_COUNCIL | {"7009", "7010", "7011", "7012", "7015", "7016", "7017", "7018", "7019", "7020", "7021",
                                   "7023", "7024", "7025", "7030", "7050", "7052", "7053", "7054", "7055", "7170"}
LAUNCESTON = {"7248", "7249", "7250"}

SOURCES = [{
    "source_id": SOURCE_ID,
    "publisher": "Department of Justice Tasmania (Consumer, Building and Occupational Services)",
    "title": "Rental Bond and Rental Data, April, May and June 2026 monthly files, 'Active Bonds' sheet (bonds lodged in the month)",
    "url": "https://data.gov.au/data/dataset/rental-bond-and-rental-data-july-2024-to-june-2025",
    "licence": "Creative Commons Attribution 4.0 International",
    "retrieved": "2026-11-17",
    "period": PERIOD,
    "note": "One row per bond lodged in the month (new tenancies). The median is computed by this project from the rows; the publisher gives none.",
}]


def download(name: str) -> pathlib.Path:
    path = CACHE / name
    if not path.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(f"{BASE}{FILES[name]}/download/{name}", headers={"User-Agent": UA})
        path.write_bytes(urllib.request.urlopen(req, timeout=120).read())
    return path


def bonds() -> list[dict]:
    """Private-housing bonds lodged in the quarter, as dicts keyed by the sheet's column titles."""
    out = []
    for name in FILES:
        wb = openpyxl.load_workbook(download(name), data_only=True, read_only=True)
        it = wb["Active Bonds"].iter_rows(values_only=True)
        next(it)
        header = list(next(it))
        for r in it:
            if r[0]:
                out.append(dict(zip(header, r)))
    return out


def two_bed_flats(rows_: list[dict], postcodes: set[str] | None = None) -> list[float]:
    return [float(b["Weekly Rent"]) for b in rows_
            if b["Housing Type"] == "Private housing" and b["Number of Bedrooms"] == 2 and b["Dwelling / Premises Type"] in FLAT_TYPES
            and (postcodes is None or str(b["Postcode"]) in postcodes)]


def monthly(weekly: float) -> int:
    return round(weekly * 52 / 12)


def row(code: str, rents: list[float], measured: str, extra: str = "") -> dict:
    weekly = statistics.median(rents)
    return {
        "place_code": code, "amount": monthly(weekly), "currency": "AUD", "unit": "per_month", "period": PERIOD,
        "measured_for": measured, "source_id": SOURCE_ID,
        "note": (f"Median weekly rent ${weekly:,.2f} x 52 / 12, computed from {len(rents)} private two-bedroom unit/apartment/flat "
                 f"bonds lodged April-June 2026 (new tenancies), Tasmanian rental bond data. {extra}").strip(),
    }


def rows() -> list[dict]:
    b = bonds()
    hobart, greater = two_bed_flats(b, HOBART_COUNCIL), two_bed_flats(b, GREATER_HOBART)
    return [
        row("AU-TAS", two_bed_flats(b), "Tasmania, whole state, private two-bedroom flats/units/apartments, bonds lodged in the quarter (new tenancies)"),
        row(city_code("Hobart", "AU", "06"), hobart,
            "Hobart, City of Hobart council area (postcodes 7000, 7004, 7005, 7007, 7008), private two-bedroom flats/units/apartments, bonds lodged in the quarter (new tenancies)",
            f"Greater Hobart (five councils, by postcode) median is ${statistics.median(greater):,.2f} a week from {len(greater)} bonds."),
        row(city_code("Launceston", "AU", "06"), two_bed_flats(b, LAUNCESTON),
            "Launceston, urban area (postcodes 7248, 7249, 7250), private two-bedroom flats/units/apartments, bonds lodged in the quarter (new tenancies)"),
    ]


if __name__ == "__main__":
    data = rows()
    w = csv.DictWriter(sys.stdout, fieldnames=list(data[0]))
    w.writeheader()
    w.writerows(data)
