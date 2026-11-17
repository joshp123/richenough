"""Price level of everyday spending (household consumption excluding housing), US = 100, for Europe's NUTS 3 regions.

1. Each country's level against the EU average comes from Eurostat's 2025 purchasing power parities (prc_ppp_ind_1,
   COICOP 2018): household final consumption expenditure without "housing, water, electricity, gas and other fuels",
   aggregated from the two published headings with their 2025 expenditure in euro. This is the aggregate the
   World Bank's ICP calls "individual consumption expenditure by households without housing", which the world-data
   agent uses for every other country, so the two maps join at Europe's edge.
2. It is carried from 2025 to July to September 2026 with each country's HICP against the EU's and its exchange
   rate against the euro (Eurostat), the same carry-forward the World Bank uses between benchmarks.
3. Eurostat publishes the US only for whole household consumption, and US housing is dear, so the US level for this
   aggregate is not published. We anchor on the world-data agent's ICP 2021 figures for the same countries (carried
   forward with the IMF's CPIs): the median, over the 37 countries both cover, of their figure over ours. That fixes
   one number, the US price level against the EU, and leaves Eurostat's fresher comparisons between European
   countries as they are.
4. Regions: official sub-national price levels excluding rent where they exist (regional_prices.py: Germany by Kreis,
   Italy, the UK and France by region); elsewhere the national figure, with measured_for set to the country.
"""

import csv
import json
import statistics

import common as c
import regional_prices

PPP_ID = "eurostat-ppp-2025"
HICP_ID = "eurostat-hicp"
FX_ID = "eurostat-exchange-rates"
ONS_CPI_ID = "ons-cpi"
NOW = ["2026-07", "2026-08", "2026-09"]
BASE_YEAR = "2025"

SOURCES = [
    c.source(PPP_ID, "Eurostat", "Purchasing power parities, price level indices, nominal and real expenditures by "
             "analytical categories, based on COICOP 2018 (prc_ppp_ind_1)",
             "https://ec.europa.eu/eurostat/databrowser/view/prc_ppp_ind_1/default/table",
             "CC BY 4.0 (Eurostat reuse policy)", "2025",
             "Eurostat-OECD PPP programme. 2025 values are Eurostat's estimates from the 2024 benchmark. Headings used: "
             "household final consumption expenditure (E011) and housing, water, electricity, gas and other fuels "
             "(A0104); price level index EU27 = 100 and expenditure in euro. UK 2025 lacks A0104, so its housing share "
             "comes from 2020 in prc_ppp_ind (COICOP 1999)."),
    c.source(HICP_ID, "Eurostat", "HICP, monthly index 2025 = 100, all items (prc_hicp_minr)",
             "https://ec.europa.eu/eurostat/databrowser/view/prc_hicp_minr/default/table",
             "CC BY 4.0 (Eurostat reuse policy)", "2025-01 to 2026-09", "Carries 2025 price levels to 2026-Q3."),
    c.source(FX_ID, "Eurostat", "Euro exchange rates, monthly averages (ert_bil_eur_m)",
             "https://ec.europa.eu/eurostat/databrowser/view/ert_bil_eur_m/default/table",
             "CC BY 4.0 (Eurostat reuse policy)", "2025-01 to 2026-09", "National currency per euro."),
    c.source(ONS_CPI_ID, "Office for National Statistics", "CPI index 00: all items 2015 = 100 (series D7BT)",
             "https://www.ons.gov.uk/economy/inflationandpriceindices/timeseries/d7bt/mm23",
             "Open Government Licence v3.0", "2025-01 to 2026-09", "The UK left the HICP; its CPI is the same measure."),
] + regional_prices.SOURCES

CURRENCY = {iso: cur for iso, cur in c.ISO_TO_CURRENCY.items()}
EUROSTAT_GEO = {"GR": "EL", "GB": "UK"}


def _value_map(df, *dims):
    return {tuple(r[d] for d in dims): r["OBS_VALUE"] for _, r in df.iterrows() if r["OBS_VALUE"] == r["OBS_VALUE"]}


def eurostat_levels() -> dict[str, float]:
    """ISO -> 2025 price level of household consumption without housing, EU27 = 100."""
    ppp = c.eurostat("prc_ppp_ind_1", "A.PLI_EU27_2020+EXP_EUR.E011+A0104+A01.", startPeriod="2020")
    v = _value_map(ppp, "indic_ppp", "ppp_cat18", "geo", "TIME_PERIOD")
    out = {}
    for iso in {r for r in c.nuts3()["iso"].unique()} | {"GB"}:
        geo = EUROSTAT_GEO.get(iso, iso)
        try:
            e, pe = v[("EXP_EUR", "E011", geo, BASE_YEAR)], v[("PLI_EU27_2020", "E011", geo, BASE_YEAR)]
        except KeyError:
            continue
        if ("EXP_EUR", "A0104", geo, BASE_YEAR) in v:
            h, ph = v[("EXP_EUR", "A0104", geo, BASE_YEAR)], v[("PLI_EU27_2020", "A0104", geo, BASE_YEAR)]
            out[iso] = (e - h) / (e / pe - h / ph)
        elif iso == "GB":
            old = c.eurostat("prc_ppp_ind", "A.PLI_EU27_2020+EXP_EUR.E011+A0104.UK", startPeriod="2020", endPeriod="2020")
            o = _value_map(old, "na_item", "ppp_cat", "TIME_PERIOD")
            e0, pe0 = o[("EXP_EUR", "E011", "2020")], o[("PLI_EU27_2020", "E011", "2020")]
            h0, ph0 = o[("EXP_EUR", "A0104", "2020")], o[("PLI_EU27_2020", "A0104", "2020")]
            out[iso] = pe * ((e0 - h0) / (e0 / pe0 - h0 / ph0)) / pe0
    return out


def _monthly(df, key_dim):
    out: dict[str, dict[str, float]] = {}
    for _, r in df.iterrows():
        if r["OBS_VALUE"] == r["OBS_VALUE"]:
            out.setdefault(r[key_dim], {})[r["TIME_PERIOD"]] = r["OBS_VALUE"]
    return out


def uk_cpi() -> dict[str, float]:
    path = c.fetch(ONS_CPI_ID, "https://www.ons.gov.uk/economy/inflationandpriceindices/timeseries/d7bt/mm23/data", "d7bt.json")
    data = json.loads(path.read_text())
    months = {"JAN": "01", "FEB": "02", "MAR": "03", "APR": "04", "MAY": "05", "JUN": "06", "JUL": "07", "AUG": "08",
              "SEP": "09", "OCT": "10", "NOV": "11", "DEC": "12"}
    return {f"{m['year']}-{months[m['month'][:3].upper()]}": float(m["value"]) for m in data["months"]}


def carry_factors() -> dict[str, tuple[float, str]]:
    """ISO -> (factor taking a 2025 level against the EU to 2026-Q3, description)."""
    hicp = _monthly(c.eurostat("prc_hicp_minr", "M.I25.TOTAL.", startPeriod="2025-01"), "geo")
    hicp["UK"] = uk_cpi()
    fx = _monthly(c.eurostat("ert_bil_eur_m", "M.AVG.NAC.", startPeriod="2025-01"), "currency")
    year = [f"{BASE_YEAR}-{m:02d}" for m in range(1, 13)]

    def ratio(series):
        return statistics.fmean(series[m] for m in NOW) / statistics.fmean(series[m] for m in year)

    eu = ratio(hicp["EU27_2020"])
    out = {}
    for iso in set(c.nuts3()["iso"]) | {"GB"}:
        geo = EUROSTAT_GEO.get(iso, iso)
        if geo not in hicp or not all(m in hicp[geo] for m in NOW + year):
            continue
        cur = CURRENCY[iso]
        fx_ratio = 1.0 if cur == "EUR" else ratio(fx[cur])
        f = ratio(hicp[geo]) / eu / fx_ratio
        out[iso] = (f, f"prices {ratio(hicp[geo]) - 1:+.1%} against the EU's {eu - 1:+.1%}"
                       + ("" if cur == "EUR" else f", {cur} per euro {fx_ratio - 1:+.1%}"))
    return out


def world_levels() -> dict[str, dict]:
    path = c.TABLES / "price-level-everyday.world.csv"
    with path.open() as f:
        return {r["place_code"]: r for r in csv.DictReader(f)}


def national() -> tuple[dict[str, dict], dict]:
    eu = eurostat_levels()
    carry = carry_factors()
    world = world_levels()
    now = {iso: eu[iso] * carry[iso][0] for iso in eu if iso in carry}
    ratios = {iso: float(world[iso]["amount"]) / now[iso] for iso in now if iso in world}
    k = statistics.median(ratios.values())
    us_against_eu = 100 / k
    out = {}
    for iso, level in now.items():
        out[iso] = {"amount": level * k, "period": "2026-Q3", "measured_for": iso, "source_id": PPP_ID,
                    "note": f"Eurostat 2025 price level of household consumption without housing {eu[iso]:.1f} (EU27 = 100), "
                            f"carried to 2026-Q3 ({carry[iso][1]}): {level:.1f}; divided by the US level for the same "
                            f"aggregate, {us_against_eu:.1f} (EU27 = 100, anchored on the ICP 2021 figures for Europe)."
                            + (f" ICP-based figure for comparison: {float(world[iso]['amount']):.1f}." if iso in world else "")}
    # Countries outside Eurostat's PPP programme.
    if "CH" in out:
        out["LI"] = dict(out["CH"], measured_for="CH",
                         note="Switzerland's level: Liechtenstein shares its currency, customs union and prices and has no PPP of its own. " + out["CH"]["note"])
    for iso in ("XK", "UA"):
        if iso in world:
            w = world[iso]
            out[iso] = {"amount": float(w["amount"]), "period": w["period"], "measured_for": iso, "source_id": w["source_id"],
                        "note": f"Not in Eurostat's PPP programme; the world-data agent's figure: {w['measured_for']}. {w['note']}"}
    return out, {"k": k, "us_against_eu": us_against_eu, "ratios": ratios}


def rows():
    levels, _ = national()
    regional: dict[str, dict] = {}
    for r in regional_prices.relative_levels():
        regional[r["nuts"]] = r
    out = []
    for region in c.nuts3().itertuples():
        nat = levels.get(region.iso)
        if not nat:
            continue
        match = next((regional[region.nuts[:n]] for n in (5, 4, 3) if region.nuts[:n] in regional), None)
        if match:
            out.append(c.row(c.place(region.nuts), nat["amount"] * match["relative"], "", "index_us_100", nat["period"],
                             c.place(match["nuts"]), match["source_id"],
                             f"National {nat['amount']:.1f} x {match['relative']:.3f} for {match['nuts']}. {match['note']} "
                             f"National: {nat['note']}"))
        else:
            out.append(c.row(c.place(region.nuts), nat["amount"], "", "index_us_100", nat["period"], nat["measured_for"],
                             nat["source_id"], f"National figure; no official price level below the country. {nat['note']}"))
    return out


if __name__ == "__main__":
    levels, info = national()
    print(f"anchor: median ICP/Eurostat ratio {info['k']:.4f}, US level for this aggregate {info['us_against_eu']:.1f} (EU27 = 100)")
    for iso in sorted(levels):
        r = info["ratios"].get(iso)
        print(f"{iso} {levels[iso]['amount']:6.1f}  ICP/ours {r:.3f}" if r else f"{iso} {levels[iso]['amount']:6.1f}")
