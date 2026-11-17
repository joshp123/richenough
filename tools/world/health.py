"""Health cover for the couple (both 45, new residents, living off investments), per month, every country.

What the figure is, in order of precedence (each row's note says which):
1. Local evidence (tools/world/health/local.curated.csv): the statutory scheme a new resident must or can join, at
   its fixed charge (the part that depends on income is left to the tax rules and stated in the note), or a
   mid-range local private plan from a published premium table, where that is what such a couple would rely on.
2. Otherwise a regional international health insurance plan with a deductible, the kind a well-off couple buys when
   no local option applies: the median of three insurers' published premiums for two people aged 45 in the
   country's zone, Asia-only cover for residents of East, South-East and South Asia and worldwide-excluding-USA cover
   elsewhere: AXA GlobalReach Comprehensive with a USD 3,125 deductible, Generali InternationalExclusive Plan 2,
   Globality YouGenio World Classic with a EUR 1,000 outpatient deductible. Rate tables and zone lists come from
   tools/world/health/ipmi_tables.py (notes in health/health-cover.notes.md).
Amounts in local currency for local evidence, US dollars for international plans (their pricing currency).
"""

import statistics

from exchange_rates import rates
from lib import NUTS_COUNTRIES, PLAN_COUNTRY, REPO, countries, read_csv

HEALTH = REPO / "tools" / "world" / "health"
ASIA = set("CN HK MO TW JP KR MN KP TH MY SG ID PH VN KH LA MM BN TL IN PK BD LK NP BT MV".split())
PERIOD = {"axa-globalreach": "2025-09", "generali-intl-exclusive": "2025-02", "globality-yougenio": "2025-01"}


def usd_per(fx: dict, currency: str) -> float:
    if currency == "USD":
        return 1.0
    monthly = fx[currency]["monthly"]
    return 1 / monthly[max(monthly)]


def regional_plans(fx: dict) -> dict[str, dict[str, tuple[float, str]]]:
    """ISO2 -> {source_id: (USD per month for the couple, description)}."""
    zones = {name: {r["iso2"]: r["zone"] for r in read_csv(HEALTH / f"{name}.zones.csv")}
             for name in ("axa-globalreach", "generali-intl-exclusive", "globality-yougenio")}
    axa = {(r["zone"], r["area_of_cover"]): float(r["annual_premium_usd"]) for r in read_csv(HEALTH / "axa-globalreach.rates.csv")
           if r["benefit_level"] == "Comprehensive" and r["annual_deductible_usd"] == "3125" and r["age_last_birthday"] == "45" and not r["note"]}
    generali = {(r["zone"], r["area_of_cover"]): float(r["annual_premium_myr"]) for r in read_csv(HEALTH / "generali-intl-exclusive.rates.csv")
                if r["plan"] == "2" and r["age_last_birthday"] == "45"}
    globality = {r["zone"]: float(r["monthly_premium_eur"]) for r in read_csv(HEALTH / "globality-yougenio.rates.csv")
                 if r["plan"] == "Classic" and r["outpatient_deductible_eur"] == "1000" and r["age_band"] == "45-49"}
    out: dict[str, dict] = {}
    for iso2 in countries():
        area = "Asia" if iso2 in ASIA else "Worldwide excl. USA"
        got = {}
        z = zones["axa-globalreach"].get(iso2)
        if z and (z, area) in axa:
            got["axa-globalreach"] = (axa[(z, area)] * 2 / 12, f"AXA Comprehensive, {area}, USD 3,125 deductible, zone {z}")
        z = zones["generali-intl-exclusive"].get(iso2)
        if z and (z, area) in generali:
            got["generali-intl-exclusive"] = (generali[(z, area)] * 2 / 12 * usd_per(fx, "MYR"), f"Generali Plan 2, {area}, zone {z}")
        z = zones["globality-yougenio"].get(iso2)
        if z and z in globality:
            got["globality-yougenio"] = (globality[z] * 2 * usd_per(fx, "EUR"), f"Globality Classic, EUR 1,000 outpatient deductible, zone {z}")
        if got:
            out[iso2] = got
    return out


def build() -> list[dict]:
    fx = rates()
    plans = regional_plans(fx)
    local_path = HEALTH / "local.curated.csv"
    local = {r["place_code"]: r for r in read_csv(local_path)} if local_path.exists() else {}
    rows = []
    for iso2, c in sorted(countries().items()):
        if iso2 in ("US", "PS", "AQ") or not c["population"]:
            continue
        code = PLAN_COUNTRY.get(iso2, iso2)
        name = "Israel and Palestine (Israel's insurer zones)" if code == "PS" else c["name"]
        suffix = ". National row for checking against the Europe agent's figure" if iso2 in NUTS_COUNTRIES else ""
        if code in local:
            r = local[code]
            rows.append({k: r[k] for k in ("place_code", "amount", "currency", "unit", "period", "measured_for", "source_id")}
                        | {"note": r["note"] + suffix})
            continue
        got = plans.get(iso2)
        if not got or len(got) < 2:
            continue
        usd = statistics.median(v for v, _ in got.values())
        chosen = min(got, key=lambda k: abs(got[k][0] - usd))
        parts = "; ".join(f"{d}: USD {v:,.0f}" for v, d in got.values())
        how = "median" if len(got) == 3 else "mean of two (only two insurers list this country)"
        rows.append({"place_code": code, "amount": f"{usd:.0f}", "currency": "USD", "unit": "per_month", "period": PERIOD[chosen],
                     "measured_for": f"{name}: regional international health insurance, couple aged 45",
                     "source_id": chosen,
                     "note": f"kind=international-regional; no local option with published prices found. {how.capitalize()} of the insurers' published premiums for "
                             f"two people aged 45, per month. {parts}{suffix}"})
    return rows


def sources() -> list[dict]:
    keep = set(PERIOD)
    out = [r for r in read_csv(HEALTH / "health-cover.sources.csv") if r["source_id"] in keep or r["source_id"].startswith("health-local-")]
    local = HEALTH / "local.sources.csv"
    return out + (read_csv(local) if local.exists() else [])


if __name__ == "__main__":
    from lib import upsert_sources, write_table

    write_table("health-cover", build())
    upsert_sources(sources())
