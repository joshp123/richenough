"""Romania: asking rents of flats in each county seat, from Storia.ro's public search pages, 17 Nov 2026.

No official source has rents below national level (INS publishes a rent price index only; BNR's reports quote the
portals). Storia (OLX group, also carries cross-listed ads) is Romania's largest flat portal. Each county seat's
"flats for rent" search page embeds its listings as JSON; we read up to 10 pages (360 listings) per city, keep
flats of 55 to 100 m2 (lei ads converted at the ECB rate) and price a 75 m2 two-bed at 75 x the median rent per
m2. Cities with fewer than 15 such ads are too thin; they get the median of the ordinary county seats (labelled
national, RO).
"""

import json
import re
import statistics
import time
import unicodedata

import requests

import common as c

SOURCE_ID = "storia-ro-chirii"
PERIOD = "2026-11"
MAX_PAGES = 10
MIN_ADS = 15
AREA_RANGE = (55, 100)
PRICE_RANGE = (100, 5000)  # EUR per month; drops placeholder prices and sale prices typed into rent ads
BIG = {"RO321", "RO113", "RO122", "RO213", "RO424", "RO223", "RO126", "RO411", "RO111", "RO421"}

# main-town overrides: (storia county slug override, storia city slug, display name)
OVERRIDE = {
    "RO423": ("hunedoara", "deva", "Deva"),                 # county seat; Hunedoara is slightly bigger
    "RO322": ("ilfov", "voluntari", "Voluntari"),           # Ilfov has no seat inside it; Voluntari is its administrative centre
    "RO123": ("covasna", "sfantu-gheorghe", "Sfântu Gheorghe"),
    "RO214": ("neamt", "piatra--neamt", "Piatra Neamț"),
}

SOURCES = [c.source(
    SOURCE_ID, "Storia.ro (OLX Group)",
    "Flats for rent in each Romanian county seat: public search result pages (embedded listing JSON)",
    "https://www.storia.ro/ro/rezultate/inchiriere/apartament", "Free to read, no licence stated (portal listings; "
    "derived medians only, no listings republished)", PERIOD,
    "Asking rents of current listings; up to 360 per city; EUR; flats 55 to 100 m2.")]


def _slug(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    text = re.sub(r"[^a-z0-9 -]", "", text.strip())
    return text.replace("-", "--").replace(" ", "-")


def _ads(path: str) -> list[dict]:
    """Compact ads (price, area, rooms) for a Storia location path, cached as JSON in cache/storia-ro-chirii/."""
    folder = c.CACHE / SOURCE_ID
    folder.mkdir(parents=True, exist_ok=True)
    cache = folder / (path.replace("/", "__") + ".json")
    if cache.exists():
        return json.loads(cache.read_text())
    session = requests.Session()
    session.headers["User-Agent"] = c.USER_AGENT
    ads: list[dict] = []
    for page in range(1, MAX_PAGES + 1):
        url = f"https://www.storia.ro/ro/rezultate/inchiriere/apartament/{path}" + (f"?page={page}" if page > 1 else "")
        response = session.get(url, timeout=60)
        time.sleep(0.7)
        if response.status_code != 200:
            break
        match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', response.text, re.S)
        props = json.loads(match.group(1))["props"]["pageProps"]
        found = props["data"]["searchAds"]
        for item in found["items"]:
            price = item.get("totalPrice") or {}
            if item.get("transaction") != "RENT" or item.get("estate") != "FLAT" or not price.get("value"):
                continue
            ads.append({"id": item["id"], "price": price["value"], "currency": price["currency"],
                        "area": item.get("areaInSquareMeters"), "rooms": item.get("roomsNumber")})
        if page >= found["pagination"]["totalPages"]:
            break
    cache.write_text(json.dumps(ads))
    return ads


def _lei_per_euro() -> float:
    """ECB reference rate, lei per euro, latest observation (cached)."""
    url = "https://data-api.ecb.europa.eu/service/data/EXR/D.RON.EUR.SP00.A?lastNObservations=1&format=csvdata"
    rows = c.fetch(SOURCE_ID, url, "ecb-ron-eur-2026-11-17.csv").read_text().strip().splitlines()
    header = rows[0].split(",")
    return float(rows[1].split(",")[header.index("OBS_VALUE")])


def _rate(ads: list[dict]) -> tuple[float, int]:
    """Median rent per m2 (EUR) and the number of ads used, one per ad id. Lei ads are converted at the ECB rate."""
    lei = _lei_per_euro()
    seen, rates = set(), []
    for ad in ads:
        if ad["id"] in seen or not ad["area"] or ad["currency"] not in ("EUR", "RON"):
            continue
        seen.add(ad["id"])
        price = ad["price"] / lei if ad["currency"] == "RON" else ad["price"]
        if AREA_RANGE[0] <= ad["area"] <= AREA_RANGE[1] and PRICE_RANGE[0] <= price <= PRICE_RANGE[1]:
            rates.append(price / ad["area"])
    return (statistics.median(rates) if rates else 0.0), len(rates)


def rows():
    counties = c.nuts3().set_index("nuts")["name"]
    plan = []
    for nuts3 in c.regions_in("RO"):
        town = c.main_towns(nuts3).iloc[0]
        if nuts3 in OVERRIDE:
            county, city, name = OVERRIDE[nuts3]
        else:
            name = re.sub(r"^(Municipiul|Oraş|Orașul)\s+", "", town["name"])
            county, city = _slug(counties[nuts3]), _slug(name)
        path = "bucuresti" if nuts3 == "RO321" else f"{county}/{city}"
        code = c.city_code("RO", name, town["name_latin"]) if nuts3 != "RO321" else c.city_code("RO", "Bucharest", "București")
        plan.append((nuts3, name, path, code))

    measured = {}
    for nuts3, name, path, code in plan:
        measured[nuts3] = _rate(_ads(path))
    ordinary = [rate for nuts3, (rate, n) in measured.items() if nuts3 not in BIG and nuts3 != "RO322" and n >= 30]
    fallback = statistics.median(ordinary)

    out = []
    for nuts3, name, path, code in plan:
        rate, n = measured[nuts3]
        if n >= MIN_ADS:
            out.append(c.row(
                c.place(nuts3), round(rate * c.TWO_BED_M2), "EUR", "per_month", PERIOD, code or c.place(nuts3), SOURCE_ID,
                f"Storia.ro median asking rent in {name}, {rate:.2f} EUR/m2 over {n} flats of "
                f"{AREA_RANGE[0]} to {AREA_RANGE[1]} m2 (newest of up to 360 ads), x 75 m2."))
        else:
            seen = f"Storia.ro had only {n} usable ads in {name}. "
            out.append(c.row(
                c.place(nuts3), round(fallback * c.TWO_BED_M2), "EUR", "per_month", PERIOD, "RO", SOURCE_ID,
                f"{seen}National stand-in, not local: median {fallback:.2f} EUR/m2 over {len(ordinary)} ordinary county "
                f"seats with 30+ ads, x 75 m2."))
    return out
