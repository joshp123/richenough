"""Annual road tax for the reference car (new Corolla-class, 8 years, 12,000 km a year) outside the US and Europe.

Writes road-tax.curated.csv from the rules typed in below. Value-based taxes use the car module's own price
(tools/world/car.py: price_new in US dollars, converted at the same rate, read from data/tables/car.world.csv) and its
depreciation (straight line to 50% at 8 years), so the base at the start of year k is price x (1 - 0.0625 (k-1)).
Every quote is checked against the saved page in cache/<source_id>/; a quote that is not on the page stops the run.

Written by AI on 2026.11.18 by model claude sonnet 5.5. Run: python3 -I road_tax.py
"""

import csv
import logging
import html
import re
import sys
from pathlib import Path

logging.getLogger("pypdf").setLevel(logging.CRITICAL)
ROOT = Path(__file__).resolve().parents[3]
CACHE = ROOT / "cache"
OUT = Path(__file__).parent
YEARS = 8


def factor(k):
    return 1 - 0.5 * (k - 1) / YEARS


MEAN_FACTOR = sum(factor(k) for k in range(1, YEARS + 1)) / YEARS  # 0.78125


def car_price_local(code):
    """Model price new in local currency (price in US dollars from the car note x the note's rate)."""
    for r in csv.DictReader(open(ROOT / "data/tables/car.world.csv")):
        if r["place_code"] == code:
            usd = float(re.search(r"price new about ([\d.]+) US dollars", r["note"]).group(1))
            fx = float(re.search(r"converted at ([\d.]+) \w+ per US dollar", r["note"]).group(1))
            return usd * fx
    raise KeyError(code)


def text_of(source_id):
    out = []
    for p in (CACHE / source_id).iterdir():
        if p.suffix == ".pdf":
            from pypdf import PdfReader  # uv run --with pypdf
            out.append(" ".join((pg.extract_text() or "") for pg in PdfReader(p).pages))
        else:
            t = p.read_text(errors="ignore")
            t = re.sub(r"(?is)<(script|style).*?</\1>", " ", t)
            out.append(html.unescape(re.sub(r"<[^>]+>", " ", t)))
    return re.sub(r"\s+", " ", " ".join(out))


rows = []


def add(code, amount, cur, measured, src, note, url, quote):
    rows.append(dict(place_code=code, amount=f"{amount:.2f}" if amount < 10000 else f"{amount:.0f}", currency=cur,
                     unit="per_year", period="2026", measured_for=measured, source_id=src, note=note, url=url, quote=quote))


# ---------------------------------------------------------------- Asia
# Thailand: 0.50 THB/cc for the first 600 cc, 1.50 for 601-1,800, 4.00 above; 10/20/30/40/50% off in years 6-10.
tax = 600 * 0.5 + (1798 - 600) * 1.5
th = (tax * (5 + 0.9 + 0.8 + 0.7) + 200) / YEARS
add("TH", th, "THB", "Thailand, whole country (private car up to 7 seats, taxed on engine cc)", "road-tax-th-itax",
    f"1,798 cc: 600 x 0.50 + 1,198 x 1.50 = {tax:,.0f} THB a year; years 1-5 full, years 6-8 at 90/80/70% -> {tax * 7.4 / YEARS:,.1f} a year. "
    "Plus the roadworthiness test (about 200 THB at a private station) once, at the year-8 renewal, because cars of 7 years and over need it "
    "(200/8 = 25 a year; source road-tax-th-autospinn-inspection, a search-tool summary because the page returned 403). "
    "Hybrids are taxed on cc like petrol cars. Compulsory insurance (the PRB) is left out. The DLT's own tariff page could not be fetched; iTAX copies it.",
    "https://www.itax.in.th/media/%E0%B8%A0%E0%B8%B2%E0%B8%A9%E0%B8%B5%E0%B8%A3%E0%B8%96%E0%B8%A2%E0%B8%99%E0%B8%95%E0%B9%8C-2569",
    "ส่วนเกิน 600 cc ถึง 1,800 cc")

# Malaysia: JPJ private saloon, Peninsular Malaysia: RM200 + RM0.40 per cc above 1,600.
add("MY", 200 + 0.4 * (1798 - 1600), "MYR", "Peninsular Malaysia, private saloon owned by an individual (Sabah and Sarawak pay less)", "road-tax-my-bjak",
    "1,798 cc: 200 + (1,798 - 1,600) x 0.40 = 279.20 MYR a year; flat in every year of the car's life. JPJ publishes the schedule as a PDF "
    "(its July 2026 upload carries the 2009 rates); BJAK copies it. No periodic inspection for a private car unless it changes hands. "
    "SUVs and MPVs (the Corolla Cross) use the non-saloon schedule: 300 + 0.30 x 198 = 359.40.",
    "https://bjak.my/en/car-insurance/learning-hub/road-tax-price-by-engine-capacity", "1,601 to 1,800cc")

# Singapore: LTA formula, six-monthly, x2. Hybrid pays the higher of engine and motor-power tax; the engine figure is higher.
sg_road = ((475 + 0.75 * (1798 - 1600)) * 0.782) * 2
sg = sg_road + 3 * 68.67 / YEARS
add("SG", sg, "SGD", "Singapore, whole country (private car, 1,798 cc petrol hybrid)", "road-tax-sg-lta-structure",
    f"LTA road tax for 1,601-3,000 cc: [475 + 0.75 x (1,798 - 1,600)] x 0.782 = {sg_road / 2:,.2f} per six months, {sg_road:,.2f} a year (no age surcharge until year 11). "
    "The 1.8 hybrid's motor (about 53 kW) gives a lower power-based figure, and a petrol-electric car pays the higher of the two. "
    "Plus the periodic inspection: none under 3 years, then every 2 years, so 3 inspections in 8 years at about 68.67 SGD "
    "(source road-tax-sg-singsaver-inspection; another site says 68.04) = 25.75 a year. The COE and ARF are in the car's price.",
    "https://onemotoring.lta.gov.sg/content/onemotoring/home/buying/upfront-vehicle-costs/tax-structure.html", "[$475 + $0.75(EC - 1,600)] x 0.782")

# Japan: automobile tax 36,000 (1.5-2.0 L), weight tax at the base rate 7,500 a year for 1.0-1.5 t, shaken fee 2,100 per inspection.
jp = 36000 + 7500 + 3 * 2100 / YEARS
add("JP", jp, "JPY", "Japan, whole country (private white-plate car, 1.5-2.0 L, 1.0-1.5 t)", "road-tax-jp-kurumaerabi-corolla",
    f"Automobile tax (prefecture) 36,000 JPY a year for 1.5-2.0 L, registered after 1 Oct 2019. Weight tax 22,500 JPY for the first 3 years = 7,500 a year, "
    "the catalogue's figure for the Corolla 1.8 Hybrid W x B (the base rate: no 'eco-car' cut applies to it). Official inspection fee 1,700 revenue stamp + 400 certificate = 2,100 "
    "at the shaken at years 3, 5 and 7 (3 x 2,100 / 8 = 787.50 a year; source road-tax-jp-bestcalendar-shaken). "
    "Left out: the one-off 75% green cut on the year-2 automobile tax (applies to qualifying hybrids until March 2028; not checked for this trim), "
    "dealer shaken service charges, and compulsory CALI insurance. The 13-year surcharge is beyond the 8 years.",
    "https://www.kurumaerabi.com/catalog/toyota/22947/fmc001/155048/", "自動車税 36,000円 自動車重量税 22,500円")

# Taiwan
add("TW", 7120 + 4800, "TWD", "Taiwan, whole country (private small passenger car, 1,201-1,800 cc petrol)", "road-tax-tw-chungautos",
    "Vehicle licence tax 7,120 TWD (1,201-1,800 cc, paid in April) + highway maintenance fee (formerly the fuel-use fee) 4,800 TWD (petrol, 1,201-1,800 cc, paid in July) = 11,920 a year; "
    "the same every year. Hybrids are not exempt (only battery-electric cars are). The licence-tax table is also in the Ministry of Finance's PDF (road-tax-tw-mof-table). "
    "Not included: the periodic vehicle inspection, which starts after the car's first years; its fee was not found.",
    "https://chungautos.com/archives/2317", "11,920")

# Hong Kong
add("HK", 7498 + 2 * 585 / YEARS, "HKD", "Hong Kong, whole territory (private car, 1,500-2,500 cc petrol)", "road-tax-hk-td341",
    "Annual vehicle licence fee 7,498 HKD (petrol private car over 1,500 cc up to 2,500 cc; includes the levy shown in the Transport Department's form TD341, Feb 2026). "
    "Plus the annual examination, required once the car is 6 years old: 2 exams at 585 HKD in years 7 and 8 = 146.25 a year "
    "(fee from a MoneyHero price list, road-tax-hk-moneyhero-exam; the Transport Department's own table was not read). First registration tax is in the car's price.",
    "https://www.td.gov.hk/filemanager/common/td341_2_2026_eng.pdf", "exceeding 1,500c.c. but not exceeding 2,500c.c. 7,498")

# Vietnam
fee = (4_320_000 + 3_000_000 + 3_000_000 + 1_560_000)  # 36 months, 24, 24 and 12 months of road-use fee
vn = (fee + 3 * 250_000) / YEARS
add("VN", vn, "VND", "Vietnam, whole country (private car up to 8 seats; same in Ho Chi Minh City and Da Nang)", "road-tax-vn-decree-364",
    f"Road-use fee (Decree 364/2025, from 1 Jan 2026): 36 months 4,320,000 + 24 months 3,000,000 + 24 months 3,000,000 + 12 months 1,560,000 = {fee:,} VND over 96 months. "
    "Inspection cycle for a private car: first at 36 months, then every 24 months until 7 years, then yearly, so 3 inspections in 8 years at 250,000 VND (Circular 55/2022; "
    "source road-tax-vn-ketoananpha-dangkiem). Vietnam has no annual vehicle tax on cars; the registration fee is one-off. "
    f"({fee:,} + 750,000) / 8 = {vn:,.0f} a year.",
    "https://thuvienphapluat.vn/chinh-sach-phap-luat-moi/vn/ho-tro-phap-luat/chinh-sach-moi/102872/cap-nhat-bieu-muc-thu-phi-su-dung-duong-bo-doi-voi-xe-o-to-nam-2026",
    "Xe chở người đến 8 chỗ (không kể chỗ của người lái xe) không hoạt động kinh doanh vận tải.")

# Indonesia (Jakarta): 2% x 1.025 (sedan coefficient) x NJKB; NJKB assumed = model price x straight-line path.
p = car_price_local("ID")
njkb = p * MEAN_FACTOR
add("ID", 0.02 * 1.025 * njkb, "IDR", "Jakarta (DKI Jakarta provincial rate: first car 2%, no opsen; other provinces about 1.1% + 66% opsen)", "road-tax-id-bapenda-jakarta",
    f"PKB = 2% x 1.025 (sedan weight coefficient; 1.05 for an SUV) x NJKB. Taxable value (NJKB) is not the purchase price; the Pergub depreciation table was not found, "
    f"so NJKB is taken as the car module's price ({p:,.0f} IDR) falling in a straight line to 50% at year 8: mean {MEAN_FACTOR:.5f} x price = {njkb:,.0f} IDR; tax {0.02 * 1.025 * njkb:,.0f} a year. "
    "Left out: the SWDKLLJ road-accident levy (143,000 IDR, a compulsory insurance-type contribution), the 5-yearly plate fee. Thin: the base is assumed.",
    "https://bapenda.jakarta.go.id/artikel/tarif-baru-pkb-dan-bbnkb-di-jakarta", "2% (dua persen)")

# Korea
kr_full = 1798 * 200 * 1.3
kr = kr_full * (2 + 0.95 + 0.9 + 0.85 + 0.8 + 0.75 + 0.7) / YEARS
add("KR", kr, "KRW", "South Korea, whole country (private passenger car, over 1,600 cc)", "road-tax-kr-jabguyver",
    f"Automobile tax = cc x 200 KRW (over 1,600 cc) = 359,600 + 30% local education tax = {kr_full:,.0f} KRW in years 1-2; "
    "from year 3 it falls 5% a year (year 8: -30%). Mean over 8 years = " f"{kr:,.0f}. Hybrids pay on engine cc. Rates here are the standard rule read from a blog; "
    "wetax.go.kr was not reachable. The periodic inspection (first at 4 years, then every 2 years) is not included.",
    "https://jab-guyver.co.kr/3786", "200원/cc")

# ---------------------------------------------------------------- Gulf
# UAE Dubai: renewal 350 + 20; test 150 + 20 needed from year 4 (renewals at ends of years 3-7 => 5 tests in 8 years).
ae = (YEARS * 370 + 5 * 170) / YEARS
add("AE", ae, "AED", "Dubai (RTA; Abu Dhabi charges 350 + a 150 test)", "road-tax-ae-uaevehicletesting",
    "Registration (mulkiya) renewal 350 + 20 Knowledge and Innovation = 370 AED a year (8 x 370; the first year is paid at registration). "
    "A new private car skips the technical test for 3 years; then each renewal needs a test, 150 + 20 = 170 AED, 5 tests in years 4-8. "
    "(8 x 370 + 5 x 170) / 8 = 476.25. No annual tax on the car itself; Salik tolls and insurance are not included. Fees read from a guide that cites RTA's pages.",
    "https://uaevehicletesting.com/vehicle-test-fees-uae", "Dubai (RTA) 170 (150 + 20)")

# Oman
add("OM", 23, "OMR", "Oman, whole country (private car under 3 tonnes, 1,500 to below 3,000 cc)", "road-tax-om-rop",
    "Royal Oman Police registration renewal (mulkiya): 23 OMR a year for 1,500 cc to below 3,000 cc. Technical inspection (5 OMR extra) is only for private cars of 10 years, so none in the 8 years. "
    "The 18 OMR band is for engines under 1,500 cc.",
    "https://www.rop.gov.om/english/Vehicle_Registration_renewal.aspx", "1500cc to below 3000cc")

# ---------------------------------------------------------------- Caucasus, Africa
# Georgia: property tax on cars 0.8% (Tbilisi) of market value at the end of the previous year, only when family income > 100,000 GEL.
pg = car_price_local("GE")
ge_tax = 0.008 * pg * MEAN_FACTOR
ge_insp = 3 * 60 / YEARS
add("GE", ge_tax + ge_insp, "GEL", "Georgia, Tbilisi rate (0.8% of market value); applies only if the couple's family income is over 100,000 GEL a year", "road-tax-ge-doberi-property",
    f"Property tax on a passenger car: 0.8% of the value at 31 December of the previous year (Tbilisi), but only for families with income over 100,000 GEL (from 30 Sept 2026; it was 40,000). "
    f"Value: the car module's price {pg:,.0f} GEL on a straight line to 50% at year 8, mean {MEAN_FACTOR * pg:,.0f} -> {ge_tax:,.0f} a year. "
    "Mandatory inspection: first 4 years after manufacture, then every 2 years, 60 GEL (source road-tax-ge-doberi-inspection), so 3 in 8 years = 22.50 a year. "
    "If the couple's income is under the threshold the figure is 22.50. Thin: whether foreign-source withdrawals count as 'family income' was not checked.",
    "https://doberi.ge/en/move/property-tax", "The rate is 0.8 to 1 % of market value, 0.8 % in Tbilisi and Batumi.")

# Morocco: hybrids exempt from the vignette (CGI art. 260-15); technical inspection yearly from about year 5, 370 DH for 8-10 fiscal hp.
ma = 4 * 370 / YEARS
add("MA", ma, "MAD", "Morocco, whole country (petrol-electric hybrid, 8-10 fiscal hp)", "road-tax-ma-fiscalitemaroc",
    "Annual vignette (TSAVA): 0 MAD, because article 260-15 of the General Tax Code exempts hybrid cars. (The payment site mavignette.ma still lists hybrids at the petrol rate, 650 DH for 8-10 cv, "
    "350 DH under 8 cv; if that is enforced, add that figure.) Mandatory technical inspection: the first within 6 months before the 5th anniversary, then yearly, 370 DH for 8-10 cv "
    "(road-tax-ma-autoactu-ct: 'entre 370 et 400 DH', first control five years after registration, then annual; NARSA yearly cycle: road-tax-ma-demarchesmaroc-ct), so 4 inspections in 8 years = 185 a year. Thin: the Corolla hybrid's fiscal horsepower was assumed to be 8-10 cv, and the 370 DH tariff is a press figure (the official NARSA grid page is built by script and could not be saved).",
    "https://fiscalitemaroc.com/fiscalite/tsava", "L'article 260-15° du CGI exonère les véhicules à moteur électrique ainsi que les véhicules à moteur hybride")

# South Africa: Western Cape licence fee, tare 1,251-1,500 kg: R690; plus RTMC transaction fee R72.
add("ZA", 690 + 72, "ZAR", "Cape Town (Western Cape tariff from 1 July 2026; Gauteng charges R732 + 72 for the same tare band)", "road-tax-za-wc-gazette",
    "Annual motor vehicle licence fee, tare 1,251-1,500 kg: R690 (Western Cape Provincial Gazette Extraordinary 9248, 9 June 2026) + R72 national transaction fee on every renewal = R762. "
    "No roadworthiness test for a private car except when it is sold. Left out: the one-off registration fee (R310) and the first-year disc, which is part of buying the car. "
    "The R72 fee is on easynatis.co.za/fees (road-tax-za-easynatis); the WC fee also appears in thesouthafrican.com (road-tax-za-thesouthafrican).",
    "https://www.westerncape.gov.za/mobility/service/vehicle-licence", "1 251–1 500 R690,00")

# ---------------------------------------------------------------- Latin America
# Mexico City: hybrids are exempt from the tenencia; only the refrendo fee. Verification: exempt holograma free for hybrids.
add("MX", 760, "MXN", "Mexico City (Ciudad de México plates)", "road-tax-mx-motorpasion-tenencia",
    "Tenencia (annual vehicle ownership tax): 0, because electric and hybrid cars are exempt in Mexico City (the car's invoice value, about 678,000 MXN here, is also above the 638,000 MXN cap for the general subsidy). "
    "Refrendo 2026: 760 MXN, 'preliminary cost'. Emissions verification: hybrids get the free 'Exento' holograma (road-tax-mx-tvazteca-verificacion). "
    "Thin: the hybrid exemption is read from news reports; the Código Fiscal text was not found, and whether hybrids pay the refrendo was not checked.",
    "https://www.motorpasion.com.mx/industria/tenencia-2026-pago", "Cubrir el refrendo 2026, cuyo costo preliminar es de")

# Costa Rica: property tax in the marchamo on the depreciated value, progressive scale (2026 values, colones).
def cr_tax(v):
    steps = [(220_000, None), (3_010_000, .006), (4_000_000, .018), (5_010_000, .021), (6_010_000, .025), (10_010_000, .028), (13_020_000, .0315)]
    tax, prev = 23_100, 220_000
    for top, r in steps[1:]:
        if v > prev:
            tax += (min(v, top) - prev) * r
        prev = top
    if v > 13_020_000:
        tax += (v - 13_020_000) * .035
    return tax


cum = [0, .103, .203, .298, .387, .465, .533, .593]  # cumulative depreciation by model age 0..7
pcr = car_price_local("CR")
cr = sum(cr_tax(pcr * (1 - cum[k])) for k in range(YEARS)) / YEARS
add("CR", cr, "CRC", "Costa Rica, whole country (property-tax part of the marchamo; the same everywhere)", "road-tax-cr-hacienda-tarifas",
    f"Impuesto a la propiedad de vehículos (Ley 7088 art. 9 as amended by Ley 10390), 2026 scale: 23,100 minimum to 220,000, then 0.60%, 1.80%, 2.10%, 2.50%, 2.80%, 3.15%, 3.50% on each slice. "
    f"Depreciation by model age 0-7: 0, 10.3, 20.3, 29.8, 38.7, 46.5, 53.3, 59.3%. Base = the car module's price {pcr:,.0f} CRC (the law uses the customs value for a new car, which is lower, so this overstates year 1). Mean of the 8 yearly taxes = {cr:,.0f}. "
    "Left out: the compulsory SOA insurance (30,238 CRC) and the other small marchamo lines (timbres, fees); the roadworthiness test (RTV) fee, because the operator changed in 2026 and no current tariff was found. Thin.",
    "https://www.hacienda.go.cr/docs/Tarifasimppropiedadvehiculos.pdf", "Sobre el exceso de ₡13.020.000 3,50%")

# Peru (Lima)
ppe = car_price_local("PE")
pe = (3 * 0.01 * ppe + 4 * 87.5) / YEARS
add("PE", pe, "PEN", "Lima (SAT Lima; the same national rate applies in every province)", "road-tax-pe-gob-impuesto",
    f"Impuesto al patrimonio vehicular: 1% of the purchase value (never below the MEF table), for only the first 3 years after first registration = 0.01 x {ppe:,.0f} = {0.01 * ppe:,.0f} a year for 3 years, nothing after. "
    "Roadworthiness test (CITV): first from the 4th year, then yearly, 80-95 PEN (road-tax-pe-gob-citv: S/ 80-95; first test from the 4th year, road-tax-pe-gob-citv-primera): 4 tests in 8 years at 87.50. "
    f"(3 x {0.01 * ppe:,.0f} + 350) / 8 = {pe:,.0f} a year. The base uses the car module's price in soles, not an invoice.",
    "https://www.gob.pe/115132-informacion-de-impuesto-vehicular", "La tasa del impuesto es el 1% de la base imponible.")

# Colombia (Medellin / Antioquia)
pco = car_price_local("CO")
def co_rate(v):
    return .015 if v <= 57_349_000 else (.025 if v <= 129_032_000 else .035)
co_tax = sum(co_rate(pco * factor(k)) * pco * factor(k) for k in range(1, YEARS + 1)) / YEARS
co = co_tax + 3 * 343_090 / YEARS
add("CO", co, "COP", "Medellín (Antioquia: the national rates apply; the department keeps 80%, the municipality 20%)", "road-tax-co-incp-rangos",
    f"Impuesto vehicular 2026 (Decreto 1457/2025): 1.5% up to 57,349,000 COP, 2.5% up to 129,032,000, 3.5% above, on the Ministry of Transport's base value. "
    f"Base = the car module's price {pco:,.0f} COP on a straight line to 50% at year 8, so the rate falls from 3.5% to 2.5% in year 5; mean tax {co_tax:,.0f} a year. "
    "Plus the technical-mechanical inspection: first from the 5th year, then yearly; 317,728-368,453 COP for a 3-7 year old car (mid 343,090): 3 tests in 8 years = 128,659 a year (road-tax-co-semana-rtm; first test at 5 years: road-tax-co-caracol-rtm). Compulsory SOAT is left out. "
    "Thin: the Ministry's actual base value for the Corolla hybrid was not read.",
    "https://incp.org.co/publicaciones/infoincp-publicaciones/impuestos/2026/01/rangos-de-avaluo-comercial-del-impuesto-de-vehiculos-2026", "Hasta $ 57.349.000")

# Brazil
pbr = car_price_local("BR")
add("BR-SP", 0.04 * pbr * MEAN_FACTOR + 174.08, "BRL", "São Paulo state (IPVA 4%; licensing fee 174.08 BRL)", "road-tax-br-zuldigital-sp",
    f"IPVA 4% of the valor venal (Sefaz-SP's FIPE-based table) + annual licensing fee 174.08 BRL (Detran-SP). Valor venal = the car module's price {pbr:,.0f} BRL on a straight line to 50% at year 8, mean {pbr * MEAN_FACTOR:,.0f} -> IPVA {0.04 * pbr * MEAN_FACTOR:,.0f}. "
    "Real FIPE values fall faster in the first years, so this is a ceiling. The DPVAT insurance is no longer charged. Thin: base assumed.",
    "https://www.zuldigital.com.br/blog/ipva-sao-paulo-2026", "4% para veículos de passeios;")
add("BR-SC", 0.02 * pbr * MEAN_FACTOR, "BRL", "Santa Catarina state (IPVA 2%; Florianópolis); licensing fee not included", "road-tax-br-sef-sc",
    f"IPVA 2% of the valor venal (Sefaz-SC, FIPE-based). Valor venal as for São Paulo, mean {pbr * MEAN_FACTOR:,.0f} -> {0.02 * pbr * MEAN_FACTOR:,.0f}. "
    "Santa Catarina gives no discount for paying in one go. The Detran-SC licensing fee (about 100 BRL) was not read, so it is missing here. Thin: base assumed.",
    "https://www.sef.sc.gov.br/noticias/secretaria-de-estado-da-fazenda-divulga-calendario-do-ipva-para-2026", "2% para carros e utilitários nacionais ou estrangeiros")

# Chile (Santiago)
UTM = 72_440
def cl_tax(v):
    steps = [(60 * UTM, .01), (120 * UTM, .02), (250 * UTM, .03), (400 * UTM, .04)]
    t, prev = 0, 0
    for top, r in steps:
        if v > prev:
            t += (min(v, top) - prev) * r
        prev = top
    if v > 400 * UTM:
        t += (v - 400 * UTM) * .045
    return max(t, UTM / 2)


pcl = car_price_local("CL")
vals = [pcl / 1.19] + [pcl * factor(k) for k in range(2, YEARS + 1)]
cl_pm = sum(cl_tax(v) for v in vals) / YEARS
cl = cl_pm + 5 * 18_000 / YEARS
add("CL", cl, "CLP", "Chile, whole country scale (permiso de circulación paid to Santiago's commune; communes keep it, rate is national)", "road-tax-cl-indicadores-permiso",
    f"Permiso de circulación: 1% of the SII tasación up to 60 UTM, 2% to 120, 3% to 250, 4% to 400, 4.5% above (UTM {UTM:,} CLP, Nov 2026). Tasación: year 1 the net invoice (price {pcl:,.0f} CLP / 1.19), "
    f"then the car module's price on a straight line; mean permiso {cl_pm:,.0f} a year. Plug-in hybrids get 25% of the tax; ordinary hybrids pay in full. "
    "Revisión técnica: since mid-2026 the first one is at 36-48 months, then yearly: 5 in 8 years at about 18,000 CLP (an aggregator's average; plants set their own price) = 11,250 a year. "
    "The SOAP insurance is left out. Thin: tasación path assumed.",
    "https://indicadores.cl/blog/permiso-circulacion-chile-2026", "Sobre 400 UTM")

# Uruguay (Montevideo)
puy = car_price_local("UY")
uy_gross = (0.05 * puy / 1.22 + sum(0.045 * puy * factor(k) for k in range(2, YEARS + 1))) / YEARS
add("UY", uy_gross * 0.8, "UYU", "Uruguay, whole country (SUCIVE collects the same patente for every department; Montevideo)", "road-tax-uy-drivo",
    f"Patente de rodados: a new car pays 5% of its value without VAT in its first year, a used one 4.5% of the 'valor de aforo' (Autodata's reference value, roughly market value). "
    f"Base = the car module's price {puy:,.0f} UYU, year 1 net of 22% VAT, years 2-8 on a straight line; mean before discounts {uy_gross:,.0f}. "
    f"Paying the whole year in January gives 20% off, so {uy_gross * 0.8:,.0f} a year (10% off if paid by instalment on time: {uy_gross * 0.9:,.0f}). No periodic inspection for private cars was found. Thin: aforo path assumed.",
    "https://www.drivo.com.uy/blog/patente-de-rodados-uruguay", "4,5 % del valor de aforo")

# Panama
add("PA", 28, "PAB", "Panama City (Alcaldía de Panamá annual circulation tax)", "road-tax-pa-telemetro-circulacion",
    "Impuesto anual de circulación for a private car: 28 PAB (Telemetro, undated). The annual 'revisado vehicular' (ATTT) is also needed to collect the sticker and its fee, and the plate/sticker charges, were not found, "
    "so the true figure is higher. Thin: a single undated press line.",
    "https://www.telemetro.com/impuesto-circulacion-a4006170", "Municipio aclara que impuesto de circulación para autos particulares seguirá siendo de B/.28.00")

# ---------------------------------------------------------------- Others
add("CA-ON", 0, "CAD", "Ontario (passenger vehicles; the plate sticker fee was abolished in 2022)", "road-tax-ca-ontario-sticker",
    "Ontario charges no annual plate renewal fee for passenger cars (automatic renewal, no sticker, no fee). There is no periodic safety inspection for a private car. Insurance is excluded. Other provinces were not checked.",
    "https://www.ontario.ca/page/renew-licence-plate-sticker", "you will not have to pay a fee")
add("AU-NSW", 84 + 391, "AUD", "New South Wales (excluding the CTP green slip)", "road-tax-au-nsw-fees",
    "Registration fee 84 AUD + vehicle tax for private use, tare 1,151-1,500 kg, 391 AUD = 475 a year (page figures before the 2.65% rise on 1 July 2026 and the one-off 100 AUD discount from September 2026). "
    "No periodic inspection for a car under 5 years; CTP insurance is excluded. Other states were not checked (Victoria charges more because its TAC levy is in the fee).",
    "https://www.nsw.gov.au/driving-boating-and-transport/driving-nsw/vehicle-registration/fees-concessions-and-forms/vehicle-registration-fees", "1151 to 1500 $391")

# ----------------------------------------------------------------
bad = []
for r in rows:
    t = text_of(r["source_id"]) if (CACHE / r["source_id"]).exists() else ""
    q = re.sub(r"\s+", " ", r["quote"])
    if q not in t:
        bad.append((r["place_code"], r["source_id"], r["quote"]))
if bad:
    print("QUOTES NOT FOUND:")
    for b in bad:
        print("  ", b)

cols = "place_code,amount,currency,unit,period,measured_for,source_id,note,url,quote".split(",")
with open(OUT / "road-tax.curated.csv", "w", newline="") as f:
    w = csv.DictWriter(f, cols)
    w.writeheader()
    w.writerows(rows)
for r in rows:
    print(f"{r['place_code']:14} {float(r['amount']):>14,.2f} {r['currency']}")
