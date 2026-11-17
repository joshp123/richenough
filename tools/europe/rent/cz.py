"""Czechia: the Ministry of Finance's rent price map (cenova mapa najemneho), 15 Nov 2026 edition.

Estimated market rent per m2 for 3+kk / 3+3 flats (size category VK3, median 68-71 m2, the closest to our 75 m2
two-bedroom), by cadastral area, from asking rents of listings taken off the market (taken as a signed lease),
Oct 2021 to Sep 2026, weighted to 2026. For each kraj (NUTS 3) we take the main town's centre: the cadastral area
named like the town ("Plzen"), else "Mesto <town>", else the town's single row, else the median of its
well-covered cadastral areas. Overrides (the centres): Prague Nove Mesto, Olomouc "Olomouc-mesto", Ostrava "Moravska Ostrava".
"""

import pandas as pd

import common as c

SOURCE_ID = "cz-mf-cenova-mapa"
URL = "https://mf.gov.cz/assets/attachments/2026-11-15_Cenova-mapa.xlsx"
PAGE = "https://mf.gov.cz/cs/rozpoctova-politika/podpora-projektoveho-rizeni/cenova-mapa/cenova-mapa-infografika"

SOURCES = [c.source(
    SOURCE_ID, "Ministry of Finance of the Czech Republic",
    "Cenova mapa najemneho (rent price map), tabular output of 15 November 2026 (data to 30 September 2026)",
    PAGE, "free to read, no licence stated (official map under Act 151/1997 and decree 456/2024)", "2026-Q3",
    "Estimated market rent per m2 of an unfurnished reference flat in good condition, from asking rents of listings "
    "removed from portals (treated as let), by cadastral area and size category. Updated quarterly.")]

VK3_REF_COL = 25   # "Najemne referencniho bytu za m2", size category 3 (3+kk, 3+3)
VK3_COVER_COL = 32
OVERRIDE = {"CZ010": "Nové Město", "CZ071": "Olomouc-město", "CZ080": "Moravská Ostrava"}


def rows():
    path = c.fetch(SOURCE_ID, URL, "2026-11-15_Cenova-mapa.xlsx")
    d = pd.read_excel(path, sheet_name="Cenové mapy nájemného", header=None, skiprows=1)
    d = d[[0, 1, 2, 3, VK3_REF_COL, VK3_COVER_COL]]
    d.columns = ["kraj", "ku", "obec", "kod", "rent", "cover"]
    d = d.dropna(subset=["rent"])
    d["obec_f"] = d["obec"].map(c._fold)
    lau = c.lau()
    out = []
    for nuts3 in c.regions_in("CZ"):
        towns = c.main_towns(nuts3)
        for town in towns.itertuples():
            s = d[d["obec_f"] == c._fold(town.name)]
            if s.empty:
                continue
            ku = s["ku"].map(lambda x: c._fold(x) if isinstance(x, str) else "")
            name = c._fold(OVERRIDE.get(nuts3, town.name))
            pick = s[ku == name]
            how = "cadastral area " + (OVERRIDE.get(nuts3) or town.name)
            if pick.empty:
                pick = s[ku == "mesto " + name]
                how = f"cadastral area Město {town.name}"
            if pick.empty and len(s) == 1:
                pick, how = s, "the municipality's single figure"
            if pick.empty:
                good = s[s["cover"] >= 4]
                pick = good if len(good) else s
                how = f"median of {len(pick)} cadastral areas of {town.name}"
            rent = float(pick["rent"].median())
            measured = town.city_code or c.place(nuts3)
            out.append(c.row(
                c.place(nuts3), round(rent * c.TWO_BED_M2), "CZK", "per_month", "2026-Q3", measured, SOURCE_ID,
                f"MF rent price map, 3+kk reference flat, {rent:.0f} CZK/m2 x 75 m2 ({how}). Asking rents of "
                f"listings taken down (taken as let), unfurnished, good condition; data Oct 2021 to Sep 2026."))
            break
    return out
