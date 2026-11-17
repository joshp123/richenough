"""Turkey: the central bank's (TCMB) median rent per m2 of valued dwellings, by province, 2026 Q3.

TCMB publishes the "Degerlemesi Yapilan Konutlarin Birim Kiralari" (unit rents of valued dwellings) quarterly in EVDS,
from bank valuation reports: the rent a valuer says the flat could be let for now, median per m2 of gross floor area
after trimming extremes. It is a new-let estimate, not the rent of sitting tenants. Provinces with too few valuations
(Ardahan, Bayburt, Bingol, Gumushane, Hakkari, Sirnak, Tunceli) get the median of the provinces that do have a figure
in the same NUTS 2 region. The public EVDS dashboard endpoint needs no key; we call the same endpoint the page uses.
"""

import json

import common as c

SOURCE_ID = "tcmb-ykke"
CHART_URL = "https://evds3.tcmb.gov.tr/igmevdsms-dis/public/charts/portlet/Njk5NDEzNTFjNjAxMWY0MDU2MDdmZjJm"
DATA_URL = "https://evds3.tcmb.gov.tr/igmevdsms-dis/fe"
PERIOD = "2026-Q3"

SOURCES = [c.source(
    SOURCE_ID, "Central Bank of the Republic of Turkey (TCMB)",
    "Valued dwellings' unit rents (Degerlemesi Yapilan Konutlarin Birim Kiralari), quarterly, TL/m2, by province, "
    "EVDS series TP.BK.*",
    "https://evds3.tcmb.gov.tr/tumSeriler/2003/bie_kfe", "TCMB data is free to read; no licence stated (EVDS terms of use apply)",
    PERIOD,
    "Median rent per m2 of gross area from bank valuation reports (the rent a valuer says the flat could be let for), "
    "new-tenant basis. Published from Feb 2026; provinces with too few valuations have no figure.")]


def _series() -> tuple[list[str], list[str]]:
    chart = json.loads(c.fetch(SOURCE_ID, CHART_URL, "chart-unit-rents.json").read_text())
    settings = json.loads(chart["chartSettings"])[0]
    codes = settings["serieCodes"].split("#")
    names = [n.replace(" Konut Birim Kiraları", "") for n in settings["serieNames"].split("#")]
    return codes, names


def _values() -> dict[str, dict[str, float]]:
    codes, _ = _series()
    body = {"type": "json", "series": "-".join(x.replace("_", ".") for x in codes),
            "aggregationTypes": "-".join(["avg"] * len(codes)), "formulas": "-".join(["0"] * len(codes)),
            "startDate": "01-01-2025", "endDate": "01-12-2026", "frequency": "6", "decimalSeperator": ".",
            "decimal": "2", "dateFormat": "0", "lang": "TR", "yon": "", "sira": "", "ozelFormuller": [],
            "groupSeperator": False, "isRaporSayfasi": False}
    path = c.fetch(SOURCE_ID, DATA_URL, "unit-rents.json", data=json.dumps(body).encode(),
                   headers={"Content-Type": "application/json", "Origin": "https://evds3.tcmb.gov.tr",
                            "Referer": "https://evds3.tcmb.gov.tr/"})
    return {item["Tarih"]: item for item in json.loads(path.read_text())["items"]}


def rows():
    codes, names = _series()
    latest = _values()[PERIOD]
    per_m2 = {n: float(latest[code]) for code, n in zip(codes, names) if latest.get(code) not in (None, "")}
    nuts = c.nuts_regions()
    provinces = nuts[(nuts["country"] == "TR") & (nuts["level"] == 3)].set_index("nuts")["name"]
    assert set(provinces) <= set(names), set(provinces) - set(names)
    by_nuts2 = {}
    for code, name in provinces.items():
        if name in per_m2:
            by_nuts2.setdefault(code[:4], []).append(per_m2[name])

    out = []
    for code in c.regions_in("TR"):
        name = provinces[code]
        city = c.city_code("TR", name)
        if name in per_m2:
            out.append(c.row(
                c.place(code), per_m2[name] * c.TWO_BED_M2, "TRY", "per_month", PERIOD, city or c.place(code), SOURCE_ID,
                f"TCMB median rent of valued dwellings in {name} province, {per_m2[name]:.2f} TL/m2 x 75 m2 "
                "(bank valuers' estimate of what the flat would let for today, a new-let basis)."))
        else:
            peers = sorted(by_nuts2[code[:4]])
            mid = (peers[(len(peers) - 1) // 2] + peers[len(peers) // 2]) / 2
            out.append(c.row(
                c.place(code), mid * c.TWO_BED_M2, "TRY", "per_month", PERIOD, c.place(code[:4]), SOURCE_ID,
                f"TCMB publishes no figure for {name} (too few valuations). Median of the {len(peers)} provinces "
                f"with a figure in the same NUTS 2 region {code[:4]}, {mid:.2f} TL/m2 x 75 m2."))
    return out
