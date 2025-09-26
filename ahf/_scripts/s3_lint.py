#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
S3-Lint - Stage-3軽量版リント
最小5チェック実装
"""

import re
from typing import Dict, List, Tuple

class S3Lint:
    """S3-Lint 軽量版実装"""
    
    def __init__(self):
        self.checks = {
            "L1": self._check_evidence_length,
            "L2": self._check_anchor_format,
            "L3": self._check_test_formula,
            "L4": self._check_ttl_range,
            "L5": self._check_inference_steps
        }
    
    def _check_evidence_length(self, card: Dict) -> Tuple[bool, str]:
        """L1: 逐語が≤25語か"""
        evidence = card.get("evidence", "")
        word_count = len(evidence.split())
        
        if word_count <= 25:
            return True, ""
        else:
            return False, f"L1(逐語{word_count}語>25語)"
    
    def _check_anchor_format(self, card: Dict) -> Tuple[bool, str]:
        """L2: URLが#:~:text=付きか（PDFは anchor_backup 併記）"""
        evidence = card.get("evidence", "")
        
        has_anchor = ("#:~:text=" in evidence or 
                     "anchor_backup" in evidence)
        
        if has_anchor:
            return True, ""
        else:
            return False, "L2(anchor missing #:)"
    
    def _check_test_formula(self, card: Dict) -> Tuple[bool, str]:
        """L3: テスト式が1行で四則のみか"""
        test_formula = card.get("test_formula", "")
        
        if not test_formula:
            return False, "L3(test formula absent)"
        
        # 1行チェック
        if len(test_formula.split('\n')) > 1:
            return False, "L3(multi-line formula)"
        
        # 四則演算のみチェック
        allowed_chars = r'[0-9+\-*/%≤≥=().\s]'
        if not re.match(f'^{allowed_chars}+$', test_formula):
            return False, "L3(invalid formula chars)"
        
        return True, ""
    
    def _check_ttl_range(self, card: Dict) -> Tuple[bool, str]:
        """L4: TTLが7-90dか"""
        ttl_days = card.get("ttl_days", 0)
        
        if 7 <= ttl_days <= 90:
            return True, ""
        else:
            return False, f"L4(TTL{ttl_days}d not in 7-90d)"
    
    def _check_inference_steps(self, card: Dict) -> Tuple[bool, str]:
        """L5: 推論段数≤1（"だから→"が一回まで）"""
        evidence = card.get("evidence", "")
        
        # 推論段数カウント
        inference_count = evidence.count("だから") + evidence.count("→")
        
        if inference_count <= 1:
            return True, ""
        else:
            return False, f"L5(inference steps {inference_count}>1)"
    
    def run_lint(self, card: Dict) -> Tuple[bool, str]:
        """S3-Lint実行"""
        errors = []
        
        for check_name, check_func in self.checks.items():
            is_valid, error_msg = check_func(card)
            if not is_valid:
                errors.append(error_msg)
        
        if errors:
            return False, "Lint FAIL: " + " / ".join(errors)
        else:
            return True, "Lint PASS"
    
    def get_detailed_report(self, card: Dict) -> Dict:
        """詳細リントレポート"""
        report = {
            "card_id": card.get("id", "unknown"),
            "checks": {},
            "overall": "PASS"
        }
        
        for check_name, check_func in self.checks.items():
            is_valid, error_msg = check_func(card)
            report["checks"][check_name] = {
                "valid": is_valid,
                "message": error_msg if not is_valid else "OK"
            }
        
        # 全体判定
        failed_checks = [name for name, result in report["checks"].items() 
                        if not result["valid"]]
        
        if failed_checks:
            report["overall"] = "FAIL"
            report["failed_checks"] = failed_checks
        
        return report

def main():
    """テスト実行"""
    lint = S3Lint()
    
    # テストカード（PASS例）
    pass_card = {
        "id": "TEST001",
        "evidence": "ガイダンス中点$121M、直前Q$103Mだから→q/q%=17.48% #:~:text=Revenue",
        "test_formula": "q_q_pct >= 17",
        "ttl_days": 30
    }
    
    # テストカード（FAIL例）
    fail_card = {
        "id": "TEST002",
        "evidence": "これは非常に長い証拠文で25語を大幅に超えているため、L1チェックで失敗するはずです。",
        "test_formula": "invalid formula with @ symbols",
        "ttl_days": 5
    }
    
    # PASS例のテスト
    print("=== PASS例のテスト ===")
    is_valid, message = lint.run_lint(pass_card)
    print(f"結果: {is_valid}, メッセージ: {message}")
    
    # FAIL例のテスト
    print("\n=== FAIL例のテスト ===")
    is_valid, message = lint.run_lint(fail_card)
    print(f"結果: {is_valid}, メッセージ: {message}")
    
    # 詳細レポート
    print("\n=== 詳細レポート ===")
    report = lint.get_detailed_report(fail_card)
    print(f"全体: {report['overall']}")
    for check, result in report['checks'].items():
        print(f"{check}: {result['message']}")

if __name__ == "__main__":
    main()
