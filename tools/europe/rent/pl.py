"""Poland: Otodom asking rents for the 9 big-city regions, modelled from GUS sale prices for the other 64.

Measured: average asking rent of a 60-89 m2 flat, June 2026, Otodom Analytics via Bankier.pl (10 cities, of which
Gdynia only informs the fit). Neither Statistics Poland nor the National Bank publishes rents; the NBP's 17-city
asking-rent series sits behind a firewall that refuses plain fetches (nbp.pl, tried with browser agents and Wayback).
Modelled: for every other region we take the main town's powiat (county) and Statistics Poland's median transaction
price per m2 of market flat sales in 2025 (BDL, official, 380 powiats), and apply the log-log line fitted to the 10 cities
with measured rents (rent = exp(a) x price^b). The fit has R2 0.70 and a residual spread of 11 percent in-sample;
small towns are an extrapolation. Rows from the model say so in their note and put the region itself in measured_for.
"""

import json
import urllib.request

import numpy as np

import common as c

RENT_ID = "pl-otodom-rents-2026-06"
PRICE_ID = "pl-gus-bdl-price-m2"
RENT_URL = "https://www.bankier.pl/wiadomosc/Ceny-ofertowe-wynajmu-mieszkan-lipiec-2026-Raport-Bankier-pl-9167757.html"
PRICE_URL = ("https://bdl.stat.gov.pl/api/v1/data/by-variable/633677?unit-level=5&year=2025&page-size=100"
             "&format=json&lang=pl")

SOURCES = [
    c.source(RENT_ID, "Otodom Analytics, published by Bankier.pl",
             "Average asking rents of flats in selected cities, June 2026 (Bankier.pl report of 15 July 2026)",
             RENT_URL, "free to read, no licence stated", "2026-06",
             "Average monthly asking rent of 60-89 m2 flats on Otodom in 10 cities (all-size table also published)."),
    c.source(PRICE_ID, "Statistics Poland (GUS), Local Data Bank",
             "Median price per m2 of residential premises sold in market transactions, by powiat, 2025 "
             "(variable 633677, subject P3787, from the Register of Real Estate Prices and Values)",
             "https://bdl.stat.gov.pl/", "Statistics Poland open data (free reuse with attribution)", "2025",
             "Used only to carry the measured rents to the other regions, through a fitted line."),
]

# average asking rent, PLN per month, 60-89 m2 flats, June 2026, and the powiat (TERYT, 4 digits) of the city
MEASURED = {
    "Warszawa": ("1465", 6056), "Gdynia": ("2262", 4364), "Kraków": ("1261", 4130), "Gdańsk": ("2261", 4436),
    "Szczecin": ("3262", 3848), "Wrocław": ("0264", 3990), "Katowice": ("2469", 3105), "Poznań": ("3064", 3470),
    "Lublin": ("0663", 2985), "Łódź": ("1061", 3160),
}
REGION_CITY = {"PL911": "Warszawa", "PL213": "Kraków", "PL633": "Gdańsk", "PL424": "Szczecin", "PL514": "Wrocław",
               "PL22A": "Katowice", "PL415": "Poznań", "PL814": "Lublin", "PL711": "Łódź"}
OVERRIDE_TOWN = {"PL21A": "Oświęcim"}  # the region's namesake; the largest unit is Olkusz


def powiat_prices() -> dict[str, tuple[str, float]]:
    path = c.CACHE / "pl-gus-bdl" / "median_price_m2_powiat.json"
    if not path.exists():
        rows, page = [], 0
        while True:
            req = urllib.request.Request(PRICE_URL + f"&page={page}", headers={"Accept": "application/json"})
            data = json.load(urllib.request.urlopen(req, timeout=60))
            rows += data["results"]
            if "next" not in data.get("links", {}):
                break
            page += 1
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"633677_2025": rows}, ensure_ascii=False))
    rows = json.loads(path.read_text())["633677_2025"]
    # BDL unit id: digits 2-3 voivodeship, 7-8 powiat (the TERYT powiat code)
    return {r["id"][2:4] + r["id"][7:9]: (r["name"], float(r["values"][0]["val"])) for r in rows if r["values"]}


def rows():
    c.fetch(RENT_ID, RENT_URL, "lipiec-2026.html")
    prices = powiat_prices()
    xs = np.log([prices[t][1] for t, _ in MEASURED.values()])
    ys = np.log([rent for _, rent in MEASURED.values()])
    b, a = np.polyfit(xs, ys, 1)
    r2 = 1 - np.var(ys - (a + b * xs)) / np.var(ys)

    lau = c.lau()
    out = []
    for nuts3 in c.regions_in("PL"):
        city = REGION_CITY.get(nuts3)
        if city:
            teryt, rent = MEASURED[city]
            out.append(c.row(
                c.place(nuts3), rent, "PLN", "per_month", "2026-06", c.city_code("PL", city), RENT_ID,
                f"Otodom Analytics via Bankier.pl: average asking rent of a 60-89 m2 flat in {city}, June 2026."))
            continue
        towns = c.main_towns(nuts3)
        if nuts3 in OVERRIDE_TOWN:
            towns = towns[towns["name"] == OVERRIDE_TOWN[nuts3]]
        town = towns.iloc[0]
        code = str(town["lau_code"])
        teryt = code[4:6] + code[9:11]
        name, price = prices[teryt]
        rent = float(np.exp(a + b * np.log(price)))
        out.append(c.row(
            c.place(nuts3), round(rent, -1), "PLN", "per_month", "2026-06", c.place(nuts3), RENT_ID,
            f"MODELLED, not measured (sources {RENT_ID} and {PRICE_ID}). {town['name']} ({name}): GUS median sale price {price:.0f} PLN/m2 (2025) "
            f"through rent = exp({a:.3f}) x price^{b:.2f} fitted to Otodom June 2026 asking rents (60-89 m2) of "
            f"10 big cities (R2 {r2:.2f}, spread about 11 percent)."))
    return out
