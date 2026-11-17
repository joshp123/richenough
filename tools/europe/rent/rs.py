"""Serbia: median asking rent per m2 of flats advertised on 4zida.rs, in each district's main city.

Serbia publishes no official rent statistics (the Republic Geodetic Authority reports sales only). 4zida.rs, a large
listings portal, marks up every listing with schema.org data (price, floor size, rooms). For each main city we read a
spread of result pages (evenly spaced across all of the city's listings, so the sample is not only the newest ads),
keep flats of 40 to 120 m2, and take the median EUR per m2 x 75 m2. Cities with fewer than 15 usable listings get the
median of the cities that do have a figure, outside Belgrade, labelled as Serbia-wide (measured_for RS).
"""

import re
import statistics
import time

import common as c

SOURCE_ID = "4zida-rs"
BASE = "https://www.4zida.rs/izdavanje-stanova/"
PERIOD = "2026-11"
MIN_LISTINGS = 15
MAX_PAGES = 8

# district (NUTS 3) -> (main city, 4zida slug). Eurostat's LAU list for Serbia is settlements without population,
# so main_towns cannot rank them; these are the district seats.
SEATS = {
    "RS110": ("Belgrade", "beograd"), "RS121": ("Sombor", "sombor"), "RS122": ("Pančevo", "pancevo"),
    "RS123": ("Novi Sad", "novi-sad"), "RS124": ("Kikinda", "kikinda"), "RS125": ("Subotica", "subotica"),
    "RS126": ("Zrenjanin", "zrenjanin"), "RS127": ("Sremska Mitrovica", "sremska-mitrovica"),
    "RS211": ("Užice", "uzice"), "RS212": ("Valjevo", "valjevo"), "RS213": ("Šabac", "sabac"),
    "RS214": ("Čačak", "cacak"), "RS215": ("Jagodina", "jagodina"), "RS216": ("Kruševac", "krusevac"),
    "RS217": ("Kraljevo", "kraljevo"), "RS218": ("Kragujevac", "kragujevac"), "RS221": ("Bor", "bor"),
    "RS222": ("Požarevac", "pozarevac"), "RS223": ("Zaječar", "zajecar"), "RS224": ("Leskovac", "leskovac"),
    "RS225": ("Niš", "nis"), "RS226": ("Pirot", "pirot"), "RS227": ("Smederevo", "smederevo"),
    "RS228": ("Vranje", "vranje"), "RS229": ("Prokuplje", "prokuplje"),
}
GEONAMES_NAMES = {"Belgrade": "Belgrade", "Pančevo": "Pancevo", "Užice": "Uzice"}

LISTING = re.compile(
    r'"url":"https://www\.4zida\.rs/izdavanje-stanova/([^"/]*)/[^"]*","businessFunction":"[^"]*","price":(\d+),'
    r'"priceCurrency":"EUR"\},"itemOffered":\{"@type":"Apartment","@id":"[^"]*","floorSize":\{"@type":"QuantitativeValue",'
    r'"value":(\d+),"unitCode":"MTK"\}')

SOURCES = [c.source(
    SOURCE_ID, "4zida.rs", "Rental listings of flats (izdavanje stanova), schema.org markup on result pages",
    "https://www.4zida.rs/izdavanje-stanova/beograd", "free to read, no licence stated", PERIOD,
    "Asking rents (EUR per month) and floor sizes of advertised flats; we compute medians ourselves from a spread of "
    "result pages per city. Asking, not agreed, rents; sample of up to about 150 listings per city.")]


def _page(slug: str, page: int) -> str:
    url = BASE + slug + (f"?strana={page}" if page > 1 else "")
    path = c.fetch(SOURCE_ID, url, f"{slug}-{page}.html")
    return path.read_text()


def _city(slug: str) -> tuple[float, int] | None:
    first = _page(slug, 1)
    count = max([int(n.replace(".", "")) for n in re.findall(r"(\d[\d.]*)\+? (?:aktuelnih )?oglas", first)] or [0])
    pages = max(1, -(-count // 20))
    wanted = sorted({round(1 + i * (pages - 1) / (MAX_PAGES - 1)) for i in range(MAX_PAGES)}) if pages > 1 else [1]
    seen, per_m2 = set(), []
    for page in wanted:
        html = first if page == 1 else _page(slug, page)
        for location, price, area in LISTING.findall(html):
            key = (location, price, area)
            if key in seen or not location.endswith(slug):
                continue
            seen.add(key)
            if 40 <= int(area) <= 120:
                per_m2.append(int(price) / int(area))
        time.sleep(0.5)
    if len(per_m2) < MIN_LISTINGS:
        return None
    return statistics.median(per_m2), len(per_m2)


def rows():
    figures = {}
    for code in c.regions_in("RS"):
        city, slug = SEATS[code]
        figures[code] = _city(slug)
    local = {k: v[0] for k, v in figures.items() if v}
    elsewhere = statistics.median([v for k, v in local.items() if k != "RS110"])
    out = []
    for code in c.regions_in("RS"):
        city, slug = SEATS[code]
        if figures[code]:
            per_m2, n = figures[code]
            city_id = c.city_code("RS", GEONAMES_NAMES.get(city, city))
            out.append(c.row(
                c.place(code), per_m2 * c.TWO_BED_M2, "EUR", "per_month", PERIOD, city_id or c.place(code), SOURCE_ID,
                f"Median asking rent of {n} advertised flats of 40 to 120 m2 in {city} on 4zida.rs, {per_m2:.2f} EUR/m2 "
                "x 75 m2. Asking rents from a spread of result pages, not an official statistic."))
        else:
            out.append(c.row(
                c.place(code), elsewhere * c.TWO_BED_M2, "EUR", "per_month", PERIOD, "RS", SOURCE_ID,
                f"Too few 4zida.rs listings in {city} (under {MIN_LISTINGS}). Median {elsewhere:.2f} EUR/m2 x 75 m2 of "
                f"the {len(local) - 1} Serbian district seats outside Belgrade that have a figure; not a measurement "
                "of this district."))
    return out
