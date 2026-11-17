"""Monthly cost of owning and running one mid-size car, for every country outside the US and Europe.

The reference car and use match the Europe agent's (tools/europe/car.py), so neighbouring countries compare:
a new Toyota Corolla 1.8 Hybrid, bought for cash, kept 8 years and 96,000 km (12,000 km a year), 5.1 l/100 km.
Per month, in US dollars and then local currency:

    depreciation   price_new x 50% / 96
    insurance      3.1% of price_new a year / 12 (the German anchor's ratio: 1,030 EUR on 33,340 EUR)
    fuel           12,000 km x 5.1 l/100 km x local petrol price / 12
    maintenance    80 EUR a month in Germany, scaled by the everyday price level (mostly local labour)

price_new is the German list price (33,340 EUR, ADAC) scaled by ICP 2021's price level for "purchase of vehicles"
relative to Germany, carried to 2026 like the everyday price level. ICP prices cars at what buyers pay, so import
duties, quotas and registration charges that are part of the price (Singapore's COE, for example) are included.
Insurance is a share of the car's value, not of local wages, because outside rich countries motor insurers price
comprehensive cover on the vehicle's value. Annual road tax and registration fees are not included.
"""

import math
import re

from exchange_rates import rate_for_months, rates
from lib import CACHE, NUTS_COUNTRIES, PLAN_COUNTRY, countries, fmt, wb_icp, iso3_to_iso2
from price_level import ICP_ALIASES, NOT_CARRIED, REDENOMINATED, build as build_price_level

GERMAN_PRICE_EUR = 33_340
RESIDUAL_8Y = 0.50
MONTHS = 96
INSURANCE_SHARE = 1_030 / 33_340
LITRES_PER_MONTH = 12_000 * 5.1 / 100 / 12
GERMAN_MAINTENANCE_EUR_MONTH = 80

SOURCES = [
    {
        "source_id": "globalpetrolprices-gasoline",
        "publisher": "GlobalPetrolPrices.com (Globalen LLC)",
        "title": "Gasoline prices around the world, 09-Nov-2026 (US dollars per litre, octane 95)",
        "url": "https://www.globalpetrolprices.com/gasoline_prices/",
        "licence": "Dataset metadata on the page says CC BY 4.0; the site footer says CC BY-NC-ND 3.0. Used as one input, with attribution.",
        "retrieved": "2026-11-17",
        "period": "2026-11-09",
        "note": "Weekly retail petrol prices for 170 countries, collected from official sources and fuel companies. Countries missing here use their region's median, said so in each row.",
    },
    {
        "source_id": "adac-autokatalog-corolla",
        "publisher": "ADAC",
        "title": "Autokatalog: Toyota Corolla 1.8 Hybrid Comfort (140 PS), list price and running costs",
        "url": "https://www.adac.de/rund-ums-fahrzeug/autokatalog/",
        "licence": "Publisher copyright; numerical facts reused",
        "retrieved": "2026-11-17",
        "period": "2025-02",
        "note": "The Europe agent's anchor (33,340 EUR list price; insurance 1,030 EUR a year; maintenance 80 EUR a month); see .agent/research/europe/car.md.",
    },
]

GPP_NAMES = {"USA": "US", "UAE": "AE", "UK": "GB", "South-Korea": "KR", "Swaziland": "SZ", "Burma": "MM", "Myanmar": "MM",
             "Trinidad-and-Tobago": "TT", "Dominican-Republic": "DO", "Bosnia-and-Herzegovina": "BA", "Ivory-Coast": "CI",
             "Cape-Verde": "CV", "Czech-Republic": "CZ", "Hong-Kong": "HK", "Macao": "MO", "Laos": "LA", "Russia": "RU",
             "Congo-Democratic-Republic": "CD", "Congo": "CG", "North-Macedonia": "MK", "Macedonia": "MK", "Moldova": "MD",
             "Syria": "SY", "Iran": "IR", "Vietnam": "VN", "Taiwan": "TW", "Kyrgyzstan": "KG", "Bolivia": "BO", "Tanzania": "TZ",
             "Venezuela": "VE", "Brunei": "BN", "Palestine": "PS", "Israel": "IL", "Kosovo": "XK"}


def petrol_usd_per_litre() -> dict[str, float]:
    s = (CACHE / "globalpetrolprices" / "gasoline_prices.html").read_text(encoding="utf-8", errors="replace")
    names = [n for _, n in re.findall(r"id=\"hl(\d+)\" >\s*<a href='/([^/]+)/gasoline_prices/'", s)]
    values = [float(v) for v in re.findall(r">\s*(\d+\.\d{3})\s*<", s)]
    if len(names) != len(values) or values != sorted(values):
        raise ValueError("GlobalPetrolPrices page layout changed: names and prices no longer line up")
    by_name = {c["name"].replace(" ", "-"): iso2 for iso2, c in countries().items()}
    out = {}
    for name, value in zip(names, values):
        iso2 = GPP_NAMES.get(name) or by_name.get(name)
        if iso2:
            out[iso2] = value
    return out


def vehicle_price_levels(now: dict) -> dict[str, float]:
    """ISO2 -> ICP 2021 'purchase of vehicles' price level carried to now, US = 100, using the everyday CPI ratio."""
    d = wb_icp("1107100")
    us = d["USA"]["PX.WL"]
    to2 = iso3_to_iso2()
    out = {}
    for code, v in d.items():
        iso2 = ICP_ALIASES.get(code) or to2.get(code)
        if iso2 in now and "PX.WL" in v and iso2 not in NOT_CARRIED:
            # The everyday level's drift since 2021 (inflation against the dollar) is applied to cars too.
            drift = now[iso2]["pli"] / now[iso2]["pli2021"]
            out[iso2] = 100 * v["PX.WL"] / us * drift
    return out


def build() -> tuple[list[dict], dict]:
    _, info = build_price_level()
    now, imputed = info["now"], info["imputed"]
    everyday = {k: v["pli"] for k, v in {**imputed, **now}.items()}
    vehicles = vehicle_price_levels(now)
    petrol = petrol_usd_per_litre()
    fx = rates()
    usd_per_eur = 1 / fx["EUR"]["monthly"][max(fx["EUR"]["monthly"])]

    de_vehicle, de_everyday = vehicles["DE"], everyday["DE"]
    # Where ICP has no vehicle price level, use the median ratio of vehicle to everyday price levels in the same continent.
    ratio_by_continent: dict[str, list[float]] = {}
    for iso2, v in vehicles.items():
        ratio_by_continent.setdefault(countries()[iso2]["continent"], []).append(math.log(v / everyday[iso2]))
    petrol_by_continent: dict[str, list[float]] = {}
    for iso2, p in petrol.items():
        if iso2 in countries():
            petrol_by_continent.setdefault(countries()[iso2]["continent"], []).append(p)

    def median(xs):
        xs = sorted(xs)
        return xs[len(xs) // 2] if len(xs) % 2 else (xs[len(xs) // 2 - 1] + xs[len(xs) // 2]) / 2

    rows = []
    for iso2, level in sorted(everyday.items()):
        if iso2 in NUTS_COUNTRIES or iso2 == "US":
            continue  # the Europe and US agents own these; a row here would stand in for theirs on the site
        c = countries()[iso2]
        thin = []
        if iso2 in vehicles:
            vehicle = vehicles[iso2]
        else:
            vehicle = level * math.exp(median(ratio_by_continent.get(c["continent"]) or [x for xs in ratio_by_continent.values() for x in xs]))
            thin.append("car price level estimated from the everyday price level and the continent's typical car-to-everyday ratio")
        if iso2 in petrol:
            litre = petrol[iso2]
        else:
            litre = median(petrol_by_continent.get(c["continent"]) or list(petrol.values()))
            thin.append(f"petrol price is the {c['continent']} median, {litre:.2f} US dollars a litre")
        price = GERMAN_PRICE_EUR * usd_per_eur * vehicle / de_vehicle
        parts = {
            "depreciation": price * (1 - RESIDUAL_8Y) / MONTHS,
            "insurance": price * INSURANCE_SHARE / 12,
            "fuel": LITRES_PER_MONTH * litre,
            "maintenance": GERMAN_MAINTENANCE_EUR_MONTH * usd_per_eur * level / de_everyday,
        }
        total_usd = sum(parts.values())
        cur = c["currency"]
        xr, xr_period, _ = rate_for_months(fx.get(cur, {"monthly": {}}), ["2026-07", "2026-08", "2026-09"])
        if xr is None:
            continue
        code = PLAN_COUNTRY.get(iso2, iso2)
        if iso2 == "PS":
            continue
        note = (f"Corolla 1.8 Hybrid, 8 years, 12,000 km a year: price new about {fmt(price, 3)} US dollars; per month in US dollars "
                + ", ".join(f"{k} {v:,.0f}" for k, v in parts.items())
                + f"; converted at {fmt(xr)} {cur} per US dollar ({xr_period}). Road tax and registration not included")
        if thin:
            note += ". Thin: " + "; ".join(thin)
        rows.append({"place_code": code, "amount": fmt(total_usd * xr, 4), "currency": cur, "unit": "per_month", "period": "2026",
                     "measured_for": f"{c['name'] if code != 'PS' else 'Israel and Palestine (figure for Israel)'}, whole country",
                     "source_id": "wb-icp-2021", "note": note})
    return rows, {"vehicles": vehicles, "petrol": petrol}


if __name__ == "__main__":
    from lib import upsert_sources, write_table

    rows, _ = build()
    write_table("car", rows)
    upsert_sources(SOURCES)
