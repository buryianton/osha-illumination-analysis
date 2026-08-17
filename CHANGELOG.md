# Changelog

## v3.0 — August 2026 (manuscript revision, *New Solutions* NEW-26-0032)

Response to peer review. See `corrected_analysis/README.md` for full detail.

- **Fixed:** 29 CFR 1910.37(b) matching restricted to lighting paragraphs (b)(1) and (b)(6); marking paragraphs (b)(2)–(b)(5), (b)(7) excluded. Removes ~23,000 non-illumination records.
- **Fixed:** Era-specific mapping across the December 2002 Subpart E recodification (old §1910.36(b)(6) and §1910.37(q)(6)–(7) → new §1910.37(b)(1) and (b)(6)). Eliminates the artificial 2003 discontinuity.
- **Fixed:** Maritime standard regexes (8-digit clean codes). Maritime total corrected from 0 → 326.
- **Fixed:** Study period enforced to 1972–2024 (2025 partial year removed).
- **Added:** 29 CFR 1926.26 (construction general lighting) alongside §1926.56.
- **Added:** Penalty analysis (initial and current) by category.
- **Added:** Record-level output `illumination_records_v3.csv` for reproducibility.
- **Changed:** Headline total revised from 31,788 → 17,622 (all) / 7,962 (strict). Annual share range revised from "0.03–0.07%" → 0.06–0.22% (all) / 0.04–0.13% (strict).
- **Removed:** Sector/industry analysis (violation files lack NAICS codes).

## v2.0 — early 2026 ("corrected analysis")

- Restricted from full §1910.37 to §1910.37(b). Superseded by v3.0.

## v1.0 — 2025

- Initial keyword and full-§1910.37 analysis. Superseded.
