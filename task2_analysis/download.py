"""
Downloads all mini-SWE-agent-v2 trajectories for a given Docent collection.
"""

import json
import requests
from pathlib import Path
from tqdm import tqdm
import os
from dotenv import load_dotenv

load_dotenv() 

DOCENT_SESSION = os.getenv("DOCENT_SESSION")
if not DOCENT_SESSION:
    raise RuntimeError(
        "DOCENT_SESSION not found. Add it to .env file in project root."
    )

COOKIES = {"docent_session": DOCENT_SESSION}
# base URL for the Docent public API
API_BASE = "https://api.docent.transluce.org/rest"


def get_all_agent_run_ids(collection_id: str, page_size: int = 100) -> list[str]:
    """
    Fetch all agent_run_ids in a collection by paginating through the
    /agent_run_ids_paginated/query endpoint.

    The endpoint accepts a POST with a JSON body(taken from the page using dev tools):
        {"filter": null, "sort_field": null, "sort_direction": "asc",
         "limit": <page_size>, "offset": <offset>}
    and returns:
        {"ids": ["uuid", "uuid", ...], ...}

    Returns a flat list of all ids across all pages.
    """
    url = f"{API_BASE}/{collection_id}/agent_run_ids_paginated/query"
    all_ids: list[str] = []
    offset = 0

    while True:
        body = {
            "filter": None,
            "sort_field": None,
            "sort_direction": "asc",
            "limit": page_size,
            "offset": offset,
            }

        response = requests.post(url, json=body, cookies=COOKIES)
        response.raise_for_status()  # raises if HTTP status is 4xx/5xx

        data = response.json()
        page_ids = data["ids"]

        all_ids.extend(page_ids)
        if len(page_ids) < page_size:
            break # we've reached the last page

        offset += page_size

    return all_ids

def download_trajectory(
        collection_id: str,
        agent_run_id: str,
        output_dir: Path,
        ) -> Path:
    """
    Download a single trajectory from Docent and save it as JSON.

    Skips download if the file already exists (so the script is resumable
    after interruption).

    Returns the path to the saved file.
    """
    output_path = output_dir / f"{agent_run_id}.json"

    # skip if already downloaded —> makes the script safely resumable
    if output_path.exists():
        return output_path

    url = f"{API_BASE}/{collection_id}/agent_run_with_tree"
    params = {
        "agent_run_id": agent_run_id,
        "full_tree": "false",
    }
    response = requests.get(url, params=params, cookies=COOKIES)
    response.raise_for_status()

    output_path.write_text(response.text)

    return output_path

def download_collection(
    collection_id: str,
    output_dir: Path,
    limit: int | None = None,
) -> None:
    """
    Download all trajectories from a Docent collection into output_dir.

    Already-downloaded files are skipped (download_trajectory handles that),
    so this function is safely resumable after interruption.

    Args:
        collection_id: Docent collection UUID
        output_dir: where to save trajectory JSON files
        limit: if set, stop after this many trajectories (useful for testing)
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Fetching agent_run_ids for collection {collection_id}...")
    ids = get_all_agent_run_ids(collection_id)
    print(f"Found {len(ids)} trajectories")

    if limit is not None:
        ids = ids[:limit]
        print(f"Limited to first {limit} for this run")

    for agent_run_id in tqdm(ids, desc="Downloading"):
        try:
            download_trajectory(collection_id, agent_run_id, output_dir)
        except requests.HTTPError as e:
            # Don't crash the whole batch if one trajectory fails — log and continue
            print(f"\n  ! Failed {agent_run_id}: {e}")

            
if __name__ == "__main__":
    CLAUDE_45_OPUS = "b038912e-0133-4594-b093-92806f8ffb17"
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    output_dir = PROJECT_ROOT / "data" / "trajectories" / "claude-4-5-opus-high"

    # Full download — all 500 trajectories
    download_collection(CLAUDE_45_OPUS, output_dir)