"""Price level of everyday spending (household consumption excluding housing), US = 100, for every country.

Method, the one the World Bank itself uses between ICP benchmarks:
  PPP_now = PPP_2021 x (CPI_country_now / CPI_country_2021) / (CPI_US_now / CPI_US_2021)
  price level = 100 x PPP_now / exchange rate_now
where PPP_2021 is ICP 2021's purchasing power parity for "individual consumption expenditure by households,
without housing" (local currency per US dollar), CPI is the IMF's monthly headline CPI, and "now" is the
three months July to September 2026. Countries ICP 2021 does not cover are estimated from GDP per head
and, where the EU publishes one, its cost-of-living coefficient for its staff in that capital (see impute()).
"""

import json
import math
import statistics

from exchange_rates import DOLLAR_PEGS, rate_for_months, rates
from lib import CACHE, NUTS_COUNTRIES, PLAN_COUNTRY, countries, fmt, imf_sdmx, iso3_to_iso2, wb_icp

NOW = ["2026-07", "2026-08", "2026-09"]
NOW_LABEL = "2026-Q3"
EARLIEST_NOW = "2026-04"  # a country's latest three months of CPI must end on or after this month
BASE_YEAR = "2021"
ICP_ALIASES = {"RUT": "RU"}  # ICP 2021 publishes Russia under RUT
# Currencies replaced since 2021: old units per new unit, to restate ICP 2021 parities in today's currency.
REDENOMINATED = {"BG": 1.95583, "SL": 1000.0}  # ICP already restates Croatia in euro
# ICP 2021 parities that cannot be carried forward: Zimbabwe changed currency twice since 2021, and Somalia's
# parity is in US dollars while its CPI and exchange rate are in shillings. These are estimated like non-ICP countries.
NOT_CARRIED = {"ZW", "SO"}
# Territories and microstates with no GDP figure in the WEO: they take the price level of the country whose
# currency, prices and supply chains they share. Puerto Rico is left to the US tables.
PARENT = {
    "GL": "DK", "FO": "DK", "JE": "GB", "GG": "GB", "IM": "GB", "GI": "GB", "FK": "GB", "SH": "GB", "PN": "GB", "IO": "GB",
    "MC": "FR", "NC": "FR", "PF": "FR", "WF": "FR", "PM": "FR", "BL": "FR", "MF": "FR", "RE": "FR", "GP": "FR", "MQ": "FR",
    "GF": "FR", "YT": "FR", "VA": "IT", "AX": "FI", "SJ": "NO", "BV": "NO", "GU": "US", "VI": "US", "AS": "US", "MP": "US",
    "UM": "US", "CK": "NZ", "NU": "NZ", "TK": "NZ", "NF": "AU", "CX": "AU", "CC": "AU", "HM": "AU", "BQ": "CW", "SX": "CW",
    "EH": "MA", "TC": "BS", "VG": "VI",
}
SKIP = {"PR", "AQ", "TF", "GS", "AN", "CS"}  # Puerto Rico (US tables), uninhabited territories, and GeoNames' defunct codes

SOURCES = [
    {
        "source_id": "jp-stat-regional-cpi-2025",
        "publisher": "Statistics Bureau of Japan",
        "title": "Regional difference index of consumer prices, Retail Price Survey (structural edition) 2025, table 1 by prefecture",
        "url": "https://www.stat.go.jp/data/kouri/kouzou/pdf/g_2025.pdf",
        "licence": "Government of Japan Standard Terms of Use 2.0 (compatible with CC BY 4.0)",
        "retrieved": "2026-11-17",
        "period": "2025",
        "note": "All items excluding rent, national average = 100. Published 18 September 2026. Values typed into tools/world/regional/jp-regional-price.curated.csv.",
    },
    {
        "source_id": "wb-icp-2021",
        "publisher": "World Bank, International Comparison Program",
        "title": "ICP 2021: purchasing power parities and price level indexes by expenditure heading",
        "url": "https://www.worldbank.org/en/programs/icp",
        "licence": "CC BY 4.0",
        "retrieved": "2026-11-17",
        "period": "2021",
        "note": "World Bank API source 90. Heading 9260000, individual consumption expenditure by households without housing, is the everyday price level; other headings feed the car estimate.",
    },
    {
        "source_id": "imf-cpi",
        "publisher": "International Monetary Fund",
        "title": "Consumer Price Index (CPI) dataset, all items, monthly",
        "url": "https://data.imf.org/en/datasets/IMF.STA:CPI",
        "licence": "IMF terms of use: free reuse with attribution (https://www.imf.org/external/terms.htm)",
        "retrieved": "2026-11-17",
        "period": "2020-01 to 2026-10",
        "note": "National CPIs as reported to the IMF. Used to carry ICP 2021 parities forward to 2026.",
    },
    {
        "source_id": "imf-weo",
        "publisher": "International Monetary Fund",
        "title": "World Economic Outlook database, October 2026: consumer prices (PCPI) and GDP per capita (NGDPDPC)",
        "url": "https://data.imf.org/en/datasets/IMF.RES:WEO",
        "licence": "IMF terms of use: free reuse with attribution (https://www.imf.org/external/terms.htm)",
        "retrieved": "2026-11-17",
        "period": "2019 to 2026 (2026 partly IMF estimate)",
        "note": "Annual CPI where the monthly CPI stops early; GDP per head for estimating countries outside ICP 2021.",
    },
    {
        "source_id": "eurostat-colc-ext",
        "publisher": "Eurostat",
        "title": "Correction coefficients outside the European Union (duty stations), index Brussels = 100 (prc_colc_ext)",
        "url": "https://ec.europa.eu/eurostat/databrowser/view/prc_colc_ext/default/table",
        "licence": "CC BY 4.0 (Eurostat reuse policy)",
        "retrieved": "2026-11-17",
        "period": "2021 to 2026 (July of each year)",
        "note": "Cost of living for EU staff in each capital, excluding housing, measured with the Brussels staff basket. An expatriate basket: an independent check on ICP, and an input where ICP is missing.",
    },
]


def imf_cpi(name: str) -> dict[str, dict[str, float]]:
    """ISO2 -> {period: CPI} with periods as YYYY-MM or YYYY-Qn. The IMF codes West Bank and Gaza as WBG."""
    raw = imf_sdmx(CACHE / "imf-cpi" / name)
    to2 = {**iso3_to_iso2(), "WBG": "PS"}
    return {to2[c]: {p.replace("-M", "-"): v for p, v in s.items()} for c, s in raw.items() if c in to2}


def quarter_months(q: str) -> list[str]:
    year, n = q.split("-Q")
    return [f"{year}-{3 * (int(n) - 1) + k:02d}" for k in (1, 2, 3)]


def weo(indicator: str) -> dict[str, dict[str, float]]:
    raw = imf_sdmx(CACHE / "imf-weo" / f"{indicator}.xml")
    to2 = iso3_to_iso2()
    return {to2[c]: s for c, s in raw.items() if c in to2}


def cpi_ratio(iso2: str, monthly: dict, quarterly: dict, annual: dict) -> tuple[float | None, list[str], str]:
    """CPI over the latest three months (July to September 2026 where published) / CPI 2021.
    Falls back to the latest quarter, then to the IMF's 2026 annual estimate. Returns (ratio, months, how)."""
    m = monthly.get(iso2, {})
    base = [m.get(f"{BASE_YEAR}-{k:02d}") for k in range(1, 13)]
    if all(base):
        recent = sorted(k for k in m if k <= NOW[-1])[-3:]
        if len(recent) == 3 and recent[0] >= EARLIEST_NOW:
            return statistics.fmean(m[k] for k in recent) / statistics.fmean(base), recent, "monthly CPI"
    q = quarterly.get(iso2, {})
    qbase = [q.get(f"{BASE_YEAR}-Q{k}") for k in range(1, 5)]
    if all(qbase):
        recent_q = sorted(k for k in q if k <= "2026-Q3")[-1:]
        if recent_q and recent_q[0] >= "2026-Q2":
            return q[recent_q[0]] / statistics.fmean(qbase), quarter_months(recent_q[0]), "quarterly CPI"
    a = annual.get(iso2, {})
    if a.get("2026") and a.get(BASE_YEAR):
        return a["2026"] / a[BASE_YEAR], [f"2026-{k:02d}" for k in range(1, 10)], "IMF WEO 2026 annual CPI estimate"
    return None, [], ""


def eu_coefficients() -> dict[str, dict[str, float]]:
    """ISO2 -> {year: coefficient, Brussels = 100} for each country's capital duty station."""
    d = json.loads((CACHE / "eurostat-colc-ext" / "prc_colc_ext.json").read_text())
    geo = d["dimension"]["geo"]["category"]["index"]
    time = d["dimension"]["time"]["category"]["index"]
    out: dict[str, dict[str, float]] = {}
    for g, i in geo.items():
        if not g.endswith("_CAP") and g not in ("IL_DEL", "LK_DEL", "CI_DEL", "BJ_DEL", "MM_DEL"):
            continue
        iso2 = {"UK": "GB", "EL": "GR"}.get(g[:2], g[:2])
        for year, j in time.items():
            v = d["value"].get(str(i * len(time) + j))
            if v is not None:
                out.setdefault(iso2, {})[year] = float(v)
    return out


def icp_levels() -> dict[str, dict]:
    """ISO2 -> {'ppp': LCU per USD 2021, 'pli': US = 100 2021} for ICP 2021 economies."""
    d = wb_icp("9260000")
    to2 = iso3_to_iso2()
    us = d["USA"]["PX.WL"]
    out = {}
    for code, v in d.items():
        iso2 = ICP_ALIASES.get(code) or to2.get(code)
        if iso2 and "PPPGlob" in v and "PX.WL" in v:
            out[iso2] = {"ppp": v["PPPGlob"], "pli": 100 * v["PX.WL"] / us}
    return out


def ols(xs: list[list[float]], ys: list[float]) -> tuple[list[float], float]:
    """Least squares with intercept. Returns (coefficients incl. intercept first, residual standard deviation)."""
    rows = [[1.0, *x] for x in xs]
    k = len(rows[0])
    xtx = [[sum(r[i] * r[j] for r in rows) for j in range(k)] for i in range(k)]
    xty = [sum(r[i] * y for r, y in zip(rows, ys)) for i in range(k)]
    # Gaussian elimination
    a = [row[:] + [b] for row, b in zip(xtx, xty)]
    for i in range(k):
        p = max(range(i, k), key=lambda r: abs(a[r][i]))
        a[i], a[p] = a[p], a[i]
        for r in range(k):
            if r != i:
                f = a[r][i] / a[i][i]
                a[r] = [x - f * y for x, y in zip(a[r], a[i])]
    beta = [a[i][k] / a[i][i] for i in range(k)]
    resid = [y - sum(b * x for b, x in zip(beta, r)) for r, y in zip(rows, ys)]
    sd = math.sqrt(sum(e * e for e in resid) / max(1, len(ys) - k))
    return beta, sd


def build() -> tuple[list[dict], dict]:
    icp = icp_levels()
    monthly = imf_cpi("cpi-monthly.xml")
    quarterly = imf_cpi("cpi-quarterly.xml")
    annual = weo("PCPI")
    gdp = weo("NGDPDPC")
    eu = eu_coefficients()
    fx = rates()
    us_monthly = monthly["US"]
    us_base = statistics.fmean(us_monthly[f"{BASE_YEAR}-{k:02d}"] for k in range(1, 13))

    # 1. Carry ICP 2021 forward, over the same months for the country's CPI, the US CPI and the exchange rate.
    now: dict[str, dict] = {}
    for iso2, v in icp.items():
        c = countries().get(iso2)
        if not c or iso2 in NOT_CARRIED:
            continue
        ratio, months, how = cpi_ratio(iso2, monthly, quarterly, annual)
        if ratio is None and c["currency"] in DOLLAR_PEGS:
            # Small economies pegged to the dollar with no CPI series: assume their prices kept pace with US prices.
            now[iso2] = {"pli": v["pli"], "ppp": v["ppp"], "xr": DOLLAR_PEGS[c["currency"]], "xr_period": "fixed peg",
                         "xr_source": "currency peg", "cpi": "no CPI series, so held at its 2021 level relative to the US",
                         "period": "2021", "pli2021": v["pli"], "currency": c["currency"]}
            continue
        if ratio is None:
            continue
        us_ratio = statistics.fmean(us_monthly[k] for k in months) / us_base
        xr, xr_period, xr_source = rate_for_months(fx.get(c["currency"], {"monthly": {}}), months)
        if xr is None:
            continue
        ppp_now = v["ppp"] / REDENOMINATED.get(iso2, 1.0) * ratio / us_ratio
        period = f"{months[0]} to {months[-1]}"
        now[iso2] = {"pli": 100 * ppp_now / xr, "ppp": ppp_now, "xr": xr, "xr_period": xr_period, "xr_source": xr_source,
                     "cpi": how, "period": period, "pli2021": v["pli"], "currency": c["currency"]}

    # 2. Estimate countries outside ICP 2021 from GDP per head, and the EU staff coefficient where one exists.
    us_eu = eu.get("US", {}).get("2026")
    def feats(iso2):
        g = gdp.get(iso2, {}).get("2026") or gdp.get(iso2, {}).get("2025")
        e = eu.get(iso2, {}).get("2026")
        return (math.log(g) if g else None), (math.log(100 * e / us_eu) if e and us_eu else None)
    train_a, train_b = [], []
    for iso2, v in now.items():
        lg, le = feats(iso2)
        if lg is not None:
            train_a.append(([lg], math.log(v["pli"])))
            if le is not None:
                train_b.append(([lg, le], math.log(v["pli"])))
    beta_a, sd_a = ols([x for x, _ in train_a], [y for _, y in train_a])
    beta_b, sd_b = ols([x for x, _ in train_b], [y for _, y in train_b])
    beta_c, sd_c = ols([x[1:] for x, _ in train_b], [y for _, y in train_b])
    model = {"gdp_only": {"beta": beta_a, "sd": sd_a, "n": len(train_a)}, "gdp_and_eu": {"beta": beta_b, "sd": sd_b, "n": len(train_b)},
             "eu_only": {"beta": beta_c, "sd": sd_c, "n": len(train_b)}}

    imputed: dict[str, dict] = {}
    for iso2, c in countries().items():
        if iso2 in now or iso2 in SKIP or iso2 in PARENT or iso2 in NUTS_COUNTRIES or not c["population"]:
            continue
        lg, le = feats(iso2)
        if lg is not None and le is not None:
            pli = math.exp(beta_b[0] + beta_b[1] * lg + beta_b[2] * le)
            how = f"estimated from GDP per head and the EU staff coefficient for its capital (typical error about {math.expm1(sd_b):.0%})"
        elif lg is not None:
            pli = math.exp(beta_a[0] + beta_a[1] * lg)
            how = f"estimated from GDP per head alone (typical error about {math.expm1(sd_a):.0%})"
        elif le is not None:
            pli = math.exp(beta_c[0] + beta_c[1] * le)
            how = f"estimated from the EU staff coefficient for its capital alone, no GDP figure (typical error about {math.expm1(sd_c):.0%})"
        else:
            continue
        imputed[iso2] = {"pli": pli, "how": how, "currency": c["currency"]}
    for iso2, parent in PARENT.items():
        base = now.get(parent) or imputed.get(parent)
        if base and iso2 in countries() and iso2 not in now:
            imputed[iso2] = {"pli": base["pli"], "how": f"taken from {countries()[parent]['name']}, whose currency and prices it shares; no price survey of its own", "currency": countries()[iso2]["currency"]}

    rows = []
    for iso2, v in now.items():
        if iso2 == "PS":
            continue  # the plan's PS covers Israel too; written below from Israel's figures
        code = PLAN_COUNTRY.get(iso2, iso2)
        name = countries()[iso2]["name"]
        note = (f"ICP 2021 price level {v['pli2021']:.1f}, carried forward with {v['cpi']} ({v['period']}); "
                f"PPP {fmt(v['ppp'])} {v['currency']} per US dollar, exchange rate {fmt(v['xr'])} ({v['xr_period']}, {v['xr_source']})")
        if iso2 in NUTS_COUNTRIES:
            note += "; national row for checking against Eurostat"
        if code == "PS":
            name = "Israel and Palestine (figure for Israel)"
            if "PS" in now:
                note += f"; West Bank and Gaza on its own: {now['PS']['pli']:.1f}"
        rows.append({"place_code": code, "amount": f"{v['pli']:.1f}", "currency": "", "unit": "index_us_100", "period": v["period"],
                     "measured_for": f"{name}, whole country, household consumption excluding housing",
                     "source_id": "wb-icp-2021", "note": note})
    for iso2, v in imputed.items():
        if iso2 in ("IL", "PS"):
            continue
        rows.append({"place_code": iso2, "amount": f"{v['pli']:.1f}", "currency": "", "unit": "index_us_100", "period": NOW_LABEL,
                     "measured_for": f"{countries()[iso2]['name']}, whole country (not in ICP 2021)",
                     "source_id": "imf-weo", "note": f"Inferred: {v['how']}."})
    rows += japan_prefectures(now.get("JP"))
    return rows, {"now": now, "imputed": imputed, "model": model, "eu": eu}


def japan_prefectures(japan: dict | None) -> list[dict]:
    """Japan's 47 prefectures: the national level times the Statistics Bureau's regional price index excluding rent."""
    if not japan:
        return []
    from lib import REPO, read_csv
    out = []
    for r in read_csv(REPO / "tools" / "world" / "regional" / "jp-regional-price.curated.csv"):
        index = float(r["index_excluding_rent"])
        out.append({"place_code": r["place_code"], "amount": f"{japan['pli'] * index / 100:.1f}", "currency": "", "unit": "index_us_100",
                    "period": japan["period"], "measured_for": f"{r['prefecture_en']} prefecture, household consumption excluding rent",
                    "source_id": "jp-stat-regional-cpi-2025",
                    "note": f"Japan's level {japan['pli']:.1f} x the Statistics Bureau's 2025 regional difference index excluding rent, {index} (Japan = 100)"})
    return out


if __name__ == "__main__":
    from lib import upsert_sources, write_table

    rows, _ = build()
    write_table("price-level-everyday", rows)
    upsert_sources(SOURCES)
