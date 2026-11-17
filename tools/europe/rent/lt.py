"""Lithuania: asking rents per m2 for Vilnius, Kaunas and Klaipeda (Aruodas.lt, Q2 2025), Siauliai (Domoplius, Nov 2026).

No official source: Statistics Lithuania and the Centre of Registers publish sale transactions and price indices only,
and the Bank of Lithuania quotes Aruodas. Aruodas.lt (the largest portal) puts its rent statistics behind a login and
blocks automated reads, so the only citable figures are the ones reported by the press from its Q2 2025 data
(LRT, 20 Jul 2025): average asking rent per m2 of all flats, Vilnius 14.8, Kaunas 12.1, Klaipeda 11.0 EUR. They are
brought to Dec 2025 with Eurostat's HICP actual rentals for Lithuania (monthly index, Q2 2025 average to Dec 2025) and
priced at 75 m2.

Domoplius (second portal, also blocks scripts) gave Siauliai 11 monthly lets of 45 to 100 m2 on 17 Nov 2026 and
Panevezys 7. They were read by hand through a web reader (Domoplius refuses scripts), so they are embedded below
rather than fetched; they are too few to carry much weight. Siauliai is used as a local figure. Panevezys and the
other counties (Alytus, Marijampole, Taurage, Telsiai, Utena) have no usable ads, so they get the median of the 18
small-city ads (Siauliai and Panevezys), labelled national (LT).
"""

import statistics

import common as c

AR_ID = "aruodas-lt-lrt"
DOM_ID = "domoplius-lt-nuoma"

# Aruodas.lt average asking rent, EUR per m2, Q2 2025, as reported by LRT (2025-07-20)
ARUODAS_Q2_2025 = {"LT011": ("Vilnius", 14.8), "LT022": ("Kaunas", 12.1), "LT023": ("Klaipėda", 11.0)}

# Domoplius monthly lets read on 2026-11-17 from https://domoplius.lt/skelbimai/butai/nuoma/<city>: (EUR per month, m2).
# Daily and short lets, ads without area and ads under 100 EUR are left out here; only 45 to 100 m2 flats are kept.
SIAULIAI = [(625, 60), (450, 50), (500, 49.86), (370, 45), (570, 92), (800, 68.06), (450, 65), (950, 80.46),
            (500, 64), (480, 56), (450, 48.95)]
PANEVEZYS = [(250, 50.91), (400, 45.27), (270, 49), (500, 69.96), (250, 50), (320, 50), (550, 64)]

SOURCES = [
    c.source(AR_ID, "LRT.lt, citing Aruodas.lt",
             "Kambarys pas močiutę? Ne šiandien: studentai būsto nuomai tampa išrankesni (average asking rent per m2, Q2 2025)",
             "https://www.lrt.lt/naujienos/verslas/4/2606774/kambarys-pas-mociute-ne-siandien-studentai-busto-nuomai-tampa-isrankesni",
             "Free to read, no licence stated (news article quoting Aruodas.lt)", "2025-Q2",
             "Average asking rents of flats offered for rent, EUR per m2: Vilnius 14.8, Kaunas 12.1, Klaipėda 11.0.",
             retrieved="2026-11-17"),
    c.source(DOM_ID, "Domoplius.lt", "Flats for rent in Šiauliai and Panevėžys (listing pages read by hand)",
             "https://domoplius.lt/skelbimai/butai/nuoma", "Free to read, no licence stated (portal listings)",
             "2026-11", "18 monthly lets of 45 to 100 m2 in two cities; very thin.", retrieved="2026-11-17")]

COUNTIES_WITHOUT_DATA = ["LT021", "LT024", "LT027", "LT028", "LT029"]  # Alytus, Marijampole, Taurage, Telsiai, Utena


def _median_rate(ads):
    return statistics.median(price / area for price, area in ads)


def rows():
    # Q2 2025 average to Dec 2025 (latest month Eurostat has), HICP actual rentals, Lithuania
    index = c.eurostat("prc_hicp_midx", "M.I15.CP041.LT", startPeriod="2025-01")
    values = dict(zip(index["TIME_PERIOD"], index["OBS_VALUE"]))
    last = max(values)
    q2 = statistics.mean(values[m] for m in ("2025-04", "2025-05", "2025-06"))
    factor = values[last] / q2

    out = []
    for nuts3, (name, rate) in ARUODAS_Q2_2025.items():
        out.append(c.row(
            c.place(nuts3), round(rate * factor * c.TWO_BED_M2), "EUR", "per_month", last, c.city_code("LT", name) or c.place(nuts3),
            AR_ID, f"Aruodas.lt average asking rent in {name} Q2 2025, {rate} EUR/m2 (all flat sizes), x{factor:.3f} "
                   f"(HICP actual rentals, LT, Q2 2025 to {last}), x 75 m2."))
    siauliai = _median_rate(SIAULIAI)
    out.append(c.row(
        c.place("LT026"), round(siauliai * c.TWO_BED_M2), "EUR", "per_month", "2026-11", c.city_code("LT", "Šiauliai"), DOM_ID,
        f"Domoplius median asking rent in Šiauliai, {siauliai:.2f} EUR/m2 over {len(SIAULIAI)} monthly lets of 45 to 100 m2 "
        f"(very thin), x 75 m2."))
    pool = _median_rate(SIAULIAI + PANEVEZYS)
    for nuts3 in ["LT025"] + COUNTIES_WITHOUT_DATA:
        out.append(c.row(
            c.place(nuts3), round(pool * c.TWO_BED_M2), "EUR", "per_month", "2026-11", "LT", DOM_ID,
            f"No usable local ads. National stand-in, not local: median {pool:.2f} EUR/m2 of {len(SIAULIAI) + len(PANEVEZYS)} "
            f"Domoplius lets in Šiauliai and Panevėžys (very thin), x 75 m2."))
    return out
