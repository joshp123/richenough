"""Private health cover for the couple (both 45, new residents, no public cover yet), per month, every country.

Figure: the median of three insurers' published international health insurance (IPMI) premiums for the country's
zone, at age 45, two people, comprehensive inpatient and outpatient cover, worldwide excluding the USA:
AXA GlobalReach Comprehensive (nil deductible), Generali InternationalExclusive Plan 2, Globality YouGenio World Plus
(EUR 1,000 outpatient deductible). Rate tables, zone lists and the per-country couple figures come from
tools/world/health/ipmi_tables.py and couple_cost.py (run those first; notes in health/health-cover.notes.md).
The median is written in US dollars at the exchange-rate table's latest rates; the note gives all three.
"""

import statistics

from exchange_rates import rates
from lib import NUTS_COUNTRIES, PLAN_COUNTRY, REPO, countries, read_csv

HEALTH = REPO / "tools" / "world" / "health"
REFERENCE = {
    "axa-globalreach": ("AXA GlobalReach", "nil"),
    "generali-intl-exclusive": ("Generali InternationalExclusive", "none"),
    "globality-yougenio": ("Globality YouGenio World", None),
}
SHORT = {"axa-globalreach": "AXA", "generali-intl-exclusive": "Generali", "globality-yougenio": "Globality"}
PERIOD = {"axa-globalreach": "2025-09", "generali-intl-exclusive": "2025-02", "globality-yougenio": "2025-01"}


def usd_per_unit(fx: dict, currency: str) -> float:
    if currency == "USD":
        return 1.0
    monthly = fx[currency]["monthly"]
    return 1 / monthly[max(monthly)]


def build() -> list[dict]:
    fx = rates()
    by_country: dict[str, dict[str, tuple[float, float, str, str]]] = {}
    for r in read_csv(HEALTH / "health-cover.couple-45.csv"):
        for source_id, (insurer, deductible) in REFERENCE.items():
            if r["insurer"] != insurer or (deductible and r["deductible"] != deductible):
                continue
            if insurer.startswith("Generali") and r["area_of_cover"] != "Worldwide excl. USA":
                continue
            amount = float(r["couple_monthly"])
            usd = amount * usd_per_unit(fx, r["currency"])
            by_country.setdefault(r["iso2"], {})[source_id] = (usd, amount, r["currency"], r["insurer_zone"])
    rows = []
    for iso2, figures in sorted(by_country.items()):
        if iso2 == "US" or iso2 not in countries() or len(figures) < 2:
            continue
        if iso2 == "PS":
            continue  # the plan's PS is written from Israel's zones below
        code = PLAN_COUNTRY.get(iso2, iso2)
        median_usd = statistics.median(v[0] for v in figures.values())
        chosen = min(figures, key=lambda k: abs(figures[k][0] - median_usd))
        parts = "; ".join(f"{SHORT[k]} zone {v[3]}: {v[1]:,.0f} {v[2]} (USD {v[0]:,.0f})" for k, v in sorted(figures.items()))
        note = (f"{'Median' if len(figures) == 3 else 'Mean'} of {len(figures)} insurers' published premiums for two people aged 45, comprehensive in- and outpatient, "
                f"worldwide excl. USA; per month for the couple. {parts}. Exchange rates: latest month in exchange-rates.world.csv")
        if len(figures) == 2:
            note += ". Thin: only two insurers list this country, so the figure is the mean of the two"
        if iso2 in NUTS_COUNTRIES:
            note += ". National row for checking against the Europe agent's figure"
        name = "Israel and Palestine (Israel's insurer zones)" if code == "PS" else countries()[iso2]["name"]
        rows.append({"place_code": code, "amount": f"{median_usd:.0f}", "currency": "USD", "unit": "per_month",
                     "period": PERIOD[chosen], "measured_for": f"{name}, whole country, insurer zone pricing",
                     "source_id": chosen, "note": note})
    return rows


def sources() -> list[dict]:
    keep = set(REFERENCE) | {"img-gmi", "care-expat-world"}
    return [r for r in read_csv(HEALTH / "health-cover.sources.csv") if r["source_id"] in keep]


if __name__ == "__main__":
    from lib import upsert_sources, write_table

    write_table("health-cover", build())
    upsert_sources(sources())
