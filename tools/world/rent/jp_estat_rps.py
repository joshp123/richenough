#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = ["openpyxl"]
# ///
"""Japan: private rent per 3.3 m2 in every prefectural capital, from the Statistics Bureau's Retail Price Survey.

Written by AI on 2026.11.17 by model claude sonnet 5.5.

Source: 小売物価統計調査（動向編） Table 1 "主要品目の都市別小売価格", item 3001 民営家賃 (private rent), yen per month per 3.3 m2
(1 tsubo) of floor area, for the prefectural capitals and cities of 150,000+ people (Tokyo = the 23 wards, 東京都区部). Monthly
Excel files from e-Stat (https://www.e-stat.go.jp/stat-search/files?toukei=00200571&tstat=000000680001), found through
e-Stat's own file-list endpoint, no key needed. Each file goes to cache/jp-estat-rps/ once.

What it measures. The survey prices rent of rented dwellings in sampled survey districts: total rent paid divided by total floor
area of the rented homes, i.e. the average over ALL sitting private tenants, not new lets. Sitting tenants pay below the going rate
for a new let, most of all in Tokyo; the figure also covers every dwelling size (the survey has four classes: wooden small or medium,
non-wooden small or medium; the table reports the weighted mean). Months outside a district's survey month carry the earlier figure.

Rows: the mean of the latest 12 months available, / 3.3 x 75 m2.
  JP-xx   the prefectural capital's figure for the prefecture (JP-13 Tokyo = the 23 wards)
  CITY-   the 23 wards (Tokyo) and the designated cities, each its own figure
  JP      median of the 47 prefectural capitals

Run directly to print the rows as CSV.
"""

import csv
import html
import json
import pathlib
import re
import statistics
import sys
import urllib.request

import openpyxl

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from places import city_code  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[3]
CACHE = REPO / "cache" / "jp-estat-rps"
UA = {"User-Agent": "Mozilla/5.0"}
SOURCE_ID = "jp-estat-retail-price-survey-rent"
AREA, TSUBO = 75, 3.3
N_MONTHS = 12
BASE = "https://www.e-stat.go.jp/retrieve/api_file?page=1&layout=dataset&cycle=1&toukei=00200571&tstat=000000680001&tclass1val=0"

SOURCES = [{
    "source_id": SOURCE_ID,
    "publisher": "Statistics Bureau of Japan (Ministry of Internal Affairs and Communications), via e-Stat",
    "title": "Retail Price Survey (Trend Survey), Table 1 average retail prices of main items by city, item 3001 private rent",
    "url": "https://www.e-stat.go.jp/stat-search/files?toukei=00200571&tstat=000000680001",
    "licence": "e-Stat terms of use, based on the Government Standard Terms of Use version 2.0, compatible with CC BY 4.0; attribution required, numerical data and simple tables are not subject to copyright",
    "retrieved": "2026-11-17",
    "period": "latest 12 months, see rows",
    "note": "Average rent per 3.3 m2 of all sitting private tenants, not new lets; all dwelling sizes.",
}]

# prefectural capital (survey area code) -> JP-xx is the first two digits of the area code
CAPITALS = ["01100", "02201", "03201", "04100", "05201", "06201", "07201", "08201", "09201", "10201", "11100", "12100", "13100",
            "14100", "15100", "16201", "17201", "18201", "19201", "20201", "21201", "22100", "23100", "24201", "25201", "26100",
            "27100", "28100", "29201", "30201", "31201", "32201", "33100", "34100", "35203", "36201", "37201", "38201", "39201",
            "40130", "41201", "42201", "43100", "44201", "45201", "46201", "47201"]
CITIES = {"01100": "Sapporo", "04100": "Sendai", "11100": "Saitama", "12100": "Chiba", "13100": "Tokyo", "14100": "Yokohama",
          "14130": "Kawasaki", "14150": "Sagamihara", "15100": "Niigata", "22100": "Shizuoka", "22130": "Hamamatsu",
          "23100": "Nagoya", "26100": "Kyoto", "27100": "Osaka", "27140": "Sakai", "28100": "Kobe", "33100": "Okayama",
          "34100": "Hiroshima", "40100": "Kitakyushu", "40130": "Fukuoka", "43100": "Kumamoto", "17201": "Kanazawa"}


def _get(url: str) -> bytes:
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA)).read()


def _months() -> list[tuple[str, str]]:
    """(year code, month code) for every published month, newest first."""
    items = json.loads(_get(BASE.replace("layout=dataset", "layout=datalist")))["items"]
    seen, out = set(), []
    for key in re.findall(r"year=(\d+)&amp;month=(\d+)&amp;result_back", items):
        if key not in seen:
            seen.add(key)
            out.append(key)
    by_year: dict[str, list] = {}
    for key in out:  # e-Stat lists years newest first but the months of a year oldest first
        by_year.setdefault(key[0], []).append(key)
    return [key for year in by_year for key in reversed(by_year[year])]


def _rent_file(year: str, month: str) -> pathlib.Path | None:
    """Download Table 1's 3001-民営家賃 workbook for the month, or None if that month's Table 1 is not out yet."""
    items = json.loads(_get(f"{BASE}&year={year}&month={month}"))["items"]
    texts: dict[str, str] = {}
    for block in re.split(r'(?=<a href="/stat-search/file-download)', items)[1:]:
        m = re.match(r'<a href="/stat-search/file-download\?statInfId=(\d+)&fileKind=(\d)"', block)
        texts[m.group(1)] = texts.get(m.group(1), "") + html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", block)))
    for stat_id, text in texts.items():
        if "主要品目の都市別小売価格" in text and "3001 民営家賃" in text:
            path = CACHE / f"table1-{stat_id}.xlsx"
            if not path.exists():
                CACHE.mkdir(parents=True, exist_ok=True)
                path.write_bytes(_get(f"https://www.e-stat.go.jp/stat-search/file-download?statInfId={stat_id}&fileKind=0"))
            return path
    return None


def _parse(path: pathlib.Path) -> tuple[str, dict[str, tuple[str, float | None]]]:
    rows = list(openpyxl.load_workbook(path, read_only=True).worksheets[0].iter_rows(values_only=True))
    codes = next(r for r in rows if "地域コード" in r)
    names = next(r for r in rows if "地域" in r and r.index("地域") == codes.index("地域コード"))
    data = next(r for r in rows if "民営家賃" in r)
    m = re.match(r"(\d+)年(\d+)月", str(data[list(data).index("民営家賃") - 2]))  # 時間軸（月）
    month = f"{m.group(1)}-{int(m.group(2)):02d}"
    start = codes.index("地域コード") + 1
    out = {}
    for code, name, value in zip(codes[start:], names[start:], data[start:]):
        if code:
            out[str(code)] = (name, float(value) if isinstance(value, (int, float)) else None)
    return month, out


def monthly() -> list[tuple[str, dict]]:
    got = []
    for year, month in _months():
        path = _rent_file(year, month)
        if path:
            got.append(_parse(path))
        if len(got) == N_MONTHS:
            break
    return got


def rows() -> list[dict]:
    got = monthly()
    months = sorted(m for m, _ in got)
    period = f"{months[0]} to {months[-1]}"
    mean = {}
    for code in {c for _, d in got for c in d}:
        vals = [d[code][1] for _, d in got if code in d and d[code][1] is not None]
        if len(vals) == len(got):
            mean[code] = (got[0][1][code][0], statistics.mean(vals))
    out = []

    def add(place, code, measured):
        name, per_tsubo = mean[code]
        out.append({"place_code": place, "amount": int(round(per_tsubo / TSUBO * AREA, -2)), "currency": "JPY", "unit": "per_month", "period": period,
                    "measured_for": measured, "source_id": SOURCE_ID,
                    "note": (f"Average private rent in {name} (survey area {code}) = ¥{per_tsubo:,.0f} per 3.3 m2 per month, mean of {len(got)} months; "
                             f"/ 3.3 x {AREA} m2. Measures the rent paid by ALL sitting private tenants of every dwelling size, not new lets, "
                             f"so it understates the going rate for a new let.")})

    caps = []
    for code in CAPITALS:
        if code not in mean:
            continue
        name = mean[code][0]
        caps.append(mean[code][1])
        measured = "Tokyo's 23 wards (the survey's 東京都区部)" if code == "13100" else f"{name} (the prefectural capital), city-wide"
        add(f"JP-{code[:2]}", code, measured + ", private rented housing, all sitting tenants")
    for code, english in CITIES.items():
        if code in mean:
            add(city_code(english, "JP"), code, f"{mean[code][0]}{'' if code != '13100' else ' (the 23 wards)'}, private rented housing, all sitting tenants")
    out.append({"place_code": "JP", "amount": int(round(statistics.median(caps) / TSUBO * AREA, -2)), "currency": "JPY", "unit": "per_month", "period": period,
                "measured_for": "Japan: the median of the 47 prefectural capitals' private rents, all sitting tenants", "source_id": SOURCE_ID,
                "note": f"Median of the 47 prefectural capitals' mean rent per 3.3 m2 = ¥{statistics.median(caps):,.0f}; / 3.3 x {AREA} m2. Not a national average."})
    return out


if __name__ == "__main__":
    w = csv.DictWriter(sys.stdout, fieldnames=["place_code", "amount", "currency", "unit", "period", "measured_for", "source_id", "note"])
    w.writeheader()
    w.writerows(rows())
