"""North Macedonia: Eurostat's estate-agent survey of two-bedroom rents in Skopje, 2025.

The statistics office publishes no rents. pazar3.mk (listings) agrees for Skopje (median 480 EUR on 27 priced
three-room, i.e. two-bedroom, asking rents) but has too few priced two-bedroom listings elsewhere to publish; the
other seven regions are left to the inferred estimate.
"""

import common as c
from . import eurostat_capitals as e

SOURCES = e.SOURCES


def rows():
    rent, published, size = e.two_bed_75("MK_CAP")
    return [c.row(c.place("MK008"), rent, "EUR", "per_month", e.PERIOD, c.city_code("MK", "Skopje", "Скопје") or "MK008",
                  e.SOURCE_ID, f"Skopje, Eurostat estate-agent survey 2025: two-bedroom unfurnished good-quality flat, "
                  f"EUR {published:.0f} for its typical {size:.0f} m2, scaled to 75 m2, excluding charges (published in MKD 28,900).")]
