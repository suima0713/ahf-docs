# -*- coding: utf-8 -*-
"""Unit tests for RPO finder."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from mvp4.rpo_finder import find_rpo_12m

def test_rpo_text_fallback():
    text = "Remaining backlog totaled $995,410, of which approximately 58% is expected within 12 months."
    out = find_rpo_12m({}, text)
    assert out["rpo_12m_pct"] == 58.0
    assert out["find_path"] == "fallback_text"

def test_rpo_xbrl():
    xbrl = {
        "RemainingPerformanceObligation": 995410,
        "RemainingPerformanceObligationExpectedToBeSatisfiedWithinOneYear": 58.0
    }
    out = find_rpo_12m(xbrl, "")
    assert out["rpo_total_k"] == 995410
    assert out["rpo_12m_pct"] == 58.0
    assert out["find_path"] == "xbrl"

def test_rpo_manual():
    out = find_rpo_12m({}, "")
    assert out["find_path"] == "manual"

if __name__ == "__main__":
    test_rpo_text_fallback()
    test_rpo_xbrl()
    test_rpo_manual()
    print("All tests passed!")
