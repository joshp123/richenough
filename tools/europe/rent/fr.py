"""France: ANIL "carte des loyers" 2025, asking rent per m2 (charges comprises) of a 3-room-or-more flat, by commune.

One row per departement (NUTS 3). Main town: the prefecture, unless another commune has more than 3x its population.
Paris, Lyon and Marseille are published by arrondissement; we take the population-weighted mean.
Mayotte is outside the source and gets no row.
"""

import json

import pandas as pd

import common as c

SOURCE_ID = "anil-carte-loyers-2025"
BASE = ("https://static.data.gouv.fr/resources/carte-des-loyers-indicateurs-de-loyers-dannonce-par-commune-en-2025/"
        "20251211-144951/pred-app3-mef-dhup.csv")
COG_URL = "https://www.insee.fr/fr/statistiques/fichier/8377162/v_departement_2025.csv"
ARR_URL = "https://geo.api.gouv.fr/communes?type=arrondissement-municipal&fields=nom,code,population,codeDepartement&format=json"
M2 = c.TWO_BED_M2  # the source models a 72 m2 T3+ flat; its rate per m2 is applied to 75 m2 like every other country
BIGGER = 3.0  # another commune replaces the prefecture only if this many times larger
CITY_ARRONDISSEMENTS = {"75056": "75", "69123": "69", "13055": "13"}  # Paris, Lyon, Marseille: INSEE code -> departement
OVERSEAS = {"FRY1": "GP", "FRY2": "MQ", "FRY3": "GF", "FRY4": "RE"}  # GeoNames files overseas departements as countries

SOURCES = [
    c.source(SOURCE_ID, "ANIL, with the housing ministry (DGALN)",
             '"Carte des loyers" - Indicateurs de loyers d\'annonce par commune en 2025, flats of 3 rooms or more',
             "https://www.data.gouv.fr/datasets/carte-des-loyers-indicateurs-de-loyers-dannonce-par-commune-en-2025/",
             "Licence Ouverte 2.0 (credit: Estimations ANIL, a partir des donnees du Groupe SeLoger et de leboncoin)",
             "2025-Q3",
             "Modelled asking rent per m2, charges comprises, unfurnished 72 m2 flat of 3+ rooms, listed in Q3 2025; "
             "from 9.1 million listings (leboncoin, SeLoger) 2019-2025."),
    c.source("insee-cog-2025", "INSEE", "Code officiel geographique 2025: departements and their chef-lieu (prefecture)",
             COG_URL, "Licence Ouverte 2.0", "2025"),
    c.source("geo-api-gouv", "Etalab (geo.api.gouv.fr)", "Population of Paris, Lyon and Marseille arrondissements",
             ARR_URL, "Licence Ouverte 2.0", "2025"),
]


def rows():
    rent = pd.read_csv(c.fetch(SOURCE_ID, BASE, "pred-app3.csv"), sep=";", decimal=",", encoding="latin-1",
                       dtype={"INSEE_C": str, "DEP": str})
    rent = rent.set_index("INSEE_C")
    cog = pd.read_csv(c.fetch("insee-cog-2025", COG_URL, "v_departement_2025.csv"), dtype=str)
    arr = pd.DataFrame(json.loads(c.fetch("geo-api-gouv", ARR_URL, "arrondissements.json").read_text()))

    lau = c.lau()
    lau = lau[lau["country"] == "FR"]
    pref = cog.set_index("CHEFLIEU")["LIBELLE"]
    out = []
    for nuts3 in c.regions_in("FR"):
        towns = lau[lau["nuts3"] == nuts3].sort_values("population", ascending=False)
        prefecture = towns[towns["lau_code"].isin(pref.index)]
        top = towns.iloc[0]
        town = prefecture.iloc[0] if len(prefecture) else top
        if len(prefecture) and top["population"] > BIGGER * town["population"]:
            town = top
        code = town["lau_code"]
        name = town["name"]
        why = "prefecture" if code in pref.index else f"largest commune (more than {BIGGER:.0f}x the prefecture)"
        if code in CITY_ARRONDISSEMENTS:
            a = arr[arr["code"].isin(rent.index) & (arr["codeDepartement"] == CITY_ARRONDISSEMENTS[code])]
            value = (rent.loc[a["code"], "loypredm2"].to_numpy() * a["population"].to_numpy()).sum() / a["population"].sum()
            level = f"mean of its {len(a)} arrondissements weighted by population"
            quality = ""
        elif code in rent.index:
            r = rent.loc[code]
            value = r["loypredm2"]
            level = {"commune": "commune level", "maille": "level of a group of neighbouring communes",
                     "EPCI": "level of the intercommunal authority"}[r["TYPPRED"]]
            quality = f" 95% interval {r['lwr.IPm2']:.1f} to {r['upr.IPm2']:.1f} EUR/m2; {r['nbobs_com']} listings in the commune."
        else:
            continue  # Mayotte
        out.append(c.row(
            c.place(nuts3), round(value * M2, 0), "EUR", "per_month", "2025-Q3",
            c.city_code(OVERSEAS.get(nuts3[:4], "FR"), name, str(name).split("-")[0]) or c.place(nuts3), SOURCE_ID,
            f"Asking rent, charges comprises, of a new let of an unfurnished flat of 3+ rooms in {name} "
            f"({why}), {level}: {value:.2f} EUR/m2 (modelled for a 72 m2 flat) x 75 m2.{quality} Modelled from listings, not a median."))
    return out
