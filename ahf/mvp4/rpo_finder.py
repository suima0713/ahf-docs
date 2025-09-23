# -*- coding: utf-8 -*-
"""Find RPO total and 12M% using XBRL first, fallback to text phrases.
This module avoids external libs by assuming caller pre-parses XBRL dicts.
"""
from typing import Dict, Optional
from .patterns import TWELVE_MONTH_PHRASES, RE_12M_GENERIC

class RPOResult(dict):
    pass

XBRL_KEYS = {
    "rpo_total": [
        "RemainingPerformanceObligation", "RemainingPerformanceObligations",
        "ContractWithCustomerLiability"  # fallback if company stores total here
    ],
    "rpo_12m": [
        "RemainingPerformanceObligationExpectedToBeSatisfiedWithinOneYear",
        "RemainingPerformanceObligationExpectedTwelveMonths"
    ]
}

def _from_xbrl(x: Dict) -> Optional[RPOResult]:
    if not x:
        return None
    res = RPOResult(find_path="xbrl")
    total = None
    pct12 = None
    for k in XBRL_KEYS["rpo_total"]:
        if k in x:
            total = x[k]
            break
    for k in XBRL_KEYS["rpo_12m"]:
        if k in x:
            pct12 = x[k]  # allow pct (0-100) or absolute; caller normalizes
            break
    if total is None and pct12 is None:
        return None
    res["rpo_total_k"] = int(total) if total is not None else None
    res["rpo_12m_pct"] = float(pct12) if pct12 is not None and pct12 <= 100 else None
    return res


def _from_text(note_text: str) -> Optional[RPOResult]:
    if not note_text:
        return None
    lower = note_text.lower()
    if not RE_12M_GENERIC.search(lower):
        return None
    # Very light heuristic: look for patterns like "58% ... within 12 months"
    # Extract nearest percentage preceding a 12-month phrase.
    best = None
    for phr in TWELVE_MONTH_PHRASES:
        idx = lower.find(phr)
        if idx == -1:
            continue
        window = note_text[max(0, idx-60): idx]
        import re
        m = re.search(r"(\d{1,3}(?:\.\d+)?)\s*%", window)
        if m:
            best = float(m.group(1))
            break
    if best is None:
        return None
    return RPOResult(rpo_total_k=None, rpo_12m_pct=best, find_path="fallback_text")


def find_rpo_12m(xbrl: Optional[Dict], note_text: Optional[str]) -> RPOResult:
    res = _from_xbrl(xbrl)
    if res:
        return res
    res = _from_text(note_text or "")
    if res:
        return res
    return RPOResult(find_path="manual")
