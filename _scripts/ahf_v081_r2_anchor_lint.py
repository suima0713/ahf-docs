#!/usr/bin/env python3
"""
AHF v0.8.1-r2 AnchorLint
証拠階層とアンカー検証の実装

Purpose: 投資判断に直結する固定4軸で評価
MVP: ①②③④の名称と順序を絶対固定／T1 or T1*で確証（不足はn/a）／定型テーブル＋1行要約を即出力
"""

import json
import yaml
import sys
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum

class LintStatus(Enum):
    """Lintステータス"""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"

@dataclass
class LintResult:
    """Lint結果"""
    status: LintStatus
    message: str
    details: Dict[str, Any]

class AHFv081R2AnchorLint:
    """AHF v0.8.1-r2 AnchorLint"""
    
    def __init__(self):
        self.lint_rules = self._load_lint_rules()
        
    def _load_lint_rules(self) -> Dict[str, Any]:
        """Lintルール読み込み"""
        return {
            "verbatim_length": {
                "max_length": 25,
                "description": "逐語は25語以内"
            },
            "anchor_format": {
                "required_prefix": "#:~:text=",
                "description": "アンカーは#:~:text=形式"
            },
            "url_format": {
                "required_domains": ["sec.gov", "investor.", "company.com"],
                "description": "URLは信頼できるドメイン"
            },
            "t1star_independence": {
                "min_sources": 2,
                "description": "T1*は独立2源以上"
            },
            "t1star_quote_length": {
                "max_length": 25,
                "description": "T1*逐語は25語以内"
            },
            "price_lint": {
                "ev_used": True,
                "ps_used": False,
                "same_day": True,
                "same_source": True,
                "description": "価格系隔離ルール"
            }
        }
    
    def lint_batch(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """バッチLint実行"""
        results = []
        summary = {
            "total_items": len(data),
            "pass_count": 0,
            "fail_count": 0,
            "warning_count": 0,
            "pass_rate": 0.0
        }
        
        for item in data:
            result = self._lint_item(item)
            results.append(result)
            
            if result.status == LintStatus.PASS:
                summary["pass_count"] += 1
            elif result.status == LintStatus.FAIL:
                summary["fail_count"] += 1
            else:
                summary["warning_count"] += 1
        
        summary["pass_rate"] = summary["pass_count"] / summary["total_items"] if summary["total_items"] > 0 else 0.0
        
        return {
            "results": results,
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        }
    
    def _lint_item(self, item: Dict[str, Any]) -> LintResult:
        """アイテムLint実行"""
        issues = []
        
        # 逐語長チェック
        verbatim = item.get("verbatim", "")
        if len(verbatim.split()) > self.lint_rules["verbatim_length"]["max_length"]:
            issues.append(f"逐語が{self.lint_rules['verbatim_length']['max_length']}語を超過: {len(verbatim.split())}語")
        
        # アンカーフォーマットチェック
        anchor = item.get("anchor", "")
        if not anchor.startswith(self.lint_rules["anchor_format"]["required_prefix"]):
            issues.append(f"アンカー形式が不正: {anchor}")
        
        # URLドメインチェック
        url = item.get("url", "")
        if not self._check_url_domain(url):
            issues.append(f"URLドメインが信頼できない: {url}")
        
        # 証拠階層チェック
        evidence_level = item.get("evidence_level", "T2")
        if evidence_level == "T1*":
            if not self._check_t1star_independence(item):
                issues.append("T1*証拠の独立性が不十分")
        
        if issues:
            return LintResult(
                status=LintStatus.FAIL,
                message="; ".join(issues),
                details={"issues": issues}
            )
        else:
            return LintResult(
                status=LintStatus.PASS,
                message="Lint通過",
                details={}
            )
    
    def _check_url_domain(self, url: str) -> bool:
        """URLドメインチェック"""
        required_domains = self.lint_rules["url_format"]["required_domains"]
        return any(domain in url for domain in required_domains)
    
    def _check_t1star_independence(self, item: Dict[str, Any]) -> bool:
        """T1*独立性チェック"""
        # 実際の実装では、複数ソースの独立性を詳細チェック
        return item.get("two_sources", False) and item.get("independent", False)
    
    def lint_t1star_batch(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """T1*バッチLint実行"""
        results = []
        summary = {
            "total_items": len(data),
            "pass_count": 0,
            "fail_count": 0,
            "warning_count": 0,
            "pass_rate": 0.0
        }
        
        for item in data:
            result = self._lint_t1star_item(item)
            results.append(result)
            
            if result.status == LintStatus.PASS:
                summary["pass_count"] += 1
            elif result.status == LintStatus.FAIL:
                summary["fail_count"] += 1
            else:
                summary["warning_count"] += 1
        
        summary["pass_rate"] = summary["pass_count"] / summary["total_items"] if summary["total_items"] > 0 else 0.0
        
        return {
            "results": results,
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        }
    
    def _lint_t1star_item(self, item: Dict[str, Any]) -> LintResult:
        """T1*アイテムLint実行"""
        issues = []
        
        # 二重ソースチェック
        if not item.get("two_sources", False):
            issues.append("T1*は二重ソース必須")
        
        # 独立性チェック
        if not item.get("independent", False):
            issues.append("T1*は独立性必須")
        
        # 逐語長チェック
        quote_len = item.get("quote_len", 0)
        if quote_len > self.lint_rules["t1star_quote_length"]["max_length"]:
            issues.append(f"T1*逐語が{self.lint_rules['t1star_quote_length']['max_length']}語を超過: {quote_len}語")
        
        # URLテキストアンカーチェック
        if not item.get("url_has_text", False):
            issues.append("T1*はURLテキストアンカー必須")
        
        if issues:
            return LintResult(
                status=LintStatus.FAIL,
                message="; ".join(issues),
                details={"issues": issues}
            )
        else:
            return LintResult(
                status=LintStatus.PASS,
                message="T1*Lint通過",
                details={}
            )
    
    def lint_price_batch(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """価格バッチLint実行"""
        results = []
        summary = {
            "total_items": len(data),
            "pass_count": 0,
            "fail_count": 0,
            "warning_count": 0,
            "pass_rate": 0.0
        }
        
        for item in data:
            result = self._lint_price_item(item)
            results.append(result)
            
            if result.status == LintStatus.PASS:
                summary["pass_count"] += 1
            elif result.status == LintStatus.FAIL:
                summary["fail_count"] += 1
            else:
                summary["warning_count"] += 1
        
        summary["pass_rate"] = summary["pass_count"] / summary["total_items"] if summary["total_items"] > 0 else 0.0
        
        return {
            "results": results,
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        }
    
    def _lint_price_item(self, item: Dict[str, Any]) -> LintResult:
        """価格アイテムLint実行"""
        issues = []
        
        # EV使用チェック
        if not item.get("ev_used", False):
            issues.append("EV使用必須")
        
        # P/S使用禁止チェック
        if item.get("ps_used", False):
            issues.append("P/S使用禁止")
        
        # 同日チェック
        if not item.get("same_day", False):
            issues.append("同日データ必須")
        
        # 同ソースチェック
        if not item.get("same_source", False):
            issues.append("同ソースデータ必須")
        
        if issues:
            return LintResult(
                status=LintStatus.FAIL,
                message="; ".join(issues),
                details={"issues": issues}
            )
        else:
            return LintResult(
                status=LintStatus.PASS,
                message="価格Lint通過",
                details={}
            )
    
    def validate_anchor_format(self, anchor: str) -> bool:
        """アンカーフォーマット検証"""
        return anchor.startswith("#:~:text=")
    
    def validate_verbatim_length(self, verbatim: str) -> bool:
        """逐語長検証"""
        return len(verbatim.split()) <= 25
    
    def validate_url_domain(self, url: str) -> bool:
        """URLドメイン検証"""
        return self._check_url_domain(url)
    
    def validate_t1star_independence(self, item: Dict[str, Any]) -> bool:
        """T1*独立性検証"""
        return self._check_t1star_independence(item)
    
    def validate_price_lint(self, item: Dict[str, Any]) -> bool:
        """価格Lint検証"""
        return (item.get("ev_used", False) and 
                not item.get("ps_used", False) and 
                item.get("same_day", False) and 
                item.get("same_source", False))
    
    def get_lint_rules(self) -> Dict[str, Any]:
        """Lintルール取得"""
        return self.lint_rules
    
    def update_lint_rules(self, rules: Dict[str, Any]):
        """Lintルール更新"""
        self.lint_rules.update(rules)

def main():
    """メイン実行"""
    if len(sys.argv) < 2:
        print("Usage: python ahf_v081_r2_anchor_lint.py <input_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    # 入力データ読み込み
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # AnchorLint実行
    anchor_lint = AHFv081R2AnchorLint()
    result = anchor_lint.lint_batch(data)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
