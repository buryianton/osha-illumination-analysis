# osha-illumination-analysis

This repository contains Python scripts and derived datasets for a descriptive analysis of illumination-related enforcement actions recorded in the U.S. Occupational Safety and Health Administration (OSHA) inspection and violation databases.

The analysis focuses on long-term trends (1972–present) in:
- The number of illumination-related OSHA violations
- Monetary penalties associated with lighting deficiencies
- Distribution of violations across industry sectors

This work is intended to support occupational and environmental health research and is suitable for use in regulatory surveillance, exposure assessment, and policy analysis contexts.

---

## Background

Adequate workplace illumination is a fundamental occupational safety requirement, influencing visual performance, accident risk, and overall worker health. While OSHA standards specify minimum illumination requirements for certain tasks and environments (e.g., 29 CFR 1910.37, 1926.56), comprehensive assessments of enforcement patterns related to lighting deficiencies are limited.

Publicly available OSHA inspection and violation datasets provide an opportunity to examine how often illumination-related hazards are identified, penalized, and distributed across industries over time.

Raw OSHA inspection and violation data are not redistributed in this repository and must be obtained directly from OSHA’s public data portals.

---

## Data Sources

Primary data source:
U.S. Department of Labor, OSHA Enforcement Data.
https://enforcedata.dol.gov/views/data_summary.php

Publicly available OSHA inspection and violation datasets were downloaded directly from the Department of Labor enforcement data portal. Data files were accessed in CSV format and processed locally.

- **OSHA Violation Data**  
  Records of cited violations, associated standards, penalty amounts, and inspection dates.

- **OSHA Inspection Data**  
  Records of inspections, industry classification (NAICS), and inspection characteristics.

The raw data files are not redistributed in this repository and must be obtained directly from OSHA’s public data portals.

---

## Repository Structure
```

Repository Structure
├── scripts/
│   ├── extract_low_lighting_osha.py
│   │   Rule-based text mining of OSHA violation records to identify
│   │   plausibly illumination-related violations (low light, visibility,
│   │   emergency egress).
│   │
│   ├── illumination_by_sector.py
│   │   Aggregates illumination-related violations by NAICS sector and year.
│   │
│   ├── plot_illumination_trends.py
│   │   Generates time-series plots of violation counts and penalties.
│   │
│   ├── violation_lighting_search.py
│   │   Exploratory keyword-based search script used during early
│   │   development and validation.
│   │
│   └── README.md
│       Script-specific usage notes.
│
├── outputs/
│   ├── illumination_by_sector*.csv
│   │   Intermediate sector-level summaries generated in batches
│   │   (used to construct merged sector and trend datasets).
│   │
│   ├── illumination_stats_by_year_merged.csv
│   │   Final annual summary used in analysis and manuscript.
│   │
│   └── README.md
│       Description of generated datasets.
│
├── figures/
│   ├── OSHA_illumination_related_violations_per_year.png
│   │   Annual counts of illumination-related OSHA violations.
│   │
│   ├── Total_OSHA_penalties_for_lighting_violations_per_year.png
│   │   Inflation-unadjusted total penalties by year.
│   │
│   └── README.md
│       Figure descriptions.
│
├── README.md
│   Project overview, methods, and data provenance.
│
├── LICENSE
└── .gitignore


```
---

## Methods Overview

The analysis uses a rule-based text mining approach combined with regulatory standard codes to identify records plausibly related to insufficient or inadequate illumination.

Key steps include:
1. Parsing violation narrative and citation text fields
2. Identifying illumination-related records using keyword patterns and CFR references
3. Classifying records into lighting-related categories
4. Aggregating violations and penalties by year and industry sector
5. Producing descriptive statistics and time-series visualizations

No predictive modeling or causal inference is performed.

---

## Outputs

The repository generates the following primary outputs:

- **filtered_records.csv**  
  OSHA violation records plausibly related to illumination deficiencies.

- **summary_by_year.csv**  
  Annual counts of illumination-related violations.

- **summary_by_tag.csv**  
  Distribution of violation categories (e.g., explicit low light, visibility hazards).

- **illumination_by_sector*.csv**  
  Industry-specific summaries based on NAICS classifications.

- **Figures**  
  Time-series plots of violation counts and total penalties per year.

---

## Interpretation Notes

- OSHA records do not include measured illuminance (lux) values.
- Identified violations reflect enforcement activity, not direct exposure prevalence.
- Lighting-related hazards may be underreported if not explicitly cited during inspections.

---

## Reproducibility

All analyses are performed using Python (pandas, matplotlib).  
Scripts are designed to be run sequentially on raw OSHA CSV files.

Example:
```bash
python extract_low_lighting_osha.py --input osha_violation*.csv --output_dir outputs

## Citation
If you use this code or analysis, please cite:
Buryi, A. (2025). Analysis of OSHA illumination-related enforcement data (1972–present).


