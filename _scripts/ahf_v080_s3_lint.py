#!/usr/bin/env python3
"""
AHF v0.8.0 S3-Lint
Stage-3（半透明αの最大化）のLint実装

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

@dataclass
class S3LintResult:
    """S3-Lint結果"""
    pass: bool
    l1_verbatim_25w: bool
    l2_anchor_present: bool
    l3_single_formula: bool
    l4_ttl_7_90d: bool
    l5_reasoning_1step: bool
    overall_pass: bool
    messages: List[str]

class AHFv080S3Lint:
    """AHF v0.8.0 S3-Lint実装"""
    
    def __init__(self):
        self.max_verbatim_length = 25
        self.min_ttl_days = 7
        self.max_ttl_days = 90
        
    def lint_s3_card(self, card: Dict[str, Any]) -> S3LintResult:
        """S3カードのLint実行"""
        result = S3LintResult(
            pass=False,
            l1_verbatim_25w=False,
            l2_anchor_present=False,
            l3_single_formula=False,
            l4_ttl_7_90d=False,
            l5_reasoning_1step=False,
            overall_pass=False,
            messages=[]
        )
        
        # L1: 逐語≤25語
        verbatim = card.get("t1_verbatim", "")
        if len(verbatim) <= self.max_verbatim_length:
            result.l1_verbatim_25w = True
            result.messages.append(f"L1 PASS: 逐語{len(verbatim)}語 ≤ {self.max_verbatim_length}語")
        else:
            result.messages.append(f"L1 FAIL: 逐語{len(verbatim)}語 > {self.max_verbatim_length}語")
        
        # L2: アンカー有り
        url_anchor = card.get("url_anchor", "")
        if url_anchor and url_anchor.strip() != "":
            result.l2_anchor_present = True
            result.messages.append("L2 PASS: アンカー有り")
        else:
            result.messages.append("L2 FAIL: アンカーなし")
        
        # L3: 四則1行
        test_formula = card.get("test_formula", "")
        if self._is_single_formula(test_formula):
            result.l3_single_formula = True
            result.messages.append("L3 PASS: 四則1行のテスト式")
        else:
            result.messages.append("L3 FAIL: 四則1行でないテスト式")
        
        # L4: TTL=7–90d
        ttl_days = card.get("ttl_days", 0)
        if self.min_ttl_days <= ttl_days <= self.max_ttl_days:
            result.l4_ttl_7_90d = True
            result.messages.append(f"L4 PASS: TTL {ttl_days}日（{self.min_ttl_days}-{self.max_ttl_days}日）")
        else:
            result.messages.append(f"L4 FAIL: TTL {ttl_days}日（{self.min_ttl_days}-{self.max_ttl_days}日外）")
        
        # L5: 推論≤1段
        reasoning = card.get("reasoning", "")
        if self._is_single_step_reasoning(reasoning):
            result.l5_reasoning_1step = True
            result.messages.append("L5 PASS: 推論1段")
        else:
            result.messages.append("L5 FAIL: 推論1段でない")
        
        # 全体パス判定
        result.overall_pass = (
            result.l1_verbatim_25w and
            result.l2_anchor_present and
            result.l3_single_formula and
            result.l4_ttl_7_90d and
            result.l5_reasoning_1step
        )
        
        if result.overall_pass:
            result.pass = True
            result.messages.append("S3-Lint OVERALL PASS: 全チェック通過")
        else:
            result.messages.append("S3-Lint OVERALL FAIL: チェック失敗")
        
        return result
    
    def _is_single_formula(self, formula: str) -> bool:
        """四則1行のテスト式かどうか判定"""
        if not formula or formula.strip() == "":
            return False
        
        # 改行がない（1行）
        if '\n' in formula:
            return False
        
        # 四則演算子が含まれている
        operators = ['+', '-', '*', '/', '=', '>', '<', '>=', '<=']
        has_operator = any(op in formula for op in operators)
        
        return has_operator
    
    def _is_single_step_reasoning(self, reasoning: str) -> bool:
        """推論1段かどうか判定"""
        if not reasoning or reasoning.strip() == "":
            return False
        
        # 推論の段階を示すキーワード
        multi_step_keywords = [
            "まず", "次に", "さらに", "また", "そして", "そのため", "したがって",
            "なぜなら", "なぜならば", "というのは", "つまり", "要するに"
        ]
        
        # 複数段階の推論を示すキーワードが含まれていない
        for keyword in multi_step_keywords:
            if keyword in reasoning:
                return False
        
        return True
    
    def lint_batch(self, cards: List[Dict[str, Any]]) -> Dict[str, Any]:
        """バッチS3-Lint実行"""
        results = {
            "total_cards": len(cards),
            "passed_cards": 0,
            "failed_cards": 0,
            "results": [],
            "summary": {}
        }
        
        for card in cards:
            result = self.lint_s3_card(card)
            
            if result.pass:
                results["passed_cards"] += 1
            else:
                results["failed_cards"] += 1
            
            results["results"].append({
                "card_id": card.get("id", ""),
                "result": result
            })
        
        # サマリー生成
        results["summary"] = {
            "pass_rate": results["passed_cards"] / results["total_cards"] if results["total_cards"] > 0 else 0,
            "common_failures": self._analyze_common_failures(results["results"])
        }
        
        return results
    
    def _analyze_common_failures(self, results: List[Dict[str, Any]]) -> List[str]:
        """共通の失敗パターン分析"""
        failure_patterns = []
        
        for result_item in results:
            result = result_item["result"]
            if not result.pass:
                if not result.l1_verbatim_25w:
                    failure_patterns.append("逐語長すぎ")
                if not result.l2_anchor_present:
                    failure_patterns.append("アンカーなし")
                if not result.l3_single_formula:
                    failure_patterns.append("四則1行でない")
                if not result.l4_ttl_7_90d:
                    failure_patterns.append("TTL範囲外")
                if not result.l5_reasoning_1step:
                    failure_patterns.append("推論複数段")
        
        # 頻度順にソート
        from collections import Counter
        counter = Counter(failure_patterns)
        return [pattern for pattern, count in counter.most_common()]
    
    def generate_s3_lint_report(self, results: Dict[str, Any]) -> str:
        """S3-Lintレポート生成"""
        report = f"""
# S3-Lint レポート

## サマリー
- 総カード数: {results['total_cards']}
- 通過カード数: {results['passed_cards']}
- 失敗カード数: {results['failed_cards']}
- 通過率: {results['summary']['pass_rate']:.1%}

## 共通の失敗パターン
{chr(10).join(f"- {pattern}" for pattern in results['summary']['common_failures'])}

## 詳細結果
"""
        
        for result_item in results["results"]:
            card_id = result_item["card_id"]
            result = result_item["result"]
            
            report += f"\n### {card_id}\n"
            report += f"- 通過: {'✅' if result.pass else '❌'}\n"
            report += f"- L1逐語≤25語: {'✅' if result.l1_verbatim_25w else '❌'}\n"
            report += f"- L2アンカー有り: {'✅' if result.l2_anchor_present else '❌'}\n"
            report += f"- L3四則1行: {'✅' if result.l3_single_formula else '❌'}\n"
            report += f"- L4TTL=7–90d: {'✅' if result.l4_ttl_7_90d else '❌'}\n"
            report += f"- L5推論≤1段: {'✅' if result.l5_reasoning_1step else '❌'}\n"
            
            for message in result.messages:
                report += f"- {message}\n"
        
        return report

def main():
    """メイン実行"""
    if len(sys.argv) < 2:
        print("Usage: python ahf_v080_s3_lint.py <input_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            if input_file.endswith('.json'):
                data = json.load(f)
            else:
                data = json.loads(f.read())
        
        s3_lint = AHFv080S3Lint()
        results = s3_lint.lint_batch(data)
        
        print(json.dumps(results, indent=2, ensure_ascii=False))
        
        # レポート生成
        report = s3_lint.generate_s3_lint_report(results)
        print("\n" + "="*50)
        print(report)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

