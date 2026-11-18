"""Europe: the monthly cost of owning and running one new mid-size car, for every NUTS 3 region.

Reference car: new Toyota Corolla 1.8 Hybrid (140 PS), kept 8 years and 96,000 km (12,000 km a year), bought for cash.
One national figure per country, written for every region of that country (`measured_for` = the ISO country code).
Method and every input: .agent/research/europe/car.md. In short, per month and in local currency:

    depreciation   price_new x (1 - RESIDUAL_8Y) / 96
    insurance      comprehensive for a 45-year-old with a clean record / 12
    annual tax     yearly ownership tax / 12
    fuel           12,000 km x 5.1 l/100 km x petrol price / 12
    maintenance    servicing, repairs, tyres and the periodic inspection

Price, insurance and maintenance are national only by scaling a German anchor with Eurostat price levels
(prc_ppp_ind_1: vehicles A010701, restaurants and accommodation A0111 as the local-labour price level). Petrol is
the EU Weekly Oil Bulletin (EU) or the UK's DESNZ, and Eurostat's fuel price level elsewhere. Annual tax is read
from the national rules in the ACEA Tax Guide 2022 and gov.uk. Where an input is a stand-in, `note` says so.
"""

from __future__ import annotations

import re

import pandas as pd

import common as c

# ----------------------------------------------------------------------------------------------------------
# The reference car and use
KM_PER_YEAR = 12_000
YEARS = 8
LITRES_PER_100KM = 5.1  # between ADAC's WLTP 4.4 and Autokostencheck's 5.8 (older 98 PS model); see notes
RESIDUAL_8Y = 0.50  # share of the new price left after 8 years; see notes (Autokostencheck model: 66% at 5, 43% at 10)
GERMAN_PRICE_EUR = 33_340  # ADAC Autokatalog: Corolla 1.8 Hybrid Comfort (140 PS), list price, from 02/2025
GERMAN_INSURANCE_EUR = 1_030  # per year, see notes: ADAC base tariffs (HP 1,404; fully comprehensive SB 500 2,034) at 30%
GERMAN_MAINTENANCE_EUR_MONTH = 80  # servicing, repairs, tyres and inspection; ADAC workshop costs for Corolla Hybrids
FIXED_RATES = {"BGN": 1.95583, "HRK": 7.5345}

PERIOD = "2026"

# ----------------------------------------------------------------------------------------------------------
# Annual ownership tax of the reference car, per year, averaged over the 8 years where the rate changes with age.
# (amount, currency, basis, verified). verified False = a stand-in, said so in the row's note.
TAX = {
    "AT": (441, "EUR", "ACEA 2022: motor-related insurance tax 0.72 x (kW-59) + 0.72 x (CO2-97) per month for 103 kW, 104 g/km WLTP (2026 thresholds)", True),
    "BE": (246, "EUR", "ACEA 2022: Flemish circulation tax for 10 fiscal hp (343.60) less 13.5% CO2 and 15% Euro 6 corrections; 2022 rates, not indexed", True),
    "BG": (240, "EUR", "ACEA 2022: 3.30 BGN/kW x 103 kW x 2.3 (under 5 years) x 0.6 (Euro 6) = 469 BGN at 1.95583", True),
    "CY": (52, "EUR", "ACEA 2022: road tax 0.50 EUR per g CO2/km up to 120 g/km, 104 g/km", True),
    "CZ": (0, "CZK", "ACEA 2022: road tax only on business vehicles; hybrids exempt", True),
    "DE": (46, "EUR", "ADAC Autokatalog: Kfz-Steuer 46 EUR a year for this car", True),
    "DK": (1_040, "DKK", "ACEA 2022: CO2 tax 520 DKK per half-year for 102-116 g/km; rates rise each year to 2026, so understated", True),
    "EE": (0, "EUR", "ACEA 2022: no ownership tax on cars; a motor vehicle tax started in 2025 and is not in the guide", False),
    "ES": (129, "EUR", "ACEA 2022: IVTM for 12-15.99 fiscal hp, Madrid rate; many cities discount hybrids", True),
    "FI": (130, "EUR", "ACEA 2022: basic tax runs 53.29 to 654.44 EUR with CO2; about 130 at 104 g/km read from the range, not the table", False),
    "FR": (0, "EUR", "ACEA 2022: no annual tax on private cars (company-car tax only); malus is in the price", True),
    "GR": (0, "EUR", "ACEA 2022: 0 EUR coefficient for 0-122 g/km WLTP", True),
    "HR": (94, "EUR", "ACEA 2022: 101-130 kW, 900/700/600 HRK by age (under 2, 2-5, 5-10 years) at 7.5345; 8-year average", True),
    "HU": (83, "EUR", "ACEA 2022: HUF 345/kW under 4 years, 300/kW 4-7 years, 103 kW, at 400 HUF/EUR", True),
    "IE": (180, "EUR", "ACEA 2022: motor tax band A5, 100-110 g/km WLTP", True),
    "IT": (293, "EUR", "ACEA 2022: bollo: about 2.9 EUR per kW up to 100 kW and 4.35 above (Euro 6, base region); regions vary", True),
    "LT": (0, "EUR", "ACEA 2022: no ownership tax on cars", True),
    "LU": (44, "EUR", "ACEA 2022: tax = CO2 x 0.6 x 0.7 = 104 x 0.6 x 0.7", True),
    "LV": (36, "EUR", "ACEA 2022: road tax 96-115 g/km, cars registered from 2021", True),
    "MT": (110, "EUR", "ACEA 2022: circulation tax 101-130 g/km, first 5 years; it rises after year 5 and is not in the guide", True),
    "NL": (1_000, "EUR", "Stand-in: motor vehicle tax (MRB) for a 1,400 kg petrol car is about 1,000 EUR a year; tariff table not read", False),
    "PL": (0, "EUR", "ACEA 2022: no ownership tax on private cars", True),
    "PT": (205, "EUR", "ACEA 2022: IUC (117.82 cylinder + 60.28 CO2) x 1.15", True),
    "RO": (63, "EUR", "ACEA 2022: 9 x 19 RON per 200 cc (about 35 EUR) plus the 28 EUR road sticker", True),
    "SE": (1_524, "SEK", "ACEA 2022: malus years 1-3: 360 + 107 x (104-75) = 3,463 SEK, then 360; 8-year average", True),
    "SI": (0, "EUR", "ACEA 2022: no annual tax; the motor vehicle tax is paid once and is in the price", True),
    "SK": (0, "EUR", "ACEA 2022: motor vehicle tax only on business use", True),
    "GB": (225.6, "GBP", "gov.uk vehicle tax rate tables: 405 first year (101-110 g/km), 200 standard rate from year 2; 8-year average", True),
    "IS": (12_760, "ISK", "ACEA 2022: automobile charge 6,380 ISK per period, two periods a year, WLTP up to 146 g/km", True),
    "NO": (3_000, "NOK", "Stand-in: Norway's annual traffic insurance tax is about 3,000 NOK; not read from the tax authority", False),
    "CH": (350, "CHF", "Stand-in: cantonal motor vehicle tax is about 350 CHF for a car of this size; ACEA gives no figures", False),
    "TR": (330, "EUR", "ACEA 2022: MTV 1,601-1,800 cc: 3,556 / 2,781 / 1,635 TRY by age at 8.43 TRY/EUR; 2021 rates in euros, not revalued", False),
}
# Where no figure exists the median of the verified euro figures is used (Albania, Kosovo, Montenegro, North
# Macedonia, Serbia, Ukraine); Liechtenstein takes Switzerland's.


def _wob_history() -> pd.DataFrame:
    """52-week average Euro-super 95 price in EUR per litre, by ISO code, from the EU Weekly Oil Bulletin history."""
    page = c.fetch("eu-weekly-oil-bulletin", "https://energy.ec.europa.eu/data-and-analysis/weekly-oil-bulletin_en",
                   "page.html").read_text(errors="ignore")
    link = re.search(r'href="(/document/download/[^"]+Prices_History[^"]+\.xlsx)"', page).group(1)
    path = c.fetch("eu-weekly-oil-bulletin", "https://energy.ec.europa.eu" + link, "Weekly_Oil_Bulletin_Prices_History.xlsx")
    raw = pd.read_excel(path, sheet_name="Prices with taxes", header=None)
    header = raw.iloc[0]
    cols = {v.split("_")[0]: i for i, v in enumerate(header) if isinstance(v, str) and v.endswith("price_with_tax_euro95")}
    body = raw.iloc[3:].copy()
    body["date"] = pd.to_datetime(body[0], errors="coerce")
    body = body[body["date"].notna()].sort_values("date", ascending=False).head(52)
    out = {}
    for code, i in cols.items():
        values = pd.to_numeric(body[i], errors="coerce")
        if values.notna().sum() >= 40:
            out[{"EL": "GR"}.get(code, code)] = values.mean() / 1000
    out["_to"] = body["date"].max().strftime("%Y-%m-%d")
    return out


def _uk_petrol() -> float:
    """52-week average unleaded price in GBP per litre from DESNZ's weekly road fuel prices."""
    page = c.fetch("desnz-fuel", "https://www.gov.uk/government/statistics/weekly-road-fuel-prices", "page.html",
                   refresh=True).read_text(errors="ignore")
    link = re.search(r'href="(https://assets\.publishing\.service\.gov\.uk/media/[^"]+\.csv)"', page).group(1)
    path = c.fetch("desnz-fuel", link, "weekly-road-fuel-prices.csv", refresh=True)
    df = pd.read_csv(path, encoding="utf-8-sig")
    df["date"] = pd.to_datetime(df["Date"], dayfirst=True)
    last = df.sort_values("date", ascending=False).head(52)
    return float(last.iloc[:, 1].mean()) / 100


def _pli(item: str) -> dict:
    df = c.eurostat("prc_ppp_ind_1", f"A.PLI_EU27_2020.{item}.", startPeriod="2025")
    df = df[df["TIME_PERIOD"] == "2025"]
    out = {{"EL": "GR", "UK": "GB"}.get(g, g): v for g, v in zip(df["geo"], df["OBS_VALUE"])}
    return out


def _fx() -> dict:
    df = c.eurostat("ert_bil_eur_m", "M.AVG.NAC.", startPeriod="2026-08")
    df = df[df["TIME_PERIOD"] == df["TIME_PERIOD"].max()]
    return dict(zip(df["currency"], df["OBS_VALUE"])) | {"EUR": 1.0} | FIXED_RATES


COUNTRIES = sorted(set(c.nuts3()["iso"]))
BALKAN_PROXY = ["AL", "ME", "MK", "RS"]  # price-level stand-in for Kosovo and Ukraine, which Eurostat does not cover
PROXY_FOR = {"XK": BALKAN_PROXY, "UA": BALKAN_PROXY, "LI": ["CH"]}


def _with_proxies(table: dict) -> dict:
    out = dict(table)
    for iso, sources in PROXY_FOR.items():
        values = [table[s] for s in sources if s in table]
        if iso not in out and values:
            out[iso] = sum(values) / len(values)
    return out


def _uk_stand_ins(veh: dict, svc: dict, fuel_level: dict) -> None:
    """Eurostat's detailed price levels stop at 2022 for the UK. Use Ireland's vehicle level (another right-hand-drive
    market) and the UK's overall consumption price level (prc_ppp_ind, A01, 2024) against Germany's for services."""
    a01 = c.eurostat("prc_ppp_ind", "A.PLI_EU27_2020.A01.", startPeriod="2024")
    a01 = a01[a01["TIME_PERIOD"] == "2024"].set_index("geo")["OBS_VALUE"]
    veh["GB"] = veh["IE"]
    svc["GB"] = svc["DE"] * a01["UK"] / a01["DE"]
    fuel_level["GB"] = 100.0  # not used: the UK has its own pump survey


def inputs() -> dict:
    """Every country's inputs in euros (annual tax and petrol in local currency): the model's working table."""
    veh = _with_proxies(_pli("A010701"))
    svc = _with_proxies(_pli("A0111"))
    fuel_level = _with_proxies(_pli("A010702"))
    _uk_stand_ins(veh, svc, fuel_level)
    wob = _wob_history()
    eu_avg_fuel = wob["EU"]
    out = {}
    for iso in COUNTRIES:
        price_eur = GERMAN_PRICE_EUR * veh[iso] / veh["DE"]
        service = 0.5 + 0.5 * svc[iso] / svc["DE"]
        if iso in wob:
            petrol_eur, petrol_src = wob[iso], "EU Weekly Oil Bulletin, 52-week average to " + wob["_to"]
        elif iso == "GB":
            petrol_eur, petrol_src = None, "DESNZ weekly road fuel prices, 52-week average"
        else:
            petrol_eur = eu_avg_fuel * fuel_level[iso] / 100
            petrol_src = "Eurostat fuel price level (EU = 100) x EU 52-week average Euro-super 95 price"
        out[iso] = {"price_eur": price_eur, "service": service, "petrol_eur": petrol_eur, "petrol_src": petrol_src,
                    "veh_level": veh[iso], "svc_level": svc[iso]}
    return out


def _tax_eur(iso: str, fx: dict) -> tuple[float, str, bool]:
    if iso in TAX:
        amount, currency, basis, verified = TAX[iso]
        return amount / fx[currency], basis, verified
    if iso == "LI":
        amount, currency, basis, _ = TAX["CH"]
        return amount / fx[currency], "Switzerland's figure used for Liechtenstein: " + basis, False
    verified = sorted(TAX[i][0] / fx[TAX[i][1]] for i in TAX if TAX[i][3])
    median = verified[len(verified) // 2]
    return median, "No source found for this country; median of the verified countries' annual tax", False


def monthly_eur(iso: str, inp: dict, fx: dict, *, km: int = KM_PER_YEAR, years: int = YEARS, residual: float = RESIDUAL_8Y,
                uk_petrol_eur: float | None = None) -> dict:
    """The model for one country, in euros per month."""
    x = inp[iso]
    petrol = x["petrol_eur"] if x["petrol_eur"] is not None else uk_petrol_eur
    tax, _, _ = _tax_eur(iso, fx)
    parts = {
        "depreciation": x["price_eur"] * (1 - residual) / (years * 12),
        "insurance": GERMAN_INSURANCE_EUR * x["service"] / 12,
        "tax": tax / 12,
        "fuel": km * LITRES_PER_100KM / 100 * petrol / 12,
        "maintenance": GERMAN_MAINTENANCE_EUR_MONTH * x["service"] * (km / KM_PER_YEAR) ** 0.5,
    }
    parts["total"] = sum(parts.values())
    return parts


def _archive() -> None:
    """Keep the pages behind the hard-coded inputs in cache/, so anyone can check them."""
    c.fetch("adac-corolla", "https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/toyota/corolla/e21-facelift/340185/", "page.html")
    c.fetch("autokostencheck", "https://www.autokostencheck.de/Toyota/Toyota-Corolla/Corolla/corolla-hybrid-1-8-ze1he_47039/wertverlust-restwert/",
            "corolla-hybrid-1-8-wertverlust.html")
    c.fetch("acea-tax-guide-2022", "https://www.acea.auto/files/ACEA_Tax_Guide_2022.pdf", "ACEA_Tax_Guide_2022.pdf")
    c.fetch("gov-uk-vehicle-tax", "https://www.gov.uk/vehicle-tax-rate-tables", "page.html")


def rows():
    _archive()
    inp = inputs()
    fx = _fx()
    uk_eur = _uk_petrol() / fx["GBP"]
    out = []
    table = c.nuts3()
    for iso in COUNTRIES:
        currency = c.ISO_TO_CURRENCY[iso]
        rate = fx[currency]
        parts = monthly_eur(iso, inp, fx, uk_petrol_eur=uk_eur)
        x = inp[iso]
        _, basis, verified = _tax_eur(iso, fx)
        petrol_src = x["petrol_src"]
        stand_ins = []
        if iso in PROXY_FOR:
            stand_ins.append("price levels are stand-ins from " + "/".join(PROXY_FOR[iso]))
        if iso == "GB":
            stand_ins.append("vehicle price level is Ireland's and service price level is scaled from the UK's overall price level, "
                             "because Eurostat's detailed UK price levels stop in 2022")
        if not verified:
            stand_ins.append("annual tax is a stand-in")
        if iso in {"AL", "ME", "MK", "RS", "TR", "CH", "NO", "IS", "XK", "UA", "LI"}:
            stand_ins.append("petrol from price level, not a pump survey")
        note = (
            f"Own and run a new Toyota Corolla 1.8 Hybrid 8 years, 12,000 km a year, cash purchase. Per month in {currency}: "
            f"depreciation {parts['depreciation'] * rate:,.0f}, insurance {parts['insurance'] * rate:,.0f}, annual tax "
            f"{parts['tax'] * rate:,.0f}, fuel {parts['fuel'] * rate:,.0f}, maintenance and inspection "
            f"{parts['maintenance'] * rate:,.0f}. Price {x['price_eur'] * rate:,.0f} (German list price scaled by Eurostat's "
            f"vehicle price level {x['veh_level']:.1f} vs Germany), petrol: {petrol_src}. Tax: {basis}."
            + (" Stand-ins: " + "; ".join(stand_ins) + "." if stand_ins else "")
        )
        for nuts in table[table["iso"] == iso]["nuts"]:
            out.append(c.row(c.place(nuts), parts["total"] * rate, currency, "per_month", PERIOD, iso, "car-europe-model", note))
    return out


SOURCES = [
    c.source("car-europe-model", "Our model (Eurostat prices)",
             "Europe car cost model: a German anchor scaled by Eurostat price levels, with national petrol and annual tax",
             "tools/europe/car.py (this repository)", "Derived from the sources below; the model is ours", "2026",
             "Written by AI on 2026.11.17 by model claude sonnet 5.5. See .agent/research/europe/car.md for the method and inputs."),
    c.source("car-eurostat-ppp", "Eurostat", "Purchasing power parities and price level indices (prc_ppp_ind_1): purchase of vehicles, fuels, "
             "restaurants and accommodation, 2025; euro foreign exchange reference rates (ert_bil_eur_m)",
             "https://ec.europa.eu/eurostat/databrowser/view/prc_ppp_ind_1/", "CC BY 4.0", "2025",
             "Price level indices, EU27 = 100, covering the EU, EFTA, Turkey, Albania, Montenegro, North Macedonia and Serbia (the UK only to 2022).",
             retrieved=c.today()),
    c.source("eu-weekly-oil-bulletin", "European Commission, DG Energy", "Weekly Oil Bulletin, prices with taxes, history",
             "https://energy.ec.europa.eu/data-and-analysis/weekly-oil-bulletin_en", "Commission reuse policy (CC BY 4.0)", "2025-11 to 2026-11",
             "Euro-super 95 consumer price with taxes, EUR per 1,000 litres, 27 member states."),
    c.source("desnz-fuel", "UK Department for Energy Security and Net Zero", "Weekly road fuel prices",
             "https://www.gov.uk/government/statistics/weekly-road-fuel-prices", "OGL v3.0", "2025-11 to 2026-11",
             "Unleaded petrol pump price in pence per litre."),
    c.source("adac-corolla", "ADAC", "Autokatalog: Toyota Corolla 1.8 Hybrid Comfort (ab 02/25), Kosten",
             "https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/toyota/corolla/e21-facelift/340185/",
             "Free to read, no licence stated", "2025",
             "List price 33,340 EUR, annual vehicle tax 46 EUR, base insurance tariffs, WLTP 4.4 l/100 km."),
    c.source("autokostencheck", "Autokostencheck", "Toyota Corolla Hybrid 1.8: Wertverlust und Restwert",
             "https://www.autokostencheck.de/Toyota/Toyota-Corolla/Corolla/corolla-hybrid-1-8-ze1he_47039/wertverlust-restwert/",
             "Free to read, no licence stated", "2026", "Model forecast of residual value by age; used for the 8-year residual."),
    c.source("acea-tax-guide-2022", "ACEA", "Tax Guide 2022", "https://www.acea.auto/files/ACEA_Tax_Guide_2022.pdf",
             "(c) ACEA; the guide's rates are used as inputs, its text is not reproduced", "2022",
             "Annual ownership tax rules per country; rates are those of early 2022, not updated."),
    c.source("gov-uk-vehicle-tax", "GOV.UK", "Vehicle tax rate tables", "https://www.gov.uk/vehicle-tax-rate-tables", "OGL v3.0", "2026",
             "First-year rate 405 GBP (101-110 g/km) and standard rate 200 GBP."),
]
