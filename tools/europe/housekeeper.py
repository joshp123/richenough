"""Europe: gross hourly pay of a part-time, live-out cleaner or housekeeper hired by a household (`housekeeper-wage`).

Written by AI on 2026.11.17 by model claude sonnet 5.5. Notes: .agent/research/europe/housekeeper.md

Layers, best first (each row's note says which one it is):
1. France: Urssaf's declared pay of home employers (Cesu and DNS, excluding childcare) by departement, 2025.
2. United Kingdom: ASHE median hourly pay of SOC 9223 "cleaners and domestics", April 2026 (provisional),
   scaled to each ITL1 region by that region's ratio of pay in SOC 92 (elementary administration and service).
3. Everywhere else in Eurostat's structure of earnings survey (SES): mean hourly earnings of elementary occupations
   (ISCO 9) in administrative and support services (NACE N, which holds contract cleaning), firms with 10 or more
   employees, 2022, moved to 2025 with Eurostat's labour cost index for wages and salaries in NACE N.
   Floor: where a domestic-worker statutory minimum is higher (Spain, Italy), the minimum is used.
4. Turkey: ILO's mean hourly earnings of elementary occupations (labour force survey, 2025).
5. Montenegro: only the general minimum wage turned into an hourly figure; a lower bound.
6. Liechtenstein: Switzerland's figure.
Kosovo and Ukraine: nothing usable found (Ukraine's minimum wage, about 1 EUR an hour, is far below the going rate); no rows.
"""

from __future__ import annotations

import pandas as pd

import common as c

ISO_NUTS = {"GR": "EL", "GB": "TL"}
# Euro conversion rates fixed by the Council: Bulgaria (1 Jan 2026) and Croatia (1 Jan 2023).
BGN_PER_EUR = 1.95583
HRK_PER_EUR = 7.5345
HOURS_PER_MONTH = 40 * 52 / 12  # general minimum wage (monthly) to hourly, 40 hours a week

SES = "eurostat-ses22-hourly-occupation"
LCI = "eurostat-lci-wages-nace-n"
MW = "eurostat-minimum-wages"
URSSAF = "urssaf-particuliers-employeurs-2025"
ONS = "ons-ashe-2026-cleaners"
BOE = "boe-smi-2026-hogar"
ITCC = "hk-it-informazionefiscale"
ILO = "ilostat-ehra-elementary"
FRSAL = "hk-fr-salerya"

EUROSTAT_LICENCE = "CC BY 4.0 (Eurostat reuse policy)"

SOURCES = [
    c.source(SES, "Eurostat", "Structure of earnings survey 2022: mean hourly earnings by sex, occupation and economic activity (earn_ses22_47), "
             "ISCO-08 elementary occupations (OC9), NACE Rev. 2 section N (administrative and support service activities), firms with 10 or more employees",
             "https://ec.europa.eu/eurostat/databrowser/view/earn_ses22_47", EUROSTAT_LICENCE, "2022",
             "Excludes households as employers. Elementary occupations in section N are mostly cleaners. Amounts in national currency (Bulgaria in BGN, Croatia in HRK)."),
    c.source(LCI, "Eurostat", "Labour cost index by NACE Rev. 2 activity, wages and salaries (D11), 2020=100, annual (lc_lci_r2_a), section N",
             "https://ec.europa.eu/eurostat/databrowser/view/lc_lci_r2_a", EUROSTAT_LICENCE, "2022-2025",
             "Used only to move the 2022 survey figure to 2025."),
    c.source(MW, "Eurostat", "Monthly minimum wages, bi-annual data (earn_mw_cur)",
             "https://ec.europa.eu/eurostat/databrowser/view/earn_mw_cur", EUROSTAT_LICENCE, "2022-2026",
             "General national minimum wage, monthly. Used to move Albania's and North Macedonia's 2022 figure to 2025, and as the lower bound for Montenegro and Ukraine."),
    c.source(URSSAF, "Urssaf (Acoss)", "Particuliers employeurs en 2025: employers, hours declared and net wage bill by department and type of employment (Cesu, DNS, Pajemploi)",
             "https://open.urssaf.fr/explore/dataset/particuliers-employeurs-en-2025/", "ODbL 1.0", "2025",
             "Net wages declared by households that employ people at home, excluding childcare (hors garde d'enfant: cleaning, care of older people, gardening, tutoring)."),
    c.source(FRSAL, "Salerya", "Quel salaire pour une femme de menage en 2026 ? (net 10,82 EUR = brut 13,87 EUR, conges payes inclus, from 1 June 2026)",
             "https://salerya.fr/statuts/particulier-employeur/femme-de-menage/", "free to read, no licence stated", "2026",
             "Secondary source for the net-to-gross ratio of Cesu pay (0.78). Not official."),
    c.source(ONS, "Office for National Statistics", "Annual Survey of Hours and Earnings 2026 (provisional): Table 14.5a hourly pay, SOC 2020 4-digit; Table 3.5a region by SOC 2-digit",
             "https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/earningsandworkinghours/datasets/occupation4digitsoc2010ashetable14", "Open Government Licence v3.0", "2026-04",
             "Median gross hourly pay of employee jobs, April 2026. PAYE-based, so cleaners paid informally are missing."),
    c.source(BOE, "Boletin Oficial del Estado", "Real Decreto 126/2026, de 18 de febrero, por el que se fija el salario minimo interprofesional para 2026 (BOE-A-2026-3815), art. 4.2",
             "https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-3815", "Spanish public sector reuse (Ley 37/2007)", "2026",
             "Statutory minimum for domestic workers paid by the hour, living out: 9.55 EUR per hour worked, all pay elements included."),
    c.source(ITCC, "informazionefiscale.it", "Lavoro domestico: la tabella delle retribuzioni di colf e badanti per il 2026",
             "https://www.informazionefiscale.it/colf-badanti-tabella-retribuzioni-2026-aumento-stipendio", "free to read, no licence stated", "2026",
             "Secondary report of the CCNL lavoro domestico minimum rates in force from 1 January 2026 (agreement of 11 February 2026). Level B, hired by the hour, not living in: 7.01 EUR per hour."),
    c.source(ILO, "ILOSTAT (ILO)", "Average hourly earnings of employees by sex and occupation, local currency (EAR_EHRA_SEX_OCU_NB_A), ISCO-08 major group 9 elementary occupations",
             "https://rplumber.ilo.org/data/indicator/?id=EAR_EHRA_SEX_OCU_NB_A", "CC BY 4.0 (ILO)", "2025",
             "Turkey: Household Labour Force Survey, all elementary occupations in all sectors."),
]


def _nuts_regions(iso: str) -> list[str]:
    return c.regions_in(ISO_NUTS.get(iso, iso))


def _national(iso: str, amount: float, currency: str, period: str, source_id: str, measured: str, note: str) -> list[dict]:
    return [c.row(c.place(r), round(amount, 2), currency, "per_hour", period, iso, source_id, f"{measured} {note}".strip())
            for r in _nuts_regions(iso)]


def _eurostat_ses(nace: str) -> dict[str, float]:
    df = c.eurostat("earn_ses22_47", f"A.T.ERN.OC9..{nace}.NAC.")
    df = df.dropna(subset=["OBS_VALUE"])
    out = {r.geo: r.OBS_VALUE for r in df[df["sizeclas"] == "TOTAL"].itertuples()}
    out.update({r.geo: r.OBS_VALUE for r in df[df["sizeclas"] == "GE10"].itertuples()})  # firms with 10+ employees preferred
    return out


def _lci() -> dict[str, dict[int, float]]:
    df = c.eurostat("lc_lci_r2_a", "A.I20.N.D11.", startPeriod="2022")
    out: dict[str, dict[int, float]] = {}
    for r in df.dropna(subset=["OBS_VALUE"]).itertuples():
        out.setdefault(r.geo, {})[int(r.TIME_PERIOD)] = r.OBS_VALUE
    return out


def _minimum_wage() -> dict[str, dict[str, float]]:
    df = c.eurostat("earn_mw_cur", "", startPeriod="2022-S1")
    df = df[df["currency"] == "NAC"]
    out: dict[str, dict[str, float]] = {}
    for r in df.dropna(subset=["OBS_VALUE"]).itertuples():
        out.setdefault(r.geo, {})[r.TIME_PERIOD] = r.OBS_VALUE
    return out


def _france() -> list[dict]:
    path = c.fetch(URSSAF, "https://open.urssaf.fr/api/explore/v2.1/catalog/datasets/particuliers-employeurs-en-2025/exports/csv?use_labels=true", "pe2025.csv")
    d = pd.read_csv(path, sep=";", dtype=str, encoding="utf-8-sig")
    d.columns = [x.strip("﻿") for x in d.columns]
    d = d[d.iloc[:, 0].isin(["CESU_HGED", "DNS_HGED"])].copy()
    d["hours"] = d["Nombre d'heures déclarées"].astype(float)
    d["net"] = d["Masse salariale nette"].astype(float)
    dept = d.groupby("Code département")[["hours", "net"]].sum()
    national = dept["net"].sum() / dept["hours"].sum()

    lau = c.lau()
    lau = lau[lau["country"] == "FR"].copy()
    lau["dept"] = lau["lau_code"].str[:3].where(lau["lau_code"].str.startswith("97"), lau["lau_code"].str[:2])
    to_nuts = lau.groupby("dept")["nuts3"].agg(lambda s: s.mode().iat[0])

    out, seen = [], set()
    for code, r in dept.iterrows():
        nuts = to_nuts.get(code)
        if nuts is None:
            continue
        seen.add(nuts)
        net = r["net"] / r["hours"]
        out.append(c.row(
            c.place(nuts), round(net / 0.78, 2), "EUR", "per_hour", "2025", c.place(nuts), URSSAF,
            f"Layer 1. Mean declared net pay of home employers' staff excluding childcare, departement {code}: {net:.2f} EUR per hour "
            f"({r['hours'] / 1e6:.2f} million hours, Cesu and DNS), divided by 0.78 to get gross including the 10 percent paid-leave allowance that "
            f"Cesu folds into the hourly rate (net 10.82 = gross 13.87 EUR, source {FRSAL}). Without the allowance: {net / 0.78 / 1.1:.2f}. "
            "Covers cleaning, care of older people, gardening and tutoring, so it is a little above a pure cleaner's rate."))
    for nuts in c.regions_in("FR"):
        if nuts not in seen:
            out.append(c.row(c.place(nuts), round(national / 0.78, 2), "EUR", "per_hour", "2025", "FR", URSSAF,
                             f"Layer 1, national mean (no departement figure): net {national:.2f} EUR per hour divided by 0.78."))
    return out


def _united_kingdom() -> list[dict]:
    t14 = c.fetch(ONS, "https://www.ons.gov.uk/file?uri=/employmentandlabourmarket/peopleinwork/earningsandworkinghours/datasets/"
                  "occupation4digitsoc2010ashetable14/2026provisional/ashetable142026provisional.zip", "t14-2026provisional.zip")
    t3 = c.fetch(ONS, "https://www.ons.gov.uk/file?uri=/employmentandlabourmarket/peopleinwork/earningsandworkinghours/datasets/"
                 "regionbyoccupation2digitsocashetable3/2026provisional/ashetable32026provisional.zip", "table3-2026prov.zip")
    import io
    import zipfile

    def sheet(path, marker):
        with zipfile.ZipFile(path) as z:
            name = next(n for n in z.namelist() if marker in n)
            return pd.read_excel(io.BytesIO(z.read(name)), sheet_name="All", header=None)

    a = sheet(t14, "Table 14.5a")
    cleaners = float(a[a.iloc[:, 1].astype(str).str.strip("'") == "9223"].iloc[0, 3])
    b = sheet(t3, "Table 3.5a")
    b = b[b.iloc[:, 1].astype(str).str.strip("'") == "92"]
    labels = {"United Kingdom": "UK"}
    ratio: dict[str, float] = {}
    uk92 = None
    for desc, med in zip(b.iloc[:, 0].astype(str), pd.to_numeric(b.iloc[:, 3], errors="coerce")):
        name = desc.split(",")[0] if "," in desc else "United Kingdom"
        if pd.isna(med):
            continue
        ratio[name.strip()] = float(med)
    uk92 = ratio.pop("United Kingdom", None) or ratio.get("UK")
    itl1 = {"North East": "TLC", "North West": "TLD", "Yorkshire and The Humber": "TLE", "East Midlands": "TLF", "West Midlands": "TLG",
            "East": "TLH", "London": "TLI", "South East": "TLJ", "South West": "TLK", "Wales": "TLL", "Scotland": "TLM", "Northern Ireland": "TLN"}
    out = [c.row("GB", cleaners, "GBP", "per_hour", "2026", "GB", ONS,
                 "ONS ASHE table 14.5a, UK median gross hourly pay for cleaners and domestics (SOC 9223), April 2026.")]
    for nuts in c.regions_in("TL"):
        region = next((n for n, code in itl1.items() if nuts.startswith(code)), None)
        med92 = ratio.get(region) if region else None
        if med92 and uk92:
            amount = cleaners * med92 / uk92
            note = (f"Layer 2. UK median hourly pay of SOC 9223 cleaners and domestics, April 2026 (provisional): {cleaners:.2f} GBP, "
                    f"times {region}'s median in SOC 92 elementary administration and service ({med92:.2f}) over the UK's ({uk92:.2f}). "
                    "Workplace region. PAYE employees only. Cleaners at firms and in homes are mixed.")
            measured = c.place(nuts[:3])
        else:
            amount, note, measured = cleaners, f"Layer 2. UK median hourly pay of SOC 9223 cleaners and domestics, April 2026 (provisional): {cleaners:.2f} GBP; no regional ratio.", "GB"
        out.append(c.row(c.place(nuts), round(amount, 2), "GBP", "per_hour", "2026", measured, ONS, note))
    return out


def rows() -> list[dict]:
    out: list[dict] = _france() + _united_kingdom()
    ses_n, ses_all = _eurostat_ses("N"), _eurostat_ses("B-S_X_O")
    lci, mw = _lci(), _minimum_wage()
    floors = {"ES": (9.55, BOE, "domestic-worker statutory minimum, Real Decreto 126/2026 art. 4.2"),
              "IT": (7.01, ITCC, "CCNL lavoro domestico minimum, level B, hired by the hour, from 1 January 2026")}

    for iso in c.ISO_TO_CURRENCY:
        if iso in ("FR", "GB"):
            continue
        geo = ISO_NUTS.get(iso, iso)
        currency = c.ISO_TO_CURRENCY[iso]
        if iso == "TR":
            ilo = pd.read_csv(c.fetch(ILO, "https://rplumber.ilo.org/data/indicator/?id=EAR_EHRA_SEX_OCU_NB_A", "EAR_EHRA_SEX_OCU_NB_A_europe.csv"),
                              dtype=str, encoding="utf-8-sig")
            t = ilo[(ilo["ref_area"] == "TUR") & (ilo["classif1"] == "OCU_ISCO08_9")].sort_values("time").iloc[-1]
            m = mw.get("TR", {})
            last_k = sorted(m)[-1]
            floor = m[last_k] / HOURS_PER_MONTH
            note = (f"Mean hourly earnings of ISCO 9 elementary occupations, all sectors, labour force survey {t['time']}: {float(t['obs_value']):.2f} TRY. "
                    "Wider than cleaning; formal and informal employees.")
            if floor > float(t["obs_value"]):
                out += _national("TR", floor, "TRY", last_k[:4], MW, "Layer 4.",
                                 note + f" Raised to the general minimum wage of {last_k}, {m[last_k]:.0f} TRY a month over {HOURS_PER_MONTH:.1f} hours, "
                                 "because the 2025 survey figure is below the 2026 minimum after Turkey's large rise.")
            else:
                out += _national("TR", float(t["obs_value"]), "TRY", str(t["time"]), ILO, "Layer 4.", note)
            continue
        base = ses_n.get(geo)
        basis = "NACE N"
        if base is None:
            base, basis = ses_all.get(geo), "all sectors (NACE B-S excl. O)"
        if base is not None:
            # move 2022 -> 2025 (latest year the wage index has)
            series = lci.get(geo, {})
            years = [y for y in sorted(series) if y >= 2022]
            if 2022 in series and len(years) > 1:
                last = years[-1]
                factor, how = series[last] / series[2022], f"labour cost index wages NACE N {last}/2022"
            else:
                m = mw.get(geo, {})
                first = next((k for k in sorted(m) if k.startswith("2022")), None)
                last_k = sorted(m)[-1] if m else None
                if first and last_k:
                    factor, how, last = m[last_k] / m[first], f"minimum wage {last_k}/{first}", int(last_k[:4])
                else:
                    factor, how, last = 1.0, "no wage index available, so left at 2022 prices", 2022
            amount = base * factor
            rate = 1.0
            if iso == "BG":
                rate = 1 / BGN_PER_EUR
            elif iso == "HR":
                rate = 1 / HRK_PER_EUR
            amount *= rate
            floor = floors.get(iso)
            note = (f"Layer 3. Eurostat SES 2022 mean hourly earnings of elementary occupations, {basis}, firms with 10+ employees: {base:.2f} "
                    f"{'BGN' if iso == 'BG' else 'HRK' if iso == 'HR' else currency}, times {factor:.3f} ({how})"
                    f"{', converted at the fixed euro rate' if rate != 1.0 else ''}. Excludes households as employers, so it is what cleaners "
                    "employed by firms earn, not a household's direct hire.")
            src = SES
            if floor and amount < floor[0]:
                note += f" Raised to the {floor[2]}: {floor[0]:.2f}."
                amount, src = floor[0], floor[1]
            elif floor:
                note += f" For reference, the {floor[2]}: {floor[0]:.2f}."
            out += _national(iso, amount, currency, str(last), src, "", note)
            continue
        m = mw.get(geo)
        if m and iso == "ME":  # Ukraine's minimum (about 1 EUR an hour) is far below what households pay, so no row
            last_k = sorted(m)[-1]
            hourly = m[last_k] / HOURS_PER_MONTH
            out += _national(iso, hourly, currency, last_k[:4], MW, "Layer 5.",
                             f"General national minimum wage {last_k}: {m[last_k]:.0f} {currency} a month, divided by {HOURS_PER_MONTH:.1f} hours. "
                             "A lower bound: no occupation-level pay found.")
    swiss = [r for r in out if r["place_code"].startswith("NUTS-CH")]
    if swiss:
        r = swiss[0]
        out += _national("LI", r["amount"], "CHF", r["period"], r["source_id"], "",
                         "Switzerland's figure: Liechtenstein shares its currency and labour market and has no survey of its own. "
                         + r["note"])
    return out
