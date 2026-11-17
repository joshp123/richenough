"""United Kingdom: ONS Price Index of Private Rents (PIPR), average monthly rent of a two-bed, by local authority.

England and Wales: local authority districts (mean rent of all privately rented two-beds, new and existing tenancies,
September 2026). Scotland: Broad Rental Market Areas (mostly advertised new lets). Northern Ireland: Broad Rental
Market Areas (advertised new lets, latest month July 2026).

Each ITL 3 region gets the figure of the local authority named after its largest town, else its most populous
authority (Scotland and Northern Ireland: of the BRMA that holds that town). London's ITL 3 regions are groups of boroughs, so they get the population-weighted
mean of their boroughs. No scaling to a new-let level: see .agent/research/europe/gb.md (HomeLet's agreed new-let rents
sit within a few per cent of PIPR; Rightmove's asking rents run 20 to 35% above).
"""

import pandas as pd

import common as c

SOURCE_ID = "ons-pipr"
URL = ("https://www.ons.gov.uk/file?uri=/economy/inflationandpriceindices/datasets/"
       "priceindexofprivaterentsukmonthlypricestatistics/21october2026/priceindexofprivaterentsukmonthlypricestatistics.xlsx")
POP_ID = "nomis-la-population"
POP_URL = ("https://www.nomisweb.co.uk/api/v01/dataset/NM_2002_1.data.csv?geography=TYPE424&date=latest&gender=0&c_age=200"
           "&measures=20100&select=geography_code,geography_name,obs_value,date_name")

SOURCES = [
    c.source(SOURCE_ID, "Office for National Statistics",
             "Price Index of Private Rents, UK: monthly price statistics (21 October 2026 release), rental price two bed",
             "https://www.ons.gov.uk/economy/inflationandpriceindices/datasets/priceindexofprivaterentsukmonthlypricestatistics",
             "Open Government Licence v3.0", "2026-09",
             "Average (mean) monthly rent, all privately rented two-bed homes: England and Wales by local authority "
             "(new and existing tenancies), Scotland and Northern Ireland by Broad Rental Market Area (mostly advertised "
             "new lets). Northern Ireland ends 2026-07."),
    c.source(POP_ID, "Office for National Statistics via Nomis",
             "Population estimates, local authorities in the UK (NM_2002_1), all ages, latest year",
             "https://www.nomisweb.co.uk/api/v01/dataset/NM_2002_1.data.csv", "Open Government Licence v3.0", "2025",
             "Used only to pick the most populous local authority in each ITL 3 region and to weight London boroughs."),
]

# Scottish Government Broad Rental Market Areas by council area (council boundaries; PIPR names the 18 BRMAs).
SCOTS_BRMA = {
    "Aberdeen City": "Aberdeen and Shire", "Aberdeenshire": "Aberdeen and Shire",
    "Argyll and Bute": "Argyll and Bute",
    "North Ayrshire": "Ayrshires", "East Ayrshire": "Ayrshires", "South Ayrshire": "Ayrshires",
    "Dumfries and Galloway": "Dumfries and Galloway",
    "Dundee City": "Dundee and Angus", "Angus": "Dundee and Angus",
    "East Dunbartonshire": "East Dunbartonshire",
    "Fife": "Fife",
    "Falkirk": "Forth Valley", "Stirling": "Forth Valley", "Clackmannanshire": "Forth Valley",
    "Glasgow City": "Greater Glasgow", "East Renfrewshire": "Greater Glasgow",
    "Highland": "Highland and Islands", "Moray": "Highland and Islands", "Orkney Islands": "Highland and Islands",
    "Shetland Islands": "Highland and Islands", "Na h-Eileanan Siar": "Highland and Islands",
    "City of Edinburgh": "Lothian", "East Lothian": "Lothian", "Midlothian": "Lothian",
    "North Lanarkshire": "North Lanarkshire",
    "Perth and Kinross": "Perth and Kinross",
    "Renfrewshire": "Renfrewshire/Inverclyde", "Inverclyde": "Renfrewshire/Inverclyde",
    "Scottish Borders": "Scottish Borders",
    "South Lanarkshire": "South Lanarkshire",
    "West Dunbartonshire": "West Dunbartonshire",
    "West Lothian": "West Lothian",
}

# Northern Ireland: the BRMA (by BT postcode districts, NI Housing Executive) that holds each ITL 3 region's main town.
NI_BRMA = {
    "TLN06": ("Belfast", "Belfast BRMA"),
    "TLN07": ("Craigavon", "Lough Neagh Lower BRMA"),
    "TLN08": ("Newry", "South Northern Ireland BRMA"),
    "TLN09": ("Bangor", "South East Northern Ireland BRMA"),
    "TLN0A": ("Derry", "North West Northern Ireland BRMA"),
    "TLN0B": ("Dungannon", "Lough Neagh Lower BRMA"),
    "TLN0C": ("Coleraine", "North Northern Ireland BRMA"),
    "TLN0D": ("Newtownabbey", "Lough Neagh Upper BRMA"),
    "TLN0E": ("Lisburn", "South East Northern Ireland BRMA"),
    "TLN0F": ("Ballymena", "Lough Neagh Upper BRMA"),
    "TLN0G": ("Enniskillen", "South West Northern Ireland BRMA"),
}


# Where GeoNames makes a poor match (Thanet resolves to Saint Peters), name the authority holding the main town.
MAIN_LA = {"TLJ44": "Canterbury"}


def _load():
    path = c.fetch(SOURCE_ID, URL, "pipr-2026-10.xlsx")
    table = pd.read_excel(path, sheet_name="Table 1", header=2)
    table = table[pd.to_numeric(table["Rental price two bed"], errors="coerce").notna()].copy()
    table["rent"] = table["Rental price two bed"].astype(float)
    latest = table.sort_values("Time period").groupby("Area name").tail(1)  # newest month with a value per area
    pop = pd.read_csv(c.fetch(POP_ID, POP_URL, "la-population.csv"))
    return latest, pop


def _town_hit(name: str, population: float):
    """GeoNames (id, population, feature code) of the town a local authority is named after, if it is one of comparable size."""
    hit = c._geonames_hit("GB", name)
    if hit and hit[2] != "PPLL" and hit[1] >= 0.3 * population:  # PPLL is a locality (e.g. the High Peak district)
        return hit
    return None


def _town_population(name: str, population: float):
    """GeoNames population of the town the local authority is named after, when it is a town of comparable size."""
    hit = _town_hit(name, population)
    return hit[1] if hit else None


def _town_code(name: str, population: float):
    """CITY code when the local authority is a town or city of comparable size, else None."""
    hit = _town_hit(name, population)
    return f"CITY-{hit[0]}" if hit else None


def rows():
    latest, pop = _load()
    by_code = latest[latest["Area code"] != "[z]"].set_index("Area code")
    by_name = latest.set_index("Area name")
    pop_by_code = dict(zip(pop["GEOGRAPHY_CODE"], pop["OBS_VALUE"]))
    pop_by_name = dict(zip(pop["GEOGRAPHY_NAME"], pop["OBS_VALUE"]))  # Sheffield and Barnsley codes differ in Nomis
    itl = c.itl_lookup()

    out = []
    for nuts3 in c.regions_in("TL"):
        las = itl[itl["ITL325CD"] == nuts3][["LAD25CD", "LAD25NM"]].drop_duplicates()
        if nuts3 == "TLM20":  # the ONS lookup also lists North Ayrshire here; it belongs to TLM93
            las = las[las["LAD25NM"] != "North Ayrshire"]
        las = las.assign(population=[pop_by_code.get(code, pop_by_name.get(name)) for code, name in zip(las["LAD25CD"], las["LAD25NM"])])
        place = c.place(nuts3)

        if nuts3.startswith("TLN"):
            town, brma = NI_BRMA[nuts3]
            r = by_name.loc[brma]
            month = r["Time period"].strftime("%Y-%m")
            out.append(c.row(place, float(r["rent"]), "GBP", "per_month", month, place, SOURCE_ID,
                             f"ONS PIPR mean rent of a two-bed in the {brma} (BT postcode districts; holds {town}, main town of the "
                             f"region), advertised new lets, {month} (Northern Ireland ends July 2026)."))
        elif nuts3.startswith("TLM"):
            main = las.sort_values("population", ascending=False).iloc[0]
            brma = SCOTS_BRMA[main["LAD25NM"]]
            r = by_name.loc[brma]
            month = r["Time period"].strftime("%Y-%m")
            out.append(c.row(place, float(r["rent"]), "GBP", "per_month", month, place, SOURCE_ID,
                             f"ONS PIPR mean rent of a two-bed in the {brma} Broad Rental Market Area, which holds {main['LAD25NM']} "
                             f"(largest council area of the region); mostly advertised new lets, {month}. The BRMA is wider than the town."))
        elif nuts3.startswith("TLI"):  # London: group of boroughs
            las = las[las["LAD25CD"].isin(by_code.index)]
            rents = las["LAD25CD"].map(by_code["rent"])
            value = float((rents * las["population"]).sum() / las["population"].sum())
            names = ", ".join(las["LAD25NM"])
            month = by_code.loc[las["LAD25CD"].iloc[0], "Time period"].strftime("%Y-%m")
            out.append(c.row(place, value, "GBP", "per_month", month, place, SOURCE_ID,
                             f"ONS PIPR mean rent of a two-bed (all tenancies), population-weighted over the boroughs of the region: {names}, {month}."))
        else:
            las = las[las["LAD25CD"].isin(by_code.index)].copy()
            las["town_population"] = [_town_population(n, p) for n, p in zip(las["LAD25NM"], las["population"])]
            if nuts3 in MAIN_LA:
                main = las[las["LAD25NM"] == MAIN_LA[nuts3]].iloc[0]
            elif las["town_population"].notna().any():  # the authority named after the region's biggest town
                main = las.sort_values("town_population", ascending=False).iloc[0]
            else:
                main = las.sort_values("population", ascending=False).iloc[0]
            r = by_code.loc[main["LAD25CD"]]
            month = r["Time period"].strftime("%Y-%m")
            measured = _town_code(main["LAD25NM"], main["population"]) or place
            out.append(c.row(place, float(r["rent"]), "GBP", "per_month", month, measured, SOURCE_ID,
                             f"ONS PIPR mean rent of a two-bed (new and existing tenancies) in {main['LAD25NM']} local authority "
                             f"(holds the region's largest town, else the most populous authority), {month}."))
    return out
