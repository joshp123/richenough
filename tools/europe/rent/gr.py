"""Greece: xe.gr's published average asking rent per m2 by area, Q3 2026 (partial: 9 of 52 regions).

Greece has no open rent statistics below the national level that we could reach. Bank of Greece publishes only a
national rent index (and its site blocks us); ELSTAT and the tax authority (AADE) publish no rents by area;
Spitogatos' price index (the best local source) sits behind bot protection (HTTP 405 for curl and WebFetch).
xe.gr (Chrysi Efkairia, the largest listings portal) publishes, on https://www.xe.gr/property/times-akiniton, the
average asking rent per m2 by size band for 50 areas: Athens and 44 other Attica municipalities, Thessaloniki,
Kalamaria, Patras and Heraklion (Crete). We use the band up to 80 m2 (a 75 m2 flat falls in it) times 75 m2.

Regions with no area on that page get no row: nothing below the national level exists for them.
"""

import html
import re

import common as c

SOURCE_ID = "gr-xe-rents"
URL = "https://www.xe.gr/property/times-akiniton"
PERIOD = "2026-Q3"

SOURCES = [c.source(
    SOURCE_ID, "xe.gr (Chrysi Efkairia)",
    "Prices of properties per area and market trends: average rent per m2 by area and size, Q3 2026",
    URL, "Free to read; no licence stated", PERIOD,
    "Average asking rent per m2 of residential rental listings on xe.gr by area and size band, Q3 2026 against Q3 2025. "
    "Asking, not agreed; includes studios in the up-to-80 m2 band.")]

# NUTS 3 region -> (area as spelled on xe.gr, English name for the GeoNames lookup). The area is the region's
# largest municipality (common.main_towns rule); regions whose main town is not on the page get no row.
AREAS = {
    "EL301": ("Χαλάνδρι", "Chalandri"),         # North Athens
    "EL302": ("Περιστέρι", "Peristeri"),        # West Athens
    "EL303": ("Αθήνα", "Athens"),               # Central Athens
    "EL304": ("Καλλιθέα", "Kallithea"),         # South Athens
    "EL305": ("Αχαρνές", "Acharnes"),           # East Attica
    "EL307": ("Πειραιάς", "Piraeus"),           # Piraeus and islands
    "EL431": ("Ηράκλειο, Κρήτη", "Heraklion"),  # Heraklion
    "EL522": ("Θεσσαλονίκη", "Thessaloniki"),
    "EL632": ("Πάτρα", "Patras"),               # Achaia
}


def _table() -> dict[str, tuple[float, int]]:
    page = c.fetch(SOURCE_ID, URL, "times-akiniton.html").read_text(errors="ignore")
    text = html.unescape(re.sub(r"\s+", " ", re.sub(r"<script.*?</script>|<style.*?</style>|<[^>]+>", " ", page, flags=re.S)))
    rent = text.split("Τιμές ακινήτων προς ενοικίαση")[1].split("Δες όλες τις περιοχές για ενοικιάσεις")[0]
    if "Γ Τρίμηνο 2026" not in rent:
        raise ValueError("xe.gr table is no longer for Q3 2026; update PERIOD")
    out = {}
    pattern = re.compile(r"([^\d()€%]+?) Έως 80 τ\.μ\. ([\d.]+) ([\d.]+) \([^)]*\) ([\d,]+) € ([\d,]+) €")
    for m in pattern.finditer(rent):
        area = re.sub(r"^.*?Τρίμηνο 2026 ", "", m.group(1)).strip()
        out[area] = (float(m.group(5).replace(",", ".")), int(m.group(3).replace(".", "")))
    return out


def rows():
    table = _table()
    out = []
    for nuts3, (area, english) in AREAS.items():
        per_m2, listings = table[area]
        out.append(c.row(
            c.place(nuts3), round(per_m2 * c.TWO_BED_M2), "EUR", "per_month", PERIOD, c.city_code("GR", english), SOURCE_ID,
            f"xe.gr average asking rent for flats up to 80 m2 in {area.split(',')[0]}, Q3 2026: {per_m2:.2f} EUR/m2 x "
            f"75 m2 ({listings} listings). Asking rents, studios included."))
    return out
