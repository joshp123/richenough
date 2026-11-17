"""Shared helpers for Europe's tables: downloads, the NUTS 3 list, LAU lookups, city ids and rows.

Every component module (rent/<cc>.py, price_level.py, ...) exposes SOURCES (rows for data/sources.csv)
and rows() (rows for its table). build.py collects and writes them.
"""

from __future__ import annotations

import csv
import functools
import io
import re
import time
import unicodedata
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / "cache"
TABLES = ROOT / "data" / "tables"

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"

# NUTS uses EL for Greece and the UK uses ITL codes (TL...); the plan's country codes are ISO 3166-1.
NUTS_TO_ISO = {"EL": "GR", "TL": "GB", "UK": "GB"}
ISO_TO_CURRENCY = {
    "AL": "ALL", "AT": "EUR", "BE": "EUR", "BG": "EUR", "CH": "CHF", "CY": "EUR", "CZ": "CZK", "DE": "EUR",
    "DK": "DKK", "EE": "EUR", "GR": "EUR", "ES": "EUR", "FI": "EUR", "FR": "EUR", "HR": "EUR", "HU": "HUF",
    "IE": "EUR", "IS": "ISK", "IT": "EUR", "LI": "CHF", "LT": "EUR", "LU": "EUR", "LV": "EUR", "ME": "EUR",
    "MK": "MKD", "MT": "EUR", "NL": "EUR", "NO": "NOK", "PL": "PLN", "PT": "EUR", "RO": "RON", "RS": "RSD",
    "SE": "SEK", "SI": "EUR", "SK": "EUR", "TR": "TRY", "UA": "UAH", "XK": "EUR", "GB": "GBP",
}

# Ukrainian oblasts that Russia's constitution claims; the site draws and prices them as Russia (plan.md).
UA_PRICED_AS_RUSSIA_NUTS2 = {"UA21", "UA22", "UA32", "UA43", "UA44", "UA45"}  # Donetsk, Luhansk, Zaporizhzhia, Kherson, Crimea, Sevastopol

TWO_BED_M2 = 75.0  # the plan's two-bed is about 70 to 85 m2

COLUMNS = ["place_code", "amount", "currency", "unit", "period", "measured_for", "source_id", "note"]
SOURCE_COLUMNS = ["source_id", "publisher", "title", "url", "licence", "retrieved", "period", "note"]


def fetch(source_id: str, url: str, filename: str | None = None, *, data: bytes | None = None,
          headers: dict | None = None, refresh: bool = False) -> Path:
    """Download url into cache/<source_id>/<filename> once and return the path."""
    folder = CACHE / source_id
    folder.mkdir(parents=True, exist_ok=True)
    name = filename or re.sub(r"[^A-Za-z0-9._-]+", "_", url.split("?")[0].rstrip("/").split("/")[-1])[:120]
    path = folder / name
    if path.exists() and path.stat().st_size > 0 and not refresh:
        return path
    request = urllib.request.Request(url, data=data, headers={"User-Agent": USER_AGENT, **(headers or {})})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                body = response.read()
            break
        except Exception:
            if attempt == 3:
                raise
            time.sleep(2 * (attempt + 1))
    path.write_bytes(body)
    return path


def today() -> str:
    return time.strftime("%Y-%m-%d")


@functools.cache
def nuts_regions() -> pd.DataFrame:
    """Every NUTS 2024 region (all levels) plus the UK's ITL 2025 regions, with country and level."""
    path = fetch("gisco-nuts-2024", "https://gisco-services.ec.europa.eu/distribution/v2/nuts/csv/NUTS_AT_2024.csv")
    eu = pd.read_csv(path, dtype=str, encoding="utf-8-sig")
    eu = eu[~eu["NUTS_ID"].str.contains("ZZ")]
    eu = pd.DataFrame({"nuts": eu["NUTS_ID"], "name": eu["NAME_LATN"], "country": eu["CNTR_CODE"],
                       "level": eu["NUTS_ID"].str.len() - 2})
    uk = itl_lookup()
    rows = []
    for level, code_col, name_col in [(1, "ITL125CD", "ITL125NM"), (2, "ITL225CD", "ITL225NM"), (3, "ITL325CD", "ITL325NM")]:
        for code, name in uk[[code_col, name_col]].drop_duplicates().itertuples(index=False):
            rows.append({"nuts": code, "name": name, "country": "TL", "level": level})
    rows.append({"nuts": "TL", "name": "United Kingdom", "country": "TL", "level": 0})
    out = pd.concat([eu, pd.DataFrame(rows)], ignore_index=True)
    out["iso"] = out["country"].map(lambda c: NUTS_TO_ISO.get(c, c))
    return out.reset_index(drop=True)


def nuts3() -> pd.DataFrame:
    """The NUTS 3 / ITL 3 regions the Europe tables cover (excluding the Ukrainian oblasts priced as Russia)."""
    regions = nuts_regions()
    out = regions[regions["level"] == 3]
    return out[~out["nuts"].str[:4].isin(UA_PRICED_AS_RUSSIA_NUTS2)].reset_index(drop=True)


@functools.cache
def itl_lookup() -> pd.DataFrame:
    """ONS lookup from local authority district (April 2025) to ITL 3, 2 and 1 (January 2025)."""
    import json
    url = ("https://services1.arcgis.com/ESMARspQHYMw9BZ9/ArcGIS/rest/services/ITL125_ITL225_ITL325_LAU125_LAD25_UK_LU/"
           "FeatureServer/0/query?where=1%3D1&outFields=*&returnGeometry=false&f=json&resultRecordCount=2000")
    path = fetch("ons-itl-2025", url, "lad25_itl.json")
    features = json.loads(path.read_text())["features"]
    cols = ["LAD25CD", "LAD25NM", "ITL325CD", "ITL325NM", "ITL225CD", "ITL225NM", "ITL125CD", "ITL125NM"]
    return pd.DataFrame([{c: f["attributes"][c] for c in cols} for f in features])


@functools.cache
def lau() -> pd.DataFrame:
    """Eurostat's LAU 2025 list on NUTS 2024: one row per local administrative unit, with population.

    Columns: country (NUTS country code), nuts3, lau_code, name, name_latin, population, area_km2, city_id, city_name.
    Covers EU, LI, NO, CH, MK, RS, TR. Portugal's LAUs are parishes (freguesias); its municipality is the first
    four digits of the code. Ireland's are electoral divisions.
    """
    url = ("https://ec.europa.eu/eurostat/documents/345175/501971/EU-27-LAU-2025-NUTS-2024.xlsx/"
           "574c9e4a-2dae-99fe-5510-3fd18d8e90c2?t=1771601900130")
    path = fetch("eurostat-lau-2025", url, "EU-27-LAU-2025-NUTS-2024.xlsx")
    sheets = pd.read_excel(path, sheet_name=None, dtype={"LAU CODE": str, "NUTS3": str})
    frames = []
    for name, df in sheets.items():
        if len(name) != 2:
            continue
        df.columns = [c.strip() for c in df.columns]
        frames.append(pd.DataFrame({
            "country": name, "nuts3": df["NUTS3"], "lau_code": df["LAU CODE"].astype(str),
            "name": df["LAU NAME NATIONAL"], "name_latin": df["LAU NAME LATIN"],
            "population": pd.to_numeric(df["POPULATION"], errors="coerce"),
            "area_km2": pd.to_numeric(df["TOTAL AREA (m2)"], errors="coerce") / 1e6,
            "city_id": df.get("CITY ID"), "city_name": df.get("CITY NAME"),
        }))
    out = pd.concat(frames, ignore_index=True)
    return out[out["nuts3"].notna()].reset_index(drop=True)


def _fold(text: str) -> str:
    text = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


@functools.cache
def _geonames() -> pd.DataFrame:
    path = fetch("geonames", "https://download.geonames.org/export/dump/cities1000.zip")
    with zipfile.ZipFile(path) as z:
        raw = z.read("cities1000.txt").decode("utf-8")
    cols = ["id", "name", "ascii", "alternates", "lat", "lon", "fclass", "fcode", "country", "cc2", "a1", "a2", "a3",
            "a4", "population", "elevation", "dem", "tz", "modified"]
    df = pd.read_csv(io.StringIO(raw), sep="\t", header=None, names=cols, dtype=str, quoting=csv.QUOTE_NONE)
    df["population"] = pd.to_numeric(df["population"], errors="coerce").fillna(0)
    return df


@functools.cache
def _geonames_index(iso: str) -> dict:
    df = _geonames()
    df = df[df["country"] == iso].sort_values("population", ascending=False)
    index: dict[str, tuple[str, float, str]] = {}
    for row in df.itertuples(index=False):
        names = {row.name, row.ascii} | set(str(row.alternates).split(",") if isinstance(row.alternates, str) else [])
        for n in names:
            key = _fold(n)
            if key and key not in index:
                index[key] = (row.id, row.population, row.fcode)
    return index


def _geonames_hit(iso: str, name: str):
    index = _geonames_index(iso)
    if not isinstance(name, str):
        return None
    for candidate in [name, re.split(r"[,(/]", name)[0],
                      re.sub(r"\b(stadt|city|municipality|city of|ville de|grad|miasto|mesto|město)\b", "", name, flags=re.I)]:
        hit = index.get(_fold(candidate))
        if hit:
            return hit
    return None


def city_code(iso: str, *names: str) -> str | None:
    """`CITY-<geonames id>` for the most populous GeoNames place matching any of the names, or None.

    Tries each name as given, then with administrative suffixes removed ('Stuttgart, Landeshauptstadt' -> 'Stuttgart').
    """
    for name in names:
        hit = _geonames_hit(iso, name)
        if hit:
            return f"CITY-{hit[0]}"
    return None


def main_towns(nuts3_code: str, towns: pd.DataFrame | None = None) -> pd.DataFrame:
    """A region's towns, main town first: a national capital or first-level administrative seat (GeoNames PPLC or
    PPLA) with at least a third of the largest town's population, else the most populous.

    towns defaults to the region's LAUs (columns name, name_latin, population); pass your own frame with the same
    columns where the LAU is not a town (Portugal's parishes, Ireland's electoral divisions). Adds column city_code.
    """
    if towns is None:
        table = lau()
        towns = table[table["nuts3"] == nuts3_code]
    towns = towns.sort_values("population", ascending=False).copy()
    iso = NUTS_TO_ISO.get(nuts3_code[:2], nuts3_code[:2])
    hits = [_geonames_hit(iso, n) or _geonames_hit(iso, l) for n, l in zip(towns["name"], towns.get("name_latin", towns["name"]))]
    towns["city_code"] = pd.Series([f"CITY-{h[0]}" if h else None for h in hits], index=towns.index, dtype=object)
    biggest = towns["population"].max()
    towns["rank"] = [0 if h and h[2] in ("PPLC", "PPLA") and p >= biggest / 3 else 1 for h, p in zip(hits, towns["population"])]
    return towns.sort_values(["rank", "population"], ascending=[True, False]).drop(columns="rank")


def place(nuts: str) -> str:
    """Contract place code for a NUTS or ITL code at any level: 'PT170' -> 'NUTS-PT170'."""
    return f"NUTS-{nuts}"


def country_code(nuts_country: str) -> str:
    """Contract country code (ISO 3166-1) for a NUTS country code: 'EL' -> 'GR', 'TL' -> 'GB'."""
    return NUTS_TO_ISO.get(nuts_country, nuts_country)


def row(place_code: str, amount: float, currency: str, unit: str, period: str, measured_for: str, source_id: str,
        note: str) -> dict:
    return {"place_code": place_code, "amount": amount, "currency": currency, "unit": unit, "period": str(period),
            "measured_for": measured_for, "source_id": source_id, "note": note}


def source(source_id: str, publisher: str, title: str, url: str, licence: str, period: str, note: str = "",
           retrieved: str | None = None) -> dict:
    """A row for data/sources.csv. retrieved defaults to the date of the newest file in cache/<source_id>/."""
    if retrieved is None:
        files = [f for f in (CACHE / source_id).glob("**/*") if f.is_file()]
        retrieved = time.strftime("%Y-%m-%d", time.localtime(max(f.stat().st_mtime for f in files))) if files else today()
    return {"source_id": source_id, "publisher": publisher, "title": title, "url": url, "licence": licence,
            "retrieved": retrieved, "period": period, "note": note}


def regions_in(prefix: str) -> list[str]:
    """NUTS 3 codes (in the covered list) that start with prefix: a country, NUTS 1 or NUTS 2 code."""
    table = nuts3()
    return table[table["nuts"].str.startswith(prefix)]["nuts"].tolist()


def eurostat(dataset: str, key: str = "", **params) -> pd.DataFrame:
    """A Eurostat dataset (or a slice of it) as a tidy frame from the keyless SDMX-CSV API, cached once.

    key is the SDMX series key ('A.CP041.INX_A_AVG.' style, dots between dimensions, empty for all); params are extra
    query parameters such as startPeriod='2020'. Columns are the dataset's dimensions plus TIME_PERIOD and OBS_VALUE.
    """
    query = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
    url = f"https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/{dataset}/{key}?format=SDMX-CSV" + (f"&{query}" if query else "")
    name = re.sub(r"[^A-Za-z0-9]+", "_", f"{dataset}_{key}_{query}").strip("_")[:150] + ".csv"
    path = fetch("eurostat", url, name)
    df = pd.read_csv(path, dtype=str)
    df["OBS_VALUE"] = pd.to_numeric(df["OBS_VALUE"], errors="coerce")
    return df


def rent_inflation(iso: str, from_year: int, to_year: int) -> float:
    """Growth factor of actual rents (HICP COICOP 04.1, annual average) between two years, from Eurostat.

    Use it to bring a rent measured before 2024 up to a recent year, and say so in the row's note.
    """
    geo = {"GR": "EL"}.get(iso, iso)
    df = eurostat("prc_hicp_aind", f"A.INX_A_AVG.CP041.{geo}")
    values = dict(zip(df["TIME_PERIOD"].astype(int), df["OBS_VALUE"]))
    return values[to_year] / values[from_year]
