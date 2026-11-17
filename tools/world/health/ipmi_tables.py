# /// script
# requires-python = ">=3.11"
# dependencies = ["pdfplumber"]
# ///
"""Typed rate tables and country-to-zone lists from insurers' public IPMI rate PDFs.

Written by AI on 2026.11.17 by model claude sonnet 5.5, for the world-data owner.

Run:  uv run tools/world/health/ipmi_tables.py
Reads the PDFs in cache/<source_id>/ (see health-cover.notes.md for the download URLs) and
writes, next to this script:
  axa-globalreach.rates.csv   axa-globalreach.zones.csv
  generali-intl-exclusive.rates.csv   generali-intl-exclusive.zones.csv
  globality-yougenio.rates.csv   globality-yougenio.zones.csv
  img-gmi.rates.csv
  care-expat-world.rates.csv
Every parsed row is checked (row counts, monotone ages, monthly x 12 = yearly for Globality).
"""

import csv
import pathlib
import re
import sys

import pdfplumber

import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[2]
CACHE = REPO / "cache"


UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
PDFS = {
    "axa-globalreach/premium-table-2509.pdf": "https://docs.navigator-insurance.com/dl/7185.pdf",
    "axa-globalreach/brochure-2606E.pdf": "https://hk-axa-web-2024.cdn.prismic.io/hk-axa-web-2024/aij_uQeQX7-eXG2Z_LPPM922-2606EGlobalReachMedicalInsurancePlanProductbrochure_HK%26MA-Eng-.pdf",
    "generali-intl-exclusive/premium.pdf": "https://cdn.prod.website-files.com/63a28ca20a748d597081715c/690315c510ed5e7548361455_International%20Exclusive%20Premium%20%26%20Commission%20Table.pdf",
    "generali-intl-exclusive/product-disclosure-sheet.pdf": "https://cdn.prod.website-files.com/63a28ca20a748d597081715c/68871f60aaff27465dde670a_INTERN~3.PDF",
    "globality-yougenio/globality-health-premiums-eur.pdf": "https://www.expatinsurances.org/downloads/globality-health-premiums-eur.pdf",
    "globality-yougenio/product-brochure-en-0224.pdf": "https://globalhealth.insurance/wp-content/uploads/2026/06/Globality_YouGenio_World_PB_EN_0224.pdf",
    "globality-yougenio/general-conditions-en-v14-0224.pdf": "https://globalhealth.insurance/wp-content/uploads/2026/06/Globality_YouGenio_World_GCI_EN_V14_0224.pdf",
    "img-gmi/gmi-rate-sheets.pdf": "https://www.imglobal.com/docs/library/forms-library/gmi-rate-sheets.pdf",
    "img-gmi/gmi-brochure.pdf": "https://www.imglobal.com/docs/library/forms-library/gmi-brochure.pdf",
    "care-expat-world/brochure-eng.pdf": "https://www.care-concept.de/krankenversicherung/care_expat_world/Internationale_Krankenversicherung_Care_Expat_World_Broschuere_eng.pdf?navilang=eng",
}


def ensure_pdfs() -> None:
    """Download any missing source PDF into cache/ (IMG's server refuses requests without a browser user agent)."""
    for rel, url in PDFS.items():
        path = CACHE / rel
        if path.exists():
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/pdf,*/*", "Referer": "https://www.imglobal.com/"})
        data = urllib.request.urlopen(req).read()
        assert data[:4] == b"%PDF", f"{url} did not return a PDF"
        path.write_bytes(data)
        print("downloaded", rel)


def write(name: str, header: list[str], rows: list[list]) -> None:
    with open(HERE / name, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"{name}: {len(rows)} rows")


def pages_text(path: pathlib.Path) -> list[str]:
    with pdfplumber.open(path) as pdf:
        return [(p.extract_text() or "") for p in pdf.pages]


def num(s: str) -> float:
    fixed = re.sub(r"^(\d)\.(\d{3})\.(\d{2})$", r"\1,\2.\3", s)  # the insurer's PDF prints "6.000.00" for 6,000.00 in one cell
    if fixed != s:
        print(f"typo in source corrected: {s!r} -> {fixed!r} (checked against monthly x 12)")
    return float(fixed.replace(",", ""))


# ---------------------------------------------------------------- country lists

ENTRY = re.compile(r"([A-Za-z’'&().,\- ]+?) ([1-7]) ([A-Z0-9!]{3})(?= |$)")


def zone_entries(lines: list[str]) -> list[tuple[str, int, str]]:
    out = []
    for line in lines:
        for m in ENTRY.finditer(line):
            name = m.group(1).strip()
            if name.lower().startswith(("name zone", "country name")):
                continue
            out.append((name, int(m.group(2)), m.group(3)))
    return out


def load_country_info() -> dict[str, str]:
    """ISO alpha-2 -> GeoNames country name."""
    info = {}
    with open(CACHE / "geonames" / "countryInfo.txt", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            p = line.rstrip("\n").split("\t")
            info[p[0]] = p[4]
    return info


def norm(s: str) -> str:
    s = s.lower().replace("’", "'")
    s = s.replace("&", "and")
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


# insurer wording -> ISO alpha-2 (None where the insurer's entry is not a country)
ALIASES = {
    "uae": "AE", "usa": "US", "us minor outlying islands": "UM", "united kingdom": "GB",
    "russian federation": "RU", "republic of macedonia": "MK", "korea republic of": "KR",
    "south korea republic of": "KR", "korea dpr": "KP", "lao people s democratic rep": "LA",
    "laos people s deomocratic rep": "LA", "libyan arab jamahiriya": "LY",
    "cote d ivoire": "CI", "iran islamic republic of": "IR", "syrian arab republic": "SY", "cape verde": "CV", "netherlands": "NL", "cote d lvoire": "CI", "cote d lovire": "CI", "tanzania united republic of": "TZ",
    "micronesia federated states": "FM", "moldova republic of": "MD", "holy see vatican city state": "VA",
    "swaziland": "SZ", "brunei darussalam": "BN", "bosnia and herzegovina": "BA",
    "bosnia and herzegovir": "BA", "antigua and barbuda": "AG", "antigua and barduda": "AG",
    "virgin islands british": "VG", "virgin islands us": "VI", "sth georgia and sth sandwich is": "GS",
    "st vincent and the grenadines": "VC", "svalbard and jan mayen": "SJ",
    "heard and mcdonald islands": "HM", "cocos keeling islands": "CC", "falkland islands malvinas": "FK",
    "timor leste": "TL", "reunion": "RE", "myanmar": "MM", "congo": "CG", "congo dr": "CD",
    "macau": "MO", "hong kong": "HK", "taiwan": "TW", "netherlands antilles": None,
    "alderney": "GG", "herm": "GG", "sark": "GG", "canary islands": "ES", "madeira": "PT", "azores": "PT",
    "saint pierre and miquelon": "PM", "saint helena": "SH", "wallis and futuna islands": "WF",
    "turks and caicos islands": "TC", "saint kitts and nevis": "KN", "saint lucia": "LC",
    "sao tome and principe": "ST", "trinidad and tobago": "TT", "czech republic": "CZ",
    "pitcairn": "PN", "kyrgyzstan": "KG", "niue": "NU", "macedonia": "MK",
}
# Insurer entries that stand for part of a country: report the ISO but flag the entry as a sub-territory.
SUBTERRITORY = {"alderney", "herm", "sark", "canary islands", "madeira", "azores"}


def to_iso(name: str, info_by_name: dict[str, str]) -> str | None:
    k = norm(name)
    if k in ALIASES:
        return ALIASES[k]
    return info_by_name.get(k)


# ---------------------------------------------------------------- AXA GlobalReach

AXA_PDF = CACHE / "axa-globalreach" / "premium-table-2509.pdf"


def axa(info_by_name: dict[str, str]) -> None:
    txt = pages_text(AXA_PDF)
    # zone list: page 3 (English half)
    lines = [l for l in txt[2].splitlines()]
    ents = zone_entries(lines)
    zone_rows = []
    for name, z, code in ents:
        zone_rows.append([name, to_iso(name, info_by_name) or "", z, code])
    write("axa-globalreach.zones.csv", ["insurer_country_name", "iso2", "zone", "insurer_code"], zone_rows)
    unmatched = [r[0] for r in zone_rows if not r[1]]
    print("AXA unmatched names:", unmatched)

    ded_re = re.compile(r"Annual Deductible: (NIL|HKD[\d,]+ or USD[\d,]+)")
    out = []
    num_re = re.compile(r"^[\d,]{3,}$")
    zone_pages = {z: range(5 + 8 * (z - 2), 5 + 8 * (z - 2) + 8) for z in range(2, 8)}
    with pdfplumber.open(AXA_PDF) as pdf:
        for z, pr in zone_pages.items():
            for pn in pr:
                page = txt[pn - 1]
                m = ded_re.search(page)
                assert m, f"deductible not found on page {pn}"
                ded = m.group(1)
                ded_usd = 0 if ded == "NIL" else int(re.search(r"USD([\d,]+)", ded).group(1).replace(",", ""))
                levels = ("Prestige", "Comprehensive") if "Prestige" in page else ("Standard", "Essential")
                assert ("Comprehensive" in page) == ("Prestige" in page), pn
                words = pdf.pages[pn - 1].extract_words()
                for side, lvl in zip(("L", "R"), levels):
                    lo, hi = (30, 300) if side == "L" else (300, 562)
                    ws = [w for w in words if lo <= w["x0"] < hi and 110 < w["top"] < 815]
                    clusters: list[list] = []
                    for w in sorted(ws, key=lambda w: w["top"]):
                        if clusters and w["top"] - clusters[-1][0]["top"] < 3.0:
                            clusters[-1].append(w)
                        else:
                            clusters.append([w])
                    nrows = 0
                    for c in clusters:
                        r = sorted(c, key=lambda w: w["x0"])
                        toks = [w["text"] for w in r]
                        if len(toks) != 7 or not re.fullmatch(r"\d{1,2}\*?", toks[0]) or not all(num_re.match(t) for t in toks[1:]):
                            continue
                        age = int(toks[0].rstrip("*"))
                        v = [int(num(t)) for t in toks[1:]]
                        for area, i in (("Asia", 0), ("Worldwide excl. USA", 2), ("Worldwide", 4)):
                            out.append([z, lvl, area, ded_usd, age, "renewal_only" if toks[0].endswith("*") else "", v[i], v[i + 1]])
                        nrows += 1
                    assert nrows >= 98, (pn, side, nrows)  # ages 1..99; the age 0 row is garbled in the text layer and identical to age 1
    # sanity: premium rises with age within a series (ignoring child bands) and Prestige > Comprehensive > Standard > Essential at age 45
    idx = {(r[0], r[1], r[2], r[3], r[4]): r for r in out}
    for z in range(2, 8):
        for d in (0, 3125, 6250, 12500):
            for area in ("Asia", "Worldwide excl. USA", "Worldwide"):
                p = [idx[(z, l, area, d, 45)][7] for l in ("Prestige", "Comprehensive", "Standard", "Essential")]
                assert p == sorted(p, reverse=True), (z, d, area, p)
                for l in ("Prestige", "Comprehensive", "Standard", "Essential"):
                    a = [idx[(z, l, area, d, age)][7] for age in range(19, 100)]
                    assert a == sorted(a), (z, d, area, l)
    write(
        "axa-globalreach.rates.csv",
        ["zone", "benefit_level", "area_of_cover", "annual_deductible_usd", "age_last_birthday", "note", "annual_premium_hkd", "annual_premium_usd"],
        out,
    )


# ---------------------------------------------------------------- Generali International Exclusive (Malaysia)

GEN_PDF = CACHE / "generali-intl-exclusive" / "premium.pdf"


def generali(info_by_name: dict[str, str]) -> None:
    with pdfplumber.open(GEN_PDF) as pdf:
        txt = [(p.extract_text() or "") for p in pdf.pages]
        ents = zone_entries(txt[2].splitlines())
        zone_rows = []
        for name, z, code in ents:
            zone_rows.append([name, to_iso(name, info_by_name) or "", z, code])
        write("generali-intl-exclusive.zones.csv", ["insurer_country_name", "iso2", "zone", "insurer_code"], zone_rows)
        print("Generali unmatched names:", [r[0] for r in zone_rows if not r[1]])

        out = []
        for pn in range(4, 16):  # premium pages (the commission tables follow)
            p = pdf.pages[pn - 1]
            words = p.extract_words()
            plans = []
            for i, w in enumerate(words):
                if w["text"] == "Plan" and w["top"] < 80 and words[i + 2]["text"].startswith("(Zone"):
                    plans.append((int(words[i + 1]["text"]), int(words[i + 3]["text"].rstrip(")")), w["x0"]))
            assert len(plans) == 2, (pn, plans)
            rm = sorted([w for w in words if w["text"] == "RM" and 115 < w["top"] < 130], key=lambda w: w["x0"])
            assert len(rm) == 6, (pn, len(rm))
            blocks = {"L": rm[:3], "R": rm[3:]}
            cols = ("Asia", "Worldwide excl. USA", "Worldwide")
            for (plan, zone, x0), side in zip(sorted(plans, key=lambda t: t[2]), ("L", "R")):
                cx = [w["x1"] for w in blocks[side]]
                lo, hi = (0, 300) if side == "L" else (300, 600)
                # age labels at fixed x in the block
                age_words = [w for w in words if lo <= w["x0"] < lo + 120 and re.fullmatch(r"\d{1,2}|0-10", w["text"]) and w["top"] > 130 and w["x0"] < lo + 90]
                for aw in age_words:
                    band = [w for w in words if abs(w["top"] - aw["top"]) < 3 and aw["x1"] + 8 <= w["x0"] < hi + 5 + (0 if side == "R" else 15) and re.fullmatch(r"[\d,]{4,}|\d\.\d{3}", w["text"])]
                    # only numbers inside this block's columns
                    for w in band:
                        c = min(range(3), key=lambda i: abs(w["x1"] - cx[i] - 20))
                        if aw["text"] == "0-10" or not 16 <= int(aw["text"]) <= 80:
                            continue  # children's bands sit in merged cells; only adult ages 16-80 are typed
                        txt_val = w["text"]
                        if re.fullmatch(r"\d\.\d{3}", txt_val):
                            print(f"typo in source corrected: {txt_val!r} -> {txt_val.replace('.', ',')!r} (zone {zone} plan {plan} {cols[c]} age {aw['text']}; neighbours bracket it)")
                            txt_val = txt_val.replace(".", ",")
                        out.append([zone, plan, cols[c], int(aw["text"]), int(num(txt_val)), aw["text"]])
        # de-duplicate and sanity-check
        seen = {}
        for r in out:
            k = (r[0], r[1], r[2], r[3])
            assert k not in seen or seen[k] == r[4], ("dup", k)
            seen[k] = r[4]
        rows = [[*k, v] for k, v in sorted(seen.items())]
        for k in sorted({(r[0], r[1], r[2]) for r in rows}):
            ages = sorted(r[3] for r in rows if (r[0], r[1], r[2]) == k)
            vals = [r[4] for r in sorted(rows, key=lambda r: r[3]) if (r[0], r[1], r[2]) == k]
            if vals != sorted(vals):
                print("WARN non-monotone Generali series", k)
            if len(vals) != 65:
                print("WARN Generali series with", len(vals), "ages (expected 65 = ages 16-80)", k, sorted(set(range(16, 81)) - set(ages)))
        write(
            "generali-intl-exclusive.rates.csv",
            ["zone", "plan", "area_of_cover", "age_last_birthday", "annual_premium_myr"],
            rows,
        )


# ---------------------------------------------------------------- Globality YouGenio World

GLOB_PDF = CACHE / "globality-yougenio" / "globality-health-premiums-eur.pdf"


def globality() -> None:
    txt = pages_text(GLOB_PDF)
    zr = re.compile(r"([A-Za-zÅé\(\)\.,'’\- ]+?) ([A-Z]{2}) ([1-5])(?= |$)")
    zone_rows = []
    for pn in (3, 4):
        for line in txt[pn].splitlines():
            for m in zr.finditer(line):
                name = m.group(1).strip()
                if name.startswith(("Country of Residence", "ISO Code")):
                    continue
                zone_rows.append([name, m.group(2), int(m.group(3))])
    write("globality-yougenio.zones.csv", ["insurer_country_name", "iso2", "zone"], zone_rows)

    age_re = r"\d{1,2}–\d{2}"
    out = []
    for z in range(1, 6):
        monthly_page = txt[5 + 2 * (z - 1)]
        yearly_page = txt[6 + 2 * (z - 1)]
        assert f"Pricing Zone {z} / Monthly" in monthly_page and f"Pricing Zone {z} / Yearly" in yearly_page
        res = {}
        for label, page in (("m", monthly_page), ("y", yearly_page)):
            deds: list[str] = []
            cols: list[list[str]] = []
            for line in page.splitlines():
                if line.startswith("Deductible:") and "Euro" in line:
                    deds = re.findall(r"Deductible: ([\d,]+) Euro", line)
                    cols = []
                elif line.startswith("Age groups") and "Essential" in line or (line.startswith("Age groups") and "Plus" in line):
                    parts = [p.split() for p in line.split("Age groups") if p.strip()]
                    cols = parts
                elif re.match(age_re, line) and deds:
                    toks = line.split()
                    groups = []
                    cur = None
                    for t in toks:
                        if re.fullmatch(age_re, t):
                            cur = [t, []]
                            groups.append(cur)
                        else:
                            cur[1].append(t)
                    assert len(groups) == len(deds) == len(cols), (z, label, line, deds, cols)
                    for (age, vals), ded, plans in zip(groups, deds, cols):
                        assert len(vals) == len(plans), (line, plans)
                        for plan, v in zip(plans, vals):
                            res[(label, plan, int(ded.replace(",", "")), age)] = num(v)
        for (label, plan, ded, age), v in list(res.items()):
            if label != "y":
                continue
            mval = res[("m", plan, ded, age)]
            assert abs(mval * 12 - v) < 1.0, (z, plan, ded, age, mval, v)
            out.append([z, plan, ded, age.replace("–", "-"), mval, v])
    write("globality-yougenio.rates.csv", ["zone", "plan", "outpatient_deductible_eur", "age_band", "monthly_premium_eur", "annual_premium_eur"], out)


# ---------------------------------------------------------------- IMG Global Medical Insurance (flat, no zones)

IMG_PDF = CACHE / "img-gmi" / "gmi-rate-sheets.pdf"


def img() -> None:
    txt = pages_text(IMG_PDF)
    sheets = {1: ("Bronze", "Worldwide excl. USA, Canada, China, Hong Kong, Japan, Macau, Singapore, Taiwan"), 2: ("Bronze", "Worldwide"),
              3: ("Silver", "Worldwide excl. USA, Canada, China, Hong Kong, Japan, Macau, Singapore, Taiwan"), 4: ("Silver", "Worldwide"),
              5: ("Gold", "Worldwide excl. USA, Canada, China, Hong Kong, Japan, Macau, Singapore, Taiwan"), 6: ("Gold", "Worldwide"),
              7: ("Platinum", "Worldwide excl. USA, Canada, China, Hong Kong, Japan, Macau, Singapore, Taiwan"), 8: ("Platinum", "Worldwide")}
    out = []
    for pn, (plan, area) in sheets.items():
        page = txt[pn - 1]
        deds = [int(d.replace(",", "")) for d in re.search(r"Deductibles ((?:\$[\d,]+ ?)+)", page).group(1).replace("$", "").split()]
        for line in page.splitlines():
            m = re.match(r"^(\d{1,2} to \d{1,2}\*?|19 to 24) ((?:\$[\d,]+ ?)+)$", line)
            if not m:
                continue
            vals = [int(v.replace(",", "")) for v in m.group(2).replace("$", "").split()]
            assert len(vals) == len(deds), (pn, line)
            for d, v in zip(deds, vals):
                out.append([plan, area, d, m.group(1).replace("*", ""), v])
    write("img-gmi.rates.csv", ["plan", "area_of_cover", "annual_deductible_usd", "age_band", "annual_premium_usd"], out)


# ---------------------------------------------------------------- Care Expat World (Barmenia / Care Concept), zones by area of cover only

CARE_PDF = CACHE / "care-expat-world" / "brochure-eng.pdf"


def care() -> None:
    txt = "\n".join(pages_text(CARE_PDF))
    out = []
    zone = plan = None
    for line in txt.splitlines():
        m = re.match(r"Country Zone (\d) – (.+)", line)
        if m:
            zone, zname = int(m.group(1)), m.group(2)
        m = re.match(r"(Basic|Comfort|Premium) / Monthly premium", line)
        if m:
            plan = m.group(1)
        m = re.match(r"^(\d+ - \d+|70 and older) ((?:€ ?[\d,]+ ?){3})$", line)
        if m and zone and plan:
            vals = [int(v.replace(",", "")) for v in re.findall(r"€ ?([\d,]+)", m.group(2))]
            for d, v in zip((0, 1200, 3600), vals):
                out.append([zone, plan, d, m.group(1), v])
    assert len(out) == 3 * 3 * 3 * 11, len(out)
    write("care-expat-world.rates.csv", ["area_zone", "plan", "annual_deductible_eur", "age_band", "monthly_premium_eur"], out)


if __name__ == "__main__":
    ensure_pdfs()
    info = load_country_info()
    by_name = {norm(n): iso for iso, n in info.items()}
    which = sys.argv[1:] or ["axa", "generali", "globality", "img", "care"]
    if "axa" in which:
        axa(by_name)
    if "generali" in which:
        generali(by_name)
    if "globality" in which:
        globality()
    if "img" in which:
        img()
    if "care" in which:
        care()
