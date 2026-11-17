#!/usr/bin/env python3
"""Median asking rent of two-bedroom flats advertised to expatriates on Expat.com, for countries with no better free source.

Expat.com lists flats for rent per country. For each country we save the results pages (English site) in
cache/expat-com/<slug>/, keep ads that say "N bedrooms" = 2 and are priced "per month", and take the median per
currency (the dominant currency wins). Run directly to print the rows as CSV. A country needs MIN_ADS usable ads
to get a row; the note carries the sample size.
"""

import collections
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
CACHE = REPO / "cache" / "expat-com"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
SOURCE_ID = "expat-com-listings"
MAX_PAGES = 30
MIN_ADS = 7

SOURCES = [
    {
        "source_id": SOURCE_ID,
        "publisher": "Expat.com",
        "title": "Flats for rent, per-country listings (asking rents advertised to expatriates)",
        "url": "https://www.expat.com/en/housing/africa/ivory-coast/flats-for-rent.html",
        "licence": "free to read, no licence stated; pages saved in cache, medians are our own calculation",
        "retrieved": "2026-11-17",
        "period": "2026-11",
        "note": "Median asking monthly rent of current two-bedroom flat ads in the country's Expat.com listings. Ads can be months old; Expat.com's currency symbols are not always right, so the currency is the one the country's ads mostly use.",
    }
]

# slug, ISO code, expected currency for the unlabelled/odd symbols, city name for a city row (None = country row), label
COUNTRIES = [
    ("ivory-coast", "CI", "XOF", "Abidjan", "Abidjan (Cocody, Marcory, Plateau)"),
    ("senegal", "SN", "XOF", "Dakar", "Dakar"),
    ("madagascar", "MG", "MGA", "Antananarivo", "Antananarivo"),
    ("mauritius", "MU", "MUR", None, "Mauritius"),
    ("cameroon", "CM", "XAF", None, "Cameroon (Douala, Yaoundé)"),
    ("benin", "BJ", "XOF", "Cotonou", "Cotonou"),
    ("togo", "TG", "XOF", None, "Togo (Lomé)"),
    ("burkina-faso", "BF", "XOF", None, "Burkina Faso (Ouagadougou)"),
    ("democratic-republic-of-congo", "CD", "USD", None, "DR Congo (Kinshasa)"),
    ("ethiopia", "ET", "ETB", None, "Ethiopia (Addis Ababa)"),
    ("kenya", "KE", "KES", None, "Kenya (Nairobi)"),
    ("tanzania", "TZ", "TZS", None, "Tanzania (Dar es Salaam)"),
]
SYMBOLS = {"$": "USD", "€": "EUR", "£": "GBP"}


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


CARD = re.compile(
    r"\|([^|]{2,40})\|\|([^|]*?) per month\|\|\|([^|]*)\|\|[^|]*\|\|(?:Flat|Apartment)[^|]*?for rent, (\d+) bedrooms?,? ?(?:(\d+) \(m2\))?\|\|([^|]*)\|"
)


def ads(text: str) -> list[dict]:
    body = re.sub(r"<script.*?</script>|<style.*?</style>", "", text, flags=re.S)
    flat = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "|", body)))
    out = []
    for place, price, title, beds, size, age in CARD.findall(flat):
        digits = re.sub(r"\D", "", price.split(".")[0] if re.search(r"\.\d{2}$", price) else price)
        if not digits:
            continue
        symbol = re.sub(r"[\d,.\s]", "", price)
        out.append({"place": place.strip(), "price": int(digits), "symbol": symbol, "beds": int(beds), "size": int(size) if size else None, "age": age.strip(), "title": title.strip()})
    return out


def collect(slug: str) -> list[dict]:
    found = []
    for p in range(1, MAX_PAGES + 1):
        suffix = "" if p == 1 else f"_{p}"
        page = ads(fetch(f"https://www.expat.com/en/housing/africa/{slug}/flats-for-rent{suffix}.html", CACHE / slug / f"p{p}.html"))
        if not page:
            break
        found += page
    seen, unique = set(), []
    for a in found:
        key = (a["place"], a["price"], a["title"])
        if key not in seen:
            seen.add(key)
            unique.append(a)
    return unique


def rows() -> list[dict]:
    out = []
    for slug, iso, expected, city, label in COUNTRIES:
        two = [a for a in collect(slug) if a["beds"] == 2]
        if len(two) < MIN_ADS:
            continue
        currencies = collections.Counter(SYMBOLS.get(a["symbol"], expected) for a in two)
        cur, n = currencies.most_common(1)[0]
        prices = sorted(a["price"] for a in two if SYMBOLS.get(a["symbol"], expected) == cur)
        code = city_code(city, iso) if city else iso
        out.append({
            "place_code": code,
            "amount": round(statistics.median(prices)),
            "currency": cur,
            "unit": "per_month",
            "period": "2026-11",
            "measured_for": f"{label}, two-bedroom flats advertised to expatriates on Expat.com, asking rent",
            "source_id": SOURCE_ID,
            "note": f"THIN: median of {n} two-bedroom flat ads priced per month (of {len(two)} two-bedroom ads, {currencies.get(cur, 0)} in {cur}); quartiles {prices[len(prices)//4]} to {prices[3*len(prices)//4]}. Ads up to several months old; one portal.",
        })
    return out


if __name__ == "__main__":
    w = csv.DictWriter(sys.stdout, fieldnames=["place_code", "amount", "currency", "unit", "period", "measured_for", "source_id", "note"])
    w.writeheader()
    w.writerows(rows())
