# -*- coding: utf-8 -*-
"""12Mテキスト抽出（注記）
HTML本文から12ヶ月以内の比率を決め撃ちで抽出
"""
import re
from typing import Optional, List

# 12ヶ月関連フレーズ
PHRASES = [
    "within 12 months", 
    "within twelve months", 
    "next 12 months", 
    "next twelve months",
    "twelve-month period",
    "12-month period"
]

# 見出し候補（RPO関連）
RPO_HEADERS = [
    "remaining performance obligations",
    "remaining performance obligation",
    "contract liability",
    "contract asset",
    "backlog"
]

def strip_html(html_text: str) -> str:
    """超簡易HTML剥がし"""
    return re.sub(r"<[^>]+>", " ", html_text)

def find_12m_pct(html_text: str) -> Optional[float]:
    """HTML本文から12ヶ月以内の比率を抽出"""
    # HTMLタグを除去
    text = strip_html(html_text)
    text_lower = text.lower()
    
    # 12ヶ月フレーズを検索
    for phrase in PHRASES:
        idx = text_lower.find(phrase)
        if idx == -1:
            continue
            
        # フレーズ前の120文字から%を抽出
        window = text[max(0, idx-120): idx]
        match = re.search(r"(\d{1,3}(?:\.\d+)?)\s*%", window)
        if match:
            return float(match.group(1))
    
    return None

def find_rpo_section(html_text: str) -> Optional[str]:
    """RPO関連セクションを特定"""
    text_lower = html_text.lower()
    
    for header in RPO_HEADERS:
        # 見出しパターンを検索（h1-h6, strong, b等）
        header_pattern = rf"<(?:h[1-6]|strong|b)[^>]*>.*?{re.escape(header)}.*?</(?:h[1-6]|strong|b)>"
        match = re.search(header_pattern, text_lower, re.IGNORECASE | re.DOTALL)
        if match:
            # 見出しの次の段落を取得（簡易実装）
            start_pos = match.end()
            next_header = re.search(r"<(?:h[1-6]|strong|b)[^>]*>", html_text[start_pos:])
            if next_header:
                return html_text[start_pos:start_pos + next_header.start()]
            else:
                return html_text[start_pos:start_pos + 2000]  # 2000文字まで
    
    return None

def extract_12m_from_rpo_section(html_text: str) -> Optional[float]:
    """RPOセクションから12M%を抽出"""
    rpo_section = find_rpo_section(html_text)
    if rpo_section:
        return find_12m_pct(rpo_section)
    return None

def get_12m_percentage(html_text: str) -> Optional[float]:
    """12ヶ月以内の比率を取得（最適化された抽出）"""
    # まずRPOセクションを特定してから抽出
    result = extract_12m_from_rpo_section(html_text)
    if result is not None:
        return result
    
    # セクション特定に失敗した場合は全文検索
    return find_12m_pct(html_text)
