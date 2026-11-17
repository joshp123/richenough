# /// script
# requires-python = ">=3.12"
# dependencies = ["pandas>=2.2", "openpyxl", "xlrd", "pdfplumber", "lxml", "requests"]
# ///
"""Europe: price levels of household consumption excluding rent, inside countries, from official sub-national studies.

Eurostat's PPPs give one price level per country. Here we collect where an official body measured price LEVELS
(not inflation) below the national level, so that Munich and the Uckermark, or Milan and Calabria, can differ.
`relative_levels()` returns one dict per region:

    {"nuts": <NUTS or ITL code, any level>, "relative": <price level excluding rent, national average = 1.0>,
     "period", "source_id", "note", "excludes_rent": True/False}

`excludes_rent` is False where the study could not drop housing rent (France's overseas departments): the
coordinator decides whether to use those. Re-basing: each study's own base (Germany = 100 and so on) is re-based so
that the population-weighted mean of its regions is exactly 1.0 (population: Eurostat LAU 2025). Where a study
already uses a population or expenditure weighted national base that we cannot reproduce (UK), its base is kept.

Countries with a sub-national figure here: DE (400 Kreise), IT (21 regions), GB (12 regions), FR (metropolitan
regions in three groups, plus the overseas departments). Everything else has no official sub-national price level
that I could open; see .agent/research/europe/regional-prices.md.

Run `uv run tools/europe/regional_prices.py` to print the table.
"""

from __future__ import annotations

import re

import pandas as pd

import common as c

# ---------------------------------------------------------------------------------------------------------------
# Germany: BBSR and IW Koeln, Regionaler Preisindex 2022, "ohne Wohnkosten", all 400 Kreise.
# ---------------------------------------------------------------------------------------------------------------
DE_ID = "bbsr-iw-rpi-2022"
DE_URL = "https://epflicht.ulb.uni-bonn.de/download/pdf/756930"
DE_STATES = ("Schleswig-Holstein|Hamburg|Niedersachsen|Bremen|Nordrhein-Westfalen|Hessen|Rheinland-Pfalz|"
             "Baden-Württemberg|Bayern|Saarland|Berlin|Brandenburg|Mecklenburg-Vorpommern|Sachsen-Anhalt|Sachsen|"
             "Thüringen|Mecklenburg-")  # the state name wraps onto a second line for Mecklenburg-Vorpommern


# ---------------------------------------------------------------------------------------------------------------
# Italy: ISTAT, indici spaziali dei prezzi al consumo 2022 (experimental), five ECOICOP divisions, 21 regions.
# ---------------------------------------------------------------------------------------------------------------
IT_ID = "istat-spc-2022"
IT_URL = "https://www.istat.it/wp-content/uploads/2024/10/Tabelle-e-grafici.xlsx"
IT_REGIONS = {  # ISTAT's region name -> NUTS 2 (Trentino-Alto Adige is published as two provinces)
    "Piemonte": "ITC1", "Valle d'Aosta": "ITC2", "Liguria": "ITC3", "Lombardia": "ITC4", "Alto Adige": "ITH1",
    "Trentino": "ITH2", "Veneto": "ITH3", "Friuli-Venezia Giulia": "ITH4", "Emilia-Romagna": "ITH5",
    "Toscana": "ITI1", "Umbria": "ITI2", "Marche": "ITI3", "Lazio": "ITI4", "Abruzzo": "ITF1", "Molise": "ITF2",
    "Campania": "ITF3", "Puglia": "ITF4", "Basilicata": "ITF5", "Calabria": "ITF6", "Sicilia": "ITG1",
    "Sardegna": "ITG2",
}

# ---------------------------------------------------------------------------------------------------------------
# United Kingdom: ONS relative regional consumer price levels 2016, Table 3 (all divisions, 12 regions).
# ---------------------------------------------------------------------------------------------------------------
GB_ID = "ons-rrcpl-2016"
GB_URL = ("https://www.ons.gov.uk/file?uri=/economy/inflationandpriceindices/articles/"
          "relativeregionalconsumerpricelevelsuk/2016/d3842817.xls")
GB_REGIONS = {  # ONS Table 3 name -> ITL 1 code (2025)
    "London": "TLI", "South East": "TLJ", "East": "TLH", "West Midlands": "TLG", "Scotland": "TLM",
    "South West": "TLK", "East Midlands": "TLF", "Wales": "TLL", "North West": "TLD", "North East": "TLC",
    "Northern Ireland": "TLN", "Yorkshire and the Humber": "TLE",
}

# ---------------------------------------------------------------------------------------------------------------
# France: INSEE spatial price comparison survey 2022 (Insee Premiere 1959 and 1958, July 2023; Insee Flash Corse 81).
# ---------------------------------------------------------------------------------------------------------------
FR_ID = "insee-ecsp-2022"
FR_URL_1959 = "https://www.insee.fr/fr/statistiques/fichier/7649921/ip1959.pdf"
FR_URL_1958 = "https://www.insee.fr/fr/statistiques/fichier/7648939/ip1958.pdf"
FR_PARIS = 1.050   # Paris urban unit against the rest of mainland France except Corsica, all consumption excluding rents (Fisher), ip1959 fig. 1
FR_CORSICA = 1.07  # Corsica against the rest of mainland France except the Paris urban unit, excluding rents (Fisher), ip1959 box
FR_DOM = {  # Fisher gap against metropolitan France, ip1958 fig. 1; Mayotte excludes rents, the others include them
    "FRY1": (1.158, True, "Guadeloupe"), "FRY2": (1.138, True, "Martinique"), "FRY3": (1.137, True, "Guyane"),
    "FRY4": (1.089, True, "La Reunion"), "FRY5": (1.103, False, "Mayotte"),
}  # tuple: gap, includes_rent, name

SOURCES = [
    c.source(DE_ID, "BBSR (Federal Institute for Research on Building, Urban Affairs and Spatial Development) and "
             "Institut der deutschen Wirtschaft Koeln",
             "Regionaler Preisindex fuer Deutschland - ein neuer Erhebungsansatz mit Big Data (Goecke, Henger, "
             "Schroeder, Schroeder, Wendt, Kawka; BBSR, Bonn 2023, ISBN 978-3-87994-047-9), annex table: "
             "Regionaler Preisindex ohne Wohnkosten 2022 by Kreis", DE_URL,
             "No open licence: 'Alle Rechte vorbehalten. Nachdruck nur mit genauer Quellenangabe gestattet' (BBSR "
             "imprint). Free to read; reuse of the Kreis values needs Josh's decision",
             "2022",
             "Web-scraped prices (online shops, chains, platforms) on the Destatis basket, 400 Kreise, Germany = 100 "
             "(population weighted). The 'ohne Wohnkosten' index leaves out all of COICOP 04 (rent, energy, water, "
             "service charges). IW Kurzbericht 93/2025 repeats the exercise for 2024 and finds the pattern stable."),
    c.source(IT_ID, "ISTAT", "Indici spaziali dei prezzi al consumo, anno 2022 (statistica sperimentale), "
             "Tabelle e grafici, Tavola 1: aggregate of five ECOICOP divisions, by region",
             "https://www.istat.it/statistica-sperimentale/indici-spaziali-dei-prezzi-al-consumo-anno-2022/",
             "ISTAT website content is CC BY 4.0 (istat.it copyright notice)", "2022",
             "Italy = 100. Covers food and non-alcoholic drinks, alcohol and tobacco, clothing, furnishings and "
             "household services, hotels and restaurants: about 48% of household spending. No housing, transport, "
             "health, communications or leisure. Scanner data, local CPI quotes and direct surveys in regional capitals "
             "(plus Padova and Bolzano). Experimental statistics."),
    c.source(GB_ID, "Office for National Statistics",
             "Relative regional consumer price levels of goods and services, UK: 2016 (Table 3, supplementary results)",
             "https://www.ons.gov.uk/economy/inflationandpriceindices/articles/relativeregionalconsumerpricelevelsuk/2016",
             "Open Government Licence v3.0", "2016",
             "UK = 100. 539 items in 10 COICOP divisions; division 04 covers housing services but excludes rental "
             "costs and owner-occupier costs. Survey by a contractor plus CPI price quotes. Latest ONS edition; ONS "
             "calls the finer English regions 'less robust' and says to read ranks, not exact values."),
    c.source(FR_ID, "INSEE", "Enquete de comparaison spatiale des prix 2022; Insee Premiere 1959 (Paris region against "
             "the provinces, and Corsica) and Insee Premiere 1958 (overseas departments), July 2023",
             "https://www.insee.fr/fr/statistiques/7649921",
             "Etalab Open Licence 2.0 (INSEE publications)", "2022",
             "Fisher price gaps between territory pairs, not a full regional grid. Paris urban unit +5.0% against the "
             "rest of mainland France excluding Corsica, excluding rents. Corsica +7% against the rest of mainland "
             "France, excluding rents. Overseas departments against metropolitan France: rents included except "
             "Mayotte."),
]


def _weights(prefixes: list[str]) -> dict[str, float]:
    """Population (Eurostat LAU 2025) of the regions whose NUTS 3 code starts with each prefix."""
    lau = c.lau()
    return {p: float(lau[lau["nuts3"].str.startswith(p)]["population"].sum()) for p in prefixes}


def _rebase(levels: dict[str, float], weights: dict[str, float]) -> dict[str, float]:
    mean = sum(levels[k] * weights[k] for k in levels) / sum(weights[k] for k in levels)
    return {k: v / mean for k, v in levels.items()}


def _german() -> list[dict]:
    import pdfplumber
    path = c.fetch(DE_ID, DE_URL, "bbsr-regionaler-preisindex.pdf")
    line = re.compile(rf"^(\d{{5}}) (.+?) ({DE_STATES}) (\d+,\d) (\d+,\d) (\d+,\d)$")
    found: dict[str, tuple[str, float, float, float]] = {}
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages[56:66]:  # annex pages 57 to 66
            for text in (page.extract_text() or "").splitlines():
                m = line.match(text.strip())
                if m:
                    total, ex_housing, housing = (float(m.group(i).replace(",", ".")) for i in (4, 5, 6))
                    found[m.group(1)] = (m.group(2), total, ex_housing, housing)
    lau = c.lau()
    lau = lau[lau["country"] == "DE"].copy()
    lau["kreis"] = lau["lau_code"].str[:5]
    kreis_nuts = lau.groupby("kreis")["nuts3"].first().to_dict()
    kreis_pop = lau.groupby("kreis")["population"].sum().to_dict()
    missing = sorted(set(found) - set(kreis_nuts))
    if missing or len(found) != 400:
        raise RuntimeError(f"Germany: parsed {len(found)} Kreise, unmatched to LAU: {missing}")
    levels = {k: v[2] for k, v in found.items()}
    relative = _rebase(levels, {k: kreis_pop[k] for k in levels})
    return [{"nuts": kreis_nuts[k], "relative": round(relative[k], 4), "period": "2022", "source_id": DE_ID,
             "excludes_rent": True,
             "note": f"BBSR/IW Regionaler Preisindex 2022 ohne Wohnkosten (all of COICOP 04 left out), Kreis "
                     f"{found[k][0]} ({k}): {found[k][2]} with Germany = 100; re-based to the population-weighted "
                     f"mean of the 400 Kreise. Index with housing: {found[k][1]}, housing alone: {found[k][3]}."}
            for k in sorted(found)]


def _italian() -> list[dict]:
    path = c.fetch(IT_ID, IT_URL, "istat-spc-2022-tabelle-e-grafici.xlsx")
    sheet = pd.read_excel(path, sheet_name=0, header=None)
    table = sheet.iloc[4:25]
    levels = {IT_REGIONS[str(row[0]).replace("’", "'")]: float(row.dropna().iloc[-1]) for _, row in table.iterrows()}
    if len(levels) != 21:
        raise RuntimeError(f"Italy: expected 21 regions, got {len(levels)}")
    relative = _rebase(levels, _weights(list(levels)))
    return [{"nuts": k, "relative": round(relative[k], 4), "period": "2022", "source_id": IT_ID, "excludes_rent": True,
             "note": f"ISTAT spatial price index 2022, aggregate of five ECOICOP divisions (food, drink and tobacco, "
                     f"clothing, furnishings, hotels and restaurants; about 48% of spending), Italy = 100: "
                     f"{levels[k]:.1f}; re-based to the population-weighted mean of the 21 regions. Region level; "
                     f"no housing, transport or health in the basket."}
            for k in levels]


def _british() -> list[dict]:
    path = c.fetch(GB_ID, GB_URL, "d3842817.xls")
    sheet = pd.read_excel(path, sheet_name=0, header=None)
    values = {str(a).strip(): float(b) for a, b in zip(sheet[0], sheet[1]) if str(a).strip() in GB_REGIONS}
    if len(values) != 12:
        raise RuntimeError(f"UK: expected 12 regions, got {len(values)}")
    return [{"nuts": GB_REGIONS[name], "relative": round(v / 100, 4), "period": "2016", "source_id": GB_ID,
             "excludes_rent": True,
             "note": f"ONS relative regional consumer price level 2016, {name}: {v} with UK = 100 (all ten COICOP "
                     f"divisions; rent and owner-occupier housing costs excluded). Region level (ITL 1). Prices are "
                     f"2016 relativities, not brought forward."}
            for name, v in values.items()]


def _check_french_figures() -> None:
    """The French gaps are typed in from two Insee Premiere PDFs; stop if the PDFs no longer say what we typed."""
    import pdfplumber
    expect = {FR_URL_1959: ["Ensemble hors loyers 5,0", "En Corse, les prix sont plus élevés de 7 % qu’en province (hors loyers)"],
              FR_URL_1958: ["Guadeloupe 15,8", "Martinique 13,8", "Guyane 13,7", "La Réunion 8,9",
                            "Mayotte (hors loyers) 10,3"]}
    for url, phrases in expect.items():
        path = c.fetch(FR_ID, url, url.rsplit("/", 1)[1])
        with pdfplumber.open(path) as pdf:
            text = " ".join(" ".join((page.extract_text() or "").split()) for page in pdf.pages)
        for phrase in phrases:
            if phrase not in text:
                raise RuntimeError(f"France: {url} no longer contains {phrase!r}")


def _french() -> list[dict]:
    _check_french_figures()
    regions = c.nuts_regions()
    fr2 = [n for n in regions[(regions["iso"] == "FR") & (regions["level"] == 2)]["nuts"]]
    metro = [n for n in fr2 if not n.startswith("FRY")]
    level = {n: 100.0 for n in metro}  # province = 100
    level["FR10"] = 100 * FR_PARIS
    level["FRM0"] = 100 * FR_CORSICA
    weights = _weights(metro)
    metro_mean = sum(level[n] * weights[n] for n in metro) / sum(weights.values())
    all_levels = dict(level)
    for code, (gap, _, _) in FR_DOM.items():
        all_levels[code] = metro_mean * gap
        weights.update(_weights([code]))
    relative = _rebase(all_levels, weights)
    out = []
    for n in metro:
        what = {"FR10": "Paris urban unit against the rest of mainland France (applied to the whole Ile-de-France "
                        "region): +5.0%",
                "FRM0": "Corsica against the rest of mainland France: +7%"}.get(
            n, "the rest of mainland France (the 'province' of the study, the base of both gaps)")
        out.append({"nuts": n, "relative": round(relative[n], 4), "period": "2022", "source_id": FR_ID,
                    "excludes_rent": True,
                    "note": f"INSEE spatial price comparison 2022, all consumption excluding rents (Fisher): {what}. "
                            f"Province = 100, Paris 105, Corsica 107; re-based to the population-weighted mean of "
                            f"France including the overseas departments. Three price groups only, region level."})
    for code, (gap, includes_rent, name) in FR_DOM.items():
        out.append({"nuts": code, "relative": round(relative[code], 4), "period": "2022", "source_id": FR_ID,
                    "excludes_rent": not includes_rent,
                    "note": f"INSEE spatial price comparison 2022, {name} against metropolitan France: "
                            f"{(gap - 1) * 100:+.1f}% (Fisher), "
                            + ("rents included, so not a rent-free level; " if includes_rent else "rents excluded; ")
                            + "metropolitan mean taken as 1.0 before re-basing to France including the overseas "
                              "departments."})
    return out


def relative_levels() -> list[dict]:
    return _german() + _italian() + _british() + _french()


if __name__ == "__main__":
    levels = relative_levels()
    df = pd.DataFrame(levels)
    df["country"] = df["nuts"].str[:2]
    with pd.option_context("display.max_rows", None, "display.width", 200, "display.max_colwidth", 60):
        print(df.drop(columns=["note"]).to_string())
        print(df.groupby("country")["relative"].agg(["count", "min", "max", "mean"]).to_string())
    known = set(c.nuts_regions()["nuts"])
    bad = [x["nuts"] for x in levels if x["nuts"] not in known]
    print("unknown NUTS codes:", bad)
    for s in SOURCES:
        print("source", s["source_id"], "|", s["licence"], "|", s["period"], "|", s["url"])
