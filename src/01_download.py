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

# Path in the Hugging Face repo -> local file name
FILES = {
    "release_2026_01_15/data/intermediate/aei_raw_claude_ai_2025-11-13_to_2025-11-20.csv":
        "aei_raw_claude_ai_2025-11-13_to_2025-11-20.csv",
    "release_2025_03_27/onet_task_statements.csv":
        "onet_task_statements.csv",
    "release_2025_03_27/SOC_Structure.csv":
        "SOC_Structure.csv",
}


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    for repo_path, local_name in FILES.items():
        target = RAW_DIR / local_name
        if target.exists():
            print(f"Already downloaded: {target}")
            continue

        cached = hf_hub_download(
            repo_id=REPO_ID,
            repo_type="dataset",
            filename=repo_path,
        )
        shutil.copy(cached, target)
        print(f"Saved: {target} ({target.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()