# -*- coding: utf-8 -*-
"""Unit tests for anchor utilities."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from mvp4.anchor_utils import DualAnchor

def test_dual_anchor():
    d = DualAnchor.build("u", "Remaining backlog ... 58% within 12 months.", 9)
    assert d.hash is not None and len(d.hash) == 40
    assert d.anchor_primary == "u"
    assert d.quote == "Remaining backlog ... 58% within 12 months."
    assert d.pageno == 9

def test_dual_anchor_as_dict():
    d = DualAnchor.build("https://example.com", "Test quote", 5)
    result = d.as_dict()
    assert "anchor_primary" in result
    assert "anchor_backup" in result
    assert result["anchor_backup"]["pageno"] == 5
    assert result["anchor_backup"]["quote"] == "Test quote"
    assert result["anchor_backup"]["hash"] is not None

if __name__ == "__main__":
    test_dual_anchor()
    test_dual_anchor_as_dict()
    print("All tests passed!")
