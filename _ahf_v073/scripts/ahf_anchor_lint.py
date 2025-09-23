#!/usr/bin/env python3
"""
AHF v0.7.3 AnchorLint v1
Purpose: 逐語≤25語＋#:~:text=必須の厳密なアンカー管理
"""

import re
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from urllib.parse import urlparse, quote

class AnchorStatus(Enum):
    """アンカーステータス"""
    VALID = "VALID"                    # 有効
    INVALID_VERBATIM_LENGTH = "INVALID_VERBATIM_LENGTH"  # 逐語>25語
    INVALID_ANCHOR_FORMAT = "INVALID_ANCHOR_FORMAT"      # アンカー形式不正
    MISSING_ANCHOR = "MISSING_ANCHOR"  # アンカー欠如
    PDF_NOT_SUPPORTED = "PDF_NOT_SUPPORTED"  # PDF不可
    SEC_ANCHOR_FAILED = "SEC_ANCHOR_FAILED"  # SECアンカー失敗

class DualAnchorStatus(Enum):
    """デュアルアンカーステータス"""
    CONFIRMED = "CONFIRMED"        # SEC確認済み
    PENDING_SEC = "PENDING_SEC"    # IR/PR一次→SEC待ち
    SINGLE = "SINGLE"              # 単一ソース

@dataclass
class AnchorLintResult:
    """AnchorLint結果"""
    fact_id: str
    status: AnchorStatus
    verbatim_length: int
    anchor_format: str
    dual_anchor_status: DualAnchorStatus
    anchor_backup: Optional[Dict[str, str]]
    lint_messages: List[str]
    fix_suggestions: List[str]

@dataclass
class AnchorBackup:
    """アンカーバックアップ"""
    pageno: Optional[int]
    quote: str
    hash: str
    source_type: str  # "SEC" | "IR" | "PR"

class AnchorLintEngine:
    """AnchorLint v1エンジン"""
    
    def __init__(self):
        self.whitelist_domains = ["sec.gov", "issuer IR"]  # 白ドメイン
        self.max_verbatim_length = 25
        self.anchor_patterns = {
            "sec_anchor": r"#:~:text=([^&]+)",
            "anchor_backup": r"anchor_backup\{([^}]+)\}",
            "url_fragment": r"#([^?]+)"
        }
    
    def lint_fact(self, fact: Dict[str, Any]) -> AnchorLintResult:
        """単一事実のAnchorLint実行"""
        fact_id = fact.get("kpi", "")
        verbatim = fact.get("verbatim", "")
        anchor = fact.get("anchor", "")
        url = fact.get("url", "")
        
        # 逐語長チェック
        verbatim_length = len(verbatim.split()) if verbatim else 0
        verbatim_valid = verbatim_length <= self.max_verbatim_length
        
        # アンカー形式チェック
        anchor_format = self._analyze_anchor_format(anchor)
        anchor_valid = self._validate_anchor_format(anchor, url)
        
        # デュアルアンカーステータス判定
        dual_status = self._determine_dual_anchor_status(url, anchor)
        
        # アンカーバックアップ生成
        anchor_backup = self._generate_anchor_backup(fact) if not anchor_valid else None
        
        # ステータス決定
        status = self._determine_anchor_status(verbatim_valid, anchor_valid, url)
        
        # リントメッセージ生成
        lint_messages = self._generate_lint_messages(verbatim_valid, anchor_valid, status)
        
        # 修正提案生成
        fix_suggestions = self._generate_fix_suggestions(verbatim, anchor, url, status)
        
        return AnchorLintResult(
            fact_id=fact_id,
            status=status,
            verbatim_length=verbatim_length,
            anchor_format=anchor_format,
            dual_anchor_status=dual_status,
            anchor_backup=anchor_backup,
            lint_messages=lint_messages,
            fix_suggestions=fix_suggestions
        )
    
    def _analyze_anchor_format(self, anchor: str) -> str:
        """アンカー形式を解析"""
        if not anchor:
            return "MISSING"
        
        if "#:~:text=" in anchor:
            return "SEC_ANCHOR"
        elif "anchor_backup" in anchor:
            return "ANCHOR_BACKUP"
        elif "#" in anchor:
            return "URL_FRAGMENT"
        else:
            return "UNKNOWN"
    
    def _validate_anchor_format(self, anchor: str, url: str) -> bool:
        """アンカー形式の妥当性を検証"""
        if not anchor:
            return False
        
        # SEC文書の場合は#:~:text=必須
        if "sec.gov" in url:
            return "#:~:text=" in anchor
        
        # その他の場合はanchor_backup許容
        return "anchor_backup" in anchor or "#:~:text=" in anchor
    
    def _determine_dual_anchor_status(self, url: str, anchor: str) -> DualAnchorStatus:
        """デュアルアンカーステータスを判定"""
        if "sec.gov" in url and "#:~:text=" in anchor:
            return DualAnchorStatus.CONFIRMED
        elif "sec.gov" not in url and "anchor_backup" in anchor:
            return DualAnchorStatus.PENDING_SEC
        else:
            return DualAnchorStatus.SINGLE
    
    def _generate_anchor_backup(self, fact: Dict[str, Any]) -> Dict[str, str]:
        """アンカーバックアップを生成"""
        verbatim = fact.get("verbatim", "")
        url = fact.get("url", "")
        
        # ページ番号推定（簡略化）
        pageno = self._estimate_page_number(url, verbatim)
        
        # ハッシュ生成（簡略化）
        hash_value = self._generate_content_hash(verbatim)
        
        # ソースタイプ判定
        source_type = "SEC" if "sec.gov" in url else "IR"
        
        return {
            "pageno": str(pageno) if pageno else "unknown",
            "quote": verbatim,
            "hash": hash_value,
            "source_type": source_type
        }
    
    def _estimate_page_number(self, url: str, verbatim: str) -> Optional[int]:
        """ページ番号を推定"""
        # 実装は簡略化（実際はURL解析や文書構造分析）
        return None
    
    def _generate_content_hash(self, verbatim: str) -> str:
        """コンテンツハッシュを生成"""
        import hashlib
        return hashlib.md5(verbatim.encode()).hexdigest()[:8]
    
    def _determine_anchor_status(self, verbatim_valid: bool, anchor_valid: bool, url: str) -> AnchorStatus:
        """アンカーステータスを決定"""
        if not verbatim_valid:
            return AnchorStatus.INVALID_VERBATIM_LENGTH
        
        if not anchor_valid:
            if "sec.gov" in url:
                return AnchorStatus.SEC_ANCHOR_FAILED
            elif url.endswith(".pdf"):
                return AnchorStatus.PDF_NOT_SUPPORTED
            else:
                return AnchorStatus.INVALID_ANCHOR_FORMAT
        
        if not anchor_valid and not url:
            return AnchorStatus.MISSING_ANCHOR
        
        return AnchorStatus.VALID
    
    def _generate_lint_messages(self, verbatim_valid: bool, anchor_valid: bool, status: AnchorStatus) -> List[str]:
        """リントメッセージを生成"""
        messages = []
        
        if not verbatim_valid:
            messages.append(f"逐語長超過: {self.max_verbatim_length}語を超過")
        
        if not anchor_valid:
            if status == AnchorStatus.SEC_ANCHOR_FAILED:
                messages.append("SEC文書に#:~:text=アンカーが必要")
            elif status == AnchorStatus.PDF_NOT_SUPPORTED:
                messages.append("PDF文書はanchor_backup使用")
            else:
                messages.append("アンカー形式が不正")
        
        if status == AnchorStatus.MISSING_ANCHOR:
            messages.append("アンカーが欠如")
        
        return messages
    
    def _generate_fix_suggestions(self, verbatim: str, anchor: str, url: str, status: AnchorStatus) -> List[str]:
        """修正提案を生成"""
        suggestions = []
        
        if status == AnchorStatus.INVALID_VERBATIM_LENGTH:
            # 逐語短縮提案
            words = verbatim.split()
            if len(words) > self.max_verbatim_length:
                shortened = " ".join(words[:self.max_verbatim_length])
                suggestions.append(f"逐語短縮: '{shortened}'")
        
        if status == AnchorStatus.SEC_ANCHOR_FAILED:
            # SECアンカー生成提案
            text_fragment = quote(verbatim.replace(" ", "%20"))
            sec_anchor = f"{url}#:~:text={text_fragment}"
            suggestions.append(f"SECアンカー生成: {sec_anchor}")
        
        if status == AnchorStatus.PDF_NOT_SUPPORTED:
            # アンカーバックアップ生成提案
            backup = f"anchor_backup{{pageno: 'unknown', quote: '{verbatim}', hash: 'pending'}}"
            suggestions.append(f"アンカーバックアップ: {backup}")
        
        return suggestions
    
    def batch_lint_facts(self, facts: List[Dict[str, Any]]) -> List[AnchorLintResult]:
        """複数事実の一括AnchorLint実行"""
        results = []
        
        for fact in facts:
            result = self.lint_fact(fact)
            results.append(result)
        
        return results
    
    def generate_lint_report(self, results: List[AnchorLintResult]) -> Dict[str, Any]:
        """AnchorLintレポートを生成"""
        total_facts = len(results)
        valid_count = len([r for r in results if r.status == AnchorStatus.VALID])
        invalid_count = total_facts - valid_count
        
        status_distribution = {}
        for result in results:
            status = result.status.value
            status_distribution[status] = status_distribution.get(status, 0) + 1
        
        dual_status_distribution = {}
        for result in results:
            status = result.dual_anchor_status.value
            dual_status_distribution[status] = dual_status_distribution.get(status, 0) + 1
        
        # 問題のある事実を抽出
        problematic_facts = [r for r in results if r.status != AnchorStatus.VALID]
        
        # 修正提案を統合
        all_suggestions = []
        for result in problematic_facts:
            all_suggestions.extend(result.fix_suggestions)
        
        return {
            "summary": {
                "total_facts": total_facts,
                "valid_count": valid_count,
                "invalid_count": invalid_count,
                "validity_rate": (valid_count / total_facts * 100) if total_facts > 0 else 0
            },
            "status_distribution": status_distribution,
            "dual_status_distribution": dual_status_distribution,
            "problematic_facts": [
                {
                    "fact_id": r.fact_id,
                    "status": r.status.value,
                    "verbatim_length": r.verbatim_length,
                    "lint_messages": r.lint_messages,
                    "fix_suggestions": r.fix_suggestions
                }
                for r in problematic_facts
            ],
            "common_suggestions": list(set(all_suggestions)),
            "lint_timestamp": datetime.now().isoformat()
        }
    
    def fix_anchor_issues(self, results: List[AnchorLintResult]) -> List[Dict[str, Any]]:
        """アンカー問題を自動修正"""
        fixed_facts = []
        
        for result in results:
            if result.status == AnchorStatus.VALID:
                continue
            
            fixed_fact = {
                "fact_id": result.fact_id,
                "original_status": result.status.value,
                "fixes_applied": []
            }
            
            # 逐語短縮
            if result.status == AnchorStatus.INVALID_VERBATIM_LENGTH:
                # 実装は簡略化
                fixed_fact["fixes_applied"].append("verbatim_shortened")
            
            # アンカー生成
            if result.status in [AnchorStatus.SEC_ANCHOR_FAILED, AnchorStatus.PDF_NOT_SUPPORTED]:
                if result.anchor_backup:
                    fixed_fact["anchor_backup"] = result.anchor_backup
                    fixed_fact["fixes_applied"].append("anchor_backup_generated")
            
            fixed_facts.append(fixed_fact)
        
        return fixed_facts

def main():
    """メイン実行"""
    lint_engine = AnchorLintEngine()
    
    # サンプル事実データ
    sample_facts = [
        {
            "kpi": "guidance_fy26_mid",
            "verbatim": "FY26 revenue guidance midpoint $2.5B",
            "anchor": "https://sec.gov/edgar/...#:~:text=FY26%20revenue%20guidance",
            "url": "https://sec.gov/edgar/..."
        },
        {
            "kpi": "backlog_growth",
            "verbatim": "This is a very long verbatim that exceeds the 25 word limit and should be flagged by the lint engine",
            "anchor": "anchor_backup{quote: 'backlog growth', hash: 'abc123'}",
            "url": "https://ir.company.com/earnings/"
        },
        {
            "kpi": "opm_drift",
            "verbatim": "Operating margin improved",
            "anchor": "",
            "url": "https://sec.gov/edgar/..."
        }
    ]
    
    # AnchorLint実行
    results = lint_engine.batch_lint_facts(sample_facts)
    
    # レポート生成
    report = lint_engine.generate_lint_report(results)
    
    print("=== AnchorLint v1 レポート ===")
    print(f"総事実数: {report['summary']['total_facts']}")
    print(f"有効数: {report['summary']['valid_count']}")
    print(f"無効数: {report['summary']['invalid_count']}")
    print(f"有効率: {report['summary']['validity_rate']:.1f}%")
    print()
    
    print("ステータス分布:")
    for status, count in report['status_distribution'].items():
        print(f"  {status}: {count}")
    print()
    
    print("問題のある事実:")
    for fact in report['problematic_facts']:
        print(f"  {fact['fact_id']}: {fact['status']}")
        for msg in fact['lint_messages']:
            print(f"    - {msg}")
        for suggestion in fact['fix_suggestions']:
            print(f"    → {suggestion}")
        print()

if __name__ == "__main__":
    main()
