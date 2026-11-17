"""Albania: Eurostat's estate-agent survey of two-bedroom rents in Tirana, 2025, plus Durres and Vlore by the
portal's median ratio.

INSTAT and the Bank of Albania publish no rent series (the Bank's real-estate survey covers sale prices). Tirana: the
Eurostat survey. Durres and Vlore: duashpi.al, Albania's largest property portal, reported through Balkanweb (29 Jan
2026) median asking rents of about 600 EUR in Tirana and about 400 EUR in Durres and Vlore for all apartments in
2025; we apply that 400/600 ratio to the Tirana survey figure. The portal's own site blocks plain fetches, so the
article that quotes it is the source. Other regions are left to the inferred estimate.
"""

import common as c
from . import eurostat_capitals as e

PORTAL_ID = "duashpi-al-balkanweb-2026"
PORTAL_URL = ("https://www.balkanweb.com/tregu-i-banesave-ne-shqiperi-analize-bazuar-ne-te-dhenat-e-duashpi-al-portali-"
              "me-i-madh-ne-shqiperi-dedikuar-pronave/")
TIRANA_MEDIAN, COAST_MEDIAN = 600.0, 400.0

SOURCES = e.SOURCES + [c.source(
    PORTAL_ID, "Balkanweb, quoting duashpi.al", "Tregu i banesave ne Shqiperi: analize bazuar ne te dhenat e Duashpi.al",
    PORTAL_URL, "free to read, no licence stated", "2025",
    "News article quoting the portal's 2025 median asking rents: Tirana about 600 EUR/month, Durres and Vlore about "
    "400 EUR (all apartments; seasonal tourist lets distort the coast). Used only as a ratio.")]


def rows():
    c.fetch(PORTAL_ID, PORTAL_URL, "balkanweb-duashpi.html")
    rent, published, size = e.two_bed_75("AL_CAP")
    out = [c.row(c.place("AL022"), rent, "EUR", "per_month", e.PERIOD, c.city_code("AL", "Tirana", "Tiranë") or "AL022",
                 e.SOURCE_ID, f"Tirana, Eurostat estate-agent survey 2025: two-bedroom unfurnished good-quality flat, "
                 f"EUR {published:.0f} for its typical {size:.0f} m2, scaled to 75 m2, excluding charges (published in ALL 90,300).")]
    ratio = COAST_MEDIAN / TIRANA_MEDIAN
    for code, town, names in (("AL012", "Durres", ("Durrës", "Durres")), ("AL035", "Vlore", ("Vlorë", "Vlore"))):
        out.append(c.row(
            c.place(code), rent * ratio, "EUR", "per_month", e.PERIOD, c.city_code("AL", *names) or c.place(code),
            PORTAL_ID, f"{town}: Tirana's survey figure ({rent:.0f} EUR) x {ratio:.2f}, the ratio of duashpi.al's 2025 median "
            "asking rents (about 400 EUR in Durres and Vlore, about 600 EUR in Tirana). Indicative: the coast's median mixes "
            "long lets with seasonal ones."))
    return out
