#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""Chile: median asking rent of two-bedroom flats per comuna, from Aguila Inmobiliaria's open CSV.

Written by AI on 2026.11.17 by model claude sonnet 5.5, for the world-data owner.

Aguila is a small Chilean portal. Its monthly rent report (7,013 de-duplicated flat ads on 10 Oct 2026) is
published with a CSV of one row per comuna and bedroom count: n, quartiles, rent per m2, median area. A figure
is only published when there are at least 30 ads. Asking rents in pesos; ads in UF are converted at the UF of
the cut-off date. The median 2-bed flat is smaller (55 m2 nationally) than the 70 to 85 m2 the table asks for.

Rows:
  - CL            : median of all 2,942 two-bed ads in Chile.
  - CITY-<Santiago>: Providencia comuna (central and sought-after), not the whole city; the note lists the
                    other comunas of Santiago.
  - CITY-<x>, CL-<region>: the comuna with most two-bed ads in each other region, for the 9 regions where it
                    has at least 30 two-bed ads; the region row repeats the figure of that main town.
Santiago region (CL-RM) gets no row: its comunas differ by a factor of three and no single one stands for it.

Run: uv run tools/world/rent/latin-america-aguila.py        (prints the rows as CSV)
"""

import csv
import io
import pathlib
import sys
import urllib.request

REPO = pathlib.Path(__file__).resolve().parents[3]
CACHE = REPO / "cache" / "aguila-cl"
CSV_FILE = CACHE / "informe-arriendos-2026-10.csv"
CSV_URL = "https://aguilainmobiliaria.cl/informes/informe-arriendos-2026-10.csv"
REPORT_URL = "https://aguilainmobiliaria.cl/informes/arriendos-2026-10/"

SOURCES = [{
    "source_id": "aguila-cl-arriendos", "publisher": "Aguila Inmobiliaria (Chile)", "title": "Informe de arriendos de Chile, octubre de 2026",
    "url": REPORT_URL, "licence": "free to read; the page offers its table as open CSV, no licence stated", "retrieved": "2026-11-17", "period": "2026-10",
    "note": "Asking rents of 7,013 de-duplicated flat ads on the portal at 10 Oct 2026; a figure needs at least 30 ads",
}]

REGION_CODE = {
    "Valparaíso": "CL-VS", "Biobío": "CL-BI", "Araucanía": "CL-AR", "Maule": "CL-ML", "Antofagasta": "CL-AN", "Coquimbo": "CL-CO",
    "O'Higgins": "CL-LI", "Los Lagos": "CL-LL", "Ñuble": "CL-NB", "Los Ríos": "CL-LR", "Atacama": "CL-AT", "Arica y Parinacota": "CL-AP", "Tarapacá": "CL-TA",
}
SANTIAGO_COMUNAS = ("Providencia", "Las Condes", "Ñuñoa", "Santiago", "Vitacura", "Lo Barnechea", "La Florida", "Maipú")


def _csv() -> list[dict]:
    if not CSV_FILE.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(CSV_URL, headers={"User-Agent": "Mozilla/5.0"})
        CSV_FILE.write_bytes(urllib.request.urlopen(req, timeout=60).read())
    return list(csv.DictReader(io.StringIO(CSV_FILE.read_text(encoding="utf-8-sig"))))


def _row(code: str, measured: str, r: dict, extra: str = "") -> dict:
    return {
        "place_code": code, "amount": r["mediana_arriendo_mensual"], "currency": "CLP", "unit": "per_month", "period": "2026-10",
        "measured_for": f"{measured}; median asking rent of 2-bedroom flats on Aguila",
        "source_id": "aguila-cl-arriendos",
        "note": (f"{r['n']} ads, quartiles {int(r['p25_arriendo_mensual']):,} to {int(r['p75_arriendo_mensual']):,}, median flat {r['superficie_mediana_m2']} m2, "
                 f"CLP {r['mediana_por_m2']} per m2 (x 75 m2 = {int(r['mediana_por_m2']) * 75:,}). Aguila is a small portal; asking rents, not leases. {extra}").strip(),
    }


def rows() -> list[dict]:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
    from places import city_code

    two = [r for r in _csv() if r["dormitorios"] == "2"]
    by_name = {r["nombre"]: r for r in two if r["nivel"] == "comuna"}
    out = [_row("CL", "All Chile, every comuna together", next(r for r in two if r["nivel"] == "pais"),
                "Understates a 70 to 85 m2 flat because the median 2-bed ad is only 55 m2.")]
    others = "; ".join(f"{n} {int(by_name[n]['mediana_arriendo_mensual']):,} ({by_name[n]['n']} ads)" for n in SANTIAGO_COMUNAS if n in by_name and n != "Providencia")
    out.append(_row(city_code("Santiago", "CL"), "Providencia comuna, Santiago (central and sought-after, not the whole city)", by_name["Providencia"], f"Other comunas: {others}."))
    best: dict[str, dict] = {}
    for r in by_name.values():
        if r["region"] in REGION_CODE and int(r["n"]) >= 30 and int(r["n"]) > int(best.get(r["region"], {"n": 0})["n"]):
            best[r["region"]] = r
    for region, r in sorted(best.items()):
        town = r["nombre"]
        out.append(_row(city_code(town, "CL"), f"{town} comuna, whole comuna", r))
        out.append(_row(REGION_CODE[region], f"{town}, the region's comuna with most 2-bed ads, not the whole region", r))
    return out


if __name__ == "__main__":
    w = csv.DictWriter(sys.stdout, ["place_code", "amount", "currency", "unit", "period", "measured_for", "source_id", "note"])
    w.writeheader()
    w.writerows(rows())
