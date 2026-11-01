"""
Step 6 — Join each AEI task to its O*NET occupation and SOC groups.

Inputs:  data/processed/task_metrics.csv (from step 4)
         data/raw/onet_task_statements.csv, data/raw/SOC_Structure.csv
Outputs: data/processed/task_occupation.csv  one row per platform x task x occupation
         data/processed/occupation.csv       one row per occupation (dimension table)
         data/processed/unmatched_tasks.csv  AEI tasks with no O*NET match
"""

from pathlib import Path

import pandas as pd

RAW = Path("data/raw")
PROC = Path("data/processed")


def normalise(text: pd.Series) -> pd.Series:
    """Lowercase, collapse spaces, drop trailing punctuation, so the same task matches."""
    return (text.fillna("").str.lower()
                .str.replace(r"\s+", " ", regex=True)
                .str.strip()
                .str.rstrip(".;: "))


def load_onet() -> pd.DataFrame:
    onet = pd.read_csv(RAW / "onet_task_statements.csv", dtype=str, keep_default_na=False)
    onet = onet.rename(columns={"O*NET-SOC Code": "onet_soc_code", "Title": "occupation",
                                "Task Type": "task_type"})
    onet["task_key"] = normalise(onet["Task"])
    onet["task_type"] = onet["task_type"].replace("", "Unknown")
    onet["soc_detailed"] = onet["onet_soc_code"].str[:7]           # 11-1011.03 -> 11-1011

    # Same task listed twice for one occupation would double count: keep one.
    onet = onet.drop_duplicates(["task_key", "onet_soc_code"])
    return onet[["task_key", "onet_soc_code", "occupation", "task_type", "soc_detailed"]]


def load_soc_hierarchy() -> pd.DataFrame:
    """Walk SOC_Structure top to bottom: each detailed occupation belongs to the
    most recent minor and major group above it. Minor-group codes do not follow one
    pattern (e.g. 15-1200, 11-9000), so they are read from the file, never derived."""
    soc = pd.read_csv(RAW / "SOC_Structure.csv", dtype=str, keep_default_na=False)
    title_col = soc.columns[-1]
    major = minor = None
    rows = []
    for _, r in soc.iterrows():
        if r["Major Group"]:
            major = (r["Major Group"], r[title_col])
        elif r["Minor Group"]:
            minor = (r["Minor Group"], r[title_col])
        elif r["Detailed Occupation"]:
            rows.append({"soc_detailed": r["Detailed Occupation"],
                         "soc_minor": minor[0] if minor else None,
                         "minor_group": minor[1] if minor else None,
                         "soc_major": major[0] if major else None,
                         "major_group": major[1] if major else None})
    return pd.DataFrame(rows).drop_duplicates("soc_detailed")


def load_major_titles() -> dict:
    soc = pd.read_csv(RAW / "SOC_Structure.csv", dtype=str, keep_default_na=False)
    major = soc[soc["Major Group"] != ""]
    return dict(zip(major["Major Group"], major[soc.columns[-1]]))


def main() -> None:
    tasks = pd.read_csv(PROC / "task_metrics.csv")
    tasks = tasks[tasks["is_real_task"]].copy()
    tasks["task_key"] = normalise(tasks["task"])
    print(f"Real tasks to match: {len(tasks):,} rows (both platforms)")

    onet = load_onet()

    # How many occupations share each task statement (k_t), for the equal split.
    k = onet.groupby("task_key")["onet_soc_code"].nunique().rename("k_occupations")
    onet = onet.join(k, on="task_key")

    joined = tasks.merge(onet, on="task_key", how="left", indicator=True)
    matched = joined[joined["_merge"] == "both"].drop(columns="_merge").copy()
    unmatched = joined.loc[joined["_merge"] == "left_only", ["platform", "task", "n"]]

    # Equal split: n_alloc = n / k, so usage is never counted twice.
    matched["n_alloc"] = matched["n"] / matched["k_occupations"]

    hierarchy = load_soc_hierarchy().drop(columns=["soc_major", "major_group"])
    matched = matched.merge(hierarchy, on="soc_detailed", how="left")

    # The O*NET task file mixes SOC 2010 and SOC 2019 codes; SOC_Structure has 2019 only.
    # Major groups are the same in both versions (first two digits), so derive them from
    # the code. Minor groups changed between versions, so 2010 codes are labelled, not guessed.
    matched["soc_version"] = matched["soc_minor"].notna().map({True: "2019", False: "2010"})
    matched["soc_major"] = matched["onet_soc_code"].str[:2] + "-0000"
    matched["major_group"] = matched["soc_major"].map(load_major_titles())
    matched["minor_group"] = matched["minor_group"].fillna("Not mapped (SOC 2010 code)")

    # ---- Checks ----
    print("\nMatch rates (real tasks only):")
    for platform, g in tasks.groupby("platform"):
        m = matched[matched["platform"] == platform]
        task_rate = m["task"].nunique() / g["task"].nunique()
        usage_rate = m.drop_duplicates("task")["n"].sum() / g["n"].sum()
        print(f"  {platform:<10} tasks matched={task_rate:.1%}  usage matched={usage_rate:.1%}")

    for platform, m in matched.groupby("platform"):
        before = m.drop_duplicates("task")["n"].sum()
        after = m["n_alloc"].sum()
        status = "OK" if abs(before - after) < 1e-6 * max(before, 1) else "MISMATCH"
        print(f"  {platform:<10} split check: {before:,.0f} before vs {after:,.0f} after -> {status}")

    no_major = matched["major_group"].isna().sum()
    print(f"\nRows without a major group title: {no_major}")
    for platform, m in matched.groupby("platform"):
        old_share = m.loc[m["soc_version"] == "2010", "n_alloc"].sum() / m["n_alloc"].sum()
        print(f"  {platform:<10} usage on SOC 2010 codes (no minor group): {old_share:.1%}")
    print("\nUsage by major group (Claude.ai, top 5):")
    top = (matched[matched["platform"] == "claude_ai"]
           .groupby("major_group")["n_alloc"].sum().sort_values(ascending=False))
    print((top / top.sum()).head(5).map("{:.1%}".format).to_string())

    # ---- Save ----
    occupation = (matched[["onet_soc_code", "occupation", "soc_version", "soc_detailed",
                           "soc_minor", "minor_group", "soc_major", "major_group"]]
                  .drop_duplicates("onet_soc_code").sort_values("onet_soc_code"))
    matched.drop(columns="task_key").to_csv(PROC / "task_occupation.csv", index=False)
    occupation.to_csv(PROC / "occupation.csv", index=False)
    unmatched.sort_values("n", ascending=False).to_csv(PROC / "unmatched_tasks.csv", index=False)
    print(f"\nSaved task_occupation.csv ({len(matched):,} rows), occupation.csv "
          f"({len(occupation):,} rows), unmatched_tasks.csv ({len(unmatched):,} rows)")


if __name__ == "__main__":
    main()