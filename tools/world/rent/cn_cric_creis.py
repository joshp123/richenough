#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = ["pypdf"]
# ///
"""Mainland China: rent of a 60-90 m2 flat in 50 cities, from China Index Academy's (中指研究院) October 2026 report.

Written by AI on 2026.11.17 by model claude sonnet 5.5.

Source: "中国房地产指数系统百城价格指数报告（2026年10月）", a free PDF linked from
https://www.cih-index.com/data/index/rentIndex.html (Table 5 on page 9 and Table 6 on page 10, "数据来源：中指数据CREIS").
The PDF goes to cache/cn-cric-creis-2026-10/ once; delete the folder to fetch again.

What the rows measure. The index takes the asking (listing) rents on Fang.com, Lianjia, Beike and Anjuke for a fixed
sample of active residential compounds in the urban districts of each city, on the 25th of the month. It is an
asking rent, not a signed contract, and it covers whole-city urban districts, not a central zone (the district split
is in paid reports and in chart images only).
  city row      Table 6, "平均套租金 60-90m2": average monthly rent of a whole listed flat of 60-90 m2 (building area),
                weighted by listed floor area. It is the nearest published band to a 70-85 m2 two-bedroom. It is not
                filtered to two bedrooms.
  province row  the same figure for the provincial capital only, labelled so in measured_for.
  CN row        median of the 50 cities' 60-90 m2 rents: the middle city of China's 50 largest rental markets,
                not a national average.
Table 5 (rent per m2, average and median) is parsed too and written into each note, with 75 m2 x the average as a cross-check.

Run directly to print the rows as CSV.
"""

import csv
import pathlib
import re
import statistics
import sys
import unicodedata
import urllib.request

from pypdf import PdfReader

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from places import city_code  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[3]
CACHE = REPO / "cache" / "cn-cric-creis-2026-10"
PDF = CACHE / "creis.pdf"
URL = "https://cihcdnzip.soufunimg.com/backend/reportCreisFile/130762/1445a9fba05845d497ef73f2ca5af3a0.pdf"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
SOURCE_ID = "cn-cric-creis-2026-10"
PERIOD = "2026-10"

SOURCES = [{
    "source_id": SOURCE_ID,
    "publisher": "China Index Academy (中指研究院), China Real Estate Index System (CREIS)",
    "title": "中国房地产指数系统百城价格指数报告（2026年10月）: Table 5 (50城住宅租赁价格指数) and Table 6 (50城住宅租赁价格分类指数)",
    "url": "https://www.cih-index.com/data/index/rentIndex.html (PDF: " + URL + ")",
    "licence": "free to read, no licence stated (the report states only: 本报告由中国房地产指数系统完成)",
    "retrieved": "2026-11-17",
    "period": PERIOD,
    "note": "Asking (listing) rents scraped from Fang.com, Lianjia, Beike, Anjuke for fixed sample compounds, 25th of the month; urban districts of each of 50 cities; building area.",
}]

# Chinese name -> (GeoNames name, ISO 3166-2 of the province, or None, label for the province row)
CITIES = {
    "北京": ("Beijing", "CN-BJ"), "上海": ("Shanghai", "CN-SH"), "天津": ("Tianjin", "CN-TJ"),
    "重庆": ("Chongqing", "CN-CQ"), "深圳": ("Shenzhen", None), "广州": ("Guangzhou", "CN-GD"),
    "杭州": ("Hangzhou", "CN-ZJ"), "成都": ("Chengdu", "CN-SC"), "南京": ("Nanjing", "CN-JS"),
    "苏州": ("Suzhou", None), "武汉": ("Wuhan", "CN-HB"), "西安": ("Xi'an", "CN-SN"),
    "厦门": ("Xiamen", None), "三亚": ("Sanya", None), "珠海": ("Zhuhai", None), "福州": ("Fuzhou", "CN-FJ"),
    "宁波": ("Ningbo", None), "海口": ("Haikou", "CN-HI"), "东莞": ("Dongguan", None), "大连": ("Dalian", None),
    "佛山": ("Foshan", None), "无锡": ("Wuxi", None), "长沙": ("Changsha", "CN-HN"), "合肥": ("Hefei", "CN-AH"),
    "青岛": ("Qingdao", None), "泉州": ("Quanzhou", None), "常州": ("Changzhou", None),
    "乌鲁木齐": ("Urumqi", "CN-XJ"), "济南": ("Jinan", "CN-SD"), "南宁": ("Nanning", "CN-GX"),
    "嘉兴": ("Jiaxing", None), "温州": ("Wenzhou", None), "昆明": ("Kunming", "CN-YN"), "绍兴": ("Shaoxing", None),
    "西宁": ("Xining", "CN-QH"), "哈尔滨": ("Harbin", "CN-HL"), "郑州": ("Zhengzhou", "CN-HA"),
    "沈阳": ("Shenyang", "CN-LN"), "兰州": ("Lanzhou", "CN-GS"), "贵阳": ("Guiyang", "CN-GZ"),
    "长春": ("Changchun", "CN-JL"), "惠州": ("Huizhou", None), "石家庄": ("Shijiazhuang", "CN-HE"),
    "南昌": ("Nanchang", "CN-JX"), "南通": ("Nantong", None), "呼和浩特": ("Hohhot", "CN-NM"),
    "太原": ("Taiyuan", "CN-SX"), "徐州": ("Xuzhou", None), "银川": ("Yinchuan", "CN-NX"), "北海": ("Beihai", None),
}
MUNICIPALITIES = {"CN-BJ", "CN-SH", "CN-TJ", "CN-CQ"}


def fetch() -> pathlib.Path:
    if not PDF.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        PDF.write_bytes(urllib.request.urlopen(urllib.request.Request(URL, headers={"User-Agent": UA}), timeout=120).read())
    return PDF


RADICALS = str.maketrans({"⻔": "门", "⻬": "齐", "⻄": "西", "⻘": "青", "⻓": "长"})  # NFKC leaves these simplified radicals alone


def norm(s: str) -> str:
    """The PDF's text layer uses CJK radical lookalikes (⼴, ⻄, ⻘); NFKC and RADICALS turn them into the usual characters."""
    s = unicodedata.normalize("NFKC", s).translate(RADICALS)
    return re.sub(r"\(主城区\)|（主城区）", "", s)


def tables() -> tuple[dict, dict]:
    """(per_m2, bands): per_m2[city] = (average, change %, median) from Table 5; bands[city] = [5 band rents or None] from Table 6."""
    pages = PdfReader(str(fetch())).pages
    t5 = norm(pages[8].extract_text())
    assert "表5:2026年10月50城住宅租赁价格指数" in t5, "Table 5 is not on page 9"
    per_m2 = {}
    for city, avg, chg, med in re.findall(r"([一-鿿]+)\s+([\d.]+)\s+(-?[\d.]+)%\s+([\d.]+)", t5):
        per_m2[city] = (float(avg), float(chg), float(med))
    t6 = norm(pages[9].extract_text())
    assert "表6:2026年10月50城住宅租赁价格分类指数" in t6, "Table 6 is not on page 10"
    bands = {}
    for line in t6.splitlines():
        parts = line.split()
        if len(parts) == 11 and parts[0] in CITIES:
            bands[parts[0]] = [None if p == "-" else int(p) for p in parts[1:6]]
    assert len(per_m2) == 50 and len(bands) == 50, (len(per_m2), len(bands))
    return per_m2, bands


def rows() -> list[dict]:
    per_m2, bands = tables()
    out = []
    unit_rents = {}
    for cn, (en, province) in CITIES.items():
        avg, chg, med = per_m2[cn]
        rent = bands[cn][2]  # 60-90 m2
        unit_rents[cn] = rent
        note = (f"CRIC/CREIS Oct 2026 Table 6: average asking rent of a listed 60-90 m2 flat is {rent:,} yuan a month "
                f"(flats of 30-60 m2: {bands[cn][1]:,}; 90-140 m2: {bands[cn][3]:,}). Table 5, whole city, per m2 of building area: "
                f"average {avg} yuan, median {med} yuan; 75 m2 x average = {round(avg * 75):,} yuan. "
                f"Urban districts of the whole city, not a central zone. Not filtered to two bedrooms.")
        out.append({
            "place_code": city_code(en, "CN"), "amount": rent, "currency": "CNY", "unit": "per_month", "period": PERIOD,
            "measured_for": f"{en}, urban districts city-wide, asking rent of listed flats of 60-90 m2 (Fang, Lianjia, Beike, Anjuke listings)",
            "source_id": SOURCE_ID, "note": note,
        })
        if province:
            if province in MUNICIPALITIES:
                measured = f"{en} municipality, urban districts, asking rent of listed flats of 60-90 m2"
                pnote = f"{en} is a province-level municipality: same figure as the city row. " + note
            else:
                measured = f"{en} only (the provincial capital), not the province; asking rent of listed flats of 60-90 m2"
                pnote = f"Provincial capital's figure written under the province code. " + note
            out.append({
                "place_code": province, "amount": rent, "currency": "CNY", "unit": "per_month", "period": PERIOD,
                "measured_for": measured, "source_id": SOURCE_ID, "note": pnote,
            })
    median_rent = round(statistics.median(unit_rents.values()))
    out.append({
        "place_code": "CN", "amount": median_rent, "currency": "CNY", "unit": "per_month", "period": PERIOD,
        "measured_for": "Median of the 50 cities in CRIC's rent index (China's largest rental markets), asking rent of listed flats of 60-90 m2; not a national average",
        "source_id": SOURCE_ID,
        "note": "Median of the 50 city figures in Table 6. Smaller towns and rural China are not covered and are cheaper; treat as a fallback only.",
    })
    return out


if __name__ == "__main__":
    columns = ["place_code", "amount", "currency", "unit", "period", "measured_for", "source_id", "note"]
    writer = csv.DictWriter(sys.stdout, fieldnames=columns, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows())
