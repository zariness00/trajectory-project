"""
analyze.py -> run count_messages over a directory of trajectories
and summarize results into a CSV.

Usage:
    python analyze.py <path_to_trajectory_dir> --output results.csv
"""

import argparse
import csv
import sys
from pathlib import Path
import json

# task1_tool package importable when running from project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from task1_tool.count_messages import load_messages, count_by_role
from tqdm import tqdm


def analyze_directory(trajectories_dir: Path) -> list[dict]:
    """
    Iterate over all .json files in trajectories_dir, count messages
    per role for each, and return a list of result dicts.

    Each result dict has keys:
        agent_run_id, system, user, assistant, tool, total
    """
    results = []
    json_files = sorted(trajectories_dir.glob("*.json"))

    for path in tqdm(json_files, desc="Analyzing"):
        try:
            messages = load_messages(path)
            counts = count_by_role(messages)

            # extracting metadata from the traj file
            with path.open() as f:
                data = json.load(f)
            agent_run_id = data[0]
            metadata = agent_run_id.get("metadata", {})

        except (KeyError, IndexError, ValueError) as e:
            print(f"\nSkipped {path.name}: {e}", file=sys.stderr)
            continue
        results.append({
            "agent_run_id": path.stem, # filename without json
            "instance_id": metadata.get("instance_id", ""),
            "exit_status": metadata.get("exit_status", ""),
            "resolved": metadata.get("scores", {}).get("resolved", 0),
            "api_calls": metadata.get("model_stats", {}).get("api_calls", 0),
            "instance_cost": metadata.get("model_stats", {}).get("instance_cost", 0.0),
            "mini_version": metadata.get("mini_version", ""),
            "system": counts.get("system", 0),
            "user": counts.get("user", 0),
            "assistant": counts.get("assistant", 0),
            "tool": counts.get("tool", 0),
            "total": sum(counts.values()),
        })

    return results


def write_csv(results: list[dict], output_path: Path) -> None:

    if not results:
        print("No results to write", file=sys.stderr)
        return

    fieldnames = ["agent_run_id", "instance_id", "exit_status", "resolved", 
                  "api_calls", "instance_cost", "mini_version", "system",
                    "user", "assistant", "tool", "total"]
    with output_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Wrote {len(results)} rows to {output_path}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("directory", type=Path, help="dir with trajectory JSONs")
    parser.add_argument("--output", type=Path, required=True, help="output csv path")
    args = parser.parse_args()

    if not args.directory.is_dir():
        print(f"Not a directory: {args.directory}", file=sys.stderr)
        return 1

    results = analyze_directory(args.directory)
    write_csv(results, args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())