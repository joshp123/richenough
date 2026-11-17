"""An expatriate-basket alternative to the everyday price level, US = 100, for every country (reference, not a table).

The EU sets a cost-of-living coefficient for its staff in each capital (Eurostat prc_colc_ext, Brussels = 100,
housing excluded), measured with the basket EU officials actually buy. Rebased to the US average:
    expat level = coefficient / coefficient(Washington DC) x 103.42
where 103.42 is BEA's 2024 price parity for goods and other services in the Washington metro area (the US agent's
row US-11001). Where the EU publishes no coefficient, the expat level is the ICP-based everyday level times the
expat-to-ICP ratio predicted from GDP per head (fitted on the countries that have both).

Written to data/reference/, not data/tables/: the site uses ICP by default; this is the coordinator's alternative.
"""

import csv
import math
import statistics

from lib import PLAN_COUNTRY, REPO, TABLE_COLUMNS, countries
from price_level import build as build_price_level, weo

DC_PRICE_PARITY = 103.42
OUT = REPO / "data" / "reference" / "price-level-everyday-expat.world.csv"


def build() -> list[dict]:
    rows_icp, info = build_price_level()
    icp = {r["place_code"]: float(r["amount"]) for r in rows_icp}
    eu = info["eu"]
    gdp = weo("NGDPDPC")
    dc = eu["US"]["2026"]
    expat = {}
    for iso2, years in eu.items():
        if "2026" in years and iso2 != "US":
            expat[PLAN_COUNTRY.get(iso2, iso2)] = 100 * years["2026"] / dc * DC_PRICE_PARITY / 100
    points = []
    for code, e in expat.items():
        g = gdp.get(code if code != "PS" else "IL", {}).get("2026")
        if code in icp and g:
            points.append((math.log(g), math.log(e / icp[code])))
    mx = statistics.fmean(x for x, _ in points)
    my = statistics.fmean(y for _, y in points)
    slope = sum((x - mx) * (y - my) for x, y in points) / sum((x - mx) ** 2 for x, _ in points)
    intercept = my - slope * mx
    sd = statistics.pstdev([y - intercept - slope * x for x, y in points])
    rows = []
    for code, level in sorted(icp.items()):
        name = "Israel and Palestine (Tel Aviv for the EU figure)" if code == "PS" else countries().get(code, {}).get("name", code)
        if code in expat:
            rows.append({"place_code": code, "amount": f"{expat[code]:.1f}", "currency": "", "unit": "index_us_100", "period": "2026-07",
                         "measured_for": f"{name}, capital city, EU staff basket excluding housing", "source_id": "eurostat-colc-ext",
                         "note": f"EU coefficient {eu[code if code != 'PS' else 'IL']['2026']} (Brussels = 100), Washington DC {dc}; ICP-based everyday level {level:.1f}"})
            continue
        g = gdp.get(code if code != "PS" else "IL", {}).get("2026")
        if not g:
            continue
        ratio = math.exp(intercept + slope * math.log(g))
        rows.append({"place_code": code, "amount": f"{level * ratio:.1f}", "currency": "", "unit": "index_us_100", "period": "2026",
                     "measured_for": f"{name}, whole country, estimated", "source_id": "eurostat-colc-ext",
                     "note": f"Inferred: ICP-based everyday level {level:.1f} x {ratio:.2f}, the expat-to-ICP ratio the EU coefficients show for countries with GDP per head of USD {g:,.0f} (typical error about {math.expm1(sd):.0%})"})
    return rows


if __name__ == "__main__":
    rows = build()
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=TABLE_COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {OUT.relative_to(REPO)} ({len(rows)} rows)")
