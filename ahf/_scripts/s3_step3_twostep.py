#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
S3-Step3-TwoStep v1.0（最小・強制）
③バリュエーション＋認知ギャップ｜Two-Step v1.0
Step-1｜フェアバリュー差（割安/割高の素点）
Step-2｜適正性チェック（期待成長/認知ギャップで妥当性を判断）
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

class S3Step3TwoStep:
    """③バリュエーション＋認知ギャップ｜Two-Step v1.0実装"""
    
    def __init__(self):
        # Vmult（変更不可）
        self.vmult = {
            "Green": 1.05,
            "Amber": 0.90,
            "Red": 0.75
        }
        
        # 認知フラグ（±）
        self.positive_flags = [
            "raises guidance", "began", "volume shipments", "contract liabilities↑", 
            "ATM sales to date=0", "10%顧客分散"
        ]
        
        self.negative_flags = [
            "acceptance required", "Raw/WIP滞留", "ATM実行", "集中度悪化"
        ]
    
    def calculate_fair_ev_s_rdcf(self, g_fwd: float, opm_fwd: float) -> float:
        """rDCFライトの帯で決めるフェアEV/S"""
        if g_fwd >= 25 and opm_fwd >= 0:
            return 10.0  # g_fwd≥25% かつ OPM_fwd≥0%
        elif (g_fwd >= 10 and g_fwd < 25) or (opm_fwd >= -5 and opm_fwd < 0):
            return 8.0   # いずれか中間（10–25% or −5〜0%）
        else:
            return 6.0    # g_fwd<10% or OPM_fwd≤−5%
    
    def calculate_fair_ev_s_base(self, ev_s_peer_median: float, ev_s_fair_rdcf: float) -> float:
        """フェアの基準：EV/S_fair_base = max(EV/S_peer_median, EV/S_fair_rDCF)（保守）"""
        return max(ev_s_peer_median, ev_s_fair_rdcf)
    
    def calculate_discount_rate(self, ev_s_fair_base: float, ev_s_actual: float) -> float:
        """割引率：Disc% = (EV/S_fair_base − EV/S_actual) / EV/S_fair_base"""
        if ev_s_fair_base == 0:
            return 0.0
        return (ev_s_fair_base - ev_s_actual) / ev_s_fair_base
    
    def determine_color_step1(self, disc_pct: float) -> str:
        """色（DI倍率）はStep-1だけで機械決定"""
        abs_disc = abs(disc_pct)
        
        if abs_disc <= 10:
            return "Green"    # |Disc%| ≤ 10%
        elif abs_disc <= 25:
            return "Amber"    # 10% < |Disc%| ≤ 25%
        else:
            return "Red"      # |Disc%| > 25%
    
    def calculate_growth_delta(self, g_fwd: float, g_peer_median: float) -> float:
        """期待成長の相対差：Δg = g_fwd − g_peer_median"""
        return g_fwd - g_peer_median
    
    def count_cognitive_flags(self, evidence: str) -> Tuple[int, int]:
        """認知フラグ（±）のカウント"""
        evidence_lower = evidence.lower()
        
        positive_count = sum(1 for flag in self.positive_flags if flag in evidence_lower)
        negative_count = sum(1 for flag in self.negative_flags if flag in evidence_lower)
        
        return positive_count, negative_count
    
    def determine_verdict_step2(self, disc_pct: float, delta_g: float, 
                              positive_flags: int, negative_flags: int) -> str:
        """Step-2のVerdict判定"""
        abs_disc = abs(disc_pct)
        
        if disc_pct > 10:  # 割安
            if delta_g >= 10 or positive_flags >= 2:
                return "Underpriced / 不適正（割安すぎ）"
            elif abs(delta_g) < 10 and abs(positive_flags - negative_flags) <= 1:
                return "Underpriced / ほぼ適正"
            else:
                return "Underpriced / ほぼ適正"
        
        elif disc_pct < -10:  # 割高
            if delta_g <= -10 or negative_flags >= 2:
                return "Overpriced / 不適正（割高すぎ）"
            elif abs(delta_g) < 10 and abs(positive_flags - negative_flags) <= 1:
                return "Overpriced / ほぼ適正"
            else:
                return "Overpriced / ほぼ適正"
        
        else:  # 中立
            return "中立"
    
    def evaluate_step1(self, ev_s_actual: float, ev_s_peer_median: float, 
                      g_fwd: float, opm_fwd: float, actual_date: str = "", 
                      actual_source: str = "") -> Dict:
        """Step-1｜フェアバリュー差（割安/割高の素点）"""
        # rDCFライトの帯で決めるフェアEV/S
        ev_s_fair_rdcf = self.calculate_fair_ev_s_rdcf(g_fwd, opm_fwd)
        
        # フェアの基準
        ev_s_fair_base = self.calculate_fair_ev_s_base(ev_s_peer_median, ev_s_fair_rdcf)
        
        # 割引率
        disc_pct = self.calculate_discount_rate(ev_s_fair_base, ev_s_actual)
        
        # 色判定
        color = self.determine_color_step1(disc_pct)
        
        # Vmult
        vmult = self.vmult.get(color, 0.90)
        
        return {
            "ev_s_actual": ev_s_actual,
            "ev_s_peer_median": ev_s_peer_median,
            "ev_s_fair_rdcf": ev_s_fair_rdcf,
            "ev_s_fair_base": ev_s_fair_base,
            "disc_pct": disc_pct,
            "color": color,
            "vmult": vmult,
            "actual_date": actual_date,
            "actual_source": actual_source
        }
    
    def evaluate_step2(self, step1_result: Dict, g_fwd: float, g_peer_median: float, 
                      evidence: str) -> Dict:
        """Step-2｜適正性チェック（期待成長/認知ギャップで妥当性を判断）"""
        # 期待成長の相対差
        delta_g = self.calculate_growth_delta(g_fwd, g_peer_median)
        
        # 認知フラグ（±）
        positive_flags, negative_flags = self.count_cognitive_flags(evidence)
        
        # Verdict判定
        verdict = self.determine_verdict_step2(
            step1_result["disc_pct"], delta_g, positive_flags, negative_flags
        )
        
        return {
            "delta_g": delta_g,
            "positive_flags": positive_flags,
            "negative_flags": negative_flags,
            "verdict": verdict
        }
    
    def get_step3_output_format(self, step1_result: Dict, step2_result: Dict) -> str:
        """出力フォーマット（③の固定欄）"""
        return f"""
[Step-1] EV/S_actual({step1_result['actual_date']}/{step1_result['actual_source']}) = {step1_result['ev_s_actual']:.1f}×
        EV/S_peer_median = {step1_result['ev_s_peer_median']:.1f}×, EV/S_fair_rDCF = {step1_result['ev_s_fair_rdcf']:.1f}× → EV/S_fair_base = {step1_result['ev_s_fair_base']:.1f}×
        Disc% = {step1_result['disc_pct']:.1f}%
        色 = {step1_result['color']}（Vmult={step1_result['vmult']:.2f}）

[Step-2] 期待成長Δg = {step2_result['delta_g']:.1f}pp, 認知フラグ [+{step2_result['positive_flags']} / −{step2_result['negative_flags']}]
        Verdict = {step2_result['verdict']}
"""
    
    def run_s3_lint_step3(self, ev_s_actual: float, ev_s_peer_median: float, 
                         g_fwd: float, opm_fwd: float, evidence: str) -> Tuple[bool, List[str]]:
        """S3-Lint ③（追加の最小チェック）"""
        errors = []
        
        # L5-a：③にRo40が出現したらFAIL
        if "ro40" in evidence.lower() or "ro 40" in evidence.lower():
            errors.append("L5-a: ③にRo40が出現")
        
        # L5-b：③はEV/S_actual・ピア中央値・rDCF帯のみ（他指標混入でFAIL）
        forbidden_terms = ["margin", "opm", "growth", "成長", "マージン", "roic", "wacc"]
        for term in forbidden_terms:
            if term in evidence.lower():
                errors.append(f"L5-b: ③に{term}が混入（EV/S_actual・ピア中央値・rDCF帯のみ）")
        
        # L6：Price-Modeは日付＋出典名必須
        if "price" in evidence.lower() or "yahoo" in evidence.lower():
            if not any(date_pattern in evidence for date_pattern in ["2025", "2024", "2023"]):
                errors.append("L6: Price-Mode使用時に日付が不明記")
        
        # L7：欠測はn/a
        if "未確定" in evidence or "不明" in evidence:
            if "n/a" not in evidence:
                errors.append("L7: 欠測がn/a表記でない")
        
        return len(errors) == 0, errors
    
    def evaluate_complete_step3(self, ev_s_actual: float, ev_s_peer_median: float, 
                               g_fwd: float, opm_fwd: float, g_peer_median: float, 
                               evidence: str, actual_date: str = "", 
                               actual_source: str = "") -> Dict:
        """③バリュエーション＋認知ギャップの完全評価"""
        # Step-1評価
        step1_result = self.evaluate_step1(ev_s_actual, ev_s_peer_median, g_fwd, opm_fwd, 
                                         actual_date, actual_source)
        
        # Step-2評価
        step2_result = self.evaluate_step2(step1_result, g_fwd, g_peer_median, evidence)
        
        # S3-Lint ③チェック
        lint_pass, lint_errors = self.run_s3_lint_step3(ev_s_actual, ev_s_peer_median, 
                                                       g_fwd, opm_fwd, evidence)
        
        return {
            "step1": step1_result,
            "step2": step2_result,
            "lint_pass": lint_pass,
            "lint_errors": lint_errors,
            "output_format": self.get_step3_output_format(step1_result, step2_result)
        }

def main():
    """テスト実行"""
    s3_step3 = S3Step3TwoStep()
    
    # テストケース1（Green）
    print("=== テストケース1（Green） ===")
    result1 = s3_step3.evaluate_complete_step3(
        ev_s_actual=5.0,
        ev_s_peer_median=5.0,
        g_fwd=15.0,
        opm_fwd=5.0,
        g_peer_median=12.0,
        evidence="raises guidance, began volume shipments #:~:text=raises%20guidance",
        actual_date="2025-09-19",
        actual_source="Yahoo Finance"
    )
    print(result1["output_format"])
    print(f"Lint結果: {'PASS' if result1['lint_pass'] else 'FAIL'}")
    if result1['lint_errors']:
        print("エラー:", result1['lint_errors'])
    
    # テストケース2（Amber）
    print("\n=== テストケース2（Amber） ===")
    result2 = s3_step3.evaluate_complete_step3(
        ev_s_actual=6.0,
        ev_s_peer_median=5.0,
        g_fwd=20.0,
        opm_fwd=3.0,
        g_peer_median=15.0,
        evidence="contract liabilities↑, 10%顧客分散 #:~:text=contract%20liabilities",
        actual_date="2025-09-19",
        actual_source="Yahoo Finance"
    )
    print(result2["output_format"])
    
    # テストケース3（Red）
    print("\n=== テストケース3（Red） ===")
    result3 = s3_step3.evaluate_complete_step3(
        ev_s_actual=8.0,
        ev_s_peer_median=5.0,
        g_fwd=5.0,
        opm_fwd=-2.0,
        g_peer_median=15.0,
        evidence="Raw/WIP滞留, ATM実行, 集中度悪化 #:~:text=Raw%2FWIP",
        actual_date="2025-09-19",
        actual_source="Yahoo Finance"
    )
    print(result3["output_format"])
    
    # Lintエラーテスト
    print("\n=== Lintエラーテスト ===")
    result4 = s3_step3.evaluate_complete_step3(
        ev_s_actual=5.0,
        ev_s_peer_median=5.0,
        g_fwd=15.0,
        opm_fwd=5.0,
        g_peer_median=12.0,
        evidence="ro40=45, margin改善 #:~:text=ro40"  # Ro40混入でエラー
    )
    print(f"Lint結果: {'PASS' if result4['lint_pass'] else 'FAIL'}")
    if result4['lint_errors']:
        print("エラー:", result4['lint_errors'])

if __name__ == "__main__":
    main()
