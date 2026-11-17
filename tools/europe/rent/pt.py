"""Portugal: INE's median rent per m2 of new lease contracts, by municipality, 2025 (2026 methodology).

New contracts declared to the tax authority (Imposto do Selo, Modelo 2), all sizes 20 to 600 m2. For each NUTS 3
region we take its main municipality (common.main_towns) and price a 75 m2 two-bed at that municipality's median.
"""

import json

import common as c

SOURCE_ID = "ine-pt-rendas"
URL = "https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0014698&lang=EN"

SOURCES = [c.source(
    SOURCE_ID, "Statistics Portugal (INE)",
    "Median house rental value of new lease agreements (2026 methodology, EUR/m2) by NUTS 2024 and municipality; "
    "House rental statistics at local level (indicator 0014698)",
    URL, "CC BY 4.0", "2025",
    "Median of rents declared for new residential leases (tax form Modelo 2 of Imposto do Selo), all dwelling sizes.")]


def rows():
    data = json.loads(c.fetch(SOURCE_ID, URL, "0014698.json").read_text())[0]
    period = data["UltimoPref"]
    values = {x["geocod"]: float(x["valor"]) for x in data["Dados"][period] if x.get("valor")}
    names = {x["geocod"]: x["geodsg"] for x in data["Dados"][period]}

    lau = c.lau()
    lau = lau[lau["country"] == "PT"].copy()
    lau["municipality"] = lau["lau_code"].str.zfill(6).str[:4]
    population = lau.groupby(["nuts3", "municipality"])["population"].sum().reset_index()

    out = []
    for nuts3 in c.regions_in("PT"):
        towns = population[population["nuts3"] == nuts3].copy()
        towns["geocod"] = nuts3[2:] + towns["municipality"]
        towns["name"] = towns["geocod"].map(names)
        towns = c.main_towns(nuts3, towns.dropna(subset=["name"]))
        for town in towns.itertuples():
            geocod = town.geocod
            if geocod in values:
                name = names[geocod]
                measured = town.city_code or c.place(nuts3)
                out.append(c.row(
                    c.place(nuts3), values[geocod] * c.TWO_BED_M2, "EUR", "per_month", period, measured, SOURCE_ID,
                    f"Median rent of new leases in the municipality of {name}, {values[geocod]:.2f} EUR/m2 x 75 m2."))
                break
        else:
            if nuts3[2:] in values:
                out.append(c.row(
                    c.place(nuts3), values[nuts3[2:]] * c.TWO_BED_M2, "EUR", "per_month", period, c.place(nuts3),
                    SOURCE_ID, f"Median rent of new leases in the region, {values[nuts3[2:]]:.2f} EUR/m2 x 75 m2."))
    return out
