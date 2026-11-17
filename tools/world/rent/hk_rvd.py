#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = ["xlrd"]
# ///
"""Hong Kong: average rent of a class C flat (70 to 99.9 m2 saleable area), from the Rating and Valuation Department.

Written by AI on 2026.11.17 by model claude sonnet 5.5.

Source: "Private Domestic - Average Rents by Class (from 1982)", https://www.rvd.gov.hk/doc/en/statistics/his_data_1.xls
(sheet "Monthly", HK$ per m2 of saleable area per month, by class A to E and by region: Hong Kong Island, Kowloon,
New Territories). The RVD counts rents on tenancy agreements it receives for stamping, so the series follows new
lettings and renewals signed in the month, not every sitting tenant. A figure in brackets means fewer than 20 deals.

Rows: the mean of the latest three months with a figure, times 75 m2 (class C is 70 to 99.9 m2 of saleable area, which in
Hong Kong is the flat's own floor area without common parts, so a 75 m2 flat is a large two-bed by local standards).
  CITY-1819729  Hong Kong Island, class C   (the city's centre; the RVD does not split by district in this table)
  HK            Kowloon, class C            (the RVD publishes no territory-wide class C average; Kowloon is the middle region)

Run directly to print the rows as CSV.
"""

import csv
import pathlib
import statistics
import sys
import urllib.request

import xlrd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from places import city_code  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[3]
CACHE = REPO / "cache" / "hk-rvd"
URL = "https://www.rvd.gov.hk/doc/en/statistics/his_data_1.xls"
SOURCE_ID = "hk-rvd-avg-rents-by-class"
AREA = 75
REGIONS = {"Hong Kong Island": 6, "Kowloon": 7, "New Territories": 8}  # class C columns among the 15 values

SOURCES = [{
    "source_id": SOURCE_ID,
    "publisher": "Rating and Valuation Department, Government of the Hong Kong SAR",
    "title": "Private Domestic - Average Rents by Class (from 1982), monthly sheet",
    "url": URL,
    "licence": "free to read, no licence stated on the RVD statistics page or beside the file",
    "retrieved": "2026-11-17",
    "period": "2026-06 to 2026-08",
    "note": "HK$ per m2 of saleable area per month, class C = 70 to 99.9 m2; from tenancy agreements received for stamping; latest months provisional.",
}]


def _download() -> pathlib.Path:
    path = CACHE / "his_data_1.xls"
    if not path.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
        path.write_bytes(urllib.request.urlopen(req).read())
    return path


def monthly() -> list[tuple[int, int, list, bool]]:
    """(year, month, 15 values with None for '-', provisional) for every month."""
    sheet = xlrd.open_workbook(_download()).sheet_by_name("Monthly  按月")
    out, year = [], None
    for r in range(sheet.nrows):
        cells = [c for c in sheet.row_values(r) if c not in ("", " ")]
        if not cells or not isinstance(cells[0], (int, float, str)):
            continue
        if isinstance(cells[0], float) and cells[0] >= 1999:
            year = int(cells[0])
            cells = cells[1:]
        elif isinstance(cells[0], str) and cells[0].strip().isdigit() and year:
            pass
        else:
            continue
        try:
            month = int(float(cells[0]))
        except (TypeError, ValueError):
            continue
        rest = cells[1:]
        provisional = "*" in rest
        vals = [v for v in rest if v not in ("(", ")", "*")]
        if len(vals) != 15 or year is None or not 1 <= month <= 12:
            continue
        out.append((year, month, [None if v == "-" else v for v in vals], provisional))
    return out


def _latest(region: str, n: int = 3) -> tuple[list[tuple[int, int, float]], bool]:
    idx = REGIONS[region]
    got = [(y, m, v[idx]) for y, m, v, _ in monthly() if v[idx] is not None]
    prov = any(p for y, m, v, p in monthly()[-n:])
    return got[-n:], prov


def rows() -> list[dict]:
    out = []
    for place, region, measured in [
        (city_code("Hong Kong", "HK"), "Hong Kong Island", "Hong Kong Island (the city's centre), class C flats of 70 to 99.9 m2, private sector"),
        ("HK", "Kowloon", "Kowloon, class C flats of 70 to 99.9 m2, private sector (no territory-wide class C figure is published)"),
    ]:
        last, prov = _latest(region)
        per_m2 = statistics.mean(v for _, _, v in last)
        span = f"{last[0][0]}-{last[0][1]:02d} to {last[-1][0]}-{last[-1][1]:02d}"
        out.append({
            "place_code": place,
            "amount": round(per_m2 * AREA),
            "currency": "HKD",
            "unit": "per_month",
            "period": f"{last[-1][0]}-{last[-1][1]:02d}",
            "measured_for": measured,
            "source_id": SOURCE_ID,
            "note": (f"Mean of the three latest months ({span}) of the RVD average rent for {region}, class C = HK${per_m2:.0f} per m2 "
                     f"per month, times {AREA} m2. Rents on tenancy agreements received for stamping (new lets and renewals), not asking rents. "
                     f"Latest months are provisional{' (the RVD marks the newest figures *)' if prov else ''}. "
                     f"Monthly figures: {', '.join(f'{y}-{m:02d} {v:.0f}' for y, m, v in last)}."),
        })
    return out


if __name__ == "__main__":
    w = csv.DictWriter(sys.stdout, fieldnames=["place_code", "amount", "currency", "unit", "period", "measured_for", "source_id", "note"])
    w.writeheader()
    w.writerows(rows())
