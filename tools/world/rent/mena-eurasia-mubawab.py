# /// script
# requires-python = ">=3.11"
# ///
"""Median asking rent of two-bedroom flats on Mubawab (Morocco), from saved listing pages.

Written by AI on 2026.11.17 by model claude sonnet 5.5, for the Enough site.

Downloads the first PAGES result pages of "appartements à louer" for each city into
cache/ma-mubawab-listings/<city>/ (skipped if already saved) and takes the median of
the monthly asking rent of listings with exactly two bedrooms ("Chambres") and a living
area of 60 to 100 m2.

Run: uv run tools/world/rent/mena-eurasia-mubawab.py        (prints rows as CSV)
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
CACHE = REPO / "cache" / "ma-mubawab-listings"
PAGES = 15
CITIES = {  # slug on mubawab.ma -> (place_code, name, central districts as Mubawab names them, or None)
    "marrakech": ("CITY-2542997", "Marrakesh", {"Guéliz", "Hivernage", "Agdal", "Majorelle", "Victor Hugo", "Semlalia"}),
    "casablanca": ("CITY-2553604", "Casablanca", None),
    "rabat": ("CITY-2538475", "Rabat", None),
}
SOURCES = [
    {
        "source_id": "ma-mubawab-listings",
        "publisher": "Mubawab",
        "title": "Appartements à louer (listing pages, saved by us)",
        "url": "https://www.mubawab.ma/fr/st/marrakech/appartements-a-louer",
        "licence": "free to read, no licence stated; only a median of our own saved sample is published",
        "retrieved": "2026-11-17",
        "period": "2026-11",
        "note": "Asking rents, not signed leases; includes furnished flats (Mubawab marks them).",
    }
]


def fetch(city: str, page: int) -> str:
    path = CACHE / city / f"p{page:02d}.html"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        suffix = "" if page == 1 else f":p:{page}"
        url = f"https://www.mubawab.ma/fr/st/{city}/appartements-a-louer{suffix}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        path.write_bytes(urllib.request.urlopen(req, timeout=60).read())
        time.sleep(1.5)
    return path.read_text(errors="ignore")


def listings(city: str) -> list[dict]:
    seen, out = set(), []
    for page in range(1, PAGES + 1):
        for box in re.split(r'<div class="listingBox', fetch(city, page))[1:]:
            ad = re.search(r'class="adId" value="(\d+)"', box)
            price = re.search(r'<bdi dir="ltr">([\d\s  ]+)</bdi>\s*<span class="priceCurrency">DH', box)
            area = re.search(r"(\d+)\s*m²", box)
            beds = re.search(r"(\d+)\s*Chambres?", box)
            if not (ad and price and area and beds) or ad.group(1) in seen:
                continue
            seen.add(ad.group(1))
            where = re.search(r'<i class="icon-location"></i>\s*([^<]+)', box)
            out.append({
                "id": ad.group(1),
                "rent": int(re.sub(r"\D", "", price.group(1))),
                "m2": int(area.group(1)),
                "bedrooms": int(beds.group(1)),
                "where": html.unescape(where.group(1)).strip() if where else "",
                "furnished": "icon-furnished" in box,
            })
    return out


def rows() -> list[dict]:
    result = []
    for city, (code, name, centre) in CITIES.items():
        sample = [x for x in listings(city) if x["bedrooms"] == 2 and 60 <= x["m2"] <= 100 and 1500 <= x["rent"] <= 60000]
        if len(sample) < 30:
            continue
        whole = statistics.median(x["rent"] for x in sample)
        where = f"{name}, whole city"
        if centre:
            central = [x for x in sample if x["where"].split(",")[0].strip() in centre]
            median, where = statistics.median(x["rent"] for x in central), f"{name}, central districts ({', '.join(sorted(centre))})"
            extra = f" Central districts: {len(central)} listings; whole city: median {round(whole)} from {len(sample)}."
        else:
            median, extra = whole, ""
        unfurnished = [x["rent"] for x in sample if not x["furnished"]]
        row = {
            "place_code": code,
            "amount": round(median / 100) * 100,
            "currency": "MAD",
            "unit": "per_month",
            "period": "2026-11",
            "measured_for": f"{where}, 2-bedroom flats of 60 to 100 m2, asking rent on Mubawab",
            "source_id": "ma-mubawab-listings",
            "note": f"Median of {len(sample)} listings in the city sample (first {PAGES} result pages, saved 2026-11-17); "
            f"median of the {len(unfurnished)} not marked furnished: {round(statistics.median(unfurnished)) if unfurnished else 'n/a'}.{extra} Thin: asking rents.",
        }
        result.append(row)
        if city == "casablanca":  # Casablanca stands for Morocco: the biggest city, and cheaper than Rabat
            result.append({**row, "place_code": "MA", "measured_for": row["measured_for"] + " (used for Morocco)"})
    return result


if __name__ == "__main__":
    out = csv.DictWriter(sys.stdout, fieldnames=["place_code", "amount", "currency", "unit", "period", "measured_for", "source_id", "note"])
    out.writeheader()
    out.writerows(rows())
