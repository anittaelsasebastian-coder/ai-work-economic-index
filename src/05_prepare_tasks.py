"""
Step 4 — Build one clean table: one row per platform x task.

Reads the two raw AEI files (global rows only) and writes
data/processed/task_metrics.csv with usage, success, collaboration and time.
"""

from pathlib import Path

import pandas as pd

RAW = Path("data/raw")
OUT = Path("data/processed")

FILES = {
    "claude_ai": RAW / "aei_raw_claude_ai_2025-11-13_to_2025-11-20.csv",
    "api": RAW / "aei_raw_1p_api_2025-11-13_to_2025-11-20.csv",
}

AUTOMATION = ["directive", "feedback loop"]
AUGMENTATION = ["task iteration", "learning", "validation"]

# Placeholder "tasks": conversations that matched no O*NET task, or could not be classified.
NOT_A_TASK = {"none", "not_classified"}


def load_global(path: Path, platform: str) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    df = df[df["geography"] == "global"].copy()
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df["platform"] = platform
    return df


def split_task(rows: pd.DataFrame) -> pd.DataFrame:
    """'task text::category' -> columns task, category (split on the LAST '::')."""
    parts = rows["cluster_name"].str.rsplit("::", n=1, expand=True)
    rows = rows.assign(task=parts[0].str.strip(), category=parts[1].str.strip())
    return rows


def counts_by_category(df: pd.DataFrame, facet: str, prefix: str) -> pd.DataFrame:
    rows = df[(df["facet"] == facet) & df["variable"].str.endswith("_count")]
    rows = split_task(rows)
    wide = rows.pivot_table(index=["platform", "task"], columns="category",
                            values="value", aggfunc="sum", fill_value=0)
    wide.columns = [f"{prefix}_{c.replace(' ', '_')}" for c in wide.columns]
    return wide


def task_mean(df: pd.DataFrame, facet: str, name: str) -> pd.Series:
    rows = df[(df["facet"] == facet) & df["variable"].str.endswith("_mean")].copy()
    rows["task"] = rows["cluster_name"].str.split("::").str[0].str.strip()
    return rows.groupby(["platform", "task"])["value"].mean().rename(name)


def build(df: pd.DataFrame) -> pd.DataFrame:
    usage = df[(df["facet"] == "onet_task") & (df["variable"] == "onet_task_count")]
    usage = usage.assign(task=usage["cluster_name"].str.strip())
    table = usage.groupby(["platform", "task"])["value"].sum().rename("n").to_frame()

    table = table.join(counts_by_category(df, "onet_task::task_success", "success"))
    table = table.join(counts_by_category(df, "onet_task::collaboration", "collab"))
    table = table.join(task_mean(df, "onet_task::human_only_time", "human_only_time"))
    table = table.join(task_mean(df, "onet_task::human_with_ai_time", "human_with_ai_time"))
    table = table.join(task_mean(df, "onet_task::ai_autonomy", "ai_autonomy"))
    table = table.fillna({c: 0 for c in table.columns if c.startswith(("success_", "collab_"))})
    return table.reset_index()


def add_metrics(t: pd.DataFrame) -> pd.DataFrame:
    # Flag placeholders; they stay in the denominator (all records) but are never ranked.
    t["is_real_task"] = ~t["task"].isin(NOT_A_TASK)

    # Usage share = share of ALL records on the platform, as Anthropic reports it.
    t["usage_share"] = t["n"] / t.groupby("platform")["n"].transform("sum")

    # Success rate: yes / (yes + no). not_classified is excluded from the denominator.
    assessed = t["success_yes"] + t["success_no"]
    t["success_assessed"] = assessed
    t["success_rate"] = t["success_yes"] / assessed.where(assessed > 0)

    # Collaboration: shares of classified modes only (not_classified and none excluded).
    auto = sum(t.get(f"collab_{m.replace(' ', '_')}", 0) for m in AUTOMATION)
    aug = sum(t.get(f"collab_{m.replace(' ', '_')}", 0) for m in AUGMENTATION)
    classified = auto + aug
    t["automation_share"] = auto / classified.where(classified > 0)
    t["augmentation_share"] = aug / classified.where(classified > 0)

        # Units differ: human_only_time is in HOURS, human_with_ai_time is in MINUTES
    # (global means 3.09 h vs 15.35 min on Claude.ai), so convert hours to minutes first.
    t["speedup"] = (t["human_only_time"] * 60) / t["human_with_ai_time"].where(t["human_with_ai_time"] > 0)
    return t


def checks(t: pd.DataFrame) -> None:
    print("\nChecks per platform:")
    for platform, g in t.groupby("platform"):
        real = g[g["is_real_task"]]
        top10 = real.nlargest(10, "n")["usage_share"].sum()
        placeholders = g.loc[~g["is_real_task"], "usage_share"].sum()
        print(f"  {platform:<10} real_tasks={len(real):>5,}  records={g['n'].sum():>10,.0f}  "
              f"share_sum={g['usage_share'].sum():.3f}  none+not_classified={placeholders:.1%}  "
              f"top10_share={top10:.1%}  real_tasks_n>=100={(real['n'] >= 100).sum():,}")
    print("\nTop 5 real tasks on Claude.ai:")
    top = t[(t["platform"] == "claude_ai") & t["is_real_task"]].nlargest(5, "n")
    print(top[["task", "n", "usage_share", "success_rate", "automation_share"]].to_string(index=False))


def main() -> None:
    raw = pd.concat([load_global(p, name) for name, p in FILES.items()], ignore_index=True)
    print(f"Global rows loaded: {len(raw):,}")

    tasks = add_metrics(build(raw))
    checks(tasks)

    OUT.mkdir(parents=True, exist_ok=True)
    tasks.to_csv(OUT / "task_metrics.csv", index=False)
    print(f"\nSaved {OUT / 'task_metrics.csv'} ({len(tasks):,} rows, {tasks.shape[1]} columns)")


if __name__ == "__main__":
    main()