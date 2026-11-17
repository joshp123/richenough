#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = ["openpyxl"]
# ///
"""Canada: two-bedroom rent for a new let, from CMHC's Rental Market Survey, October 2025.

Written by AI on 2026.11.17 by model claude sonnet 5.5.

Source: CMHC "Rental Market Survey Data Tables" (Excel), one national workbook and one workbook per centre,
https://www.cmhc-schl.gc.ca/professionals/housing-markets-data-and-research/housing-data/data-tables/rental-market/rental-market-report-data-tables
Downloads go to cache/ca-cmhc-rms-2025/ once; delete the folder to fetch again.

What each row measures (the survey covers purpose-built rental apartments in structures of 3+ units; it leaves out
condominium apartments, houses, basement suites and rooms):
  province    Table 6.0, "<province> 10,000+": average rent of two-bedroom units that turned over in the past 12 months
              (new tenants), all urban areas of 10,000+ people in the province.
  city        Table 1.1.9, central zone: average asking rent of two-bedroom units that were VACANT at the survey, when the
              zone's quality code is a, b or c. Otherwise Table 6.0, the whole CMA's turnover rent.
  territory   Yellowknife only (CMHC surveys no other territorial centre): Table 1.1.2 average of all tenants.

Run directly to print the rows as CSV.
"""

import csv
import pathlib
import re
import sys
import urllib.request

import openpyxl

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from places import city_code  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[3]
CACHE = REPO / "cache" / "ca-cmhc-rms-2025"
BASE = ("https://assets.cmhc-schl.gc.ca/sites/cmhc/professional/housing-markets-data-and-research/"
        "housing-data-tables/rental-market/rental-market-report-data-tables/2025/")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
COLUMNS = ["place_code", "amount", "currency", "unit", "period", "measured_for", "source_id", "note"]
SOURCE_ID = "ca-cmhc-rms-2025"
PERIOD = "2025-10"

SOURCES = [{
    "source_id": SOURCE_ID,
    "publisher": "Canada Mortgage and Housing Corporation (CMHC)",
    "title": "Rental Market Survey Data Tables, October 2025 (national workbook and one workbook per centre)",
    "url": "https://www.cmhc-schl.gc.ca/professionals/housing-markets-data-and-research/housing-data/data-tables/rental-market/rental-market-report-data-tables",
    "licence": "CMHC copyright; free to download, no licence stated on the tables (page footer: © 2025 Canada Mortgage and Housing Corporation)",
    "retrieved": "2026-11-17",
    "period": PERIOD,
    "note": "Survey of purpose-built rental apartments in structures of 3+ units, first two weeks of October 2025. Excludes condominium rentals, houses, basement suites.",
}]

# ISO 3166-2 code, name as in "<name> 10,000+" in Table 6.0 (national workbook)
PROVINCES = {
    "CA-NL": "Newfoundland and Labrador", "CA-PE": "Prince Edward Island", "CA-NS": "Nova Scotia",
    "CA-NB": "New Brunswick", "CA-QC": "Québec", "CA-ON": "Ontario", "CA-MB": "Manitoba",
    "CA-SK": "Saskatchewan", "CA-AB": "Alberta", "CA-BC": "British Columbia",
}

# centre -> (centre workbook slug, name of the CMA row in Table 6.0 (national),
#            central zone row in Table 1.1.9 of the centre workbook or None, GeoNames name, admin1, label of the central zone)
# admin1 is the GeoNames admin1 code (Canada: 01 AB, 02 BC, 03 MB, 04 NB, 05 NL, 07 NS, 08 ON, 09 PE, 10 QC, 11 SK, 12 YT, 13 NT, 14 NU).
CENTRES = [
    ("toronto", "Toronto CMA", "Zone 1 - Toronto (Central)", "Toronto", "08", "Toronto (Central) zone"),
    ("montreal", "Montréal CMA", "Zone 1 - Downtown Montréal/Îles-des-Soeurs", "Montréal", "10", "Downtown Montréal / Île-des-Soeurs zone"),
    ("vancouver", "Vancouver CMA", "Zone 3 - Downtown", "Vancouver", "02", "Downtown Vancouver zone"),
    ("calgary", "Calgary CMA", "Zone 1 - Downtown", "Calgary", "01", "Downtown Calgary zone"),
    ("edmonton", "Edmonton CMA", "Zone 1 - Downtown", "Edmonton", "01", "Downtown Edmonton zone"),
    ("ottawa", "Ottawa-Gatineau CMA (Ont. part)", "Zone 1 - Downtown", "Ottawa", "08", "Downtown Ottawa zone"),
    ("gatineau", "Ottawa-Gatineau CMA (Qué. part)", "Zone 21 - Hull", "Gatineau", "10", "Hull zone"),
    ("winnipeg", "Winnipeg CMA", "Core Area (Zones 1-4)", "Winnipeg", "03", "Winnipeg core area (zones 1-4)"),
    ("quebec-cma", "Québec CMA", "Zone 1 - Haute-Ville", "Québec", "10", "Haute-Ville zone"),
    ("hamilton", "Hamilton CMA", "Zone 1 - Downtown Core", "Hamilton", "08", "Downtown Hamilton zone"),
    ("kitchener-cambridge-waterloo", "Kitchener-Cambridge-Waterloo CMA", "Zone 2 - Kitchener Central", "Kitchener", "08", "Kitchener Central zone"),
    ("london", "London CMA", "Zone 1 - Downtown North", "London", "08", "Downtown North London zone"),
    ("st-catharines-niagara", "St. Catharines-Niagara CMA", "Zone 1 - St. Catharines (Core)", "St. Catharines", "08", "St. Catharines core zone"),
    ("halifax", "Halifax CMA", "Zone 1 - Peninsula (South)", "Halifax", "07", "Halifax Peninsula (South) zone"),
    ("victoria", "Victoria CMA", "City of Victoria (Zones 1-4)", "Victoria", "02", "City of Victoria (zones 1-4)"),
    ("windsor", "Windsor CMA", "Zone 1 - Centre", "Windsor", "08", "Windsor centre zone"),
    ("oshawa", "Oshawa CMA", "Zone 2 - Oshawa (South/Central)", "Oshawa", "08", "Oshawa South/Central zone"),
    ("saskatoon", "Saskatoon CMA", "Zone 1 - Central", "Saskatoon", "11", "Saskatoon Central zone"),
    ("regina", "Regina CMA", "Zone 1 - Central", "Regina", "11", "Regina Central zone"),
    ("st-johns", "St. John's CMA", "Zone 1 - St. John's (East)", "St. John's", "05", "St. John's East zone"),
    ("barrie", "Barrie CMA", None, "Barrie", "08", ""),
    ("kelowna", "Kelowna CMA", "Zone 1 - Core Area", "Kelowna", "02", "Kelowna Core Area zone"),
    ("abbotsford-mission", "Abbotsford-Mission CMA", "Zone 1 - Abbotsford", "Abbotsford", "02", "Abbotsford zone"),
    ("sherbrooke", "Sherbrooke CMA", "Zone 2 - Central District", "Sherbrooke", "10", "Central District zone"),
    ("guelph", "Guelph CMA", None, "Guelph", "08", ""),
    ("kingston", "Kingston CMA", "Zone 1 - Downtown Kingston", "Kingston", "08", "Downtown Kingston zone"),
    ("moncton", "Moncton CMA", "Zone 1 - Central Moncton", "Moncton", "04", "Central Moncton zone"),
    ("saguenay", "Saguenay CMA", None, "Saguenay", "10", ""),
    ("trois-rivieres", "Trois-Rivières CMA", "Zone 1 - Downtown", "Trois-Rivières", "10", "Downtown zone"),
    ("thunder-bay", "Thunder Bay CMA", None, "Thunder Bay", "08", ""),
    ("brantford", "Brantford CMA", None, "Brantford", "08", ""),
    ("peterborough", "Peterborough CMA", "Zone 1 - Downtown", "Peterborough", "08", "Downtown Peterborough zone"),
    ("greater-sudbury", "Greater Sudbury/Grand Sudbury CMA", None, "Greater Sudbury", "08", ""),
    ("lethbridge", "Lethbridge CMA", None, "Lethbridge", "01", ""),
    ("nanaimo", "Nanaimo CMA", "Zone 1 - Centre", "Nanaimo", "02", "Nanaimo Centre zone"),
    ("kamloops", "Kamloops CMA", None, "Kamloops", "02", ""),
    ("fredericton", "Fredericton CMA", None, "Fredericton", "04", ""),
    ("saint-john", "Saint John CMA", "Zone 1 - South", "Saint John", "04", "Saint John South zone"),
    ("red-deer", "Red Deer CMA", None, "Red Deer", "01", ""),
    ("chilliwack", "Chilliwack CMA", None, "Chilliwack", "02", ""),
    ("drummondville", "Drummondville CMA", None, "Drummondville", "10", ""),
    ("belleville-quintewest", "Belleville - Quinte West CMA", "Zone 1 - City of Belleville", "Belleville", "08", "City of Belleville zone"),
    ("charlottetown", "Charlottetown CA", "Zone 1 - Downtown", "Charlottetown", "09", "Downtown Charlottetown zone"),
]


def download(name: str) -> pathlib.Path:
    path = CACHE / name
    if not path.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(BASE + name, headers={"User-Agent": UA})
        path.write_bytes(urllib.request.urlopen(req, timeout=120).read())
    return path


def num(cell) -> float | None:
    if cell is None:
        return None
    s = str(cell).replace(",", "").strip()
    return float(s) if re.fullmatch(r"\d+(\.\d+)?", s) else None


def fmt(value: float) -> str:
    return f"{value:,.0f}"


def national() -> dict:
    """Table 6.0 turnover 2BR, Table 1.0 average 2BR all tenants, Table 4.2 condo 2BR, keyed by centre name."""
    wb = openpyxl.load_workbook(download("rmr-canada-2025-en.xlsx"), data_only=True)
    out: dict[str, dict] = {}
    for r in wb["Table 6.0"].iter_rows(min_row=6, values_only=True):
        if r[0] and num(r[12]) is not None:
            out.setdefault(r[0], {})["turnover"] = (num(r[12]), r[13])
    for r in wb["Table 1.0"].iter_rows(min_row=4, values_only=True):
        if r[0] and num(r[13]) is not None:
            out.setdefault(r[0], {})["average"] = (num(r[13]), r[14])
    for r in wb["Table 4.2"].iter_rows(min_row=4, values_only=True):
        if r[0] and num(r[8]) is not None:
            out.setdefault(r[0], {})["condo"] = (num(r[8]), r[9])
    return out


def central_vacant(slug: str, zone: str) -> tuple[float, str] | None:
    """Average rent of vacant two-bedroom apartments in a zone (Table 1.1.9), or None when suppressed or quality d."""
    wb = openpyxl.load_workbook(download(f"rmr-{slug}-2025-en.xlsx"), data_only=True)
    for r in wb["Table 1.1.9"].iter_rows(min_row=5, values_only=True):
        if r[0] and str(r[0]).strip() == zone:
            value, quality = num(r[11]), r[12]
            if value is not None and quality in ("a", "b", "c"):
                return value, quality
            return None
    raise KeyError(f"{zone!r} not in {slug} Table 1.1.9")


def rows() -> list[dict]:
    nat = national()
    out = []
    for code, name in PROVINCES.items():
        d = nat[f"{name} 10,000+"]
        value, quality = d["turnover"]
        out.append({
            "place_code": code, "amount": value, "currency": "CAD", "unit": "per_month", "period": PERIOD,
            "measured_for": f"{name}, all urban areas of 10,000+ people, purpose-built rental apartments, units that turned over in the past 12 months",
            "source_id": SOURCE_ID,
            "note": (f"CMHC Rental Market Survey Oct 2025 Table 6.0, average rent of two-bedroom turnover units (new tenants), quality {quality}. "
                     f"All sitting and new tenants average ${fmt(d['average'][0])} (Table 1.0). Excludes condominium rentals and houses."),
        })
    d = nat["Canada 10,000+"]
    value, quality = d["turnover"]
    out.append({
        "place_code": "CA", "amount": value, "currency": "CAD", "unit": "per_month", "period": PERIOD,
        "measured_for": "Canada, all urban areas of 10,000+ people, purpose-built rental apartments, units that turned over in the past 12 months",
        "source_id": SOURCE_ID,
        "note": (f"CMHC Rental Market Survey Oct 2025 Table 6.0, average rent of two-bedroom turnover units (new tenants), quality {quality}. "
                 f"All sitting and new tenants average ${fmt(d['average'][0])} (Table 1.0). Excludes condominium rentals and houses."),
    })
    for slug, cma, zone, gname, admin1, label in CENTRES:
        d = nat[cma]
        cv = central_vacant(slug, zone) if zone else None
        extras = f" All tenants average ${fmt(d['average'][0])} (Table 1.0)." if "average" in d else ""
        if "condo" in d:
            extras += f" Rented condominium apartments average ${fmt(d['condo'][0])} (Table 4.2)."
        if cv:
            value, quality = cv
            measured = f"{gname}, {label}, purpose-built rental apartments, vacant units (asking rent)"
            note = (f"CMHC Oct 2025 Table 1.1.9, {zone}: average rent of vacant two-bedroom apartments, quality {quality}. "
                    f"Whole-CMA turnover rent is ${fmt(d['turnover'][0])} (Table 6.0)." + extras)
        else:
            value, quality = d["turnover"]
            why = "no central zone published" if not zone else f"central zone ({label}) suppressed or poor quality"
            measured = f"{gname} CMA, purpose-built rental apartments, units that turned over in the past 12 months"
            note = f"CMHC Oct 2025 Table 6.0, whole-CMA average rent of two-bedroom turnover units, quality {quality}; {why}." + extras
        out.append({
            "place_code": city_code(gname, "CA", admin1), "amount": value, "currency": "CAD", "unit": "per_month",
            "period": PERIOD, "measured_for": measured, "source_id": SOURCE_ID, "note": note,
        })
    wb = openpyxl.load_workbook(download("rmr-yellowknife-2025-en.xlsx"), data_only=True)
    for r in wb["Table 1.1.2"].iter_rows(min_row=3, values_only=True):
        if r[0] == "Yellowknife CA":
            value, quality = num(r[11]), r[12]
            vacant = "suppressed"
    out.append({
        "place_code": "CA-NT", "amount": value, "currency": "CAD", "unit": "per_month", "period": PERIOD,
        "measured_for": "Yellowknife census agglomeration (the only Northwest Territories centre CMHC surveys), purpose-built rental apartments, all tenants",
        "source_id": SOURCE_ID,
        "note": f"CMHC Oct 2025 Yellowknife workbook Table 1.1.2, average two-bedroom rent of all tenants, quality {quality}. Vacant-unit (asking) rent {vacant}; no turnover rent published.",
    })
    out.append({**out[-1], "place_code": city_code("Yellowknife", "CA", "13"),
                "measured_for": "Yellowknife census agglomeration, purpose-built rental apartments, all tenants"})
    return out


if __name__ == "__main__":
    data = rows()
    w = csv.DictWriter(sys.stdout, fieldnames=COLUMNS)
    w.writeheader()
    w.writerows(data)
