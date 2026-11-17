"""Two-bed rent for four cities where no portal publishes a median, computed from current listing pages.

Written by AI on 2026.11.17 by model claude sonnet 5.5. Cities: George Town (Rummah), Da Nang (FazWaz Vietnam),
Colombo (LankaPropertyWeb) and Phnom Penh's Chamkarmon district (realestate.com.kh). Each is the median asking rent
of the two-bedroom flats on the first result pages, saved in cache/<source_id>/ so the sample can be re-read.
Asking rents on one portal, not signed leases: every row says so in `note`.

Run:  python3 -I tools/world/rent/south-southeast-asia.py   (stdlib only; downloads missing pages, 1.5 s apart)
"""

import csv
import datetime
import html
import pathlib
import re
import statistics
import sys
import time
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from places import city_code  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[3]
CACHE = REPO / "cache"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"

SOURCES = [
    dict(source_id="my-rummah-rent", publisher="Rummah.my", title="Condos for rent in George Town, Penang (listing pages 1-7)",
         url="https://rummah.my/condo-for-rent/penang/george-town", licence="free to read, no licence stated", retrieved="2026-11-17",
         period="2026-11", note="Agent listings only. Page says 'As of 18 Nov 2026' (Malaysian time). Median taken by script from the 2-bed listings."),
    dict(source_id="vn-fazwaz-danang-rent", publisher="FazWaz Vietnam", title="2 bedroom property for rent in Da Nang (listing pages 1-6)",
         url="https://www.fazwaz.vn/2-bedroom-property-for-rent/vietnam/da-nang", licence="free to read, no licence stated", retrieved="2026-11-17",
         period="2026-11", note="Prices shown in EUR by the portal (converted from VND or USD). Median taken by script from apartment listings only."),
    dict(source_id="lk-lankapropertyweb-rent", publisher="LankaPropertyWeb", title="Apartments for rent, Colombo district (listing pages 1-15)",
         url="https://www.lankapropertyweb.com/rentals/colombo/apartment/", licence="free to read, no licence stated", retrieved="2026-11-17",
         period="2026-11", note="Colombo district includes Mount Lavinia and the suburbs; the two-bed stock is mostly new towers. Prices in LKR per month."),
    dict(source_id="kh-realestate-kh-rent", publisher="realestate.com.kh", title="Apartments and condos for rent in Chamkarmon, Phnom Penh (listing pages 1-6)",
         url="https://www.realestate.com.kh/rent/chamkarmon/apartment/", licence="free to read, no licence stated", retrieved="2026-11-17",
         period="2026-11", note="Chamkarmon khan holds BKK1, Tonle Bassac and Toul Tum Poung. Median taken by script from the 2-bed listings."),
]


def _page(source_id: str, name: str, url: str) -> str:
    path = CACHE / source_id / name
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en"})
        path.write_bytes(urllib.request.urlopen(req, timeout=60).read())
        time.sleep(1.5)
    return path.read_text(encoding="utf-8", errors="ignore")


def _text(raw: str) -> str:
    raw = re.sub(r"<script.*?</script>|<style.*?</style>", "", raw, flags=re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw)))


def _row(place_code, amounts, currency, measured_for, source_id, note):
    return dict(place_code=place_code, amount=round(statistics.median(amounts)), currency=currency, unit="per_month",
                period="2026-11", measured_for=measured_for, source_id=source_id,
                note=f"{note} Median asking rent of {len(amounts)} listings (range {min(amounts):,} to {max(amounts):,}).")


def george_town() -> dict:
    base = "https://rummah.my/condo-for-rent/penang/george-town"
    seen = {}
    for p in range(1, 8):
        url = base if p == 1 else f"{base}/page/{p}"
        text = _text(_page("my-rummah-rent", f"p{p}.html", url))
        text = text[text.find("listings matching this search"):]
        for title, price, beds, sqft in re.findall(r"(.{3,160}?) George Town, Penang RM ([\d,]+)/mo (\d) bed · \d bath(?: · ([\d,]+) sqft)?", text):
            if beds == "2":
                seen[(title[-50:], price, sqft)] = int(price.replace(",", ""))
    return _row(city_code("George Town", "MY"), list(seen.values()), "MYR", "George Town, Penang, condominium and apartment listings with two bedrooms",
                "my-rummah-rent", "Asking rents on one portal, all posted by agents; not signed leases.")


def da_nang() -> dict:
    seen = {}
    for p in range(1, 7):
        text = _text(_page("vn-fazwaz-danang-rent", f"p{p}.html", f"https://www.fazwaz.vn/2-bedroom-property-for-rent/vietnam/da-nang?page={p}"))
        pattern = r"Updated [^€]{0,12}ago ([^€]{3,80}?)€([\d,]+)/mo \(€([\d.,]+)/SqM\) (2 Bedroom (\w+) [^ ]* ?rent[^€]{0,70})"
        for district, price, psm, title, kind in re.findall(pattern, text):
            if kind == "Apartment":
                seen[(district.strip(), price, psm, title[:50])] = int(price.replace(",", ""))
    return _row(city_code("Da Nang", "VN"), list(seen.values()), "EUR", "Da Nang (Hai Chau, Son Tra and Ngu Hanh Son districts), two-bedroom apartment listings",
                "vn-fazwaz-danang-rent", "Asking rents on one portal, shown in EUR by the portal; not signed leases. Most listings are in the beach districts, not the Han river centre.")


def colombo() -> dict:
    cards = {}
    for p in range(1, 16):
        url = ("https://www.lankapropertyweb.com/rentals/colombo/apartment/" if p == 1 else
               f"https://www.lankapropertyweb.com/rentals/index.php?page={p}&location=_Colombo&property-type=Apartment&searchbox=Colombo+district")
        raw = _page("lk-lankapropertyweb-rent", f"p{p}.html", url)
        for card in raw.split('class="listing-summery"')[1:]:
            card = card[:6000]
            beds = re.search(r'alt="bed icon"[^>]*>\s*<span class="count">(\d+)', card)
            ad = re.search(r'data-advertid="(\d+)"', card)
            price = re.search(r'listing-price">\s*Rs\.? ([\d,]+)\s*<span class="span_psf">\s*Per (Month|SQFT)', card)
            if ad and price and beds and beds.group(1) == "2" and price.group(2) == "Month":
                cards[ad.group(1)] = int(price.group(1).replace(",", ""))
    return _row(city_code("Colombo", "LK"), list(cards.values()), "LKR", "Colombo district, two-bedroom apartment listings (mostly Colombo 1 to 7 towers)",
                "lk-lankapropertyweb-rent", "Asking rents on one portal; not signed leases.")


def phnom_penh() -> dict:
    seen = {}
    for p in range(1, 7):
        url = "https://www.realestate.com.kh/rent/chamkarmon/apartment/" + ("" if p == 1 else f"?page={p}")
        text = _text(_page("kh-realestate-kh-rent", f"chamkarmon_apartment_p{p}.html", url))
        for price, title, beds, area, kind, place in re.findall(
                r"\$([\d,]+) ([^$]{3,200}?) (\d) bed (\d+)m² (Apartment|Condo|Serviced Apartment) ([^$]{3,80}?), (?:Chamkarmon|Daun Penh|7 Makara|Toul Kork)", text):
            if beds == "2":
                seen[(title[:60], price, area, place)] = int(price.replace(",", ""))
    return _row(city_code("Phnom Penh", "KH"), list(seen.values()), "USD", "Phnom Penh, Chamkarmon district (BKK1, Tonle Bassac), two-bedroom apartment and condo listings",
                "kh-realestate-kh-rent", "Asking rents on one portal, first six result pages (featured listings come first); not signed leases.")


def _as_country(row: dict, iso2: str, city: str) -> dict:
    return dict(row, place_code=iso2, measured_for=f"{city} (the country's main city): {row['measured_for']}")


def rows() -> list[dict]:
    colombo_row, phnom_penh_row = colombo(), phnom_penh()
    return [george_town(), da_nang(), colombo_row, _as_country(colombo_row, "LK", "Colombo"),
            phnom_penh_row, _as_country(phnom_penh_row, "KH", "Phnom Penh")]


if __name__ == "__main__":
    out = rows()
    writer = csv.DictWriter(sys.stdout, fieldnames=list(out[0]))
    writer.writeheader()
    writer.writerows(out)
