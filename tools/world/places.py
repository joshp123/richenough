"""Place codes for the world tables: cities by GeoNames id, as the plan's contract requires.

Usage from another script in tools/world/:  from places import city_code
"""

import csv
import functools
import io
import pathlib
import urllib.request
import zipfile

REPO = pathlib.Path(__file__).resolve().parents[2]
GEONAMES = REPO / "cache" / "geonames"


def _ensure_cities() -> pathlib.Path:
    path = GEONAMES / "cities15000.txt"
    if not path.exists():
        GEONAMES.mkdir(parents=True, exist_ok=True)
        data = urllib.request.urlopen("https://download.geonames.org/export/dump/cities15000.zip").read()
        zipfile.ZipFile(io.BytesIO(data)).extract("cities15000.txt", GEONAMES)
    return path


@functools.cache
def _cities() -> list[dict]:
    rows = []
    with open(_ensure_cities(), encoding="utf-8") as f:
        for r in csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
            names = {r[1].casefold(), r[2].casefold(), *(n.casefold() for n in r[3].split(",") if n)}
            rows.append({"id": r[0], "name": r[1], "country": r[8], "admin1": r[10], "population": int(r[14] or 0), "names": names})
    return rows


def city(name: str, country: str, admin1: str | None = None) -> dict:
    """The most populous GeoNames city (population 15,000+) in `country` (ISO alpha-2) called `name`."""
    key = name.casefold()
    matches = [c for c in _cities() if c["country"] == country and key in c["names"] and (admin1 is None or c["admin1"] == admin1)]
    if not matches:
        raise KeyError(f"no GeoNames city {name!r} in {country}")
    return max(matches, key=lambda c: c["population"])


def city_code(name: str, country: str, admin1: str | None = None) -> str:
    return f"CITY-{city(name, country, admin1)['id']}"


if __name__ == "__main__":
    import sys

    print(city_code(sys.argv[1], sys.argv[2]))
