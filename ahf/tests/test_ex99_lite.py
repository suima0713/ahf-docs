# -*- coding: utf-8 -*-
"""Unit tests for Ex.99.1 lite parser."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from mvp4.ex99_lite import parse_ex99_lite

def test_parse_ex99():
    sample = """
    Total revenues 144,498
    Non-GAAP Gross margin 36.9%
    ADJUSTED EBITDA (27,584)
    """
    out = parse_ex99_lite(sample)
    assert out["rev_k"] == 144498
    assert out["ng_gm_pct"] == 36.9
    assert out["adj_ebitda_k"] == -27584
    assert out["status"] == "ok"

def test_parse_ex99_partial():
    sample = """
    Total revenues 144,498
    Non-GAAP Gross margin 36.9%
    """
    out = parse_ex99_lite(sample)
    assert out["rev_k"] == 144498
    assert out["ng_gm_pct"] == 36.9
    assert "adj_ebitda_k" not in out
    assert out["status"] == "partial"

if __name__ == "__main__":
    test_parse_ex99()
    test_parse_ex99_partial()
    print("All tests passed!")
