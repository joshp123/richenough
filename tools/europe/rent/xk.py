"""Kosovo: Eurostat's estate-agent survey of two-bedroom rents in Pristina, 2025, plus four districts by listing ratio.

The Kosovo Agency of Statistics and the Central Bank publish no rents. Pristina: the Eurostat survey. Other districts:
asking rents of flats advertised "me qira" on merrjep.com (public pages, JSON-LD price). Within the same filter
(flats of 45 to 110 m2 or unstated size, not 1+1 or 3+1, not daily or weekly lets, priced 100 to 1500
EUR) we take each town's median and divide by the median of the site's Kosovo-wide rental feed (mostly Pristina and
Fushe Kosove), then multiply the Pristina survey figure by that ratio. A town needs at least 10 distinct priced
listings, else it is left to the inferred estimate (Gjilan and Mitrovice fall short).
"""

import re
import statistics
import time
import unicodedata

import common as c
from . import eurostat_capitals as e

PORTAL_ID = "merrjep-xk-rent"
BASE = "https://www.merrjep.com/shpallje/patundshmeri/"
MIN_LISTINGS = 10
# district (NUTS 3) -> (town, search slug, fragment of the town's name in a title)
TOWNS = {"XK004": ("Prizren", "prizren", "prizren"), "XK003": ("Peje", "peje", "pej"),
         "XK005": ("Ferizaj", "ferizaj", "ferizaj"), "XK007": ("Gjakove", "gjakove", "gjakov"),
         "XK006": ("Gjilan", "gjilan", "gjilan"), "XK002": ("Mitrovice", "mitrovice", "mitrovic")}
BAD = (r"ditore|javore|pushim|diaspor|lokal|zyre|zyra|depo|truall|toke|shtepi|vile|dhome|dhoma me|cimer|garsonjer|"
       r"1\+1|1 \+ 1|3\+1|4\+1|shitje|shitet|shiten|1 dhom|3 dhom|4 dhom|hapesir|biznes|objekt|magazin")
ITEM = re.compile(r'"Product","name":"([^"]*)".*?"price":([\d.]+)')

SOURCES = e.SOURCES + [c.source(
    PORTAL_ID, "MerrJep (merrjep.com)", "Banesa me qira, Kosovo: public result pages",
    BASE + "banesa/me-qira", "free to read, no licence stated", "2026-11",
    "Asking rents of rental flats; medians computed by us, used only as ratios to the Pristina survey figure.")]


def _fold(text: str) -> str:
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()


def _prices(url_stem: str, pages: int, name: str, town_fragment: str | None) -> list[float]:
    seen = {}
    for page in range(1, pages + 1):
        url = BASE + url_stem + (f"?Page={page}" if page > 1 else "")
        html = c.fetch(PORTAL_ID, url, f"{name}-{page}.html").read_text(errors="replace")
        for title, price in ITEM.findall(html):
            f = _fold(title)
            if not re.search(r"q[ei]ra|qera", f) or not re.search(r"banes|apartament", f) or re.search(BAD, f):
                continue
            if town_fragment and town_fragment not in f:
                continue
            m = re.search(r"(\d+(?:[.,]\d+)?)\s*m", f)
            if m and not 45 <= float(m.group(1).replace(",", ".")) <= 110:
                continue
            if 100 <= float(price) <= 1500:
                seen[(f, float(price))] = float(price)
        time.sleep(0.3)
    return list(seen.values())


def rows():
    rent, published, size = e.two_bed_75("XK_CAP")
    out = [c.row(c.place("XK001"), rent, "EUR", "per_month", e.PERIOD, c.city_code("XK", "Pristina", "Prishtinë") or "XK",
                 e.SOURCE_ID, f"Pristina, Eurostat estate-agent survey 2025: two-bedroom unfurnished good-quality flat, "
                 f"EUR {published:.0f} for its typical {size:.0f} m2, scaled to 75 m2, excluding charges.")]
    base = _prices("banesa/me-qira", 8, "kosovo-feed", None)
    base_median = statistics.median(base)
    for code, (town, slug, fragment) in TOWNS.items():
        found = _prices(f"q-me-qira-{slug}", 5, slug, fragment)
        if len(found) < MIN_LISTINGS:
            continue
        median = statistics.median(found)
        out.append(c.row(
            c.place(code), rent * median / base_median, "EUR", "per_month", "2026-11",
            c.city_code("XK", town) or c.place(code), PORTAL_ID,
            f"{town}: Pristina survey figure ({rent:.0f} EUR) x {median:.0f}/{base_median:.0f}, the ratio of median asking rents "
            f"of {len(found)} flats advertised in {town} to {len(base)} in Kosovo's whole rental feed on merrjep.com. "
            "Indicative: small asking-rent sample, mixed quality."))
    return out
