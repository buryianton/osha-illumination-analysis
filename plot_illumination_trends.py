"""
plot_illumination_trends.py

Reads OSHA illumination statistics from:
    illumination_stats_by_year_merged.csv

and produces two figures:
1) OSHA Illumination-Related Violations per Year
2) Total OSHA Penalties for Lighting Violations per Year

Usage (from the same folder as the CSV):
    python plot_illumination_trends.py
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


# ========== CONFIG ==========
STATS_FILE = "illumination_stats_by_year_merged.csv"
FIG1_NAME = "OSHA_illumination_related_violations_per_year.png"
FIG2_NAME = "Total_OSHA_penalties_for_lighting_violations_per_year.png"

# Optional: restrict to a range of years (set to None to use all)
YEAR_MIN = None   # e.g. 1972
YEAR_MAX = None   # e.g. 2025
# ============================


def load_stats(base_path: Path) -> pd.DataFrame:
    path = base_path / STATS_FILE
    print(f"[INFO] Loading stats from {path}")
    df = pd.read_csv(path)

    # Expect columns: year, n_violations, total_penalty
    required_cols = {"year", "n_violations", "total_penalty"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in CSV: {missing}")

    # Sort and filter by year
    df = df.sort_values("year")
    if YEAR_MIN is not None:
        df = df[df["year"] >= YEAR_MIN]
    if YEAR_MAX is not None:
        df = df[df["year"] <= YEAR_MAX]

    print(f"[INFO] Loaded {len(df)} rows, years {df['year'].min()}–{df['year'].max()}")
    return df


def plot_violations(df: pd.DataFrame, base_path: Path) -> None:
    plt.figure(figsize=(12, 6))
    plt.plot(df["year"], df["n_violations"], marker="o", linestyle="-", color="orange")
    plt.title("OSHA Illumination-Related Violations per Year", fontsize=18)
    plt.xlabel("Year", fontsize=14)
    plt.ylabel("Number of Violations", fontsize=14)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()

    out_path = base_path / FIG1_NAME
    plt.savefig(out_path, dpi=300)
    print(f"[INFO] Saved figure: {out_path}")


def plot_penalties(df: pd.DataFrame, base_path: Path) -> None:
    plt.figure(figsize=(12, 6))
    plt.plot(df["year"], df["total_penalty"], marker="o", linestyle="-", color="orange")
    plt.title("Total OSHA Penalties for Lighting Violations per Year", fontsize=18)
    plt.xlabel("Year", fontsize=14)
    plt.ylabel("Total Penalty (USD)", fontsize=14)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()

    out_path = base_path / FIG2_NAME
    plt.savefig(out_path, dpi=300)
    print(f"[INFO] Saved figure: {out_path}")


def main():
    base_path = Path.cwd()
    df = load_stats(base_path)
    plot_violations(df, base_path)
    plot_penalties(df, base_path)
    print("[INFO] Done.")


if __name__ == "__main__":
    main()
