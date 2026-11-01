"""
Download the Anthropic Economic Index files used in this project.

The BLS OEWS file must be downloaded manually (BLS blocks scripted downloads):
https://www.bls.gov/oes/tables.htm -> May 2025 -> National -> XLSX
Unzip it into data/raw/.
"""

import shutil
from pathlib import Path

from huggingface_hub import hf_hub_download

RAW_DIR = Path("data/raw")
REPO_ID = "Anthropic/EconomicIndex"

# Local file name -> path(s) in the Hugging Face repo, tried in order.
# The dataset README lists the Nov 2025 API file under the 2025-09-15 folder;
# the 2026-01-15 folder is tried as a fallback in case it has moved.
FILES = {
    "aei_raw_claude_ai_2025-11-13_to_2025-11-20.csv": [
        "release_2026_01_15/data/intermediate/aei_raw_claude_ai_2025-11-13_to_2025-11-20.csv",
    ],
    "aei_raw_1p_api_2025-11-13_to_2025-11-20.csv": [
        "release_2025_09_15/data/intermediate/aei_raw_1p_api_2025-11-13_to_2025-11-20.csv",
        "release_2026_01_15/data/intermediate/aei_raw_1p_api_2025-11-13_to_2025-11-20.csv",
    ],
    "onet_task_statements.csv": [
        "release_2025_03_27/onet_task_statements.csv",
    ],
    "SOC_Structure.csv": [
        "release_2025_03_27/SOC_Structure.csv",
    ],
}


def download(local_name: str, repo_paths: list[str]) -> None:
    target = RAW_DIR / local_name
    if target.exists():
        print(f"Already downloaded: {target}")
        return

    for repo_path in repo_paths:
        try:
            cached = hf_hub_download(repo_id=REPO_ID, repo_type="dataset", filename=repo_path)
        except Exception as error:  # file missing at this path, or a network error
            print(f"Could not download {repo_path}: {type(error).__name__}. Trying next location.")
            continue
        shutil.copy(cached, target)
        print(f"Saved: {target} ({target.stat().st_size / 1e6:.1f} MB) from {repo_path}")
        return

    raise FileNotFoundError(f"{local_name} was not found at any known location: {repo_paths}")


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for local_name, repo_paths in FILES.items():
        download(local_name, repo_paths)


if __name__ == "__main__":
    main()