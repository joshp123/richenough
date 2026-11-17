#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = ["pypdf"]
# ///
"""Tokyo region: rents of signed new lets in the Tokyo metropolitan area, from REINS (East Japan Real Estate Information Network).

Written by AI on 2026.11.17 by model claude sonnet 5.5.

Source: 首都圏賃貸居住用物件の取引動向（2026年7～9月）, REINS quarterly market report, 2 pages, published 2026-10-19,
https://www.reins.or.jp/pdf/trend/sc/sc_202607-09.pdf (page 1, マンション = reinforced-concrete condominium-type rentals).
For each ward and prefecture: number of rental contracts concluded through member brokers in the quarter (成約), their
average monthly rent, average floor area and rent per m2 (㎡単価). These are concluded contracts, so a new-let measure. They
cover every unit size (average area is only 28 to 50 m2), so rent per m2 x 75 m2 for a 75 m2 flat is an extrapolation: small
units cost more per m2, which pushes it up, and the dearest wards have the biggest units, which pushes it down.

reins.or.jp serves an incomplete certificate chain, so the download skips certificate checks; the file's sha256 is in
the notes file so a changed file is detectable.

Rows (rent per m2 x 75 m2, weighted by contract count where several areas are combined):
  JP-11 Saitama prefecture, JP-12 Chiba prefecture, JP-13 Tokyo prefecture (23 wards plus the rest of Tokyo),
  JP-14 Kanagawa prefecture (Yokohama and Kawasaki plus the rest)
  CITY-1850147 Tokyo: the five central wards Chiyoda, Chuo, Minato, Shinjuku and Shibuya
  CITY Yokohama, CITY Kawasaki: all their wards
`districts()` gives every ward.

Run directly to print the rows as CSV.
"""

import csv
import io
import pathlib
import re
import ssl
import sys
import urllib.request

from pypdf import PdfReader

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from places import city_code  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[3]
CACHE = REPO / "cache" / "jp-reins-rental"
URL = "https://www.reins.or.jp/pdf/trend/sc/sc_202607-09.pdf"
SOURCE_ID = "jp-reins-rental-2026q3"
PERIOD = "2026-07 to 2026-09"
AREA = 75
CENTRAL = ["千代田区", "中央区", "港区", "新宿区", "渋谷区"]
WARDS_EN = {"千代田区": "Chiyoda", "中央区": "Chuo", "港区": "Minato", "新宿区": "Shinjuku", "渋谷区": "Shibuya"}

SOURCES = [{
    "source_id": SOURCE_ID,
    "publisher": "East Japan Real Estate Information Network (公益財団法人東日本不動産流通機構, REINS)",
    "title": "首都圏賃貸居住用物件の取引動向（2026年7～9月）, page 1, マンション",
    "url": URL,
    "licence": "free to read, no licence stated in the PDF",
    "retrieved": "2026-11-17",
    "period": PERIOD,
    "note": "Average rent per m2 of rental contracts concluded through member brokers in the quarter (new lets), all unit sizes (average 28 to 50 m2).",
}]


def _pdf() -> pathlib.Path:
    path = CACHE / "sc_202607-09.pdf"
    if not path.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        ctx = ssl.create_default_context()
        ctx.check_hostname, ctx.verify_mode = False, ssl.CERT_NONE
        path.write_bytes(urllib.request.urlopen(urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"}), context=ctx).read())
    return path


def table() -> dict[str, dict[str, tuple[int, float, float, int]]]:
    """{section: {area: (contracts, rent in 10,000 yen, area m2, yen per m2)}} from page 1 (condominiums)."""
    text = PdfReader(_pdf()).pages[0].extract_text()
    out, section = {}, "prefectures"
    for line in text.splitlines():
        if "件数（件）" in line:
            head = line.split()[0]
            section = "prefectures" if head == "都県・地域名" else head
            out.setdefault(section, {})
            continue
        m = re.match(r"^(\S+?)\*?\s+([\d,]+)\s+([\d.]+)\s+([\d.]+)\s+([\d,]+)\s*$", line)
        if m and section:
            out.setdefault(section, {})[m.group(1)] = (int(m.group(2).replace(",", "")), float(m.group(3)), float(m.group(4)), int(m.group(5).replace(",", "")))
    return out


def _combine(parts: list[tuple[int, float, float, int]]) -> tuple[int, int]:
    n = sum(p[0] for p in parts)
    return n, round(sum(p[0] * p[3] for p in parts) / n)


def _row(place, parts, measured, what):
    n, per_m2 = _combine(parts)
    return {"place_code": place, "amount": round(per_m2 * AREA, -2), "currency": "JPY", "unit": "per_month", "period": PERIOD,
            "measured_for": measured, "source_id": SOURCE_ID,
            "note": (f"Rent per m2 of {n:,} rental contracts concluded through REINS member brokers in Jul to Sep 2026 ({what}) = ¥{per_m2:,} per m2 per month, "
                     f"weighted by contract count; x {AREA} m2. Concluded new lets of condominium-type flats of every size (average 28 to 50 m2), "
                     f"not filtered to two bedrooms, so extrapolated to 75 m2.")}


def rows() -> list[dict]:
    t = table()
    pref, tokyo = t["prefectures"], t["東京23区"]
    out = [
        _row("JP-11", [pref["埼玉県"]], "Saitama Prefecture, all condominium lets", "Saitama Prefecture"),
        _row("JP-12", [pref["千葉県"]], "Chiba Prefecture, all condominium lets", "Chiba Prefecture"),
        _row("JP-13", [pref["東京23区"], pref["東京都他"]], "Tokyo Prefecture: the 23 wards and the rest of Tokyo, all condominium lets", "23 wards and the rest of Tokyo"),
        _row("JP-14", [pref["横浜・川崎"], pref["神奈川県他"]], "Kanagawa Prefecture: Yokohama, Kawasaki and the rest, all condominium lets", "Yokohama, Kawasaki and the rest of Kanagawa"),
        _row(city_code("Tokyo", "JP"), [tokyo[w] for w in CENTRAL], "Tokyo's five central wards (Chiyoda, Chuo, Minato, Shinjuku, Shibuya), new lets of condominium-type flats",
             "Chiyoda, Chuo, Minato, Shinjuku and Shibuya wards"),
        _row(city_code("Yokohama", "JP"), list(t["横浜市"].values()), "Yokohama, all 18 wards, new lets of condominium-type flats", "Yokohama's 18 wards"),
        _row(city_code("Kawasaki", "JP"), list(t["川崎市"].values()), "Kawasaki, all 7 wards, new lets of condominium-type flats", "Kawasaki's 7 wards"),
    ]
    return out


def districts() -> list[dict]:
    """Every ward: contracts, average rent (yen), average area, yen per m2, and per m2 x 75 m2."""
    out = []
    for city in ("東京23区", "横浜市", "川崎市"):
        for ward, (n, rent, area, per_m2) in table()[city].items():
            out.append({"city": city, "ward": ward, "contracts": n, "avg_rent_yen": round(rent * 10000), "avg_area_m2": area,
                        "yen_per_m2": per_m2, "per_m2_x_75": round(per_m2 * AREA, -2), "source_id": SOURCE_ID, "period": PERIOD})
    return out


if __name__ == "__main__":
    w = csv.DictWriter(sys.stdout, fieldnames=["place_code", "amount", "currency", "unit", "period", "measured_for", "source_id", "note"])
    w.writeheader()
    w.writerows(rows())
