"""
Step 7 — Run the SQL queries in sql/ with DuckDB and save each result for Power BI.

Run from the project root:
    python src/07_run_sql.py                         # every query in sql/
    python src/07_run_sql.py q1_usage_by_task.sql    # one query

Each query's result is saved to data/outputs/<query name>.csv.
"""

import sys
from pathlib import Path

import duckdb
import pandas as pd

SQL_DIR = Path("sql")
OUT = Path("data/outputs")


def run(path: Path, con: duckdb.DuckDBPyConnection) -> None:
    result = con.sql(path.read_text()).df()
    OUT.mkdir(parents=True, exist_ok=True)
    target = OUT / f"{path.stem}.csv"
    result.to_csv(target, index=False)

    print(f"\n===== {path.name}: {len(result):,} rows -> {target} =====")
    with pd.option_context("display.max_colwidth", 60, "display.width", 200):
        print(result.head(12).to_string(index=False))


def main() -> None:
    names = sys.argv[1:]
    paths = [SQL_DIR / n for n in names] if names else sorted(SQL_DIR.glob("*.sql"))
    if not paths:
        raise SystemExit("No .sql files found in sql/")

    con = duckdb.connect()  # in-memory: queries read the CSV files directly
    for path in paths:
        run(path, con)


if __name__ == "__main__":
    main()