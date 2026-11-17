"""Rent of a two-bed flat at the going rate for a new let, every country outside the US and Europe.

1. Runs each region's build under tools/world/rent/ (each reads its own cache/<source_id>/ and downloads what is
   missing) and reads the rows: official statistics, registries and portal data, with notes per region in
   tools/world/rent/*.notes.md.
2. Keeps first-level region rows (ISO 3166-2, as Natural Earth codes them, since the map draws Natural Earth shapes)
   only for countries whose data covers their regions honestly (REGION_COUNTRIES). Elsewhere a lone capital-region
   row becomes a city dot, so a country is never coloured region by region on the strength of its capital alone.
3. Every country with no row gets one estimated from GDP per head and its everyday price level, fitted on the
   countries that have a measured figure; such rows say "Inferred".
"""

import csv
import io
import json
import math
import re
import statistics
import subprocess
import sys

from exchange_rates import rates
from lib import NUTS_COUNTRIES, REPO, countries, fmt, read_csv
from places import city_code
from price_level import weo

RENT = REPO / "tools" / "world" / "rent"
NE_ADMIN1 = REPO / "cache" / "map" / "ne_10m_admin_1_states_provinces.geojson"

# Countries the map should colour by first-level region from these rows (see .agent/research/world.md).
REGION_COUNTRIES = {"CA", "AU", "NZ", "JP", "KR", "CN", "TW", "KZ", "RU", "BR"}
# Covered by the Europe agent, or drawn as part of another country.
NOT_MINE = NUTS_COUNTRIES | {"UA", "XK", "US", "PR", "IL"}

# Region codes in the sources that Natural Earth spells differently, or that are newer than its shapes.
NE_CODE = {"TW-NWT": "TW-TPQ", "KZ-TUR": "KZ-YUZ", "ZA-GP": "ZA-GT", "ZA-KZN": "ZA-NL"}
# Region rows that are really one city: written as that city's dot (name, country) when the country is not drawn by region.
REGION_CITY = {
    "AE-AZ": ("Abu Dhabi", "AE"), "UZ-TK": ("Tashkent", "UZ"), "AZ-BA": ("Baku", "AZ"), "KG-GB": ("Bishkek", "KG"),
    "MD-CU": ("Chisinau", "MD"), "SA-01": ("Riyadh", "SA"), "OM-MA": ("Muscat", "OM"), "MN-1": ("Ulan Bator", "MN"),
    "KZ-SHY": ("Shymkent", "KZ"), "KZ-ALM": ("Qonayev", "KZ"), "KZ-ABA": ("Semey", "KZ"), "KZ-ZHE": ("Taldykorgan", "KZ"),
}
# Region rows dropped: the country row already carries the same figure, or Natural Earth has no such shape.
DROP = {"AE-DU", "ID-BA"}

# How to rebuild each region's rows: (region, commands, kind, add the region's curated CSV).
# "table" builds write <region>.table.csv (curated rows included); "stdout" builds print CSV rows.
UV = ["uv", "run", "--quiet"]
BUILDS = [
    ("canada-australia-nz", [UV + ["tools/world/rent/canada-australia-nz-build.py"]], "table", False),
    ("east-asia", [UV + ["tools/world/rent/east-asia-build.py"]], "table", False),
    ("mena-eurasia", [UV + ["tools/world/rent/mena-eurasia-build.py"]], "stdout", False),
    ("south-southeast-asia", [[sys.executable, "-I", "tools/world/rent/south-southeast-asia.py"]], "stdout", True),
    ("sub-saharan-africa", [[sys.executable, "-I", "tools/world/rent/sub-saharan-africa.py"]], "table", False),
    ("latin-america", [UV + [f"tools/world/rent/latin-america-{name}.py"] for name in ("fipezap", "aguila", "listings", "encuentra24-archive")], "stdout", True),
]


def natural_earth_codes() -> set[str]:
    d = json.loads(NE_ADMIN1.read_text())
    return {f["properties"]["iso_3166_2"] for f in d["features"]}


def region_rows() -> list[dict]:
    rows = []
    for region, commands, kind, add_curated in BUILDS:
        got = []
        for command in commands:
            out = subprocess.run(command, cwd=REPO, capture_output=True, text=True)
            if out.returncode != 0:
                raise RuntimeError(f"{region} build failed ({command[-1]}):\n{out.stderr[-2000:]}")
            if kind == "stdout":
                got += list(csv.DictReader(io.StringIO(out.stdout)))
        if kind == "table":
            got = read_csv(RENT / f"{region}.table.csv")
        if add_curated:
            got += read_csv(RENT / f"{region}.curated.csv")
        for r in got:
            r["_region"] = region
        rows += got
    return rows


def region_sources() -> list[dict]:
    seen: dict[str, dict] = {}
    for path in sorted(RENT.glob("*.sources*.csv")):
        for r in read_csv(path):
            seen.setdefault(r["source_id"], r)
    for command in (["uv", "run", "--quiet", "tools/world/rent/mena-eurasia-build.py", "--sources"],
                    [sys.executable, "-I", "tools/world/rent/sub-saharan-africa.py", "--sources"]):
        out = subprocess.run(command, cwd=REPO, capture_output=True, text=True, check=True)
        for r in csv.DictReader(io.StringIO(out.stdout)):
            seen.setdefault(r["source_id"], r)
    # Scripts that keep their sources in a SOURCES list rather than a CSV (some need openpyxl to import).
    loader = ("import csv, importlib.util, sys\n"
              "w = csv.DictWriter(sys.stdout, ['source_id','publisher','title','url','licence','retrieved','period','note'], extrasaction='ignore')\n"
              "w.writeheader()\n"
              "for path in sys.argv[1:]:\n"
              "    spec = importlib.util.spec_from_file_location('m', path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)\n"
              "    w.writerows(m.SOURCES)\n")
    scripts = [str(RENT / "south-southeast-asia.py")] + [str(p) for p in sorted(RENT.glob("latin-america-*.py"))]
    out = subprocess.run(["uv", "run", "--quiet", "--with", "openpyxl", "python3", "-c", loader, *scripts], cwd=REPO, capture_output=True, text=True, check=True)
    for r in csv.DictReader(io.StringIO(out.stdout)):
        seen.setdefault(r["source_id"], r)
    return list(seen.values())


def build() -> tuple[list[dict], dict]:
    ne = natural_earth_codes()
    raw = region_rows()
    kept: dict[str, dict] = {}
    dropped = []

    def keep(code: str, r: dict, why: str = "") -> None:
        if code in kept:
            dropped.append((code, r["_region"], f"duplicate of {kept[code]['_region']}"))
            return
        kept[code] = {**r, "place_code": code}

    for r in raw:
        code = r["place_code"].strip()
        if r["unit"] != "per_month" or not r["amount"]:
            dropped.append((code, r["_region"], f"unit {r['unit']}"))
            continue
        if code.startswith("CITY-"):
            keep(code, r)
            continue
        country = code[:2]
        if country in NOT_MINE:
            dropped.append((code, r["_region"], "covered elsewhere or drawn as part of another country"))
            continue
        if "-" not in code:
            keep(code, r)
            continue
        code = NE_CODE.get(code, code)
        if code in DROP:
            dropped.append((code, r["_region"], "same figure as the country row"))
        elif country in REGION_COUNTRIES and code in ne:
            keep(code, r)
        elif code in REGION_CITY or r["place_code"] in REGION_CITY:
            name, iso2 = REGION_CITY.get(code) or REGION_CITY[r["place_code"]]
            try:
                keep(city_code(name, iso2), {**r, "note": r["note"] + f" (written as the city; the source labels it {r['place_code']})"})
            except KeyError:
                dropped.append((code, r["_region"], f"no GeoNames city {name}"))
        else:
            dropped.append((code, r["_region"], "region code for a country not drawn by region, or not a Natural Earth shape"))

    # Australia: Victoria and Western Australia from their capitals' rows; the country from the median of states.
    for state, city in (("AU-VIC", "Melbourne"), ("AU-WA", "Perth")):
        c = city_code(city, "AU")
        if state not in kept and c in kept:
            kept[state] = {**kept[c], "place_code": state, "measured_for": f"{city} (used for the state): " + kept[c]["measured_for"],
                           "note": kept[c]["note"] + f". Written for {state} from {city}'s row: no state-wide figure"}
    if "AU" not in kept:
        states = [kept[s] for s in ("AU-NSW", "AU-VIC", "AU-QLD", "AU-WA", "AU-SA", "AU-TAS") if s in kept]
        mid = statistics.median(float(s["amount"]) for s in states)
        kept["AU"] = {**states[0], "place_code": "AU", "amount": fmt(mid, 4), "measured_for": "Australia: median of the six states' figures",
                      "note": "Median of " + ", ".join(f"{s['place_code']} {s['amount']}" for s in states) + " AUD a month; no national two-bed figure is published",
                      "_region": "canada-australia-nz"}

    # South Africa: PayProp's national row averages every dwelling size on existing leases; use the main cities' two-beds.
    za_cities = [kept[c] for c in (city_code(n, "ZA") for n in ("Cape Town", "Johannesburg", "Pretoria", "Durban")) if c in kept]
    if za_cities:
        mid = statistics.median(float(c["amount"]) for c in za_cities)
        payprop = kept.get("ZA", {}).get("amount", "")
        kept["ZA"] = {**za_cities[0], "place_code": "ZA", "amount": fmt(mid, 4), "measured_for": "South Africa: median of Cape Town, Johannesburg, Pretoria and Durban two-bed asking rents",
                      "note": "Median of " + ", ".join(f"{c['measured_for'].split(',')[0]} {c['amount']}" for c in za_cities)
                              + f" ZAR a month (Property24 asking rents, 65-95 m2). PayProp's national average rent paid, all dwelling sizes, is {payprop}",
                      "_region": "sub-saharan-africa"}
    return list(kept.values()), {"dropped": dropped}


def add_inferred(rows: list[dict]) -> list[dict]:
    """A row for every country without one: the main city's figure if there is a city row, else a GDP and price-level model."""
    fx = rates()
    gdp = weo("NGDPDPC")
    price_level = {r["place_code"]: float(r["amount"]) for r in read_csv(REPO / "data" / "tables" / "price-level-everyday.world.csv")}

    def usd(r):
        cur = r["currency"]
        if cur == "USD":
            return float(r["amount"])
        return float(r["amount"]) / fx[cur]["monthly"][max(fx[cur]["monthly"])]

    have = {r["place_code"] for r in rows}
    # Train on each country's largest measured city: the same concept everywhere (a main-city two-bed), unlike
    # country rows, which mix national averages with main-city figures.
    population, country_of = {}, {}
    with open(REPO / "cache" / "geonames" / "cities15000.txt", encoding="utf-8") as f:
        for line in f:
            x = line.split("\t")
            population["CITY-" + x[0]] = int(x[14] or 0)
            country_of["CITY-" + x[0]] = x[8]
    main_city: dict[str, dict] = {}
    for r in rows:
        code = r["place_code"]
        if code in country_of and "Inferred" not in r["note"]:
            iso2 = "PS" if country_of[code] == "IL" else country_of[code]
            if iso2 not in main_city or population[code] > population[main_city[iso2]["place_code"]]:
                main_city[iso2] = r
    points = []
    for iso2, r in main_city.items():
        g = gdp.get("IL" if iso2 == "PS" else iso2, {}).get("2026")
        if g and iso2 in price_level:
            points.append(([math.log(g), math.log(price_level[iso2])], math.log(usd(r))))
    from price_level import ols
    beta, sd = ols([x for x, _ in points], [y for _, y in points])
    out = list(rows)
    for iso2, c in sorted(countries().items()):
        if iso2 in have or iso2 in NOT_MINE or iso2 in ("AQ", "PS") or not c["population"]:
            continue
        g = gdp.get(iso2, {}).get("2026")
        if not g or iso2 not in price_level or c["currency"] not in fx or not fx[c["currency"]]["monthly"]:
            continue
        estimate = math.exp(beta[0] + beta[1] * math.log(g) + beta[2] * math.log(price_level[iso2]))
        local = estimate * fx[c["currency"]]["monthly"][max(fx[c["currency"]]["monthly"])]
        out.append({"place_code": iso2, "amount": fmt(local, 3), "currency": c["currency"], "unit": "per_month", "period": "2026",
                    "measured_for": f"{c['name']}, main city, estimated", "source_id": "imf-weo",
                    "note": f"Inferred, not measured: no published two-bed rent found. Estimated from GDP per head (USD {g:,.0f}) and the everyday price level "
                            f"({price_level[iso2]:.0f}), fitted on the main-city figures of {len(points)} countries (typical error about {math.expm1(sd):.0%})",
                    "_region": "model"})
    return out


REGION_TOKEN = re.compile(r"\b([A-Z]{2})-([A-Z0-9]{1,3})\b")


def scrub(text: str, ne: set[str]) -> str:
    """The map builder draws a country by region if any table text names one of its region codes, so codes of countries
    not drawn by region are written with a non-breaking hyphen in notes."""
    return REGION_TOKEN.sub(lambda m: m.group(0) if m.group(1) in REGION_COUNTRIES or m.group(0) not in ne else f"{m.group(1)}‑{m.group(2)}", text)


if __name__ == "__main__":
    from lib import upsert_sources, write_table

    rows, info = build()
    rows = add_inferred(rows)
    ne = natural_earth_codes()
    for r in rows:
        r["note"] = scrub(r.get("note", ""), ne)
        r["measured_for"] = scrub(r.get("measured_for", ""), ne)
    write_table("rent-two-bedroom", rows)
    upsert_sources(region_sources())
    for d in info["dropped"]:
        print("dropped", *d)
