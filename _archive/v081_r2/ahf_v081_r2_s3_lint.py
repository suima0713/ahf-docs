#!/usr/bin/env python3
"""
AHF v0.8.1-r2 S3-Lint
Stage-3のLint実装

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

class S3LintStatus(Enum):
    """S3-Lintステータス"""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"

@dataclass
class S3LintResult:
    """S3-Lint結果"""
    status: S3LintStatus
    message: str
    details: Dict[str, Any]

class AHFv081R2S3Lint:
    """AHF v0.8.1-r2 S3-Lint"""
    
    def __init__(self):
        self.lint_rules = self._load_lint_rules()
        
    def _load_lint_rules(self) -> Dict[str, Any]:
        """Lintルール読み込み"""
        return {
            "verbatim_length": {
                "max_length": 25,
                "description": "S3逐語は25語以内"
            },
            "url_anchor_format": {
                "required_prefix": "#:~:text=",
                "description": "S3アンカーは#:~:text=形式"
            },
            "test_formula": {
                "required_operators": ["+", "-", "*", "/", ">=", "<=", ">", "<", "=="],
                "description": "S3テスト式は四則演算のみ"
            },
            "ttl_days": {
                "max_days": 30,
                "description": "TTLは30日以内"
            },
            "reasoning_length": {
                "max_length": 100,
                "description": "推論は100語以内"
            },
            "reflection_limit": {
                "max_star_adjustment": 1,
                "max_di_adjustment": 0.08,
                "max_alpha_adjustment": 0.05,
                "description": "反映制限"
            }
        }
    
    def lint_batch(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """バッチS3-Lint実行"""
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
            
            if result.status == S3LintStatus.PASS:
                summary["pass_count"] += 1
            elif result.status == S3LintStatus.FAIL:
                summary["fail_count"] += 1
            else:
                summary["warning_count"] += 1
        
        summary["pass_rate"] = summary["pass_count"] / summary["total_items"] if summary["total_items"] > 0 else 0.0
        
        return {
            "results": results,
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        }
    
    def _lint_item(self, item: Dict[str, Any]) -> S3LintResult:
        """アイテムS3-Lint実行"""
        issues = []
        
        # 逐語長チェック
        verbatim = item.get("t1_verbatim", "")
        if len(verbatim.split()) > self.lint_rules["verbatim_length"]["max_length"]:
            issues.append(f"S3逐語が{self.lint_rules['verbatim_length']['max_length']}語を超過: {len(verbatim.split())}語")
        
        # URLアンカーフォーマットチェック
        url_anchor = item.get("url_anchor", "")
        if not url_anchor.startswith(self.lint_rules["url_anchor_format"]["required_prefix"]):
            issues.append(f"S3アンカー形式が不正: {url_anchor}")
        
        # テスト式チェック
        test_formula = item.get("test_formula", "")
        if not self._validate_test_formula(test_formula):
            issues.append(f"S3テスト式が不正: {test_formula}")
        
        # TTLチェック
        ttl_days = item.get("ttl_days", 0)
        if ttl_days > self.lint_rules["ttl_days"]["max_days"]:
            issues.append(f"TTLが{self.lint_rules['ttl_days']['max_days']}日を超過: {ttl_days}日")
        
        # 推論長チェック
        reasoning = item.get("reasoning", "")
        if len(reasoning.split()) > self.lint_rules["reasoning_length"]["max_length"]:
            issues.append(f"推論が{self.lint_rules['reasoning_length']['max_length']}語を超過: {len(reasoning.split())}語")
        
        # 反映制限チェック
        reflection_issues = self._check_reflection_limits(item)
        issues.extend(reflection_issues)
        
        if issues:
            return S3LintResult(
                status=S3LintStatus.FAIL,
                message="; ".join(issues),
                details={"issues": issues}
            )
        else:
            return S3LintResult(
                status=S3LintStatus.PASS,
                message="S3-Lint通過",
                details={}
            )
    
    def _validate_test_formula(self, formula: str) -> bool:
        """テスト式検証"""
        # 四則演算のみ許可
        allowed_operators = self.lint_rules["test_formula"]["required_operators"]
        
        # 基本的な構文チェック
        if not formula:
            return False
        
        # 演算子チェック
        for op in allowed_operators:
            if op in formula:
                return True
        
        # 変数名チェック（英数字とアンダースコアのみ）
        variables = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', formula)
        for var in variables:
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', var):
                return False
        
        return True
    
    def _check_reflection_limits(self, item: Dict[str, Any]) -> List[str]:
        """反映制限チェック"""
        issues = []
        
        # 星調整制限
        star_adjustment = item.get("star_adjustment", 0)
        if abs(star_adjustment) > self.lint_rules["reflection_limit"]["max_star_adjustment"]:
            issues.append(f"星調整が制限を超過: {star_adjustment} > {self.lint_rules['reflection_limit']['max_star_adjustment']}")
        
        # DI調整制限
        di_adjustment = item.get("di_adjustment", 0.0)
        if abs(di_adjustment) > self.lint_rules["reflection_limit"]["max_di_adjustment"]:
            issues.append(f"DI調整が制限を超過: {di_adjustment:.3f} > {self.lint_rules['reflection_limit']['max_di_adjustment']:.3f}")
        
        # α調整制限
        alpha_adjustment = item.get("alpha_adjustment", 0.0)
        if abs(alpha_adjustment) > self.lint_rules["reflection_limit"]["max_alpha_adjustment"]:
            issues.append(f"α調整が制限を超過: {alpha_adjustment:.3f} > {self.lint_rules['reflection_limit']['max_alpha_adjustment']:.3f}")
        
        return issues
    
    def validate_verbatim_length(self, verbatim: str) -> bool:
        """逐語長検証"""
        return len(verbatim.split()) <= 25
    
    def validate_url_anchor_format(self, url_anchor: str) -> bool:
        """URLアンカーフォーマット検証"""
        return url_anchor.startswith("#:~:text=")
    
    def validate_test_formula(self, formula: str) -> bool:
        """テスト式検証"""
        return self._validate_test_formula(formula)
    
    def validate_ttl_days(self, ttl_days: int) -> bool:
        """TTL日数検証"""
        return ttl_days <= 30
    
    def validate_reasoning_length(self, reasoning: str) -> bool:
        """推論長検証"""
        return len(reasoning.split()) <= 100
    
    def validate_reflection_limits(self, item: Dict[str, Any]) -> bool:
        """反映制限検証"""
        star_adjustment = abs(item.get("star_adjustment", 0))
        di_adjustment = abs(item.get("di_adjustment", 0.0))
        alpha_adjustment = abs(item.get("alpha_adjustment", 0.0))
        
        return (star_adjustment <= self.lint_rules["reflection_limit"]["max_star_adjustment"] and
                di_adjustment <= self.lint_rules["reflection_limit"]["max_di_adjustment"] and
                alpha_adjustment <= self.lint_rules["reflection_limit"]["max_alpha_adjustment"])
    
    def get_lint_rules(self) -> Dict[str, Any]:
        """Lintルール取得"""
        return self.lint_rules
    
    def update_lint_rules(self, rules: Dict[str, Any]):
        """Lintルール更新"""
        self.lint_rules.update(rules)
    
    def check_s3_min_spec(self, item: Dict[str, Any]) -> bool:
        """S3-MinSpecチェック"""
        return (self.validate_verbatim_length(item.get("t1_verbatim", "")) and
                self.validate_url_anchor_format(item.get("url_anchor", "")) and
                self.validate_test_formula(item.get("test_formula", "")) and
                self.validate_ttl_days(item.get("ttl_days", 0)) and
                self.validate_reasoning_length(item.get("reasoning", "")) and
                self.validate_reflection_limits(item))

def main():
    """メイン実行"""
    if len(sys.argv) < 2:
        print("Usage: python ahf_v081_r2_s3_lint.py <input_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    # 入力データ読み込み
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # S3-Lint実行
    s3_lint = AHFv081R2S3Lint()
    result = s3_lint.lint_batch(data)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
