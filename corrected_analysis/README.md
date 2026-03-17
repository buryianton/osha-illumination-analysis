# Corrected Illumination Analysis (2026 Update)

## Summary

This updated analysis refines the identification of illumination-related OSHA violations.

Previous versions of the analysis included all citations under 29 CFR 1910.37 (exit routes).  
However, subsection-level review showed that most of these citations correspond to non-illumination provisions.

## Correction

Only lighting-specific standards are now included:

- 29 CFR 1910.37(b) – Exit route illumination
- 29 CFR 1926.56 – Construction illumination
- 29 CFR 1915.82 – Shipyard lighting
- 29 CFR 1917.123 – Marine terminal lighting
- 29 CFR 1918.92 – Longshoring lighting

## Key Result

Illumination-related violations represent a very small fraction of OSHA enforcement activity:

- ~0.03%–0.07% of all violations per year
- 31,788 total lighting-related violations (1972–2024)

## Implication

This correction shows that lighting hazards are likely **underrepresented in enforcement data**, reinforcing the need for alternative exposure assessment methods (e.g., AI-based lux estimation).

## Files

- `violations_count_corrected.py` – full analysis script
- `table1_corrected_lighting_standards.csv` – Table 1 data
- `annual_corrected_illumination_summary.csv` – time-series data
- `figure1_light_violations_per_year.png` – Figure 1
- `figure2_share_light_violations.png` – Figure 2
