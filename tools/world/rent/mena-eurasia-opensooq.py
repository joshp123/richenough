# /// script
# requires-python = ">=3.11"
# ///
"""Very thin fallback: median asking rent of two-bedroom flats on OpenSooq, for countries with no better free source.

Written by AI on 2026.11.17 by model claude sonnet 5.5, for the Enough site.

OpenSooq runs classifieds in most Arab countries. For each country this saves the first PAGES pages of
"apartments for rent, 2 bedrooms" (30 cards a page, country-wide) to cache/opensooq/<country>/ and takes
the median price of cards that: have exactly 2 bedrooms, state an area of 60 to 100 m2, are listed monthly,
and are not obvious typing errors (below a quarter or above four times the sample's first-pass median).
Use cards marked Monthly so annual and short-stay quotes cannot enter the median.

Run: uv run tools/world/rent/mena-eurasia-opensooq.py        (prints rows as CSV)
"""

import csv
import html
import pathlib
import re
import statistics
import sys
import time
import urllib.request

REPO = pathlib.Path(__file__).resolve().parents[3]
CACHE = REPO / "cache" / "opensooq"
PAGES = 10
# Source location ends in its governorate. Kuwait City and Hawally form one metro.
CAPITAL_AREAS = {
    "kw": ("CITY-285787", "Kuwait City", {"Kuwait City", "Hawally"}),
    "bh": ("CITY-290340", "Manama", {"Manama"}),
    "iq": ("CITY-98182", "Baghdad", {"Baghdad"}),
    "jo": ("CITY-250441", "Amman", {"Amman"}),
    "eg": ("CITY-360630", "Greater Cairo", {"Cairo", "Giza"}),
    "ly": ("CITY-2210247", "Tripoli", {"Tripoli"}),
    "om": ("CITY-287286", "Muscat", {"Muscat"}),
}
CURRENCY = {"kw": "KWD", "bh": "BHD", "iq": "IQD", "jo": "JOD", "eg": "EGP", "ly": "LYD", "om": "OMR", }
SOURCES = [
    {
        "source_id": f"opensooq-{sub}",
        "publisher": "OpenSooq",
        "title": f"Two-bedroom apartment listings in {sub.upper()}",
        "url": f"https://{sub}.opensooq.com/en/property/apartments-for-rent/2-bedrooms",
        "licence": "free to read, no licence stated; only a median of our own saved sample is published",
        "retrieved": "2026-11-17",
        "period": "2026-11",
        "note": "Asking rents from a classifieds site, undated cards; very thin.",
    } for sub in CAPITAL_AREAS
]


def page(country: str, n: int) -> str:
    path = CACHE / country / f"p{n:02d}.html"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        url = f"https://{country}.opensooq.com/en/property/apartments-for-rent/2-bedrooms" + ("" if n == 1 else f"?page={n}")
        path.write_bytes(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read())
        time.sleep(1.5)
    return path.read_text(errors="ignore")


def cards(country: str) -> list[dict]:
    seen, out = set(), []
    for n in range(1, PAGES + 1):
        for part in re.split(r'(?=<a href="/en/search/\d+")', page(country, n))[1:]:
            part = part[:6000]
            ident = re.match(r'<a href="/en/search/(\d+)"', part).group(1)
            price = re.search(r'redColor bold font-18">([\d,]+)\s*([A-Z]{3})<', part)
            alts = dict(re.findall(r'star_cps/(\w+)\.webp" alt="([^"]*)"', part))
            where = re.search(r"locationRow.*?<span[^>]*>([^<]+)<", part, flags=re.S)
            area = re.search(r"(\d+)\s*m2", alts.get("area", ""))
            if ident in seen or not (price and area):
                continue
            seen.add(ident)
            out.append({
                "price": int(price.group(1).replace(",", "")), "currency": price.group(2), "m2": int(area.group(1)),
                "bedrooms": alts.get("bedrooms", ""), "period": alts.get("rental_period", ""), "where": html.unescape(where.group(1)) if where else "",
            })
    return out


def clean(sample: list[dict]) -> list[dict]:
    first = statistics.median(x["price"] for x in sample)
    return [x for x in sample if first / 4 <= x["price"] <= first * 4]


def rows() -> list[dict]:
    result = []
    for sub, (city, name, areas) in CAPITAL_AREAS.items():
        sample = [x for x in cards(sub) if x["bedrooms"].startswith("2 ") and 60 <= x["m2"] <= 100
                  and x["period"] == "Monthly" and x["currency"] == CURRENCY[sub]]
        capital = [x for x in sample if x["where"].rsplit(",", 1)[-1].strip() in areas]
        for code, location, listings in [(sub.upper(), "Country-wide", sample), (city, name, capital)]:
            if len(listings) < 15:
                continue
            kept = clean(listings)
            if len(kept) < 15:
                continue
            result.append({
                "place_code": code, "amount": round(statistics.median(x["price"] for x in kept)),
                "currency": CURRENCY[sub], "unit": "per_month", "period": "2026-11",
                "measured_for": f"{location} listings in {sub.upper()}, two-bedroom flats of 60 to 100 m²",
                "source_id": f"opensooq-{sub}",
                "note": f"Median of {len(kept)} distinct ads marked Monthly on the first {PAGES} pages, saved 2026-11-17. "
                        f"Excluded {len(listings) - len(kept)} prices outside ¼ to 4× the first median. "
                        f"Thin asking-price sample: https://{sub}.opensooq.com/en/property/apartments-for-rent/2-bedrooms",
            })
    return result


if __name__ == "__main__":
    out = csv.DictWriter(sys.stdout, fieldnames=["place_code", "amount", "currency", "unit", "period", "measured_for", "source_id", "note"])
    out.writeheader()
    out.writerows(rows())
