#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = ["shapely"]
# ///
"""New Zealand: two-bedroom rent of new tenancies, from MBIE / Tenancy Services bond data, the 12 months to September 2026.

Written by AI on 2026.11.17 by model claude sonnet 5.5.

Source: Tenancy Services "Rental bond data" (MBIE), file "Detailed quarterly report, January 2020 to July 2026" (CSV).
https://www.tenancy.govt.nz/about-tenancy-services/data-and-statistics/rental-bond-data/
Every private-landlord bond lodged in the quarter, by SA2 area (Stats NZ 2018/2019 areas), dwelling type and bedrooms.
Fixed random rounding to base 3 on counts; areas with fewer than 5 bonds are suppressed.

The file has no region or territorial authority rows, so we pool its SA2 rows ourselves: the bond-weighted median of the
SA2 medians (each SA2 and quarter is one observation, weighted by its bonds lodged). A weighted geometric mean of the SA2
geometric means was tried first and rejected: tiny SA2 cells with junk low rents (for example a 'median' of NZ$148 in Titahi Bay)
drag it down. Checked against the published monthly region file (all dwelling types, all bedrooms, Jul-Sep 2026, SA2 rows pooled
the same way): Auckland 650 vs monthly medians 640/650/640, Bay of Plenty 650 vs 650/650/648, Canterbury 550 vs 560/550/560,
Wellington 575 vs 570/575/580, Otago 588 vs 575/600/580, Waikato 575 vs 575/580/580.
We pool the four quarters Oct 2025 to Sep 2026, because one quarter of two-bedroom bonds leaves most SA2 cells suppressed (<5 bonds);
the national median barely moved over the year. A place needs 30+ pooled bonds to get a row.
SA2 -> territorial authority and region: Stats NZ SA2 2018 centroids tested against Stats NZ TA 2018 and Regional Council 2018
polygons (ArcGIS REST, keyless). Boundaries are cached in cache/nz-mbie-bonds/.

Measured: two-bedroom dwellings of ALL types (houses, apartments, flats; boarding rooms excluded by the bedroom filter).
NZ private rentals are mostly houses, and apartments are too few outside Auckland to give regional figures, so a
"flat only" figure would be too thin; the note on each row gives the apartment-only figure when 30+ bonds exist.
Weekly rent is converted to monthly by x 52 / 12.
"""

import csv
import json
import math
import pathlib
import re
import sys
import urllib.parse
import urllib.request
from collections import defaultdict

from shapely.geometry import Point, shape

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from places import city_code  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[3]
CACHE = REPO / "cache" / "nz-mbie-bonds"
PAGE = "https://www.tenancy.govt.nz/about-tenancy-services/data-and-statistics/rental-bond-data/"
ARC = "https://services2.arcgis.com/vKb0s8tBIA3bdocZ/ArcGIS/rest/services/"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
COLUMNS = ["place_code", "amount", "currency", "unit", "period", "measured_for", "source_id", "note"]
SOURCE_ID = "nz-mbie-bonds-2026"
TIMEFRAMES = ("1/10/2025", "1/01/2026", "1/04/2026", "1/07/2026")
PERIOD = "2025-10/2026-09"
MIN_BONDS = 30

SOURCES = [
    {
        "source_id": SOURCE_ID,
        "publisher": "Ministry of Business, Innovation and Employment (Tenancy Services), New Zealand",
        "title": "Rental bond data: detailed quarterly report, January 2020 to July 2026 (private bonds by SA2, dwelling type and bedrooms)",
        "url": PAGE,
        "licence": "Creative Commons Attribution 3.0 New Zealand (credit the Ministry of Business, Innovation and Employment)",
        "retrieved": "2026-11-17",
        "period": PERIOD,
        "note": "All new private-landlord bonds lodged Oct 2025 to Sep 2026 (four quarters), by tenancy start date. Pooled by us from SA2 rows into territorial authorities and regions with a bond-weighted median of SA2 medians.",
    },
    {
        "source_id": "nz-statsnz-geographies-2018",
        "publisher": "Stats NZ",
        "title": "Statistical Area 2 2018 (centroids), Territorial Authority 2018 and Regional Council 2018 boundaries, ArcGIS REST services",
        "url": ARC,
        "licence": "Creative Commons Attribution 4.0 International (Stats NZ open data)",
        "retrieved": "2026-11-17",
        "period": "2018",
        "note": "Used only to assign each SA2 to a territorial authority and a region.",
    },
]

# ISO 3166-2:NZ code, region name in Stats NZ Regional Council 2018, label
REGIONS = {
    "NZ-NTL": "Northland Region", "NZ-AUK": "Auckland Region", "NZ-WKO": "Waikato Region", "NZ-BOP": "Bay of Plenty Region",
    "NZ-GIS": "Gisborne Region", "NZ-HKB": "Hawke's Bay Region", "NZ-TKI": "Taranaki Region", "NZ-MWT": "Manawatu-Wanganui Region",
    "NZ-WGN": "Wellington Region", "NZ-TAS": "Tasman Region", "NZ-NSN": "Nelson Region", "NZ-MBH": "Marlborough Region",
    "NZ-WTC": "West Coast Region", "NZ-CAN": "Canterbury Region", "NZ-OTA": "Otago Region", "NZ-STL": "Southland Region",
}

# GeoNames city name, Stats NZ territorial authority 2018 it sits in
CITIES = [
    ("Auckland", "Auckland"), ("Wellington", "Wellington City"), ("Christchurch", "Christchurch City"),
    ("Hamilton", "Hamilton City"), ("Tauranga", "Tauranga City"), ("Dunedin", "Dunedin City"),
    ("Palmerston North", "Palmerston North City"), ("Napier", "Napier City"), ("Nelson", "Nelson City"),
    ("Rotorua", "Rotorua District"), ("New Plymouth", "New Plymouth District"), ("Whangarei", "Whangarei District"),
    ("Invercargill", "Invercargill City"), ("Whanganui", "Whanganui District"), ("Gisborne", "Gisborne District"),
    ("Hastings", "Hastings District"), ("Lower Hutt", "Lower Hutt City"), ("Upper Hutt", "Upper Hutt City"),
    ("Porirua", "Porirua City"), ("Timaru", "Timaru District"),
    ("Taupo", "Taupo District"), ("Masterton", "Masterton District"),
    ("Levin", "Horowhenua District"), ("Whakatane", "Whakatane District"),
]


def get(url: str, dest: pathlib.Path, binary: bool = False):
    if not dest.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=180).read())
    return dest.read_bytes() if binary else dest.read_text(encoding="utf-8")


def quarterly_csv() -> pathlib.Path:
    dest = CACHE / "quarterly.csv"
    if not dest.exists():
        page = get(PAGE, CACHE / "page.html")
        m = re.search(r'href="([^"]*detailed-quarterly-tenancy-q1-2020q3[^"?]*\.csv)', page)
        if not m:
            raise RuntimeError("quarterly CSV link not found on the MBIE page")
        get(urllib.parse.urljoin(PAGE, m.group(1)), dest)
    return dest


def arcgis(svc: str, params: dict, name: str):
    dest = CACHE / name
    if not dest.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        url = f"{ARC}{svc}/FeatureServer/0/query?" + urllib.parse.urlencode({"where": "1=1", **params})
        dest.write_bytes(urllib.request.urlopen(url, timeout=180).read())
    return json.loads(dest.read_text(encoding="utf-8"))


def sa2_map() -> dict[str, tuple[str, str, str]]:
    cents = []
    for off in range(0, 3000, 1000):
        d = arcgis("Statistical_Area_2_2018", dict(f="json", outFields="SA22018_V1_00,SA22018_V1_NAME", returnGeometry="false",
                                                    returnCentroid="true", outSR="4326", resultOffset=off, resultRecordCount=1000),
                   f"sa2-centroids-{off}.json")
        cents += d.get("features", [])
    polys = {}
    for key, svc, code, label in [("ta", "Territorial_Authority_2018", "TA2018_V1_00", "TA2018_V1_00_NAME"),
                                  ("rc", "Regional_Council_2018", "REGC2018_V1_00", "REGC2018_V1_00_NAME")]:
        d = arcgis(svc, dict(f="geojson", outFields="*", outSR="4326", maxAllowableOffset="0.002", resultRecordCount=200), f"{svc}.geojson")
        polys[key] = [(f["properties"][label], shape(f["geometry"])) for f in d["features"]]

    def find(pt, polygons):
        for name, geom in polygons:
            if geom.contains(pt):
                return name
        return min(polygons, key=lambda p: p[1].distance(pt))[0]  # generalised edges: nearest polygon

    out = {}
    for f in cents:
        if "centroid" not in f:
            continue
        pt = Point(f["centroid"]["x"], f["centroid"]["y"])
        a = f["attributes"]
        out[a["SA22018_V1_00"]] = (a["SA22018_V1_NAME"], find(pt, polys["ta"]), find(pt, polys["rc"]))
    return out


def pooled(rows_, level: int, mapping: dict, dwelling: str, beds: str) -> dict[str, tuple[float, float]]:
    """Bond-weighted median of SA2 medians, and the bonds behind it, per territorial authority or region."""
    acc = defaultdict(list)
    for r in rows_:
        if r["TimeFrame"] not in TIMEFRAMES or r["Dwelling Type"] != dwelling or r["Number Of Beds"] != beds:
            continue
        loc = r["Location Id"]
        if loc not in mapping or r["Median Rent"] in ("NULL", ""):
            continue
        n = float(r["Total Bonds"].replace(",", ""))
        if n > 0:
            acc[mapping[loc][level]].append((float(r["Median Rent"]), n))
    out = {}
    for key, obs in acc.items():
        total = sum(n for _, n in obs)
        if total < MIN_BONDS:
            continue
        run = 0.0
        for rent, n in sorted(obs):
            run += n
            if run >= total / 2:
                out[key] = (rent, total)
                break
    return out


def monthly(weekly: float) -> float:
    return round(weekly * 52 / 12)


def rows() -> list[dict]:
    data = list(csv.DictReader(open(quarterly_csv(), encoding="utf-8-sig")))
    mapping = sa2_map()
    ta2 = pooled(data, 1, mapping, "ALL", "2")
    rc2 = pooled(data, 2, mapping, "ALL", "2")
    ta_apt = pooled(data, 1, mapping, "Apartment", "2")
    rc_apt = pooled(data, 2, mapping, "Apartment", "2")
    base = {"currency": "NZD", "unit": "per_month", "period": PERIOD, "source_id": SOURCE_ID}
    out = []

    def apt_note(table, key):
        if key in table:
            return f" Two-bedroom apartments only: NZ${table[key][0]:.0f} a week from {table[key][1]:.0f} bonds."
        return ""

    nat = next(r for r in data if r["TimeFrame"] == "1/07/2026" and r["Location Id"] == "-99" and r["Dwelling Type"] == "ALL" and r["Number Of Beds"] == "2")
    out.append({**base, "period": "2026-Q3", "place_code": "NZ", "amount": monthly(float(nat["Median Rent"])),
                "measured_for": "New Zealand, two-bedroom rentals of all types (houses, apartments, flats), new private bonds Jul-Sep 2026",
                "note": (f"MBIE bond data, national row for Jul-Sep 2026: median NZ${nat['Median Rent']} a week from {nat['Total Bonds']} bonds; x 52/12. "
                         f"Apartments only (2 bed): median NZ${next(r for r in data if r['TimeFrame'] == '1/07/2026' and r['Location Id'] == '-99' and r['Dwelling Type'] == 'Apartment' and r['Number Of Beds'] == '2')['Median Rent']} a week.")})
    for code, name in REGIONS.items():
        if name not in rc2:
            print(f"  no two-bedroom rows for {name} (fewer than 30 unsuppressed bonds in the year)", file=sys.stderr)
            continue
        w, n = rc2[name]
        out.append({**base, "place_code": code, "amount": monthly(w),
                    "measured_for": f"{name.removesuffix(' Region')} region-wide, two-bedroom rentals of all types, new private bonds Oct 2025 to Sep 2026",
                    "note": f"MBIE bond data, bond-weighted median of SA2 medians over four quarters, NZ${w:.0f} a week from {n:.0f} bonds; x 52/12." + apt_note(rc_apt, name)})
    for city, ta in CITIES:
        if ta not in ta2:
            print(f"  no data for {ta}", file=sys.stderr)
            continue
        try:
            code = city_code(city, "NZ")
        except KeyError:
            print(f"  no GeoNames city {city}", file=sys.stderr)
            continue
        w, n = ta2[ta]
        out.append({**base, "place_code": code, "amount": monthly(w),
                    "measured_for": f"{ta} (the city's whole territorial authority), two-bedroom rentals of all types, new private bonds Oct 2025 to Sep 2026",
                    "note": f"MBIE bond data, bond-weighted median of SA2 medians over four quarters, NZ${w:.0f} a week from {n:.0f} bonds; x 52/12." + apt_note(ta_apt, ta)})
    return out


if __name__ == "__main__":
    data = rows()
    w = csv.DictWriter(sys.stdout, fieldnames=COLUMNS)
    w.writeheader()
    w.writerows(data)
