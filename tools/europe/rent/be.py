"""Belgium: the CIB/Korfine rental barometer (new leases through estate agents), first half of 2026.

Flanders and Brussels: average apartment rent by municipality (CIB Huurbarometer, datawrapper maps), main town of each
arrondissement. Wallonia: Federia's barometer (same method, same partners) publishes only by province, so each
Walloon arrondissement gets its province's average rent for all dwelling types.
"""

import re

import pandas as pd

import common as c

CIB_ID = "be-cib-huurbarometer"
FEDERIA_ID = "be-federia-barometre"
# datawrapper chart versions current on 2026-11-17; column "Gemiddelde" is the first half of 2026.
FLANDERS = "https://datawrapper.dwcdn.net/2EjX0/6/dataset.csv"   # apartments, Flemish municipalities
BRUSSELS = "https://datawrapper.dwcdn.net/HXMqw/16/dataset.csv"  # apartments, Brussels communes
PERIOD = "2026-H1"

# Federia barometer, first half of 2026, average rent of new leases, all dwelling types (Belga, 2026-09-11).
WALLONIA_PROVINCE = {"BE31": ("Brabant wallon", 1218), "BE32": ("Hainaut", 847), "BE33": ("Liège", 848),
                     "BE34": ("Luxembourg", 910), "BE35": ("Namur", 895)}

SOURCES = [
    c.source(CIB_ID, "CIB (Confederatie van Immobiliënberoepen) and Korfine",
             "Huurbarometer: average rent of new leases by municipality, apartments, Flanders and Brussels",
             "https://www.cib.be/sector-inzichten-overzicht/b4f7e61a-5171-41fa-a5b7-065e6a55be2f",
             "Free to read, no licence stated", PERIOD,
             "Leases signed through estate agents (not private landlords), mean rent excluding charges. Chart data "
             "from the datawrapper maps embedded in the CIB page."),
    c.source(FEDERIA_ID, "Federia (francophone estate agents) with CIB and Korfine",
             "Baromètre des locations, 1st half 2026: average rent of new leases by Walloon province",
             "https://www.parismatch.be/actualites/2026/09/11/bonne-nouvelle-pour-les-locataires-la-hausse-du-prix-des-loyers-ralentit-en-wallonie-et-a-bruxelles-RAULMJRLRRELPPCGU4Y7743VGY/",
             "Free to read, no licence stated", PERIOD,
             "Figures as reported by Belga (Paris Match, 2026-09-11); Federia's own site was unreachable."),
]


def _table() -> pd.DataFrame:
    frames = [pd.read_csv(c.fetch(CIB_ID, url, name), dtype=str)
              for url, name in [(FLANDERS, "flanders-apartments.csv"), (BRUSSELS, "brussels-apartments.csv")]]
    df = pd.concat(frames).dropna(subset=["X.1", "Gemeente"])
    df["rent"] = pd.to_numeric(df["Gemiddelde"], errors="coerce")
    return df[df["rent"] > 0]


def _key(name: str) -> str:
    return c._fold(re.sub(r"\(.*?\)", "", name))


def rows():
    table = _table()
    by_code = dict(zip(table["X.1"], table["rent"]))
    by_name = {_key(n): r for n, r in zip(table["Gemeente"], table["rent"])}
    lau = c.lau()
    lau = lau[lau["country"] == "BE"].copy()
    lau["rent"] = [by_code.get(code, by_name.get(_key(name))) for code, name in zip(lau["lau_code"], lau["name"])]
    out = []
    for nuts3 in c.regions_in("BE"):
        region = lau[lau["nuts3"] == nuts3]
        if nuts3[:4] in WALLONIA_PROVINCE:
            province, rent = WALLONIA_PROVINCE[nuts3[:4]]
            out.append(c.row(
                c.place(nuts3), rent, "EUR", "per_month", PERIOD, f"NUTS-{nuts3[:4]}", FEDERIA_ID,
                f"Federia barometer: average rent of new leases (all dwelling types) in the province of {province}, "
                f"first half of 2026. Federia publishes nothing finer for Wallonia; same figure for every "
                f"arrondissement of the province."))
            continue
        town = c.main_towns(nuts3, region).iloc[0]
        rent = by_code.get(town["lau_code"], by_name.get(_key(town["name"])))
        if rent is not None:
            code = c.place(nuts3) if pd.isna(town["city_code"]) else town["city_code"]
            out.append(c.row(
                c.place(nuts3), rent, "EUR", "per_month", PERIOD, code, CIB_ID,
                f"CIB/Korfine barometer: average apartment rent of new leases through estate agents in {town['name']}, "
                f"first half of 2026 (all apartment sizes, excluding charges)."))
            continue
        rents = region["rent"].dropna()
        out.append(c.row(
            c.place(nuts3), float(rents.median()), "EUR", "per_month", PERIOD, c.place(nuts3), CIB_ID,
            f"CIB/Korfine barometer has no figure for {town['name']}; median of the {len(rents)} municipalities of the "
            f"arrondissement that have one (average apartment rent of new leases, first half of 2026)."))
    return out
