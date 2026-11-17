# /// script
# requires-python = ">=3.11"
# ///
"""Belarus: median asking rent of two-room flats in Minsk on Realt.by, from saved listing pages.

Written by AI on 2026.11.17 by model claude sonnet 5.5, for the Enough site.

Saves every result page of "long-term flat rent in Minsk" (90 listings a page) to
cache/by-realt/ and takes the median of listings with 2 rooms and a total area of 50 to 100 m2.
Prices are in the listing's own currency (code 840 = US dollars, 933 = Belarusian rubles).

Run: uv run tools/world/rent/mena-eurasia-realtby.py        (prints rows as CSV)
"""

import csv
import json
import pathlib
import re
import statistics
import sys
import time
import urllib.request

REPO = pathlib.Path(__file__).resolve().parents[3]
CACHE = REPO / "cache" / "by-realt"
URL = "https://realt.by/rent/flat-for-long/"
CURRENCY = {840: "USD", 933: "BYN", 978: "EUR", 643: "RUB"}
SOURCES = [
    {
        "source_id": "by-realt",
        "publisher": "Realt.by",
        "title": "Long-term flat rent in Minsk (listing pages, saved by us)",
        "url": URL,
        "licence": "free to read, no licence stated; only a median of our own saved sample is published",
        "retrieved": "2026-11-17",
        "period": "2026-11",
        "note": "Asking rents, not signed leases.",
    }
]


def page(n: int) -> dict:
    path = CACHE / f"p{n:02d}.html"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        request = urllib.request.Request(f"{URL}?page={n}", headers={"User-Agent": "Mozilla/5.0"})
        path.write_bytes(urllib.request.urlopen(request, timeout=60).read())
        time.sleep(1.5)
    data = json.loads(re.search(r'__NEXT_DATA__" type="application/json">(.*?)</script>', path.read_text(errors="ignore"), flags=re.S).group(1))
    return data["props"]["pageProps"]


def listings() -> list[dict]:
    first = page(1)
    pages = -(-first["pagination"]["totalCount"] // first["pagination"]["pageSize"])
    seen, out = set(), []
    for n in range(1, pages + 1):
        for obj in page(n)["objects"]:
            if obj["uuid"] not in seen:
                seen.add(obj["uuid"])
                out.append(obj)
    return out


def rows() -> list[dict]:
    everything = listings()
    n_unique = len(everything)
    sample = [o for o in everything if o.get("rooms") == 2 and o.get("areaTotal") and 50 <= o["areaTotal"] <= 100 and o.get("price")]
    by_currency = {}
    for o in sample:
        by_currency.setdefault(o["priceCurrency"], []).append(o["price"])
    code = 933 if len(by_currency.get(933, [])) >= 30 else max(by_currency, key=lambda c: len(by_currency[c]))
    prices = by_currency[code]
    others = "; ".join(f"{len(v)} listings priced in {CURRENCY[c]} have median {round(statistics.median(v))}" for c, v in by_currency.items() if c != code)
    row = {
        "place_code": "CITY-625144",
        "amount": round(statistics.median(prices)),
        "currency": CURRENCY[code],
        "unit": "per_month",
        "period": "2026-11",
        "measured_for": "Minsk, whole city, 2-room flats of 50 to 100 m2, asking rent on Realt.by",
        "source_id": "by-realt",
        "note": f"Median of {len(prices)} listings priced in {CURRENCY[code]} (of {len(sample)} two-room listings; {n_unique} unique listings on the Minsk long-term rent pages, saved 2026-11-17). Other currencies in the same sample: {others}. Thin: asking rents.",
    }
    return [row, {**row, "place_code": "BY", "measured_for": row["measured_for"] + " (used for Belarus)"}]


if __name__ == "__main__":
    out = csv.DictWriter(sys.stdout, fieldnames=["place_code", "amount", "currency", "unit", "period", "measured_for", "source_id", "note"])
    out.writeheader()
    out.writerows(rows())
