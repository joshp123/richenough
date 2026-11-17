"""Switzerland: Federal Statistical Office (BFS) structural survey, 2024, average net rent of a 3-room flat.

A Swiss two-bed is a 3-room flat (3 Zimmer, BFS count: rooms including a kitchen of 4 m2 or more, so roughly 65 to
85 m2). Net rent, without heating and service charges (Nebenkosten), cooperatives included.

New-let level, by canton: the canton's average 3-room rent (all tenancies) x the canton's new-tenancy premium. The
premium is the national 3-room premium of rents for tenancies under two years in older flats (BFS table 09.03.03.65)
times the canton's own premium (all-room new-tenancy rent / all-room average, table 09.03.03.64) relative to the
national one, so cantons with big gaps between sitting and new tenants (Geneva) show it. Where BFS publishes the
3-room rent of tenancies under two years for the cantonal capital itself (Zurich, Geneva, Basel, Lausanne, Bern:
table 09.03.03.67), we use that and measure the city.
"""

import pandas as pd

import common as c

SOURCE_ID = "bfs-mietpreise"
PAGE = "https://www.bfs.admin.ch/asset/de/je-d-09.03.03.{n}"
DAM = "https://dam-api.bfs.admin.ch/hub/api/dam/assets/{id}/master"
FILES = {"kanton_zimmer": 36398431, "kanton_bezugsdauer": 36398542, "gemtyp_zimmer_bezug": 36398546,
         "staedte_zimmer_bezug": 36398555}

SOURCES = [c.source(
    SOURCE_ID, "Federal Statistical Office (BFS), Switzerland",
    "Durchschnittlicher Mietpreis (structural survey 2024): by number of rooms and canton (T 09.03.03.01), by length of "
    "tenancy and canton (.64), by rooms, municipality type and length of tenancy (.65), by rooms and length of tenancy for "
    "the largest cities (.67)",
    "https://www.bfs.admin.ch/bfs/de/home/statistiken/bau-wohnungswesen/wohnungen/mietpreise.html",
    "OGD, free use with source attribution (opendata.swiss terms: BY)", "2024",
    "Monthly net rent (no heating or service charges) of rented and cooperative flats, self-reported in the structural survey "
    "(sample of about 200,000 people a year, pooled with earlier years).")]

# BFS canton name (as in the tables) -> NUTS 3
CANTONS = {
    "Zürich": "CH040", "Bern": "CH021", "Luzern": "CH061", "Uri": "CH062", "Schwyz": "CH063", "Obwalden": "CH064",
    "Nidwalden": "CH065", "Glarus": "CH051", "Zug": "CH066", "Freiburg": "CH022", "Solothurn": "CH023",
    "Basel-Stadt": "CH031", "Basel-Landschaft": "CH032", "Schaffhausen": "CH052", "Appenzell A.Rh.": "CH053",
    "Appenzell I.Rh.": "CH054", "St.Gallen": "CH055", "Graubünden": "CH056", "Aargau": "CH033", "Thurgau": "CH057",
    "Tessin": "CH070", "Waadt": "CH011", "Wallis": "CH012", "Neuenburg": "CH024", "Genf": "CH013", "Jura": "CH025",
}
CAPITALS = {"CH040": "Zürich", "CH021": "Bern", "CH061": "Luzern", "CH062": "Altdorf (UR)", "CH063": "Schwyz",
            "CH064": "Sarnen", "CH065": "Stans", "CH051": "Glarus", "CH066": "Zug", "CH022": "Fribourg",
            "CH023": "Solothurn", "CH031": "Basel", "CH032": "Liestal", "CH052": "Schaffhausen", "CH053": "Herisau",
            "CH054": "Appenzell", "CH055": "St. Gallen", "CH056": "Chur", "CH033": "Aarau", "CH057": "Frauenfeld",
            "CH070": "Bellinzona", "CH011": "Lausanne", "CH012": "Sion", "CH024": "Neuchâtel", "CH013": "Genève",
            "CH025": "Delémont"}
# the largest-city table's names -> NUTS 3 of the canton whose capital they are
CITY_TABLE = {"Zürich": "CH040", "Genf": "CH013", "Basel": "CH031", "Lausanne": "CH011", "Bern": "CH021"}


def _sheet(name: str) -> pd.DataFrame:
    path = c.fetch(SOURCE_ID, DAM.format(id=FILES[name]), f"{name}.xlsx")
    return pd.read_excel(path, sheet_name="2024", header=None)


def _num(value) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def rows():
    rooms = _sheet("kanton_zimmer")      # col 1 total, col 7 = 3 rooms
    tenure = _sheet("kanton_bezugsdauer")  # col 1 total, col 5 = new tenancy of a flat more than two years old
    types = _sheet("gemtyp_zimmer_bezug")
    cities = _sheet("staedte_zimmer_bezug")

    three = {r[0]: _num(r[7]) for r in rooms.itertuples(index=False) if r[0] in CANTONS or r[0] == "Schweiz"}
    ratio = {r[0]: _num(r[5]) / _num(r[1]) for r in tenure.itertuples(index=False) if r[0] in CANTONS or r[0] == "Schweiz"}
    # national 3-room: tenancies under two years in older flats / all tenancies (the "3 Zimmer" total line of table .65)
    line = next(r for r in types.itertuples(index=False) if r[0] == "3 Zimmer")
    national_three = _num(line[5]) / _num(line[1])

    # largest cities: 3-room total and tenancies under two years
    city_rent, current = {}, None
    for r in cities.itertuples(index=False):
        if r[0] in ("Schweiz", *CITY_TABLE):
            current = r[0]
        elif r[0] == "3 Zimmer" and current in CITY_TABLE:
            city_rent[current] = (_num(r[1]), _num(r[3]))

    out = []
    for name, nuts in CANTONS.items():
        town = CAPITALS[nuts]
        if (city := next((k for k, v in CITY_TABLE.items() if v == nuts), None)):
            total, new = city_rent[city]
            out.append(c.row(
                c.place(nuts), new, "CHF", "per_month", "2024", c.city_code("CH", town), SOURCE_ID,
                f"Average net rent of a 3-room flat let to its tenants less than two years ago in the city of {town} "
                f"(3 Zimmer, no service charges; all 3-room tenancies in the city average CHF {total:.0f})."))
            continue
        premium = national_three * ratio[name] / ratio["Schweiz"]
        out.append(c.row(
            c.place(nuts), round(three[name] * premium), "CHF", "per_month", "2024", c.place(nuts), SOURCE_ID,
            f"Canton-wide, not the capital: average net rent of a 3-room flat in canton {name} (CHF {three[name]:.0f}, no service "
            f"charges) x {premium:.3f} new-tenancy premium (national 3-room {national_three:.3f} x canton relative "
            f"{ratio[name] / ratio['Schweiz']:.3f}). Capital: {town}."))
    return out
