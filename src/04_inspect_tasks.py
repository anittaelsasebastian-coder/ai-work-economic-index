"""Step 3 — Show what the task-level rows look like."""

import pandas as pd

df = pd.read_csv("data/raw/aei_raw_claude_ai_2025-11-13_to_2025-11-20.csv",
                 dtype=str, keep_default_na=False)
df = df[df["geography"] == "global"]

for facet in ["onet_task", "onet_task::task_success", "onet_task::collaboration"]:
    rows = df[df["facet"] == facet]
    print(f"\n===== {facet} =====")
    print("Example rows:")
    print(rows[["variable", "cluster_name", "value"]].head(6).to_string(index=False))

    if "::" in facet:
        categories = rows["cluster_name"].str.split("::").str[-1].value_counts()
        print("\nCategories after the last '::':")
        print(categories.to_string())