"""Step 2 — List the facets in each AEI file (global rows only)."""

import pandas as pd

files = {
    "Claude.ai": "data/raw/aei_raw_claude_ai_2025-11-13_to_2025-11-20.csv",
    "API": "data/raw/aei_raw_1p_api_2025-11-13_to_2025-11-20.csv",
}

for label, path in files.items():
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    df = df[df["geography"] == "global"]

    print(f"\n===== {label}: facets at global level =====")
    summary = (df.groupby("facet")
                 .agg(rows=("value", "size"),
                      variables=("variable", lambda v: ", ".join(sorted(v.unique())[:4])))
                 .sort_values("rows", ascending=False))
    print(summary.to_string())