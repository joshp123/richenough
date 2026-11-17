#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = ["xlrd", "openpyxl", "pypdf"]
# ///
"""Builds the East Asia rent table from every source script and curated file in this folder.

Written by AI on 2026.11.17 by model claude sonnet 5.5.

Writes next to this file:
  east-asia.table.csv         one row per place code, the rows for data/tables/rent-two-bedroom.*.csv
  east-asia.crosschecks.csv   rows that lost a place code to a better source, plus alternates (HDB, KREB stock rents, Chengdu bureau)
  east-asia.sources.all.csv   data/sources.csv rows for every source used
  east-asia-japan.districts.csv  every Tokyo, Yokohama and Kawasaki ward (REINS)

Rule when two sources give the same place code: the later one in ORDER wins and the earlier one goes to crosschecks.
Japan: REINS (signed new lets, Tokyo region) beats the Retail Price Survey (all sitting tenants) where both exist.
"""

import csv
import importlib.util
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
COLUMNS = ["place_code", "amount", "currency", "unit", "period", "measured_for", "source_id", "note"]
# (module file, function name); later entries win a place code
ORDER = [("jp_estat_rps", "rows"), ("jp_reins", "rows"), ("hk_rvd", "rows"), ("sg_ura_hdb", "rows"), ("tw_moi_lvr", "rows"),
         ("kr_molit_rtms", "rows"), ("cn_cric_creis", "rows")]
CROSSCHECK_ONLY = [("kr_reb_rone", "rows"), ("sg_ura_hdb", "alt_rows")]
CURATED = HERE / "east-asia-china-mo-mn.curated.csv"
CURATED_CROSSCHECK_SOURCES = {"cn-chengdu-rent-2026q2"}


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    table, cross, sources = {}, [], {}
    modules = {}
    for name, fn in ORDER + CROSSCHECK_ONLY:
        modules[name] = modules.get(name) or load(name)
    for name in modules:
        for s in modules[name].SOURCES:
            sources[s["source_id"]] = s
    for name, fn in ORDER:
        for row in getattr(modules[name], fn)():
            if row["place_code"] in table:
                cross.append(table[row["place_code"]])
            table[row["place_code"]] = {k: row[k] for k in COLUMNS}
    for name, fn in CROSSCHECK_ONLY:
        cross += [{k: r[k] for k in COLUMNS} for r in getattr(modules[name], fn)()]
    with open(CURATED, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            row = {k: r[k] for k in COLUMNS}
            if r["source_id"] in CURATED_CROSSCHECK_SOURCES:
                cross.append(row)
            else:
                if row["place_code"] in table:
                    cross.append(table[row["place_code"]])
                table[row["place_code"]] = row
    for path in sorted(HERE.glob("east-asia-*.sources.csv")):
        with open(path, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                sources.setdefault(r["source_id"], r)
    used = {r["source_id"] for r in list(table.values()) + cross}
    missing = used - set(sources)
    if missing:
        sys.exit(f"sources missing a description: {sorted(missing)}")

    def write(name, fields, rows):
        with open(HERE / name, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
            w.writeheader()
            w.writerows(rows)

    write("east-asia.table.csv", COLUMNS, sorted(table.values(), key=lambda r: r["place_code"]))
    write("east-asia.crosschecks.csv", COLUMNS, cross)
    fields = ["source_id", "publisher", "title", "url", "licence", "retrieved", "period", "note"]
    write("east-asia.sources.all.csv", fields, [{k: sources[s].get(k, "") for k in fields} for s in sorted(used)])
    d = modules["jp_reins"].districts()
    write("east-asia-japan.districts.csv", list(d[0]), d)
    print(f"{len(table)} rows, {len(cross)} crosschecks, {len(used)} sources", file=sys.stderr)


if __name__ == "__main__":
    main()
