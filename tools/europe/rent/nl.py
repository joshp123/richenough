"""Netherlands: Rent.nl's asking rents per m2 by municipality, calibrated to Pararius's free-sector level.

Rent.nl (Nationale Huurindex / Huurkaart) scans nearly all Dutch rental listings (platforms, agents, landlords) and
publishes the mean asking rent per m2 for every municipality and quarter. Its mean includes rooms and studios, which
cost far more per m2, so it runs about a quarter above Pararius's free-sector figure. For the 19 municipalities where
both publish, we take the median ratio (Pararius Q3 2026 / Rent.nl, n-weighted mean of the last four quarters) and
apply it to every municipality: Rent.nl gives the local pattern, Pararius the level. A 75 m2 two-bed follows.
"""

import json
import statistics

import pandas as pd

import common as c

SOURCE_ID = "nl-rentnl-huurkaart"
PARARIUS_ID = "nl-pararius-huurmonitor"
BASE = "https://www.rent.nl/huurindex/kaart/data/"
QUARTERS = ["2025Q4", "2026Q1", "2026Q2", "2026Q3"]
MIN_LISTINGS = 100  # a town needs this many listings over the four quarters, else its COROP region is used

# Pararius Huurmonitor Q3 2026, average free-sector rent per m2 for new tenants, by CBS municipality code.
# Pararius blocks plain fetches, so these are as reproduced on hubsnap.nl (cache/nl-pararius-huurmonitor/).
PARARIUS_Q3_2026 = {
    "GM0363": 28.56, "GM0392": 24.34, "GM0546": 23.45, "GM0518": 22.95, "GM0599": 22.92, "GM0344": 22.87,
    "GM0503": 22.49, "GM0772": 19.61, "GM0268": 19.36, "GM0014": 19.05, "GM0935": 18.87, "GM0758": 18.75,
    "GM0034": 18.69, "GM0307": 17.81, "GM0855": 17.64, "GM0202": 17.24, "GM0153": 15.98, "GM0200": 15.70,
    "GM0193": 14.32,
}
MAIN_TOWN = {"NL362": "GM0503"}  # Delft rather than Westland (a municipality of glasshouse villages)

SOURCES = [
    c.source(SOURCE_ID, "Rent.nl (Nationale Huurindex)",
             "Huurkaart: average asking rent per m2 by province, municipality and quarter, Q2 2024 to Q3 2026",
             "https://www.rent.nl/huurindex/kaart/", "Free to read, no licence stated (data for research on request)",
             "2025Q4-2026Q3",
             "Mean of rent/m2 over all listings Rent.nl found, including rooms and studios; service costs excluded; "
             "areas under the listing threshold are blank."),
    c.source(PARARIUS_ID, "Pararius",
             "Huurmonitor Q3 2026: average rent per m2 of free-sector homes let to new tenants, by city",
             "https://www.pararius.nl/huurmonitor", "Free to read, no licence stated", "2026-Q3",
             "Used only to calibrate Rent.nl's level. Pararius blocks plain fetches; figures taken from the "
             "reproduction at https://www.hubsnap.nl/blog/average-rent-netherlands."),
]


def _areas() -> dict:
    """Municipality code -> (listings, n-weighted mean rent/m2 over the four quarters)."""
    top = json.loads(c.fetch(SOURCE_ID, BASE + "landelijk/", "provincie.json", headers={"Accept": "application/json"}).read_text())
    out = {}
    for prov in top["features"]:
        path = c.fetch(SOURCE_ID, f"{BASE}provincie/{prov['slug']}/", f"prov-{prov['slug']}.json",
                       headers={"Accept": "application/json"})
        for f in json.loads(path.read_text())["features"]:
            series = [f["reeks"][q] for q in QUARTERS if q in f["reeks"]]
            n = sum(s["n"] for s in series)
            if n:
                out[f["code"]] = (n, sum(s["p"] * s["n"] for s in series) / n)
    return out


def _factor(areas: dict) -> float:
    ratios = [pararius / areas[code][1] for code, pararius in PARARIUS_Q3_2026.items() if code in areas]
    return statistics.median(ratios)


def rows():
    areas = _areas()
    factor = _factor(areas)
    matched = sum(code in areas for code in PARARIUS_Q3_2026)
    lau = c.lau()
    lau = lau[lau["country"] == "NL"].copy()
    lau["n"] = lau["lau_code"].map(lambda k: areas.get(k, (0, 0))[0])
    lau["p"] = lau["lau_code"].map(lambda k: areas.get(k, (0, 0))[1])
    out = []
    for nuts3 in c.regions_in("NL"):
        region = lau[lau["nuts3"] == nuts3]
        towns = c.main_towns(nuts3, region)
        if nuts3 in MAIN_TOWN:
            towns = towns.sort_values("lau_code", key=lambda s: s != MAIN_TOWN[nuts3], kind="stable")
        town = towns.iloc[0]
        if town["n"] >= MIN_LISTINGS:
            m2_rent, n, measured, where = town["p"], int(town["n"]), c.place(nuts3) if pd.isna(town["city_code"]) else town["city_code"], f"the municipality of {town['name']}"
        else:
            n = int(region["n"].sum())
            m2_rent = (region["n"] * region["p"]).sum() / n
            measured, where = c.place(nuts3), f"the whole region (the main town, {town['name']}, has only {int(town['n'])} listings)"
        out.append(c.row(
            c.place(nuts3), round(m2_rent * factor * c.TWO_BED_M2), "EUR", "per_month", "2025Q4-2026Q3", measured,
            SOURCE_ID,
            f"Rent.nl mean asking rent in {where}, {m2_rent:.2f} EUR/m2 over {n} listings (Q4 2025 to Q3 2026), "
            f"x {factor:.3f} (median of Pararius Q3 2026 / Rent.nl over {matched} municipalities, removes the rooms and "
            f"studios bias) x 75 m2. Asking rents of new lets, all sectors."))
    return out
