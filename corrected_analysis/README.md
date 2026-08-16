# Corrected Illumination Analysis — v3 (2026 Revision)

This directory documents the corrected identification of illumination-related
OSHA violations used in the revised manuscript (analysis window 1972–2024).
Version 3 (`violations_count_v3.py`) supersedes both the original keyword-based
analysis and the earlier corrected version (`violations_count_corrected.py`,
retained here for transparency).

## What was wrong in earlier versions

1. **Wholesale inclusion of 29 CFR 1910.37(b).** The previous corrected script
   counted every citation code beginning with `19100037B` as illumination.
   Under the post-2002 numbering, 1910.37(b) is titled "Lighting and marking":
   only (b)(1) (exit route lighting) and (b)(6) (exit sign illumination,
   5 foot-candles) are lighting provisions. Subsections (b)(2), (b)(4), (b)(5),
   and (b)(7) are exit-sign *marking* provisions — (b)(2) alone accounts for
   13,186 records — and are now excluded. This inflated the earlier total to
   31,788.

2. **No era mapping.** The current 1910.37(b) numbering exists only since
   OSHA's Subpart E recodification (67 FR 67950, effective December 9, 2002).
   Before that, exit-route lighting was old 1910.36(b)(6) and exit-sign
   illumination old 1910.37(q)(6)–(q)(7). Code strings `19100037B**` cited
   before 2003 refer to the *old* 1910.37(b) "Fundamental requirements"
   (not lighting) and are excluded (n = 133).

3. **Maritime standards silently matched zero records.** The earlier regexes
   (`1915082`, `1917123`, `1918092`) do not occur in the data; the actual clean
   codes are 8-digit (`19150082`, `19170123`, `19180092`). Maritime lighting
   (n = 326) was therefore missing entirely from earlier counts.

4. **No upper year bound.** Records from partial-year 2025 were previously
   included; the analysis is now restricted to 1972 ≤ issuance year ≤ 2024.

## Era mapping used in v3

| Category | Old numbering (counted in all years) | 2003+ numbering (counted from 2003) |
|---|---|---|
| Exit route lighting | 29 CFR 1910.36(b)(6) | 29 CFR 1910.37(b)(1) |
| Exit sign illumination | 29 CFR 1910.37(q)(6), (q)(7) | 29 CFR 1910.37(b)(6) |
| Construction illumination | 29 CFR 1926.56, 1926.26 (all years) | — |
| Maritime lighting | 29 CFR 1915.82, 1917.123, 1918.92 (all years) | — |

Old-numbering codes are counted in every year because those code strings are
unambiguous and OSHA continued citing them after the recodification while
inspections opened under the old rule were closed out (459 lag citations in
2003–2014, concentrated 2003–2005). With this rule, exit-route lighting
averages 119/yr in 1998–2002 vs 120/yr in 2003–2007, i.e., the series is
continuous across the recodification.

The **strict subset** comprises work-area/route lighting only: exit route
lighting + construction illumination + maritime lighting (exit sign
illumination excluded).

## Key results (1972–2024)

- Total illumination-related violations: **17,622** (strict subset: **7,962**)
- Average per year: 332.5 (strict: 150.2)
- Annual share of all OSHA violations: 0.064% (1984) – 0.219% (1972);
  strict: 0.040% (1991) – 0.126% (1972)
- By category: exit sign illumination 9,660; exit route lighting 4,827;
  construction illumination 2,809; maritime lighting 326
- Median initial penalty: $0 in every category (77.4% of records carry a
  zero or blank initial penalty); total initial penalties $5,770,535
  (current penalties $3,574,552)

**Penalty handling:** blank/missing `initial_penalty` and `current_penalty`
values are treated as $0 (common in early records); the zero-penalty shares
include them.

## Implication (unchanged)

Illumination-related citations remain a very small share of OSHA enforcement
activity (< 0.22% of all violations in every year), reinforcing that lighting
hazards are underrepresented in enforcement data and supporting the need for
alternative exposure assessment methods (e.g., AI-based lux estimation).

## Files

- `violations_count_v3.py` — full v3 analysis script (memory-safe single pass
  over the raw `osha_violation0..13.csv` files; prints era-mapping diagnostics
  and the 2003 continuity check)
- `table1_v3.csv` — counts and penalty statistics by standard and category
- `annual_v3.csv` — year, total OSHA violations, illumination counts
  (all/strict), and shares (%)
- `illumination_records_v3.csv` — record-level subset (activity_nr, standard,
  category, strict flag, year, penalties)
- `figure1_v3.png` — annual counts by category, 300 dpi
- `figure2_v3.png` — annual share of all OSHA violations (all vs strict), 300 dpi
- `violations_count_corrected.py`, `table1_corrected_lighting_standards.csv`,
  `annual_corrected_illumination_summary.csv`, `figure1/2_*.png` — superseded
  v2 files, retained for transparency

Raw OSHA violation files are not redistributed; obtain them from
https://enforcedata.dol.gov/views/data_summary.php
