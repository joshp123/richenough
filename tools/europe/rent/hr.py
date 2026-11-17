"""Croatia: median rent per m2 of registered lease contracts for flats, 2025 (MPGI / EIZ market review).

Source: "Pregled tržišta nekretnina Republike Hrvatske 2025" (Ekonomski institut Zagreb with the Ministry of Physical
Planning, Construction and State Assets), table 2.10 (by county) and table 2.14 (by large city). The
figures come from the tax administration's e-Nekretnine records of registered lease contracts (new contracts and
renewals registered in 2025), median EUR per m2 per month for flats/apartments of all sizes.

The values below are transcribed from those two tables (the PDF has no machine-readable data). Rule: the main town's
own median where the town has at least 25 contracts (table 2.14), else the county median (table 2.10, at least 25
flat contracts). Regions with neither (Virovitica-Podravina, Vukovar-Srijem) get no row.
"""

import common as c

SOURCE_ID = "hr-eiz-ptn2025"
URL = ("https://eizg.hr/userdocsimages/publikacije/serijske-publikacije/pregled%20tr%C5%BEi%C5%A1ta%20nekretnina/"
       "pregled_trzista_nekretnina_2025/PTN_2025_final.pdf")
PERIOD = "2025"

SOURCES = [c.source(
    SOURCE_ID, "Ekonomski institut Zagreb (EIZ) and Ministry of Physical Planning, Construction and State Assets (MPGI)",
    "Pregled tržišta nekretnina Republike Hrvatske 2025, chapter 2.2 Najam i zakup, tables 2.10 and 2.14",
    URL, "Free to read; no licence stated", PERIOD,
    "Median monthly rent per m2 of flats in lease contracts registered in 2025 (tax administration e-Nekretnine data), "
    "by county and large city. Registered contracts, not asking rents; includes renewals and all flat sizes.")]

# NUTS 3 -> (level, name for GeoNames, median EUR/m2, contracts). level "city": table 2.14; "county": table 2.10.
TABLE = {
    "HR021": ("county", None, 4.9, 27),         # Bjelovar-Bilogora (Bjelovar city: under 25)
    "HR023": ("county", None, 5.0, 50),         # Pozega-Slavonia (Pozega city: 19)
    "HR024": ("city", "Slavonski Brod", 7.1, 222),
    "HR025": ("city", "Osijek", 8.0, 893),
    "HR027": ("city", "Karlovac", 8.2, 380),
    "HR028": ("county", None, 5.5, 331),        # Sisak-Moslavina (Sisak city: under 25)
    "HR031": ("city", "Rijeka", 10.4, 206),
    "HR032": ("city", "Gospic", 5.1, 92),
    "HR033": ("county", None, 7.4, 189),        # Zadar (Zadar city: under 25)
    "HR034": ("city", "Sibenik", 7.5, 393),
    "HR035": ("city", "Split", 12.3, 1641),
    "HR036": ("city", "Pula", 9.8, 70),
    "HR037": ("city", "Dubrovnik", 13.7, 36),
    "HR050": ("city", "Zagreb", 12.8, 3341),    # table 2.10, City of Zagreb
    "HR061": ("city", "Cakovec", 6.5, 145),
    "HR062": ("city", "Varazdin", 8.5, 532),
    "HR063": ("city", "Koprivnica", 7.6, 136),
    "HR064": ("county", None, 8.3, 192),        # Krapina-Zagorje (Krapina city: under 25)
    "HR065": ("city", "Velika Gorica", 9.7, 500),
}


def rows():
    c.fetch(SOURCE_ID, URL, "PTN_2025_final.pdf")  # cached by hand: eizg.hr's certificate chain fails Python's check
    out = []
    for nuts3, (level, name, per_m2, contracts) in TABLE.items():
        measured = (c.city_code("HR", name) if name else None) or c.place(nuts3)
        where = f"the city of {name}" if level == "city" else "the county"
        out.append(c.row(
            c.place(nuts3), round(per_m2 * c.TWO_BED_M2), "EUR", "per_month", PERIOD, measured, SOURCE_ID,
            f"Median rent of flats in lease contracts registered in 2025 in {where}: {per_m2} EUR/m2 x 75 m2 "
            f"({contracts} contracts)."))
    return out
