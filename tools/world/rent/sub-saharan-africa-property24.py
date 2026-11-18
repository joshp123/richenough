#!/usr/bin/env python3
"""Median asking rent of two-bedroom flats on Property24 (South Africa), for the Rich enough world rent table.

Property24 lists every active rental ad per city. We save each results page (two bedrooms, all pages) in
cache/property24-za/<slug>/, keep the ads whose title says Apartment / Flat, and take the median asking price.
Ads with a stated floor size of 65-95 m2 give a second median (the brief's "about 70 to 85 m2" band, widened
slightly because sizes are sparse). Run directly to print the rows as CSV; pass --refresh to download again.
"""

import csv
import html
import pathlib
import re
import statistics
import sys
import time
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from places import city_code  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[3]
CACHE = REPO / "cache" / "property24-za"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
SOURCE_ID = "property24-za-listings"

SOURCES = [
    {
        "source_id": SOURCE_ID,
        "publisher": "Property24 (Media24 / Naspers group)",
        "title": "Property to rent, two bedrooms, results pages per city (asking rents)",
        "url": "https://www.property24.com/to-rent/cape-town/western-cape/432?bedrooms=2",
        "licence": "free to read, no licence stated; pages saved in cache, medians are our own calculation",
        "retrieved": "2026-11-17",
        "period": "2026-11",
        "note": "Median asking rent of all current two-bedroom apartment/flat ads in the city's results pages. Asking, not paid, rent.",
    }
]

# slug, Property24 path, place name, ISO country, GeoNames admin1, label for measured_for
CITIES = [
    ("cape-town", "cape-town/western-cape/432", "Cape Town", "ZA", None, "Cape Town"),
    ("johannesburg", "johannesburg/gauteng/100", "Johannesburg", "ZA", None, "Johannesburg"),
    ("pretoria", "pretoria/gauteng/1", "Pretoria", "ZA", None, "Pretoria"),
    ("durban", "durban/kwazulu-natal/169", "Durban", "ZA", None, "Durban"),
]


def fetch(url: str, dest: pathlib.Path, refresh: bool) -> str:
    if dest.exists() and not refresh:
        return dest.read_text(encoding="utf-8")
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(4):
        try:
            text = urllib.request.urlopen(req, timeout=40).read().decode("utf-8", "replace")
            break
        except Exception:
            time.sleep(3 * (attempt + 1))
    else:
        raise RuntimeError(f"cannot fetch {url}")
    dest.write_text(text, encoding="utf-8")
    time.sleep(1.2)
    return text


def parse(text: str) -> list[dict]:
    ads = []
    for tile in re.split(r'<div class="[^"]*js_resultTile p24_tileContainer', text)[1:]:
        tile = re.sub(r"\s+", " ", tile)
        price = re.search(r'class="p24_price" itemprop="price" content="(\d+)"', tile)
        title = re.search(r'itemprop="name" content="([^"]*)"', tile)
        loc = re.search(r'p24_location[^>]*>([^<]*)', tile)
        size = re.search(r'title="Floor Size".*?<span>(\d[\d ]*)\s*m', tile)
        beds = re.search(r'title="Bedrooms".*?<span>\s*(\d+)', tile)
        ref = re.search(r'data-listing-number="(\d+)"', tile)
        if not (price and title):
            continue
        ads.append({
            "id": ref.group(1) if ref else "",
            "price": int(price.group(1)),
            "title": html.unescape(title.group(1)),
            "suburb": html.unescape(loc.group(1).strip()) if loc else "",
            "size": int(size.group(1).replace(" ", "")) if size else None,
            "beds": int(beds.group(1)) if beds else None,
        })
    return ads


def collect(slug: str, path: str, refresh: bool = False) -> list[dict]:
    base = f"https://www.property24.com/to-rent/{path}"
    first = fetch(f"{base}?bedrooms=2", CACHE / slug / "p1.html", refresh)
    pages = max([int(n) for n in re.findall(r'data-pagenumber="(\d+)"', first)] or [1])
    ads = parse(first)
    for n in range(2, pages + 1):
        # Property24 builds the page path as /<area>/<id>/pN
        head, _, area_id = path.rpartition("/")
        url = f"https://www.property24.com/to-rent/{head}/{area_id}/p{n}?bedrooms=2"
        ads += parse(fetch(url, CACHE / slug / f"p{n}.html", refresh))
    seen, unique = set(), []
    for a in ads:
        if a["id"] not in seen:
            seen.add(a["id"])
            unique.append(a)
    return unique


def stats(ads: list[dict]) -> dict:
    flats = [a for a in ads if re.search(r"apartment|flat", a["title"], re.I) and a["beds"] in (2, None)]
    sized = [a for a in flats if a["size"] and 65 <= a["size"] <= 95]
    med = lambda xs: round(statistics.median(a["price"] for a in xs)) if xs else None
    return {"all_ads": len(ads), "flats": len(flats), "flats_median": med(flats), "sized": len(sized), "sized_median": med(sized)}


def rows(refresh: bool = False) -> list[dict]:
    out = []
    for slug, path, name, iso, admin1, label in CITIES:
        s = stats(collect(slug, path, refresh))
        use_sized = s["sized"] >= 50
        amount = s["sized_median"] if use_sized else s["flats_median"]
        basis = (f"ads with a stated floor size of 65-95 m2 ({s['sized']} ads)" if use_sized else f"all {s['flats']} two-bedroom apartment/flat ads")
        out.append({
            "place_code": city_code(name, iso, admin1),
            "amount": amount,
            "currency": "ZAR",
            "unit": "per_month",
            "period": "2026-11",
            "measured_for": f"{label}, whole city as Property24 defines it, two-bedroom apartment/flat ads of 65-95 m2, asking rent",
            "source_id": SOURCE_ID,
            "note": (
                f"Median asking rent of {basis}, from all {s['all_ads']} two-bedroom ads on Property24 results pages, 17 Nov 2026. "
                f"Median of all {s['flats']} two-bedroom apartment/flat ads regardless of size: R{s['flats_median']}. "
                "Asking, not paid, rent. Ads cluster in the suburbs agents list most (see notes file)."
            ),
        })
    return out


if __name__ == "__main__":
    w = csv.DictWriter(sys.stdout, fieldnames=["place_code", "amount", "currency", "unit", "period", "measured_for", "source_id", "note"])
    w.writeheader()
    w.writerows(rows("--refresh" in sys.argv))
