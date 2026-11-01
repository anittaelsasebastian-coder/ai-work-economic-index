"""
Step 1 — Import the four raw files and run basic checks.

Run from the project root:
    python src/02_import.py

Nothing is changed or saved: this step only loads the files and prints
what was loaded, so you can confirm the data arrived intact.
"""

from pathlib import Path

import pandas as pd

RAW = Path("data/raw")

FILES = {
    "claude_ai": "aei_raw_claude_ai_2025-11-13_to_2025-11-20.csv",
    "api": "aei_raw_1p_api_2025-11-13_to_2025-11-20.csv",
    "onet_tasks": "onet_task_statements.csv",
    "soc": "SOC_Structure.csv",
}

AEI_COLUMNS = [
    "geo_id", "geography", "date_start", "date_end", "platform_and_product",
    "facet", "level", "variable", "cluster_name", "value",
]


def load_all() -> dict[str, pd.DataFrame]:
    """Read every file as text, so codes like 11-2021 are never turned into dates."""
    missing = [name for name in FILES.values() if not (RAW / name).exists()]
    if missing:
        raise FileNotFoundError(f"Missing in {RAW}/: {missing}. Run src/01_download.py first.")

    return {key: pd.read_csv(RAW / name, dtype=str, keep_default_na=False, na_values=[""])
            for key, name in FILES.items()}


def convert_aei_numbers(df: pd.DataFrame, label: str) -> pd.DataFrame:
    """Convert value and level to numbers, keeping the original text for the audit trail."""
    df = df.copy()
    df["value_raw"] = df["value"]
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df["level"] = pd.to_numeric(df["level"], errors="coerce")

    failed = df["value"].isna() & df["value_raw"].notna()
    print(f"  {label}: {failed.sum()} values could not be converted to numbers")
    if failed.any():
        print(df.loc[failed, ["facet", "variable", "value_raw"]].head(10).to_string())
    return df


def check_aei(df: pd.DataFrame, label: str) -> None:
    print(f"\n=== {label}: {len(df):,} rows ===")
    missing_cols = set(AEI_COLUMNS) - set(df.columns)
    print("  Columns OK" if not missing_cols else f"  MISSING COLUMNS: {missing_cols}")
    print(f"  Platform:   {df['platform_and_product'].unique().tolist()}")
    print(f"  Dates:      {df['date_start'].unique().tolist()} to {df['date_end'].unique().tolist()}")
    print(f"  Geography:  {df['geography'].value_counts().to_dict()}")
    print(f"  Facets:     {df['facet'].nunique()} unique")
    print(f"  Duplicate rows: {df.duplicated().sum()}")


def check_soc_codes(soc: pd.DataFrame) -> None:
    """Excel turns codes like 11-2021 into 'Nov-21'. Any month name means the file is damaged."""
    months = "Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec"
    code_cols = soc.columns[:5]
    damaged = soc[code_cols].apply(lambda col: col.str.contains(months, na=False)).any(axis=1)
    if damaged.any():
        print(f"\n  WARNING: {damaged.sum()} SOC rows contain dates instead of codes.")
        print("  Delete data/raw/SOC_Structure.csv and run src/01_download.py again.")
    else:
        print("\n  SOC codes OK: no Excel date damage found")


def main() -> None:
    data = load_all()

    print("Rows loaded:")
    for key, df in data.items():
        print(f"  {key:<11} {len(df):>10,} rows  {df.shape[1]} columns")

    print("\nConverting numbers:")
    data["claude_ai"] = convert_aei_numbers(data["claude_ai"], "claude_ai")
    data["api"] = convert_aei_numbers(data["api"], "api")

    check_aei(data["claude_ai"], "Claude.ai")
    check_aei(data["api"], "1P API")

    print("\n=== O*NET task statements ===")
    print(f"  Columns: {data['onet_tasks'].columns.tolist()}")
    print(f"  Task types: {data['onet_tasks']['Task Type'].value_counts(dropna=False).to_dict()}")
    print(f"  Occupations: {data['onet_tasks']['O*NET-SOC Code'].nunique():,}")

    print("\n=== SOC structure ===")
    print(f"  Columns: {data['soc'].columns.tolist()}")
    check_soc_codes(data["soc"])


if __name__ == "__main__":
    main()