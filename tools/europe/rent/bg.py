"""Bulgaria: asking rents of flats per m2 by town, from alo.bg's published "average rent" page, 17 Nov 2026.

No official source: NSI and the BNB publish sale prices and rent indices only. alo.bg publishes, for every town with
five or more rental listings, the average asking rent per m2 of all rental flats (EUR, Bulgaria uses the euro from
2026). A 75 m2 two-bed is priced at 75 x that rate. Towns with fewer than 10 listings are too thin to trust; they get
the median of the well-covered ordinary regional centres, labelled as national (BG).
"""

import re
import statistics

import common as c

SOURCE_ID = "alo-bg-naemi"
URL = "https://www.alo.bg/sredni_ceni/imoti-naemi/apartamenti/"
MIN_LISTINGS = 10
PERIOD = "2026-11"

SOURCES = [c.source(
    SOURCE_ID, "alo.bg (Bulgarian classifieds portal)",
    "Average rents by town and neighbourhood: rent per m2 and per month by number of rooms, from alo.bg listings "
    "(Средни цени на наемите, apartments)",
    URL, "Free to read, no licence stated (portal's own aggregate of its listings)", PERIOD,
    "Asking rents of current listings, all rental flats in the town, EUR per m2 per month; page dated 17.11.2026.")]


def _table() -> dict[str, tuple[int, float]]:
    html = c.fetch(SOURCE_ID, URL, "alo-bg-sredni-naemi-2026-11-17.html").read_text(errors="ignore")
    text = re.sub(r"<script.*?</script>|<style.*?</style>", "", html, flags=re.S)
    text = re.sub(r"<[^>]+>", "|", text)
    text = re.sub(r"\|[\s|]*\|", "|", text)
    text = re.sub(r"\s+", " ", text)
    table = text[text.find("Намери място"):]
    found = {m.group(1): (int(m.group(2)), float(m.group(3).replace(",", ".")))
             for m in re.finditer(r"\|([^|]+)\|(?:обл\. [^|·]+ · )?(\d+) обяв[аи]\|([\d,]+)\| €/м²", table)}
    if len(found) < 40:
        raise RuntimeError("alo.bg page layout changed")
    return found


def rows():
    table = _table()
    mains = {}
    for nuts3 in c.regions_in("BG"):
        town = c.main_towns(nuts3).iloc[0]
        if town["name"] == "Столична":  # the LAU is the municipality of Sofia
            mains[nuts3] = ("София", "Sofia", c.city_code("BG", "Sofia"))
        else:
            mains[nuts3] = (town["name"], town["name_latin"], town["city_code"])

    # fallback: ordinary regional centres with solid coverage (not Sofia or the three big seaside/Plovdiv cities)
    big = {"София", "Пловдив", "Варна", "Бургас"}
    solid = [table[n][1] for n, _, _ in mains.values() if n not in big and n in table and table[n][0] >= 20]
    fallback = statistics.median(solid)

    out = []
    for nuts3, (name, latin, city) in mains.items():
        count, rate = table.get(name, (0, None))
        if rate is not None and count >= MIN_LISTINGS:
            out.append(c.row(
                c.place(nuts3), round(rate * c.TWO_BED_M2), "EUR", "per_month", PERIOD, city or c.place(nuts3), SOURCE_ID,
                f"alo.bg average asking rent in {latin}, {rate:.1f} EUR/m2 over {count} listings (all flat sizes) x 75 m2."))
        else:
            seen = f"alo.bg shows {rate:.1f} EUR/m2 from {count} listings; too few to use. " if rate else \
                f"alo.bg lists fewer than 5 rental flats for {latin}. "
            out.append(c.row(
                c.place(nuts3), round(fallback * c.TWO_BED_M2), "EUR", "per_month", PERIOD, "BG", SOURCE_ID,
                f"{seen}National stand-in, not local: median {fallback:.1f} EUR/m2 of {len(solid)} ordinary regional "
                f"centres with 20+ listings, x 75 m2."))
    return out
