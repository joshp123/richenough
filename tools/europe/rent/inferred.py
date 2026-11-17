"""Inferred rents for the regions no source covers, so the map has a labelled national estimate instead of a hole.

For each country with measured rows, its typical figure is the median of its regions measured locally (rows whose
measured_for is a town or the region itself), in euro. log(typical rent) is fitted on log(price level of everyday
spending, US = 100) and log(GDP per head) across those countries; each country that has no measured row, or each
region left without one, gets its country's prediction, one figure for the whole country (no invented variation
inside it), with measured_for set to the country and a note that starts "Inferred". The world-data agent does the
same for countries outside Europe.
Only countries measured in at least three regions, or in half of them, train the fit, so a country measured only in
its capital does not pass the capital's rent off as typical.
"""

import csv
import math
import statistics

import common as c
import price_level

GDP_ID = "eurostat-gdp-per-head"
SOURCES = [c.source(GDP_ID, "Eurostat", "Gross domestic product at market prices, euro per head (nama_10_pc)",
                    "https://ec.europa.eu/eurostat/databrowser/view/nama_10_pc/default/table",
                    "CC BY 4.0 (Eurostat reuse policy)", "2024",
                    "Used only to infer rents for countries with no rent source.")]

def _fx() -> dict[str, float]:
    """Units of each currency per euro, from the world table's units per US dollar."""
    with (c.TABLES / "exchange-rates.world.csv").open() as f:
        per_usd = {r["currency"]: float(r["amount"]) for r in csv.DictReader(f)}
    return {cur: v / per_usd["EUR"] for cur, v in per_usd.items()}


def _gdp() -> dict[str, float]:
    df = c.eurostat("nama_10_pc", "A.CP_EUR_HAB.B1GQ.", startPeriod="2024", endPeriod="2024")
    return {{"EL": "GR", "UK": "GB"}.get(g, g): v for g, v in zip(df["geo"], df["OBS_VALUE"]) if v == v}


def _ols(xs, ys):
    """Least squares with intercept; returns coefficients and the residual standard deviation."""
    n, k = len(ys), len(xs[0]) + 1
    rows = [[1.0, *x] for x in xs]
    a = [[sum(r[i] * r[j] for r in rows) for j in range(k)] + [sum(r[i] * y for r, y in zip(rows, ys))] for i in range(k)]
    for i in range(k):
        p = max(range(i, k), key=lambda r: abs(a[r][i]))
        a[i], a[p] = a[p], a[i]
        for r in range(k):
            if r != i:
                f = a[r][i] / a[i][i]
                a[r] = [x - f * y for x, y in zip(a[r], a[i])]
    beta = [a[i][k] / a[i][i] for i in range(k)]
    resid = [y - sum(b * x for b, x in zip(beta, r)) for r, y in zip(rows, ys)]
    return beta, math.sqrt(sum(e * e for e in resid) / (n - k))


def fill(existing: list[dict]) -> list[dict]:
    covered = {r["place_code"] for r in existing}
    fx = _fx()
    levels, _ = price_level.national()
    gdp = _gdp()
    regions = c.nuts3()
    iso_of = dict(zip(regions["nuts"].map(c.place), regions["iso"]))

    local: dict[str, list[float]] = {}
    for r in existing:
        if r["measured_for"].startswith("CITY-") or r["measured_for"] == r["place_code"]:
            local.setdefault(iso_of[r["place_code"]], []).append(r["amount"] / fx[r["currency"]])
    size = regions.groupby("iso").size()
    typical = {iso: statistics.median(v) for iso, v in local.items() if len(v) >= 3 or len(v) >= size[iso] / 2}
    train = [iso for iso in typical if iso in levels and iso in gdp]
    beta, sd = _ols([[math.log(levels[i]["amount"]), math.log(gdp[i])] for i in train], [math.log(typical[i]) for i in train])
    beta_p, sd_p = _ols([[math.log(levels[i]["amount"])] for i in train], [math.log(typical[i]) for i in train])

    out = []
    for region in regions.itertuples():
        code = c.place(region.nuts)
        if code in covered:
            continue
        iso = region.iso
        if iso not in levels or iso == "FR":  # Mayotte is too unlike metropolitan France to infer from it
            continue
        pl = levels[iso]["amount"]
        if iso in gdp:
            eur = math.exp(beta[0] + beta[1] * math.log(pl) + beta[2] * math.log(gdp[iso]))
            how = (f"price level {pl:.1f} (US = 100) and GDP per head EUR {gdp[iso]:,.0f} (2024), fitted on {len(train)} "
                   f"European countries' typical measured rents (typical error about {math.expm1(sd):.0%})")
        else:
            eur = math.exp(beta_p[0] + beta_p[1] * math.log(pl))
            how = (f"price level {pl:.1f} (US = 100) alone, no Eurostat GDP figure, fitted on {len(train)} European "
                   f"countries' typical measured rents (typical error about {math.expm1(sd_p):.0%})")
        currency = c.ISO_TO_CURRENCY[iso]
        out.append(c.row(code, eur * fx[currency], currency, "per_month", "2026", iso, GDP_ID,
                         f"Inferred, not measured: no rent source reached for this region. Estimated for the whole "
                         f"country from {how}. The typical figure is the median of a country's regions' main towns, "
                         f"so a capital will be dearer than this."))
    return out
