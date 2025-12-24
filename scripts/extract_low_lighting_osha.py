#!/usr/bin/env python3
"""
Extract OSHA violation records plausibly connected to LOW LIGHTING / INSUFFICIENT ILLUMINATION
from a raw OSHA violations CSV (or any similar export).

What it does:
1) Reads a raw OSHA CSV
2) Builds a broad candidate set using lighting/visibility keywords (high recall)
3) Excludes electrical/fixture-only stuff (reduce false positives)
4) Classifies each row into:
   - low_light_explicit
   - low_light_visibility_hazard
   - egress_emergency_lighting
   - electrical_fixture_only
   - unclear_or_other
5) Saves:
   - filtered_records.csv (the extracted records with tags + a score)
   - summary_by_tag.csv
   - summary_by_year.csv (if a year/date column exists)

Usage (examples):
  python extract_low_lighting_osha.py --input osha_violations.csv --output_dir out

If your column names differ, pass them explicitly, e.g.:
  python extract_low_lighting_osha.py --input osha.csv --output_dir out \
      --text_cols "VIOLATION_DESCRIPTION,ABATEMENT_TEXT,NARRATIVE" \
      --cfr_col "CITATION_STANDARD" --date_col "ISSUED_DATE" --naics_col "NAICS"

Notes:
- This is a text-based proxy. OSHA records often do NOT include measured lux values.
- You can tighten/loosen filters by editing KEYWORDS / EXCLUDE lists.
"""

import argparse
import os
import re
import sys
from typing import List, Optional

import pandas as pd

import glob

def read_input_files(inputs):
    dfs = []
    for inp in inputs:                       # inputs is a list now
        for f in glob.glob(inp):             # each inp can be a pattern
            if "osha_violation_20251208.csv" in f:
                print(f"SKIP (excluded): {f}")
                continue
            try:
                print(f"READ: {f}")
                dfs.append(pd.read_csv(f, low_memory=False))
            except PermissionError:
                print(f"SKIP (locked): {f}")

    if not dfs:
        raise RuntimeError("No readable input CSVs were loaded.")

    return pd.concat(dfs, ignore_index=True)


# -----------------------------
# Keyword / pattern dictionaries
# -----------------------------

# Broad capture (high recall)
KW_BROAD = [
    r"\billum",              # illumination, illuminated
    r"\blight",              # lighting, lighted, low light
    r"\bdark\b",
    r"\bvisibility\b",
    r"\bsee\b|\bseeing\b|\bvisible\b",
    r"\bdim\b",
    r"\bpoor lighting\b",
]

# Strong indicators that it's specifically LOW / INSUFFICIENT light
KW_LOW_EXPLICIT = [
    r"\binsufficient (illum|illumination|lighting)\b",
    r"\binadequate (illum|illumination|lighting)\b",
    r"\bnot adequately (lighted|lit)\b",
    r"\bpoor (illumination|lighting)\b",
    r"\blow light levels?\b",
    r"\bdim(ly)? lit\b",
    r"\btoo dark\b",
]

# Visibility-dependent hazards (often caused by low lighting even if not explicit)
KW_VISIBILITY_HAZARD = [
    r"\btrip(ped)?\b|\btripping\b",
    r"\bslip(ped)?\b|\bslipping\b",
    r"\bfall(s|ing|en)?\b",
    r"\bstair(s|way)?\b",
    r"\buneven\b|\bhole\b|\bdebris\b|\bobstruction\b",
    r"\bstruck[- ]by\b|\bbumped\b|\bcollision\b",
    r"\bunable to see\b|\bcould not see\b|\bnot visible\b",
]

# Egress / emergency lighting
KW_EGRESS = [
    r"\begress\b",
    r"\bexit route\b",
    r"\bexit(s)?\b",
    r"\bemergency lighting\b",
    r"\bexit sign\b",
    r"\bstairwell\b",
    r"\bcorridor\b",
]

# Exclusions: electrical/fixture-only issues not about "not enough light"
# (We still tag them, but you may exclude them from your final "low-light" set.)
KW_ELECTRICAL_FIXTURE_ONLY = [
    r"\bground(ing|ed)\b",
    r"\bwiring\b|\bwire\b",
    r"\bconduit\b",
    r"\bjunction\b|\boutlet\b|\breceptacle\b",
    r"\bbreaker\b|\bpanel\b|\benergized\b",
    r"\bcord\b|\bplug\b",
    r"\bfixture\b|\blamp\b|\bbulb\b",  # keep, but combined with other signals determines class
    r"\bbattery\b|\binverter\b",
]

# CFR patterns: helpful for context; may be absent or messy in exports
CFR_EGRESS_HINTS = [r"1910\.37", r"1910\.36", r"1926\.34", r"1926\.56"]
CFR_CONSTRUCTION_HINTS = [r"1926\."]
CFR_GENERAL_INDUSTRY_HINTS = [r"1910\."]


def compile_any(patterns: List[str]) -> re.Pattern:
    return re.compile("(?:" + "|".join(patterns) + ")", flags=re.IGNORECASE)


RE_BROAD = compile_any(KW_BROAD)
RE_LOW_EXPLICIT = compile_any(KW_LOW_EXPLICIT)
RE_VIS_HAZ = compile_any(KW_VISIBILITY_HAZARD)
RE_EGRESS = compile_any(KW_EGRESS)
RE_ELEC = compile_any(KW_ELECTRICAL_FIXTURE_ONLY)

RE_CFR_EGRESS = compile_any(CFR_EGRESS_HINTS)
RE_CFR_CONST = compile_any(CFR_CONSTRUCTION_HINTS)
RE_CFR_1910 = compile_any(CFR_GENERAL_INDUSTRY_HINTS)


def normalize_text(s: str) -> str:
    s = str(s) if s is not None else ""
    s = s.replace("\n", " ").replace("\r", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def build_text_blob(row: pd.Series, cols: List[str]) -> str:
    parts = []
    for c in cols:
        if c in row and pd.notna(row[c]):
            parts.append(normalize_text(row[c]))
    return " | ".join(parts)


def safe_parse_year(value) -> Optional[int]:
    if pd.isna(value):
        return None
    # Try pandas datetime parse
    try:
        dt = pd.to_datetime(value, errors="coerce")
        if pd.isna(dt):
            return None
        return int(dt.year)
    except Exception:
        return None


def tag_record(text: str, cfr_text: str) -> dict:
    """
    Returns a dict with:
      - tag (category)
      - score (rough confidence score)
      - flags (booleans)
    """
    t = text
    c = cfr_text or ""

    broad = bool(RE_BROAD.search(t))
    low_explicit = bool(RE_LOW_EXPLICIT.search(t))
    vis_haz = bool(RE_VIS_HAZ.search(t))
    egress = bool(RE_EGRESS.search(t)) or bool(RE_CFR_EGRESS.search(c))
    elec = bool(RE_ELEC.search(t))

    # Simple scoring: higher means more likely "low light"
    score = 0
    if broad:
        score += 1
    if low_explicit:
        score += 4
    if vis_haz:
        score += 2
    if egress:
        score += 2
    if elec:
        score -= 2  # electrical-only tends to be false positive for low-lux

    # Classification logic
    if low_explicit and not elec:
        tag = "low_light_explicit"
    elif low_explicit and elec:
        # still likely low light, but mentions fixtures; keep as explicit
        tag = "low_light_explicit"
    elif (vis_haz or egress) and broad and score >= 2 and not (elec and not (low_explicit or vis_haz or egress)):
        # visibility hazard / egress suggests poor visibility
        tag = "low_light_visibility_hazard" if vis_haz else "egress_emergency_lighting"
    elif elec and broad and not (low_explicit or vis_haz or egress):
        tag = "electrical_fixture_only"
    else:
        tag = "unclear_or_other"

    return {
        "tag": tag,
        "score": score,
        "broad_kw": broad,
        "low_explicit_kw": low_explicit,
        "visibility_hazard_kw": vis_haz,
        "egress_kw": egress,
        "electrical_kw": elec,
    }


def parse_list_arg(s: str) -> List[str]:
    return [x.strip() for x in s.split(",") if x.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", nargs="+", required=True, help="Path/pattern(s) to raw OSHA CSV(s)")
    ap.add_argument("--output_dir", required=True, help="Directory to save outputs")
    ap.add_argument("--text_cols", default="", help="Comma-separated text columns to combine for search")
    ap.add_argument("--cfr_col", default="", help="Column containing CFR/standard (optional)")
    ap.add_argument("--date_col", default="", help="Column containing a date (optional)")
    ap.add_argument("--naics_col", default="", help="NAICS column (optional; kept in output if present)")
    ap.add_argument("--keep_tags", default="low_light_explicit,low_light_visibility_hazard,egress_emergency_lighting",
                    help="Comma-separated tags to keep in filtered output")
    ap.add_argument("--min_score", type=int, default=2, help="Minimum score to keep (default=2)")
    args = ap.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    df = read_input_files(args.input)
    original_cols = list(df.columns)

    # Auto-detect useful columns if not provided
    if not args.text_cols:
        # Common OSHA export field guesses
        candidates = [
            "violation_description", "Violation Description", "VIOLATION_DESCRIPTION",
            "citation_text", "Citation Text", "CITATION_TEXT",
            "narrative", "Narrative", "NARRATIVE",
            "abatement_text", "Abatement", "ABATEMENT_TEXT",
            "hazard_description", "Hazard", "HAZARD_DESCRIPTION",
        ]
        text_cols = [c for c in candidates if c in original_cols]
        if not text_cols:
            # fallback: any object columns (first few) – better than nothing
            obj_cols = [c for c in original_cols if df[c].dtype == "object"]
            text_cols = obj_cols[:5]
    else:
        text_cols = parse_list_arg(args.text_cols)

    cfr_col = args.cfr_col if args.cfr_col in original_cols else ""
    date_col = args.date_col if args.date_col in original_cols else ""
    naics_col = args.naics_col if args.naics_col in original_cols else ""

    keep_tags = set(parse_list_arg(args.keep_tags))

    # Build searchable blob
    df["_text_blob"] = df.apply(lambda r: build_text_blob(r, text_cols), axis=1)
    if cfr_col:
        df["_cfr_text"] = df[cfr_col].astype(str).fillna("")
    else:
        # try to auto-find a standards/cfr-like column
        possible = [c for c in original_cols if "cfr" in c.lower() or "standard" in c.lower() or "citation" in c.lower()]
        if possible:
            cfr_col = possible[0]
            df["_cfr_text"] = df[cfr_col].astype(str).fillna("")
        else:
            df["_cfr_text"] = ""

    # Broad candidate set
    cand = df[df["_text_blob"].str.contains(RE_BROAD, na=False)].copy()

    # Tagging
    print("ABOUT TO TAG:", len(cand))
    tags = cand.apply(lambda r: tag_record(r["_text_blob"], r["_cfr_text"]), axis=1)
    tags_df = pd.json_normalize(list(tags))

    if "tag" not in tags_df.columns:
        tags_df["tag"] = "unknown"
    if "score" not in tags_df.columns:
        tags_df["score"] = 1

    cand = pd.concat([cand.reset_index(drop=True), tags_df.reset_index(drop=True)], axis=1)
    print(cand[["tag", "score"]].head())
    print("TOTAL ROWS:", len(df))
    print("CAND ROWS:", len(cand))
    print("OUT DIR:", os.path.abspath(args.output_dir))

    # Optional year extraction
    if date_col:
        cand["year"] = cand[date_col].apply(safe_parse_year)
    else:
        # attempt to guess a date column
        possible_dates = [c for c in original_cols if "date" in c.lower() or "issued" in c.lower() or "open" in c.lower()]
        if possible_dates:
            date_col = possible_dates[0]
            cand["year"] = cand[date_col].apply(safe_parse_year)
        else:
            cand["year"] = None

    # Filter: keep likely low-light related records
    filtered = cand[(cand["tag"].isin(keep_tags)) & (cand["score"] >= args.min_score)].copy()

    # Save outputs
    filtered_path = os.path.join(args.output_dir, "filtered_records.csv")
    summary_tag_path = os.path.join(args.output_dir, "summary_by_tag.csv")
    summary_year_path = os.path.join(args.output_dir, "summary_by_year.csv")

    # Keep a compact set of columns, but don’t drop anything important from the original row
    # (You can edit this to keep only a subset for a paper appendix.)
    print("FILTERED ROWS:", len(filtered))
    filtered.to_csv(filtered_path, index=False)

    summary_by_tag = (
        cand.groupby("tag", dropna=False)
        .size()
        .reset_index(name="n_records")
        .sort_values("n_records", ascending=False)
    )
    summary_by_tag.to_csv(summary_tag_path, index=False)

    if "year" in filtered.columns and filtered["year"].notna().any():
        summary_by_year = (
            filtered.dropna(subset=["year"])
            .groupby(["year", "tag"], dropna=False)
            .size()
            .reset_index(name="n_records")
            .sort_values(["year", "n_records"], ascending=[True, False])
        )
    else:
        summary_by_year = pd.DataFrame(columns=["year", "tag", "n_records"])

    summary_by_year.to_csv(summary_year_path, index=False)

    # Console report
    print("=== DONE ===")
    print(f"Input rows: {len(df):,}")
    print(f"Broad keyword candidates: {len(cand):,}")
    print(f"Filtered (kept tags + min_score): {len(filtered):,}")
    print(f"Saved: {filtered_path}")
    print(f"Saved: {summary_tag_path}")
    print(f"Saved: {summary_year_path}")
    print("\nUsed text columns:", text_cols)
    if cfr_col:
        print("CFR column:", cfr_col)
    if date_col:
        print("Date column:", date_col)
    if naics_col:
        print("NAICS column:", naics_col)
    
    cand.head(1).to_csv(os.path.join(args.output_dir, "_debug_head.csv"), index=False)


if __name__ == "__main__":
    main()
