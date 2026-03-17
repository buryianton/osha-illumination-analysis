import pandas as pd
import matplotlib.pyplot as plt
import glob
import os
import re

# =========================================================
# SETTINGS
# =========================================================
base_dir = r"C:\Users\buryy\MyProjects\Lux_estimation"

# =========================================================
# 1. FIND ONLY RAW OSHA VIOLATION FILES
#    Keeps only:
#    osha_violation0.csv ... osha_violation13.csv
#    Ignores:
#    osha_violation_types_counts.csv
#    osha_violation_20251208.csv
# =========================================================
all_candidates = sorted(glob.glob(os.path.join(base_dir, "osha_violation*.csv")))

files = []
for f in all_candidates:
    name = os.path.basename(f)
    if re.fullmatch(r"osha_violation\d+\.csv", name):
        files.append(f)

print("Files to load:")
for f in files:
    print(" -", os.path.basename(f))

if len(files) == 0:
    raise FileNotFoundError(
        "No raw OSHA violation files found.\n"
        "Expected files like: osha_violation0.csv ... osha_violation13.csv"
    )

# =========================================================
# 2. LOAD FILES
# =========================================================
dfs = []
for f in files:
    print("Loading:", os.path.basename(f))
    df_part = pd.read_csv(f, low_memory=False)
    dfs.append(df_part)

df = pd.concat(dfs, ignore_index=True)
print("\nTotal rows loaded:", len(df))

# =========================================================
# 3. CHECK REQUIRED COLUMNS
# =========================================================
required_cols = ["standard", "issuance_date"]
for col in required_cols:
    if col not in df.columns:
        raise KeyError(f"Required column not found: {col}")

# =========================================================
# 4. PREPARE COLUMNS
# =========================================================
df["issuance_date"] = pd.to_datetime(df["issuance_date"], errors="coerce")
df["year"] = df["issuance_date"].dt.year

df["standard_raw"] = df["standard"].astype(str)

# Remove spaces, dots, parentheses, dashes, etc.
df["standard_clean"] = (
    df["standard_raw"]
    .str.upper()
    .str.replace(r"[^A-Z0-9]", "", regex=True)
    .str.strip()
)

# =========================================================
# 5. CLASSIFY CORRECTED LIGHTING STANDARDS
# =========================================================
def classify_lighting_standard(s):
    # 29 CFR 1910.37(b)
    if re.fullmatch(r"19100037B", s):
        return "29 CFR 1910.37(b)"
    elif re.match(r"^19100037B[A-Z0-9]+$", s):
        return "29 CFR 1910.37(b)"

    # 29 CFR 1926.56
    elif re.match(r"^19260056[A-Z0-9]*$", s):
        return "29 CFR 1926.56"

    # 29 CFR 1915.82
    elif re.match(r"^1915082[A-Z0-9]*$", s):
        return "29 CFR 1915.82"

    # 29 CFR 1917.123
    elif re.match(r"^1917123[A-Z0-9]*$", s):
        return "29 CFR 1917.123"

    # 29 CFR 1918.92
    elif re.match(r"^1918092[A-Z0-9]*$", s):
        return "29 CFR 1918.92"

    else:
        return None

df["lighting_standard"] = df["standard_clean"].apply(classify_lighting_standard)
light_df = df[df["lighting_standard"].notna()].copy()

print("Total illumination-related rows:", len(light_df))

# =========================================================
# 6. BUILD TABLE 1
# =========================================================
description_map = {
    "29 CFR 1910.37(b)": "Exit route illumination",
    "29 CFR 1926.56": "Construction illumination",
    "29 CFR 1915.82": "Shipyard lighting",
    "29 CFR 1917.123": "Marine terminal lighting",
    "29 CFR 1918.92": "Longshoring lighting",
}

all_standards = pd.DataFrame({
    "OSHA Standard": [
        "29 CFR 1910.37(b)",
        "29 CFR 1926.56",
        "29 CFR 1915.82",
        "29 CFR 1917.123",
        "29 CFR 1918.92",
    ]
})

counts = (
    light_df["lighting_standard"]
    .value_counts()
    .rename_axis("OSHA Standard")
    .reset_index(name="Violations")
)

table1 = all_standards.merge(counts, on="OSHA Standard", how="left")
table1["Violations"] = table1["Violations"].fillna(0).astype(int)
table1["Description"] = table1["OSHA Standard"].map(description_map)
table1 = table1[["OSHA Standard", "Description", "Violations"]]

print("\n" + "=" * 75)
print("Table 1. OSHA lighting-specific standards included in the analysis")
print("=" * 75)
print(table1.to_string(index=False))
print("=" * 75)

# Save Table 1 as CSV
table1_csv = os.path.join(base_dir, "table1_corrected_lighting_standards.csv")
table1.to_csv(table1_csv, index=False)

# Save Table 1 as manuscript-ready text
table1_txt = os.path.join(base_dir, "table1_for_manuscript.txt")
with open(table1_txt, "w", encoding="utf-8") as f:
    f.write("Table 1. OSHA lighting-specific standards included in the illumination-related violation analysis.\n\n")
    f.write(table1.to_string(index=False))
    f.write("\n\n")
    f.write("Note. Violations were identified from OSHA citation codes corresponding to lighting-specific regulatory provisions. ")
    f.write("Counts represent violation records, not unique inspections, establishments, or employers.\n")

# =========================================================
# 7. BUILD ANNUAL SUMMARY
# =========================================================
annual_total = (
    df.dropna(subset=["year"])
      .groupby("year")
      .size()
      .rename("total_violations")
)

annual_light = (
    light_df.dropna(subset=["year"])
            .groupby("year")
            .size()
            .rename("light_violations")
)

annual = pd.concat([annual_total, annual_light], axis=1).fillna(0)
annual["light_violations"] = annual["light_violations"].astype(int)
annual["share_percent"] = 100 * annual["light_violations"] / annual["total_violations"]
annual = annual.reset_index()

annual_csv = os.path.join(base_dir, "annual_corrected_illumination_summary.csv")
annual.to_csv(annual_csv, index=False)

print("\nFirst 15 rows of annual summary:")
print(annual.head(15).to_string(index=False))

# =========================================================
# 8. PLOT FIGURE 1
#    Annual counts of illumination-related violations
# =========================================================
plt.rcParams.update({
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 12,
    "figure.dpi": 300,
    "savefig.dpi": 300
})

fig1_path = os.path.join(base_dir, "figure1_light_violations_per_year.png")

plt.figure(figsize=(10, 5.5))
plt.plot(annual["year"], annual["light_violations"], linewidth=2)
plt.title("Annual Counts of OSHA Illumination-Related Violations, 1972–2024")
plt.xlabel("Year")
plt.ylabel("Number of Illumination-Related Violations")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(fig1_path, bbox_inches="tight")
plt.close()

# =========================================================
# 9. PLOT FIGURE 2
#    Share of illumination-related violations among all OSHA violations
# =========================================================
fig2_path = os.path.join(base_dir, "figure2_share_light_violations.png")

plt.figure(figsize=(10, 5.5))
plt.plot(annual["year"], annual["share_percent"], linewidth=2)
plt.title("Illumination-Related Violations as a Percentage of All OSHA Violations, 1972–2024")
plt.xlabel("Year")
plt.ylabel("Illumination-Related Violations (% of all OSHA violations)")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(fig2_path, bbox_inches="tight")
plt.close()

# =========================================================
# 10. SAVE FIGURE CAPTIONS
# =========================================================
captions_txt = os.path.join(base_dir, "figure_captions_corrected.txt")
with open(captions_txt, "w", encoding="utf-8") as f:
    f.write("Figure 1. Annual counts of OSHA illumination-related violations, United States, 1972–2024. ")
    f.write("Illumination-related violations were identified from publicly available OSHA enforcement records using ")
    f.write("lighting-specific regulatory provisions, including 29 CFR 1910.37(b), 29 CFR 1926.56, 29 CFR 1915.82, ")
    f.write("29 CFR 1917.123, and 29 CFR 1918.92. Annual counts represent cited enforcement actions rather than direct ")
    f.write("measurements of workplace illuminance.\n\n")

    f.write("Figure 2. Illumination-related OSHA violations as a percentage of all OSHA violations, United States, 1972–2024. ")
    f.write("Percentages were calculated by dividing annual counts of illumination-related violations identified under ")
    f.write("lighting-specific regulatory provisions by the total number of OSHA violation records for the same year. ")
    f.write("Illumination-related citations represented a very small share of OSHA enforcement activity and generally ")
    f.write("remained below 0.1% of all violations across the study period.\n")

# =========================================================
# 11. OPTIONAL: SAVE MATCHED CODES FOR REVIEW
# =========================================================
matched_codes = (
    light_df[["standard_raw", "standard_clean", "lighting_standard"]]
    .value_counts()
    .reset_index(name="Count")
    .sort_values(["lighting_standard", "Count"], ascending=[True, False])
)

matched_codes_csv = os.path.join(base_dir, "matched_lighting_codes_review.csv")
matched_codes.to_csv(matched_codes_csv, index=False)

# =========================================================
# 12. PRINT FINAL OUTPUT SUMMARY
# =========================================================
print("\nSaved files:")
print(" -", table1_csv)
print(" -", table1_txt)
print(" -", annual_csv)
print(" -", fig1_path)
print(" -", fig2_path)
print(" -", captions_txt)
print(" -", matched_codes_csv)

print("\nDONE.")
