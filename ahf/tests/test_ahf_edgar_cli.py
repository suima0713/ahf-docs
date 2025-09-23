# -*- coding: utf-8 -*-
"""AHF EDGAR CLI テストケース"""
import sys
import os
import json
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ahf_edgar_cli import (
    num_to_int_k, sha1, strip_tags, find_12m_pct_from_html,
    parse_ex99, dual_anchor, gap, alpha5_compute_opex_k, alpha5_band,
    alpha4_coverage_months
)

def test_num_to_int_k():
    """数値変換テスト"""
    assert num_to_int_k("144,498") == 144498
    assert num_to_int_k("(27,584)") == -27584
    assert num_to_int_k("36.9") == 37
    print("数値変換テスト: パス")

def test_sha1():
    """SHA1ハッシュテスト"""
    result = sha1("Remaining backlog ... 58% within 12 months.")
    assert len(result) == 40
    assert result.isalnum()
    print("SHA1ハッシュテスト: パス")

def test_strip_tags():
    """HTMLタグ除去テスト"""
    html = "<h2>Remaining Performance Obligations</h2><p>Our remaining performance obligations totaled $995,410, of which approximately 58% is expected within 12 months.</p>"
    result = strip_tags(html)
    assert "<" not in result and ">" not in result
    print("HTMLタグ除去テスト: パス")

def test_find_12m_pct():
    """12M%抽出テスト"""
    html = """
    <h2>Remaining Performance Obligations</h2>
    <p>Our remaining performance obligations totaled $995,410, of which approximately 58% is expected within 12 months.</p>
    """
    result = find_12m_pct_from_html(html)
    assert result == 58.0
    print("12M%抽出テスト: パス")

def test_parse_ex99():
    """Ex.99.1解析テスト"""
    text = """
    Total revenues 144,498
    Non-GAAP Gross margin 36.9%
    ADJUSTED EBITDA (27,584)
    """
    result = parse_ex99(text)
    assert result["rev_$k"] == 144498
    assert result["ng_gm_pct"] == 36.9
    assert result["adj_ebitda_$k"] == -27584
    assert result["status"] == "ok"
    print("Ex.99.1解析テスト: パス")

def test_dual_anchor():
    """Dual-Anchorテスト"""
    result = dual_anchor("https://example.com", "Sample quote", 5)
    assert "anchor_primary" in result
    assert "anchor_backup" in result
    assert result["anchor_backup"]["pageno"] == 5
    assert result["anchor_backup"]["hash"] is not None
    print("Dual-Anchorテスト: パス")

def test_gap():
    """Gap-Reasonテスト"""
    result = gap("rpo_12m_pct", "PHRASE_NOT_FOUND", 30)
    assert result["field"] == "rpo_12m_pct"
    assert result["status"] == "data_gap"
    assert result["reason"] == "PHRASE_NOT_FOUND"
    assert result["ttl_days"] == 30
    print("Gap-Reasonテスト: パス")

def test_alpha5_compute_opex():
    """α5 OpEx計算テスト"""
    result = alpha5_compute_opex_k(144498, 36.9, -27584)
    expected = int(round(144498 * (36.9 / 100.0) - (-27584)))
    assert result == expected
    print("α5 OpEx計算テスト: パス")

def test_alpha5_band():
    """α5 Band判定テスト"""
    assert alpha5_band(80000, 83000, 86500) == "Green"
    assert alpha5_band(84000, 83000, 86500) == "Amber"
    assert alpha5_band(87000, 83000, 86500) == "Red"
    print("α5 Band判定テスト: パス")

def test_alpha4_coverage_months():
    """α4 Coverage Months計算テスト"""
    result = alpha4_coverage_months(580000, 144498)  # 58% of 1M RPO, 144k quarterly rev
    expected = round((580000 / 144498) * 3.0, 1)
    assert result == expected
    print("α4 Coverage Months計算テスト: パス")

def test_cli_interface():
    """CLIインターフェーステスト"""
    # 実際のAPI呼び出しは行わず、モックテスト
    print("CLIインターフェーステスト: スキップ（実際のAPI呼び出しなし）")

if __name__ == "__main__":
    test_num_to_int_k()
    test_sha1()
    test_strip_tags()
    test_find_12m_pct()
    test_parse_ex99()
    test_dual_anchor()
    test_gap()
    test_alpha5_compute_opex()
    test_alpha5_band()
    test_alpha4_coverage_months()
    test_cli_interface()
    print("全AHF EDGAR CLIテスト: パス")
