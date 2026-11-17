"""Shared by rent.ee and rent.lv: every flat for rent on City24 in one country, from City24's own public listing API.

City24 (Estonia's and Latvia's second-largest property portal) serves its website's search from
https://api.city24.lv/lv_LV/search/realties, which needs no key. Country code 1 is Estonia, 2 is Latvia. We read all
pages once and keep a compact record per ad in cache/<source_id>/.
"""

import json
import statistics
import time

import requests

import common as c

API = "https://api.city24.lv/lv_LV/search/realties"
AREA_RANGE = (55, 100)
PRICE_RANGE = (100, 5000)


def all_ads(source_id: str, cc: int) -> list[dict]:
    folder = c.CACHE / source_id
    folder.mkdir(parents=True, exist_ok=True)
    cache = folder / f"ads-cc{cc}.json"
    if cache.exists():
        return json.loads(cache.read_text())
    session = requests.Session()
    session.headers["User-Agent"] = c.USER_AGENT
    ads, page = {}, 1
    while True:
        params = {"address[cc]": cc, "tsType": "rent", "unitType": "Apartment", "itemsPerPage": 100, "page": page}
        response = session.get(API, params=params, timeout=120)
        response.raise_for_status()
        batch = response.json()
        if not batch:
            break
        for item in batch:
            address = item.get("address") or {}
            attrs = item.get("attributes") or {}
            ads[item["id"]] = {
                "id": item["id"], "price": float(item["price"]) if item.get("price") else None,
                "area": item.get("property_size"), "rooms": item.get("room_count"),
                "bedrooms": attrs.get("NUMBER_OF_BEDROOMS"),
                "county": (address.get("county") or {}).get("name"), "parish": (address.get("parish") or {}).get("name"),
                "city": (address.get("city") or {}).get("name"), "published": item.get("date_published")}
        page += 1
        time.sleep(0.7)
        if page > 200:
            raise RuntimeError("City24 pagination did not end")
    out = list(ads.values())
    cache.write_text(json.dumps(out))
    return out


def rate(ads: list[dict]) -> tuple[float, int]:
    """Median asking rent per m2 (EUR) over flats of 55 to 100 m2, and how many ads that is."""
    rates = [a["price"] / a["area"] for a in ads
             if a["price"] and a["area"] and AREA_RANGE[0] <= a["area"] <= AREA_RANGE[1]
             and PRICE_RANGE[0] <= a["price"] <= PRICE_RANGE[1]]
    return (statistics.median(rates) if rates else 0.0), len(rates)
