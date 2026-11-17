"""Slovakia: Deloitte Rent Index Q3 2026, average asking rent of a flat in each regional capital.

Deloitte's index averages asking rents (excluding utility advances) of flats listed on real-estate portals during
the quarter, for the eight regional capitals (Poprad appears on the map but is not a regional capital). The
published city figure is per flat, all sizes (the average flat let is about 66 m2). We scale it to a 3-room
(2 bedroom) flat with the national ratio of the 3-room average (883 EUR) to the all-size average (754 EUR), 1.171.
The figures sit in the PDF's map graphic, so they are keyed in here from the cached PDF (word positions checked).
Neither the National Bank of Slovakia nor the Statistical Office publishes rents by region.
"""

import common as c

SOURCE_ID = "sk-deloitte-rent-index"
URL = ("https://www.deloitte.com/content/dam/assets-zone2/cz-sk/sk/docs/industries/financial-services/2026/"
       "Rent_Index_Q3_2026_SK.pdf")

SOURCES = [c.source(
    SOURCE_ID, "Deloitte Slovensko",
    "Rent Index Q3 2026 SR: average asking rent of flats in the regional capitals",
    URL, "free to read, no licence stated", "2026-Q3",
    "Average asking rent per flat (all sizes, ex utilities) from real-estate portals during the quarter. "
    "A consultancy report, used because no official regional rent source exists.")]

# EUR per month per flat, Q3 2026, all sizes
CITY_AVERAGE = {
    "SK010": ("Bratislava", 1013), "SK021": ("Trnava", 629), "SK022": ("Trenčín", 578), "SK023": ("Nitra", 664),
    "SK031": ("Žilina", 673), "SK032": ("Banská Bystrica", 590), "SK041": ("Prešov", 625), "SK042": ("Košice", 750),
}
NATIONAL_ALL_SIZES = 754
NATIONAL_THREE_ROOM = 883
FACTOR = NATIONAL_THREE_ROOM / NATIONAL_ALL_SIZES


def rows():
    c.fetch(SOURCE_ID, URL, "Rent_Index_Q3_2026_SK.pdf")
    out = []
    for nuts3 in c.regions_in("SK"):
        name, average = CITY_AVERAGE[nuts3]
        measured = c.city_code("SK", name) or c.place(nuts3)
        out.append(c.row(
            c.place(nuts3), round(average * FACTOR), "EUR", "per_month", "2026-Q3", measured, SOURCE_ID,
            f"Deloitte Rent Index Q3 2026: average asking rent in {name} {average} EUR per flat (all sizes, avg about "
            f"66 m2), x {FACTOR:.3f} (national 3-room {NATIONAL_THREE_ROOM} / all sizes {NATIONAL_ALL_SIZES}) for a "
            f"3-room flat. Portal asking rents, ex utilities."))
    return out
