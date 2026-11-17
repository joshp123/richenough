#!/usr/bin/env python3
"""Median asking rent of two-bedroom flats on the Property24 network's African country sites.

Property24's non-South-African sites (Kenya, Zambia, Botswana, Zimbabwe, Mozambique, Nigeria, Mauritius) share one
results-page layout. For each city we save up to MAX_PAGES results pages in cache/property24-network/<slug>/, drop
duplicate ad numbers, keep ads titled exactly "2 Bedroom Apartment / Flat", and take the median asking price.
Nigerian ads are quoted per year; the script divides by 12. Run directly to print the rows as CSV.
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
CACHE = REPO / "cache" / "property24-network"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
SOURCE_ID = "property24-africa-listings"
MAX_PAGES = 40

SOURCES = [
    {
        "source_id": SOURCE_ID,
        "publisher": "Property24 (Media24 / Naspers group), country sites",
        "title": "Apartments / flats to rent, two bedrooms, results pages per city (asking rents)",
        "url": "https://www.property24.co.ke/2-bedroom-apartments-flats-to-rent-in-nairobi-p95",
        "licence": "free to read, no licence stated; pages saved in cache, medians are our own calculation",
        "retrieved": "2026-11-17",
        "period": "2026-11",
        "note": "Median asking rent of distinct current ads titled '2 Bedroom Apartment / Flat'. Asking, not paid, rent. Property24's minor-country sites carry few ads and many come from a handful of agents.",
    }
]

# slug, domain, path, place name, ISO country, currency, divisor (12 where the portal quotes a year), label
CITIES = [
    ("nairobi", "property24.co.ke", "2-bedroom-apartments-flats-to-rent-in-nairobi-p95", "Nairobi", "KE", "KES", 1, "Nairobi, whole city, mostly Westlands, Kilimani, Kileleshwa and Parklands"),
    ("lusaka", "property24.co.zm", "2-bedroom-apartments-flats-to-rent-in-lusaka-p155", "Lusaka", "ZM", "ZMW", 1, "Lusaka, whole city"),
    ("gaborone", "property24.co.bw", "2-bedroom-apartments-flats-to-rent-in-south-east-district-p132", "Gaborone", "BW", "BWP", 1, "Gaborone and the South-East District"),
    ("harare", "property24.co.zw", "2-bedroom-apartments-flats-to-rent-in-harare-p58", "Harare", "ZW", "USD", 1, "Harare, whole city, quoted in US dollars"),
    ("maputo", "property24.co.mz", "2-bedroom-apartments-flats-to-rent-in-maputo-p143", "Maputo", "MZ", "MZN", 1, "Maputo, whole city, mostly Polana and Sommerschield"),
    ("abuja", "property24.com.ng", "2-bedroom-apartments-flats-to-rent-in-abuja-p20", "Abuja", "NG", "NGN", 12, "Abuja, whole city; annual rents divided by 12"),
]


def fetch(url: str, dest: pathlib.Path) -> str:
    if dest.exists():
        return dest.read_text(encoding="utf-8")
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(3):
        try:
            text = urllib.request.urlopen(req, timeout=40).read().decode("utf-8", "replace")
            break
        except Exception:
            time.sleep(3 * (attempt + 1))
    else:
        return ""
    dest.write_text(text, encoding="utf-8")
    time.sleep(1.0)
    return text


def parse(text: str) -> list[dict]:
    ads = []
    for tile in re.split(r'<div data-testid="listing-index-\d+"', text)[1:]:
        tile = re.sub(r"\s+", " ", tile)
        price = re.search(r'p24_price">\s*([^<]*?)\s*<', tile)
        title = re.search(r'p24_propertyTitle ">([^<]*)', tile)
        loc = re.search(r'p24_location ">([^<]*)', tile)
        ref = re.search(r'data-listing-number="(\d+)"', tile)
        size = re.search(r'title="Floor Size".*?<span>(\d[\d ]*)\s*m', tile)
        if not (price and title and ref):
            continue
        digits = re.sub(r"\D", "", html.unescape(price.group(1)))
        if not digits:
            continue
        ads.append({"id": ref.group(1), "price": int(digits), "title": html.unescape(title.group(1)).strip(),
                    "suburb": html.unescape(loc.group(1)).strip() if loc else "", "size": int(size.group(1).replace(" ", "")) if size else None})
    return ads


def collect(slug: str, domain: str, path: str) -> tuple[list[dict], int]:
    base = f"https://www.{domain}/{path}"
    first = fetch(base, CACHE / slug / "p1.html")
    pages = min(max([int(n) for n in re.findall(r"\?page=(\d+)", first)] or [1]), MAX_PAGES)
    ads = parse(first)
    for n in range(2, pages + 1):
        ads += parse(fetch(f"{base}?page={n}", CACHE / slug / f"p{n}.html"))
    unique = {a["id"]: a for a in ads}
    return list(unique.values()), pages


def rows() -> list[dict]:
    out = []
    for slug, domain, path, name, iso, cur, div, label in CITIES:
        ads, pages = collect(slug, domain, path)
        two = [a for a in ads if a["title"] == "2 Bedroom Apartment / Flat"]
        if len(two) < 5:
            continue
        prices = sorted(a["price"] / div for a in two)
        med = round(statistics.median(prices))
        sized = [a["price"] / div for a in two if a["size"] and 60 <= a["size"] <= 100]
        suburbs = len({a["suburb"] for a in two})
        out.append({
            "place_code": city_code(name, iso),
            "amount": med,
            "currency": cur,
            "unit": "per_month",
            "period": "2026-11",
            "measured_for": f"{label}, two-bedroom apartment/flat ads, asking rent",
            "source_id": SOURCE_ID,
            "note": (f"Median of {len(two)} distinct 2-bedroom ads in {suburbs} suburbs (first {pages} results pages, 17 Nov 2026, Property24 {iso}); "
                     f"quartiles {round(prices[len(prices)//4])} to {round(prices[3*len(prices)//4])}. "
                     + (f"{len(sized)} ads with 60-100 m2 floor size, median {round(statistics.median(sized))}. " if sized else "")
                     + "Labelled thin: one portal, asking rents."),
        })
    return out


if __name__ == "__main__":
    w = csv.DictWriter(sys.stdout, fieldnames=["place_code", "amount", "currency", "unit", "period", "measured_for", "source_id", "note"])
    w.writeheader()
    w.writerows(rows())
