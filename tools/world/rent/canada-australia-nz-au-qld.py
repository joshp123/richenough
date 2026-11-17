#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = ["openpyxl"]
# ///
"""Queensland: median weekly rent of two-bedroom flats on NEW bonds, from the RTA's median rents quarterly data.

Written by AI on 2026.11.17 by model claude sonnet 5.5.

Source: Residential Tenancies Authority (RTA) Queensland, "Median rents quarterly data" (Excel workbook "rta-bond-statistics.xlsx").
https://www.rta.qld.gov.au/forms-resources/rta-data-releases/median-rents-quarterly-data
Median weekly rent paid for new tenancies commencing in the quarter (bonds lodged), by dwelling "Flat 2" (a two-bedroom flat/unit),
for the state, local government areas (LGA) and postcodes. We take the latest quarter in the file, convert weekly to monthly
by x 52 / 12, and need 30+ new bonds in the quarter for a city row. A city's central postcode is used where the RTA gives one with
30+ bonds (Brisbane 4000, Surfers Paradise 4217, Maroochydore 4558, Townsville 4810, Cairns 4870); otherwise its LGA.
The workbook is replaced in place each quarter; the saved copy is in cache/au-qld-rta-median-rents/.
"""

import csv
import pathlib
import sys
import urllib.request

import openpyxl

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from places import city_code  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[3]
CACHE = REPO / "cache" / "au-qld-rta-median-rents"
URL = "https://www.rta.qld.gov.au/sites/default/files/2023-04/rta-bond-statistics.xlsx"
PAGE = "https://www.rta.qld.gov.au/forms-resources/rta-data-releases/median-rents-quarterly-data"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
SOURCE_ID = "au-qld-rta-median-rents"
COLUMNS = ["place_code", "amount", "currency", "unit", "period", "measured_for", "source_id", "note"]

SOURCES = [{
    "source_id": SOURCE_ID,
    "publisher": "Residential Tenancies Authority (RTA), Queensland Government",
    "title": "Median rents quarterly data (bond statistics workbook): median rents by postcode, suburb, local government area and state",
    "url": PAGE,
    "licence": "Creative Commons Attribution 3.0 Australia (RTA copyright page, https://www.rta.qld.gov.au/copyright)",
    "retrieved": "2026-11-17",
    "period": "2026-Q3",
    "note": "Median weekly rent of new bonds lodged in the September 2026 quarter, dwelling type Flat 2 (two-bedroom flat/unit).",
}]

# GeoNames name (Queensland = admin1 04), LGA in the RTA workbook, central postcode or None, label for measured_for
CITIES = [
    ("Brisbane", "Brisbane (C)", 4000, "Brisbane City postcode 4000 (the CBD)"),
    ("Gold Coast", "Gold Coast (C)", 4217, "Surfers Paradise postcode 4217 (the Gold Coast's centre)"),
    ("Sunshine Coast", "Sunshine Coast (R)", 4558, "Maroochydore postcode 4558 (the Sunshine Coast's centre)"),
    ("Townsville", "Townsville (C)", 4810, "Townsville postcode 4810 (the city centre)"),
    ("Cairns", "Cairns (R)", 4870, "Cairns postcode 4870 (the city centre)"),
    ("Toowoomba", "Toowoomba (R)", None, "Toowoomba local government area"),
    ("Mackay", "Mackay (R)", None, "Mackay local government area"),
    ("Rockhampton", "Rockhampton (R)", None, "Rockhampton local government area"),
    ("Bundaberg", "Bundaberg (R)", None, "Bundaberg local government area"),
    ("Hervey Bay", "Fraser Coast (R)", None, "Fraser Coast local government area (Hervey Bay and Maryborough)"),
    ("Logan City", "Logan (C)", None, "Logan local government area"),
    ("Gladstone", "Gladstone (R)", None, "Gladstone local government area"),
    ("Mount Isa", "Mount Isa (C)", None, "Mount Isa local government area"),
]


def workbook() -> openpyxl.Workbook:
    dest = CACHE / "rta-bond-statistics.xlsx"
    if not dest.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(urllib.request.urlopen(urllib.request.Request(URL, headers={"User-Agent": UA}), timeout=180).read())
    return openpyxl.load_workbook(dest, data_only=True, read_only=True)


def latest(wb, rents_sheet: str, bonds_sheet: str) -> tuple[dict, str]:
    """{place: (median weekly rent, new bonds)} for Flat 2 in the latest quarter, and the quarter's label."""
    rents = [r for r in wb[rents_sheet].iter_rows(values_only=True)]
    bonds = {(r[2], r[3]): r for r in wb[bonds_sheet].iter_rows(values_only=True)}
    head = next(i for i, r in enumerate(rents) if "Mar" in r and "Jun" in r)
    months, years = rents[head], rents[head + 1]
    col = max(i for i, v in enumerate(years) if isinstance(v, int))
    label = f"{years[col]}-Q{ {'Mar': 1, 'Jun': 2, 'Sep': 3, 'Dec': 4}[months[col]] }"
    out = {}
    for r in rents[head + 2:]:
        if r[3] == "Flat 2" and isinstance(r[col], (int, float)):
            b = bonds.get((r[2], r[3]))
            out[r[2]] = (float(r[col]), int(b[col]) if b and isinstance(b[col], (int, float)) else None)
    return out, label


def monthly(weekly: float) -> float:
    return round(weekly * 52 / 12)


def rows() -> list[dict]:
    wb = workbook()
    state, label = latest(wb, "10 qld-rents", "11 qld-new-bonds")
    lga, _ = latest(wb, "7 lga-rents ", "8 lga-new-bonds")
    pc, _ = latest(wb, "1 pc-rents", "2 pc-new-bonds")
    base = {"currency": "AUD", "unit": "per_month", "period": label, "source_id": SOURCE_ID}
    quarter = f"{ {1: 'Jan-Mar', 2: 'Apr-Jun', 3: 'Jul-Sep', 4: 'Oct-Dec'}[int(label[-1])] } {label[:4]}"
    out = []
    w, n = state["Queensland"]
    out.append({**base, "place_code": "AU-QLD", "amount": monthly(w),
                "measured_for": f"Queensland state-wide, two-bedroom flats and units, new bonds {quarter}",
                "note": f"RTA Queensland median rents, Flat 2: median weekly rent for new tenancies AUD {w:.0f} from {n} bonds; x 52/12."})
    for gname, lga_name, postcode, desc in CITIES:
        if postcode is not None and postcode in pc and (pc[postcode][1] or 0) >= 30:
            (w, n), where, extra = pc[postcode], desc, f" Whole {lga_name} LGA: AUD {lga[lga_name][0]:.0f} a week."
        elif lga_name in lga and (lga[lga_name][1] or 0) >= 30:
            (w, n), where, extra = lga[lga_name], desc.split(" postcode")[0] if postcode else desc, ""
            if postcode is not None:
                where = f"{lga_name.split(' (')[0]} local government area (central postcode had under 30 bonds)"
        else:
            print(f"  skipped {gname}: too few bonds", file=sys.stderr)
            continue
        try:
            code = city_code(gname, "AU", "04")
        except KeyError:
            print(f"  no GeoNames city {gname}", file=sys.stderr)
            continue
        out.append({**base, "place_code": code, "amount": monthly(w),
                    "measured_for": f"{where}, two-bedroom flats and units, new bonds {quarter}",
                    "note": f"RTA Queensland median rents, Flat 2: median weekly rent for new tenancies AUD {w:.0f} from {n} bonds; x 52/12." + extra})
    return out


if __name__ == "__main__":
    data = rows()
    w = csv.DictWriter(sys.stdout, fieldnames=COLUMNS)
    w.writeheader()
    w.writerows(data)
