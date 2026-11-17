#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""Median asking rent of two-bedroom flats, sampled from current listings on two portal platforms.

Written by AI on 2026.11.17 by model claude sonnet 5.5, for the world-data owner.

Why a sample: for these places no official or published market series exists (see
latin-america.notes.md), so the figure is a median over listings. Every row is labelled thin.

Portals: Fincaraiz (Colombia) and InfoCasas (Uruguay, Paraguay, Bolivia) run on one platform. Each search
page carries its results as JSON in `__NEXT_DATA__` -> props.pageProps.fetchResult.searchFast.data
(21 listings per page, with price, currency, bedrooms and area), so nothing is read off the visible text.

Sample rule: apartments with exactly 2 bedrooms and a stated area of 50 to 110 m2. The pages fetched are
the first 12 result pages (or fewer if the search has fewer) in the portal's default order, so it is not a
random draw. The rent is the advertised rent without building fees. Where a market lists in two currencies,
the median is taken over the currency with more listings; the other is recorded in the note.

rows()        -> table rows: the places named in each target, plus a pooled country row for Colombia and Bolivia
crosschecks() -> same columns, for a district or a second figure; written to the notes only, place_code is the
                 area's own code

Run: uv run tools/world/rent/latin-america-listings.py [--crosschecks]     (prints the rows as CSV)
Raw pages are kept gzipped in cache/latin-america-listings/<target>/pN.html.gz.
"""

import csv
import gzip
import json
import pathlib
import re
import statistics
import sys
import time
import urllib.request

REPO = pathlib.Path(__file__).resolve().parents[3]
CACHE = REPO / "cache" / "latin-america-listings"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
RETRIEVED = "2026-11-17"
PAGES = 12

SOURCES = [
    {"source_id": "fincaraiz-co-listings", "publisher": "Fincaraiz (Colombia)", "title": "Apartments for rent, 2 bedrooms, listing sample", "url": "https://www.fincaraiz.com.co/arriendo/apartamentos", "licence": "free to read, no licence stated", "retrieved": RETRIEVED, "period": "2026-11", "note": "Median of advertised rents, first 12 result pages per search; thin"},
    {"source_id": "infocasas-listings", "publisher": "InfoCasas (Uruguay, Paraguay, Bolivia)", "title": "Apartments for rent, 2 bedrooms, listing sample", "url": "https://www.infocasas.com.uy/alquiler/apartamentos", "licence": "free to read, no licence stated", "retrieved": RETRIEVED, "period": "2026-11", "note": "Median of advertised rents, first 12 result pages per search; thin"},
]

# slug, url, places (ISO 3166-2 code, or (name, iso2) for a GeoNames city), measured_for, source_id, in_table
TARGETS = [
    ("co-medellin", "https://www.fincaraiz.com.co/arriendo/apartamentos/medellin/2-habitaciones", ["CO-ANT"], "Medellin, whole city (the main town of Antioquia), flats on the portal", "fincaraiz-co-listings", True),
    ("co-medellin-el-poblado", "https://www.fincaraiz.com.co/arriendo/apartamentos/el-poblado/medellin/2-habitaciones", [("Medellín", "CO")], "Medellin, the portal's El Poblado search (also catches neighbouring Castropol and Guayabal)", "fincaraiz-co-listings", False),
    ("co-bogota", "https://www.fincaraiz.com.co/arriendo/apartamentos/bogota/2-habitaciones", [("Bogotá", "CO"), "CO-DC"], "Bogota, whole city, flats on the portal", "fincaraiz-co-listings", True),
    ("co-cali", "https://www.fincaraiz.com.co/arriendo/apartamentos/cali/2-habitaciones", [("Cali", "CO"), "CO-VAC"], "Cali, whole city (the main town of Valle del Cauca), flats on the portal", "fincaraiz-co-listings", True),
    ("co-barranquilla", "https://www.fincaraiz.com.co/arriendo/apartamentos/barranquilla/2-habitaciones", [("Barranquilla", "CO"), "CO-ATL"], "Barranquilla, whole city (the main town of Atlantico), flats on the portal", "fincaraiz-co-listings", True),
    ("uy-montevideo", "https://www.infocasas.com.uy/alquiler/apartamentos/montevideo/2-dormitorios", ["UY-MO"], "Montevideo department, flats on the portal", "infocasas-listings", False),
    ("py-asuncion", "https://www.infocasas.com.py/alquiler/departamentos/asuncion", [("Asunción", "PY"), "PY-ASU", "PY"], "Asuncion, flats on the portal (the capital; no other Paraguayan city sampled)", "infocasas-listings", True),
    ("bo-la-paz", "https://www.infocasas.com.bo/alquiler/departamentos/la-paz/2-dormitorios", [("La Paz", "BO"), "BO-L"], "La Paz (Bolivia), flats on the portal", "infocasas-listings", True),
    ("bo-santa-cruz", "https://www.infocasas.com.bo/alquiler/departamentos/santa-cruz/2-dormitorios", [("Santa Cruz de la Sierra", "BO"), "BO-S"], "Santa Cruz de la Sierra, flats on the portal", "infocasas-listings", True),
]
POOLED = {  # country row: pooled median over these targets (all in one currency)
    "CO": ("co-medellin", "co-bogota", "co-cali", "co-barranquilla"),
    "BO": ("bo-la-paz", "bo-santa-cruz"),
}
LOCAL = {"CO": "COP", "UY": "UYU", "PY": "PYG", "BO": "BOB"}
CURRENCY_CODE = {"U$S": "USD", "Gs.": "PYG", "Bs": "BOB"}


def _get(url: str) -> str:
    for attempt in range(3):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=40).read().decode("utf-8", "replace")
        except Exception:
            if attempt == 2:
                raise
            time.sleep(3)
    raise RuntimeError("unreachable")


def _next_data(html: str) -> dict:
    return json.loads(re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S).group(1))["props"]["pageProps"]["fetchResult"]["searchFast"]


def _pages(slug: str, url: str) -> list[dict]:
    """The search pages as parsed `searchFast` blocks, fetched once and kept gzipped."""
    d = CACHE / slug
    d.mkdir(parents=True, exist_ok=True)
    out, last, n = [], PAGES, 1
    while n <= last:
        f = d / f"p{n}.html.gz"
        if not f.exists():
            html = _get(url if n == 1 else f"{url}/pagina{n}")
            if "__NEXT_DATA__" not in html or _next_data(html)["paginatorInfo"]["currentPage"] != n:
                break  # a challenge page, or the portal silently served page 1 again
            with gzip.open(f, "wt", encoding="utf-8") as fh:
                fh.write(html)
            time.sleep(1.0)
        with gzip.open(f, "rt", encoding="utf-8") as fh:
            block = _next_data(fh.read())
        out.append(block)
        if n == 1:
            last = min(PAGES, block["paginatorInfo"]["lastPage"])
        n += 1
    return out


def _area(x: dict):
    for k in ("m2apto", "m2Built", "m2"):
        v = x.get(k)
        if isinstance(v, str):
            m = re.search(r"[\d.]+", v)
            v = float(m.group(0)) if m else None
        if v:
            return float(v)
    return None


def _flats(slug: str, url: str, iso2: str) -> dict[str, list[dict]]:
    """Two-bedroom flats of 50 to 110 m2, grouped by rent currency."""
    seen, by = set(), {}
    for block in _pages(slug, url):
        for x in block["data"]:
            area, bed = _area(x), x.get("bedrooms")
            if x["id"] in seen or bed != 2 or not area or not 50 <= area <= 110 or not x["price"]["amount"]:
                continue
            seen.add(x["id"])
            name = (x["price"].get("currency") or {}).get("name")
            code = CURRENCY_CODE.get(name, LOCAL[iso2] if name == "$" else name)
            by.setdefault(code, []).append({"rent": x["price"]["amount"], "area": area})
    return by


def _q(vals, p):
    vals = sorted(vals)
    k = (len(vals) - 1) * p
    lo, hi = int(k), min(int(k) + 1, len(vals) - 1)
    return vals[lo] + (vals[hi] - vals[lo]) * (k - lo)


def _row(code, measured, source_id, items, main, url, other="", pooled=""):
    rents = [i["rent"] for i in items]
    return {
        "place_code": code, "amount": f"{statistics.median(rents):.0f}", "currency": main, "unit": "per_month", "period": "2026-11",
        "measured_for": f"{measured}; median advertised rent of 2-bedroom flats, without building fees",
        "source_id": source_id,
        "note": (f"THIN: {pooled or 'sample'} of {len(items)} flats (2 bedrooms, 50-110 m2, median {statistics.median(i['area'] for i in items):.0f} m2), "
                 f"quartiles {_q(rents, .25):,.0f} to {_q(rents, .75):,.0f}; first {PAGES} result pages at most, in the portal's default order, fetched {RETRIEVED}; URL {url}"
                 + (f"; also {other}" if other else "")),
    }


def _build(table: bool) -> list[dict]:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
    from places import city_code

    out, data = [], {}
    for slug, url, places, measured, source_id, in_table in TARGETS:
        iso2 = slug[:2].upper()
        by = _flats(slug, url, iso2)
        if not by:
            continue
        main = max(by, key=lambda c: len(by[c]))
        data[slug] = (iso2, main, by[main], url, source_id)
        if in_table != table:
            continue
        other = "; ".join(f"{len(v)} listings in {c} (median {statistics.median([i['rent'] for i in v]):,.0f})" for c, v in by.items() if c != main)
        for p in places:
            code = p if isinstance(p, str) else city_code(*p)
            out.append(_row(code, measured, source_id, by[main], main, url, other))
    if table:
        for iso2, slugs in POOLED.items():
            cur = {data[s][1] for s in slugs if s in data}
            if len(cur) != 1:
                continue
            items = [i for s in slugs if s in data for i in data[s][2]]
            out.append(_row(iso2, f"The {len(slugs)} sampled cities together ({', '.join(s.split('-', 1)[1] for s in slugs)}), unweighted pool; not a national figure",
                            data[slugs[0]][4], items, cur.pop(), data[slugs[0]][3], pooled="pooled sample"))
    return out


def rows() -> list[dict]:
    return _build(table=True)


def crosschecks() -> list[dict]:
    return _build(table=False)


if __name__ == "__main__":
    w = csv.DictWriter(sys.stdout, ["place_code", "amount", "currency", "unit", "period", "measured_for", "source_id", "note"])
    w.writeheader()
    w.writerows(crosschecks() if "--crosschecks" in sys.argv else rows())
