#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""South Korea: rent of a 60-85 m2 apartment on a NEW contract, from the Ministry of Land (MOLIT) actual-transaction register.

Written by AI on 2026.11.17 by model claude sonnet 5.5.

Source: MOLIT 실거래가 공개시스템 (rt.molit.go.kr), "자료제공" CSV download for apartment rentals (아파트 전월세).
Keyless: the site's own download form posts to /pt/xls/ptXlsCSVDown.do. Nationwide downloads are limited to one month,
a province to one year, so we fetch one file per province (16 requests), contract dates 2025-10-01 to 2026-09-30,
apartments, area class "60 m2 < area <= 85 m2" (the site's own class). Files go to cache/kr-molit-rtms-2026/ once;
delete the folder to fetch again. The CSVs are untrusted data: this script only parses them as text.

Every row of the register is one lease reported to the state (leases above KRW 60m deposit or KRW 300,000 rent, in
cities and the capital region, must be reported within 30 days; small low-end wolse and rural 군 are under-reported).

What the figures are (see rows()):
  Use only contracts marked 신규 (a NEW contract; renewals 갱신 are capped by law at +5% and are not a "new let")
  and 월세 (wolse: a deposit plus monthly rent). Jeonse (deposit only, no rent) is shown in the note, not in the amount.
  amount = MEDIAN over those contracts of  monthly rent + deposit x r / 12
  where r is KREB's market jeonse-to-wolse conversion rate for apartments of 60-85 m2 in that contract's province
  (R-ONE table A_2024_00159, latest month, see kr_reb_rone.py). That puts every wolse flat on a zero-deposit footing:
  a higher deposit buys a lower rent, and the formula adds the deposit's cost back at the market exchange rate.
  The note gives median rent and median deposit separately, and the amount at the statutory cap
  (Bank of Korea base rate 3.00% since 2026-08-27 + 2 points = 5.0%; Housing Lease Protection Act art. 7-2 and
  Enforcement Decree art. 9) as a sensitivity.

Window: contracts dated 2026-04 to 2026-09 (6 months); where that gives fewer than MIN_N contracts, 2025-10 to
2026-09 (12 months); where that is still fewer than MIN_N, no row. Run directly to print the rows as CSV;
`--districts` prints the same statistic for every 시군구 (city/district) and writes east-asia-korea.districts.csv.
"""

import csv
import io
import json
import pathlib
import statistics
import sys
import time
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from places import city_code  # noqa: E402
import kr_reb_rone  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[3]
CACHE = REPO / "cache" / "kr-molit-rtms-2026"
HERE = pathlib.Path(__file__).resolve().parent
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
SOURCE_ID = "kr-molit-rtms-2026"
PAGE = "https://rt.molit.go.kr/pt/xls/xls.do?mobileAt="
FROM, TO = "2025-10-01", "2026-09-30"
SHORT = ("202604", "202609")
MIN_N = 30
STATUTORY = 5.0  # Bank of Korea base rate 3.00% (since 2026-08-27, bok.or.kr) + 2.00 points (Enforcement Decree art. 9(2))

SOURCES = [{
    "source_id": SOURCE_ID,
    "publisher": "Ministry of Land, Infrastructure and Transport (국토교통부), Real Transaction Price Disclosure System",
    "title": "Apartment lease (전월세) real transaction prices, contracts 2025-10-01 to 2026-09-30, 60-85 m2, CSV download per province",
    "url": PAGE,
    "licence": "Public data of the Korean government; the download page states no licence. The download page says the data has no legal force and is for reference, and that figures aggregated from it should not be published as official statistics (official aggregates are by report date).",
    "retrieved": "2026-11-17",
    "period": "2026-04 to 2026-09 (6-month window; 2025-10 to 2026-09 where a place has under 30 contracts)",
    "note": "Register of reported leases: new (신규) wolse contracts only for the amount. Under-reports small low-end wolse and rural counties. The newest month is incomplete because reports arrive up to 30 days late.",
}, {
    "source_id": "kr-bok-base-rate",
    "publisher": "Bank of Korea (한국은행)",
    "title": "Bank of Korea base rate history (3.00% since 2026-08-27)",
    "url": "https://www.bok.or.kr/portal/singl/baseRate/list.do?dataSeCd=01&menuNo=200643",
    "licence": "Free to read, no licence stated",
    "retrieved": "2026-11-17",
    "period": "2026-08-27 onwards",
    "note": "Used only for the sensitivity 'statutory cap' = base rate + 2 points = 5.0%. Page saved in cache/kr-bok-base-rate/.",
}, {
    "source_id": "kr-hlpa-decree-art9",
    "publisher": "korea.legal (unofficial English/Korean mirror of the statute; official text at law.go.kr)",
    "title": "Enforcement Decree of the Housing Lease Protection Act, Article 9 (rate for converting a deposit to monthly rent): 10% a year, and base rate + 2%, whichever is lower (Act art. 7-2)",
    "url": "https://korea.legal/wiki/주택임대차보호법-시행령-제9조/",
    "licence": "Statute text is public; mirror states no licence",
    "retrieved": "2026-11-17",
    "period": "in force since 2020-09-29",
    "note": "The cap binds conversions of existing leases and renewals; it does not bind the rent on a new contract. Page saved in cache/kr-bok-base-rate/.",
}] + kr_reb_rone.SOURCES

# download-form province code -> ISO 3166-2 (12000 is the merged 전남광주 and is split on the address)
SIDO = {
    "11000": "KR-11", "12000": "KR-29/46", "26000": "KR-26", "27000": "KR-27", "28000": "KR-28", "30000": "KR-30",
    "31000": "KR-31", "36000": "KR-50", "41000": "KR-41", "43000": "KR-43", "44000": "KR-44", "47000": "KR-47",
    "48000": "KR-48", "50000": "KR-49", "51000": "KR-42", "52000": "KR-45",
}
# main cities: (Korean 시 name as in the address, ISO province, GeoNames name)
CITIES = [
    ("수원시", "KR-41", "Suwon"), ("성남시", "KR-41", "Seongnam"), ("고양시", "KR-41", "Goyang"), ("용인시", "KR-41", "Yongin"),
    ("부천시", "KR-41", "Bucheon"), ("안산시", "KR-41", "Ansan"), ("안양시", "KR-41", "Anyang"), ("화성시", "KR-41", "Hwaseong"),
    ("평택시", "KR-41", "Pyeongtaek"), ("의정부시", "KR-41", "Uijeongbu"), ("파주시", "KR-41", "Paju"),
    ("김포시", "KR-41", "Gimpo"), ("광명시", "KR-41", "Gwangmyeong"), ("하남시", "KR-41", "Hanam"),
    ("창원시", "KR-48", "Changwon"), ("김해시", "KR-48", "Gimhae"), ("진주시", "KR-48", "Jinju"), ("양산시", "KR-48", "Yangsan"),
    ("청주시", "KR-43", "Cheongju"), ("충주시", "KR-43", "Chungju"), ("천안시", "KR-44", "Cheonan"), ("아산시", "KR-44", "Asan"),
    ("전주시", "KR-45", "Jeonju"), ("익산시", "KR-45", "Iksan"), ("군산시", "KR-45", "Gunsan"),
    ("포항시", "KR-47", "Pohang"), ("구미시", "KR-47", "Gumi"), ("경산시", "KR-47", "Gyeongsan"),
    ("제주시", "KR-49", "Jeju"), ("춘천시", "KR-42", "Chuncheon"), ("원주시", "KR-42", "Wonju"), ("강릉시", "KR-42", "Gangneung"),
    ("순천시", "KR-46", "Suncheon"), ("여수시", "KR-46", "Yeosu"), ("목포시", "KR-46", "Mokpo"),
]
METRO = {"Busan": "KR-26", "Daegu": "KR-27", "Incheon": "KR-28", "Gwangju": "KR-29", "Daejeon": "KR-30", "Ulsan": "KR-31", "Sejong": "KR-50"}
SEOUL_CENTRE = ("종로구", "중구", "용산구")  # KREB's 도심권 (central zone)
NAMES = kr_reb_rone.NAMES


def _download(code: str) -> pathlib.Path:
    path = CACHE / f"{code}.csv"
    if path.exists():
        return path
    CACHE.mkdir(parents=True, exist_ok=True)
    import http.cookiejar
    import urllib.parse
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    opener.open(urllib.request.Request(PAGE, headers={"User-Agent": UA}), timeout=60).read()
    form = urllib.parse.urlencode({
        "srhThingNo": "A", "srhDelngSecd": "2", "srhAddrGbn": "1", "srhLfstsSecd": "1", "sidoNm": "", "sggNm": "", "emdNm": "",
        "loadNm": "", "areaNm": "", "hsmpNm": "", "mobileAt": "", "srhFromDt": FROM, "srhToDt": TO, "srhRoadNm": "",
        "srhFromAmount": "", "srhToAmount": "", "srhSidoCd": code, "srhSggCd": "", "srhEmdCd": "", "srhLoadCd": "",
        "srhHsmpCd": "", "srhArea": "", "srhLrArea": "2",
    }).encode()
    hdr = {"User-Agent": UA, "Referer": PAGE}
    check = json.loads(opener.open(urllib.request.Request("https://rt.molit.go.kr/pt/xls/ptXlsDownDataCheck.do", data=form, headers=hdr), timeout=120).read())
    if not check.get("cnt"):
        raise RuntimeError(f"MOLIT returned no contracts for {code}: {check}")
    data = opener.open(urllib.request.Request("https://rt.molit.go.kr/pt/xls/ptXlsCSVDown.do", data=form, headers=hdr), timeout=900).read()
    path.with_suffix(".part").write_bytes(data)
    path.with_suffix(".part").rename(path)
    time.sleep(2)
    return path


def _parse(code: str):
    """Yield dicts for each contract in a province file."""
    raw = _download(code).read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("cp949")
    rows = list(csv.reader(io.StringIO(text)))
    head = next(i for i, r in enumerate(rows) if r and r[0] == "NO")
    cols = {name: i for i, name in enumerate(rows[head])}
    for r in rows[head + 1:]:
        if len(r) < len(cols) or not r[0]:
            continue
        toks = r[cols["시군구"]].split()
        yield {
            "tok": toks, "kind": r[cols["전월세구분"]], "area": float(r[cols["전용면적(㎡)"]]),
            "ym": r[cols["계약년월"]], "deposit": float(r[cols["보증금(만원)"]].replace(",", "")) * 10_000,
            "rent": float(r[cols["월세금(만원)"]].replace(",", "")) * 10_000, "new": r[cols["계약구분"]],
        }


def _contracts():
    """All contracts with province ISO code and sigungu key. Gwangju (구) and South Jeolla (시/군) split on the address."""
    out = []
    for code, iso in SIDO.items():
        for c in _parse(code):
            t = c["tok"]
            prov = iso
            if iso == "KR-29/46":
                prov = "KR-29" if t[1].endswith("구") else "KR-46"
            c["prov"] = prov
            # city key: "수원시" for "경기도 수원시 장안구"; district key e.g. "강남구" for Seoul
            c["city"] = t[1]
            c["sgg"] = t[1] if not (len(t) > 2 and t[1].endswith("시") and t[2].endswith("구")) else f"{t[1]} {t[2]}"
            out.append(c)
    return out


def _median(xs):
    return statistics.median(xs)


def _stats(cs, rates, label_rate=None):
    """cs: contracts of one place. Returns the dict of statistics or None when n < MIN_N."""
    for window, ym in (("6m", lambda c: SHORT[0] <= c["ym"] <= SHORT[1]), ("12m", lambda c: True)):
        w = [c for c in cs if ym(c)]
        wolse = [c for c in w if c["kind"] == "월세" and c["new"] == "신규" and c["rent"] > 0]
        if len(wolse) >= MIN_N:
            break
    else:
        return None
    jeonse = [c for c in w if c["kind"] == "전세" and c["new"] == "신규"]
    eq = [c["rent"] + c["deposit"] * rates[c["prov"]] / 100 / 12 for c in wolse]
    eq_stat = [c["rent"] + c["deposit"] * STATUTORY / 100 / 12 for c in wolse]
    rate_med = _median([rates[c["prov"]] for c in wolse])
    return {
        "window": window, "n": len(wolse), "n_jeonse": len(jeonse), "rate": rate_med,
        "amount": round(_median(eq) / 1000) * 1000, "amount_stat": round(_median(eq_stat) / 1000) * 1000,
        "rent": _median([c["rent"] for c in wolse]), "deposit": _median([c["deposit"] for c in wolse]),
        "area": _median([c["area"] for c in wolse]),
        "jeonse_dep": _median([c["deposit"] for c in jeonse]) if jeonse else None,
        "months": ("2026-04/2026-09" if window == "6m" else "2025-10/2026-09"),
        "n_all_new": len([c for c in w if c["new"] == "신규"]),
    }


def _row(place, label, s, rates_desc):
    n_note = (f"{s['n']} new wolse contracts, {s['months']}" + ("" if s["window"] == "6m" else " (12-month window: fewer than 30 in 6 months)"))
    jeonse = (f" For reference, {s['n_jeonse']} new jeonse (no rent) contracts had a median deposit of KRW {s['jeonse_dep']:,.0f}; "
              f"at the same rate that deposit costs KRW {s['jeonse_dep'] * s['rate'] / 100 / 12:,.0f} a month. Jeonse is not in the amount."
              if s["jeonse_dep"] else "")
    return {
        "place_code": place, "amount": int(s["amount"]), "currency": "KRW", "unit": "per_month", "period": s["months"],
        "measured_for": f"{label}, apartments of 60-85 m2 (median {s['area']:.1f} m2), new wolse contracts reported to the state",
        "source_id": SOURCE_ID,
        "note": (f"Median, over {n_note}, of: monthly rent + deposit x conversion rate / 12, worked out per contract. "
                 f"The next two figures are separate medians and do not add up to the amount: median monthly rent KRW {s['rent']:,.0f}; median deposit KRW {s['deposit']:,.0f}; "
                 f"conversion rate {rates_desc} (KREB, apartments 60-85 m2, 2026-09). At the statutory cap of 5.0% (Bank of Korea base rate 3.00% + 2 points) "
                 f"the amount would be KRW {s['amount_stat']:,.0f}. Renewals (갱신, rent rise capped at 5%) and jeonse are excluded.{jeonse}"),
    }


def _rates():
    return {k: v[1] for k, v in kr_reb_rone.conversion_rates_60_85().items()}


def _places(cs):
    """Yield (place_code, label, contracts) for every row we publish."""
    yield "KR", "South Korea, all provinces pooled", cs
    for iso in kr_reb_rone.PROVINCES:
        if iso == "KR":
            continue
        yield iso, f"{NAMES[iso]}, whole province or metropolitan city", [c for c in cs if c["prov"] == iso]
    centre = [c for c in cs if c["prov"] == "KR-11" and c["city"] in SEOUL_CENTRE]
    yield city_code("Seoul", "KR"), "Seoul central zone (Jongno, Jung and Yongsan districts)", centre
    for geo, iso in METRO.items():
        yield city_code(geo, "KR"), f"{geo}, whole metropolitan city", [c for c in cs if c["prov"] == iso]
    for kr_name, iso, geo in CITIES:
        try:
            code = city_code(geo, "KR")
        except KeyError:  # GeoNames cities15000 has no Yongin
            continue
        yield code, f"{geo}, whole city (all its districts)", [c for c in cs if c["prov"] == iso and c["city"] == kr_name]


def rows() -> list[dict]:
    cs = _contracts()
    rates = _rates()
    out = []
    for place, label, subset in _places(cs):
        s = _stats(subset, rates)
        if s is None:
            continue
        iso = place if place.startswith("KR-") else None
        if place == "KR":
            lo, hi = min(rates[i] for i in rates if i != "KR"), max(rates[i] for i in rates if i != "KR")
            desc = f"of each contract's own province (range {lo}% to {hi}%)"
        elif iso:
            desc = f"{rates[iso]}%"
        else:
            provs = {c["prov"] for c in subset}
            desc = "/".join(f"{rates[p]}%" for p in sorted(provs)) + f" ({'/'.join(NAMES[p] for p in sorted(provs))} province rate)"
        out.append(_row(place, label, s, desc))
    return out


def districts() -> list[dict]:
    cs = _contracts()
    rates = _rates()
    res = []
    for prov in kr_reb_rone.PROVINCES:
        if prov == "KR":
            continue
        groups = {}
        for c in cs:
            if c["prov"] == prov:
                groups.setdefault(c["sgg"], []).append(c)
        for name, g in sorted(groups.items()):
            s = _stats(g, rates)
            if s:
                res.append({"province": prov, "sigungu": name, "n": s["n"], "window": s["window"], "median_rent": int(s["rent"]),
                            "median_deposit": int(s["deposit"]), "rate_pct": s["rate"], "amount": int(s["amount"]),
                            "amount_at_5pct": int(s["amount_stat"]), "median_area_m2": round(s["area"], 1)})
    return res


FIELDS = ["place_code", "amount", "currency", "unit", "period", "measured_for", "source_id", "note"]

if __name__ == "__main__":
    if "--districts" in sys.argv:
        d = districts()
        path = HERE / "east-asia-korea.districts.csv"
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(d[0]))
            w.writeheader()
            w.writerows(d)
        print(f"{len(d)} districts -> {path}", file=sys.stderr)
    else:
        out = rows()
        w = csv.DictWriter(sys.stdout, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(out)
        print(f"{len(out)} rows", file=sys.stderr)
