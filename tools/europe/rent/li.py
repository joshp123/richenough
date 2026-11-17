"""Liechtenstein: Amt fuer Statistik census rent survey 2015 (eTab PxWeb API), brought forward to 2025.

The Amt's own site (statistikportal.li) sits behind Cloudflare, but its eTab database (etab.llv.li) is republished on
opendata.swiss and answers a plain keyless PxWeb API. The latest table there is the 31.12.2015 census: average net
rent (no service charges) of all rented flats by useful floor space and municipality. We take the 60-<80 m2 band for
the whole country (Vaduz alone is a thin cell: CHF 1,200 against 1,275 for the country), bring it to 2025 with the
Swiss HICP actual-rentals index (Eurostat has no Liechtenstein series; the two economies share the franc and the
market) and apply Switzerland's new-let premium (see rent/ch.py: rent of tenancies under two years against all
tenancies, 3-room flats). The Amt's 2020 census publication gives only an all-sizes figure (gross CHF 1,963, against
1,705 in 2015, +15%) and is not reachable by plain fetch.
"""

import json

import common as c
from rent import ch

SOURCE_ID = "li-etab-mietpreise"
API = "https://etab.llv.li/PXWEb/api/v1/en/eTab/Bauen%20und%20Wohnen/Mietpreise/394.002e.px"
PAGE = "https://ckan.opendata.swiss/perma/394.002d@amt-fuer-statistik-fl"

SOURCES = [c.source(
    SOURCE_ID, "Office of Statistics Liechtenstein (Amt fuer Statistik), eTab, via opendata.swiss",
    "394.002e Average net rent by useful floor space and municipality (census, 31.12.2015)", PAGE,
    "opendata.swiss terms of use, BY (free use with source attribution)", "2015",
    "Average net monthly rent of rented flats (stock, not new lets) from the census survey; flats 60-<80 m2.")]


def rows():
    body = json.dumps({"query": [
        {"code": "Reference date", "selection": {"filter": "item", "values": ["1"]}},
        {"code": "Useful floor space", "selection": {"filter": "item", "values": ["5"]}},
        {"code": "Municipality", "selection": {"filter": "item", "values": ["0", "1"]}}],
        "response": {"format": "json"}}).encode()
    path = c.fetch(SOURCE_ID, API, "net_rent_60_80_2015.json", data=body, headers={"Content-Type": "application/json"})
    data = {tuple(d["key"]): float(d["values"][0]) for d in json.loads(path.read_text(encoding="utf-8-sig"))["data"]}
    country, vaduz = data[("1", "5", "0")], data[("1", "5", "1")]

    line = next(r for r in ch._sheet("gemtyp_zimmer_bezug").itertuples(index=False) if r[0] == "3 Zimmer")
    premium = float(line[5]) / float(line[1])
    growth = c.rent_inflation("CH", 2015, 2025)
    amount = round(country * growth * premium, -1)
    return [c.row(
        c.place("LI000"), amount, "CHF", "per_month", "2025", c.place("LI000"), SOURCE_ID,
        f"Census 2015 average net rent of flats of 60-<80 m2, whole country CHF {country:.0f} (Vaduz CHF {vaduz:.0f}), "
        f"x {growth:.4f} (Swiss HICP actual rentals 2015 to 2025) x {premium:.4f} (Swiss new-let premium, 3 rooms, "
        f"BFS 2024). Stock rent scaled to new lets; no service charges. Main town Vaduz.")]
