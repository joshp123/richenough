# /// script
# requires-python = ">=3.11"
# ///
"""Very thin fallback: median asking rent of two-bedroom flats on OpenSooq, for countries with no better free source.

Written by AI on 2026.11.17 by model claude sonnet 5.5, for the Enough site.

OpenSooq runs classifieds in most Arab countries. For each country this saves the first PAGES pages of
"apartments for rent, 2 bedrooms" (30 cards a page, country-wide) to cache/opensooq/<country>/ and takes
the median price of cards that: have exactly 2 bedrooms, state an area of 60 to 100 m2, are not priced per day,
and are not obvious typing errors (below a quarter or above four times the sample's first-pass median).
OpenSooq's "rental period" label is the lease term, not the unit the price is quoted in, so prices are
read as monthly rents; a price of a whole year would show up as an outlier and be dropped.

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
COUNTRIES = {  # subdomain -> (ISO country, place_code to write, name of the place the sample describes, words that mark the capital in the card's location line)
    "kw": ("KW", "KW", "Kuwait", ("Kuwait City", "Hawally", "Salmiya", "Al Asimah", "Capital")),
    "bh": ("BH", "BH", "Bahrain", ("Manama", "Juffair", "Capital")),
    "iq": ("IQ", "IQ", "Iraq", ("Baghdad",)),
    "jo": ("JO", "JO", "Jordan", ("Amman",)),
    "eg": ("EG", "EG", "Egypt", ("Cairo", "Giza", "New Cairo")),
    "ly": ("LY", "LY", "Libya", ("Tripoli",)),
    "om": ("OM", "OM", "Oman", ("Muscat", "Seeb", "Bawshar", "Mutrah")),
}
CURRENCY = {"kw": "KWD", "bh": "BHD", "iq": "IQD", "jo": "JOD", "eg": "EGP", "ly": "LYD", "om": "OMR", }
SOURCES = [
    {
        "source_id": "opensooq",
        "publisher": "OpenSooq",
        "title": "Apartments for rent, 2 bedrooms (listing pages, saved by us)",
        "url": "https://kw.opensooq.com/en/property/apartments-for-rent/2-bedrooms",
        "licence": "free to read, no licence stated; only a median of our own saved sample is published",
        "retrieved": "2026-11-17",
        "period": "2026-11",
        "note": "Asking rents from a classifieds site, undated cards; very thin.",
    }
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
    for sub, (iso, code, name, capital_words) in COUNTRIES.items():
        sample = [x for x in cards(sub) if x["bedrooms"].startswith("2 ") and 60 <= x["m2"] <= 100 and x["period"] != "Daily" and x["currency"] == CURRENCY[sub]]
        if len(sample) < 30:
            continue
        sample = clean(sample)
        capital = [x for x in sample if any(w in x["where"] for w in capital_words)]
        result.append({
            "place_code": code, "amount": round(statistics.median(x["price"] for x in sample)), "currency": CURRENCY[sub], "unit": "per_month",
            "period": "2026-11", "measured_for": f"{name}, country-wide listings of 2-bedroom flats of 60 to 100 m2, asking rent on OpenSooq", "source_id": "opensooq",
            "note": f"Median of {len(sample)} cards (first {PAGES} pages, saved 2026-11-17); capital area alone: {len(capital)} cards"
            + (f", median {round(statistics.median(x['price'] for x in capital))}" if len(capital) >= 15 else ", too few for a median")
            + ". Very thin: undated classifieds.",
        })
    return result


if __name__ == "__main__":
    out = csv.DictWriter(sys.stdout, fieldnames=["place_code", "amount", "currency", "unit", "period", "measured_for", "source_id", "note"])
    out.writeheader()
    out.writerows(rows())
