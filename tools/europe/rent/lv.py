"""Latvia: asking rents of flats in each region's main town, from ss.lv's public "flats to let" listings, 17 Nov 2026.

No official source: the State Land Service and the CSP publish sale prices and a dwelling price index, not rents.
ss.lv is Latvia's largest classifieds site. For Riga, Daugavpils, Jelgava and Liepaja we read every listing page of
"Izire" (landlords letting flats; monthly lets only, daily lets dropped), keep flats of 45 to 100 m2 and price a
75 m2 two-bed at 75 x the median rent per m2. Valmiera (Vidzeme) has too few such ads; Vidzeme gets the median of the
three regional cities, labelled national (LV). City24's API cross-checks Riga.
"""

import json
import re
import statistics
import time

import requests

import common as c

SOURCE_ID = "ss-lv-ire"
PERIOD = "2026-11"
AREA_RANGE = (45, 100)  # wider than elsewhere: Latvian regional cities have few flats over 55 m2
PRICE_RANGE = (100, 5000)
MIN_ADS = 10
BASE = "https://www.ss.lv/lv/real-estate/flats/"

# NUTS 3 -> (ss.lv path, name, GeoNames name); Vidzeme's main town is Valmiera, not the biggest LAU (Ogre).
CITIES = {
    "LV00A": ("riga/all", "Rīga", "Riga"),
    "LV005": ("daugavpils-and-reg/daugavpils", "Daugavpils", "Daugavpils"),
    "LV009": ("jelgava-and-reg/jelgava", "Jelgava", "Jelgava"),
    "LV00B": ("liepaja-and-reg/liepaja", "Liepāja", "Liepaja"),
    "LV00C": ("valmiera-and-reg/valmiera", "Valmiera", "Valmiera"),
}

SOURCES = [c.source(
    SOURCE_ID, "SS.LV (Latvian classifieds portal)",
    "Flats to let (Izīrē) in Rīga, Daugavpils, Jelgava, Liepāja and Valmiera: public listing pages",
    BASE, "Free to read, no licence stated (portal listings; derived medians only, no listings republished)", PERIOD,
    "Asking rents of current monthly lets; robots.txt allows /lv/ listing pages.")]


def _parse(html: str) -> list[dict]:
    ads = []
    for match in re.finditer(r'<tr id="tr_(\d+)"(.*?)</tr>', html, flags=re.S):
        cells = [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", x)).strip()
                 for x in re.findall(r"<td[^>]*>(.*?)</td>", match.group(2), flags=re.S)]
        if len(cells) < 9 or "€/mēn" not in cells[-1]:
            continue
        try:
            area = float(cells[5].replace(",", "."))
            price = float(cells[-1].split("€")[0].replace(" ", "").replace(",", ""))  # "1,000 €/mēn."
        except ValueError:
            continue
        ads.append({"id": match.group(1), "area": area, "price": price})
    return ads


def _ads(path: str) -> list[dict]:
    folder = c.CACHE / SOURCE_ID
    folder.mkdir(parents=True, exist_ok=True)
    cache = folder / (path.replace("/", "__") + ".json")
    if cache.exists():
        return json.loads(cache.read_text())
    session = requests.Session()
    session.headers["User-Agent"] = c.USER_AGENT
    ads: dict[str, dict] = {}
    seen: set[str] = set()
    for page in range(1, 80):
        url = f"{BASE}{path}/hand_over/" + (f"page{page}.html" if page > 1 else "")
        response = session.get(url, timeout=60)
        time.sleep(0.7)
        ids = set(re.findall(r'<tr id="tr_(\d+)"', response.text)) if response.status_code == 200 else set()
        if not ids - seen:
            break
        seen |= ids
        ads.update({a["id"]: a for a in _parse(response.text)})
    out = list(ads.values())
    cache.write_text(json.dumps(out))
    return out


def _rate(ads: list[dict]) -> tuple[float, int]:
    rates = [a["price"] / a["area"] for a in ads
             if AREA_RANGE[0] <= a["area"] <= AREA_RANGE[1] and PRICE_RANGE[0] <= a["price"] <= PRICE_RANGE[1]]
    return (statistics.median(rates) if rates else 0.0), len(rates)


def rows():
    measured = {nuts3: _rate(_ads(path)) for nuts3, (path, _, _) in CITIES.items()}
    regional = [rate for nuts3, (rate, n) in measured.items() if nuts3 not in ("LV00A", "LV00C") and n >= MIN_ADS]
    fallback = statistics.median(regional)
    out = []
    for nuts3, (path, name, geonames) in CITIES.items():
        rate, n = measured[nuts3]
        code = c.city_code("LV", geonames)
        if n >= MIN_ADS:
            out.append(c.row(
                c.place(nuts3), round(rate * c.TWO_BED_M2), "EUR", "per_month", PERIOD, code or c.place(nuts3), SOURCE_ID,
                f"ss.lv median asking rent in {name}, {rate:.2f} EUR/m2 over {n} monthly lets of {AREA_RANGE[0]} to "
                f"{AREA_RANGE[1]} m2, x 75 m2."))
        else:
            out.append(c.row(
                c.place(nuts3), round(fallback * c.TWO_BED_M2), "EUR", "per_month", PERIOD, "LV", SOURCE_ID,
                f"ss.lv had only {n} usable ads in {name}. National stand-in, not local: median {fallback:.2f} EUR/m2 "
                f"of Daugavpils, Jelgava and Liepaja (regional cities outside Riga), x 75 m2."))
    return out
