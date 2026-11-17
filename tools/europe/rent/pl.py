"""Poland: Otodom asking rents for the 9 big-city regions, modelled from GUS sale prices for the other 64.

Measured: average asking rent of a 60-89 m2 flat, June 2026, Otodom Analytics via Bankier.pl (10 cities, of which
Gdynia only informs the fit). Neither Statistics Poland nor the National Bank publishes rents; the NBP's 17-city
asking-rent series sits behind a firewall that refuses plain fetches (nbp.pl, tried with browser agents and Wayback).
Added 2026-11-18: Otodom's January 2026 report (all flat sizes, 16 cities) adds Opole, Rzeszow, Kielce, Olsztyn,
Bydgoszcz, Bialystok and Zielona Gora, and Rankomat.pl and Rentier.io's March 2026 report prints per-m2 asking rents for 5 more cities (Radom,
Sosnowiec, Czestochowa, Torun) in running text. Each is scaled to the Otodom June 60-89 m2 level by the median ratio
between the two sources over the cities both publish, then used as a measured row and as an extra fit point. Modelled: for every other region we take the main town's powiat (county) and Statistics Poland's median transaction
price per m2 of market flat sales in 2025 (BDL, official, 380 powiats), and apply the log-log line fitted to the 10 cities
with measured rents (rent = exp(a) x price^b). The fit has R2 0.70 and a residual spread of 11 percent in-sample;
small towns are an extrapolation. Rows from the model say so in their note and put the region itself in measured_for.
"""

import json
import urllib.request

import numpy as np

import common as c

RENT_ID = "pl-otodom-rents-2026-06"
OJ_ID = "pl-otodom-rents-2026-01"
OJ_URL = "https://www.otodom.pl/wiadomosci/wp-content/uploads/2026/02/Otodom_raport-z-rynku-najmu_styczen-2026.pdf"
RK_ID = "pl-rankomat-rents-2026-03"
RK_URL = "https://rankomat.pl/o-nas/biuro-prasowe/raport-rankomat-pl-i-rentier-io-ceny-najmu-marzec-2026-r"
PRICE_ID = "pl-gus-bdl-price-m2"
RENT_URL = "https://www.bankier.pl/wiadomosc/Ceny-ofertowe-wynajmu-mieszkan-lipiec-2026-Raport-Bankier-pl-9167757.html"
PRICE_URL = ("https://bdl.stat.gov.pl/api/v1/data/by-variable/633677?unit-level=5&year=2025&page-size=100"
             "&format=json&lang=pl")

SOURCES = [
    c.source(RENT_ID, "Otodom Analytics, published by Bankier.pl",
             "Average asking rents of flats in selected cities, June 2026 (Bankier.pl report of 15 July 2026)",
             RENT_URL, "free to read, no licence stated", "2026-06",
             "Average monthly asking rent of 60-89 m2 flats on Otodom in 10 cities (all-size table also published)."),
    c.source(OJ_ID, "Otodom Analytics (Otodom raport z rynku najmu, styczen 2026)",
             "Average asking rent of flats in 18 big cities, January 2026 (PDF report)", OJ_URL,
             "free to read, no licence stated", "2026-01",
             "Average monthly asking rent, all flat sizes (national mean 51 m2), without bills, of Otodom listings."),
    c.source(RK_ID, "Rankomat.pl and Rentier.io",
             "Rental prices, 17 largest cities, February 2026 (report of March 2026)", RK_URL,
             "free to read, no licence stated", "2026-02",
             "Average asking rent per m2 of flats, without bills, in 17 cities, as printed in the press release text "
             "(chart not machine-readable). Mixed flat sizes, small flats weigh more, so per-m2 figures run above Otodom's 60-89 m2."),
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
# Otodom January 2026, all sizes, PLN per month: the cities it shares with MEASURED (Gdansk is "Trojmiasto"), then new ones
OJ_SHARED = {"Warszawa": 4941, "Kraków": 3188, "Gdańsk": 3201, "Szczecin": 2895, "Wrocław": 3128, "Katowice": 2399,
             "Poznań": 2649, "Lublin": 2565, "Łódź": 2312}
OJ_EXTRA = {"Opole": ("1661", 2512), "Rzeszów": ("1863", 2530), "Kielce": ("2661", 2040), "Olsztyn": ("2862", 2413),
            "Bydgoszcz": ("0461", 2230), "Białystok": ("2061", 2030), "Zielona Góra": ("0862", 2337)}
# Rankomat PLN/m2, February 2026 (report text): the six cities shared with Otodom, then the extra ones
RK_SHARED = {"Warszawa": 78, "Gdańsk": 66, "Kraków": 66, "Wrocław": 65, "Łódź": 50, "Katowice": 50}
RK_EXTRA = {"Radom": ("1463", 43), "Sosnowiec": ("2475", 43), "Częstochowa": ("2464", 38), "Toruń": ("0463", 46)}
# region -> (city, source key); the region's main town is that city
SCALED_REGION = {"PL524": "Opole", "PL823": "Rzeszów", "PL721": "Kielce", "PL622": "Olsztyn", "PL613": "Bydgoszcz",
                 "PL841": "Białystok", "PL432": "Zielona Góra", "PL921": "Radom", "PL22B": "Sosnowiec",
                 "PL224": "Częstochowa"}
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
    c.fetch(OJ_ID, OJ_URL, "styczen-2026.pdf")
    c.fetch(RK_ID, RK_URL, "najem-luty-2026.html")
    prices = powiat_prices()
    oj_ratio = float(np.median([MEASURED[k][1] / v for k, v in OJ_SHARED.items()]))
    rk_ratio = float(np.median([MEASURED[k][1] / v for k, v in RK_SHARED.items()]))
    scaled = {k: (t, round(v * oj_ratio, -1), OJ_ID, "2026-01", v, f"Otodom January 2026 average asking rent of all flats, {v} PLN, "
              f"x {oj_ratio:.3f} (median ratio of Otodom June 60-89 m2 rent to its January all-size rent over {len(OJ_SHARED)} shared cities)")
              for k, (t, v) in OJ_EXTRA.items()}
    scaled |= {k: (t, round(v * rk_ratio, -1), RK_ID, "2026-02", v, f"Rankomat.pl/Rentier.io asking rent {v} PLN/m2 (Feb 2026, mixed flat "
               f"sizes) x {rk_ratio:.1f} (median ratio of Otodom June 60-89 m2 monthly rent to Rankomat PLN/m2 over {len(RK_SHARED)} shared cities)")
               for k, (t, v) in RK_EXTRA.items()}
    points = {**MEASURED, **{k: (v[0], v[1]) for k, v in scaled.items()}}
    xs = np.log([prices[t][1] for t, _ in points.values()])
    ys = np.log([rent for _, rent in points.values()])
    b, a = np.polyfit(xs, ys, 1)
    r2 = 1 - np.var(ys - (a + b * xs)) / np.var(ys)

    lau = c.lau()
    out = []
    for nuts3 in c.regions_in("PL"):
        if nuts3 in SCALED_REGION:
            city = SCALED_REGION[nuts3]
            _, rent, sid, period, _, how = scaled[city]
            out.append(c.row(c.place(nuts3), rent, "PLN", "per_month", period, c.city_code("PL", city), sid,
                             f"{city}: {how}. Scaled to a 60-89 m2 flat; asking rent, not agreed."))
            continue
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
            f"through rent = exp({a:.3f}) x price^{b:.2f} fitted to asking rents (Otodom June 2026 60-89 m2, plus "
            f"{len(scaled)} cities scaled to it) of {len(points)} cities (R2 {r2:.2f})."))
    return out
