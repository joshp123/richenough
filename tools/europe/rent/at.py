"""Austria: asking rents of 51 to 80 m2 flats by district (Bezirk), from immopreise.at (derStandard), November 2026.

One figure per NUTS 3 region: the 51-80 m2 asking rent per m2 in the district of the region's main town, times 75 m2.
Rent includes operating costs (Betriebskosten) and VAT, as listings quote it. Where the district has no 51-80 m2 figure
we scale its all-size average by the median ratio of the two; where it has neither we use the median of the state's
other districts and say so. Statistik Austria's Mikrozensus (rents of tenancies under two years, by state) is the
official cross-check, not the source: it is a mean over all lets, social housing included, and only goes down to state.
"""

import re
import statistics

from lxml import html

import common as c

SOURCE_ID = "immopreise-at"
BASE = "https://www.immopreise.at"
MZ_SOURCE_ID = "statistik-at-wohnen"

SOURCES = [c.source(
    SOURCE_ID, "immopreise.at (STANDARD Verlagsgesellschaft, derStandard.at)",
    "Mietpreise Wohnungen: average asking rent per m2 by district and flat size, November 2026",
    f"{BASE}/Wien/Wohnung/Miete", "free to read, no licence stated", "2026-11",
    "Asking rents of listings on immobilien.derstandard.at, incl. operating costs and VAT; each value needs at least four "
    "listings, outliers removed (site's own method note). Page dated 11.11.2026.")]

# NUTS 3 -> (state page, district row as the site names it, main town for the city code)
STATES = {"Burgenland": "AT11", "Niederoesterreich": "AT12", "Wien": "AT13", "Kaernten": "AT21", "Steiermark": "AT22",
          "Oberoesterreich": "AT31", "Salzburg": "AT32", "Tirol": "AT33", "Vorarlberg": "AT34"}
CAPITAL_DISTRICTS = {"Salzburg (Stadt)", "Innsbruck-Stadt", "Klagenfurt (Stadt)", "Graz", "Linz (Stadt)", "Eisenstadt (Stadt)",
                     "Sankt Pölten (Stadt)", "Bregenz"}
# region -> (state, district, main town). Town is c.main_towns' first pick unless noted.
REGIONS = {
    "AT111": ("Burgenland", "Oberpullendorf", "Oberpullendorf"),
    "AT112": ("Burgenland", "Eisenstadt (Stadt)", "Eisenstadt"),
    "AT113": ("Burgenland", "Oberwart", "Oberwart"),
    "AT121": ("Niederoesterreich", "Amstetten", "Amstetten"),
    "AT122": ("Niederoesterreich", "Wiener Neustadt (Stadt)", "Wiener Neustadt"),
    "AT123": ("Niederoesterreich", "Sankt Pölten (Stadt)", "St. Pölten"),
    "AT124": ("Niederoesterreich", "Krems an der Donau", "Krems an der Donau"),
    "AT125": ("Niederoesterreich", "Hollabrunn", "Hollabrunn"),
    "AT126": ("Niederoesterreich", "Tulln", "Klosterneuburg"),  # Klosterneuburg is in Bezirk Tulln since 2017
    "AT127": ("Niederoesterreich", "Baden", "Baden"),  # override: largest town and a district seat (main_towns picks Perchtoldsdorf)
    "AT130": ("Wien", None, "Wien"),
    "AT211": ("Kaernten", "Klagenfurt (Stadt)", "Klagenfurt am Wörthersee"),
    "AT212": ("Kaernten", "Spittal an der Drau", "Spittal an der Drau"),
    "AT213": ("Kaernten", "Wolfsberg", "Wolfsberg"),
    "AT221": ("Steiermark", "Graz", "Graz"),
    "AT222": ("Steiermark", "Liezen", "Liezen"),
    "AT223": ("Steiermark", "Leoben", "Leoben"),
    "AT224": ("Steiermark", "Südoststeiermark", "Feldbach"),
    "AT225": ("Steiermark", "Leibnitz", "Leibnitz"),
    "AT226": ("Steiermark", "Murtal", "Knittelfeld"),
    "AT311": ("Oberoesterreich", "Braunau am Inn", "Braunau am Inn"),
    "AT312": ("Oberoesterreich", "Linz (Stadt)", "Linz"),
    "AT313": ("Oberoesterreich", "Perg", "Perg"),
    "AT314": ("Oberoesterreich", "Steyr (Stadt)", "Steyr"),
    "AT315": ("Oberoesterreich", "Gmunden", "Bad Ischl"),  # Bad Ischl is in Bezirk Gmunden
    "AT321": ("Salzburg", "Tamsweg", "Tamsweg"),
    "AT322": ("Salzburg", "Zell am See", "Saalfelden am Steinernen Meer"),  # Saalfelden is in Bezirk Zell am See
    "AT323": ("Salzburg", "Salzburg (Stadt)", "Salzburg"),
    "AT331": ("Tirol", "Reutte", "Reutte"),
    "AT332": ("Tirol", "Innsbruck-Stadt", "Innsbruck"),
    "AT333": ("Tirol", "Lienz", "Lienz"),
    "AT334": ("Tirol", "Imst", "Imst"),
    "AT335": ("Tirol", "Kufstein", "Kufstein"),
    "AT341": ("Vorarlberg", "Bludenz", "Bludenz"),
    "AT342": ("Vorarlberg", "Bregenz", "Bregenz"),
}


def _num(text: str) -> float | None:
    text = text.strip().replace("\xa0", "")
    return float(text.replace(",", ".")) if re.fullmatch(r"\d+(,\d+)?", text) else None


def _tables() -> dict[str, dict[str, tuple[float | None, float | None]]]:
    """state slug -> district -> (51-80 m2 rent per m2, all-size average per m2)."""
    out = {}
    for slug in STATES:
        path = c.fetch(SOURCE_ID, f"{BASE}/{slug}/Wohnung/Miete", f"{slug}.html")
        doc = html.parse(str(path)).getroot()
        rows = {}
        for table in doc.iter("table"):
            cells = [[re.sub(r"\s+", " ", td.text_content()).strip() for td in tr.xpath("./th|./td")] for tr in table.xpath(".//tr")]
            if cells and cells[0] and cells[0][0].startswith("Bezirk"):
                for r in cells[1:]:
                    rows[r[0]] = (_num(r[2]), _num(r[5]))
        out[slug] = rows
    return out


def rows():
    tables = _tables()
    pairs = [(b, a) for t in tables.values() for b, a in t.values() if b and a and a < 30]
    k = statistics.median(b / a for b, a in pairs)  # 51-80 m2 rent relative to the all-size average
    out = []
    for nuts, (state, district, town) in REGIONS.items():
        table = tables[state]
        city = c.city_code("AT", town)
        period = "2026-11"
        if state == "Wien":
            values = [b for b, _ in table.values() if b]
            rent = statistics.fmean(values)
            how = f"mean of the 51-80 m2 asking rent per m2 in Vienna's {len(values)} districts, unweighted"
            measured = city
        else:
            band, avg = table[district]
            if band:
                rent, how, measured = band, f"asking rent of 51-80 m2 flats in district {district}", city
            elif avg:
                rent, how, measured = avg * k, (f"district {district} has no 51-80 m2 figure; its all-size average {avg:.1f} EUR/m2 "
                                                f"x {k:.2f}, the median ratio of the 51-80 m2 rent to the all-size average over all districts"), city
            else:
                others = [b or (a * k if a else None) for d, (b, a) in table.items() if d != district and d not in CAPITAL_DISTRICTS]
                others = [v for v in others if v]
                rent, measured = statistics.median(others), c.place(STATES[state])
                how = (f"district {district} has no figures; median of the state's other districts (capital excluded, "
                       f"{len(others)} districts, 51-80 m2 rent or all-size average x {k:.2f}), so it is a state figure, not local")
        out.append(c.row(
            c.place(nuts), round(rent * c.TWO_BED_M2, 0), "EUR", "per_month", period, measured, SOURCE_ID,
            f"Asking rent incl. operating costs and VAT, {rent:.1f} EUR/m2 x 75 m2: {how}. Main town: {town}."))
    return out
