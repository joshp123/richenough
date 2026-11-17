"""Health cover for the couple (two 45-year-olds, non-working, new residents from outside the EU/EEA/Switzerland).

The coordinator's rule (18 Nov 2026), the same for every place on the site: the mid-range local private plan a
well-off couple who have just moved there would buy (in-patient and out-patient, moderate deductible, not worldwide
expat cover), plus any statutory premium or fixed contribution a resident must pay. One monthly figure for both, in
local currency. Income-based charges are not in it; they are listed in each country's file for the tax code.

Switzerland is computed from the Federal Office of Public Health's open premium data, by canton. Every other country
is read from health/<cc>.json (written from the country's own official sources; see health/README in the notes at
.agent/research/europe/health.md). A JSON file may carry `regional` figures at NUTS 2 or 3 level.
"""

import json
from pathlib import Path

import pandas as pd

import common as c

HERE = Path(__file__).resolve().parent / "health"

CH_ID = "bag-priminfo"
CH_PREMIUMS = "https://opendata.bagnet.ch/?r=/download&path=L1ByYWVtaWVuL0FyY2hpdl9QcmFlbWllbl8yMDI2LnppcA%3D%3D"
CH_CANTONS = {
    "VD": "CH011", "VS": "CH012", "GE": "CH013", "BE": "CH021", "FR": "CH022", "SO": "CH023", "NE": "CH024",
    "JU": "CH025", "BS": "CH031", "BL": "CH032", "AG": "CH033", "ZH": "CH040", "GL": "CH051", "SH": "CH052",
    "AR": "CH053", "AI": "CH054", "SG": "CH055", "GR": "CH056", "TG": "CH057", "LU": "CH061", "UR": "CH062",
    "SZ": "CH063", "OW": "CH064", "NW": "CH065", "ZG": "CH066", "TI": "CH070",
}


def _country_files() -> list[dict]:
    return [json.loads(p.read_text()) for p in sorted(HERE.glob("*.json"))]


def _sources() -> list[dict]:
    out = {}
    for d in _country_files():
        for s in d.get("sources", []):
            out[s["source_id"]] = c.source(
                s["source_id"], s["publisher"], s["title"], s["url"], s["licence"], str(s.get("period", d["period"])),
                s.get("measures", ""), retrieved=s.get("retrieved"))
    return list(out.values())


# Where a country's file has no priced private plan, the cheapest mainstream international policy stands in: Care Expat World (Barmenia) Basic, EUR 1,200 deductible,
# age band 45-49, EUR 170 a month each (tools/world/health/care-expat-world.rates.csv, area 1). It is dearer than
# local products where we could compare (Spain: 238 against 340), so it is an upper bound for the country.
FALLBACK_ID = "health-eu-care-expat"
FALLBACK_COUNTRIES = ["UA"]  # the only country where no local private plan was priced
FALLBACK_EUR = 2 * 170.0


SOURCES = [c.source(
    CH_ID, "Federal Office of Public Health (FOPH/BAG), Switzerland",
    "Health insurance premiums (Priminfo open data), compulsory basic insurance, premium year 2026",
    "https://opendata.swiss/en/dataset/health-insurance-premiums", "Open data of the Swiss federal administration "
    "(terms of use: opendata.swiss; free reuse, source to be named)", "2026",
    "Approved premium of every insurer by canton and premium region, adults 26+, by model and deductible; "
    "plus the insured population by insurer and canton."),
    c.source(FALLBACK_ID, "Care Concept AG (insurer: Barmenia Krankenversicherung AG)",
             "Care Expat World brochure with premium tables (Basic, EUR 1,200 deductible, age 45 to 49)",
             "https://www.care-concept.de/krankenversicherung/care_expat_world/Internationale_Krankenversicherung_Care_Expat_World_Broschuere_eng.pdf?navilang=eng",
             "No licence stated; public document free to read", "2026",
             "International private medical insurance priced by area of cover, not by country of residence. Used only "
             "where a country's own tariff could not be reached.", retrieved="2026-11-17")] + _sources()


def _swiss_rows() -> list[dict]:
    import zipfile
    zpath = c.fetch(CH_ID, CH_PREMIUMS, "archiv2026.zip")
    folder = zpath.parent / "a2026"
    if not (folder / "Versichertenbestand_CH.csv").exists():
        with zipfile.ZipFile(zpath) as z:
            for name in z.namelist():
                if name.endswith((".csv",)):
                    (folder).mkdir(exist_ok=True)
                    (folder / Path(name).name).write_bytes(z.read(name))
    prem_file = next(folder.glob("Pr*mien_CH.csv"))
    d = pd.read_csv(prem_file, encoding="utf-8-sig")
    q = d[d["Altersklasse"].str.contains("ERW") & d["Unfalleinschluss"].str.startswith("MIT")
          & d["Tariftyp"].str.contains("BASE") & (d["Franchise"] == "FRA-300") & d["Kanton"].isin(CH_CANTONS)]
    ins = pd.read_csv(folder / "Versichertenbestand_CH.csv", sep=";", encoding="utf-8-sig", dtype={"Versicherer": str})
    ins["Versicherer"] = ins["Versicherer"].astype(int)
    ins = ins.rename(columns={"Durchschnittsbestand": "w"})[["Versicherer", "Kanton", "w"]]
    # one premium per insurer, canton and premium region; the canton's figure is the unweighted mean of its regions'
    # insured-weighted medians (the premium-region populations are not in the open data).
    q = q.groupby(["Versicherer", "Kanton", "Region"], as_index=False)["Prämie"].first().merge(ins, on=["Versicherer", "Kanton"], how="left")
    q["w"] = q["w"].fillna(0)
    out = []
    for canton, nuts in CH_CANTONS.items():
        regions = []
        for _, g in q[q["Kanton"] == canton].groupby("Region"):
            g = g.sort_values("Prämie")
            cum = g["w"].cumsum() / g["w"].sum()
            regions.append(float(g.loc[cum >= 0.5, "Prämie"].iloc[0]))
        adult = sum(regions) / len(regions)
        out.append(c.row(
            c.place(nuts), round(2 * adult, 2), "CHF", "per_month", "2026", c.place(nuts), CH_ID,
            f"Compulsory basic insurance (LAMal/KVG), standard model with free choice of doctor, CHF 300 deductible, "
            f"accident cover included, two adults. Insurer-weighted median adult premium CHF {adult:.2f} a month "
            f"(mean of {len(regions)} premium region(s): {', '.join(f'{r:.0f}' for r in regions)}) x 2. Residents without "
            f"work must join within 3 months. Cheaper models or higher deductibles lower it."))
    return out


def _fx() -> dict[str, float]:
    """Units of each currency per euro, from the world table's units per US dollar."""
    import csv
    with (c.TABLES / "exchange-rates.world.csv").open() as f:
        per_usd = {r["currency"]: float(r["amount"]) for r in csv.DictReader(f)}
    return {cur: v / per_usd["EUR"] for cur, v in per_usd.items()}


def _in(amount: float, currency: str, target: str, fx: dict) -> float:
    return amount if currency == target else amount / fx[currency] * fx[target]


def _private(d: dict, fx: dict) -> tuple[float, str, str] | None:
    """(monthly amount for two in the file's currency, description, source_id) of the mid-range private plan."""
    p = d.get("private_plan") or {}
    if p.get("amount") is None:
        return None
    amount = _in(float(p["amount"]), p["currency"], d["currency"], fx)
    what = (f"private plan {p.get('insurer', '')}, {p.get('product', '')} ({p.get('kind', '')}): "
            f"{p['amount']:,.2f} {p['currency']} for two. {p.get('pricing', '')}")
    return amount, what, p.get("source_id") or d["sources"][0]["source_id"]


def _statutory(d: dict, fx: dict) -> tuple[float, str]:
    """(monthly amount for two in the file's currency, description) of the statutory part.

    A premium or fixed contribution residents must pay counts. Where the private plan only supplements the public
    system and the couple's way into it is a voluntary scheme with a fixed contribution (Italy, Poland, Estonia,
    Romania, Albania), that contribution counts too: without it the plan would leave them with no hospital cover.
    """
    s = d.get("statutory_must_pay") or {}
    if s.get("amount"):
        return _in(float(s["amount"]), s.get("currency") or d["currency"], d["currency"], fx), f"compulsory: {s.get('what', '')}"
    p = d.get("private_plan") or {}
    if p.get("kind") == "supplementary" and d.get("kind") == "statutory-fixed" and d.get("amount"):
        return float(d["amount"]), (f"voluntary statutory base the supplementary plan relies on: {d.get('policy', '')[:300]} "
                                    f"{float(d['amount']):,.2f} {d['currency']} for two")
    return 0.0, f"no compulsory premium: {s.get('what', 'none')}"


def rows() -> list[dict]:
    fx = _fx()
    files = {d["country"]: d for d in _country_files()}
    out = []
    swiss_private = _private(files["CH"], fx) if "CH" in files else None
    for r in _swiss_rows():
        if swiss_private:
            r["note"] = (f"Compulsory basic insurance {r['amount']:,.2f} CHF + {swiss_private[1]} "
                         f"Basic: {r['note']}")
            r["amount"] = round(r["amount"] + swiss_private[0], 2)
        out.append(r)
    regions = c.nuts3()
    for iso, d in files.items():
        if iso == "CH":
            continue
        mine = regions[regions["iso"] == iso]
        if mine.empty:
            continue
        private = _private(d, fx)
        if iso == "LI":
            statutory = (float(d["amount"]), f"compulsory basic insurance (OKP) with accident cover: {d.get('working', '')}")
        else:
            statutory = _statutory(d, fx)
        if private is None:
            if iso not in FALLBACK_COUNTRIES:
                continue
            amount = statutory[0] + _in(FALLBACK_EUR, "EUR", d["currency"], fx)
            note = (f"Stand-in, no local private tariff found: an international policy for Europe (Care Expat World "
                    f"Basic, EUR 170 each at 45 to 49), an upper bound for a local plan. Statutory: {statutory[1]}")
            source_id = FALLBACK_ID
        else:
            amount = statutory[0] + private[0]
            note = (f"Statutory {statutory[0]:,.2f} {d['currency']} ({statutory[1]}) + {private[1]}")
            source_id = private[2]
        for nuts in mine["nuts"]:
            out.append(c.row(c.place(nuts), round(amount, 2), d["currency"], "per_month", d["period"], iso, source_id,
                             f"National figure for two 45-year-olds who have just moved there. {note}"))
    return out
