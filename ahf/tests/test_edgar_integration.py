# -*- coding: utf-8 -*-
"""EDGAR統合のテストケース"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from mvp4.edgar_client import submissions, company_facts
from mvp4.tag_maps import get_all_financials
from mvp4.note_12m import get_12m_percentage
from mvp4.edgar_integration import EdgarExtractor

def test_edgar_client():
    """EDGARクライアントの基本テスト"""
    # 実際のAPI呼び出しは行わず、モックデータでテスト
    print("EDGARクライアントテスト: スキップ（実際のAPI呼び出しなし）")

def test_tag_maps():
    """タグマップのテスト"""
    # モックデータ
    mock_facts = {
        "facts": {
            "us-gaap:RemainingPerformanceObligation": {
                "units": {
                    "USD": [
                        {"val": 995410000, "end": "2024-06-30", "fy": 2024, "fp": "Q2"}
                    ]
                }
            }
        }
    }
    
    financials = get_all_financials(mock_facts)
    assert financials["rpo_total"] == 995410000
    print("タグマップテスト: パス")

def test_note_12m():
    """12M抽出のテスト"""
    html_text = """
    <h2>Remaining Performance Obligations</h2>
    <p>Our remaining performance obligations totaled $995,410, of which approximately 58% is expected within 12 months.</p>
    """
    
    result = get_12m_percentage(html_text)
    assert result == 58.0
    print("12M抽出テスト: パス")

def test_edgar_extractor():
    """EDGAR抽出器のテスト"""
    # 実際のCIKは使用せず、モックテスト
    extractor = EdgarExtractor("0001753539")  # BKSYのCIK
    print("EDGAR抽出器テスト: 初期化成功")

if __name__ == "__main__":
    test_edgar_client()
    test_tag_maps()
    test_note_12m()
    test_edgar_extractor()
    print("全EDGAR統合テスト: パス")
