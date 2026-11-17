"""Hungary: HCSO (KSH)-ingatlan.com rent index, average advertised monthly rent, 2026 first half.

Table 4 of the October 2026 edition gives the average advertised monthly rent (thousand HUF) and table 5 the average
floor area (m2) of rental ads on ingatlan.com, for Budapest, Pest county and, for each of the six other NUTS 2
regions, its county towns together. The average ad is a small flat (53 to 61 m2, bigger in Pest county), so we scale its rent to 75 m2 with rent
proportional to area^0.66. The exponent comes from Czechia's Ministry of Finance rent map (median ratio of the
per-m2 rent of 3+kk to 2+kk flats, 0.92, over the 309 well-covered cadastral areas, between 54 and 70 m2); Hungary
publishes no size breakdown. Without it the figure would be 10 to 12 percent higher.
The six regions' counties share one figure (the region's county-town average): the source has nothing finer, and
the 19 county towns differ a lot inside a region (the press reports Szeged about twice Bekescsaba).
"""

import pandas as pd

import common as c

SOURCE_ID = "hu-ksh-ingatlan-rent"
BASE = "https://www.ksh.hu/s/en/experimental-statistics/publications/hcsoingatlancom-rent-index-october-2026/"
URL = BASE + "table-attachment.xlsx"
SAFARI = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) "
                        "Version/17.0 Safari/605.1.15"}  # ksh.hu's firewall rejects the default agent

SOURCES = [c.source(
    SOURCE_ID, "Hungarian Central Statistical Office (KSH/HCSO) with ingatlan.com",
    "HCSO-ingatlan.com rent index, October 2026 (tables 4 and 5: average rent and floor area by region)",
    BASE, "free to read, no licence stated (HCSO experimental statistics)", "2026-H1",
    "Average advertised monthly rent of homes (flats and houses) on ingatlan.com, half-yearly, by region and county towns.")]

# column of the rent table (and the area table) for each NUTS 2 region: county towns, or the whole county for Pest
SIZE_EXPONENT = 0.66  # rent proportional to floor area to this power, from the Czech MF rent map
COLUMN = {"HU11": 2, "HU12": 3, "HU21": 6, "HU22": 8, "HU23": 10, "HU31": 12, "HU32": 14, "HU33": 16}


def rows():
    path = c.fetch(SOURCE_ID, URL, "rent-index-2026-10.xlsx", headers=SAFARI)
    sheets = pd.read_excel(path, sheet_name=None, header=None)
    rent, area = sheets["3"], sheets["4"]
    row = rent.index[(rent[0] == 2026) & (rent[1] == "I.")][0]
    out = []
    for nuts3 in c.regions_in("HU"):
        nuts2 = nuts3[:4]
        col = COLUMN[nuts2]
        thousand_huf, m2 = float(rent.at[row, col]), float(area.at[row, col])
        per_m2 = thousand_huf * 1000 / m2
        amount = thousand_huf * 1000 * (c.TWO_BED_M2 / m2) ** SIZE_EXPONENT
        if nuts2 in ("HU11", "HU12"):
            scope, measured = ("Budapest" if nuts2 == "HU11" else "Pest county (all ads, houses included)"), c.place(nuts3)
            if nuts2 == "HU11":
                measured = c.city_code("HU", "Budapest") or measured
        else:
            scope, measured = "county towns of the region together", c.place(nuts2)
        out.append(c.row(
            c.place(nuts3), round(amount, -2), "HUF", "per_month", "2026-H1", measured, SOURCE_ID,
            f"HCSO-ingatlan.com, {scope}: average advertised rent {thousand_huf:.0f} thousand HUF for {m2:.0f} m2 "
            f"scaled to 75 m2 by (75/{m2:.0f})^0.66. Same figure for every county of the NUTS 2 region."
            if nuts2 not in ("HU11", "HU12") else
            f"HCSO-ingatlan.com, {scope}: average advertised rent {thousand_huf:.0f} thousand HUF for {m2:.0f} m2 "
            f"scaled to 75 m2 by (75/{m2:.0f})^0.66."))
    return out
