"""Denmark: asking rents of flats listed to rent on EDC Lejeindeks (which carries BoligPortal's and EDC's adverts), Nov 2026.

Statistics Denmark publishes only rent indices (HUS1, LABY32), no levels. Landsbyggefonden's rent statistics cover
social housing only (a waiting-list stock). So for the going rate of a new let we take the live listings of the region's main
municipality: median rent per m2 of flats of 50 to 110 m2, times 75 m2.
"""

import re
import statistics
import time

import common as c

SOURCE_ID = "edc-dk-lejebolig"
BASE = "https://www.edc.dk/lejebolig/"
PERIOD = "2026-11"
MIN_LISTINGS = 8

# NUTS 3 -> (municipality slug on edc.dk, town name for the note, GeoNames lookup names, neighbouring municipalities
# pooled in order only when the main municipality lists fewer than MIN_LISTINGS flats of the right size).
# Rule: the region's most populous municipality, except Copenhagen's omegn (Gentofte, the largest) and Vest- og Sydsjælland
# where common.main_towns picks Sorø, a small regional seat, over Næstved, which has almost three times its population.
TOWNS = {
    "DK011": ("koebenhavn", "København", ["København"], []),
    "DK012": ("gentofte", "Gentofte", ["Gentofte", "Hellerup"], []),
    "DK013": ("hilleroed", "Hillerød", ["Hillerød"], []),
    "DK014": ("bornholm", "Bornholm (Rønne)", ["Rønne"], []),
    "DK021": ("roskilde", "Roskilde", ["Roskilde"], ["koege", "greve"]),
    "DK022": ("naestved", "Næstved", ["Næstved"], []),
    "DK031": ("odense", "Odense", ["Odense"], []),
    "DK032": ("vejle", "Vejle", ["Vejle"], []),
    "DK041": ("viborg", "Viborg", ["Viborg"], []),
    "DK042": ("aarhus", "Aarhus", ["Aarhus", "Århus"], []),
    "DK050": ("aalborg", "Aalborg", ["Aalborg"], []),
}

SOURCES = [c.source(
    SOURCE_ID, "EDC (listings of BoligPortal and EDC)",
    "EDC Lejeindeks: homes for rent by municipality (live adverts, asking rents)",
    BASE, "Free to read, no licence stated; robots.txt allows crawling", PERIOD,
    "Asking rents of live adverts, scraped Nov 2026. Statistics Denmark (HUS1, LABY32) has rent indices only, no levels; "
    "Landsbyggefonden's huslejestatistik covers social housing only.")]

CARD = re.compile(r'>(Lejlighed|Villa|Rækkehus|Værelse|[A-ZÆØÅ][a-zæøå]+) fra .*?<h2[^>]*>([^<]*)</h2>.*?(\d+) rum, (\d+) m².*?([\d.]+) kr\./md', re.S)


def _listings(slug: str) -> dict[tuple, tuple[str, int, int]]:
    """Every advert of a municipality, deduplicated: (address, rooms, m2, rent) -> (type, m2, rent). Pages are ?side=N."""
    found, page, last = {}, 1, 1
    while page <= last:
        path = c.fetch(SOURCE_ID, f"{BASE}{slug}/" + (f"?side={page}" if page > 1 else ""), f"{slug}-{page}.html")
        html = path.read_text(encoding="utf-8", errors="ignore")
        last = max([last] + [int(n) for n in re.findall(r"\?side=(\d+)", html)])
        for article in html.split("<article")[1:]:
            m = CARD.search(article)
            if m:
                found[(m.group(2), m.group(3), m.group(4), m.group(5))] = (m.group(1), int(m.group(4)), int(m.group(5).replace(".", "")))
        page += 1
        time.sleep(0.3)
    return found


def rows():
    out = []
    for nuts3 in c.regions_in("DK"):
        slug, town, names, neighbours = TOWNS[nuts3]
        flats, used = [], []
        for municipality in [slug, *neighbours]:
            flats += [(m2, rent) for kind, m2, rent in _listings(municipality).values() if kind == "Lejlighed" and 50 <= m2 <= 110]
            used.append(municipality)
            if len(flats) >= MIN_LISTINGS:
                break
        if len(flats) < MIN_LISTINGS:
            raise ValueError(f"{town}: only {len(flats)} flats listed")
        where = f"{town} municipality" + (f" plus {', '.join(used[1:])}" if len(used) > 1 else "")
        per_m2 = statistics.median(rent / m2 for m2, rent in flats)
        measured = c.city_code("DK", *names) or c.place(nuts3)
        out.append(c.row(
            c.place(nuts3), round(per_m2 * c.TWO_BED_M2), "DKK", "per_month", PERIOD, measured, SOURCE_ID,
            f"Median asking rent of {len(flats)} listed flats of 50-110 m2 in {where}, {per_m2:.0f} DKK/m2/month x 75 m2. "
            f"Asking rents of live adverts, not agreed rents."))
    return out
