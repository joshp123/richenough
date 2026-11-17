"""Ireland: RTB average monthly rent of new tenancies, two-bed, by county or town (CSO PxStat table RIQ02), 2025 Q4.

The Residential Tenancies Board registers every new tenancy; the CSO publishes the average rent by number of bedrooms
for counties, cities and towns. For each NUTS 3 region we take its main town (largest town, found from the CSO's
2022 census list of urban areas; Dublin is the county, which is also the NUTS 3 region).
"""

import json

import common as c

SOURCE_ID = "cso-rtb-riq02"
URL = "https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/RIQ02/JSON-stat/2.0/en"
QUARTER = "2025Q4"

SOURCES = [c.source(
    SOURCE_ID, "Residential Tenancies Board (RTB), published by the Central Statistics Office",
    "RTB Average Monthly Rent Report (RIQ02): average monthly rent of new tenancies by bedrooms, property type and location",
    "https://data.cso.ie/table/RIQ02", "CC BY 4.0", QUARTER,
    "Average rent of new tenancies registered with the RTB in the quarter, per bedroom count and county/city/town. "
    "Table last updated 14 May 2026; the RTB's Q1 2026 report is out but not yet in the table.")]

# NUTS 3 region -> (RTB location of its main town, town name). Largest town of each region by population.
MAIN = {
    "IE041": ("Letterkenny, Donegal", "Letterkenny"),   # Border: Letterkenny (about 22,000) ahead of Sligo
    "IE042": ("Galway City", "Galway"),
    "IE051": ("Limerick City", "Limerick"),
    "IE052": ("Waterford City", "Waterford"),
    "IE053": ("Cork City", "Cork"),
    "IE061": ("Dublin", "Dublin"),                       # county Dublin = the region
    "IE062": ("Drogheda, Louth", "Drogheda"),            # Mid-East: Drogheda (about 44,000) ahead of Dundalk, Navan
    "IE063": ("Athlone, Westmeath", "Athlone"),          # Midland: Athlone ahead of Mullingar, Portlaoise
}


def _values():
    d = json.loads(c.fetch(SOURCE_ID, URL, "RIQ02.json").read_text())
    dim = d["dimension"]

    def labels(key):
        cat = dim[key]["category"]
        return [cat["label"][i] for i in sorted(cat["index"], key=lambda z: cat["index"][z])] \
            if isinstance(cat["index"], dict) else [cat["label"][i] for i in cat["index"]]

    t, b, p, l = (labels(k) for k in ["TLIST(Q1)", "C02970V03592", "C02969V03591", "C03004V03625"])

    def get(location):
        i = ((t.index(QUARTER) * len(b) + b.index("Two bed")) * len(p) + p.index("All property types")) * len(l) + l.index(location)
        return d["value"][i]
    return get


def rows():
    get = _values()
    out = []
    for nuts3 in c.regions_in("IE"):
        location, town = MAIN[nuts3]
        value = get(location)
        if value is None:
            raise ValueError(f"no RTB two-bed rent for {location} in {QUARTER}")
        measured = c.place(nuts3) if location == "Dublin" else (c.city_code("IE", town) or c.place(nuts3))
        scope = "county Dublin (the whole region)" if location == "Dublin" else f"{town} ({location})"
        out.append(c.row(
            c.place(nuts3), round(float(value), 2), "EUR", "per_month", QUARTER.replace("Q", "-Q"), measured, SOURCE_ID,
            f"RTB average rent of new tenancies, two-bed (all property types), {scope}; registered new tenancies "
            f"started in the quarter."))
    return out
