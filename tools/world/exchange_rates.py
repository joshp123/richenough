"""Exchange rates for every currency in the world tables, in units per US dollar.

Primary: IMF exchange rates, monthly average of national currency per US dollar.
Fallback where the IMF series stops early: US Treasury Reporting Rates of Exchange (quarter-end).
The euro comes from the ECB's reference rates; currencies pegged to the euro or the dollar follow their peg.
"""

import csv
import io
import json
import zipfile

from lib import CACHE, countries, fmt, imf_sdmx, iso3_to_iso2

# Fixed pegs, units per anchor currency, set by treaty or currency board.
EURO_PEGS = {"XOF": 655.957, "XAF": 655.957, "KMF": 491.96775, "BAM": 1.95583, "CVE": 110.265, "XPF": 119.33174}
# Currencies issued at par with sterling.
STERLING_PAR = {"FKP", "SHP", "GIP"}
DOLLAR_PEGS = {"USD": 1.0, "XCD": 2.7, "PAB": 1.0, "BMD": 1.0, "KYD": 1 / 1.2, "AWG": 1.79, "XCG": 1.79, "BSD": 1.0}

# Treasury country names that differ from GeoNames names.
TREASURY_NAMES = {
    "Antigua & Barbuda": "AG", "Bosnia": "BA", "Cape Verde": "CV", "Cote D'Ivoire": "CI", "Curacao": "CW",
    "Democratic Republic Of Congo": "CD", "Congo": "CG", "Euro Zone": None, "Guinea Bissau": "GW", "Korea": "KR",
    "Republic Of North Macedonia": "MK", "Sao Tome & Principe": "ST", "Somali": "SO", "St. Lucia": "LC",
    "Trinidad & Tobago": "TT", "Western Samoa": "WS", "Timor-Leste": "TL", "Micronesia": "FM", "Laos": "LA",
    "Gambia": "GM", "Vietnam": "VN", "Russia": "RU", "Syria": "SY", "Iran": "IR", "Taiwan": "TW", "Brunei": "BN",
    "Eswatini": "SZ", "Myanmar": "MM", "Czech Republic": "CZ", "Turkey": "TR", "Bahamas": "BS", "Hong Kong": "HK",
    "Macao": "MO", "Kyrgyzstan": "KG", "Moldova": "MD", "Bolivia": "BO", "Tanzania": "TZ", "Venezuela": "VE",
    "St. Kitts & Nevis": "KN", "St. Vincent & Grenadines": "VC", "United Kingdom": "GB", "United Arab Emirates": "AE",
}

CUBA_HOUSEHOLD = {
    "source_id": "bcc-household-exchange",
    "publisher": "Banco Central de Cuba",
    "title": "Tipo de cambio del segmento III para personas naturales, 17 de noviembre de 2026",
    "url": "https://api.bc.gob.cu/v1/tasas-de-cambio/activas-por-fecha?fecha=2026-11-17",
    "licence": "Published central bank quotation, numerical facts",
    "retrieved": "2026-11-18",
    "period": "2026-11-17",
    "note": "USD tasaEspecial, the floating Segment III rate for individuals. The accounting and enterprise rates are separate.",
}

SOURCES = [
    CUBA_HOUSEHOLD,
    {
        "source_id": "imf-er",
        "publisher": "International Monetary Fund",
        "title": "Exchange Rates (ER) dataset: national currency per US dollar, period average and end of period, monthly",
        "url": "https://data.imf.org/en/datasets/IMF.STA:ER",
        "licence": "IMF terms of use: free reuse with attribution (https://www.imf.org/external/terms.htm)",
        "retrieved": "2026-11-17",
        "period": "2020-01 to 2026-10",
        "note": "Keyless SDMX API, api.imf.org. Some series stop before 2026; the Treasury rates fill those.",
    },
    {
        "source_id": "us-treasury-rates-of-exchange",
        "publisher": "US Department of the Treasury, Bureau of the Fiscal Service",
        "title": "Treasury Reporting Rates of Exchange",
        "url": "https://fiscaldata.treasury.gov/datasets/treasury-reporting-rates-exchange/",
        "licence": "Public domain (US Government work)",
        "retrieved": "2026-11-17",
        "period": "2025-03-31 to 2026-09-30, quarterly",
        "note": "Units of foreign currency per US dollar at quarter end, for every currency the US government transacts in.",
    },
    {
        "source_id": "ecb-euro-reference-rates",
        "publisher": "European Central Bank",
        "title": "Euro foreign exchange reference rates, full history",
        "url": "https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html",
        "licence": "Free reuse with attribution (ECB statistics reuse policy)",
        "retrieved": "2026-11-17",
        "period": "daily to 2026-11",
        "note": "Used for the US dollar per euro rate and so for every currency pegged to the euro.",
    },
]


# These tables freeze the inputs available on the original retrieval date.
AS_OF = "2026-11-17"


def month_key(period: str) -> str:
    """'2026-M09' -> '2026-09'."""
    return period.replace("-M", "-")


def imf_monthly() -> dict[str, dict[str, float]]:
    """ISO2 -> {YYYY-MM: national currency per USD, monthly average}."""
    raw = imf_sdmx(CACHE / "imf-er" / "xdc-usd-monthly-average.xml")
    to2 = iso3_to_iso2()
    return {to2[c]: {month_key(p): v for p, v in s.items() if month_key(p) <= AS_OF[:7]} for c, s in raw.items() if c in to2}


def ecb_usd_per_eur_monthly() -> dict[str, float]:
    with zipfile.ZipFile(CACHE / "ecb-euro-reference-rates" / "eurofxref-hist.zip") as z:
        text = z.read(z.namelist()[0]).decode()
    sums: dict[str, list[float]] = {}
    for row in csv.DictReader(io.StringIO(text)):
        value = row.get("USD", "").strip()
        if row["Date"] <= AS_OF and value and value != "N/A":
            sums.setdefault(row["Date"][:7], []).append(float(value))
    return {m: sum(v) / len(v) for m, v in sums.items()}


def treasury() -> dict[str, dict[str, float]]:
    """ISO2 -> {effective date: units per USD}, including Treasury amendments."""
    data = json.loads((CACHE / "us-treasury-rates-of-exchange" / "since-2025.json").read_text())["data"]
    by_name = {c["name"]: iso2 for iso2, c in countries().items()}
    out: dict[str, dict[str, float]] = {}
    for r in data:
        name = r["country"]
        iso2 = TREASURY_NAMES[name] if name in TREASURY_NAMES else by_name.get(name)
        if iso2 == "CU" and r["currency"] != "Peso":
            continue  # Treasury also reports the Chavito at par. It is not CUP.
        if iso2 and r["effective_date"] <= AS_OF:
            out.setdefault(iso2, {})[r["effective_date"]] = float(r["exchange_rate"])
    return out


def rates() -> dict[str, dict]:
    """Currency -> {'monthly': {YYYY-MM: per USD}, 'treasury': {date: per USD}, 'basis': text} for every country currency."""
    imf = imf_monthly()
    tre = treasury()
    usd_per_eur = ecb_usd_per_eur_monthly()
    eur = {m: 1 / v for m, v in usd_per_eur.items()}
    out: dict[str, dict] = {}
    for iso2, c in countries().items():
        cur = c["currency"]
        if not cur or cur in out:
            continue
        if cur == "EUR":
            out[cur] = {"monthly": eur, "basis": "ECB reference rate, monthly average", "source_id": "ecb-euro-reference-rates"}
        elif cur in EURO_PEGS:
            out[cur] = {"monthly": {m: v * EURO_PEGS[cur] for m, v in eur.items()}, "basis": f"fixed at {EURO_PEGS[cur]} per euro, ECB euro rate", "source_id": "ecb-euro-reference-rates"}
        elif cur in DOLLAR_PEGS:
            out[cur] = {"monthly": {m: DOLLAR_PEGS[cur] for m in eur}, "basis": f"fixed at {fmt(DOLLAR_PEGS[cur])} per US dollar", "source_id": "us-treasury-rates-of-exchange"}
    # Floating currencies: the IMF series of the most populous country using the currency.
    by_currency: dict[str, list[str]] = {}
    for iso2, c in countries().items():
        by_currency.setdefault(c["currency"], []).append(iso2)
    for cur, members in by_currency.items():
        if not cur or cur in out:
            continue
        members.sort(key=lambda i: -countries()[i]["population"])
        series = next((imf[i] for i in members if i in imf and imf[i]), {})
        treasury_series = next((tre[i] for i in members if i in tre), {})
        out[cur] = {"monthly": series, "treasury": treasury_series, "basis": "IMF monthly average", "source_id": "imf-er"}
    for cur in STERLING_PAR:
        out[cur] = {**out["GBP"], "basis": "at par with the pound sterling, IMF monthly average for GBP"}
    for cur, r in out.items():
        r.setdefault("treasury", {})
    return out


def rate_for_months(entry: dict, months: list[str]) -> tuple[float | None, str, str]:
    """Average units per USD over `months`; falls back to the nearest Treasury quarter-end rate. Returns (rate, period, source_id)."""
    got = [entry["monthly"][m] for m in months if m in entry["monthly"]]
    if len(got) == len(months):
        return sum(got) / len(got), f"{months[0]} to {months[-1]}" if len(months) > 1 else months[0], entry["source_id"]
    treasury_rates = entry.get("treasury") or {}
    if treasury_rates:
        last = months[-1]
        candidates = sorted(d for d in treasury_rates if d[:7] <= last)
        if candidates:
            d = candidates[-1]
            return treasury_rates[d], d, "us-treasury-rates-of-exchange"
    return None, "", ""


def build_table() -> list[dict]:
    """The exchange-rates table: one row per currency, the latest monthly average (or Treasury rate), with date and source."""
    rows = []
    for cur, entry in sorted(rates().items()):
        monthly = entry["monthly"]
        latest = max(monthly) if monthly else None
        tre = entry.get("treasury") or {}
        tre_latest = max(tre) if tre else None
        if cur == "CUP":
            amount, period = 832, CUBA_HOUSEHOLD["period"]
            source_id, basis = CUBA_HOUSEHOLD["source_id"], "Banco Central de Cuba, USD household rate, segment III"
        elif latest and latest >= "2026-07":
            amount, period, source_id, basis = monthly[latest], latest, entry["source_id"], entry["basis"]
        elif tre_latest:
            amount, period, source_id, basis = tre[tre_latest], tre_latest, "us-treasury-rates-of-exchange", "Treasury reporting rate on its effective date"
        elif latest:
            amount, period, source_id, basis = monthly[latest], latest, entry["source_id"], f"{entry['basis']}, stale"
        else:
            continue
        note = basis
        if tre_latest and source_id == entry["source_id"] and latest:
            gap = monthly[latest] / tre[tre_latest] - 1
            if abs(gap) > 0.05:
                note += f"; Treasury rate on {tre_latest} differs by {gap:+.0%}"
        rows.append({"place_code": "", "amount": fmt(amount, 6), "currency": cur, "unit": "per_usd", "period": period,
                     "measured_for": "units of this currency per US dollar", "source_id": source_id, "note": note})
    return rows


def current_rates() -> dict[str, float]:
    """Local units per USD at the same precision and vintage used by the page."""
    return {r["currency"]: float(r["amount"]) for r in build_table()}


if __name__ == "__main__":
    from lib import upsert_sources, write_table

    write_table("exchange-rates", build_table())
    upsert_sources(SOURCES)
