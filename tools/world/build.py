"""Rebuild every world table from the raw files, in order.

Run from the repository root:  python3 tools/world/build.py [--fetch]
--fetch first downloads any raw file missing from cache/ (World Bank, IMF, Treasury, ECB, Eurostat, ILOSTAT).
Region and insurer scripts download their own raw files into cache/<source_id>/ when missing.
Writes data/tables/*.world.csv, data/reference/price-level-everyday-expat.world.csv and this agent's rows of
data/sources.csv. Notes: .agent/research/world.md.
"""

import subprocess
import sys

from lib import REPO

STEPS = [
    ["uv", "run", "--quiet", "tools/world/health/ipmi_tables.py"],
    ["uv", "run", "--quiet", "tools/world/health/couple_cost.py"],
    [sys.executable, "tools/world/exchange_rates.py"],
    [sys.executable, "tools/world/price_level.py"],
    [sys.executable, "tools/world/price_level_expat.py"],
    [sys.executable, "tools/world/health.py"],
    [sys.executable, "tools/world/housekeeper.py"],
    [sys.executable, "tools/world/car.py"],
    [sys.executable, "tools/world/rent.py"],
]

if __name__ == "__main__":
    if "--fetch" in sys.argv:
        subprocess.run([sys.executable, "tools/world/fetch.py"], cwd=REPO, check=True)
    for step in STEPS:
        print("==", " ".join(step[-1:]))
        subprocess.run(step, cwd=REPO, check=True)
