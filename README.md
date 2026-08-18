# osha-illumination-analysis

This repository contains Python scripts and derived datasets for a descriptive analysis of illumination-related enforcement actions recorded in the U.S. Occupational Safety and Health Administration (OSHA) violation database, 1972–2024.

The analysis examines long-term trends in:
- The number of illumination-related OSHA violations
- Their share of all OSHA enforcement activity
- Monetary penalties associated with lighting deficiencies

Illumination-related violations are identified by matching cited citation codes to lighting-specific CFR provisions, with era-specific mapping across OSHA's December 2002 recodification of 29 CFR Part 1910 Subpart E. No industry-sector analysis is performed: the raw violation files contain no NAICS/SIC codes.

This work is intended to support occupational and environmental health research and is suitable for use in regulatory surveillance, exposure assessment, and policy analysis contexts.

---

## Background

Adequate workplace illumination is a fundamental occupational safety requirement, influencing visual performance, accident risk, and overall worker health. While OSHA standards specify minimum illumination requirements for certain tasks and environments (e.g., 29 CFR 1910.37(b), 1926.56), comprehensive assessments of enforcement patterns related to lighting deficiencies are limited.

Publicly available OSHA violation datasets provide an opportunity to examine how often illumination-related hazards are cited and penalized over time.

---

## Data Sources

Primary data source:
U.S. Department of Labor, OSHA Enforcement Data.
https://enforcedata.dol.gov/views/data_summary.php

- **OSHA Violation Data** (`osha_violation0.csv` … `osha_violation13.csv`)
  Records of cited violations, associated standards, penalty amounts, and issuance dates (~13 million records).

The raw data files are not redistributed in this repository and must be obtained directly from OSHA's public data portals. OSHA inspection data (which carry industry codes) are not used in the current analysis.

---

## Repository Structure

```
├── corrected_analysis/     Current (v3) analysis — script, outputs, figures,
│                           and a README documenting all corrections
├── CHANGELOG.md            Revision history (v1.0 → v3.0)
├── scripts/                Legacy v1 keyword-based exploration (superseded)
├── outputs/                Legacy v1 outputs (superseded)
├── figures/                Legacy v1 figures (superseded)
├── README.md
├── LICENSE
└── .gitignore
```

The `scripts/`, `outputs/`, and `figures/` directories contain the initial keyword-based exploratory analysis and are retained for transparency only; their results are superseded by `corrected_analysis/`.

---

## Methods Overview

The current (v3) analysis is code-based matching of CFR provisions — no text mining or keyword screening is used.

Key steps:
1. Clean each cited standard code (uppercase, strip non-alphanumerics)
2. Match against lighting-specific provisions, era-specific across the December 2002 Subpart E recodification: old §1910.36(b)(6) / §1910.37(q)(6)–(7) and current §1910.37(b)(1) / (b)(6), plus §1926.26, §1926.56 (construction) and §1915.82, §1917.123, §1918.92 (maritime)
3. Classify records into four categories (exit route lighting, exit sign illumination, construction illumination, maritime lighting) and a strict work-area/route-lighting subset
4. Aggregate counts, shares, and penalties by year, 1972–2024

See `corrected_analysis/README.md` for full methodological detail. No predictive modeling or causal inference is performed.

---

## Key Result

17,622 illumination-related violations (0.14% of 13.05 million), 7,962 for work-area and route lighting; annual share 0.06–0.22%; median penalty $0.

See `corrected_analysis/` for the current (v3) analysis and `CHANGELOG.md` for the revision history.

## Interpretation Notes

- OSHA records do not include measured illuminance (lux) values.
- Identified violations reflect enforcement activity, not direct exposure prevalence.
- Lighting-related hazards may be underreported if not explicitly cited during inspections.

---

## Reproducibility

All analyses are performed using Python (pandas, matplotlib).

```bash
python corrected_analysis/violations_count_v3.py
```

The script is self-contained: it reads the raw `osha_violation0..13.csv` files (placed in the directory configured at the top of the script) in a single memory-safe pass and writes all tables and figures to `corrected_analysis/`.

## Citation

If you use this code or analysis, please cite:
Buryi, A. (2026). Analysis of OSHA illumination-related enforcement data (1972–2024).
