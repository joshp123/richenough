"""Luxembourg: the Observatoire de l'Habitat's advertised apartment rents (immotop.lu listings), by commune.

Mean advertised rent per m2 for Luxembourg city, July 2025 to June 2026. The mean is dominated by small flats (about
40 m2 on average), whose rent per m2 is far above that of a 75 m2 two-bed. The Observatoire's 2025 report gives the
national mean rent per m2 for all apartments (39.7) and for apartments of 70 to 89 m2 (26.9); that ratio scales the
city's mean rent per m2 to a two-bed's.
"""

import pandas as pd

import common as c

SOURCE_ID = "lu-observatoire-loyers"
URL = "https://download.data.public.lu/resources/loyers-annonces-des-logements-par-commune/20260924-085311/location-appartement-2025-26.xls"
REPORT = "https://gouvernement.lu/dam-assets/images-documents/actualites/2026/09-septembre/30-observatoire-habitat/rapport-loyers-annoncs-en-2025.pdf"
MEAN_ALL_M2, MEAN_70_89_M2 = 39.7, 26.9  # report, table 2 and figure 5 (2025, apartments, EUR/m2)
PERIOD = "2025-07/2026-06"

SOURCES = [
    c.source(SOURCE_ID, "Observatoire de l'Habitat (Ministère du Logement), via data.public.lu",
             "Loyers annoncés des logements - Par commune: apartments, last 12 months", URL, "CC0 (cc-zero)",
             PERIOD,
             "Asking rents of new lets from immotop.lu listings; mean rent and mean rent per m2 per commune. The size "
             f"scaling uses the Observatoire's report {REPORT}."),
]


def rows():
    path = c.fetch(SOURCE_ID, URL, "location-appartement-2025-26.xls")
    df = pd.read_excel(path, header=None, skiprows=9, usecols=[2, 3, 4, 5])
    df.columns = ["commune", "offers", "rent", "rent_m2"]
    city = df[df["commune"].astype(str).str.strip() == "Luxembourg"].iloc[0]
    scale = MEAN_70_89_M2 / MEAN_ALL_M2
    amount = round(float(city["rent_m2"]) * scale * c.TWO_BED_M2)
    return [c.row(
        "NUTS-LU000", amount, "EUR", "per_month", PERIOD, c.city_code("LU", "Luxembourg") or "NUTS-LU000", SOURCE_ID,
        f"Mean advertised rent of apartments in Luxembourg city, {float(city['rent_m2']):.2f} EUR/m2 over "
        f"{int(city['offers'])} listings, x {scale:.3f} (national mean rent/m2 of 70-89 m2 flats {MEAN_70_89_M2} / all "
        f"flats {MEAN_ALL_M2}, Observatoire report on 2025) x 75 m2. Asking rents of new lets, no sitting tenants.")]
