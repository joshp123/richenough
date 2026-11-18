"""Hourly pay of a part-time, live-out housekeeper, for every country outside the US and Europe and Palombo's cities.

1. Cities (Palombo's 25 outside the US and Europe): the median of every published going rate the housekeeper helper
   found (agency and platform prices, direct-hire rates and surveys; tools/world/housekeeper/housekeeper.curated.csv,
   each with a saved page). Per-visit and per-day prices count only where the hours are stated.
2. A country containing one of those cities takes that city's figure.
3. Every other country: the geometric mean of two estimates, where both exist, else the one that does:
   a. GDP per head: log(rate) on log(GDP per head) across the cities above and the US and Europe agents' national
      medians (in US dollars);
   b. ILOSTAT's mean hourly earnings of employees in households as employers (ISIC section T), carried to 2026 with
      the CPI and multiplied by the median ratio of city going rates to that national figure (city households pay
      more than the national average of domestic workers, which includes live-in and rural work).
   Floor: the general minimum wage (ILOSTAT, monthly, over 173.3 hours) and any domestic-worker minimum the helper
   verified, carried to 2026 with the CPI.
"""

import csv
import math
import re
import statistics

from exchange_rates import current_rates
from lib import EUROPE_AGENT, PLAN_COUNTRY, REPO, countries, fmt, ilostat, iso3_to_iso2, read_csv
from price_level import weo

HOUSEKEEPER = REPO / "tools" / "world" / "housekeeper"
HOURS_PER_MONTH = 40 * 52 / 12
CITY_NAMES = {
    "CITY-112931": "Tehran", "CITY-1850147": "Tokyo", "CITY-1668341": "Taipei", "CITY-1880252": "Singapore", "CITY-1609350": "Bangkok",
    "CITY-1151254": "Phuket", "CITY-1153671": "Chiang Mai", "CITY-1735161": "Kuala Lumpur", "CITY-1735106": "George Town (Penang)",
    "CITY-1566083": "Ho Chi Minh City", "CITY-1583992": "Da Nang", "CITY-1645528": "Denpasar (south Bali)", "CITY-1622846": "Ubud (Bali)",
    "CITY-292223": "Dubai", "CITY-287286": "Muscat", "CITY-611717": "Tbilisi", "CITY-2542997": "Marrakesh", "CITY-3369157": "Cape Town",
    "CITY-3530597": "Mexico City", "CITY-3621849": "San José (Costa Rica)", "CITY-3703443": "Panama City", "CITY-3674962": "Medellín",
    "CITY-3936456": "Lima", "CITY-3463237": "Florianópolis", "CITY-3871336": "Santiago", "CITY-3435910": "Buenos Aires",
    "CITY-3441575": "Montevideo",
}

SOURCES = [
    {
        "source_id": "ilostat-earnings-isic-t",
        "publisher": "International Labour Organization, ILOSTAT",
        "title": "Average hourly earnings of employees by sex and economic activity (EAR_EHRA_SEX_ECO_NB_A), ISIC Rev.4 section T, activities of households as employers",
        "url": "https://ilostat.ilo.org/data/",
        "licence": "CC BY 4.0",
        "retrieved": "2026-11-17",
        "period": "2017 to 2025, latest year per country",
        "note": "Bulk download from rplumber.ilo.org, no key. Mean pay of all employees of households (live-in and live-out, rural and urban).",
    },
    {
        "source_id": "ilostat-minimum-wage",
        "publisher": "International Labour Organization, ILOSTAT",
        "title": "Monthly minimum wage, local currency (EAR_INEE_NOC_NB_A)",
        "url": "https://ilostat.ilo.org/data/",
        "licence": "CC BY 4.0",
        "retrieved": "2026-11-17",
        "period": "latest year per country, to 2026",
        "note": "Statutory general minimum wage; used only as a floor, at 173.3 hours a month.",
    },
]


def hours_in(note: str) -> float | None:
    n = note.lower()
    for pattern in (r"hours?\s*=\s*([\d.]+)", r"\(([\d.]+)\s*h\)", r"(\d+(?:\.\d+)?)[- ]hours?\b", r"\b(\d+(?:\.\d+)?)\s*h\b"):
        m = re.search(pattern, n)
        if m:
            return float(m.group(1))
    return None


def usd_per(fx: dict, currency: str) -> float:
    return 1 / fx[currency]


def city_country() -> dict[str, str]:
    out = {}
    with open(REPO / "cache" / "geonames" / "cities15000.txt", encoding="utf-8") as f:
        for line in f:
            r = line.split("\t")
            out[r[0]] = r[8]
    return out


def going_rates(fx: dict) -> dict[str, dict]:
    """CITY code -> {'usd': median USD per hour, 'n', 'types': {type: [usd...]}, 'currency': most common currency}."""
    cities: dict[str, dict] = {}
    for r in read_csv(HOUSEKEEPER / "housekeeper.curated.csv"):
        kind = r["note"].split(";")[0].replace("type=", "").strip()
        if not r["place_code"].startswith("CITY-") or kind == "statutory-domestic-min":
            continue
        if "CROSS-CHECK ONLY" in r["note"] or "OUTLIER" in r["note"]:
            continue
        amount = float(r["amount"])
        if r["unit"] == "per_hour":
            hourly = amount
        elif r["unit"] in ("per_visit", "per_day") and hours_in(r["note"]):
            hourly = amount / hours_in(r["note"])
        else:
            continue
        c = cities.setdefault(r["place_code"], {"types": {}, "figures": []})
        usd = hourly * usd_per(fx, r["currency"])
        c["types"].setdefault(kind, []).append(usd)
        c["figures"].append((usd, r["source_id"]))
    for c in cities.values():
        c["usd"] = statistics.median(v for v, _ in c["figures"])
        c["n"] = len(c["figures"])
        c["source_id"] = min(c["figures"], key=lambda f: abs(f[0] - c["usd"]))[1]
    return cities


def statutory_floors(fx: dict) -> dict[str, float]:
    """ISO2 (or ISO 3166-2 region) -> highest verified domestic-worker minimum, USD per hour."""
    out: dict[str, float] = {}
    for r in read_csv(HOUSEKEEPER / "housekeeper.curated.csv"):
        if not r["note"].startswith("type=statutory-domestic-min") or "UNVERIFIED" in r["note"].upper():
            continue
        amount = float(r["amount"])
        if r["unit"] == "per_hour":
            hourly = amount
        elif r["unit"] == "per_month":
            hourly = amount / HOURS_PER_MONTH
        elif r["unit"] == "per_day" and hours_in(r["note"]):
            hourly = amount / hours_in(r["note"])
        elif r["unit"] == "per_day":
            hourly = amount / 8
        else:
            continue
        code = r["place_code"]
        iso2 = code.split("-")[0] if not code.startswith("CITY-") else None
        if iso2:
            out[iso2] = max(out.get(iso2, 0), hourly * usd_per(fx, r["currency"]))
    return out


ILO_USD_CODES = {"T30:384", "T30:405"}


def ilo_latest(indicator: str, keep) -> dict[str, tuple[float, str, bool]]:
    to2 = iso3_to_iso2()
    out: dict[str, tuple[float, str, bool]] = {}
    for x in ilostat(indicator):
        if keep(x) and x["obs_value"] and x["time"] >= "2017":
            k = to2.get(x["ref_area"])
            if k and (k not in out or x["time"] > out[k][1]):
                # ILO currency dictionary: https://rplumber.ilo.org/metadata/dic/?var=note_indicator&lang=en&format=.csv
                notes = x["note_indicator"].split("_")
                if "T30:58" in notes or (k == "SY" and x["time"] < "2026"):
                    continue  # discontinued ZWL or old Syrian pounds; no continuous CPI bridge
                value = float(x["obs_value"]) / (1000 if "T30:44" in notes else 1)
                out[k] = (value, x["time"], any(n in notes for n in ILO_USD_CODES))
    return out


def build() -> list[dict]:
    fx = current_rates()
    cpi = weo("PCPI")
    gdp = weo("NGDPDPC")
    to_country = city_country()

    def to_2026(iso2: str, value: float, year: str) -> float:
        c = cpi.get(iso2, {})
        return value * c["2026"] / c[year] if c.get("2026") and c.get(year) else value

    cities = going_rates(fx)
    floors = statutory_floors(fx)
    isic_t = ilo_latest("EAR_EHRA_SEX_ECO_NB_A", lambda x: x["classif1"] == "ECO_ISIC4_T" and x["sex"] == "SEX_T")
    minimum = ilo_latest("EAR_INEE_NOC_NB_A", lambda x: True)

    def wage_usd(iso2, observation):
        value, year, in_dollars = observation
        if in_dollars:
            return to_2026("US", value, year)
        return to_2026(iso2, value, year) / fx[countries()[iso2]["currency"]]

    def gdp_2026(iso2):
        g = gdp.get(iso2, {})
        return g.get("2026") or g.get("2025")

    # Fit both estimators on the cities.
    points = []
    for code, c in cities.items():
        iso2 = to_country[code[5:]]
        points.append((iso2, c["usd"]))
    by_country: dict[str, list[float]] = {}
    for iso2, v in points:
        by_country.setdefault(iso2, []).append(v)
    country_rate = {k: statistics.median(v) for k, v in by_country.items()}
    # The US and Europe agents' tables, as national medians, widen the fit to rich countries (not written as rows here).
    neighbours: dict[str, list[float]] = {}
    national: dict[str, float] = {}
    for area in ("us", "europe"):
        path = REPO / "data" / "tables" / f"housekeeper-wage.{area}.csv"
        if not path.exists():
            continue
        for r in read_csv(path):
            code = r["place_code"]
            if len(code) == 2 and r["currency"] in fx:
                national[code] = float(r["amount"]) / fx[r["currency"]]
                continue
            iso2 = "US" if code.startswith("US") else {"EL": "GR", "UK": "GB", "TL": "GB"}.get(code[5:7], code[5:7]) if code.startswith("NUTS-") else None
            if iso2 and r["currency"] in fx and r["amount"]:
                neighbours.setdefault(iso2, []).append(float(r["amount"]) * usd_per(fx, r["currency"]))
    training = {**{k: statistics.median(v) for k, v in neighbours.items()}, **national, **country_rate}
    xs = [(math.log(gdp_2026(k)), math.log(v)) for k, v in training.items() if gdp_2026(k)]
    mx = statistics.fmean(x for x, _ in xs)
    my = statistics.fmean(y for _, y in xs)
    slope = sum((x - mx) * (y - my) for x, y in xs) / sum((x - mx) ** 2 for x, _ in xs)
    intercept = my - slope * mx
    sd_gdp = statistics.pstdev([y - intercept - slope * x for x, y in xs])
    premium = statistics.median(v / wage_usd(k, isic_t[k]) for k, v in country_rate.items() if k in isic_t)

    rows = []
    # Cities.
    for code, c in sorted(cities.items()):
        iso2 = to_country[code[5:]]
        cur = countries()[iso2]["currency"]
        local = c["usd"] / usd_per(fx, cur)
        detail = ", ".join(f"{k} median USD {statistics.median(v):.2f} ({len(v)})" for k, v in sorted(c["types"].items()))
        rows.append({"place_code": code, "amount": fmt(local, 3), "currency": cur, "unit": "per_hour", "period": "2026",
                     "measured_for": f"{CITY_NAMES.get(code, code)}, published going rates for households", "source_id": c["source_id"],
                     "note": f"Median of {c['n']} published going rates (agency, platform, direct hire and surveys), each with a saved source in tools/world/housekeeper/housekeeper.curated.csv: {detail}"
                             + (". Thin: fewer than four figures" if c["n"] < 4 else "")})
    # Countries.
    for iso2, c in sorted(countries().items()):
        if iso2 in ("US", "PS", "AQ") or not c["population"] or iso2 in EUROPE_AGENT:
            continue
        cur = c["currency"]
        if cur not in fx:
            continue
        estimates, words = [], []
        if iso2 in country_rate:
            usd = country_rate[iso2]
            city_codes = [k for k in cities if to_country[k[5:]] == iso2]
            city_words = " and ".join(CITY_NAMES.get(k, k) for k in city_codes)
            basis = f"the going rate in {city_words} (see the city rows)"
            source_id = cities[city_codes[0]]["source_id"]
            thin = False
        else:
            g = gdp_2026(iso2)
            if g:
                estimates.append(intercept + slope * math.log(g))
                words.append(f"GDP per head (USD {g:,.0f})")
            if iso2 in isic_t:
                estimates.append(math.log(wage_usd(iso2, isic_t[iso2]) * premium))
                wage_basis = f"ILOSTAT's pay of household employees in {isic_t[iso2][1]} x {premium:.2f}"
                if iso2 == "SL" and isic_t[iso2][1] < "2022":
                    wage_basis += " (1,000 old leones per SLE)"
                if isic_t[iso2][2]:
                    wage_basis += " (reported in US dollars)"
                words.append(wage_basis)
            if not estimates:
                continue
            usd = math.exp(statistics.fmean(estimates))
            basis = "estimated from " + " and ".join(words)
            thin = True
        floor_usd, floor_word = 0.0, ""
        if iso2 in minimum:
            mw = wage_usd(iso2, minimum[iso2]) / HOURS_PER_MONTH
            if mw > floor_usd:
                floor_usd, floor_word = mw, f"general minimum wage ({minimum[iso2][1]})"
        if floors.get(iso2, 0) > floor_usd:
            floor_usd, floor_word = floors[iso2], "domestic-worker minimum wage"
        note = f"Basis: {basis}"
        if floor_usd > usd:
            note += f"; raised to the {floor_word}, USD {floor_usd:.2f} an hour"
            usd = floor_usd
        if thin:
            note += f". Inferred, not measured: typical error about {math.expm1(sd_gdp):.0%}"
        code = PLAN_COUNTRY.get(iso2, iso2)
        rows.append({"place_code": code, "amount": fmt(usd / usd_per(fx, cur), 3), "currency": cur, "unit": "per_hour", "period": "2026",
                     "measured_for": (f"{c['name']}: going rate in {city_words}" if not thin else
                                      f"{c['name'] if code != 'PS' else 'Israel and Palestine (figure for Israel)'}, whole country, estimated"),
                     "source_id": source_id if not thin else ("ilostat-earnings-isic-t" if iso2 in isic_t else "imf-weo"),
                     "note": note})
    return rows


def sources() -> list[dict]:
    return SOURCES + read_csv(HOUSEKEEPER / "housekeeper.sources.csv")


if __name__ == "__main__":
    from lib import upsert_sources, write_table

    write_table("housekeeper-wage", build())
    upsert_sources(sources())
