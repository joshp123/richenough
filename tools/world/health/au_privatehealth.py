"""Australian private health insurance couple premiums from the official PrivateHealth.gov.au open data.

Written by AI on 2026.11.18 by model claude sonnet 5.5, as research helper for the agent that owns the world data.

Source: Private Health Insurance Ombudsman, data.gov.au dataset "private-health-insurance"
(Creative Commons Attribution 3.0 Australia). One zip a month with every product published on
PrivateHealth.gov.au. This script downloads the newest zip into cache/au-privatehealth-open-data/ if the
zip is missing, reads "Combined Open *.xml" (hospital plus extras, open to new members), keeps products for
two adults and no children, and prints the median monthly premium (PremiumNoRebate, before rebate and
Lifetime Health Cover loading) by hospital tier for one state.

Run: python3 tools/world/health/au_privatehealth.py [STATE]    (default NSW; ALL, VIC, QLD, WA, SA, TAS, NT)
"""

import csv
import json
import re
import statistics
import sys
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

API = "https://data.gov.au/data/api/3/action/package_show?id=private-health-insurance"
CACHE = Path(__file__).resolve().parents[3] / "cache" / "au-privatehealth-open-data"
NS = "{http://admin.privatehealth.gov.au/ws/Schemas}"

SOURCES = [
    {
        "source_id": "au-privatehealth-open-data",
        "publisher": "Private Health Insurance Ombudsman (PrivateHealth.gov.au) via data.gov.au",
        "title": "PrivateHealth.gov.au monthly product data (premiums, hospital tier, excess, who is covered)",
        "url": "https://data.gov.au/data/dataset/private-health-insurance",
        "licence": "Creative Commons Attribution 3.0 Australia",
        "retrieved": "2026-11-17",
        "period": "Release of 2026-11-02",
        "note": "Community rated: premium does not depend on age. PremiumNoRebate is per month.",
    }
]


def fetch_latest_zip() -> Path:
    CACHE.mkdir(parents=True, exist_ok=True)
    existing = sorted(CACHE.glob("privatehealth-*.zip"))
    if existing:
        return existing[-1]
    with urllib.request.urlopen(API) as r:
        resources = json.load(r)["result"]["resources"]
    latest = sorted(resources, key=lambda x: x.get("created", ""))[-1]
    target = CACHE / latest["url"].rsplit("/", 1)[-1]
    urllib.request.urlretrieve(latest["url"], target)
    return target


def couple_products(zip_path: Path, state: str):
    with zipfile.ZipFile(zip_path) as z:
        name = next(n for n in z.namelist() if n.startswith("Combined Open") and n.endswith(".xml"))
        with z.open(name) as f:
            for _, el in ET.iterparse(f, events=("end",)):
                if el.tag != NS + "Product":
                    continue
                who = ET.tostring(el.find(NS + "WhoIsCovered"), encoding="unicode")
                only_with = ET.tostring(el.find(NS + "OnlyAvailableWith"), encoding="unicode")
                is_couple = 'NumberOfAdults="2"' in who and 'Title="Child" Covered="false"' in who
                if is_couple and "NotApplicable" in only_with and el.find(NS + "State").text == state:
                    hc = el.find(NS + "HospitalCover")
                    yield {
                        "product_code": el.get("ProductCode"),
                        "fund": el.find(NS + "FundCode").text,
                        "name": el.find(NS + "Name").text,
                        "hospital_tier": hc.find(NS + "HospitalTier").text,
                        "excess_type": el.find(NS + "Excesses").get("ExcessType"),
                        "premium_no_rebate_per_month_aud": el.find(NS + "PremiumNoRebate").text,
                    }
                el.clear()


if __name__ == "__main__":
    state = sys.argv[1] if len(sys.argv) > 1 else "NSW"
    products = list(couple_products(fetch_latest_zip(), state))
    out = CACHE / f"derived-{state.lower()}-couple-combined-open.csv"
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(products[0]))
        w.writeheader()
        w.writerows(products)
    for tier in ("Gold", "SilverPlus", "Silver", "BronzePlus"):
        v = [float(p["premium_no_rebate_per_month_aud"]) for p in products if p["hospital_tier"] == tier]
        if v:
            print(f"{state} {tier}: n={len(v)} median={statistics.median(v):.2f} min={min(v):.2f} max={max(v):.2f}")
