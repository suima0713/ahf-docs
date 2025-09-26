# -*- coding: utf-8 -*-
"""Centralized regex/phrases used across MVP-4 utilities."""
import re

# Rev / Non-GAAP GM / Adj. EBITDA (case-insensitive)
RE_TOTAL_REVENUES = re.compile(r"\bTotal\s+revenues?\b[^\d\-\(]*([\(\)\-\d,]+)", re.I)
RE_NG_GM_PCT = re.compile(r"\bNon\-GAAP\s+Gross\s+margin\b[^\d%]*([\-\d\.]+)\s*%", re.I)
RE_ADJ_EBITDA = re.compile(r"\bAdjusted\s+EBITDA\b[^\d\-\(]*([\(\)\-\d,]+)", re.I)

# 12-month phrases
TWELVE_MONTH_PHRASES = [
    "within 12 months", "within twelve months", "next 12 months",
    "next twelve months", "twelve-month period", "12-month period"
]
RE_12M_GENERIC = re.compile(r"(12\s*months?|twelve\s*months?)", re.I)

# Currency/number helpers
RE_NUMBER = re.compile(r"[\(\)\-]?\d{1,3}(?:,\d{3})*(?:\.\d+)?")

def parse_num_to_int_k(value: str) -> int:
    s = value.strip().replace(",", "")
    neg = s.startswith("(") or s.startswith("-")
    s = s.strip("()-")
    if s == "":
        return 0
    n = float(s)
    if neg:
        n = -n
    # assume already in $k for our pipeline; if $ units given, adapt upstream
    return int(round(n))
