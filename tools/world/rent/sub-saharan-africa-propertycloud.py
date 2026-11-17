#!/usr/bin/env python3
"""Median asking rent of two-bedroom flats on the Propertycloud-engine portals of Mauritius and Zimbabwe.

Propertycloud.mu and Property.co.zw share one layout: a results page per "2 Bedroom ... for Rent" with ads priced
"<currency> N per month". For each site we save every results page in cache/propertycloud/<slug>/, take the median
of the prices, and report the quartiles. No ad id is exposed, so ads that repeat across pages (featured ads) are
counted each time they appear. Run directly to print the rows as CSV.
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
CACHE = REPO / "cache" / "propertycloud"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
SOURCE_ID = "propertycloud-listings"
MAX_PAGES = 80

SOURCES = [
    {
        "source_id": SOURCE_ID,
        "publisher": "Propertycloud.mu and Property.co.zw (same portal engine)",
        "title": "2 Bedroom apartments / flats for rent (results pages)",
        "url": "https://www.propertycloud.mu/apartments-for-rent/2-bedroom",
        "licence": "free to read, no licence stated; pages saved in cache, medians are our own calculation",
        "retrieved": "2026-11-17",
        "period": "2026-11",
        "note": "Median asking monthly rent of current two-bedroom ads, long-term and furnished mixed. Asking, not paid, rent.",
    }
]

# slug, results URL, price regex prefix, place code, currency, measured_for
SITES = [
    ("mauritius", "https://www.propertycloud.mu/apartments-for-rent/2-bedroom", "Rs", "MU", "MUR",
     "Mauritius, island-wide (mostly Grand Baie, Flic-en-Flac, Quatre Bornes, Moka), two-bedroom apartment ads, asking rent"),
    ("zimbabwe", "https://www.property.co.zw/flats-apartments-for-rent/2-bedroom", "USD", "ZW", "USD",
     "Zimbabwe (mostly Harare), two-bedroom flat and apartment ads priced in US dollars, asking rent"),
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


def prices(text: str, prefix: str) -> list[int]:
    body = re.sub(r"<script.*?</script>|<style.*?</style>", "", text, flags=re.S)
    plain = html.unescape(re.sub(r"<[^>]+>", " ", body))
    return [int(p.replace(",", "")) for p in re.findall(prefix + r"\s?([\d,]+)\s*per month", plain)]


def rows() -> list[dict]:
    out = []
    for slug, base, prefix, code, cur, label in SITES:
        found = prices(fetch(base, CACHE / slug / "p1.html"), prefix)
        pages = 1
        for n in range(2, MAX_PAGES + 1):
            more = prices(fetch(f"{base}?page={n}", CACHE / slug / f"p{n}.html"), prefix)
            if len(more) < 5:
                break
            found += more
            pages = n
        found = sorted(p for p in found if p >= (5000 if cur == "MUR" else 100))
        if len(found) < 10:
            continue
        out.append({
            "place_code": code,
            "amount": round(statistics.median(found)),
            "currency": cur,
            "unit": "per_month",
            "period": "2026-11",
            "measured_for": label,
            "source_id": SOURCE_ID,
            "note": (f"Median of {len(found)} '{prefix} N per month' prices on {pages} results pages (17 Nov 2026), quartiles {found[len(found)//4]} to {found[3*len(found)//4]}. "
                     "Featured ads can repeat across pages (no ad id is exposed). THIN: one portal, asking rents."),
        })
    return out


if __name__ == "__main__":
    w = csv.DictWriter(sys.stdout, fieldnames=["place_code", "amount", "currency", "unit", "period", "measured_for", "source_id", "note"])
    w.writeheader()
    w.writerows(rows())
