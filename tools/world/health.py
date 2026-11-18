"""Health cover for the couple (both 45, just moved there, living off investments), per month, every country.

The coordinator's rule, the same for every agent: the private health insurance a well-off couple of 45-year-olds who
have just moved there would buy, a mid-range local private plan (in-patient and out-patient, moderate deductible, not
top-tier worldwide expat cover), plus any statutory premium or contribution a resident must pay. Where public cover is
free and private is optional, the private plan is still priced, because the lifestyle has private cover.

1. Local private plan: from a published premium table (tools/world/health/local.curated.csv, rows `kind=local-private`).
   Where none is published, it is estimated: the country's regional international plan price (below) times the median
   ratio of local plan to international plan in the countries that have both. International insurers price by zone
   from local medical costs, so the zone carries the local information; the ratio removes the expat premium.
2. Statutory charge: rows `kind=statutory` in local.curated.csv or local-statutory.curated.csv, the fixed part a
   resident must pay; the part that depends on income is in the note, for the tax rules.
Regional international plan: the median of three insurers' published premiums for two people aged 45, Asia-only cover
in East, South-East and South Asia, worldwide excluding the USA elsewhere: AXA GlobalReach Comprehensive with a
USD 3,125 deductible, Generali InternationalExclusive Plan 2, Globality YouGenio World Classic with a EUR 1,000
outpatient deductible (tools/world/health/ipmi_tables.py; notes in health/health-cover.notes.md).
"""

import statistics

from exchange_rates import current_rates
from lib import EUROPE_AGENT, PLAN_COUNTRY, REPO, countries, fmt, read_csv

HEALTH = REPO / "tools" / "world" / "health"
ASIA = set("CN HK MO TW JP KR MN KP TH MY SG ID PH VN KH LA MM BN TL IN PK BD LK NP BT MV".split())
PERIOD = {"axa-globalreach": "2025-09", "generali-intl-exclusive": "2025-02", "globality-yougenio": "2025-01"}
# Published local plans that cover hospital stays only: too narrow for the rule, so they serve as a floor under the estimate.
HOSPITAL_ONLY = {"HK", "SG", "TH", "MY"}
# Statutory charges a new resident must pay (the helper's file also lists voluntary schemes: Mexico's IMSS, Peru's
# EsSalud, Chile's 7% for earners, Dubai's minimum plan, which the private plan already satisfies).
COMPULSORY = {"IR", "JP", "KR", "TW", "CO", "CR", "CA", "NZ", "AU"}
# Which published option is the mid-range plan, where the helper listed several (text found in its note).
CHOSEN = {"HK": "ward-level Flexi"}
# Rows written under a region or city code that stand for the country.
AS_COUNTRY = {"JP-13": "JP", "AU-NSW": "AU", "CITY-292223": "AE"}


def usd_per(fx: dict, currency: str) -> float:
    return 1 / fx[currency]


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
            got["axa-globalreach"] = (axa[(z, area)] * 2 / 12, f"AXA Comprehensive, {area}, USD 3,125 deductible")
        z = zones["generali-intl-exclusive"].get(iso2)
        if z and (z, area) in generali:
            got["generali-intl-exclusive"] = (generali[(z, area)] * 2 / 12 * usd_per(fx, "MYR"), f"Generali Plan 2, {area}")
        z = zones["globality-yougenio"].get(iso2)
        if z and z in globality:
            got["globality-yougenio"] = (globality[z] * 2 * usd_per(fx, "EUR"), "Globality Classic, EUR 1,000 outpatient deductible")
        if len(got) >= 2:
            out[iso2] = got
    return out


def local_rows(kind: str) -> dict[str, dict]:
    """Country -> the chosen row of this kind: the CHOSEN option, else the helper's recommended row, else the first."""
    found: dict[str, list[dict]] = {}
    for name in ("local.curated.csv", "local-statutory.curated.csv"):
        path = HEALTH / name
        if path.exists():
            for r in read_csv(path):
                if r["note"].startswith(f"kind={kind}") and r["amount"]:
                    found.setdefault(AS_COUNTRY.get(r["place_code"], r["place_code"]), []).append(r)
    out = {}
    for code, rs in found.items():
        pick = [r for r in rs if CHOSEN.get(code, "\0") in r["note"]] or [r for r in rs if "recommended row" in r["note"]] or rs
        out[code] = pick[0]
    return out


def build() -> tuple[list[dict], dict]:
    fx = current_rates()
    plans = regional_plans(fx)
    international = {k: statistics.median(v for v, _ in got.values()) for k, got in plans.items()}
    private = local_rows("local-private")
    statutory = {k: r for k, r in local_rows("statutory").items() if k in COMPULSORY}

    def usd(r):
        return float(r["amount"]) * usd_per(fx, r["currency"])

    ratios = {k: usd(r) / international[k] for k, r in private.items() if k in international and k not in HOSPITAL_ONLY}
    ratio = statistics.median(ratios.values()) if ratios else None
    spread = (min(ratios.values()), max(ratios.values())) if ratios else (None, None)

    rows = []
    for iso2, c in sorted(countries().items()):
        if iso2 in ("US", "PS", "AQ") or iso2 in EUROPE_AGENT or not c["population"]:
            continue  # Europe's countries are the Europe agent's; a row here would stand in for theirs on the site
        code = PLAN_COUNTRY.get(iso2, iso2)
        cur = c["currency"]
        if cur not in fx:
            continue
        parts, words, sources, inferred = [], [], [], False
        published = private.get(code)
        estimate = international[iso2] * ratio if iso2 in international and ratio else None
        if published and (code not in HOSPITAL_ONLY or not estimate or usd(published) >= estimate):
            r = published
            parts.append(usd(r))
            words.append(f"local private plan {fmt(float(r['amount']), 4)} {r['currency']} ({r['measured_for']}; {r['note'].split(';', 1)[-1].strip()})")
            sources.append(r["source_id"])
        elif estimate:
            parts.append(estimate)
            got = plans[iso2]
            words.append(f"local private plan with in- and out-patient cover estimated at USD {estimate:,.0f}: the regional international plan, USD {international[iso2]:,.0f} "
                         f"(median of {', '.join(f'{d} USD {v:,.0f}' for v, d in got.values())}), times {ratio:.2f}, the median ratio of "
                         f"published local in- and out-patient plans to it in {len(ratios)} countries ({', '.join(f'{k} {v:.2f}' for k, v in sorted(ratios.items()))})")
            if published:
                words.append(f"the only published local plan covers hospital stays only: {fmt(float(published['amount']), 4)} {published['currency']} a month "
                             f"({published['note'].split(';', 1)[-1].strip()[:160]})")
            sources.append(min(got, key=lambda k: abs(got[k][0] - international[iso2])))
            inferred = True
        else:
            continue
        if code in statutory:
            r = statutory[code]
            parts.append(usd(r))
            words.append(f"plus statutory {fmt(float(r['amount']), 4)} {r['currency']} ({r['note'].split(';', 1)[-1].strip()} Source: {r['source_id']})")
            sources.append(r["source_id"])
        total_local = sum(parts) / usd_per(fx, cur)
        name = "Israel and Palestine (figure for Israel)" if code == "PS" else c["name"]
        rows.append({"place_code": code, "amount": fmt(total_local, 4), "currency": cur, "unit": "per_month", "period": "2026",
                     "measured_for": f"{name}: {'estimated ' if inferred else ''}local private health insurance for a couple aged 45"
                                     + (" plus the statutory charge" if code in statutory else ""),
                     "source_id": sources[0],
                     "note": ("Inferred, not measured: " if inferred else "") + "; ".join(words)})
    return rows, {"ratio": ratio, "ratios": ratios, "spread": spread}


def sources() -> list[dict]:
    keep = set(PERIOD)
    out = [r for r in read_csv(HEALTH / "health-cover.sources.csv") if r["source_id"] in keep or r["source_id"].startswith("health-local-")]
    for name in ("local.sources.csv", "local-statutory.sources.csv"):
        if (HEALTH / name).exists():
            out += read_csv(HEALTH / name)
    return out


if __name__ == "__main__":
    from lib import upsert_sources, write_table

    rows, info = build()
    write_table("health-cover", rows)
    upsert_sources(sources())
    print("local-to-international ratio", info["ratio"], {k: round(v, 2) for k, v in sorted(info["ratios"].items())})
