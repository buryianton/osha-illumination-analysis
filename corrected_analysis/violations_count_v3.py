"""
OSHA illumination-related violations, 1972-2024 — corrected v3 analysis.

Fixes relative to violations_count_corrected.py:
  1. 1910.37(b) is no longer counted wholesale. Post-recodification (67 FR 67950,
     effective 2002-12-09), only (b)(1) exit-route lighting and (b)(6) exit-sign
     illumination are lighting provisions; (b)(2), (b)(4), (b)(5), (b)(7) are
     exit-sign MARKING provisions and are excluded.
  2. Era-specific codes: before 2003 exit-route lighting was old 1910.36(b)(6)
     and exit-sign illumination old 1910.37(q)(6)-(q)(7).
  3. Maritime regexes fixed: the old script matched "1915082"/"1917123"/"1918092",
     which never occur — actual clean codes are 8-digit ("19150082", "19170123",
     "19180092"), so maritime standards previously contributed ZERO records.
  4. Analysis window enforced: 1972 <= issuance year <= 2024.
  5. Added 1926.26 (construction lighting, general) alongside 1926.56.
  6. Lag citations counted: old-numbering codes (1910.36(b)(6), 1910.37(q)(6)-(q)(7))
     are counted in ALL years, because those code strings are unambiguous and OSHA
     kept citing them through ~2006 (459 records in 2003+) while inspections opened
     under the pre-recodification rule were closed out. New-numbering codes
     (1910.37(b)(1), (b)(6)) are counted only from 2003, because identical code
     strings before 2003 refer to the OLD 1910.37(b) "Fundamental requirements",
     which is not a lighting provision.

Memory-safe: raw files are read one at a time in 1M-row chunks; only candidate
rows are retained. Code cleaning matches the original script: uppercase, strip
all non-alphanumeric characters.

Outputs (written next to this script):
  illumination_records_v3.csv  record-level subset with category, year, penalty
  table1_v3.csv                counts + penalty stats by standard and category
  annual_v3.csv                annual counts and shares (all / strict)
  figure1_v3.png               annual counts by category, 300 dpi
  figure2_v3.png               annual share of all OSHA violations, 300 dpi
"""

import glob
import os
import re
from collections import Counter

import matplotlib.pyplot as plt
import pandas as pd

# =========================================================
# SETTINGS
# =========================================================
base_dir = r"C:\Users\buryy\MyProjects\Lux_estimation"
out_dir = os.path.dirname(os.path.abspath(__file__))

YEAR_MIN, YEAR_MAX = 1972, 2024
ERA_SPLIT = 2003  # first year of the recodified Subpart E numbering

# Candidate clean-code prefixes (broad, filtered early for memory safety;
# 19100036/19100037 are kept broadly so era diagnostics can be printed).
CANDIDATE_PREFIXES = (
    "19100036", "19100037",              # exit routes, both eras
    "19260056", "19260026",              # construction
    "19150082", "19170123", "19180092",  # maritime
)

# (prefix, era, standard label, category)
# era: "all"  = counted in every year (old-numbering codes are unambiguous, so
#               post-2002 lag citations of them are included);
#      "post" = counted only when year >= 2003 (the same code string pre-2003
#               refers to the old, non-lighting 1910.37(b)).
CLASSIFICATION = [
    ("19100036B06", "all",  "29 CFR 1910.36(b)(6) [old numbering]", "exit route lighting"),
    ("19100037Q06", "all",  "29 CFR 1910.37(q)(6) [old numbering]", "exit sign illumination"),
    ("19100037Q07", "all",  "29 CFR 1910.37(q)(7) [old numbering]", "exit sign illumination"),
    ("19100037B01", "post", "29 CFR 1910.37(b)(1) [2003-]",         "exit route lighting"),
    ("19100037B06", "post", "29 CFR 1910.37(b)(6) [2003-]",         "exit sign illumination"),
    ("19260056",    "all",  "29 CFR 1926.56",                   "construction illumination"),
    ("19260026",    "all",  "29 CFR 1926.26",                   "construction illumination"),
    ("19150082",    "all",  "29 CFR 1915.82",                   "maritime lighting"),
    ("19170123",    "all",  "29 CFR 1917.123",                  "maritime lighting"),
    ("19180092",    "all",  "29 CFR 1918.92",                   "maritime lighting"),
]

STRICT_CATEGORIES = {"exit route lighting", "construction illumination", "maritime lighting"}

# =========================================================
# 1. FIND RAW FILES (osha_violation0.csv ... osha_violation13.csv only)
# =========================================================
files = [
    f for f in sorted(glob.glob(os.path.join(base_dir, "osha_violation*.csv")))
    if re.fullmatch(r"osha_violation\d+\.csv", os.path.basename(f))
]
print("Files to load:")
for f in files:
    print(" -", os.path.basename(f))
if not files:
    raise FileNotFoundError("No raw OSHA violation files found (osha_violation<N>.csv).")

# =========================================================
# 2. SINGLE PASS: annual totals (denominator) + candidate subset
# =========================================================
usecols = ["activity_nr", "standard", "issuance_date", "initial_penalty", "current_penalty"]
annual_totals = Counter()   # ALL OSHA violation records per issuance year
kept_chunks = []
total_rows = 0

for f in files:
    print("Loading:", os.path.basename(f), flush=True)
    for chunk in pd.read_csv(f, usecols=usecols, dtype=str, chunksize=1_000_000):
        total_rows += len(chunk)
        year = pd.to_numeric(chunk["issuance_date"].str.slice(0, 4), errors="coerce")
        chunk["year"] = year
        annual_totals.update(year.dropna().astype(int).value_counts().to_dict())
        clean = (
            chunk["standard"].astype(str)
            .str.upper()
            .str.replace(r"[^A-Z0-9]", "", regex=True)
            .str.strip()
        )
        chunk["standard_clean"] = clean
        mask = clean.str.startswith(CANDIDATE_PREFIXES, na=False)
        if mask.any():
            kept_chunks.append(chunk.loc[mask])

cand = pd.concat(kept_chunks, ignore_index=True)
del kept_chunks
cand = cand.dropna(subset=["year"])
cand["year"] = cand["year"].astype(int)
print(f"\nTotal rows scanned: {total_rows:,}")
print(f"Candidate rows retained: {len(cand):,}")

# =========================================================
# 3. DIAGNOSTICS: verify the era mapping before classifying
# =========================================================
pre = cand[cand["year"] <= ERA_SPLIT - 1]
print("\n" + "=" * 75)
print("DIAGNOSTIC: top 15 pre-2003 codes under 1910.36 and 1910.37")
print("=" * 75)
print("\n19100036* (pre-2003):")
print(pre.loc[pre["standard_clean"].str.startswith("19100036"), "standard_clean"]
      .value_counts().head(15).to_string())
print("\n19100037* (pre-2003):")
print(pre.loc[pre["standard_clean"].str.startswith("19100037"), "standard_clean"]
      .value_counts().head(15).to_string())

print("\nDIAGNOSTIC: annual counts of key era codes (all years, unfiltered):")
for pref, label in [
    ("19100036B06", "old 1910.36(b)(6) exit route lighting"),
    ("19100037Q06", "old 1910.37(q)(6) exit sign illumination"),
    ("19100037Q07", "old 1910.37(q)(7) exit sign illumination"),
    ("19100037B01", "new 1910.37(b)(1) exit route lighting"),
    ("19100037B06", "new 1910.37(b)(6) exit sign illumination"),
]:
    sub = cand[cand["standard_clean"].str.startswith(pref)]
    yrs = sub.groupby("year").size()
    print(f"\n  {pref} — {label}: total {len(sub)}")
    print("   " + yrs.to_string().replace("\n", "\n   "))

# =========================================================
# 4. CLASSIFY TRUE ILLUMINATION VIOLATIONS (era-specific)
# =========================================================
def classify(code: str, year: int):
    """Return (standard_label, category) or None."""
    for pref, era, label, category in CLASSIFICATION:
        if code.startswith(pref):
            if era == "post" and year < ERA_SPLIT:
                continue
            return label, category
    return None

res = [classify(c, y) for c, y in zip(cand["standard_clean"], cand["year"])]
cand["standard_label"] = [r[0] if r else None for r in res]
cand["category"] = [r[1] if r else None for r in res]

illum = cand[cand["category"].notna()].copy()

# Era-bleed accounting (transparency: lag citations INCLUDED, old-1910.37(b) EXCLUDED)
old_prefixes = ("19100036B06", "19100037Q06", "19100037Q07")
new_prefixes = ("19100037B01", "19100037B06")
lag_old_after = cand[(cand["standard_clean"].str.startswith(old_prefixes))
                     & (cand["year"] >= ERA_SPLIT)]
excl_new_before = cand[(cand["standard_clean"].str.startswith(new_prefixes))
                       & (cand["year"] < ERA_SPLIT)]
print("\n" + "=" * 75)
print("ERA-BLEED CHECK:")
print(f"  lag citations of old-numbering codes in {ERA_SPLIT}+ (INCLUDED — code "
      f"strings unambiguous): {len(lag_old_after)} "
      f"(by year: {dict(lag_old_after.groupby('year').size())})")
print(f"  new-style code strings before {ERA_SPLIT} (EXCLUDED — refer to old, "
      f"non-lighting 1910.37(b)): {len(excl_new_before)}")

# =========================================================
# 5. FILTER TO ANALYSIS WINDOW 1972-2024
# =========================================================
illum = illum[(illum["year"] >= YEAR_MIN) & (illum["year"] <= YEAR_MAX)].copy()
illum["initial_penalty"] = pd.to_numeric(illum["initial_penalty"], errors="coerce").fillna(0.0)
illum["current_penalty"] = pd.to_numeric(illum["current_penalty"], errors="coerce").fillna(0.0)
illum["strict"] = illum["category"].isin(STRICT_CATEGORIES)

records_csv = os.path.join(out_dir, "illumination_records_v3.csv")
illum_out = illum[["activity_nr", "standard", "standard_clean", "standard_label",
                   "category", "strict", "year", "issuance_date",
                   "initial_penalty", "current_penalty"]]
illum_out.to_csv(records_csv, index=False)

# =========================================================
# 6. TABLE 1: by standard and by category
# =========================================================
def penalty_stats(g):
    return pd.Series({
        "violations": len(g),
        "median_initial_penalty": g["initial_penalty"].median(),
        "total_initial_penalty": g["initial_penalty"].sum(),
        "pct_zero_penalty": 100.0 * (g["initial_penalty"] == 0).mean(),
    })

by_standard = (illum.groupby(["category", "standard_label"])
               .apply(penalty_stats, include_groups=False).reset_index())
by_standard.insert(0, "level", "standard")

by_category = (illum.groupby("category")
               .apply(penalty_stats, include_groups=False).reset_index())
by_category.insert(0, "level", "category")
by_category["standard_label"] = "(all standards in category)"

table1 = pd.concat([by_standard, by_category], ignore_index=True)
table1["violations"] = table1["violations"].astype(int)
table1 = table1[["level", "category", "standard_label", "violations",
                 "median_initial_penalty", "total_initial_penalty", "pct_zero_penalty"]]
table1_csv = os.path.join(out_dir, "table1_v3.csv")
table1.to_csv(table1_csv, index=False)

print("\n" + "=" * 75)
print("TABLE 1 (v3): illumination violations by standard and category, "
      f"{YEAR_MIN}-{YEAR_MAX}")
print("=" * 75)
print(table1.to_string(index=False,
                       formatters={"median_initial_penalty": "{:,.0f}".format,
                                   "total_initial_penalty": "{:,.0f}".format,
                                   "pct_zero_penalty": "{:.1f}".format}))
print("Note: blank penalties treated as $0; pct_zero_penalty includes them.")

# =========================================================
# 7. ANNUAL SERIES
# =========================================================
tot = (pd.Series(annual_totals).rename_axis("year").rename("total_violations")
       .sort_index())
tot = tot[(tot.index >= YEAR_MIN) & (tot.index <= YEAR_MAX)]

annual = tot.to_frame()
annual["illum_all"] = illum.groupby("year").size()
annual["illum_strict"] = illum[illum["strict"]].groupby("year").size()
annual = annual.fillna(0)
annual[["illum_all", "illum_strict"]] = annual[["illum_all", "illum_strict"]].astype(int)
annual["share_all_pct"] = 100 * annual["illum_all"] / annual["total_violations"]
annual["share_strict_pct"] = 100 * annual["illum_strict"] / annual["total_violations"]
annual = annual.reset_index()
annual_csv = os.path.join(out_dir, "annual_v3.csv")
annual.to_csv(annual_csv, index=False)

# =========================================================
# 8. SANITY CHECK: continuity of the series across the 2003 era split
# =========================================================
exit_cats = illum[illum["category"].isin(["exit route lighting", "exit sign illumination"])]
piv = (exit_cats.groupby(["year", "category"]).size().unstack(fill_value=0)
       .reindex(range(YEAR_MIN, YEAR_MAX + 1), fill_value=0))
window = piv.loc[1997:2009]
print("\n" + "=" * 75)
print("SANITY CHECK: exit-route / exit-sign series around the 2003 recodification")
print("=" * 75)
print(window.to_string())
pre_mean = piv.loc[1998:2002].mean()
post_mean = piv.loc[2003:2007].mean()
print("\nMean annual counts 1998-2002 vs 2003-2007:")
for cat in piv.columns:
    print(f"  {cat}: {pre_mean[cat]:.0f} -> {post_mean[cat]:.0f}")
print(f"({len(lag_old_after)} lag citations of old-numbering codes in {ERA_SPLIT}+ "
      f"are INCLUDED, concentrated in 2003-2005 — see era-bleed check above.)")

# =========================================================
# 9. FIGURES (300 dpi, plain-text legend labels)
# =========================================================
plt.rcParams.update({
    "font.size": 11, "axes.titlesize": 13, "axes.labelsize": 12,
    "figure.dpi": 300, "savefig.dpi": 300,
})

CAT_LABELS = {
    "exit route lighting":
        "Exit route lighting - 29 CFR 1910.36(b)(6) old numbering / 1910.37(b)(1) 2003-",
    "exit sign illumination":
        "Exit sign illumination - 29 CFR 1910.37(q)(6)-(q)(7) old numbering / 1910.37(b)(6) 2003-",
    "construction illumination":
        "Construction illumination - 29 CFR 1926.56 and 1926.26",
    "maritime lighting":
        "Maritime lighting - 29 CFR 1915.82, 1917.123, 1918.92",
}
CAT_ORDER = ["exit route lighting", "exit sign illumination",
             "construction illumination", "maritime lighting"]

cat_annual = (illum.groupby(["year", "category"]).size().unstack(fill_value=0)
              .reindex(range(YEAR_MIN, YEAR_MAX + 1), fill_value=0)
              .reindex(columns=CAT_ORDER, fill_value=0))

fig1_path = os.path.join(out_dir, "figure1_v3.png")
plt.figure(figsize=(10, 5.5))
for cat in CAT_ORDER:
    plt.plot(cat_annual.index, cat_annual[cat], linewidth=1.8, label=CAT_LABELS[cat])
plt.title(f"Annual Counts of OSHA Illumination-Related Violations by Category, "
          f"{YEAR_MIN}-{YEAR_MAX}")
plt.xlabel("Year")
plt.ylabel("Number of violations")
plt.legend(fontsize=8, loc="upper right", frameon=False)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(fig1_path, bbox_inches="tight")
plt.close()

fig2_path = os.path.join(out_dir, "figure2_v3.png")
plt.figure(figsize=(10, 5.5))
plt.plot(annual["year"], annual["share_all_pct"], linewidth=2,
         label="All illumination-related provisions")
plt.plot(annual["year"], annual["share_strict_pct"], linewidth=2, linestyle="--",
         label="Strict subset (work-area and route lighting only)")
plt.title(f"Illumination-Related Violations as a Share of All OSHA Violations, "
          f"{YEAR_MIN}-{YEAR_MAX}")
plt.xlabel("Year")
plt.ylabel("Share of all OSHA violations (%)")
plt.legend(fontsize=9, frameon=False)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(fig2_path, bbox_inches="tight")
plt.close()

# =========================================================
# 10. SUMMARY
# =========================================================
n_all = len(illum)
n_strict = int(illum["strict"].sum())
n_years = YEAR_MAX - YEAR_MIN + 1
print("\n" + "=" * 75)
print(f"SUMMARY ({YEAR_MIN}-{YEAR_MAX})")
print("=" * 75)
print(f"Total illumination-related violations (all):    {n_all:,}")
print(f"Total illumination-related violations (strict): {n_strict:,}")
print(f"Average per year (all / strict):                {n_all / n_years:.1f} / {n_strict / n_years:.1f}")
print(f"Annual share of all OSHA violations (all):      "
      f"min {annual['share_all_pct'].min():.4f}% ({int(annual.loc[annual['share_all_pct'].idxmin(), 'year'])}), "
      f"max {annual['share_all_pct'].max():.4f}% ({int(annual.loc[annual['share_all_pct'].idxmax(), 'year'])})")
print(f"Annual share of all OSHA violations (strict):   "
      f"min {annual['share_strict_pct'].min():.4f}% ({int(annual.loc[annual['share_strict_pct'].idxmin(), 'year'])}), "
      f"max {annual['share_strict_pct'].max():.4f}% ({int(annual.loc[annual['share_strict_pct'].idxmax(), 'year'])})")
print(f"Median initial penalty (overall):               ${illum['initial_penalty'].median():,.0f}")
for cat in CAT_ORDER:
    med = illum.loc[illum["category"] == cat, "initial_penalty"].median()
    print(f"  - {cat}: ${med:,.0f}")
print(f"Total initial penalties:                        ${illum['initial_penalty'].sum():,.0f}")
print(f"Total current penalties:                        ${illum['current_penalty'].sum():,.0f}")
print(f"Records with $0 initial penalty:                "
      f"{100.0 * (illum['initial_penalty'] == 0).mean():.1f}%")

print("\nSaved files:")
for p in [records_csv, table1_csv, annual_csv, fig1_path, fig2_path]:
    print(" -", p)
print("\nDONE.")
