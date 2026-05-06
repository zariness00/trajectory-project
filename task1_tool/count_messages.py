"""
count_messages.py — count messages by role in a mini-SWE-agent-v2 trajectory.

Usage:
    python count_messages.py <path_to_trajectory.json>

Counting convention:
    Each object in transcripts[0].messages is counted as one message,
    based on its `role` field. Parallel tool_calls inside a single assistant
    message do not increase the assistant count — that is still one message.
    This matches Docent UI's "Minimap (N messages)" count.
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path


# Roles I expect in mini-SWE-agent-v2 trajectories based on the task desccription and what I've seen in the UI
EXPECTED_ROLES = ("system", "user", "assistant", "tool")


def load_messages(trajectory_path: Path) -> list[dict]:
    """
    Load a trajectory JSON file and return its list of messages.

    The Docent API returns a JSON array where the first element is the
    agent_run object. Messages live at: data[0]["transcripts"][0]["messages"]
    """
    with trajectory_path.open() as f:
        data = json.load(f)
        messages = data[0]["transcripts"][0]["messages"] 
    #   data is a list, data[0] is a dict with a "transcripts" key,
    #   transcripts[0] is a dict with a "messages" key
    return messages


def count_by_role(messages: list[dict]) -> Counter:
    """
    Count messages by their `role` field.

    Returns a Counter where keys are roles ("system", "user", "assistant",
    "tool", possibly others) and values are counts.
    """
    counts = Counter()
    for message in messages:
        role = message.get("role", "unknown") # default to "unknown" if no role 
        counts[role] += 1


    return counts


def format_report(counts: Counter) -> str:
    """
    Format counts as a human-readable text report matching the spec.

    Example output:
        System messages:     1
        User messages:       1
        Assistant messages: 32
        Tool messages:      32
        ======================
        Total messages:     66
    """
    total = sum(counts.values())
    lines = [
        f"System messages:    {counts.get('system', 0):3d}",
        f"User messages:      {counts.get('user', 0):3d}",
        f"Assistant messages: {counts.get('assistant', 0):3d}",
        f"Tool messages:      {counts.get('tool', 0):3d}",
        "=" * 22,
        f"Total messages:     {total:3d}",
    ]

    # for any unexpected roles that might show up, surface them as a warning at the bottom
    unexpected = {r: c for r, c in counts.items() if r not in EXPECTED_ROLES}
    if unexpected:
        lines.append("")
        lines.append(f"Oops: unexpected roles found: {unexpected}")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("trajectory", type=Path, help="Path to a trajectory JSON file")
    args = parser.parse_args()

    if not args.trajectory.exists():
        print(f"Error: file not found: {args.trajectory}", file=sys.stderr)
        return 1

    messages = load_messages(args.trajectory)
    counts = count_by_role(messages)
    print(format_report(counts))
    return 0


if __name__ == "__main__":
    sys.exit(main())


# "при анализе посмотреть отношение tool/assistant — оно намекает на использование параллельных tool_calls"
# assistant messages (912a0729) contain multiple parallel tool_calls, 
# the ratio of tool messages to assistant messages can hint at how much parallelism is happening.
#  If the ratio is close to 1, it suggests that most assistant messages are followed by one tool call. 
# If the ratio is higher, it indicates that many assistant messages are triggering multiple parallel tool calls.