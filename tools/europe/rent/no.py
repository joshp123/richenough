"""Norway: SSB's predicted monthly rent of a 3-room flat (70 and 80 m2 averaged to 75 m2) by price zone, 2025 (table 09897).

SSB's Rental market survey (leiemarkedsundersøkelsen) predicts rents for standardised dwellings in 16 price zones: named
districts of the big cities and classes of urban settlement by size. Each region takes the zone of its main town.
Svalbard and Jan Mayen have no zone (Jan Mayen has no residents) and get no row.
"""

import json

import common as c

SOURCE_ID = "ssb-no-leiemarked"
URL = "https://data.ssb.no/api/v0/en/table/09897"
YEAR = "2025"

SOURCES = [c.source(
    SOURCE_ID, "Statistics Norway (SSB)",
    "Rental market survey: Predicted monthly rents (NOK) by price zone, number of rooms and utility floor space (table 09897); "
    "average rents by tenancy start (table 06230)",
    "https://www.ssb.no/en/statbank/table/09897", "CC BY 4.0 (NLOD)", YEAR,
    "Survey of rented dwellings, annual; rents predicted by SSB's model for a standardised dwelling in each price zone.")]

SETTLEMENT = {"20.00": "urban settlements over 20,000 inhabitants", "21.00": "urban settlements of 2,000-19,999 inhabitants"}
# NUTS 3 -> (town, GeoNames lookup names, zones averaged unweighted). Class zones (20/21) describe the town's size class.
ZONES = {
    "NO020": ("Hamar", ["Hamar"], ["20.00"]),
    "NO060": ("Trondheim", ["Trondheim"], ["04.01", "04.02"]),
    "NO071": ("Bodø", ["Bodø"], ["20.00"]),
    "NO072": ("Tromsø", ["Tromsø"], ["07.00"]),
    "NO073": ("Alta", ["Alta"], ["21.00"]),
    "NO081": ("Oslo", ["Oslo"], ["01.01", "01.02", "01.03", "01.04"]),
    "NO083": ("Sarpsborg", ["Sarpsborg"], ["20.00"]),
    "NO084": ("Bærum", ["Bærum", "Sandvika"], ["02.01"]),
    "NO085": ("Drammen", ["Drammen"], ["20.00"]),
    "NO092": ("Kristiansand", ["Kristiansand"], ["06.00"]),
    "NO093": ("Tønsberg", ["Tønsberg"], ["20.00"]),
    "NO094": ("Skien", ["Skien"], ["20.00"]),
    "NO0A1": ("Stavanger", ["Stavanger"], ["05.00"]),
    "NO0A2": ("Bergen", ["Bergen"], ["03.01", "03.02"]),
    "NO0A3": ("Ålesund", ["Ålesund"], ["20.00"]),
}


def rows():
    body = {"query": [
        {"code": "Soner2", "selection": {"filter": "all", "values": ["*"]}},
        {"code": "AntRomBRA", "selection": {"filter": "item", "values": ["3.070", "3.080"]}},
        {"code": "Tid", "selection": {"filter": "item", "values": [YEAR]}}], "response": {"format": "json-stat2"}}
    path = c.fetch(SOURCE_ID, URL, "09897-3rooms.json", data=json.dumps(body).encode(),
                   headers={"Content-Type": "application/json"})
    cube = json.loads(path.read_text())
    zones, sizes = cube["dimension"]["Soner2"]["category"]["index"], cube["dimension"]["AntRomBRA"]["category"]["index"]
    value = lambda zone, size: cube["value"][zones[zone] * len(sizes) + sizes[size]]  # noqa: E731

    out = []
    for nuts3 in c.regions_in("NO"):
        if nuts3 not in ZONES:
            continue
        town, names, zone_codes = ZONES[nuts3]
        amount = sum((value(z, "3.070") + value(z, "3.080")) / 2 for z in zone_codes) / len(zone_codes)
        city = len(zone_codes) > 1 or zone_codes[0] not in SETTLEMENT
        measured = (c.city_code("NO", *names) if zone_codes[0] not in SETTLEMENT else None) or c.place(nuts3)
        how = (f"mean of {len(zone_codes)} price zones of {town}" if len(zone_codes) > 1 else
               f"price zone '{SETTLEMENT[zone_codes[0]]}' (the size class of {town})" if not city else f"price zone {town}")
        out.append(c.row(
            c.place(nuts3), round(amount), "NOK", "per_month", YEAR, measured, SOURCE_ID,
            f"SSB predicted monthly rent of a 3-room flat of 75 m2 (mean of the 70 m2 and 80 m2 predictions), {how}. "
            f"Rooms count the living room, so 3 rooms is a two-bedroom flat."))
    return out
