#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# ///
"""Taiwan: median rent of a two-room 70 to 85 m2 flat, from the Ministry of the Interior's actual-price registration.

Written by AI on 2026.11.17 by model claude sonnet 5.5.

Source: 實價登錄 (real-price registration) quarterly open-data bulk files, https://plvr.land.moi.gov.tw/DownloadSeason?season=
<ROC year>S<quarter>&type=zip&fileName=lvr_landcsv.zip, file `<county letter>_lvr_land_c.csv` (租賃, rentals). Every
registered lease has its monthly rent (總額元), building area with common areas (建物總面積平方公尺), number of rooms,
rental type, contract date and, since 2024, whether a social-housing or other intermediary scheme manages it.

Selection (one rule for every place): lease of a building ("租賃房屋"), main use residential (住家用 or 集合住宅), the
whole flat let ("整棟(戶)出租", not a room or a floor of a shared flat), not managed under the social-housing
schemes (社會住宅代管, 社會住宅包租轉租), building area 70 to 85 m2, two rooms (房), monthly rent over NT$3,000, contract date in
the 12 months to July 2026. Records repeated in two quarterly files are counted once, by serial number (編號). A place needs
at least MIN_N such leases to get a row.
Taiwan's building area includes the stairwells, lifts and other shared parts (about 25 to 35% of the total), so a 70 to 85 m2
registered area is a flat with about 50 to 65 m2 inside, a normal Taiwanese two-bedroom.

Rows:
  TW-xxx        a city or county (ISO 3166-2:TW), the whole local government area
  CITY-<id>     the main city of that local government, whole built-up area as the county/city figure, except
  CITY-1668341  Taipei: the five central districts Da'an, Xinyi, Zhongshan, Zhongzheng, Songshan only
  TW            all of Taiwan pooled (the sample is dominated by Taipei, New Taipei and Kaohsiung)

Registered leases are a minority of all leases, and landlords may under-declare, so this is a registered-lease median,
not a census of tenants.

Run directly to print the rows as CSV (counts of skipped places go to stderr).
"""

import csv
import io
import pathlib
import statistics
import sys
import urllib.request
import zipfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from places import city_code  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[3]
CACHE = REPO / "cache" / "tw-moi-lvr"
SEASONS = ["114S4", "115S1", "115S2", "115S3"]
FIRST, LAST = "11408", "11507"  # ROC year+month of the lease date: Aug 2025 to Jul 2026
MIN_N = 20
SOURCE_ID = "tw-moi-lvr-rentals"

ISO = {"臺北市": "TW-TPE", "新北市": "TW-NWT", "桃園市": "TW-TAO", "臺中市": "TW-TXG", "臺南市": "TW-TNN", "高雄市": "TW-KHH",
       "基隆市": "TW-KEE", "新竹市": "TW-HSZ", "新竹縣": "TW-HSQ", "苗栗縣": "TW-MIA", "彰化縣": "TW-CHA", "南投縣": "TW-NAN",
       "雲林縣": "TW-YUN", "嘉義市": "TW-CYI", "嘉義縣": "TW-CYQ", "屏東縣": "TW-PIF", "宜蘭縣": "TW-ILA", "花蓮縣": "TW-HUA",
       "臺東縣": "TW-TTT", "澎湖縣": "TW-PEN", "金門縣": "TW-KIN", "連江縣": "TW-LIE"}
EN = {"臺北市": "Taipei City", "新北市": "New Taipei City", "桃園市": "Taoyuan City", "臺中市": "Taichung City", "臺南市": "Tainan City",
      "高雄市": "Kaohsiung City", "基隆市": "Keelung City", "新竹市": "Hsinchu City", "新竹縣": "Hsinchu County", "苗栗縣": "Miaoli County",
      "彰化縣": "Changhua County", "南投縣": "Nantou County", "雲林縣": "Yunlin County", "嘉義市": "Chiayi City", "嘉義縣": "Chiayi County",
      "屏東縣": "Pingtung County", "宜蘭縣": "Yilan County", "花蓮縣": "Hualien County", "臺東縣": "Taitung County",
      "澎湖縣": "Penghu County", "金門縣": "Kinmen County", "連江縣": "Lienchiang County"}
# the city's GeoNames name where the county figure stands for the city too
CITY_NAME = {"臺北市": "Taipei", "新北市": "New Taipei", "桃園市": "Taoyuan", "臺中市": "Taichung", "臺南市": "Tainan",
             "高雄市": "Kaohsiung", "基隆市": "Keelung", "新竹市": "Hsinchu", "嘉義市": "Chiayi", "花蓮縣": "Hualien",
             "宜蘭縣": "Yilan", "屏東縣": "Pingtung", "彰化縣": "Changhua", "苗栗縣": "Miaoli", "南投縣": "Nantou", "雲林縣": "Douliu"}
TAIPEI_CENTRE = {"大安區", "信義區", "中山區", "中正區", "松山區"}

SOURCES = [{
    "source_id": SOURCE_ID,
    "publisher": "Ministry of the Interior, Taiwan (Department of Land Administration), 實價登錄 real-price registration",
    "title": "Actual price registration, quarterly bulk download, rental records (lvr_land_c), seasons " + ", ".join(SEASONS),
    "url": "https://plvr.land.moi.gov.tw/DownloadOpenData",
    "licence": "Government Website Open Data Declaration (政府網站資料開放宣告) on the download page: free, non-exclusive, sublicensable, attribution required, no malicious alteration; the page also refers to a non-exclusive private-law licence with the Ministry (使用規範) for bulk download, whose text was not on the page",
    "retrieved": "2026-11-17",
    "period": "2025-08 to 2026-07",
    "note": "Registered leases; building area includes shared parts; social-housing intermediary leases excluded.",
}]


def _zip(season: str) -> pathlib.Path:
    path = CACHE / f"lvr_{season}.zip"
    if not path.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        url = f"https://plvr.land.moi.gov.tw/DownloadSeason?season={season}&type=zip&fileName=lvr_landcsv.zip"
        path.write_bytes(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})).read())
    return path


def leases() -> list[tuple[str, str, int]]:
    """(county name, district, monthly rent) for every lease matching the selection."""
    seen, out = set(), []
    for season in SEASONS:
        zf = zipfile.ZipFile(_zip(season))
        names = {r["name"]: r["description"] for r in csv.DictReader(io.TextIOWrapper(zf.open("manifest.csv"), encoding="utf-8-sig"))}
        for name, desc in names.items():
            if not name.endswith("_lvr_land_c.csv"):
                continue
            county = desc[:3]
            for r in list(csv.reader(io.TextIOWrapper(zf.open(name), encoding="utf-8-sig")))[2:]:
                if r[28] in seen:
                    continue
                seen.add(r[28])
                try:
                    area, rent, rooms = float(r[15]), int(r[22]), int(r[16])
                except ValueError:
                    continue
                if (r[1] == "租賃房屋" and r[12] in ("住家用", "集合住宅") and r[29] == "整棟(戶)出租"
                        and r[34] not in ("社會住宅代管", "社會住宅包租轉租") and FIRST <= r[7][:5] <= LAST
                        and 70 <= area <= 85 and rooms == 2 and rent > 3000):
                    out.append((county, r[0], rent))
    return out


def rows() -> list[dict]:
    data = leases()

    def make(place, rents, measured, extra=""):
        med = statistics.median(rents)
        q1, q3 = statistics.quantiles(rents, n=4)[0], statistics.quantiles(rents, n=4)[2]
        return {"place_code": place, "amount": round(med), "currency": "TWD", "unit": "per_month", "period": "2025-08 to 2026-07",
                "measured_for": measured, "source_id": SOURCE_ID,
                "note": (f"Median of {len(rents)} registered leases of whole two-room flats of 70 to 85 m2 (building area including shared parts), "
                         f"market leases only (social-housing schemes excluded), contracts dated Aug 2025 to Jul 2026; interquartile range "
                         f"NT${q1:,.0f} to NT${q3:,.0f}. A lease registered with the ministry, not an asking rent.{extra}")}

    out, skipped = [], []
    by_county = {}
    for county, district, rent in data:
        by_county.setdefault(county, []).append((district, rent))
    for county, recs in sorted(by_county.items()):
        rents = [r for _, r in recs]
        if len(rents) < MIN_N:
            skipped.append((EN[county], len(rents)))
            continue
        out.append(make(ISO[county], rents, f"{EN[county]}, the whole city or county"))
        if county in CITY_NAME:
            try:
                code = city_code(CITY_NAME[county], "TW")
            except KeyError:
                continue
            if county == "臺北市":
                centre = [r for d, r in recs if d in TAIPEI_CENTRE]
                if len(centre) >= MIN_N:
                    out.append(make(code, centre, "central Taipei: Da'an, Xinyi, Zhongshan, Zhongzheng and Songshan districts"))
                    continue
            out.append(make(code, rents, f"{EN[county]}, the whole city or county (the figure for the city's county-level area)"))
    out.append(make("TW", [r for _, r in [(c, rent) for c, _, rent in data]], "Taiwan, all counties pooled (dominated by Taipei, New Taipei and Kaohsiung)"))
    for name, n in skipped:
        print(f"skipped {name}: {n} leases (< {MIN_N})", file=sys.stderr)
    return out


if __name__ == "__main__":
    w = csv.DictWriter(sys.stdout, fieldnames=["place_code", "amount", "currency", "unit", "period", "measured_for", "source_id", "note"])
    w.writeheader()
    w.writerows(rows())
