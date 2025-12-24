r"""
violation_lighting_search.py

Search OSHA VIOLATIONS dataset for illumination / lighting-related violations
and summarize them. Tailored for files like "osha_violation1.csv",
"osha_violation2.csv", ..., "osha_violation13.csv".

Usage:
1. Put this file in the same folder as your OSHA violations CSVs.
   For example:
       C:\Users\buryy\MyProjects\Lux_estimation\
           - violation_lighting_search_v2.py
           - osha_violation1.csv
           - osha_violation2.csv
           - osha_violation3.csv
           - ...
2. Open this folder in Visual Studio / VS Code.
3. In the terminal, run:
       python violation_lighting_search_v2.py
4. Check the generated files:
       illumination_violations.csv
       illumination_stats_by_year.csv
"""

import pandas as pd
from pathlib import Path
import glob

# ========= CONFIGURATION =========
# Pattern for your violations CSV files.
# If your files are named osha_violation1.csv, osha_violation2.csv, etc.,
# this pattern will find them all:
VIOLATION_PATTERN = "osha_violation13.csv"

# Illumination-related standards (encoded as in OSHA data, no dots).
# 19260056 ≈ 29 CFR 1926.56  (Illumination)
# 19260026 ≈ 29 CFR 1926.26  (Illumination / lighting in construction)
# 19100037 ≈ 29 CFR 1910.37  (Exit routes, including lighting)
ILLUM_PREFIXES = [
    "19260056",
    "19260026",
    "19100037",
]
# =================================


def main():
    base_path = Path.cwd()
    print(f"[INFO] Working directory: {base_path}")

    # ---- Find and load all violations CSV files ----
    csv_paths = list(base_path.glob(VIOLATION_PATTERN))
    if not csv_paths:
        print(f"[ERROR] No CSV files found matching pattern: {VIOLATION_PATTERN}")
        print("       Check VIOLATION_PATTERN at the top of this script.")
        return

    print(f"[INFO] Found {len(csv_paths)} file(s):")
    for p in csv_paths:
        print("   -", p.name)

    df_list = []
    for p in csv_paths:
        print(f"[INFO] Loading: {p.name}")
        df_part = pd.read_csv(p, dtype=str, low_memory=False)
        df_list.append(df_part)

    df = pd.concat(df_list, ignore_index=True)
    print(f"[INFO] Combined violations rows: {len(df):,}")
    print("[INFO] Columns:", list(df.columns))

    # ---- Basic column names we expect ----
    # Using your example file, the key columns are:
    #   standard, initial_penalty, issuance_date
    if "standard" not in df.columns:
        print("[ERROR] No 'standard' column found. Cannot continue.")
        return

    penalty_col = "initial_penalty" if "initial_penalty" in df.columns else None
    date_col = "issuance_date" if "issuance_date" in df.columns else None

    print("\n[INFO] Using columns:")
    print("   standard column :", "standard")
    print("   penalty column  :", penalty_col)
    print("   date column     :", date_col)

    # ---- Filter for illumination-related standards by prefix ----
    print("\n[INFO] Filtering for illumination-related standards (prefixes):", ILLUM_PREFIXES)
    mask = False
    for pref in ILLUM_PREFIXES:
        print("   - matching prefix:", pref)
        if isinstance(mask, bool):
            mask = df["standard"].str.startswith(pref, na=False)
        else:
            mask = mask | df["standard"].str.startswith(pref, na=False)

    illum = df[mask].copy()
    print(f"[INFO] Found {len(illum):,} illumination / lighting related violations.")

    if illum.empty:
        print("[WARN] No rows matched the illumination prefixes. "
              "You may need to adjust ILLUM_PREFIXES for your dataset.")
        return

    # ---- Convert penalty and date, add year ----
    if penalty_col is not None and penalty_col in illum.columns:
        illum[penalty_col] = pd.to_numeric(illum[penalty_col], errors="coerce").fillna(0)
    else:
        print("[WARN] No 'initial_penalty' column — penalty stats will be zero.")
        illum[penalty_col] = 0

    if date_col is not None and date_col in illum.columns:
        illum[date_col] = pd.to_datetime(illum[date_col], errors="coerce")
        illum["year"] = illum[date_col].dt.year
    else:
        print("[WARN] No 'issuance_date' column — cannot compute year-by-year stats.")
        illum["year"] = None

    # ---- Save full illumination violations ----
    out_full = base_path / "illumination_violations.csv"
    illum.to_csv(out_full, index=False)
    print(f"\n[INFO] Saved illumination-related violations to: {out_full}")

    # ---- Summarize by year ----
    if "year" in illum.columns and illum["year"].notna().any():
        stats = illum.groupby("year", dropna=True).agg(
            n_violations=("standard", "count"),
            total_penalty=(penalty_col, "sum"),
        ).reset_index()

        out_stats = base_path / "illumination_stats_by_year.csv"
        stats.to_csv(out_stats, index=False)
        print(f"[INFO] Saved yearly statistics to: {out_stats}")
        print("\n[PREVIEW] Yearly statistics:")
        with pd.option_context("display.max_rows", 20):
            print(stats.head(20))
    else:
        print("[INFO] Could not compute yearly stats (no usable year information).")

    # ---- Show a small preview ----
    print("\n[PREVIEW] First 10 illumination-related violations:")
    with pd.option_context("display.max_columns", 20, "display.width", 200):
        print(illum.head(10))


if __name__ == "__main__":
    main()
