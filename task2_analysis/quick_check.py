import csv
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = PROJECT_ROOT / "results" / "claude-4-5-opus-high.csv"

with CSV_PATH.open() as f:
    rows = list(csv.DictReader(f))

# Resolution rate
resolved = sum(1 for r in rows if r["resolved"] == "1")
print(f"Resolved: {resolved}/{len(rows)} = {resolved / len(rows) * 100:.1f}%")

# Exit statuses
exits = Counter(r["exit_status"] for r in rows)
print(f"Exit statuses: {dict(exits)}")

# Mini versions (sanity check — should all be same)
versions = Counter(r["mini_version"] for r in rows)
print(f"Mini versions: {dict(versions)}")

# Total cost
total_cost = sum(float(r["instance_cost"]) for r in rows)
print(f"Total cost: ${total_cost:.2f}")