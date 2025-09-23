# -*- coding: utf-8 -*-
"""EDGAR純正APIクライアント（軽量版）
Arelle不要でEDGAR直取りによる最適解
"""
import requests
import time
from typing import Dict, Optional, Any

# EDGAR必須ヘッダー
UA = {"User-Agent": "AHF/0.6.0 (contact: ops@example.com)"}

def get_json(url: str) -> Dict[str, Any]:
    """EDGAR APIからJSONを取得（レート制限対応）"""
    r = requests.get(url, headers=UA, timeout=30)
    r.raise_for_status()
    time.sleep(0.2)  # polite throttle (5 req/s)
    return r.json()

def submissions(cik: str) -> Dict[str, Any]:
    """Company Submissions取得（最新の10-Q/10-K/8-Kのアクセッション確定）"""
    cik_padded = str(cik).zfill(10)
    return get_json(f"https://data.sec.gov/submissions/CIK{cik_padded}.json")

def company_facts(cik: str) -> Dict[str, Any]:
    """Company Facts取得（iXBRL事実）"""
    cik_padded = str(cik).zfill(10)
    return get_json(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik_padded}.json")

def frames(taxonomy: str, tag: str, unit: str, period: str, dimensions: Optional[str] = None) -> Dict[str, Any]:
    """Frames取得（系列値・次元）"""
    base_url = f"https://data.sec.gov/api/xbrl/frames/{taxonomy}/{tag}/{unit}/{period}.json"
    if dimensions:
        base_url += f"?{dimensions}"
    return get_json(base_url)

def get_latest_filings(submissions_data: Dict[str, Any], form_types: list = None) -> list:
    """最新の提出書類を取得"""
    if form_types is None:
        form_types = ["10-Q", "10-K", "8-K"]
    
    filings = submissions_data.get("filings", {}).get("recent", {})
    form_types_list = filings.get("form", [])
    accession_numbers = filings.get("accessionNumber", [])
    primary_documents = filings.get("primaryDocument", [])
    
    latest = []
    for i, form_type in enumerate(form_types_list):
        if form_type in form_types:
            latest.append({
                "form": form_type,
                "accessionNumber": accession_numbers[i],
                "primaryDocument": primary_documents[i]
            })
    
    return latest[:5]  # 最新5件

def get_primary_document_url(accession_number: str, primary_document: str) -> str:
    """主要文書のURLを構築"""
    # accession_number: 0001753539-24-000123
    # primary_document: rklb-20250630.htm
    return f"https://www.sec.gov/Archives/edgar/data/{accession_number.split('-')[0].lstrip('0')}/{accession_number.replace('-', '')}/{primary_document}"
