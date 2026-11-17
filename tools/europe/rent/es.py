"""Spain: rent of a 75 m2 two-bed in each NUTS 3 region's main town (provincial or island capital).

Three kinds of source, all measuring contracts signed in the year (new lets), as agreed rents:

1. Deposit registers (fianzas), where a region publishes them openly: Catalonia (Incasol), Valencian Community
   (Generalitat), Basque Country (EMAL). Calendar 2025, mean monthly rent per contract.
2. Tax data for everywhere else: the tax agency's (AEAT) "Estadistica de viviendas declaradas en IRPF" 2024,
   mean monthly rent and mean floor area of contracts signed in 2024, by municipality over 20,000 people.
   Brought to 2025 by the median 2024 to 2025 growth seen in the registers.
3. Navarre (own tax system, no AEAT data, no municipal register data): the Observatorio's average for its 21
   tense-market municipalities, third quarter of 2026.

Registers give rent per contract with no floor area, so the rent is scaled to 75 m2 with the mean floor area of
new contracts in the same municipality (AEAT for Catalonia and Valencia, EMAL for the Basque Country).
"""

import csv
import io
import re
import statistics

import common as c

AEAT_ID = "es-aeat-irpf-viviendas"
INCASOL_ID = "es-incasol"
GVA_ID = "es-gva-fianzas"
EMAL_ID = "es-emal"
NAVARRA_ID = "es-navarra-observatorio"

AEAT_BASE = ("https://sede.agenciatributaria.gob.es/AEAT/Contenidos_Comunes/La_Agencia_Tributaria/Estadisticas/"
             "Publicaciones/sites/irpfvivienda/2024/")
AEAT_MUNI = AEAT_BASE + "jrubik9a1ff8978fcbf71319b9de37b560d0135a635b0.html"
AEAT_PROV = AEAT_BASE + "jrubikf42fc49ff49ff008eb78484361f9a64ef49975636.html"
INCASOL_URL = "https://analisi.transparenciacatalunya.cat/resource/qww9-bvhh.csv?$limit=200000"
GVA_PACKAGE = "https://dadesobertes.gva.es/api/3/action/package_show?id=viv-reg-fia-{year}"
EMAL_URL = "https://www.euskadi.eus/contenidos/documentacion/informe_emal_2025t4/es_def/Informe-EMAL-anual-2025_cas.pdf"
NAVARRA_URL = ("https://www.navarra.es/es/-/nota-prensa/los-precios-de-los-alquileres-en-los-21-municipios-navarros-"
               "declarados-zona-de-mercado-tensionado-continuan-en-descenso-durante-el-tercer-trimestre-de-2026")
NAVARRA_ZMT_RENT = 793.0  # EUR/month, third quarter of 2026, 21 tense-market municipalities (about 93% of Navarre's lets)

SOURCES = [
    c.source(AEAT_ID, "Agencia Tributaria (AEAT)",
             "Estadistica de viviendas declaradas en IRPF 2024: comparativa de rentabilidad y precios de alquiler "
             "como vivienda habitual con los nuevos contratos (municipios de mas de 20.000 habitantes; "
             "comunidades autonomas y provincias)",
             AEAT_BASE + "home61829d753b14c91a2ac675e26cbce54b56391cf7.html",
             "Spanish public-sector information, reuse allowed with attribution (Ley 37/2007); no explicit licence "
             "line on the pages", "2024",
             "Mean monthly rent and mean floor area of contracts signed in the year, from landlords' income tax "
             "returns matched to the cadastre. Excludes the Basque Country and Navarre (own tax systems)."),
    c.source(INCASOL_ID, "Institut Catala del Sol (Incasol) via Generalitat de Catalunya open data",
             "Preu mitja del lloguer d'habitatges per municipi (fiances de lloguer dipositades)",
             "https://analisi.transparenciacatalunya.cat/d/qww9-bvhh", "Generalitat de Catalunya open data "
             "(reuse with attribution; the portal shows 'See Terms of Use')", "2025",
             "Census of all rent deposits lodged in the period: mean monthly rent of new contracts, by municipality."),
    c.source(GVA_ID, "Generalitat Valenciana (Institut Valencia de l'Habitatge)",
             "Registro de las fianzas de alquiler de viviendas 2024 and 2025 (fianzas depositadas por municipio)",
             "https://dadesobertes.gva.es/dataset/viv-reg-fia-2025", "CC BY 4.0",
             "2025", "One row per deposit (one month's rent) lodged in the year; we take the mean by municipality."),
    c.source(EMAL_ID, "Gobierno Vasco, Departamento de Vivienda y Agenda Urbana (Observatorio Vasco de la Vivienda)",
             "Estadistica del mercado de alquiler (EMAL), informe anual 2025", EMAL_URL,
             "Open Data Euskadi (CC BY 4.0)", "2025",
             "Rent deposits (fianzas) of free-market habitual-residence contracts: mean monthly rent of contracts "
             "that started in the year, by municipality, and floor-area rates for contracts in force."),
    c.source(NAVARRA_ID, "Gobierno de Navarra, Observatorio de la Vivienda de Navarra",
             "Los precios de los alquileres en los 21 municipios navarros declarados Zona de Mercado Tensionado "
             "continuan en descenso durante el tercer trimestre de 2026 (press release of 12 November 2026)",
             NAVARRA_URL, "Government of Navarre press release, no licence stated (free to read)", "2026-Q3",
             "Mean rent of contracts in the Observatorio's register of leases (RECA), 21 tense-market municipalities "
             "including Pamplona; outside them 634 EUR."),
]

# Main town where common.main_towns picks a larger or regional-capital town instead of the provincial or island
# capital. Value: INE municipality code.
MAIN_TOWN = {
    "ES111": "15030",  # A Coruna (the function picks Santiago, the regional capital)
    "ES114": "36038",  # Pontevedra, provincial capital (Vigo is larger)
    "ES431": "06015",  # Badajoz, provincial capital (function picks Merida)
    "ES612": "11012",  # Cadiz, provincial capital (function picks Jerez)
    "ES533": "07032",  # Mao, island capital (Ciutadella is slightly larger)
}

# Regions whose main town is too small for the AEAT table (under 20,000 people): use the province's figure.
PROVINCE_FALLBACK = {"ES703": "Santa Cruz de Tenerife", "ES706": "Santa Cruz de Tenerife"}

# Registers: NUTS 3 -> (INE code, EMAL name) for the Basque capitals; Catalan/Valencian by INE code.
BASQUE = {"ES211": ("01059", "Vitoria-Gasteiz"), "ES212": ("20069", "Donostia / San Sebastián"),
          "ES213": ("48020", "Bilbao")}
CATALAN = {"ES511": "08019", "ES512": "17079", "ES513": "25120", "ES514": "43148"}
VALENCIAN = {"ES521": ("03014", "ALICANTE", "ALICANTE"), "ES522": ("12040", "CASTELLÓN", "CASTELLÓ DE LA PLANA"),
             "ES523": ("46250", "VALENCIA", "VALENCIA")}


def _num(text: str) -> float:
    return float(text.replace(".", "").replace(",", "."))


def _aeat_tables():
    """Municipality and province tables: {key: (new_rent, new_m2)} from the AEAT comparison pages."""
    import html

    def parse(path):
        text = re.sub(r"(?s)<script.*?</script>|<style.*?</style>", "", path.read_text(encoding="utf-8", errors="replace"))
        out = {}
        for tr in re.findall(r"(?s)<tr[^>]*>(.*?)</tr>", text):
            cells = [re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", td))).strip()
                     for td in re.findall(r"(?s)<t[dh][^>]*>(.*?)</t[dh]>", tr)]
            if len(cells) == 9 and cells[0] != "Localización de la vivienda":
                out[cells[0]] = (_num(cells[2]), _num(cells[4]))
        return out

    muni_raw = parse(c.fetch(AEAT_ID, AEAT_MUNI, "comparativa_municipios_total_2024.html"))
    muni = {}
    for key, value in muni_raw.items():
        m = re.match(r"(.*)-(\d{5})$", key)
        if m:
            muni[m.group(2)] = (m.group(1), *value)
    prov = parse(c.fetch(AEAT_ID, AEAT_PROV, "comparativa_ccaa_provincia_2024.html"))
    return muni, prov


def _incasol():
    """{ine_code: {year: rent}} for full calendar years."""
    path = c.fetch(INCASOL_ID, INCASOL_URL, "incasol_municipi.csv")
    out = {}
    for r in csv.DictReader(path.open(encoding="utf-8")):
        if r["periode"] == "gener-desembre" and r["any"] in ("2024", "2025") and r["renda"]:
            out.setdefault(r["codi_territorial"], {})[r["any"]] = (float(r["renda"]), int(r["habitatges"]))
    return out


def _gva(year: str):
    """{(province, municipality): (mean rent, contracts)} from the Valencian deposit register."""
    import json
    import urllib.request
    meta = json.loads(c.fetch(GVA_ID, GVA_PACKAGE.format(year=year), f"package_{year}.json").read_text())["result"]
    url = next(r["url"] for r in meta["resources"] if r["format"] == "CSV")
    path = c.fetch(GVA_ID, url, f"fianzas_{year}.csv")
    groups = {}
    for r in csv.DictReader(path.open(encoding="utf-8"), delimiter=";"):
        try:
            value = float(r["importe_fianza"].replace(",", "."))
        except ValueError:
            continue
        groups.setdefault((r["provincia"], r["municipio"]), []).append(value)
    return {k: (statistics.mean(v), len(v)) for k, v in groups.items()}


def _emal():
    """{name: {'stock_rent', 'stock_m2_rate', 'new': {year: rent}}} for the three Basque capitals."""
    import pdfplumber
    path = c.fetch(EMAL_ID, EMAL_URL, "emal2025.pdf")
    with pdfplumber.open(path) as pdf:
        lines = [line for page in pdf.pages for line in (page.extract_text() or "").splitlines()]
    out = {}
    number = r"(-?[\d.]+,\d+)"
    for _, name in BASQUE.values():
        esc = re.escape(name)
        stock = [re.match(rf"^{esc} ([\d.]+) {number} {number} {number} {number} {number}$", l) for l in lines]
        stock = [m for m in stock if m]
        new = [re.match(rf"^{esc}" + (r" ([\d.]+,\d)" * 10) + "$", l) for l in lines]
        new = [m for m in new if m]
        if len(stock) != 1 or len(new) != 1:
            raise ValueError(f"EMAL: expected one stock and one new-contract line for {name}, got {len(stock)}, {len(new)}")
        out[name] = {"stock_rent": _num(stock[0].group(3)), "stock_rate": _num(stock[0].group(5)),
                     "new": {str(2016 + i): _num(v) for i, v in enumerate(new[0].groups())}}
    return out


def rows():
    muni, prov = _aeat_tables()
    incasol = _incasol()
    gva24, gva25 = _gva("2024"), _gva("2025")
    emal = _emal()

    # Growth of agreed new-contract rents 2024 -> 2025 in the ten register cities: brings AEAT 2024 to 2025.
    growth = []
    for code in CATALAN.values():
        growth.append(incasol[code]["2025"][0] / incasol[code]["2024"][0])
    for _, province, name in VALENCIAN.values():
        growth.append(gva25[(province, name)][0] / gva24[(province, name)][0])
    for name in (n for _, n in BASQUE.values()):
        growth.append(emal[name]["new"]["2025"] / emal[name]["new"]["2024"])
    factor = statistics.median(growth)
    growth_text = (f"median {factor:.3f} of the 2024-to-2025 change in agreed new-contract rents in ten cities "
                   f"(Barcelona, Girona, Lleida, Tarragona, Alicante, Castello, Valencia, Vitoria, Bilbao, Donostia; "
                   f"range {min(growth):.3f} to {max(growth):.3f})")

    out = []
    for nuts3 in c.regions_in("ES"):
        place = c.place(nuts3)
        code = MAIN_TOWN.get(nuts3)
        towns = c.main_towns(nuts3)
        if code is None:
            code = towns.iloc[0]["lau_code"]
        lau = c.lau()
        lau = lau[(lau["country"] == "ES") & (lau["lau_code"] == code)].iloc[0]
        city = c.city_code("ES", lau["name"], lau["name_latin"])
        town = lau["name"]
        measured = city or place

        if nuts3 in BASQUE:
            _, name = BASQUE[nuts3]
            e = emal[name]
            m2 = e["stock_rent"] / e["stock_rate"]
            rent25 = e["new"]["2025"]
            amount = rent25 * c.TWO_BED_M2 / m2
            note = (f"{name}: mean monthly rent of contracts that started in 2025 (Basque rent-deposit register, EMAL), "
                    f"{rent25:.1f} EUR, scaled to 75 m2 with the mean flat size of contracts in force "
                    f"({e['stock_rent']:.1f} EUR / {e['stock_rate']:.1f} EUR per m2 = {m2:.0f} m2). "
                    f"Mean, not median; free-market habitual residences in apartment blocks only.")
            out.append(c.row(place, round(amount, 2), "EUR", "per_month", "2025", measured, EMAL_ID, note))
        elif nuts3 in CATALAN:
            ine = CATALAN[nuts3]
            rent25, n = incasol[ine]["2025"]
            _, _, m2 = muni[ine]
            amount = rent25 * c.TWO_BED_M2 / m2
            note = (f"{town}: mean monthly rent of the {n} rent deposits lodged in 2025 (Incasol), {rent25:.2f} EUR, "
                    f"scaled to 75 m2 with the mean floor area of 2024 new contracts in the same municipality "
                    f"({m2:.0f} m2, AEAT). Mean, not median; all dwelling sizes.")
            out.append(c.row(place, round(amount, 2), "EUR", "per_month", "2025", measured, INCASOL_ID, note))
        elif nuts3 in VALENCIAN:
            ine, province, name = VALENCIAN[nuts3]
            rent25, n = gva25[(province, name)]
            _, _, m2 = muni[ine]
            amount = rent25 * c.TWO_BED_M2 / m2
            note = (f"{town}: mean of the {n} rent deposits (one month's rent each) lodged in 2025 in the Valencian "
                    f"register, {rent25:.0f} EUR, scaled to 75 m2 with the mean floor area of 2024 new contracts in "
                    f"the same municipality ({m2:.0f} m2, AEAT). Mean, not median; general-regime dwellings.")
            out.append(c.row(place, round(amount, 2), "EUR", "per_month", "2025", measured, GVA_ID, note))
        elif nuts3 == "ES220":
            note = ("Navarre has no municipal figure; this is the Observatorio's mean rent in the 21 tense-market "
                    "municipalities (Pamplona and its area, about 93% of Navarre's lets), third quarter of 2026. "
                    "Includes seasonal lets and all dwelling sizes, not scaled to 75 m2. Probably below a 75 m2 flat "
                    "in Pamplona itself.")
            out.append(c.row(place, NAVARRA_ZMT_RENT, "EUR", "per_month", "2026-Q3", place, NAVARRA_ID, note))
        elif nuts3 in PROVINCE_FALLBACK:
            name = PROVINCE_FALLBACK[nuts3]
            rent, m2 = prov[name]
            amount = rent / m2 * c.TWO_BED_M2 * factor
            note = (f"{town} is under 20,000 people, so no municipal figure. Province of {name} (Tenerife, La Gomera, "
                    f"La Palma, El Hierro together): mean new-contract rent {rent:.0f} EUR over mean {m2:.0f} m2 in "
                    f"2024 (AEAT), x 75 m2, x {factor:.3f} to 2025 ({growth_text}). Measured for the Canary Islands "
                    f"region (NUTS ES70) because the province has no NUTS code.")
            out.append(c.row(place, round(amount, 2), "EUR", "per_month", "2025", c.place("ES70"), AEAT_ID, note))
        else:
            if code not in muni:
                raise KeyError(f"{nuts3} {town} {code} not in the AEAT table")
            _, rent, m2 = muni[code]
            amount = rent / m2 * c.TWO_BED_M2 * factor
            note = (f"{town}: mean rent of contracts signed in 2024 {rent:.0f} EUR over mean floor area {m2:.0f} m2 "
                    f"(AEAT, landlords' tax returns), x 75 m2, x {factor:.3f} to 2025 ({growth_text}). "
                    f"Mean, not median; all dwelling sizes.")
            out.append(c.row(place, round(amount, 2), "EUR", "per_month", "2025", measured, AEAT_ID, note))
    return out
