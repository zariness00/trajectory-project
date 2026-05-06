import csv
import statistics
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS = PROJECT_ROOT / "results"


def summarize(csv_path: Path) -> dict:
    with csv_path.open() as f:
        rows = list(csv.DictReader(f))

    totals = [int(r["total"]) for r in rows]
    assistants = [int(r["assistant"]) for r in rows]
    tools = [int(r["tool"]) for r in rows]
    costs = [float(r["instance_cost"]) for r in rows]
    resolved = sum(1 for r in rows if r["resolved"] == "1")
    limits_hit = sum(1 for r in rows if r["exit_status"] == "LimitsExceeded")

    return {
        "model": csv_path.stem,
        "n": len(rows),
        "resolved_pct": resolved / len(rows) * 100,
        "limits_pct": limits_hit / len(rows) * 100,
        "median_total": statistics.median(totals),
        "mean_total": statistics.mean(totals),
        "p95_total": sorted(totals)[int(len(totals) * 0.95)],
        "max_total": max(totals),
        "tool_per_assistant": sum(tools) / sum(assistants),
        "total_cost": sum(costs),
        "cost_per_resolved": sum(costs) / resolved if resolved else float("inf"),
    }


def print_table(summaries: list[dict]) -> None:
    headers = [
        ("model", "{:<28}"),
        ("n", "{:>5}"),
        ("resolved_pct", "{:>7.1f}%"),
        ("limits_pct", "{:>7.1f}%"),
        ("median_total", "{:>7.0f}"),
        ("p95_total", "{:>7.0f}"),
        ("max_total", "{:>5}"),
        ("tool_per_assistant", "{:>6.2f}"),
        ("total_cost", "${:>7.2f}"),
        ("cost_per_resolved", "${:>6.2f}"),
    ]
    # header row
    print(" ".join(name.replace("_", " ").rjust(8) if "{:>" in fmt else name.ljust(28) for name, fmt in headers))
    print("-" * 101)
    for s in summaries:
        print(" ".join(fmt.format(s[name]) for name, fmt in headers))


if __name__ == "__main__":
    csvs = sorted(RESULTS.glob("*.csv"))
    summaries = [summarize(p) for p in csvs]
    summaries.sort(key=lambda s: s["resolved_pct"], reverse=True)
    print_table(summaries)

# Save the human-readable table
table_path = RESULTS / "comparison_table.txt"
with table_path.open("w") as f:
    # Redirect prints to file by reusing the same logic
    headers = [
        ("model", "{:<28}"),
        ("n", "{:>5}"),
        ("resolved_pct", "{:>7.1f}%"),
        ("limits_pct", "{:>7.1f}%"),
        ("median_total", "{:>7.0f}"),
        ("p95_total", "{:>7.0f}"),
        ("max_total", "{:>5}"),
        ("tool_per_assistant", "{:>6.2f}"),
        ("total_cost", "${:>7.2f}"),
        ("cost_per_resolved", "${:>6.2f}"),
    ]
    header_line = " ".join(
        name.replace("_", " ").rjust(8) if "{:>" in fmt else name.ljust(28)
        for name, fmt in headers
    )
    f.write(header_line + "\n")
    f.write("-" * 130 + "\n")
    for s in summaries:
        f.write(" ".join(fmt.format(s[name]) for name, fmt in headers) + "\n")
print(f"\nSaved table to {table_path}")
