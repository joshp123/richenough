"""Germany: BBSR's 2025 asking rents by Kreis, adjusted to each Kreis's main town with Zensus 2022 new-tenancy rents.

Level: BBSR (via the Deutschlandatlas data file), net cold rent (nettokalt) asked in internet listings for re-let
unfurnished flats of 40 to 100 m2, 2025, EUR/m2, one figure per Kreis (400 = the 400 NUTS 3 regions).
Town pattern: Zensus 2022 (15 May 2022), average net cold rent of households that had lived in their flat under one
year (i.e. a new let), per municipality and per Kreis. Town figure = Kreis asking rent x (main town / Kreis Zensus
new-tenancy rent) x 75 m2. For a kreisfreie Stadt the town is the Kreis and the factor is 1.
"""

import json
import re

import common as c
import pandas as pd

BBSR_ID = "bbsr-angebotsmieten-de"
BBSR_URL = "https://deutschlandatlas.bund.de/fileadmin/Downloaddateien/Open_Data/Deutschlandatlas_Daten.xlsx"
ZENSUS_ID = "zensus2022-wohndauer-miete"
ZENSUS_API = "https://ergebnisse.zensus2022.de/proxy/api/rest"
TABLE = "5000H-0009"  # average net cold rent per household (EUR/m2) by duration of occupancy
NEW = "WOHND000B001"  # under 1 year

SOURCES = [
    c.source(
        BBSR_ID, "Federal Institute for Research on Building, Urban Affairs and Spatial Development (BBSR), published "
        "by the Federal Ministry of Housing (BMWSB) in the Deutschlandatlas",
        "Deutschlandatlas data table KRS1224, indicator preis_miet: re-letting rents of advertised flats "
        "(asking rents, net cold) 2025, EUR/m2, by Kreis",
        BBSR_URL, "Reproduction and distribution, also in part, permitted with attribution (BMWSB, Deutschlandatlas "
        "data table imprint)", "2025",
        "Average net cold asking rent in internet listings of unfurnished existing flats offered for re-letting, "
        "40 to 100 m2, medium to good location (BBSR Wohnungsmarktbeobachtung, listings from IDN ImmoDaten). "
        "Federal average 2025: 11.11 EUR/m2."),
    c.source(
        ZENSUS_ID, "Statistical Offices of the Federation and the Laender (Zensus 2022)",
        f"Zensus 2022 table {TABLE}: average net cold rent per household (EUR/m2) by duration of occupancy, "
        "by municipality and Kreis, 15 May 2022",
        f"{ZENSUS_API}/tables/{TABLE}/data", "Datenlizenz Deutschland - Namensnennung - Version 2.0 (dl-de/by-2-0)",
        "2022-05-15",
        "Households resident in their flat for under one year at the census date, so rents agreed May 2021 to May "
        "2022. Used only as the ratio of the main town to its Kreis."),
]


def _zensus(block: str, filename: str) -> dict:
    """Zensus table 5000H-0009 for all Kreise (block v6) or all municipalities (block v8), cached.

    The keyless web API wants the table's own initial state back with the region variable swapped in.
    """
    structure = json.loads(c.fetch(ZENSUS_ID, f"{ZENSUS_API}/tables/{TABLE}/structure", "structure.json").read_text())
    state = structure["initialState"]
    state["tableStructure"]["colTitle"][0]["blockCode"] = block
    path = c.fetch(ZENSUS_ID, f"{ZENSUS_API}/tables/{TABLE}/data", filename, data=json.dumps(state).encode(),
                   headers={"Content-Type": "application/json"})
    data = json.loads(path.read_text())["data"][0]
    index = {k: v["category"]["index"] for k, v in data["dimension"].items()}
    key = data["id"][-1]
    n = len(index[key])
    column = index["WOHND1"][NEW]
    return {code: data["value"][column * n + i] for code, i in index[key].items()
            if data["status"][column * n + i] in ("e", "()")}


def _bbsr() -> dict:
    path = c.fetch(BBSR_ID, BBSR_URL, "Deutschlandatlas_Daten.xlsx")
    sheet = pd.read_excel(path, sheet_name="Deutschlandatlas_KRS1224", header=None)
    header = list(sheet.iloc[3])
    col = next(i for i, h in enumerate(header) if isinstance(h, str) and "preis_miet" in h)
    body = sheet.iloc[4:]
    body = body[pd.to_numeric(body[0], errors="coerce").notna()]
    return {str(int(code)).zfill(8)[:5]: float(v) for code, v in zip(body[0], body[col])}


# Main towns that GeoNames lists under another name or not at all: Weilheim i.OB, Weiden i.d.OPf., Weissenburg i.Bay.,
# Aue (part of Aue-Bad Schlema), Sankt Wendel; and the name clashes Frankfurt (Oder), Luechow, Eisenberg (Pfalz). Bad Krozingen, Spremberg and Herxheim bei Landau have no GeoNames
# entry of their own, so their rows are measured_for the NUTS 3 region.
CITY_OVERRIDES = {"DE21N": "CITY-2812515", "DE233": "CITY-2813040", "DE25C": "CITY-2811909", "DED42": "CITY-2954695",
                  "DEC06": "CITY-2841463", "DE403": "CITY-2925535", "DE934": "CITY-2875542",
                  "DEB3D": "CITY-2931522"}


def _city(name: str):
    """GeoNames id for a German LAU name such as 'Weilheim i.OB, St' (abbreviated qualifiers, status suffixes)."""
    base = name.split(",")[0].strip()
    spaced = base.replace("a.d.", "an der ").replace("a.Main", "am Main").replace("a. d.", "an der").replace("  ", " ")
    candidates = [base, spaced]
    for candidate in candidates:
        code = c.city_code("DE", candidate.strip())
        if code:
            return code
    return None


def rows():
    kreis_rent = _bbsr()
    zensus_kreis = _zensus("v6", "5000H-0009_kreise.json")
    zensus_town = {}
    for ars, value in _zensus("v8", "5000H-0009_gemeinden.json").items():
        zensus_town[ars[:5] + ars[9:12]] = value  # 12-digit key to 8-digit municipality code (AGS)

    lau = c.lau()
    lau = lau[lau["country"] == "DE"]
    kreis_of = lau.groupby("nuts3")["lau_code"].first().str[:5]

    out = []
    for nuts3 in c.regions_in("DE"):
        kreis = kreis_of[nuts3]
        level = kreis_rent[kreis]
        town = c.main_towns(nuts3).iloc[0]
        town_value, kreis_value = zensus_town.get(town["lau_code"]), zensus_kreis.get(kreis)
        if town_value and kreis_value:
            factor = town_value / kreis_value
            why = (f"Zensus 2022 new-tenancy rent {town_value:.2f} EUR/m2 in {town['name']} against "
                   f"{kreis_value:.2f} in the Kreis, factor {factor:.3f}")
        else:
            factor, why = 1.0, "no Zensus figure for the town, Kreis figure used unadjusted"
        measured = CITY_OVERRIDES.get(nuts3) or (town["city_code"] if isinstance(town["city_code"], str) else None) \
            or _city(town["name"]) or c.place(nuts3)
        note = (f"BBSR 2025 asking rent for re-let flats in the Kreis, net cold (excludes service and heating charges), "
                f"{level:.2f} EUR/m2, x {factor:.3f} for {town['name']} ({why}), x 75 m2. "
                f"Main town = largest municipality of the Kreis. Sources: {BBSR_ID}, {ZENSUS_ID}.")
        out.append(c.row(c.place(nuts3), level * factor * c.TWO_BED_M2, "EUR", "per_month", "2025", measured,
                         BBSR_ID, note))
    return out
