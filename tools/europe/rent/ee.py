"""Estonia: asking rents of flats in each region's main town, from City24's public listing API, 17 Nov 2026.

No official source: Statistics Estonia stopped its rent tables in 2009 and the Land and Spatial Development Board
publishes sale transactions only. City24 is Estonia's second-largest property portal (KV.ee, the largest, blocks
automated reads). We read every flat for rent (about 1,800) and, for each main town, price a 75 m2 two-bed at 75 x the
median rent per m2 of its flats of 55 to 100 m2. Kesk-Eesti has no town with enough ads; its three counties (Lääne-Viru,
Järva, Rapla) are pooled instead, with flats of 40 to 100 m2.
"""

import statistics

import common as c
from rent import city24

SOURCE_ID = "city24-ee-rent"
PERIOD = "2026-11"
MIN_ADS = 15

# NUTS 3 -> (City24 parish (municipality) name, display name, GeoNames name)
TOWNS = {
    "EE001": ("Tallinn", "Tallinn", "Tallinn"),
    "EE008": ("Tartu linn", "Tartu", "Tartu"),
    "EE00A": ("Narva linn", "Narva", "Narva"),
    "EE004": ("Pärnu linn", "Pärnu", "Pärnu"),
}
KESK_COUNTIES = {"Lääne-Viru maakond", "Järva maakond", "Rapla maakond"}

SOURCES = [c.source(
    SOURCE_ID, "City24 (property portal, Estonia and Latvia)",
    "Flats for rent in Estonia: the listing API behind city24.ee search (api.city24.lv, country code 1)",
    "https://www.city24.ee/en/real-estate-search/apartments-for-rent", "Free to read, no licence stated (portal "
    "listings; derived medians only, no listings republished)", PERIOD,
    "Asking rents of current listings, EUR per month excluding utilities.")]


def rows():
    ads = city24.all_ads(SOURCE_ID, 1)
    out = []
    for nuts3, (parish, name, geonames) in TOWNS.items():
        rate, n = city24.rate([a for a in ads if a["parish"] == parish])
        if n < MIN_ADS:
            raise RuntimeError(f"{name}: only {n} ads; the thin-market rule needs a decision")
        out.append(c.row(
            c.place(nuts3), round(rate * c.TWO_BED_M2), "EUR", "per_month", PERIOD,
            c.city_code("EE", geonames) or c.place(nuts3), SOURCE_ID,
            f"City24 median asking rent in {name}, {rate:.2f} EUR/m2 over {n} flats of 55 to 100 m2, x 75 m2."))
    pool = [a for a in ads if a["county"] in KESK_COUNTIES and a["area"] and 40 <= a["area"] <= 100 and a["price"]
            and 100 <= a["price"] <= 5000]
    rate = statistics.median(a["price"] / a["area"] for a in pool)
    out.append(c.row(
        c.place("EE009"), round(rate * c.TWO_BED_M2), "EUR", "per_month", PERIOD, c.place("EE009"), SOURCE_ID,
        f"City24 median asking rent over the region's counties (Lääne-Viru, Järva, Rapla), {rate:.2f} EUR/m2 over "
        f"{len(pool)} flats of 40 to 100 m2, x 75 m2. Rakvere alone has too few ads."))
    return out
