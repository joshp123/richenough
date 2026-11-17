"""Sweden: SCB's average monthly rent per m2 by municipality (2026), lifted to what a newcomer pays in a newly built flat.

SCB's survey "Hyror i bostadslägenheter" measures the whole rented stock at regulated (bruksvärde) rents. A newcomer to a
city cannot get such a flat without years in a queue. What a newcomer can rent is a newly built flat, whose rent is a
presumption rent (presumtionshyra) set from production cost, so we lift each municipality's stock rent by the ratio of
newly built three-room (3 rum och kök, about 71 m2) to all-sizes all-years rent per m2 in its SCB area class (table BO0406Tab05). Then x 75 m2.
"""

import json

import common as c

SOURCE_ID = "scb-se-hyror"
API = "https://api.scb.se/OV0104/v1/doris/en/ssd/BO/BO0406/BO0406E/"
YEAR = "2026"

SOURCES = [c.source(
    SOURCE_ID, "Statistics Sweden (SCB)",
    "Rent in rented dwellings (Hyror i bostadslägenheter): BO0406Tab01 by municipality, BO0406Tab05 by area class and year of construction",
    "https://www.statistikdatabasen.scb.se/pxweb/en/ssd/START__BO__BO0406__BO0406E/", "CC0 1.0 (SCB open data)", YEAR,
    "Sample survey of landlords' rents, average monthly rent per m2 (SCB's English label 'new rent' means monthly rent). "
    "Stock rents, regulated; newcomer level derived with the newbuild ratio, see note on each row.")]

CLASS_NAMES = {"0010": "Greater Stockholm", "0020": "Greater Gothenburg", "0030": "Greater Malmö",
               "0040": "municipalities over 75,000 inhabitants", "0041": "municipalities under 75,000 inhabitants"}
# The brief's main_towns pick for Gotland is the municipality, which has no GeoNames match; Visby is the town.
MAIN_TOWN_OVERRIDE = {"SE214": ("Visby", "0980")}


def _query(table: str, body: dict, name: str) -> dict:
    path = c.fetch(SOURCE_ID, API + table, name, data=json.dumps(body).encode(),
                   headers={"Content-Type": "application/json"})
    out = {}
    for item in json.loads(path.read_text(encoding="utf-8-sig"))["data"]:
        out[tuple(item["key"])] = None if item["values"][0] in ("..", "-") else float(item["values"][0])
    return out


def rows():
    muni = _query("BO0406Tab01", {"query": [
        {"code": "Region", "selection": {"filter": "all", "values": ["*"]}},
        {"code": "Hyresuppg", "selection": {"filter": "item", "values": ["Mh_kvm"]}},
        {"code": "ContentsCode", "selection": {"filter": "item", "values": ["000000RZ"]}},
        {"code": "Tid", "selection": {"filter": "item", "values": [YEAR]}}], "response": {"format": "json"}}, "tab01.json")
    classes = _query("BO0406Tab05", {"query": [
        {"code": "Region", "selection": {"filter": "item", "values": list(CLASS_NAMES)}},
        {"code": "AntalRum", "selection": {"filter": "item", "values": ["3", "00"]}},
        {"code": "ByggAr", "selection": {"filter": "item", "values": ["6", "7", "00"]}},
        {"code": "Hyresuppg", "selection": {"filter": "item", "values": ["Mh_kvm"]}},
        {"code": "ContentsCode", "selection": {"filter": "item", "values": ["0000013W"]}},
        {"code": "Tid", "selection": {"filter": "item", "values": [YEAR]}}], "response": {"format": "json"}}, "tab05.json")
    # Newbuild three-room rent per m2 over the all-sizes all-years average (the base we hold per municipality).
    # 2021- is suppressed for Greater Gothenburg; 2011-2020 stands in there.
    factor, built = {}, {}
    for k in CLASS_NAMES:
        for era, label in (("7", "2021-"), ("6", "2011-2020")):
            new = classes[(k, "3", era, "Mh_kvm", YEAR)]
            if new:
                factor[k], built[k] = new / classes[(k, "00", "00", "Mh_kvm", YEAR)], label
                break
    rate = {k[0]: v for k, v in muni.items() if v}

    lau = c.lau()
    lau = lau[lau["country"] == "SE"]
    population = dict(zip(lau["lau_code"], lau["population"]))
    names = dict(zip(lau["lau_code"], lau["name"]))

    def area_class(code):
        return {"0180": "0010", "1480": "0020", "1280": "0030"}.get(code, "0040" if population[code] > 75000 else "0041")

    out = []
    for nuts3 in c.regions_in("SE"):
        if nuts3 in MAIN_TOWN_OVERRIDE:
            town, code = MAIN_TOWN_OVERRIDE[nuts3]
            measured = c.city_code("SE", town)
        else:
            top = c.main_towns(nuts3).iloc[0]
            code, town, measured = top["lau_code"], top["name"], top["city_code"]
        cls = area_class(code)
        stock = rate[code]
        amount = stock * factor[cls] * c.TWO_BED_M2
        out.append(c.row(
            c.place(nuts3), round(amount), "SEK", "per_month", YEAR, measured or c.place(nuts3), SOURCE_ID,
            f"Newcomer level for {town}: SCB average stock rent {stock:.0f} SEK/m2/month in the municipality x {factor[cls]:.3f} "
            f"(newbuilt {built[cls]} three-room rent over all-years rent per m2, {CLASS_NAMES[cls]}) x 75 m2. Stock rents are regulated and need a years-long queue; "
            f"newbuild presumption rents are what a newcomer can rent. Likely still below the sublet market in big cities."))
    return out
