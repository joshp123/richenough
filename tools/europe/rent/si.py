"""Slovenia: GURS's last residential rent report (2016-17 contracts, by municipality) scaled to today's asking rent.

No current official regional rent source exists. GURS (the Surveying and Mapping Authority) says landlords under-report
rents to the tax authority and has not published residential rents since the 2016-17 report. The report is the only
official local pattern: weighted average rent per m2 of market leases of 6+ months, by municipality (35 municipalities
in 27 analytical areas). We keep that pattern as ratios to Ljubljana and set Ljubljana to the average advertised rent
per m2 of 2024 (19.30 EUR, Najemniski SOS from nepremicnine.net listings, as quoted in Svet24, 9 July 2025).
Per-m2 rents of the average (about 51 m2) flat are scaled to 75 m2 with rent proportional to area^0.66 (exponent from
Czechia's Ministry of Finance rent map, see rent/hu.py). The result is only as good as the single Ljubljana level.
"""

import common as c

SOURCE_ID = "si-gurs-najemni-trg-2017"
SOURCE_LEVEL = "si-najemniski-sos-2024"
URL = ("https://www.e-prostor.gov.si/fileadmin/Podrocja/Trg_vrednosti_nep/Trg_nepremicnin/Porocila_o_trgu_nepremicnin/"
       "2017/Porocilo_najemni_trg_2017.pdf")
LEVEL_URL = "https://najemniski-sos.si/porocilo/"
LEVEL_ARTICLE = "https://svet24.si/novice/slovenija/mnozicno-vrednotenje-nepremicnin-oddajanje-nadzor-financna-uprava-1831696"

SOURCES = [
    c.source(SOURCE_ID, "Surveying and Mapping Authority of Slovenia (GURS)",
             "Porocilo o najemnem trgu nepremicnin za leti 2016 in 2017 (table 2: rents of flats by municipality)",
             URL, "free to read, no licence stated (official report)", "2017",
             "Weighted average monthly rent per m2 of market leases of flats (6+ months), from the real-estate market "
             "register. Used only for the pattern between municipalities: GURS says landlords report low rents."),
    c.source(SOURCE_LEVEL, "Najemniski SOS (Institut Danes je nov dan)",
             "Neznosna nedostopnost bivanja; average advertised rent in Ljubljana 19.30 EUR/m2 (2024), quoted by Svet24",
             LEVEL_ARTICLE, "free to read, no licence stated", "2024",
             "Average advertised rent per m2 of rental flats in Ljubljana, from nepremicnine.net listings. The year "
             "('lani', last year) is inferred from the 9 July 2025 article; the report itself is " + LEVEL_URL),
]

LJUBLJANA_ASKING = 19.30  # EUR per m2 per month, 2024
AVERAGE_FLAT_M2 = 51      # GURS 2016-17 average let flat
SIZE_EXPONENT = 0.66

# GURS table 2, 2017: weighted average rent EUR/m2 by analytical area (the area holding each region's main town)
GURS_2017 = {
    "SI041": ("Ljubljana", 6.9), "SI032": ("Maribor", 4.6), "SI034": ("Celje", 4.6), "SI042": ("Kranj", 4.7),
    "SI044": ("Koper", 5.5), "SI037": ("Novo mesto", 4.5), "SI043": ("Nova Gorica", 4.7),
    "SI035": ("Zagorje, Trbovlje and Hrastnik", 2.9), "SI036": ("Brezice and Krsko", 3.8),
    "SI033": ("Slovenj Gradec, Ravne and Prevalje", 4.1), "SI038": ("Postojna", 4.5), "SI031": ("Murska Sobota", 3.7),
}
TOWN = {"SI035": "Zagorje ob Savi", "SI036": "Krško", "SI033": "Slovenj Gradec"}


def rows():
    c.fetch(SOURCE_ID, URL, "najemni_trg_2017.pdf")
    reference = GURS_2017["SI041"][1]
    size = (c.TWO_BED_M2 / AVERAGE_FLAT_M2) ** SIZE_EXPONENT / (c.TWO_BED_M2 / AVERAGE_FLAT_M2)  # per-m2 factor
    out = []
    for nuts3 in c.regions_in("SI"):
        area, gurs = GURS_2017[nuts3]
        per_m2 = LJUBLJANA_ASKING * gurs / reference * size
        town = TOWN.get(nuts3) or c.main_towns(nuts3).iloc[0]["name"].split("/")[0]
        measured = c.city_code("SI", town) or c.place(nuts3)
        out.append(c.row(
            c.place(nuts3), round(per_m2 * c.TWO_BED_M2, -1), "EUR", "per_month", "2024", measured,
            SOURCE_ID,
            f"GURS 2017 rent in {area} {gurs} EUR/m2 vs Ljubljana {reference} (ratio {gurs / reference:.2f}) x "
            f"Ljubljana 2024 advertised rent {LJUBLJANA_ASKING} EUR/m2 x size factor {size:.3f} (to 75 m2) x 75 m2. "
            f"Pattern is 2017 leases (source {SOURCE_ID}), level is one 2024 advertised average (source {SOURCE_LEVEL})."))
    return out
