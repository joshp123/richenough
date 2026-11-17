#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""Costa Rica and Panama: asking rent of two-bedroom flats, from archived Encuentra24 result pages.

Written by AI on 2026.11.17 by model claude sonnet 5.5, for the world-data owner.

Why archived pages: Encuentra24 is the main rental portal in Costa Rica, Panama and most of Central America, and no official
or published rent series exists there. Guatemala, El Salvador, Honduras, Nicaragua and the Dominican Republic were
tried the same way and left out: fewer than 8 two-bedroom flats in the archive, or (Managua) a sample of very large flats.
Encuentra24 refuses plain scripted fetches (HTTP 403 from its bot filter), so this reads the copies the
Internet Archive made of its public search pages: for each search page, one snapshot per month of 2026
(the Archive's CDX index lists them). The ads on those snapshots are pooled and de-duplicated, so the
sample mixes months from early to late 2026; the months are in the note.
A result page holds about 20 listings, the first ones paid "highlighted" ads, so the sample is small and
tilted to the dearer end. Every row is labelled very thin and a row is only written when at least
MIN_N two-bedroom flats are in the pool.

Sample rule: apartments with exactly 2 bedrooms in the target city's locations; the area is optional
because many ads omit it (the share with an area is in the note). Rent is the advertised monthly rent in
the ad's own currency; the flats are pooled and converted to US dollars at one fixed rate.

Run: uv run tools/world/rent/latin-america-encuentra24-archive.py     (prints the rows as CSV)
Snapshots are kept gzipped in cache/encuentra24-archive/<target>/.
"""

import csv
import gzip
import html
import json
import pathlib
import re
import statistics
import sys
import time
import urllib.error
import urllib.request

REPO = pathlib.Path(__file__).resolve().parents[3]
CACHE = REPO / "cache" / "encuentra24-archive"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
MIN_N = 8
FX_USD = {"CRC": 447.07, "HNL": 26.90, "NIO": 36.80, "DOP": 60.81, "GTQ": 7.64, "USD": 1.0}  # units per US dollar, open.er-api.com, 17 Nov 2026
FX_NOTE = "CRC 447.07, HNL 26.90, NIO 36.80, DOP 60.81, GTQ 7.64 per US$"

SOURCES = [{
    "source_id": "encuentra24-archive",
    "publisher": "Encuentra24 (pages as archived by the Internet Archive)",
    "title": "Apartments for rent, search result pages, 2026 snapshots",
    "url": "https://www.encuentra24.com/costa-rica-es/bienes-raices-alquiler-apartamentos",
    "licence": "free to read, no licence stated",
    "retrieved": "2026-11-17",
    "period": "2026",
    "note": "Advertised rents from about 20 listings per page, snapshot dates 2026-02 to 2026-09; very thin",
}]

# slug, places (ISO 3166-2 / ISO 3166-1 code, or (name, iso2) for a GeoNames city), [(archive path)], location regex, measured_for, snapshots per page
TARGETS = [
    ("cr-san-jose", [("San José", "CR"), "CR-SJ", "CR"],
     ["costa-rica-es/bienes-raices-alquiler-apartamentos"],
     r"San José|Escazú|Santa Ana|Curridabat|Montes de Oca|Moravia|Heredia|Belén|Alajuela|Rohrmoser|Sabana",
     "Greater San Jose (San Jose, Escazu, Santa Ana, Curridabat and neighbouring cantons)", 9),
    ("pa-panama-city", [("Panamá", "PA"), "PA-8", "PA"],
     ["panama-es/bienes-raices-alquiler-apartamentos/prov-panama-ciudad-de-panama", "panama-es/bienes-raices-alquiler-apartamentos"],
     r"Panam|Costa del Este|Cangrejo|San Francisco|Bella Vista|Obarrio|Punta|Balboa|Carmen|Coco del Mar|Marbella|Betania|Edison|Clayton|Albrook",
     "Panama City (districts such as Costa del Este, El Cangrejo, San Francisco, Bella Vista)", 9),
]


def _get(url: str) -> str:
    for attempt in range(6):
        try:
            raw = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=90).read()
            if raw[:2] == b"\x1f\x8b":  # the archive replays the original gzip encoding as-is
                raw = gzip.decompress(raw)
            return raw.decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code != 429 or attempt == 5:
                raise
            print(f"# 429 from {url[:80]}, waiting", file=sys.stderr)
            time.sleep(45)  # the Internet Archive rate-limits bursts
    raise RuntimeError("unreachable")


def _snapshots(path: str, slug: str, limit: int) -> list[tuple[str, str]]:
    """(timestamp, html) of the Internet Archive's snapshots of the page in 2026, one per month, cached on disk."""
    d = CACHE / slug
    d.mkdir(parents=True, exist_ok=True)
    slug_path = path.replace("/", "_")
    listing = d / f"{slug_path}.cdx.json"
    if not listing.exists():
        print(f"# listing snapshots of {path}", file=sys.stderr)
        try:
            listing.write_text(_get(f"https://web.archive.org/cdx/search/cdx?url=encuentra24.com/{path}&output=json&filter=statuscode:200&collapse=timestamp:6&from=2026&limit={limit}"))
        except OSError as e:
            print(f"# no snapshot list for {path}: {e}", file=sys.stderr)
            return []
    rows = json.loads(listing.read_text() or "[]")[1:]  # first row is the header
    out = []
    for row in rows:
        ts = row[1]
        f = d / f"{slug_path}-{ts}.html.gz"
        if not f.exists():
            print(f"# fetching {path} at {ts}", file=sys.stderr)
            try:
                page = _get(f"https://web.archive.org/web/{ts}id_/https://www.encuentra24.com/{path}")
            except OSError as e:
                print(f"# snapshot {ts} of {path} failed: {e}", file=sys.stderr)
                continue
            if "card_price" not in page:
                continue
            with gzip.open(f, "wt", encoding="utf-8") as fh:
                fh.write(page)
            time.sleep(5.0)
        with gzip.open(f, "rt", encoding="utf-8") as fh:
            out.append((ts, fh.read()))
    return out


def _cards(page: str) -> list[dict]:
    out = []
    for chunk in page.split('class="card_details')[1:]:
        price = re.search(r'card_price[^>]*>(.*?)</span>', chunk, re.S)
        sub = re.search(r'card_subtitle[^>]*>(.*?)</p>', chunk, re.S)
        if not price or not sub:
            continue
        ptxt = html.unescape(re.sub(r"<[^>]+>", " ", price.group(1)))
        ptxt = re.sub(r"\s+", " ", ptxt).strip()
        amount = re.search(r"([\d][\d,.]*)", ptxt)
        if not amount:
            continue
        cur = {"₡": "CRC", "RD$": "DOP", "L": "HNL", "Q": "GTQ", "C$": "NIO"}.get(re.sub(r"[\d,.\s]", "", ptxt), "USD")
        specs = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", chunk[: chunk.find("card_description") if "card_description" in chunk else 4000])))
        bed = re.search(r"(\d+)\s*Rec[aá]maras?", specs)
        area = re.search(r"(\d+)\s*m²", specs)
        out.append({
            "rent": float(amount.group(1).replace(",", "")), "currency": cur, "location": html.unescape(re.sub(r"<[^>]+>", "", sub.group(1))).strip(),
            "bedrooms": int(bed.group(1)) if bed else None, "area": int(area.group(1)) if area else None,
        })
    return out


def _q(vals, p):
    vals = sorted(vals)
    k = (len(vals) - 1) * p
    lo, hi = int(k), min(int(k) + 1, len(vals) - 1)
    return vals[lo] + (vals[hi] - vals[lo]) * (k - lo)


def _build() -> list[dict]:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
    from places import city_code

    out = []
    for slug, places, paths, loc_re, measured, limit in TARGETS:
        flats, stamps, pages = [], [], 0
        for path in paths:
            for ts, page in _snapshots(path, slug, limit):
                pages += 1
                stamps.append(ts[:6])
                flats += [c for c in _cards(page) if c["bedrooms"] == 2 and re.search(loc_re, c["location"])]
        seen, uniq = set(), []
        for f in flats:  # the same ad can sit on two of the pages
            key = (f["rent"], f["location"], f["area"])
            if key not in seen:
                seen.add(key)
                uniq.append(f)
        if len(uniq) < MIN_N:
            print(f"# {slug}: only {len(uniq)} two-bedroom flats in {pages} archived page(s); no row", file=sys.stderr)
            continue
        by = {}
        for f in uniq:
            by.setdefault(f["currency"], []).append(f["rent"])
        rents = [f["rent"] / FX_USD[f["currency"]] for f in uniq]
        areas = [i["area"] for i in uniq if i["area"]]
        split = "; ".join(f"{len(v)} flats priced in {c} (median {statistics.median(v):,.0f})" for c, v in sorted(by.items()))
        for p in places:
            code = p if isinstance(p, str) else city_code(*p)
            out.append({
                "place_code": code, "amount": f"{statistics.median(rents):.0f}", "currency": "USD", "unit": "per_month", "period": "2026",
                "measured_for": f"{measured}; median advertised rent of 2-bedroom flats on archived Encuentra24 result pages"
                                + ("" if code.startswith("CITY-") else " (the capital's sample stands for the whole area)"),
                "source_id": "encuentra24-archive",
                "note": (f"VERY THIN: {len(uniq)} distinct flats on {pages} archived result page(s) (snapshot months {', '.join(sorted(set(stamps)))}), quartiles {_q(rents, .25):,.0f} to {_q(rents, .75):,.0f}; "
                         f"{len(areas)} of them state an area (median {statistics.median(areas) if areas else 'n/a'} m2); the first ads on a page are paid highlights, so the sample leans expensive"
                         + f". Ads are in several currencies, converted to US dollars at the 17 Nov 2026 rate ({FX_NOTE}); by currency: {split}"),
            })
    return out


def rows() -> list[dict]:
    return _build()


if __name__ == "__main__":
    w = csv.DictWriter(sys.stdout, ["place_code", "amount", "currency", "unit", "period", "measured_for", "source_id", "note"])
    w.writeheader()
    w.writerows(rows())
