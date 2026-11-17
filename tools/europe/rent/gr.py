"""Greece: asking rents from xe.gr (Attica) and Spitogatos (the rest), mixed periods, 2-bed level.

Greece has no open rent statistics below the national level that we could reach (Bank of Greece: national index only;
ELSTAT and the tax authority: none by area). Listings-portal sources fill the gap, all asking rents per m2 x 75 m2:

1. xe.gr's market page (Q3 2026), flats up to 80 m2, for the six Attica regions (within about 7 per cent of
   Spitogatos' all-size figure for Athens municipality, Q3 2026: 12.2 against 13.13 EUR/m2).
2. Spitogatos blog, "Northern Greece Q1 2026": average asking rent per m2 of all flat sizes for 12 northern cities
   (Thessaloniki municipality, Kavala, Serres, Alexandroupoli, ...). Used as published.
3. Spitogatos Insights, Q2 2026 (via Thestival), student-city asking rent per m2 in 31 cities. Small flats dominate
   (it equals xe.gr's up-to-80 m2 band in Patras and Heraklion), so it is scaled to all-size level by the median ratio
   of source 2 to source 3 in the nine cities in both (computed in ratio()).
4. Spitogatos regional-unit averages (all flat sizes; Q2/Q3 2026) for Cyclades, Lefkada, Pella, used as published.

Regions with none of these get no row.
"""

import html
import re
import statistics

import common as c

SOURCE_ID = "gr-xe-rents"
URL = "https://www.xe.gr/property/times-akiniton"
XE_PERIOD = "2026-Q3"

NORTH_ID = "gr-spitogatos-north"
NORTH_URL = "https://www.spitogatos.gr/blog/agora-enoikiasi-katoikias-voreia-ellada-q1-2026-mzt-2022-2026"
STUDENT_ID = "gr-spitogatos-students"
STUDENT_AUG_URL = "https://www.vradini.gr/oikonomia/spitogatos-anodika-kinoyntai-oi-meses-zitoymenes-times-mzt-enoikiasis-foititikon-katoikion-to-2026/1709163/"
STUDENT_URL = "https://www.thestival.gr/eidiseis/koinonia/spitogatos-insights-i-eikona-ton-zitoymenon-timon-enoi/"
UNITS_ID = "gr-spitogatos-units"
UNITS_Q2_URL = "https://www.spitogatos.gr/blog/pwliseis-enoikiaseis-katoikion-ellada-2o-trimino-2026"
UNITS_Q3_URL = "https://www.mononews.gr/oikonomia/spitogatos-me-ipiotero-rythmo-i-afxisi-ton-timon-katoikion-to-g-trimino-tou-2026"

SOURCES = [
    c.source(SOURCE_ID, "xe.gr (Chrysi Efkairia)",
             "Prices of properties per area and market trends: average rent per m2 by area and size, Q3 2026", URL,
             "Free to read; no licence stated", XE_PERIOD,
             "Average asking rent per m2 of residential rental listings on xe.gr by area and size band. Asking, not "
             "agreed; includes studios in the up-to-80 m2 band."),
    c.source(NORTH_ID, "Spitogatos (blog)",
             "Housing market in Northern Greece, Q1 2026: asking sale and rent prices 2022-2026", NORTH_URL,
             "Free to read; no licence stated", "2026-Q1",
             "Average asking rent per m2 (all flat sizes) on Spitogatos by regional unit and city in Macedonia and Thrace."),
    c.source(STUDENT_ID, "Spitogatos Insights, as reported by Thestival (25 Jul 2026)",
             "Asking rents of student housing in Greece's student cities, Q2 2026 (Kozani: Aug 2026, Vradini)", STUDENT_URL + " ; " + STUDENT_AUG_URL,
             "Free to read; no licence stated", "2026-Q2",
             "Average asking rent per m2 of student flats in 31 cities. Dwelling size not stated; level matches xe.gr's "
             "up-to-80 m2 band in Patras and Heraklion, so small flats dominate."),
    c.source(UNITS_ID, "Spitogatos blog (Q2 2026) and Mononews report of Spitogatos Q3 2026",
             "Rent per m2 by regional unit: highest and lowest areas, Q2 and Q3 2026", UNITS_Q2_URL + " ; " + UNITS_Q3_URL,
             "Free to read; no licence stated", "2026-Q2/Q3",
             "Average asking rent per m2 (all flat sizes) of regional units named in the highest and lowest lists."),
]

# --- Attica: xe.gr, flats up to 80 m2 (NUTS 3 -> (area as spelled on xe.gr, English name for GeoNames)) -------------
AREAS = {
    "EL301": ("Χαλάνδρι", "Chalandri"),   # North Athens
    "EL302": ("Περιστέρι", "Peristeri"),  # West Athens
    "EL303": ("Αθήνα", "Athens"),         # Central Athens
    "EL304": ("Καλλιθέα", "Kallithea"),   # South Athens
    "EL305": ("Αχαρνές", "Acharnes"),     # East Attica
    "EL307": ("Πειραιάς", "Piraeus"),     # Piraeus and islands
}

# --- Spitogatos "Northern Greece" blog, Q1 2026, all-size asking EUR/m2 by city (NUTS 3 -> (city, EUR/m2)) --------
NORTH = {
    "EL511": ("Alexandroupoli", 9.0), "EL512": ("Xanthi", 7.3), "EL513": ("Komotini", 7.6), "EL514": ("Drama", 5.8),
    "EL515": ("Kavala", 7.3), "EL521": ("Veria", 5.0), "EL522": ("Thessaloniki", 10.4), "EL523": ("Kilkis", 5.4),
    "EL525": ("Katerini", 6.2), "EL526": ("Serres", 6.6), "EL531": ("Kozani", 5.9), "EL532": ("Kastoria", 5.9),
}  # EL522 is the municipality of Thessaloniki

# --- Spitogatos Insights Q2 2026, student-city asking EUR/m2, every city of the list (NUTS 3 -> (city, EUR/m2)) -----
STUDENT = {
    "EL411": ("Mytilini", 8.3), "EL412": ("Samos", 7.3), "EL413": ("Chios", 9.8), "EL421": ("Rhodes", 13.3),
    "EL431": ("Heraklion", 12.0), "EL433": ("Rethymno", 13.2), "EL434": ("Chania", 12.9),
    "EL511": ("Alexandroupoli", 11.3), "EL512": ("Xanthi", 8.8), "EL513": ("Komotini", 8.5), "EL514": ("Drama", 7.2),
    "EL515": ("Kavala", 8.4), "EL525": ("Katerini", 8.3), "EL526": ("Serres", 7.3), "EL531": ("Kozani", 7.3),
    "EL532": ("Kastoria", 7.4), "EL533": ("Florina", 8.9), "EL541": ("Preveza", 9.0), "EL543": ("Ioannina", 10.0),
    "EL611": ("Trikala", 8.5), "EL612": ("Larissa", 10.0), "EL613": ("Volos", 10.0), "EL622": ("Corfu", 13.4),
    "EL631": ("Agrinio", 7.2), "EL632": ("Patras", 10.0), "EL642": ("Chalkida", 10.7), "EL644": ("Lamia", 6.8),
    "EL653": ("Kalamata", 11.2),
}  # Kozani is not in the Q2 list: 7.3 is the August 2026 figure (Vradini)

# --- Spitogatos regional-unit averages, all flat sizes: (name, EUR/m2, period, which article) -------------------
UNITS = {
    "EL422": ("Cyclades", 12.2, "2026-Q3", UNITS_Q3_URL), "EL624": ("Lefkada", 11.8, "2026-Q2", UNITS_Q2_URL),
    "EL524": ("Pella", 4.6, "2026-Q2", UNITS_Q2_URL),
}


def _table() -> dict[str, tuple[float, int]]:
    page = c.fetch(SOURCE_ID, URL, "times-akiniton.html").read_text(errors="ignore")
    text = html.unescape(re.sub(r"\s+", " ", re.sub(r"<script.*?</script>|<style.*?</style>|<[^>]+>", " ", page, flags=re.S)))
    rent = text.split("Τιμές ακινήτων προς ενοικίαση")[1].split("Δες όλες τις περιοχές για ενοικιάσεις")[0]
    if "Γ Τρίμηνο 2026" not in rent:
        raise ValueError("xe.gr table is no longer for Q3 2026; update XE_PERIOD")
    out = {}
    pattern = re.compile(r"([^\d()€%]+?) Έως 80 τ\.μ\. ([\d.]+) ([\d.]+) \([^)]*\) ([\d,]+) € ([\d,]+) €")
    for m in pattern.finditer(rent):
        area = re.sub(r"^.*?Τρίμηνο 2026 ", "", m.group(1)).strip()
        out[area] = (float(m.group(5).replace(",", ".")), int(m.group(3).replace(".", "")))
    return out


def ratio() -> float:
    """Median of (all-size city rent, Spitogatos Q1 2026) / (student-city rent, Q2 2026) over cities in both."""
    return statistics.median(NORTH[n][1] / STUDENT[n][1] for n in NORTH if n in STUDENT)


def rows():
    table = _table()
    k = ratio()
    for source_id, url, name in [(NORTH_ID, NORTH_URL, "north-q1.html"), (STUDENT_ID, STUDENT_URL, "p.html"),
                                 (UNITS_ID, UNITS_Q2_URL, "p.html"), (UNITS_ID, UNITS_Q3_URL, "q3.html")]:
        c.fetch(source_id, url, name)  # the pages the figures were read from, kept in cache/
    out = []
    for nuts3, (area, english) in AREAS.items():
        per_m2, listings = table[area]
        out.append(c.row(
            c.place(nuts3), round(per_m2 * c.TWO_BED_M2), "EUR", "per_month", XE_PERIOD, c.city_code("GR", english), SOURCE_ID,
            f"xe.gr average asking rent for flats up to 80 m2 in {area}, Q3 2026: {per_m2:.2f} EUR/m2 x "
            f"75 m2 ({listings} listings). Asking rents, studios included."))
    for nuts3, (english, per_m2) in NORTH.items():
        out.append(c.row(
            c.place(nuts3), round(per_m2 * c.TWO_BED_M2), "EUR", "per_month", "2026-Q1", c.city_code("GR", english), NORTH_ID,
            f"Spitogatos average asking rent, all flat sizes, {english}{' municipality' if nuts3 == 'EL522' else ''}, "
            f"Q1 2026: {per_m2} EUR/m2 x 75 m2."))
    c.fetch(STUDENT_ID, STUDENT_AUG_URL, "vradini-aug.html")
    for nuts3, (english, per_m2) in STUDENT.items():
        if nuts3 in NORTH:
            continue
        period = "2026-Q2"
        out.append(c.row(
            c.place(nuts3), round(per_m2 * k * c.TWO_BED_M2), "EUR", "per_month", period, c.city_code("GR", english), STUDENT_ID,
            f"Spitogatos average asking rent of student flats in {english}, Q2 2026: {per_m2} EUR/m2 (mostly small flats), "
            f"scaled x{k:.2f} to all-size level (median ratio of all-size to student rent in the nine northern cities "
            f"with both) x 75 m2."))
    for nuts3, (name, per_m2, period, url) in UNITS.items():
        out.append(c.row(
            c.place(nuts3), round(per_m2 * c.TWO_BED_M2), "EUR", "per_month", period, c.place(nuts3), UNITS_ID,
            f"Spitogatos average asking rent, {name} regional unit, {period}: {per_m2} EUR/m2 (all flat sizes) x 75 m2. {url}"))
    return out
