#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# ///
"""Singapore: rent of a 75 m2 private condominium flat (URA) and of an HDB public-housing flat (HDB), from data.gov.sg.

Written by AI on 2026.11.17 by model claude sonnet 5.5.

URA, "Rentals of Non-Landed Residential Buildings, Quarterly" (data.gov.sg d_149ac00a2734bb0a03867bbe2ec0e7b0): for each
major condominium project (100+ units, 10+ rental contracts in the quarter) the 25th percentile, median and 75th
percentile rent and the number of contracts. The file does not label the unit; values of 3 to 8 for a month can only be
Singapore dollars per square foot per month, which is how URA reports private rents. Registered rental contracts of the
quarter, so a new-let measure (includes renewals signed in the quarter). 75 m2 = 807 sq ft.
  SG            all projects in the file: median of the project medians weighted by contracts, x 807 sq ft
  CITY-1880252  projects in the central postal districts 1, 2, 4, 6, 9, 10, 11 (URA's Core Central Region, approximated by
                postal district; the file carries no region field), same method
HDB, "Renting Out of Flats from Jan 2021" (d_c9f57187485a850908655db0e8cfe651): every approved HDB rental contract with
town, flat type and monthly rent, owner-declared and not verified by HDB. `alt_rows()` gives the median over the latest
three months for 3-room (about 65 m2, two bedrooms) and 4-room (about 90 m2, three bedrooms) flats. Public-housing
rents are well below private rents and a foreign couple can rent a whole HDB flat only on a minimum-occupancy-period basis,
so these are alternates, not the main figure.

Run directly to print the main rows as CSV; with --alt, the alternates.
"""

import csv
import json
import pathlib
import statistics
import sys
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from places import city_code  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[3]
UA = {"User-Agent": "Mozilla/5.0"}
SQFT = 807
CENTRAL_DISTRICTS = {"1", "2", "4", "6", "9", "10", "11"}
URA_ID = "d_149ac00a2734bb0a03867bbe2ec0e7b0"
HDB_ID = "d_c9f57187485a850908655db0e8cfe651"
URA_SOURCE = "sg-ura-rentals-nonlanded"
HDB_SOURCE = "sg-hdb-renting-out"
LICENCE = "Singapore Open Data Licence v1.0"

SOURCES = [
    {"source_id": URA_SOURCE, "publisher": "Urban Redevelopment Authority, via data.gov.sg",
     "title": "Rentals of Non-Landed Residential Buildings, Quarterly", "url": f"https://data.gov.sg/datasets/{URA_ID}/view",
     "licence": LICENCE, "retrieved": "2026-11-17", "period": "2026-Q3",
     "note": "Median rent per sq ft per month by condominium project, registered rental contracts of the quarter (unit not labelled in the file)."},
    {"source_id": HDB_SOURCE, "publisher": "Housing & Development Board, via data.gov.sg",
     "title": "Renting Out of Flats from Jan 2021", "url": f"https://data.gov.sg/datasets/{HDB_ID}/view",
     "licence": LICENCE, "retrieved": "2026-11-17", "period": "2026-08 to 2026-10",
     "note": "Approved HDB rental contracts by town and flat type; rents declared by the owner, not verified by HDB."},
]


def _fetch(dataset_id: str, folder: str, name: str) -> pathlib.Path:
    path = REPO / "cache" / folder / name
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        api = f"https://api-open.data.gov.sg/v1/public/api/datasets/{dataset_id}/poll-download"
        url = json.load(urllib.request.urlopen(urllib.request.Request(api, headers=UA)))["data"]["url"]
        path.write_bytes(urllib.request.urlopen(urllib.request.Request(url, headers=UA)).read())
    return path


def _weighted_median(pairs: list[tuple[float, int]]) -> float:
    pairs = sorted(pairs)
    half = sum(w for _, w in pairs) / 2
    run = 0
    for value, weight in pairs:
        run += weight
        if run >= half:
            return value
    raise ValueError("empty")


def _row(place, amount, measured, source, period, note):
    return {"place_code": place, "amount": int(round(amount, -1)), "currency": "SGD", "unit": "per_month", "period": period,
            "measured_for": measured, "source_id": source, "note": note}


def rows() -> list[dict]:
    path = _fetch(URA_ID, URA_SOURCE, "ura_rentals.csv")
    with open(path, encoding="utf-8") as f:
        data = list(csv.DictReader(f))
    quarters = {r["qtr"] for r in data}
    assert len(quarters) == 1, quarters
    qtr = quarters.pop()
    out = []
    for place, subset, measured, where in [
        ("SG", data, "Singapore, all major private condominium projects (100+ units)", "all"),
        (city_code("Singapore", "SG"), [r for r in data if r["postal_district"].lstrip("0") in CENTRAL_DISTRICTS],
         "Singapore's central postal districts 1, 2, 4, 6, 9, 10 and 11 (the Core Central Region), major private condominium projects", "central"),
    ]:
        pairs = [(float(r["median"]), int(r["rental_contracts"])) for r in subset]
        psf = _weighted_median(pairs)
        out.append(_row(place, psf * SQFT, measured, URA_SOURCE, qtr,
                        f"Median of the project medians, weighted by contracts, = S${psf:.2f} per sq ft per month over {len(pairs)} projects and "
                        f"{sum(w for _, w in pairs)} registered rental contracts in {qtr}; times {SQFT} sq ft (75 m2). Registered rental contracts of the quarter "
                        f"(renewals are not separated) of all sizes in condominiums (not landed houses), so the psf figure is not filtered to two bedrooms; small units rent for more per sq ft, "
                        f"so a 75 m2 flat may cost slightly less than this. Projects with fewer than 10 contracts in the quarter are not in the file."))
    return out


def alt_rows() -> list[dict]:
    path = _fetch(HDB_ID, HDB_SOURCE, "hdb.csv")
    with open(path, encoding="utf-8") as f:
        data = list(csv.DictReader(f))
    months = sorted({r["rent_approval_date"] for r in data})[-3:]
    out = []
    for flat, label in [("3-ROOM", "3-room flat (about 65 m2, two bedrooms)"), ("4-ROOM", "4-room flat (about 90 m2, three bedrooms)")]:
        rents = [int(r["monthly_rent"]) for r in data if r["rent_approval_date"] in months and r["flat_type"] == flat]
        out.append(_row("SG", statistics.median(rents), f"Singapore, HDB public housing, {label}", HDB_SOURCE, f"{months[0]} to {months[-1]}",
                        f"Alternate, not for the main figure. Median of {len(rents)} approved HDB rental contracts in {months[0]} to {months[-1]}. "
                        f"Owner-declared rent, not verified by HDB; HDB flats rent below condominiums of the same size."))
    return out


if __name__ == "__main__":
    w = csv.DictWriter(sys.stdout, fieldnames=["place_code", "amount", "currency", "unit", "period", "measured_for", "source_id", "note"])
    w.writeheader()
    w.writerows(alt_rows() if "--alt" in sys.argv else rows())
