"""Ukraine (the oblasts the site prices as Ukraine): LUN's median asking rent of two-room flats in oblast centres.

LUN (lun.ua) publishes a monthly median asking rent for 1-, 2- and 3-room flats in each oblast centre it covers
(statistics page /misto/stat/rent/<city>). No official statistic exists. Each raion containing an oblast centre gets that
city's figure; every other raion gets its oblast centre's figure, marked as measured for the oblast. Kyiv oblast's
raions get Kyiv city's figure (Kyiv is its administrative centre but its own region).
A Ukrainian "two-room" flat (living room plus one bedroom, about 50 to 60 m2) is the nearest listed size to a
two-bed; it runs below 70 to 85 m2, so the figure leans low. The 3-room median is in the note where LUN publishes it.
"""

import html
import re

import common as c

SOURCE_ID = "lun-rent-ua"
MONTHS = {"січень": 1, "лютий": 2, "березень": 3, "квітень": 4, "травень": 5, "червень": 6, "липень": 7, "серпень": 8,
          "вересень": 9, "жовтень": 10, "листопад": 11, "грудень": 12}

# raion (NUTS 3) containing the oblast centre -> (LUN slug, GeoNames English name)
CENTRES = {
    "UA630": ("kyiv", "Kyiv"), "UA733": ("lviv", "Lviv"), "UA136": ("kharkiv", "Kharkiv"), "UA425": ("odesa", "Odesa"),
    "UA311": ("dnipro", "Dnipro"), "UA511": ("vinnytsia", "Vinnytsia"), "UA114": ("poltava", "Poltava"),
    "UA145": ("chernihiv", "Chernihiv"), "UA124": ("sumy", "Sumy"), "UA814": ("lutsk", "Lutsk"),
    "UA833": ("rivne", "Rivne"), "UA522": ("ternopil", "Ternopil"), "UA722": ("ivano-frankivsk", "Ivano-Frankivsk"),
    "UA715": ("uzhhorod", "Uzhhorod"), "UA743": ("chernivtsi", "Chernivtsi"), "UA532": ("khmelnytskyi", "Khmelnytskyi"),
    "UA822": ("zhytomyr", "Zhytomyr"), "UA624": ("cherkasy", "Cherkasy"), "UA332": ("kropyvnytskyi", "Kropyvnytskyi"),
    "UA413": ("mykolaiv", "Mykolaiv"),
}
# LUN's September 2026 Uzhhorod median (45,800 UAH for two rooms) is more than twice Kyiv's and above Lviv's; a thin
# market, so Zakarpattia gets the median of the other oblast centres outside Kyiv, measured for Ukraine.
UNRELIABLE = {"UA715"}
# NUTS 2 (oblast) -> NUTS 3 raion holding its centre; Kyiv oblast uses Kyiv city
OBLAST_CENTRE = {code[:4]: code for code in CENTRES if code != "UA630"}
OBLAST_CENTRE["UA61"] = "UA630"

SOURCES = [c.source(
    SOURCE_ID, "LUN (lun.ua)", "Statistics of apartment rent prices by city (Statystyka cin orendy kvartyr), monthly",
    "https://lun.ua/misto/stat/rent/kyiv", "free to read, no licence stated", "2026-08 to 2026-10",
    "Median asking rent (UAH per month) of 1-, 2- and 3-room flats in oblast centres, from listings LUN aggregates. "
    "Oblast centres only; Uzhhorod is September 2026 and Chernivtsi August 2026, the rest October 2026.")]


def _page(slug: str) -> tuple[dict[str, int], str]:
    text = c.fetch(SOURCE_ID, f"https://lun.ua/misto/stat/rent/{slug}", f"{slug}.html").read_text()
    text = re.sub(r"<script.*?</script>|<style.*?</style>", "", text, flags=re.S)
    lines = [x.strip() for x in html.unescape(re.sub(r"<[^>]+>", "\n", text)).split("\n") if x.strip()]
    title = lines[0]
    month, year = re.search(r"за (\w+) (\d{4})", title).groups()
    sizes = {}
    for i, line in enumerate(lines):
        m = re.fullmatch(r"(\d)-кімнатні", line)
        if m and lines[i + 1] == "₴":
            sizes[m.group(1)] = int(re.sub(r"\D", "", lines[i + 2]))
    return sizes, f"{year}-{MONTHS[month]:02d}"


def rows():
    figures = {}
    for code, (slug, city) in CENTRES.items():
        sizes, period = _page(slug)
        figures[code] = (sizes, period, c.city_code("UA", city), city)
    others = sorted(f[0]["2"] for k, f in figures.items() if k not in UNRELIABLE and k != "UA630")
    national = others[len(others) // 2] if len(others) % 2 else (others[len(others) // 2 - 1] + others[len(others) // 2]) / 2
    out = []
    for code in c.regions_in("UA"):
        centre = code if code in CENTRES else OBLAST_CENTRE.get(code[:4])
        if centre is None:
            continue
        if centre in UNRELIABLE:
            bad = figures[centre]
            out.append(c.row(c.place(code), national, "UAH", "per_month", "2026-10", "UA", SOURCE_ID,
                             f"Median of LUN's 2-room medians in the {len(others)} oblast centres outside Kyiv. LUN's own "
                             f"{bad[3]} figure ({bad[0]['2']:,} UAH, {bad[1]}) is more than twice Kyiv's, so it is not used."))
            continue
        sizes, period, city_id, city = figures[centre]
        three = f" 3-room median {sizes['3']:,} UAH." if "3" in sizes else ""
        if code == centre:
            measured, text = city_id, f"LUN median asking rent of 2-room flats in {city}, {period}.{three}"
        elif code[:4] == "UA61":
            measured = city_id
            text = (f"Kyiv oblast has no figure of its own; LUN's median asking rent of 2-room flats in Kyiv city, "
                    f"{period}.{three} Commuter-belt towns near Kyiv are the likeliest to be close to it.")
        else:
            measured = c.place(code[:4])
            text = (f"No figure for this raion. LUN's median asking rent of 2-room flats in the oblast centre {city}, "
                    f"{period}, stands for the oblast; towns outside the centre are likely cheaper.{three}")
        out.append(c.row(c.place(code), sizes["2"], "UAH", "per_month", period, measured, SOURCE_ID, text))
    return out
