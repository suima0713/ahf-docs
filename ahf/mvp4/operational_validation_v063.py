#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AHF v0.6.3 運用検証と監視KPI
- Anchor充足率≥98%
- 数理チェック=100%
- CIKミスマッチ=0
- 差戻り≤5%
- TW衝突二重更新=0
- AnchorLint合格率≥98%
- PENDING_SEC→CONFIRMED 7日以内≥90%
- placeholder検出率=0
- α4/α5計算停止率=0
"""

import json
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import statistics

class OperationalValidator:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.results = {}
        self.alerts = []
    
    def validate_anchor_coverage(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Anchor充足率≥98%"""
        total_anchors = 0
        valid_anchors = 0
        
        # Core評価からAnchorをカウント
        for axis in ['right_shoulder', 'slope_quality', 'time_profile']:
            items = data.get('core_evaluation', {}).get(axis, [])
            for item in items:
                total_anchors += 1
                if item.get('anchor') and item.get('anchor_backup'):
                    valid_anchors += 1
        
        coverage_rate = (valid_anchors / total_anchors * 100) if total_anchors > 0 else 0
        threshold = 98.0
        
        result = {
            'anchor_coverage_rate': coverage_rate,
            'total_anchors': total_anchors,
            'valid_anchors': valid_anchors,
            'threshold': threshold,
            'pass': coverage_rate >= threshold,
            'description': f"Anchor充足率 {coverage_rate:.1f}% vs {threshold}%基準"
        }
        
        if not result['pass']:
            self.alerts.append(f"Anchor充足率不足: {coverage_rate:.1f}% < {threshold}%")
        
        return result
    
    def validate_math_checks(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """数理チェック=100%"""
        auto_checks = data.get('auto_checks', {})
        math_checks = [
            auto_checks.get('alpha4_gate_pass', False),
            auto_checks.get('alpha5_math_pass', False),
            auto_checks.get('anchor_lint_pass', False)
        ]
        
        total_checks = len(math_checks)
        passed_checks = sum(math_checks)
        pass_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 0
        threshold = 100.0
        
        result = {
            'math_check_rate': pass_rate,
            'total_checks': total_checks,
            'passed_checks': passed_checks,
            'threshold': threshold,
            'pass': pass_rate >= threshold,
            'description': f"数理チェック {pass_rate:.1f}% vs {threshold}%基準"
        }
        
        if not result['pass']:
            self.alerts.append(f"数理チェック不足: {pass_rate:.1f}% < {threshold}%")
        
        return result
    
    def validate_cik_consistency(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """CIKミスマッチ=0"""
        # CIK一貫性チェック（実装例）
        cik_mismatches = 0
        total_ciks = 0
        
        # 実際の実装では、複数のソースからCIKを取得して比較
        # ここでは簡略化
        cik_sources = data.get('cik_sources', {})
        if cik_sources:
            ciks = list(cik_sources.values())
            total_ciks = len(ciks)
            unique_ciks = len(set(ciks))
            cik_mismatches = total_ciks - unique_ciks
        
        result = {
            'cik_mismatches': cik_mismatches,
            'total_ciks': total_ciks,
            'threshold': 0,
            'pass': cik_mismatches == 0,
            'description': f"CIKミスマッチ {cik_mismatches} vs 0基準"
        }
        
        if not result['pass']:
            self.alerts.append(f"CIKミスマッチ検出: {cik_mismatches}件")
        
        return result
    
    def validate_rejection_rate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """差戻り≤5%"""
        # 差戻り率計算（実装例）
        total_submissions = data.get('total_submissions', 0)
        rejected_submissions = data.get('rejected_submissions', 0)
        
        rejection_rate = (rejected_submissions / total_submissions * 100) if total_submissions > 0 else 0
        threshold = 5.0
        
        result = {
            'rejection_rate': rejection_rate,
            'total_submissions': total_submissions,
            'rejected_submissions': rejected_submissions,
            'threshold': threshold,
            'pass': rejection_rate <= threshold,
            'description': f"差戻り率 {rejection_rate:.1f}% vs ≤{threshold}%基準"
        }
        
        if not result['pass']:
            self.alerts.append(f"差戻り率超過: {rejection_rate:.1f}% > {threshold}%")
        
        return result
    
    def validate_tw_conflicts(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """TW衝突二重更新=0"""
        # トリップワイヤ衝突チェック
        tw_updates = data.get('tripwire_updates', [])
        conflicts = 0
        
        # 同時更新の検出
        for i, update1 in enumerate(tw_updates):
            for update2 in tw_updates[i+1:]:
                if (update1.get('timestamp') == update2.get('timestamp') and 
                    update1.get('field') == update2.get('field')):
                    conflicts += 1
        
        result = {
            'tw_conflicts': conflicts,
            'total_tw_updates': len(tw_updates),
            'threshold': 0,
            'pass': conflicts == 0,
            'description': f"TW衝突 {conflicts} vs 0基準"
        }
        
        if not result['pass']:
            self.alerts.append(f"TW衝突検出: {conflicts}件")
        
        return result
    
    def validate_anchor_lint_pass_rate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """AnchorLint合格率≥98%"""
        anchor_lint_results = data.get('anchor_lint_results', [])
        total_tests = len(anchor_lint_results)
        passed_tests = sum(1 for result in anchor_lint_results if result.get('pass', False))
        
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        threshold = 98.0
        
        result = {
            'anchor_lint_pass_rate': pass_rate,
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'threshold': threshold,
            'pass': pass_rate >= threshold,
            'description': f"AnchorLint合格率 {pass_rate:.1f}% vs {threshold}%基準"
        }
        
        if not result['pass']:
            self.alerts.append(f"AnchorLint合格率不足: {pass_rate:.1f}% < {threshold}%")
        
        return result
    
    def validate_pending_sec_conversion(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """PENDING_SEC→CONFIRMED 7日以内≥90%"""
        pending_sec_items = data.get('pending_sec_items', [])
        converted_items = []
        
        for item in pending_sec_items:
            created_date = datetime.fromisoformat(item.get('created_date', ''))
            converted_date = item.get('converted_date')
            
            if converted_date:
                converted_date = datetime.fromisoformat(converted_date)
                days_to_convert = (converted_date - created_date).days
                if days_to_convert <= 7:
                    converted_items.append(item)
        
        conversion_rate = (len(converted_items) / len(pending_sec_items) * 100) if pending_sec_items else 0
        threshold = 90.0
        
        result = {
            'conversion_rate': conversion_rate,
            'total_pending': len(pending_sec_items),
            'converted_7days': len(converted_items),
            'threshold': threshold,
            'pass': conversion_rate >= threshold,
            'description': f"PENDING_SEC変換率 {conversion_rate:.1f}% vs {threshold}%基準"
        }
        
        if not result['pass']:
            self.alerts.append(f"PENDING_SEC変換率不足: {conversion_rate:.1f}% < {threshold}%")
        
        return result
    
    def validate_placeholder_detection(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """placeholder検出率=0"""
        # placeholder検出チェック
        placeholder_patterns = [r'\[[0-9]+\]', r'(?i)not_found', r'(?i)PLACEHOLDER']
        detected_placeholders = 0
        total_text_fields = 0
        
        # テキストフィールドをチェック
        for axis in ['right_shoulder', 'slope_quality', 'time_profile']:
            items = data.get('core_evaluation', {}).get(axis, [])
            for item in items:
                text_fields = [item.get('verbatim_≤25w', ''), item.get('anchor', '')]
                for text in text_fields:
                    if text:
                        total_text_fields += 1
                        for pattern in placeholder_patterns:
                            import re
                            if re.search(pattern, text):
                                detected_placeholders += 1
                                break
        
        result = {
            'placeholder_detection_rate': detected_placeholders,
            'total_text_fields': total_text_fields,
            'threshold': 0,
            'pass': detected_placeholders == 0,
            'description': f"placeholder検出 {detected_placeholders} vs 0基準"
        }
        
        if not result['pass']:
            self.alerts.append(f"placeholder検出: {detected_placeholders}件")
        
        return result
    
    def validate_alpha_calculation_continuity(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """α4/α5計算停止率=0"""
        # α計算の継続性チェック
        alpha_calculations = data.get('alpha_calculations', [])
        stopped_calculations = sum(1 for calc in alpha_calculations if calc.get('stopped', False))
        total_calculations = len(alpha_calculations)
        
        stop_rate = (stopped_calculations / total_calculations * 100) if total_calculations > 0 else 0
        threshold = 0.0
        
        result = {
            'alpha_stop_rate': stop_rate,
            'total_calculations': total_calculations,
            'stopped_calculations': stopped_calculations,
            'threshold': threshold,
            'pass': stop_rate <= threshold,
            'description': f"α計算停止率 {stop_rate:.1f}% vs ≤{threshold}%基準"
        }
        
        if not result['pass']:
            self.alerts.append(f"α計算停止: {stopped_calculations}件")
        
        return result
    
    def run_validation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """全検証を実行"""
        self.results = {
            'anchor_coverage': self.validate_anchor_coverage(data),
            'math_checks': self.validate_math_checks(data),
            'cik_consistency': self.validate_cik_consistency(data),
            'rejection_rate': self.validate_rejection_rate(data),
            'tw_conflicts': self.validate_tw_conflicts(data),
            'anchor_lint_pass_rate': self.validate_anchor_lint_pass_rate(data),
            'pending_sec_conversion': self.validate_pending_sec_conversion(data),
            'placeholder_detection': self.validate_placeholder_detection(data),
            'alpha_calculation_continuity': self.validate_alpha_calculation_continuity(data)
        }
        
        # 全体スコア計算
        total_checks = len(self.results)
        passed_checks = sum(1 for result in self.results.values() if result.get('pass', False))
        overall_score = (passed_checks / total_checks * 100) if total_checks > 0 else 0
        
        self.results['overall_score'] = {
            'score': overall_score,
            'total_checks': total_checks,
            'passed_checks': passed_checks,
            'alerts': self.alerts,
            'description': f"全体スコア {overall_score:.1f}% ({passed_checks}/{total_checks})"
        }
        
        return self.results

def main():
    """CLI実行"""
    if len(sys.argv) < 2:
        print("Usage: python operational_validation_v063.py <config.json>")
        sys.exit(1)
    
    config_path = sys.argv[1]
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 標準入力からデータを読み込み
    data = json.load(sys.stdin)
    
    # 運用検証実行
    validator = OperationalValidator(config)
    results = validator.run_validation(data)
    
    # 結果出力
    json.dump(results, sys.stdout, ensure_ascii=False, indent=2)
    
    # アラート表示
    if validator.alerts:
        print("\n🚨 運用アラート:", file=sys.stderr)
        for alert in validator.alerts:
            print(f"  - {alert}", file=sys.stderr)

if __name__ == '__main__':
    main()

