"""
Step 8 — Package the dashboard tables into one Excel file for Power BI (browser).

Power BI in the browser imports every Excel *table* in a workbook as a table in one
semantic model, so each sheet below is written as a formatted Excel table.

Run from the project root, after the SQL step:
    python src/08_export_powerbi.py

Output: data/outputs/powerbi_model.xlsx
"""

from pathlib import Path

import pandas as pd
from openpyxl import load_workbook
from openpyxl.worksheet.table import Table, TableStyleInfo

PROC = Path("data/processed")
OUT = Path("data/outputs")
TARGET = OUT / "powerbi_model.xlsx"

# Fact table columns for the Roles and tasks page (task x occupation x platform).
FACT_COLUMNS = [
    "platform", "task", "onet_soc_code", "task_type", "n", "n_alloc", "k_occupations",
    "success_yes", "success_no", "collab_directive", "collab_feedback_loop",
    "collab_task_iteration", "collab_learning", "collab_validation",
    "success_rate", "automation_share", "work_share", "speedup",
]


def build_tables() -> dict[str, pd.DataFrame]:
    fact = pd.read_csv(PROC / "task_occupation.csv")
    fact = fact[[c for c in FACT_COLUMNS if c in fact.columns]]

    platform = pd.DataFrame({
        "platform": ["claude_ai", "api"],
        "platform_label": ["Claude.ai (consumer)", "API (business)"],
        "sort_order": [1, 2],
    })

    return {
        "TaskUsage": pd.read_csv(OUT / "q1_usage_by_task.csv"),
        "PlatformComparison": pd.read_csv(OUT / "q2_platform_comparison.csv"),
        "PilotCandidates": pd.read_csv(OUT / "q3_pilot_candidates.csv"),
        "Checks": pd.read_csv(OUT / "q9_reconciliation_checks.csv"),
        "TaskOccupation": fact,
        "Occupation": pd.read_csv(PROC / "occupation.csv"),
        "Platform": platform,
    }


def write_workbook(tables: dict[str, pd.DataFrame]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(TARGET, engine="openpyxl") as writer:
        for name, df in tables.items():
            df.to_excel(writer, sheet_name=name, index=False)

    # Turn each sheet's data range into a named Excel table.
    wb = load_workbook(TARGET)
    for name, df in tables.items():
        ws = wb[name]
        ref = f"A1:{ws.cell(row=len(df) + 1, column=df.shape[1]).coordinate}"
        table = Table(displayName=name, ref=ref)
        table.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)
        ws.add_table(table)
        ws.freeze_panes = "A2"
    wb.save(TARGET)


def main() -> None:
    tables = build_tables()
    write_workbook(tables)
    print(f"Saved {TARGET}")
    for name, df in tables.items():
        print(f"  {name:<19} {len(df):>6,} rows  {df.shape[1]:>2} columns")


if __name__ == "__main__":
    main()
