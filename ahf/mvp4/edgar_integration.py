# -*- coding: utf-8 -*-
"""EDGAR統合モジュール
全APIを統合したワンストップでα4/α5データを取得
"""
import requests
from typing import Dict, Any, Optional, Tuple
from .edgar_client import submissions, company_facts, get_latest_filings, get_primary_document_url
from .tag_maps import get_all_financials
from .note_12m import get_12m_percentage
from .ex99_lite import parse_ex99_lite
from .anchor_utils import DualAnchor
from .gap_logger import gap

class EdgarExtractor:
    """EDGAR統合抽出器"""
    
    def __init__(self, cik: str):
        self.cik = cik
        self.submissions_data = None
        self.company_facts_data = None
    
    def fetch_submissions(self) -> Dict[str, Any]:
        """提出書類一覧を取得"""
        if self.submissions_data is None:
            self.submissions_data = submissions(self.cik)
        return self.submissions_data
    
    def fetch_company_facts(self) -> Dict[str, Any]:
        """Company Factsを取得"""
        if self.company_facts_data is None:
            self.company_facts_data = company_facts(self.cik)
        return self.company_facts_data
    
    def get_latest_documents(self) -> list:
        """最新の主要文書を取得"""
        submissions_data = self.fetch_submissions()
        return get_latest_filings(submissions_data)
    
    def get_primary_document_content(self, accession_number: str, primary_document: str) -> str:
        """主要文書のHTML内容を取得"""
        url = get_primary_document_url(accession_number, primary_document)
        response = requests.get(url, headers={"User-Agent": "AHF/0.6.0 (contact: ops@example.com)"})
        response.raise_for_status()
        return response.text
    
    def extract_alpha4_data(self) -> Dict[str, Any]:
        """α4データ（RPO）を抽出"""
        result = {"find_path": "manual", "gap_reason": None}
        
        # Company FactsからRPO合計を取得
        facts_data = self.fetch_company_facts()
        financials = get_all_financials(facts_data)
        
        if financials["rpo_total"]:
            result["rpo_total_k"] = financials["rpo_total"] // 1000  # $k単位に変換
            result["find_path"] = "xbrl"
        
        # 最新文書から12M%を抽出
        documents = self.get_latest_documents()
        for doc in documents[:3]:  # 最新3件をチェック
            try:
                content = self.get_primary_document_content(
                    doc["accessionNumber"], 
                    doc["primaryDocument"]
                )
                pct_12m = get_12m_percentage(content)
                if pct_12m is not None:
                    result["rpo_12m_pct"] = pct_12m
                    if result["find_path"] == "manual":
                        result["find_path"] = "note"
                    break
            except Exception:
                continue
        
        # データギャップの判定
        if "rpo_12m_pct" not in result or result.get("rpo_12m_pct") is None:
            result["gap_reason"] = gap("rpo_12m_pct", "NOT_DISCLOSED", 30)
        
        return result
    
    def extract_alpha5_data(self) -> Dict[str, Any]:
        """α5データ（Ex.99.1）を抽出"""
        result = {"status": "partial"}
        
        # 最新の8-K文書を検索
        documents = self.get_latest_documents()
        for doc in documents:
            if doc["form"] == "8-K":
                try:
                    content = self.get_primary_document_content(
                        doc["accessionNumber"], 
                        doc["primaryDocument"]
                    )
                    # Ex.99.1セクションを検索（簡易実装）
                    if "exhibit 99.1" in content.lower():
                        ex99_data = parse_ex99_lite(content)
                        if ex99_data.get("status") == "ok":
                            result.update(ex99_data)
                            result["find_path"] = "ex99"
                            break
                except Exception:
                    continue
        
        # データギャップの判定
        if result.get("status") == "partial":
            missing_fields = []
            if "rev_k" not in result:
                missing_fields.append("rev_k")
            if "ng_gm_pct" not in result:
                missing_fields.append("ng_gm_pct")
            if "adj_ebitda_k" not in result:
                missing_fields.append("adj_ebitda_k")
            
            if missing_fields:
                result["gap_reason"] = gap(missing_fields[0], "PHRASE_NOT_FOUND", 30)
        
        return result
    
    def create_anchor(self, url: str, quote: str, pageno: int = 0) -> Dict[str, Any]:
        """Dual-Anchorを作成"""
        anchor = DualAnchor.build(url, quote, pageno)
        return anchor.as_dict()
    
    def extract_all(self) -> Dict[str, Any]:
        """全データを一括抽出"""
        alpha4_data = self.extract_alpha4_data()
        alpha5_data = self.extract_alpha5_data()
        
        # アンカー作成（例）
        anchor = self.create_anchor(
            url="https://example.com/sec-filing",
            quote="Sample quote from SEC filing",
            pageno=0
        )
        
        return {
            "alpha4_rpo": alpha4_data,
            "alpha5_inputs": alpha5_data,
            "anchor": anchor
        }

def extract_from_edgar(cik: str) -> Dict[str, Any]:
    """EDGARから全データを抽出（便利関数）"""
    extractor = EdgarExtractor(cik)
    return extractor.extract_all()
