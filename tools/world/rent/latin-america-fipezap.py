#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["openpyxl"]
# ///
"""Brazil: monthly asking rent per m2 for apartments, from the FipeZAP residential rent index.

Written by AI on 2026.11.17 by model claude sonnet 5.5, for the world-data owner.

FipeZAP (Fipe, the University of Sao Paulo's economic research institute, with the OLX Group portals
Zap, Viva Real and OLX) tracks advertised rents of ready apartments in 36 cities and publishes a free
workbook. The "Resumo" sheet has, per city, the latest average rent in R$ per m2 (3-month moving average
of asking rents). The workbook gives per-bedroom figures only for sales, not for rents, so every figure
here is for apartments of all sizes. Small flats cost more per m2, so a 75 m2 two-bed at this rate may be
a little overstated.

The table row is R$ per m2 x 75 m2, as the brief instructs. Rows:
  - BR            : the FipeZAP index average (all monitored cities together).
  - CITY-<geoname>: each city with a published rent figure.
  - BR-<UF>       : the state's main monitored city (the state capital, or Vitoria etc.), for the 22 states
                    that have one. The five states without a monitored city (AC, AP, RO, RR, TO) get no row.

Run: uv run tools/world/rent/latin-america-fipezap.py        (prints the rows as CSV)
"""

import csv
import pathlib
import sys
import urllib.request

import openpyxl

REPO = pathlib.Path(__file__).resolve().parents[3]
CACHE = REPO / "cache" / "fipezap"
XLSX = CACHE / "fipezap-serieshistoricas.xlsx"
URL = "https://downloads.fipe.org.br/indices/fipezap/fipezap-serieshistoricas.xlsx"
AREA_M2 = 75

SOURCES = [{
    "source_id": "fipezap-locacao",
    "publisher": "Fipe and OLX Group (Zap, Viva Real, OLX)",
    "title": "Indice FipeZAP de Locacao Residencial, planilha de series historicas (aba Resumo)",
    "url": "https://www.fipe.org.br/pt-br/indices/fipezap",
    "licence": "free to download, no licence stated on the page",
    "retrieved": "2026-11-17",
    "period": "2026-10",
    "note": "Advertised rent per m2 of ready apartments, all sizes, 3-month moving average, 36 cities; monthly PDF reports at downloads.fipe.org.br/indices/fipezap/fipezap-YYYYMM-residencial-locacao.pdf",
}]

# State -> the monitored city that stands for it.
STATE_CITY = {
    "SP": "São Paulo", "RJ": "Rio de Janeiro", "MG": "Belo Horizonte", "ES": "Vitória", "PR": "Curitiba",
    "SC": "Florianópolis", "RS": "Porto Alegre", "DF": "Brasília", "MS": "Campo Grande", "MT": "Cuiabá",
    "GO": "Goiânia", "SE": "Aracaju", "CE": "Fortaleza", "PB": "João Pessoa", "AL": "Maceió", "RN": "Natal",
    "PE": "Recife", "MA": "São Luís", "BA": "Salvador", "PI": "Teresina", "PA": "Belém", "AM": "Manaus",
}


def _workbook() -> pathlib.Path:
    if not XLSX.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
        XLSX.write_bytes(urllib.request.urlopen(req, timeout=120).read())
    return XLSX


def _resumo() -> tuple[str, dict[str, tuple[str | None, float]]]:
    """(period 'YYYY-MM', {name: (uf, R$/m2)}) from the Resumo sheet; 'Indice FipeZAP' is the all-city mean."""
    ws = openpyxl.load_workbook(_workbook(), read_only=True, data_only=True)["Resumo"]
    rows = list(ws.iter_rows(values_only=True))
    period = rows[5][10].strftime("%Y-%m")  # reference date of the rent price column
    out = {}
    for r in rows[6:]:
        name, uf, price = r[0], r[2], r[10]
        if isinstance(name, str) and isinstance(price, (int, float)):
            out[name] = (uf, float(price))
    return period, out


def rows() -> list[dict]:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
    from places import city_code

    period, cities = _resumo()

    def row(code, measured, price, note):
        return {
            "place_code": code, "amount": f"{price * AREA_M2:.0f}", "currency": "BRL", "unit": "per_month",
            "period": period, "measured_for": measured, "source_id": "fipezap-locacao",
            "note": f"R$ {price:.2f}/m2 (FipeZAP asking rent, apartments of all sizes, 3-month average) x {AREA_M2} m2. {note}",
        }

    out = []
    idx = cities["Índice FipeZAP"][1]
    out.append(row("BR", "The 36 Brazilian cities in the FipeZAP index together, apartments for rent",
                   idx, "Not a national average: the index covers 36 cities, weighted by the size of each city's market."))
    for name, (uf, price) in cities.items():
        if name == "Índice FipeZAP":
            continue
        try:
            code = city_code(name, "BR")
        except KeyError:
            continue
        out.append(row(code, f"{name} ({uf}), whole city, apartments for rent", price, ""))
        if STATE_CITY.get(uf) == name:
            out.append(row(f"BR-{uf}", f"{name}, the state's main monitored city (state capital), not the whole state",
                           price, "Written under the state code because no state-wide rent exists."))
    return out


if __name__ == "__main__":
    w = csv.DictWriter(sys.stdout, ["place_code", "amount", "currency", "unit", "period", "measured_for", "source_id", "note"])
    w.writeheader()
    w.writerows(rows())
