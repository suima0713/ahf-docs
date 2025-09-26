# -*- coding: utf-8 -*-
"""Unit tests for gap logger."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from mvp4.gap_logger import gap

def test_gap_logger():
    result = gap("rpo_12m_pct", "NOT_DISCLOSED", 30)
    assert result["field"] == "rpo_12m_pct"
    assert result["status"] == "data_gap"
    assert result["reason"] == "NOT_DISCLOSED"
    assert result["ttl_days"] == 30

def test_gap_logger_invalid_reason():
    result = gap("test_field", "INVALID_REASON", 15)
    assert result["reason"] == "NOT_DISCLOSED"  # Should default to NOT_DISCLOSED

if __name__ == "__main__":
    test_gap_logger()
    test_gap_logger_invalid_reason()
    print("All tests passed!")
