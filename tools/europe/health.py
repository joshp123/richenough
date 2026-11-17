"""Health cover for the couple (two 45-year-olds, non-working, new residents from outside the EU/EEA/Switzerland).

One monthly figure for both people, in local currency: the premium of the cover the residence route requires
(private policy, or statutory cover where a fixed charge applies), 0 where statutory cover is free and private cover
is not required. Income-based charges are not in the figure; they are listed in each country's file for the tax code.

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


# Where a country's file has no sourced figure but its residence route requires insurance, the cheapest mainstream
# international policy that carries the cover stands in: Care Expat World (Barmenia) Basic, EUR 1,200 deductible,
# age band 45-49, EUR 170 a month each (tools/world/health/care-expat-world.rates.csv, area 1). It is dearer than
# local products where we could compare (Spain: 238 against 340), so it is an upper bound for the country.
FALLBACK_ID = "health-eu-care-expat"
FALLBACK_COUNTRIES = ["GR", "MT", "CY", "HR", "SK", "LT", "ME", "RS", "MK", "XK", "TR", "UA"]
FALLBACK_EUR = 2 * 170.0

# Countries whose file has no priced figure but where a resident couple is covered by the public system with no
# fixed charge (an income-based charge, if any, is in the tax code). The note says why.
PUBLIC_FREE = {
    "PT": ("health-pt-vistos-residency", "Statutory, free: residents register with the SNS (Servico Nacional de Saude) "
           "for a utente number; the D7 visa stage asks only for travel medical insurance. No fixed premium. Most "
           "well-off residents also buy private cover; not included."),
    "FR": ("health-fr-ameli-puma", "Statutory, no fixed premium: PUMa covers residents without a job by right of stable, "
           "regular residence (after about 3 months). Its income-based charge, the cotisation subsidiaire maladie "
           "(6.5% of capital income above half the PASS), belongs to the tax code. A complementary mutuelle is "
           "usual; not included."),
    "SE": (None, "Public, tax-funded county healthcare for registered residents, no premium. Sweden has no residence "
           "route for a non-working couple from outside the EU; figure is what a resident pays."),
    "FI": (None, "Public, tax-funded healthcare for permanent residents (Kela), no premium; figure is what a resident pays."),
    "IS": (None, "Public, tax-funded healthcare after six months' legal residence, no premium; a bridge policy covers "
           "the first months. Iceland has no residence route for a non-working couple from outside the EEA."),
}

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


def rows() -> list[dict]:
    out = _swiss_rows()
    regions = c.nuts3()
    for d in _country_files():
        iso = d["country"]
        mine = regions[regions["iso"] == iso]
        if mine.empty:
            continue
        if d.get("amount") is None and iso in PUBLIC_FREE:
            source_id, note = PUBLIC_FREE[iso]
            source_id = source_id or (d["sources"][0]["source_id"] if d.get("sources") else None)
            for nuts in mine["nuts"]:
                out.append(c.row(c.place(nuts), 0.0, d["currency"], "per_month", d["period"], iso, source_id, note))
            continue
        if d.get("amount") is None:
            if iso not in FALLBACK_COUNTRIES:
                continue
            for nuts in mine["nuts"]:
                out.append(c.row(
                    c.place(nuts), FALLBACK_EUR, "EUR", "per_month", "2026", iso, FALLBACK_ID,
                    "Stand-in, no local tariff reached: the residence route needs health insurance, priced as an "
                    "international policy (Care Expat World Basic, EUR 1,200 deductible, EUR 170 each at 45 to 49, "
                    "two people). An upper bound; local products are cheaper where we could compare."))
            continue
        regional = {r["nuts"]: r for r in d.get("regional") or [] if r.get("amount") is not None}
        short = f"{d['kind']}: {d['policy']}"
        for nuts in mine["nuts"]:
            hit = next((regional[k] for k in sorted(regional, key=len, reverse=True) if nuts.startswith(k)), None)
            if hit:
                out.append(c.row(c.place(nuts), hit["amount"], d["currency"], "per_month", d["period"],
                                 c.place(hit["nuts"]), hit["source_id"], hit["note"]))
            else:
                out.append(c.row(c.place(nuts), d["amount"], d["currency"], "per_month", d["period"], iso,
                                 d["sources"][0]["source_id"], f"National figure. {short} Working: {d['working']}"))
    return out
