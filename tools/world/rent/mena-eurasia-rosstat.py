# /// script
# requires-python = ">=3.11"
# dependencies = ["openpyxl"]
# ///
"""Russia: Rosstat's average price of renting a two-room flat from a private person, by region.

Written by AI on 2026.11.17 by model claude sonnet 5.5, for the Rich enough site.

Source: Rosstat, "Средние потребительские цены на отдельные виды товаров и услуг по Российской
Федерации, федеральным округам, субъектам Российской Федерации и обследуемым городам (в 2026 г.)",
column "Аренда двухкомнатной квартиры у частных лиц, месяц" (code 9421), price at the end of the
latest month in the workbook. Region rows are Rosstat's average over the towns it surveys in the region.

Rosstat's server uses a Russian root certificate that Python does not trust, so the download skips
certificate checks; the file is public statistics and is read, never executed.

Run: uv run tools/world/rent/mena-eurasia-rosstat.py        (prints rows as CSV)
"""

import csv
import pathlib
import ssl
import sys
import urllib.request

import openpyxl

REPO = pathlib.Path(__file__).resolve().parents[3]
FILE = REPO / "cache" / "ru-rosstat-avg-prices" / "sred_potreb_cen_09-2026.xlsx"
URL = "https://rosstat.gov.ru/storage/mediabank/sred_potreb_cen_09-2026.xlsx"
COLUMN_CODE = "9421"  # Аренда двухкомнатной квартиры у частных лиц, месяц

SOURCES = [
    {
        "source_id": "ru-rosstat-avg-prices",
        "publisher": "Rosstat (Federal State Statistics Service of Russia)",
        "title": "Average consumer prices of selected goods and services by region and surveyed city, 2026 (rent of a two-room flat from a private person)",
        "url": "https://rosstat.gov.ru/statistics/price",
        "licence": "Rosstat publishes it openly; no licence stated on the page",
        "retrieved": "2026-11-17",
        "period": "2026-09",
        "note": "Survey average at end of September 2026 over the surveyed towns of each region, rubles per month. Includes Crimea and Sevastopol; Rosstat does not list Donetsk, Luhansk, Zaporizhzhia or Kherson regions.",
    }
]

# first digits of Rosstat's territory code (OKATO) -> (ISO 3166-2 code, fragment of the Russian name as a check)
OKATO = {
    "01": ("RU-ALT", "Алтайский край"), "03": ("RU-KDA", "Краснодарский"), "04": ("RU-KYA", "Красноярский"),
    "05": ("RU-PRI", "Приморский"), "07": ("RU-STA", "Ставропольский"), "08": ("RU-KHA", "Хабаровский"),
    "10": ("RU-AMU", "Амурская"), "11": ("RU-ARK", "Архангельская"), "12": ("RU-AST", "Астраханская"),
    "14": ("RU-BEL", "Белгородская"), "15": ("RU-BRY", "Брянская"), "17": ("RU-VLA", "Владимирская"),
    "18": ("RU-VGG", "Волгоградская"), "19": ("RU-VLG", "Вологодская"), "20": ("RU-VOR", "Воронежская"),
    "22": ("RU-NIZ", "Нижегородская"), "24": ("RU-IVA", "Ивановская"), "25": ("RU-IRK", "Иркутская"),
    "26": ("RU-IN", "Ингушетия"), "27": ("RU-KGD", "Калининградская"), "28": ("RU-TVE", "Тверская"),
    "29": ("RU-KLU", "Калужская"), "30": ("RU-KAM", "Камчатский"), "32": ("RU-KEM", "Кемеровская"),
    "33": ("RU-KIR", "Кировская"), "34": ("RU-KOS", "Костромская"), "35": ("RU-CR", "Крым"),
    "36": ("RU-SAM", "Самарская"), "37": ("RU-KGN", "Курганская"), "38": ("RU-KRS", "Курская"),
    "40": ("RU-SPE", "Санкт-Петербург"), "41": ("RU-LEN", "Ленинградская"), "42": ("RU-LIP", "Липецкая"),
    "44": ("RU-MAG", "Магаданская"), "45": ("RU-MOW", "Москва"), "46": ("RU-MOS", "Московская"),
    "47": ("RU-MUR", "Мурманская"), "49": ("RU-NGR", "Новгородская"), "50": ("RU-NVS", "Новосибирская"),
    "52": ("RU-OMS", "Омская"), "53": ("RU-ORE", "Оренбургская"), "54": ("RU-ORL", "Орловская"),
    "56": ("RU-PNZ", "Пензенская"), "57": ("RU-PER", "Пермский"), "58": ("RU-PSK", "Псковская"),
    "60": ("RU-ROS", "Ростовская"), "61": ("RU-RYA", "Рязанская"), "63": ("RU-SAR", "Саратовская"),
    "64": ("RU-SAK", "Сахалинская"), "65": ("RU-SVE", "Свердловская"), "66": ("RU-SMO", "Смоленская"),
    "67": ("RU-SEV", "Севастополь"), "68": ("RU-TAM", "Тамбовская"), "69": ("RU-TOM", "Томская"),
    "70": ("RU-TUL", "Тульская"), "71": ("RU-TYU", "Тюменская"), "73": ("RU-ULY", "Ульяновская"),
    "75": ("RU-CHE", "Челябинская"), "76": ("RU-ZAB", "Забайкальский"), "77": ("RU-CHU", "Чукотский"),
    "78": ("RU-YAR", "Ярославская"), "79": ("RU-AD", "Адыгея"), "80": ("RU-BA", "Башкортостан"),
    "81": ("RU-BU", "Бурятия"), "82": ("RU-DA", "Дагестан"), "83": ("RU-KB", "Кабардино-Балкарская"),
    "84": ("RU-AL", "Республика Алтай"), "85": ("RU-KL", "Калмыкия"), "86": ("RU-KR", "Карелия"),
    "87": ("RU-KO", "Коми"), "88": ("RU-ME", "Марий Эл"), "89": ("RU-MO", "Мордовия"),
    "90": ("RU-SE", "Северная Осетия"), "91": ("RU-KC", "Карачаево-Черкесская"), "92": ("RU-TA", "Татарстан"),
    "93": ("RU-TY", "Тыва"), "94": ("RU-UD", "Удмуртская"), "95": ("RU-KK", "Хакасия"),
    "96": ("RU-CE", "Чеченская"), "97": ("RU-CU", "Чувашская"), "98": ("RU-SA", "Саха"),
    "99": ("RU-YEV", "Еврейская"),
}
OKRUGS = {"11100000000": ("RU-NEN", "Ненецкий"), "71100000000": ("RU-KHM", "Ханты-Мансийский"), "71140000000": ("RU-YAN", "Ямало-Ненецкий")}


def workbook() -> openpyxl.Workbook:
    if not FILE.exists():
        FILE.parent.mkdir(parents=True, exist_ok=True)
        context = ssl.create_default_context()
        context.check_hostname, context.verify_mode = False, ssl.CERT_NONE
        request = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
        FILE.write_bytes(urllib.request.urlopen(request, context=context, timeout=300).read())
    return openpyxl.load_workbook(FILE, read_only=True)


def rows() -> list[dict]:
    book = workbook()
    sheet = book[book.sheetnames[-1]]  # latest month, e.g. "09(2026)"
    month = book.sheetnames[-1][:2]
    data = list(sheet.iter_rows(values_only=True))
    column = next(j for j, code in enumerate(data[3]) if str(code) == COLUMN_CODE)
    assert "двухкомнатной" in data[4][column], data[4][column]
    out = []
    for row in data[5:]:
        if row[0] is None or row[column] in (None, "...", "…", "-"):
            continue
        code, name, price = str(row[0]), str(row[1]), float(row[column])
        if code == "643":
            place, measured, note = "RU", "Russian Federation, average over the surveyed towns of all regions", "National average."
        else:
            full = code.zfill(11)
            if len(full) != 11 or not full.endswith("00000000"):
                continue
            iso, fragment = OKRUGS.get(full) or OKATO.get(full[:2], (None, None)) if full[2:] == "000000000" or full in OKRUGS else (None, None)
            if iso is None:
                continue
            assert fragment in name, (code, name, fragment)
            place = iso
            measured = f"Rosstat region «{name}», average over its surveyed towns (mostly the regional capital)"
            note = "Rosstat survey average, not an advertised-rent sample."
        out.append({
            "place_code": place, "amount": round(price), "currency": "RUB", "unit": "per_month",
            "period": f"2026-{month}", "measured_for": measured, "source_id": "ru-rosstat-avg-prices",
            "note": "Rent of a two-room flat from a private person, price at end of month (Rosstat code 9421). " + note,
        })
    return out


if __name__ == "__main__":
    out = csv.DictWriter(sys.stdout, fieldnames=["place_code", "amount", "currency", "unit", "period", "measured_for", "source_id", "note"])
    out.writeheader()
    out.writerows(rows())
