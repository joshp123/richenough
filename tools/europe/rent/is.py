"""Iceland: HMS market-rent figures as quoted in a City of Reykjavik reply (March 2025), one national figure.

HMS (the Housing and Construction Authority) keeps the rent register (leiguskra) but hms.is sits behind a JavaScript
challenge, so we do not use it. The City of Reykjavik's welfare committee published a reply (VEL25010032, 3 March 2025)
that quotes HMS data: market rent (the whole market, excluding non-profit and social landlords) averaged ISK 3,505 per
m2 per month in 2024, and ISK 276,528 per flat. We price a 75 m2 flat at the per-m2 figure and bring it to 2025 with the
Eurostat HICP actual-rentals index for Iceland. HMS gives no regional split in what we could reach, so both regions
(the capital area, the rest) carry the national figure, measured_for IS. Import with importlib: `is` is a Python keyword.
"""

import re

import pdfplumber

import common as c

SOURCE_ID = "is-hms-via-reykjavik"
URL = ("https://fundur.reykjavik.is/sites/default/files/agenda-items/"
       "Svar%20vi%C3%B0%20framhaldsfyrirspurn%20um%20leiguver%C3%B0%20F%C3%A9lagsb%C3%BAsta%C3%B0a_VEL25010032.pdf")

SOURCES = [c.source(
    SOURCE_ID, "City of Reykjavik welfare department, quoting HMS (Housing and Construction Authority) rent data",
    "Svar við framhaldsfyrirspurn um leiguverð Félagsbústaða (VEL25010032), 3 March 2025", URL,
    "public council document, no licence stated", "2024",
    "HMS average market rent per m2 per month, 2024, the whole country; no regional split.")]


def rows():
    path = c.fetch(SOURCE_ID, URL, "VEL25010032.pdf")
    with pdfplumber.open(path) as pdf:
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    per_m2 = float(re.search(r"^2024 (\d)\.(\d{3}) ", text, re.M).expand(r"\1\2"))
    flat = float(re.search(r"Markaðsleiga ([\d.]+) ([\d.]+) 100% 100%", text).group(2).replace(".", ""))
    growth = c.rent_inflation("IS", 2024, 2025)
    amount = round(per_m2 * c.TWO_BED_M2 * growth, -3)
    note = (f"HMS 2024 average market rent {per_m2:.0f} ISK/m2 per month (average flat ISK {flat:.0f}), whole country, "
            f"x 75 m2 x {growth:.4f} (Eurostat HICP actual rentals, Iceland, 2024 to 2025). No regional split reachable: "
            "the same national figure is used for both regions.")
    return [c.row(c.place(nuts), amount, "ISK", "per_month", "2025", "IS", SOURCE_ID, note)
            for nuts in c.regions_in("IS")]
