# Corrected Illumination Analysis — Version 3 (August 2026)

## Summary

This folder contains the current analysis of illumination-related OSHA enforcement records, 1972–2024, supporting the manuscript *Illumination-Related OSHA Enforcement Activity in U.S. Workplaces: Trends, Penalties, and Surveillance Limitations, 1972–2024* (revision submitted to *New Solutions*, August 2026).

Version 3 supersedes the earlier "corrected" analysis (`violations_count_corrected.py`, kept for transparency). The revision responds to peer-review comments identifying an inconsistency between the reported time trends and the generated figures. Investigation showed that the earlier code-matching rule over-included non-illumination citations and did not account for OSHA's December 2002 recodification of 29 CFR Part 1910 Subpart E.

## What changed from Version 2 → Version 3

**1. Sub-subsection restriction of 29 CFR 1910.37(b).**
Current §1910.37(b) is titled "Lighting and marking must be adequate and appropriate." Only two of its paragraphs concern illumination:
- (b)(1) — exit routes must be adequately lighted
- (b)(6) — exit signs must be illuminated to ≥5 foot-candles (54 lux)

Paragraphs (b)(2), (b)(3), (b)(4), (b)(5), (b)(7) address exit-sign marking, wording, and visibility. Version 2 matched every code beginning `19100037B` and therefore counted these as illumination violations (≈23,000 records, dominated by (b)(2) — the "Exit" sign requirement). Version 3 counts only (b)(1) and (b)(6).

**2. Era-specific code mapping.**
The current §1910.37(b) numbering exists only since the Subpart E recodification (67 FR 67950; effective 9 Dec 2002). Before that:
- exit-route lighting was at old §1910.36(b)(6)
- exit-sign illumination was at old §1910.37(q)(6) and (q)(7)

Version 3 uses the historically equivalent provision for each period, producing a continuous 1972–2024 series. Citations issued under old-numbering codes after December 2002 (n = 459, concentrated 2003–2005) are retained because those code strings are unambiguous. Records with new-style `19100037B*` codes issued *before* 2003 (n = 133) are excluded because they reference the pre-recodification §1910.37(b) ("Fundamental requirements"), which is unrelated to lighting.

**3. Maritime standards corrected.**
Version 2 regexes for 29 CFR 1915.82, 1917.123, and 1918.92 matched zero records because the cleaned code strings are eight-digit (`19150082`, `19170123`, `19180092`), not seven-digit. Corrected maritime total: 326 violations (204 shipyard, 33 marine terminal, 89 longshoring).

**4. Construction: 29 CFR 1926.26 added.**
The 2025 OSHA proposed rule (Docket OSHA-2025-0040) would rescind both §1926.26 (general lighting) and §1926.56 (illumination table). Version 3 counts both (2,809 total).

**5. Study period enforced.**
Records are filtered to issuance year 1972–2024. Version 2 output included a partial 2025 row.

**6. Penalty analysis added.**
Initial and current penalty summaries by category are now reported (blank `initial_penalty` treated as $0; noted in table).

## Key results, 1972–2024

| Measure | All illumination | Strict* |
|---|---|---|
| Total violations | 17,622 | 7,962 |
| Mean per year | 333 | 150 |
| Share of all OSHA violations (annual range) | 0.064%–0.219% | 0.040%–0.126% |
| Median initial penalty | $0 | $0 |
| Records with $0 / blank initial penalty | 77% | — |
| Total initial / current penalties | $5.77M / $3.57M | — |

*Strict = exit-route lighting + construction + maritime; excludes exit-sign illumination (b)(6)/(q)(6)–(7).

By category (all): exit-sign illumination 9,660 · exit-route lighting 4,827 · construction illumination 2,809 · maritime lighting 326.

Continuity check across the 2002 recodification (mean/yr): exit-route lighting 119 (1998–2002) vs 120 (2003–2007) — no discontinuity.

## Files

- `violations_count_v3.py` — current analysis script (self-contained; reads the raw files in a single chunked pass, prints era-mapping diagnostics, and writes all outputs below)
- `illumination_records_v3.csv` — record-level illumination subset (year, code, category, penalty, activity_nr)
- `table1_v3.csv` — counts and penalties by standard/category
- `annual_v3.csv` — year, total OSHA violations, illumination counts (all/strict), shares
- `figure1_v3.png` — annual counts by category (300 dpi)
- `figure2_v3.png` — annual share of all OSHA violations, all vs strict (300 dpi)
- `violations_count_corrected.py`, `annual_corrected_illumination_summary.csv`, `table1_corrected_lighting_standards.csv`, `figure1_light_violations_per_year.png`, `figure2_share_light_violations.png` — **Version 2 (superseded; retained for transparency)**

## Data source

Publicly available OSHA enforcement data, U.S. Department of Labor: https://enforcedata.dol.gov/ (files `osha_violation0.csv` … `osha_violation13.csv`, downloaded 2025). Note: violation files do not contain NAICS/SIC codes; sector analysis would require joining to inspection files via `activity_nr`.

## Regulatory reference

OSHA. Exit Routes, Emergency Action Plans, and Fire Prevention Plans; Final Rule. 67 FR 67950 (7 Nov 2002), effective 9 Dec 2002.
