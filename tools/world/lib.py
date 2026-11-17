"""Shared readers and writers for the world tables (data/tables/*.world.csv)."""

import csv
import functools
import gzip
import io
import json
import pathlib
import statistics
import xml.etree.ElementTree as ET

REPO = pathlib.Path(__file__).resolve().parents[2]
CACHE = REPO / "cache"
TABLES = REPO / "data" / "tables"
SOURCES_CSV = REPO / "data" / "sources.csv"

TABLE_COLUMNS = ["place_code", "amount", "currency", "unit", "period", "measured_for", "source_id", "note"]
SOURCE_COLUMNS = ["source_id", "publisher", "title", "url", "licence", "retrieved", "period", "note"]

# Countries the Europe agent covers with NUTS or ITL codes (EU, EFTA, UK and the NUTS candidate countries).
NUTS_COUNTRIES = set(
    "AT BE BG CY CZ DE DK EE ES FI FR GR HR HU IE IT LT LU LV MT NL PL PT RO SE SI SK "
    "CH IS LI NO GB AL ME MK RS TR".split()
)

# Countries whose every component the Europe agent prices (NUTS and ITL countries, plus Ukraine and Kosovo).
EUROPE_AGENT = NUTS_COUNTRIES | {"UA", "XK"}

# Places the plan draws differently from ISO: Israel is priced and drawn as PS.
PLAN_COUNTRY = {"IL": "PS"}

# Currencies GeoNames still lists under an old code.
CURRENCY_FIXES = {"VE": "VES", "SL": "SLE", "ZW": "ZWG", "ST": "STN", "MR": "MRU", "HR": "EUR", "BG": "EUR", "CW": "XCG", "SX": "XCG"}


@functools.cache
def countries() -> dict[str, dict]:
    """ISO alpha-2 -> {iso3, name, continent, currency, population}, from GeoNames countryInfo."""
    out = {}
    with open(CACHE / "geonames" / "countryInfo.txt", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#"):
                continue
            r = line.rstrip("\n").split("\t")
            iso2 = r[0]
            out[iso2] = {
                "iso2": iso2,
                "iso3": r[1],
                "name": r[4],
                "continent": r[8],
                "currency": CURRENCY_FIXES.get(iso2, r[10]),
                "population": int(r[7] or 0),
            }
    return out


@functools.cache
def iso3_to_iso2() -> dict[str, str]:
    m = {c["iso3"]: iso2 for iso2, c in countries().items()}
    m["XKX"] = "XK"  # World Bank and IMF code for Kosovo
    m["KOS"] = "XK"
    return m


def imf_sdmx(path: pathlib.Path) -> dict[str, dict[str, float]]:
    """IMF SDMX StructureSpecificData -> {ISO3: {period: value}}."""
    out: dict[str, dict[str, float]] = {}
    for el in ET.parse(path).getroot().iter():
        if el.tag.endswith("Series"):
            series = out.setdefault(el.get("COUNTRY"), {})
            for obs in el:
                value = obs.get("OBS_VALUE")
                if obs.tag.endswith("Obs") and value not in (None, "", "NaN"):
                    series[obs.get("TIME_PERIOD")] = float(value)
    return out


def wb_icp(series: str) -> dict[str, dict[str, float]]:
    """World Bank ICP 2021 API dump -> {ISO3: {classification: value}}."""
    data = json.loads((CACHE / "wb-icp-2021" / f"{series}.json").read_text())
    out: dict[str, dict[str, float]] = {}
    for record in data["source"]["data"]:
        v = {x["concept"]: x["id"] for x in record["variable"]}
        if record["value"] is not None:
            out.setdefault(v["Country"], {})[v["Classification"]] = float(record["value"])
    return out


def wb_wdi(indicator: str) -> dict[str, dict[str, float]]:
    """World Bank WDI API dump -> {ISO3: {year: value}}."""
    data = json.loads((CACHE / "wb-wdi" / f"{indicator}.json").read_text())
    out: dict[str, dict[str, float]] = {}
    for record in data[1]:
        if record["value"] is not None:
            out.setdefault(record["countryiso3code"], {})[record["date"]] = float(record["value"])
    return out


def ilostat(indicator: str) -> list[dict]:
    with gzip.open(CACHE / "ilostat" / f"{indicator}.csv.gz", "rt", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def mean(values):
    values = [v for v in values if v is not None]
    return statistics.fmean(values) if values else None


def fmt(x: float, digits: int = 4) -> str:
    """Round to `digits` significant figures without scientific notation."""
    if x == 0:
        return "0"
    from math import floor, log10

    places = max(0, digits - 1 - floor(log10(abs(x))))
    return f"{round(x, places):.{places}f}"


def write_table(name: str, rows: list[dict]) -> pathlib.Path:
    """Write data/tables/<name>.world.csv, sorted by place code, with the contract's columns."""
    TABLES.mkdir(parents=True, exist_ok=True)
    path = TABLES / f"{name}.world.csv"
    rows = sorted(rows, key=lambda r: (r["place_code"], r.get("currency", ""), r.get("period", "")))
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=TABLE_COLUMNS, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in TABLE_COLUMNS})
    print(f"wrote {path.relative_to(REPO)} ({len(rows)} rows)")
    return path


def upsert_sources(rows: list[dict]) -> None:
    """Add or replace rows in data/sources.csv by source_id, keeping every other agent's rows as they are."""
    existing: list[dict] = []
    if SOURCES_CSV.exists():
        with open(SOURCES_CSV, newline="", encoding="utf-8") as f:
            existing = list(csv.DictReader(f))
    new = {r["source_id"]: r for r in rows}
    merged = [new.pop(r["source_id"]) if r["source_id"] in new else r for r in existing] + list(new.values())
    with open(SOURCES_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=SOURCE_COLUMNS, lineterminator="\n")
        w.writeheader()
        for r in merged:
            w.writerow({k: r.get(k, "") for k in SOURCE_COLUMNS})


def read_csv(path: pathlib.Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def read_text_csv(text: str) -> list[dict]:
    return list(csv.DictReader(io.StringIO(text)))
