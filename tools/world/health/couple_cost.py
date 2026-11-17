# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Monthly cost of private health cover for a couple, both 45, by country, from each insurer's published table.

Written by AI on 2026.11.17 by model claude sonnet 5.5, for the world-data owner.

Run after ipmi_tables.py:  uv run tools/world/health/couple_cost.py
Writes health-cover.couple-45.csv (one row per country x insurer reference plan) and
health-cover.candidate.csv (the same figures in the data/tables column contract, in each insurer's own currency),
health-cover.compare.csv (one row per country, USD per month at the day's ECB rates, with medians).

Reference plans (see health-cover.notes.md for why): comprehensive in- and outpatient, worldwide excluding the USA,
no maternity or dental, deductible nearest US$1,000.
"""

import csv
import pathlib
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[2]
FX_CACHE = REPO / "cache" / "ecb-fx-probe"

SUBTERRITORY = {"Alderney", "Herm", "Sark", "Canary Islands", "Madeira", "Azores"}
PERIOD = {"axa-globalreach": "2025-09", "generali-intl-exclusive": "2025-02", "globality-yougenio": "2025-01", "img-gmi": "2026-02", "care-expat-world": "2026"}
AGE = 45
RETRIEVED = "2026-11-17"


def read(name: str) -> list[dict]:
    with open(HERE / name, newline="") as f:
        return list(csv.DictReader(f))


def countries() -> dict[str, str]:
    out = {}
    for line in open(REPO / "cache" / "geonames" / "countryInfo.txt", encoding="utf-8"):
        if line.startswith("#") or not line.strip():
            continue
        p = line.rstrip("\n").split("\t")
        out[p[0]] = p[4].strip()
    return out


def zones(name: str) -> dict[str, int]:
    out = {}
    for r in read(name):
        if r["insurer_country_name"] == "Netherlands Antilles" or r["iso2"] == "AN":
            for iso in ("CW", "SX", "BQ"):  # the dissolved territory's successors take its zone
                out[iso] = int(r["zone"])
            continue
        if r["insurer_country_name"] in SUBTERRITORY or not r["iso2"]:
            continue
        out[r["iso2"]] = int(r["zone"])
    return out


def ecb(cur: str) -> float:
    """Units of `cur` per euro, latest ECB reference rate (cache/ecb-fx-probe, fetched if missing)."""
    path = FX_CACHE / f"{cur}.csv"
    if not path.exists():
        FX_CACHE.mkdir(parents=True, exist_ok=True)
        url = f"https://data-api.ecb.europa.eu/service/data/EXR/D.{cur}.EUR.SP00.A?lastNObservations=1&format=csvdata"
        path.write_bytes(urllib.request.urlopen(urllib.request.Request(url, headers={"Accept": "text/csv"})).read())
    row = list(csv.DictReader(open(path)))[0]
    return float(row["OBS_VALUE"])


def main() -> None:
    names = countries()
    usd_per_eur, myr_per_eur = ecb("USD"), ecb("MYR")
    usd_per_myr = usd_per_eur / myr_per_eur

    axa = {(r["zone"], r["benefit_level"], r["area_of_cover"], r["annual_deductible_usd"], r["age_last_birthday"]): r for r in read("axa-globalreach.rates.csv")}
    gen = {(r["zone"], r["plan"], r["area_of_cover"], r["age_last_birthday"]): r for r in read("generali-intl-exclusive.rates.csv")}
    glo = {(r["zone"], r["plan"], r["outpatient_deductible_eur"], r["age_band"]): r for r in read("globality-yougenio.rates.csv")}
    img = {(r["plan"], r["area_of_cover"], r["annual_deductible_usd"], r["age_band"]): r for r in read("img-gmi.rates.csv")}
    care = {(r["area_zone"], r["plan"], r["annual_deductible_eur"], r["age_band"]): r for r in read("care-expat-world.rates.csv")}
    zx, zg, zl = zones("axa-globalreach.zones.csv"), zones("generali-intl-exclusive.zones.csv"), zones("globality-yougenio.zones.csv")

    out, cand = [], []
    fieldnames = ["iso2", "country", "insurer", "plan_level", "area_of_cover", "deductible", "insurer_zone", "currency", "couple_monthly", "couple_monthly_usd_ecb_rate"]

    def add(iso, insurer, plan, area, ded, zone, cur, couple_monthly, to_usd, source_id, note, reference=True):
        out.append(
            {
                "iso2": iso,
                "country": names[iso],
                "insurer": insurer,
                "plan_level": plan,
                "area_of_cover": area,
                "deductible": ded,
                "insurer_zone": zone,
                "currency": cur,
                "couple_monthly": round(couple_monthly),
                "couple_monthly_usd_ecb_rate": round(couple_monthly * to_usd),
            }
        )
        if reference:
            cand.append([iso, round(couple_monthly), cur, "per_month", PERIOD[source_id], f"{names[iso]}, national; couple both aged {AGE}, insurer's zone {zone}", source_id, note])

    for iso in sorted(names):
        z = zx.get(iso)
        if z:
            for ded, tag in (("0", "nil"), ("3125", "usd3125")):
                r = axa.get((str(z), "Comprehensive", "Worldwide excl. USA", ded, str(AGE)))
                add(iso, "AXA GlobalReach", "Comprehensive", "Worldwide excl. USA", "nil" if ded == "0" else "USD 3,125", z, "USD", 2 * float(r["annual_premium_usd"]) / 12, 1.0, "axa-globalreach",
                    "AXA HK GlobalReach, Comprehensive level, worldwide excl. USA; premium table effective 2025-09-09 for policies issued in Hong Kong; couple = 2 x age-45 rate / 12",
                    reference=(ded == "0"))
        z = zg.get(iso)
        if z:
            area = "Worldwide" if z == 1 else "Worldwide excl. USA"  # zone 1 is the USA: the table offers only worldwide cover there
            r = gen.get((str(z), "2", area, str(AGE)))
            if r:
                add(iso, "Generali InternationalExclusive", "Plan 2", area, "none", z, "MYR", 2 * float(r["annual_premium_myr"]) / 12, usd_per_myr, "generali-intl-exclusive",
                    "Generali Malaysia InternationalExclusive Plan 2, worldwide excl. USA; premium table Feb 2025; expatriates only; couple = 2 x age-45 rate / 12")
        z = zl.get(iso)
        if z:
            r = glo.get((str(z), "Plus", "1000", "45-49"))
            add(iso, "Globality YouGenio World", "Plus", "not stated in table", "EUR 1,000 (outpatient and dental only)", z, "EUR", 2 * float(r["monthly_premium_eur"]), usd_per_eur, "globality-yougenio",
                "Globality YouGenio World Plus, EUR 1,000 outpatient deductible; table 01/2025 (product replaced by Journey in 2026); couple = 2 x age-band 45-49 monthly rate")
        # flat (no country dependence): one row per country so the table is complete
        us_like = zg.get(iso) == 1 or zl.get(iso) == 1
        r = img[("Gold", "Worldwide excl. USA, Canada, China, Hong Kong, Japan, Macau, Singapore, Taiwan", "1000", "45 to 49")]
        if not us_like:
          add(iso, "IMG Global Medical Insurance", "Gold", "Worldwide excl. USA, Canada, China, Hong Kong, Japan, Macau, Singapore, Taiwan", "USD 1,000", "none", "USD", 2 * float(r["annual_premium_usd"]) / 12, 1.0, "img-gmi",
              "IMG GMI rates do not vary by country of residence; new business from 2026-02-01; eligibility depends on country and nationality; couple = 2 x age-band 45-49 rate / 12")
        cz, carea = ("3", "Worldwide incl. China, Singapore, USA") if us_like else ("1", "Worldwide excl. China, Singapore, USA")
        r = care[(cz, "Basic", "1200", "45 - 49")]
        add(iso, "Care Expat World (Barmenia)", "Basic", carea, "EUR 1,200", f"{cz} (area of cover)", "EUR", 2 * float(r["monthly_premium_eur"]), usd_per_eur, "care-expat-world",
            "Care Expat World prices by area of cover, not by country of residence; brochure 2026; couple = 2 x age-band 45-49 monthly rate")

    import statistics
    cols = [("axa_nil", "AXA GlobalReach", "nil"), ("axa_usd3125", "AXA GlobalReach", "USD 3,125"), ("generali_plan2", "Generali InternationalExclusive", None),
            ("globality_plus", "Globality YouGenio World", None), ("img_gold", "IMG Global Medical Insurance", None), ("care_basic", "Care Expat World (Barmenia)", None)]
    wide = []
    for iso in sorted(names):
        row = {"iso2": iso, "country": names[iso]}
        for key, ins, ded in cols:
            hit = [r["couple_monthly_usd_ecb_rate"] for r in out if r["iso2"] == iso and r["insurer"] == ins and (ded is None or r["deductible"] == ded)]
            row[key] = hit[0] if hit else ""
        zoned = [row[k] for k in ("axa_nil", "generali_plan2", "globality_plus") if row[k] != ""]
        allfour = zoned + ([row["img_gold"]] if row["img_gold"] != "" else [])
        row["median_zoned"] = round(statistics.median(zoned)) if len(zoned) >= 2 else ""
        row["n_zoned"] = len(zoned)
        row["median_with_img"] = round(statistics.median(allfour)) if allfour else ""
        wide.append(row)
    with open(HERE / "health-cover.compare.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["iso2", "country", *[k for k, _, _ in cols], "n_zoned", "median_zoned", "median_with_img"])
        w.writeheader()
        w.writerows(wide)
    print(f"health-cover.compare.csv: {len(wide)} places (couple, USD per month at ECB rates)")
    with open(HERE / "health-cover.couple-45.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(out)
    with open(HERE / "health-cover.candidate.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["place_code", "amount", "currency", "unit", "period", "measured_for", "source_id", "note"])
        w.writerows(cand)
    print(f"health-cover.couple-45.csv: {len(out)} rows; ECB rates {RETRIEVED}: USD per EUR {usd_per_eur}, MYR per EUR {myr_per_eur}")


if __name__ == "__main__":
    main()
