#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""South Korea: KREB (Korea Real Estate Board) R-ONE, National Housing Price Trends Survey, apartments.

Written by AI on 2026.11.17 by model claude sonnet 5.5.

Keyless: the R-ONE web portal posts form data to JSON endpoints that need no account or API key. We call the same ones
the portal's own table viewer calls (/r-one/portal/stat/sttsDataPreviewList.do), after one GET of the table's page for
a session cookie. Raw JSON goes to cache/kr-reb-rone/ once; delete the folder to fetch again.

Tables used (all "(월)" monthly, apartments, unit: thousand won, rates in %):
  A_2024_00069  average monthly rent of wolse (monthly-rent) sample apartments, by region
  A_2024_00068  average deposit of the same wolse sample apartments, by region
  A_2024_00156  jeonse-to-wolse conversion rate, apartments, by region
  A_2024_00159  conversion rate, apartments, by region and size class (60 m2 or less; 60-85; over 85)

What it measures: KREB field staff estimate, each month, the market price of a fixed sample of 37,619 apartments
(and 6,626 row houses, 3,925 detached) from recent actual transactions, listings and agents' opinions. The "average
wolse" is the arithmetic mean of the sampled wolse flats' monthly rent (and, separately, deposit) in the region, all
sizes mixed. KREB itself says the survey is built for price indices and the averages are "for reference only". It is
an appraised level for the stock, not a register of new contracts. See kr_molit_rtms.py for the new-contract figure.

The row in `rows()` is a CROSS-CHECK: monthly rent + deposit x conversion rate / 12, for the region as a whole.
Run directly to print the rows as CSV.
"""

import csv
import http.cookiejar
import json
import pathlib
import sys
import time
import urllib.parse
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from places import city_code  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[3]
CACHE = REPO / "cache" / "kr-reb-rone"
BASE = "https://www.reb.or.kr/r-one/portal/stat/"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
SOURCE_ID = "kr-reb-rone"

SOURCES = [{
    "source_id": SOURCE_ID,
    "publisher": "Korea Real Estate Board (한국부동산원), R-ONE real estate statistics portal",
    "title": "National Housing Price Trends Survey (전국주택가격동향조사): average wolse rent and deposit, apartments (A_2024_00069, A_2024_00068); jeonse-to-wolse conversion rate (A_2024_00156, A_2024_00159)",
    "url": "https://www.reb.or.kr/r-one/portal/stat/easyStatPage/A_2024_00069.do",
    "licence": "Korean national statistics (approval no. 304004); the portal states no licence on the tables; the portal's terms permit citing with source credit (KOGL type not stated per table). Treat as: free to read, no licence stated.",
    "retrieved": "2026-11-17",
    "period": "2026-10 (rent, deposit); 2026-09 (conversion rate)",
    "note": "Appraised market level of a fixed sample of apartments, all sizes, wolse contracts only. KREB: averages are for reference; the survey is designed for price indices.",
}]

TABLES = {
    "rent": "A_2024_00069",
    "deposit": "A_2024_00068",
    "rate": "A_2024_00156",
    "rate_size": "A_2024_00159",
}
# dtacycleCd, min year, from each table's own page (firParam)
CYCLE = {"A_2024_00069": ("MM", 2015), "A_2024_00068": ("MM", 2015), "A_2024_00156": ("MM", 2011), "A_2024_00159": ("MM", 2011)}

# ISO 3166-2 -> (KREB region names). Rent tables: (CATE1, CATE2, CATE3, CATE4); rate tables: (CATE1, CATE2, CATE3).
PROVINCES = {
    "KR": ("전국", "전국"), "KR-11": ("서울", "서울"), "KR-26": ("부산", "부산"), "KR-27": ("대구", "대구"),
    "KR-28": ("인천", "인천"), "KR-29": ("전남광주", "광주"), "KR-30": ("대전", "대전"), "KR-31": ("울산", "울산"),
    "KR-50": ("세종", "세종"), "KR-41": ("경기", "경기"), "KR-42": ("강원", "강원"), "KR-43": ("충북", "충북"),
    "KR-44": ("충남", "충남"), "KR-45": ("전북", "전북"), "KR-46": ("전남광주", "전남"), "KR-47": ("경북", "경북"),
    "KR-48": ("경남", "경남"), "KR-49": ("제주", "제주"),
}
NAMES = {
    "KR": "South Korea", "KR-11": "Seoul", "KR-26": "Busan", "KR-27": "Daegu", "KR-28": "Incheon", "KR-29": "Gwangju",
    "KR-30": "Daejeon", "KR-31": "Ulsan", "KR-50": "Sejong", "KR-41": "Gyeonggi", "KR-42": "Gangwon",
    "KR-43": "North Chungcheong", "KR-44": "South Chungcheong", "KR-45": "North Jeolla", "KR-46": "South Jeolla",
    "KR-47": "North Gyeongsang", "KR-48": "South Gyeongsang", "KR-49": "Jeju",
}
# main cities (sigungu "si") -> (sido in KREB, KREB name, GeoNames name); metropolitan cities use the province row.
CITIES = [
    ("수원시", "경기", "Suwon"), ("성남시", "경기", "Seongnam"), ("고양시", "경기", "Goyang"), ("용인시", "경기", "Yongin"),
    ("부천시", "경기", "Bucheon"), ("안산시", "경기", "Ansan"), ("안양시", "경기", "Anyang"), ("화성시", "경기", "Hwaseong"),
    ("창원시", "경남", "Changwon"), ("청주시", "충북", "Cheongju"), ("전주시", "전북", "Jeonju"), ("천안시", "충남", "Cheonan"),
    ("포항시", "경북", "Pohang"), ("김해시", "경남", "Gimhae"), ("제주시", "제주", "Jeju"), ("춘천시", "강원", "Chuncheon"),
    ("원주시", "강원", "Wonju"), ("진주시", "경남", "Jinju"), ("구미시", "경북", "Gumi"),
]
METRO_CITIES = {  # GeoNames name -> province code whose figure is the city's
    "Seoul": "KR-11", "Busan": "KR-26", "Daegu": "KR-27", "Incheon": "KR-28", "Gwangju": "KR-29", "Daejeon": "KR-30",
    "Ulsan": "KR-31", "Sejong": "KR-50",
}


def _fetch(statbl: str) -> pathlib.Path:
    path = CACHE / f"{statbl}.json"
    if path.exists():
        return path
    CACHE.mkdir(parents=True, exist_ok=True)
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    page = f"{BASE}easyStatPage/{statbl}.do"
    opener.open(urllib.request.Request(page, headers={"User-Agent": UA}), timeout=60).read()
    cycle, miny = CYCLE[statbl]
    form = (f"statblId={statbl}&viewLocOpt=B&wrttimeType=L&dtadvsVal=OD&wrttimeLastestVal=200&wrttimeOrder=A"
            f"&dtacycleCd={cycle}&wrttimeMinYear={miny}&wrttimeMaxYear=2026&wrttimeStartQt=01&wrttimeEndQt=12"
            f"&wrttimeMinQt=01&wrttimeMaxQt=12&optDivVal=00&isRegionData=Y&searchType=S")
    req = urllib.request.Request(BASE + "sttsDataPreviewList.do", data=form.encode(), headers={
        "User-Agent": UA, "Referer": page, "X-Requested-With": "XMLHttpRequest"})
    data = opener.open(req, timeout=120).read()
    json.loads(data)["DATA"]  # fail loudly if the portal returned an error page
    path.write_bytes(data)
    time.sleep(1)
    return path


def _load(statbl: str) -> list[dict]:
    return json.loads(_fetch(statbl).read_text(encoding="utf-8"))["DATA"]


def _num(s):
    return None if s in (None, "", "-") else float(str(s).replace(",", ""))


def _latest(row: dict):
    """(period 'YYYY-MM', value) of the newest non-empty month column in the row."""
    cols = sorted((k for k in row if k.startswith("COL_") and _num(row[k]) is not None), reverse=True)
    if not cols:
        return None, None
    return f"{cols[0][4:8]}-{cols[0][8:10]}", _num(row[cols[0]])


def _rent_index():
    rent, dep = {}, {}
    for r in _load(TABLES["rent"]):
        rent[tuple(r[f"CATE{i}"] for i in range(1, 5))] = _latest(r)
    for r in _load(TABLES["deposit"]):
        dep[tuple(r[f"CATE{i}"] for i in range(1, 5))] = _latest(r)
    return rent, dep


def _rate_index():
    return {tuple(r[f"CATE{i}"] for i in range(1, 4)): _latest(r) for r in _load(TABLES["rate"])}


def _rate_size_index():
    return {(r["GRP1"], r["GRP2"], r["CATE1"]): _latest(r) for r in _load(TABLES["rate_size"])}


def conversion_rates_60_85() -> dict[str, tuple[str, float]]:
    """Province code -> (period, KREB apartment conversion rate in %, size class 60-85 m2, all of that province)."""
    idx = _rate_size_index()
    out = {}
    for code, (c1, c2) in PROVINCES.items():
        period, value = idx[(c1, c2, "60㎡초과 85㎡이하")]
        out[code] = (period, value)
    return out


def rows() -> list[dict]:
    rent, dep = _rent_index()
    rate = _rate_index()

    def row(place, label, key_rent, key_rate, how):
        rp, r = rent[key_rent]
        _, d = dep[key_rent]
        rtp, rt = rate[key_rate]
        if r is None or d is None or rt is None:
            return None
        rent_krw, dep_krw = r * 1000, d * 1000
        amount = round((rent_krw + dep_krw * rt / 100 / 12) / 1000) * 1000
        return {
            "place_code": place, "amount": amount, "currency": "KRW", "unit": "per_month", "period": rp,
            "measured_for": f"{label}, {how}",
            "source_id": SOURCE_ID,
            "note": (f"CROSS-CHECK, appraised stock level, all sizes. KREB average wolse rent KRW {rent_krw:,.0f} per month "
                     f"+ KREB average wolse deposit KRW {dep_krw:,.0f} x KREB apartment conversion rate {rt}% ({rtp}) / 12 "
                     f"= KRW {amount:,.0f}. Rent and deposit are means over KREB's sampled wolse apartments in the region "
                     f"({rp}); the rate is for all apartments of the region. Thin: KREB says averages are for reference only."),
        }

    out = []
    for code, (c1, c2) in PROVINCES.items():
        key_rent = (c1, c2, c2, c2)
        key_rate = (c1, c2, c2)
        label = NAMES[code] if code != "KR" else "South Korea"
        how = "all apartment wolse samples, all sizes" + (", pooled nationally" if code == "KR" else ", whole province or metropolitan city")
        r = row(code, label, key_rent, key_rate, how)
        if r:
            out.append(r)
    # Seoul city row: KREB's central zone (Jongno, Jung, Yongsan)
    r = row(city_code("Seoul", "KR"), "Seoul central zone (도심권: Jongno, Jung and Yongsan districts)",
            ("서울", "강북지역", "도심권", "도심권"), ("서울", "도심권", "도심권"), "all apartment wolse samples, all sizes")
    if r:
        out.append(r)
    for name, code in METRO_CITIES.items():
        if name == "Seoul":
            continue
        base = next(x for x in out if x["place_code"] == code)
        out.append({**base, "place_code": city_code(name, "KR"),
                    "measured_for": base["measured_for"].replace("whole province or metropolitan city", "whole metropolitan city")})
    for kr_name, sido, geo in CITIES:
        key_rent = next((k for k in rent if k[0] == sido and k[2] == kr_name and k[3] == kr_name), None)
        key_rate = next((k for k in rate if k[0] == sido and k[2] == kr_name), None)
        if key_rent is None or key_rate is None:
            continue
        try:
            code = city_code(geo, "KR")
        except KeyError:  # e.g. Yongin is missing from GeoNames cities15000
            continue
        r = row(code, geo, key_rent, key_rate, "all apartment wolse samples in the city, all sizes")
        if r:
            out.append(r)
    return out


if __name__ == "__main__":
    out = rows()
    w = csv.DictWriter(sys.stdout, fieldnames=["place_code", "amount", "currency", "unit", "period", "measured_for", "source_id", "note"])
    w.writeheader()
    w.writerows(out)
    print(f"{len(out)} rows", file=sys.stderr)
