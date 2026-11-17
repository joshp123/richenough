"""Finland: Statistics Finland's average rent per m2 of new rental contracts, three-room flats and larger, by municipality, 2026.

Table 15fa (Rents of dwellings): for each municipality it gives the average rent per m2 of tenancies agreed in the quarter
(a separate series from rents of sitting tenants), non-subsidised dwellings, by number of rooms. A two-bed is a three-room
flat (kolmio, living room plus two rooms), so we take 'three-room flat+', pooled over 2026Q1 to Q3 (weighted by contracts)
to steady the small towns, times 75 m2.
"""

import csv
import io
import json

import common as c

SOURCE_ID = "statfi-fi-vuokrat"
URL = "https://pxdata.stat.fi/PxWeb/api/v1/en/StatFin/asvu/15fa.px"
QUARTERS = ["2026Q1", "2026Q2", "2026Q3"]
MIN_CONTRACTS = 40

SOURCES = [c.source(
    SOURCE_ID, "Statistics Finland",
    "Rents of dwellings: Rent index and average rents per square metre, quarterly (table 15fa), new rental contracts",
    "https://pxdata.stat.fi/PxWeb/pxweb/en/StatFin/StatFin__asvu/", "CC BY 4.0", "2026Q1-2026Q3",
    "Average rent per m2 of new tenancy agreements, non-subsidised dwellings, from the rent register data of the Finnish "
    "Tax Administration and Kela; the number of contracts is published with each figure.")]


def _table() -> dict:
    body = {"query": [
        {"code": "alue_44_20260101", "selection": {"filter": "all", "values": ["*"]}},
        {"code": "rahoitus_2_20260101", "selection": {"filter": "item", "values": ["1"]}},
        {"code": "huoneluku_5_20260101", "selection": {"filter": "all", "values": ["*"]}},
        {"code": "timeperiod_q", "selection": {"filter": "item", "values": QUARTERS}},
        {"code": "contentscode", "selection": {"filter": "item", "values": ["asvu_keskineliovuokra_u", "asvu_keskineliovuokra_u_lkm"]}}],
        "response": {"format": "csv"}}
    path = c.fetch(SOURCE_ID, URL, "15fa-new-contracts-2026.csv", data=json.dumps(body).encode(),
                   headers={"Content-Type": "application/json"})
    out = {}
    for area, _, rooms, quarter, rent, n in list(csv.reader(io.StringIO(path.read_text(encoding="utf-8-sig"))))[1:]:
        if rent.replace(".", "", 1).isdigit():
            out[(area, rooms, quarter)] = (float(rent), int(n))
    return out


def _pooled(table: dict, area: str, rooms: str):
    """Contract-weighted average rent per m2 over the quarters, and the number of contracts."""
    obs = [table[(area, rooms, q)] for q in QUARTERS if (area, rooms, q) in table]
    n = sum(k for _, k in obs)
    return (sum(r * k for r, k in obs) / n, n) if n else (None, 0)


def rows():
    table = _table()
    big, total = "Three-room flat+", "Total"
    # Ratio of three-room-plus to all-size rents nationally, for towns too small to publish enough three-room contracts.
    ratio = _pooled(table, "Whole country", big)[0] / _pooled(table, "Whole country", total)[0]
    out = []
    for nuts3 in c.regions_in("FI"):
        top = c.main_towns(nuts3).iloc[0]
        town = top["name"]
        rent, n = _pooled(table, town, big)
        if n >= MIN_CONTRACTS:
            note = f"Average rent per m2 of new contracts in {town}, three-room flat or larger, pooled 2026Q1-Q3 ({n} contracts): {rent:.2f} EUR/m2 x 75 m2."
        else:
            all_sizes, n_all = _pooled(table, town, total)
            if not n_all:
                continue
            rent = all_sizes * ratio
            note = (f"Only {n} three-room contracts in {town}, so the all-size average of new contracts, {all_sizes:.2f} EUR/m2 "
                    f"({n_all} contracts), x {ratio:.3f} (national three-room-plus over all-size) = {rent:.2f} EUR/m2, x 75 m2.")
        out.append(c.row(c.place(nuts3), round(rent * c.TWO_BED_M2), "EUR", "per_month", "2026Q1-Q3",
                         top["city_code"] or c.place(nuts3), SOURCE_ID, note))
    # Åland (FI200) is not in the table; give it the national figure for the rest of the country outside Greater Helsinki.
    rent, n = _pooled(table, "Whole country excluding Greater Helsinki", big)
    out.append(c.row(c.place("FI200"), round(rent * c.TWO_BED_M2), "EUR", "per_month", "2026Q1-Q3", "FI", SOURCE_ID,
                     f"Åland is not in the statistic. Figure is Finland outside Greater Helsinki, three-room flat or larger, new contracts, "
                     f"{rent:.2f} EUR/m2 x 75 m2; not measured in Åland."))
    return out
