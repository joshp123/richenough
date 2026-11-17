#!/usr/bin/env python3
"""Two-bedroom monthly rent estimates published by The Africanvestor, for cities and countries with no better free source.

The Africanvestor (a seller of paid property data packs) publishes a free blog page per city or country with a
"typical 2-bedroom rent" in local currency and US dollars. Its method note says it compares the asking rents of
several portals and then adjusts them with the firm's own rent model, so the figure is a modelled estimate, not an
observed median. We save each page in cache/africanvestor/ and read the 2-bedroom sentence. Run directly to print
the rows as CSV.
"""

import csv
import html
import pathlib
import re
import sys
import time
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from places import city_code  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[3]
CACHE = REPO / "cache" / "africanvestor"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
SOURCE_ID = "africanvestor-rents"
BASE = "https://theafricanvestor.com/blogs/news/"

SOURCES = [
    {
        "source_id": SOURCE_ID,
        "publisher": "The Africanvestor",
        "title": "Updated rents in <city> (2026): free blog pages with typical 2-bedroom rents",
        "url": BASE + "kampala-rents",
        "licence": "free to read, no licence stated",
        "retrieved": "2026-11-17",
        "period": "2026",
        "note": "Modelled estimate: portal asking rents compared and then adjusted with the publisher's own rent model; method not auditable. Used as a cross-check, or as a thin figure where nothing else is free.",
    }
]

# page slug, ISO country, city name (None = country-level page), label, currency ISO code of the page's local figure
PAGES = [
    ("kampala-rents", "UG", "Kampala", "Kampala", "UGX"),
    ("cape-town-rents", "ZA", "Cape Town", "Cape Town", "ZAR"),
    ("dar-es-salaam-rents", "TZ", "Dar es Salaam", "Dar es Salaam", "TZS"),
    ("addis-ababa-rents", "ET", "Addis Ababa", "Addis Ababa", "ETB"),
    ("dakar-rents", "SN", "Dakar", "Dakar", "XOF"),
    ("abidjan-rents", "CI", "Abidjan", "Abidjan", "XOF"),
    ("maputo-rents", "MZ", "Maputo", "Maputo", "MZN"),
    ("kinshasa-rents", "CD", "Kinshasa", "Kinshasa", "CDF"),
    ("douala-rents", "CM", "Douala", "Douala", "XAF"),
    ("abuja-rents", "NG", "Abuja", "Abuja", "NGN"),
    ("ghana-rents", "GH", None, "Ghana (mostly Accra)", "GHS"),
]

SENTENCE = re.compile(r"average monthly rent for a (?:normal )?2-bedroom (?:apartment )?in [^.?]*? is about (.{1,40}?)(?:,? which|,? or roughly)", re.I)
NUMBER = re.compile(r"([\d][\d,]*(?:\.\d+)?)( million| billion)?", re.I)


def fetch(url: str, dest: pathlib.Path) -> str:
    if dest.exists():
        return dest.read_text(encoding="utf-8")
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    text = urllib.request.urlopen(req, timeout=40).read().decode("utf-8", "replace")
    dest.write_text(text, encoding="utf-8")
    time.sleep(1.0)
    return text


def two_bed(text: str) -> tuple[float, str] | None:
    plain = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", re.sub(r"<script.*?</script>|<style.*?</style>", "", text, flags=re.S))))
    m = SENTENCE.search(plain)
    n = NUMBER.search(m.group(1)) if m else None
    if not n:
        return None
    unit = {None: 1, " million": 1e6, " billion": 1e9}[n.group(2).lower() if n.group(2) else None]
    start = plain.rfind("What's the average monthly rent for a 2-bedroom", 0, m.end())
    return float(n.group(1).replace(",", "")) * unit, plain[start:start + 420]


def updated(text: str) -> str:
    m = re.search(r"Last updated on\s+([A-Z][a-z]+ \d+, \d{4})", re.sub(r"<[^>]+>", " ", text))
    return m.group(1) if m else "2026"


def rows() -> list[dict]:
    out = []
    for slug, iso, city, label, cur in PAGES:
        text = fetch(BASE + slug, CACHE / f"{slug}.html")
        found = two_bed(text)
        if not found:
            continue
        amount, quote = found
        out.append({
            "place_code": city_code(city, iso) if city else iso,
            "amount": round(amount),
            "currency": cur,
            "unit": "per_month",
            "period": "2026",
            "measured_for": f"{label}, typical 2-bedroom apartment, modelled estimate from portal asking rents",
            "source_id": SOURCE_ID,
            "note": f"THIN, modelled: page last updated {updated(text)}. Quote: '{quote}'",
        })
    return out


if __name__ == "__main__":
    w = csv.DictWriter(sys.stdout, fieldnames=["place_code", "amount", "currency", "unit", "period", "measured_for", "source_id", "note"])
    w.writeheader()
    w.writerows(rows())
