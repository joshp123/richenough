# /// script
# requires-python = ">=3.12"
# dependencies = ["pandas>=2.2", "openpyxl", "xlrd", "odfpy", "pyxlsb", "pdfplumber", "lxml", "requests"]
# ///
"""Run one module without writing anything: `uv run tools/europe/check.py rent.de [--all]`.

Prints its sources, the rows it makes, and which NUTS 3 regions of its country have no row. Safe to run while
others build, because it writes only to cache/.
"""

import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd  # noqa: E402

import build  # noqa: E402
import common  # noqa: E402


def main(name: str, show_all: bool) -> None:
    module = importlib.import_module(name)
    for s in getattr(module, "SOURCES", []):
        print(f"source {s['source_id']}: {s['publisher']} | {s['licence']} | {s['period']} | {s['url']}")
    rows = build.check(name, list(module.rows()), name)
    df = pd.DataFrame(rows, columns=common.COLUMNS)
    print(f"{len(df)} rows")
    with pd.option_context("display.max_rows", None if show_all else 40, "display.max_colwidth", 90, "display.width", 250):
        print(df.drop(columns=["note"]).to_string() if not show_all else df.to_string())
    if len(df):
        print(df["amount"].describe().to_string())
        countries = {p.removeprefix("NUTS-")[:2] for p in df["place_code"] if p.startswith("NUTS-")}
        expected = {c for cc in countries for c in common.regions_in(cc)}
        missing = sorted(expected - {p.removeprefix("NUTS-") for p in df["place_code"]})
        print(f"NUTS 3 regions without a row: {len(missing)} {missing}")
        dupes = df["place_code"][df["place_code"].duplicated()].tolist()
        if dupes:
            print(f"DUPLICATE place codes: {dupes}")


if __name__ == "__main__":
    main(sys.argv[1], "--all" in sys.argv)
