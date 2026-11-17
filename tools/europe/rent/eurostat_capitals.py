"""Eurostat's survey of market rents in European capitals (prc_colc_rents), shared by the Balkan rent modules.

Estate agents in each capital are asked for the current monthly rent of an unfurnished flat of good or very good
quality, excluding charges and utilities (the 2025 round was collected around mid-2025 and published in 2026).
FLAT2 is the two-bedroom flat; prc_colc_surf gives its typical size in each city.
"""

import common as c

SOURCE_ID = "eurostat-colc-rents"
PERIOD = "2025"
URL = "https://ec.europa.eu/eurostat/databrowser/view/prc_colc_rents/default/table?lang=en"

SOURCES = [c.source(
    SOURCE_ID, "Eurostat", "Average rent per month in cities by type of dwelling (prc_colc_rents), 2025", URL,
    "CC BY 4.0 (Eurostat reuse policy)", PERIOD,
    "Estate-agent survey of current market rents for unfurnished good-quality flats, excluding charges; FLAT2 = "
    "two-bedroom flat. Candidate and non-EU capitals are included.")]


def two_bed(geo: str) -> tuple[float, float]:
    """(monthly rent in EUR, typical size in m2) of the two-bedroom flat in the capital `geo`, e.g. 'AL_CAP'."""
    rents = c.eurostat("prc_colc_rents", "", startPeriod=PERIOD)
    rent = rents[(rents["building"] == "FLAT2") & (rents["currency"] == "EUR") & (rents["geo"] == geo)
                 & (rents["TIME_PERIOD"] == PERIOD)]["OBS_VALUE"].iloc[0]
    sizes = c.eurostat("prc_colc_surf", "", startPeriod=PERIOD)
    size = sizes[(sizes["building"] == "FLAT2") & (sizes["geo"] == geo) & (sizes["TIME_PERIOD"] == PERIOD)]["OBS_VALUE"].iloc[0]
    return float(rent), float(size)


def two_bed_75(geo: str) -> tuple[float, float, float]:
    """(rent scaled to a 75 m2 flat, rent as published, typical size in m2), so capitals match every other country."""
    rent, size = two_bed(geo)
    return rent * c.TWO_BED_M2 / size, rent, size
