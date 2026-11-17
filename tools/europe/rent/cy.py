"""Cyprus: Ministry of Interior's indicative monthly rent of an 80 m2 two-bed flat, Nicosia Municipality, September 2026.

Cyprus has no official rent level by area that we can open: the Central Bank and the RICS/KPMG Cyprus Property Index
publish price and rent indices only (no euro levels), and CYSTAT has none. The Ministry of Interior's study of
indicative rents (drawn on Department of Lands and Surveys data, for the affordable-rent scheme) lists rents of 80 m2
two-bed flats and 150 m2 three-bed houses by municipality. We could not find the Ministry's own document; the figures
come from dom.com.cy's report of the study, itself citing philenews.

The island (CY000) is one NUTS 3 region: we use Nicosia, the capital. Limassol (1,500) is in the note.
"""

import html
import re

import common as c

SOURCE_ID = "cy-moi-indicative-rents"
URL = "https://dom.com.cy/en/live/digest/rental-rates-in-cyprus-have-stabilized/"

SOURCES = [c.source(
    SOURCE_ID, "Cyprus Ministry of Interior (as reported by dom.com.cy)",
    "Indicative monthly rent of 80 m2 two-bedroom apartments by area, September 2026 (Ministry of Interior study)",
    URL, "Ministry document not found; press report, free to read, no licence stated", "2026-09",
    "Indicative rents for newly built or recently renovated unfurnished flats, an affordable-rent benchmark; unchanged "
    "since September 2024 in most areas. Original Ministry document not located.")]


def _amount(text: str, area: str) -> int:
    m = re.search(rf"{re.escape(area)} (?:—|-|–) €\s?([\d,]+)", text)
    if not m:
        raise ValueError(f"{area} not found in the dom.com.cy page")
    return int(m.group(1).replace(",", ""))


def rows():
    page = c.fetch(SOURCE_ID, URL, "rental-rates-in-cyprus-have-stabilized.html").read_text(errors="ignore")
    text = html.unescape(re.sub(r"\s+", " ", re.sub(r"<script.*?</script>|<style.*?</style>|<[^>]+>", " ", page, flags=re.S)))
    text = text.split("How Much Does It Cost to Rent a Two-Bedroom Apartment?")[-1].split("Three-Bedroom House")[0]
    nicosia = _amount(text, "Nicosia Municipality")
    limassol = _amount(text, "Limassol Municipality")
    return [c.row(
        c.place("CY000"), nicosia, "EUR", "per_month", "2026-09", c.city_code("CY", "Nicosia"), SOURCE_ID,
        f"Ministry of Interior indicative monthly rent, 80 m2 two-bed flat, Nicosia Municipality, Sept 2026 (unchanged "
        f"since Sept 2024); an affordable-rent benchmark for new or renovated unfurnished flats, so probably at or below "
        f"the market. Limassol Municipality {limassol}. Press report of the study, Ministry document not found.")]
