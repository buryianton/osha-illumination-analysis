r"""
illumination_by_sector.py

Joins OSHA INSPECTION and VIOLATION datasets to estimate how many
illumination-related violations occur in different industries, with
a focus on office/desk-based, education, and healthcare workplaces.

Steps:
1. Load ALL inspection files (osha_inspection*.csv) but keep only:
       activity_nr, sic_code, naics_code
2. Load ALL violation files (osha_violation*.csv).
3. Filter violations to illumination-related standards:
       1926.56, 1926.26, 1910.37 (encoded as prefixes)
4. Join violations -> inspections on activity_nr.
5. Map NAICS to sectors and summarize counts.
6. Save:
       illumination_by_sector.csv
       illumination_office_edu_health.csv
"""

import pandas as pd
from pathlib import Path
import glob

# ---------- CONFIG ----------
INSPECTION_PATTERN = "osha_inspection5.csv"
VIOLATION_PATTERN = "osha_violation13.csv"

ILLUM_PREFIXES = [
    "19260056",  # 1926.56 Illumination (construction)
    "19260026",  # 1926.26 Illumination / lighting
    "19100037",  # 1910.37 Exit routes (lighting included)
]
# ----------------------------


def load_inspections(base_path: Path) -> pd.DataFrame:
    paths = sorted(base_path.glob(INSPECTION_PATTERN))
    if not paths:
        raise FileNotFoundError(f"No inspection files matching {INSPECTION_PATTERN}")

    dfs = []
    for p in paths:
        print(f"[INFO] Loading inspections from {p.name}")
        df = pd.read_csv(p, dtype=str, low_memory=False)
        # keep only columns we need; adjust names if slightly different in your files
        keep_cols = [c for c in df.columns if c in ["activity_nr", "sic_code", "naics_code"]]
        df = df[keep_cols].copy()
        dfs.append(df)

    insps = pd.concat(dfs, ignore_index=True).drop_duplicates(subset=["activity_nr"])
    print(f"[INFO] Inspections loaded: {len(insps):,} unique activity_nr")
    return insps


def load_illum_violations(base_path: Path) -> pd.DataFrame:
    paths = sorted(base_path.glob(VIOLATION_PATTERN))
    if not paths:
        raise FileNotFoundError(f"No violation files matching {VIOLATION_PATTERN}")

    dfs = []
    for p in paths:
        print(f"[INFO] Loading violations from {p.name}")
        df = pd.read_csv(p, dtype=str, low_memory=False)
        dfs.append(df)

    viol = pd.concat(dfs, ignore_index=True)
    print(f"[INFO] Total violations loaded: {len(viol):,}")

    # Filter to illumination standards by prefix
    mask = False
    for pref in ILLUM_PREFIXES:
        print(f"[INFO] Matching standard prefix: {pref}")
        if isinstance(mask, bool):
            mask = viol["standard"].str.startswith(pref, na=False)
        else:
            mask = mask | viol["standard"].str.startswith(pref, na=False)

    illum = viol[mask].copy()
    print(f"[INFO] Illumination-related violations: {len(illum):,}")

    # keep activity_nr, standard, issuance_date, initial_penalty for later use
    keep_cols = [c for c in illum.columns if c in
                 ["activity_nr", "standard", "issuance_date", "initial_penalty"]]
    illum = illum[keep_cols].copy()
    return illum


def classify_sector(naics_code: str) -> str:
    """
    Map NAICS (2-digit) to coarse sectors.
    Focus on office/desk-based, education, and healthcare.
    """
    if not isinstance(naics_code, str) or naics_code.strip() == "":
        return "Unknown"

    # Take first 2 digits
    two = naics_code[:2]
    try:
        two_int = int(two)
    except ValueError:
        return "Unknown"

    if 51 <= two_int <= 56:
        return "Office / Professional / Admin"
    if two_int == 61:
        return "Education"
    if two_int == 62:
        return "Health care & social assistance"
    if 31 <= two_int <= 33:
        return "Manufacturing"
    if two_int == 23:
        return "Construction"
    if 44 <= two_int <= 45:
        return "Retail trade"
    if two_int == 92:
        return "Public administration"
    if 48 <= two_int <= 49:
        return "Transportation & warehousing"

    return "Other sectors"


def main():
    base_path = Path.cwd()
    print(f"[INFO] Working in: {base_path}")

    # 1) Load inspections (for NAICS)
    insps = load_inspections(base_path)

    # 2) Load illumination-related violations
    illum = load_illum_violations(base_path)

    # 3) Join violations -> inspections on activity_nr
    if "activity_nr" not in illum.columns or "activity_nr" not in insps.columns:
        raise KeyError("Missing 'activity_nr' in inspections or violations.")

    merged = illum.merge(insps, on="activity_nr", how="left")
    print(f"[INFO] Illum + inspection merged rows: {len(merged):,}")

    # 4) Add sector classification
    merged["sector"] = merged["naics_code"].apply(classify_sector)

    # 5) Summarize by sector
    sector_stats = merged.groupby("sector", as_index=False).agg(
        n_violations=("standard", "count")
    ).sort_values("n_violations", ascending=False)

    # 6) Focused subset: office/edu/health
    focus_sectors = [
        "Office / Professional / Admin",
        "Education",
        "Health care & social assistance",
    ]
    focus = merged[merged["sector"].isin(focus_sectors)].copy()

    focus_stats = focus.groupby("sector", as_index=False).agg(
        n_violations=("standard", "count")
    ).sort_values("n_violations", ascending=False)

    # 7) Save outputs
    out1 = base_path / "illumination_by_sector.csv"
    out2 = base_path / "illumination_office_edu_health.csv"
    merged.to_csv(out1, index=False)
    focus_stats.to_csv(out2, index=False)

    print(f"[INFO] Saved full sector breakdown to {out1}")
    print(f"[INFO] Saved office/education/health summary to {out2}")

    print("\n[PREVIEW] All sectors:")
    print(sector_stats)

    print("\n[PREVIEW] Office / Education / Health sectors:")
    print(focus_stats)


if __name__ == "__main__":
    main()
