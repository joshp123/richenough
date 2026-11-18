# /// script
# requires-python = ">=3.11"
# dependencies = ["pdfplumber"]
# ///
"""Israel (country PS on this site): Central Bureau of Statistics, average monthly rent of a 3-room flat.

Written by AI on 2026.11.17 by model claude sonnet 5.5, for the Rich enough site.

Source: CBS "Table 4.9 Average Monthly Prices of Rent (NIS), by Residential District, Big Cities and
Size Group (Rooms)", Price Statistics Monthly No. 7/2026, latest quarter 2026 Q2. In Israeli usage a
"3-room" flat is a living room plus two bedrooms; the table's size group "2.5-3" is the one used here.
The figure is the CBS consumer-price survey average over rented dwellings; it mixes in estimated
changes for dwellings not re-priced in the quarter, so it runs below what a new tenant is asked.

Run: uv run tools/world/rent/mena-eurasia-il-cbs.py        (prints rows as CSV)
"""

import csv
import pathlib
import re
import ssl
import sys
import urllib.request

import pdfplumber

REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "tools" / "world"))
from places import city_code  # noqa: E402

FILE = REPO / "cache" / "il-cbs-rent" / "2026_price09a_a4_9_e.pdf"
URL = "https://www.cbs.gov.il/he/publications/Madad/DocLib/2026/price09a/a4_9_e.pdf"
SOURCE_ID = "il-cbs-rent"
QUARTER_COLUMN = 8  # 0-based index of the pairs: 2026 Q2 is the ninth (price, error) pair

SOURCES = [
    {
        "source_id": SOURCE_ID,
        "publisher": "Central Bureau of Statistics, Israel",
        "title": "Table 4.9 Average Monthly Prices of Rent (NIS), by Residential District, Big Cities and Size Group (Rooms), Price Statistics Monthly 7/2026",
        "url": URL,
        "licence": "CBS publication, free to read; no licence stated",
        "retrieved": "2026-11-17",
        "period": "2026-Q2",
        "note": "Consumer price survey of rented dwellings; covers Israel only (not the West Bank or Gaza).",
    }
]

DISTRICTS = {"Jerusalem District": "IL-JM", "North District": "IL-Z", "Haifa District": "IL-HA", "center District": "IL-M",
             "Tel Aviv District": "IL-TA", "South District": "IL-D"}
CITIES = {"Tel Aviv": "Tel Aviv", "Jerusalem": "Jerusalem", "Haifa": "Haifa", "Rishon Lezion": "Rishon LeZion", "Petah Tiqwa": "Petah Tikva",
          "Ashdod": "Ashdod", "Netanya": "Netanya", "Beer Sheva": "Beersheba", "Holon": "Holon", "Bnei Brak": "Bnei Brak", "Ramat Gan": "Ramat Gan",
          "Ashkelon": "Ashkelon", "Rehovot": "Rehovot", "Bat Yam": "Bat Yam", "Herzlliya": "Herzliya", "Kfar Saba": "Kfar Saba", "Hadera": "Hadera",
          "Bet Shemesh": "Bet Shemesh"}


def text() -> str:
    if not FILE.exists():
        FILE.parent.mkdir(parents=True, exist_ok=True)
        context = ssl.create_default_context()
        FILE.write_bytes(urllib.request.urlopen(urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"}), context=context, timeout=120).read())
    with pdfplumber.open(FILE) as pdf:
        return "\n".join(page.extract_text(layout=True) or "" for page in pdf.pages)


def latest(line_numbers: str) -> float:
    pairs = re.findall(r"([\d,]+\.\d)\s+(\d+)", line_numbers)
    return float(pairs[QUARTER_COLUMN][0].replace(",", ""))


def blocks() -> dict[str, float]:
    """Area name -> average rent of the '2.5-3' size group in the latest quarter."""
    result, area = {}, None
    for line in text().splitlines():
        head = re.match(r"\s+([A-Za-z ]+?)\s*-\s*\d+\s+([\d,]+\.\d.*)$", line)
        size = re.match(r"\s+2\.5-3\s+(.*)$", line)
        if head:
            area = head.group(1).strip()
        elif size and area:
            result[area] = latest(size.group(1))
        elif re.match(r"\s+(Total|Residential Districts|Big cities)", line):
            area = "Total" if "Total" in line else None
    return result


def rows() -> list[dict]:
    data = blocks()
    common = dict(currency="ILS", unit="per_month", period="2026-Q2", source_id=SOURCE_ID)
    note = "Average over rented 3-room (CBS group 2.5-3 rooms) dwellings in the CBS price survey, not a sample of new lets."
    out = [{**common, "place_code": "PS", "amount": round(data["Total"]), "measured_for": "Israel, national average (the West Bank and Gaza are not covered)", "note": note}]
    for name, iso in DISTRICTS.items():
        out.append({**common, "place_code": iso, "amount": round(data[name]), "measured_for": f"{name.title().replace('Center', 'Central')} of Israel, average of 3-room flats", "note": note})
    for name, geonames in CITIES.items():
        out.append({**common, "place_code": city_code(geonames, "IL"), "amount": round(data[name]), "measured_for": f"{geonames}, whole city, average of 3-room flats", "note": note})
    return out


if __name__ == "__main__":
    out = csv.DictWriter(sys.stdout, fieldnames=["place_code", "amount", "currency", "unit", "period", "measured_for", "source_id", "note"])
    out.writeheader()
    out.writerows(rows())
