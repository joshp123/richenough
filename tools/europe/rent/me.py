"""Montenegro: Eurostat's estate-agent survey of two-bedroom rents in Podgorica, 2025.

Montenegro is one NUTS 3 region. Monstat and the Central Bank publish sale prices only. The capital's survey figure
stands for the country's one region; the coast (Budva, Kotor, Tivat) is dearer in listings but has no survey.
"""

import common as c
from . import eurostat_capitals as e

SOURCES = e.SOURCES


def rows():
    rent, published, size = e.two_bed_75("ME_CAP")
    return [c.row(c.place("ME000"), rent, "EUR", "per_month", e.PERIOD, c.city_code("ME", "Podgorica") or "ME", e.SOURCE_ID,
                  f"Podgorica, Eurostat estate-agent survey 2025: two-bedroom unfurnished good-quality flat, EUR "
                  f"{published:.0f} for its typical {size:.0f} m2, scaled to 75 m2, excluding charges. One region for the whole country; coastal towns not measured.")]
