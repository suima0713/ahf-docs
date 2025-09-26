#!/usr/bin/env python3
"""
AHF v0.8.0 AnchorLint v1
逐語≤25語＋#:~:text=必須、PDFはanchor_backup{pageno,quote,hash}

Purpose: 投資判断に直結する固定3軸で評価する
MVP: ①②③の名称と順序を固定／T1で確証（不足は n/a）／定型テーブル＋1行要約を即時出力
"""

import json
import re
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class AnchorType(Enum):
    TEXT_ANCHOR = "text_anchor"  # #:~:text=
    PDF_BACKUP = "pdf_backup"    # anchor_backup{pageno,quote,hash}

@dataclass
class AnchorLintResult:
    """AnchorLint結果"""
    pass: bool
    verbatim_length: int
    has_anchor: bool
    anchor_type: Optional[AnchorType]
    anchor_valid: bool
    messages: List[str]

class AHFv080AnchorLint:
    """AHF v0.8.0 AnchorLint v1実装"""
    
    def __init__(self):
        self.max_verbatim_length = 25
        self.text_anchor_pattern = r'#:~:text='
        self.pdf_backup_pattern = r'anchor_backup\{[^}]+\}'
        
    def lint_anchor(self, verbatim: str, url: str, anchor: str) -> AnchorLintResult:
        """アンカーのLint実行"""
        result = AnchorLintResult(
            pass=False,
            verbatim_length=len(verbatim),
            has_anchor=False,
            anchor_type=None,
            anchor_valid=False,
            messages=[]
        )
        
        # L1: 逐語≤25語
        if len(verbatim) > self.max_verbatim_length:
            result.messages.append(f"L1 FAIL: 逐語が{len(verbatim)}語（上限{self.max_verbatim_length}語）")
        else:
            result.messages.append(f"L1 PASS: 逐語{len(verbatim)}語（上限{self.max_verbatim_length}語）")
        
        # L2: アンカー有り
        if not anchor or anchor.strip() == "":
            result.messages.append("L2 FAIL: アンカーが空")
        else:
            result.has_anchor = True
            result.messages.append("L2 PASS: アンカー有り")
            
            # アンカータイプ判定
            if self._is_text_anchor(anchor):
                result.anchor_type = AnchorType.TEXT_ANCHOR
                result.messages.append("L3 PASS: #:~:text=アンカー")
            elif self._is_pdf_backup(anchor):
                result.anchor_type = AnchorType.PDF_BACKUP
                result.messages.append("L3 PASS: PDF anchor_backup")
            else:
                result.messages.append("L3 FAIL: 無効なアンカー形式")
        
        # L4: URL検証
        if self._is_valid_url(url):
            result.messages.append("L4 PASS: 有効なURL")
        else:
            result.messages.append("L4 FAIL: 無効なURL")
        
        # L5: 白ドメイン検証
        if self._is_white_domain(url):
            result.messages.append("L5 PASS: 白ドメイン")
        else:
            result.messages.append("L5 FAIL: 非白ドメイン")
        
        # 全体パス判定
        result.pass = (
            len(verbatim) <= self.max_verbatim_length and
            result.has_anchor and
            result.anchor_type is not None and
            self._is_valid_url(url) and
            self._is_white_domain(url)
        )
        
        if result.pass:
            result.messages.append("OVERALL PASS: 全チェック通過")
        else:
            result.messages.append("OVERALL FAIL: チェック失敗")
        
        return result
    
    def _is_text_anchor(self, anchor: str) -> bool:
        """#:~:text=アンカーかどうか判定"""
        return bool(re.search(self.text_anchor_pattern, anchor))
    
    def _is_pdf_backup(self, anchor: str) -> bool:
        """PDF anchor_backupかどうか判定"""
        return bool(re.search(self.pdf_backup_pattern, anchor))
    
    def _is_valid_url(self, url: str) -> bool:
        """有効なURLかどうか判定"""
        if not url or url.strip() == "":
            return False
        
        # 基本的なURL形式チェック
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return bool(re.match(url_pattern, url))
    
    def _is_white_domain(self, url: str) -> bool:
        """白ドメインかどうか判定"""
        white_domains = [
            'sec.gov',
            'investors.',
            'ir.',
            'www.',
            'company.com'
        ]
        
        for domain in white_domains:
            if domain in url.lower():
                return True
        
        return False
    
    def lint_batch(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """バッチLint実行"""
        results = {
            "total_items": len(items),
            "passed_items": 0,
            "failed_items": 0,
            "results": [],
            "summary": {}
        }
        
        for item in items:
            verbatim = item.get("verbatim", "")
            url = item.get("url", "")
            anchor = item.get("anchor", "")
            
            result = self.lint_anchor(verbatim, url, anchor)
            
            if result.pass:
                results["passed_items"] += 1
            else:
                results["failed_items"] += 1
            
            results["results"].append({
                "item_id": item.get("id", ""),
                "result": result
            })
        
        # サマリー生成
        results["summary"] = {
            "pass_rate": results["passed_items"] / results["total_items"] if results["total_items"] > 0 else 0,
            "common_failures": self._analyze_common_failures(results["results"])
        }
        
        return results
    
    def _analyze_common_failures(self, results: List[Dict[str, Any]]) -> List[str]:
        """共通の失敗パターン分析"""
        failure_patterns = []
        
        for result_item in results:
            result = result_item["result"]
            if not result.pass:
                if result.verbatim_length > self.max_verbatim_length:
                    failure_patterns.append("逐語長すぎ")
                if not result.has_anchor:
                    failure_patterns.append("アンカーなし")
                if result.anchor_type is None:
                    failure_patterns.append("無効なアンカー形式")
        
        # 頻度順にソート
        from collections import Counter
        counter = Counter(failure_patterns)
        return [pattern for pattern, count in counter.most_common()]
    
    def generate_lint_report(self, results: Dict[str, Any]) -> str:
        """Lintレポート生成"""
        report = f"""
# AnchorLint v1 レポート

## サマリー
- 総項目数: {results['total_items']}
- 通過項目数: {results['passed_items']}
- 失敗項目数: {results['failed_items']}
- 通過率: {results['summary']['pass_rate']:.1%}

## 共通の失敗パターン
{chr(10).join(f"- {pattern}" for pattern in results['summary']['common_failures'])}

## 詳細結果
"""
        
        for result_item in results["results"]:
            item_id = result_item["item_id"]
            result = result_item["result"]
            
            report += f"\n### {item_id}\n"
            report += f"- 通過: {'✅' if result.pass else '❌'}\n"
            report += f"- 逐語長: {result.verbatim_length}語\n"
            report += f"- アンカー: {'✅' if result.has_anchor else '❌'}\n"
            report += f"- アンカータイプ: {result.anchor_type.value if result.anchor_type else 'None'}\n"
            
            for message in result.messages:
                report += f"- {message}\n"
        
        return report

def main():
    """メイン実行"""
    if len(sys.argv) < 2:
        print("Usage: python ahf_v080_anchor_lint.py <input_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            if input_file.endswith('.json'):
                data = json.load(f)
            else:
                data = json.loads(f.read())
        
        lint = AHFv080AnchorLint()
        results = lint.lint_batch(data)
        
        print(json.dumps(results, indent=2, ensure_ascii=False))
        
        # レポート生成
        report = lint.generate_lint_report(results)
        print("\n" + "="*50)
        print(report)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

