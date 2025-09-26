#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
S3-Contract v1.0（過実装なし）
運用"契約" v1.0の最終実装
軸名固定・T1厳守・②の式固定・③の二段・Lintで止める
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

class S3ContractV1:
    """S3-Contract v1.0（過実装なし）実装"""
    
    def __init__(self):
        # 軸名固定（変更不可）
        self.axis_names = {
            "axis1": "①長期EV確度",
            "axis2": "②長期EV勾配", 
            "axis3": "③バリュエーション＋認知ギャップ"
        }
        
        # ②の式（変更不可）
        self.nes_formula = "NES = 0.5·q/q + 0.3·改定% + 0.2·受注% + Margin_term + Health_term(Ro40)"
        
        # NES★換算（固定）
        self.nes_thresholds = {
            (8, float('inf')): 5,    # NES≥8→★5
            (5, 8): 4,               # +5–8→★4
            (2, 5): 3,               # +2–5→★3
            (0, 2): 2,               # 0–2→★2
            (float('-inf'), 0): 1    # <0→★1
        }
        
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
    
    def validate_t1_strict(self, evidence: str) -> Tuple[bool, str]:
        """T1厳守：逐語≤25語＋#:~:text=、欠測はn/a（推測で埋めない）"""
        if not evidence:
            return False, "T1証拠が空"
        
        # 逐語≤25語
        word_count = len(evidence.split())
        if word_count > 25:
            return False, f"T1厳守違反: 逐語{word_count}語>25語"
        
        # #:~:text=付き（PDFは anchor_backup）
        if not ("#:~:text=" in evidence or "anchor_backup" in evidence):
            return False, "T1厳守違反: #:~:text=付きでない"
        
        # 欠測はn/a（推測で埋めない）
        if "未確定" in evidence or "不明" in evidence:
            if "n/a" not in evidence:
                return False, "T1厳守違反: 欠測がn/a表記でない"
        
        return True, "T1厳守OK"
    
    def calculate_nes_axis2(self, q_q_pct: float, guidance_revision_pct: float = 0, 
                           order_backlog_pct: float = 0, margin_change_bps: float = 0, 
                           ro40: float = 0) -> Tuple[float, int, Dict]:
        """②長期EV勾配（NES）の計算（変更不可）"""
        # Margin_term
        if margin_change_bps >= 50:
            margin_term = 1  # GM改善≥+50bps=+1
        elif margin_change_bps <= -50:
            margin_term = -1  # 悪化≤−50bps=−1
        else:
            margin_term = 0  # ±50bps=0
        
        # Health_term（Ro40）
        if ro40 >= 40:
            health_term = 1  # Ro40≥40→+1
        elif ro40 >= 30:
            health_term = 0  # 30–40→0
        else:
            health_term = -1  # <30→−1
        
        # NES計算（変更不可）
        nes = (0.5 * q_q_pct + 
               0.3 * guidance_revision_pct + 
               0.2 * order_backlog_pct + 
               margin_term + 
               health_term)
        
        # ★換算
        stars = 1
        for (min_val, max_val), star in self.nes_thresholds.items():
            if min_val <= nes < max_val:
                stars = star
                break
        
        return nes, stars, {
            "q_q_component": 0.5 * q_q_pct,
            "guidance_component": 0.3 * guidance_revision_pct,
            "order_component": 0.2 * order_backlog_pct,
            "margin_term": margin_term,
            "health_term": health_term,
            "nes": nes,
            "stars": stars
        }
    
    def calculate_step1_axis3(self, ev_s_actual: float, ev_s_peer_median: float, 
                             g_fwd: float, opm_fwd: float) -> Dict:
        """③Step-1：EV/S_fair_base = max(ピア中央値, rDCF帯) → Disc% → 色/Vmult決定"""
        # rDCFライトの帯
        if g_fwd >= 25 and opm_fwd >= 0:
            ev_s_fair_rdcf = 10.0  # g_fwd≥25% かつ OPM_fwd≥0%
        elif (g_fwd >= 10 and g_fwd < 25) or (opm_fwd >= -5 and opm_fwd < 0):
            ev_s_fair_rdcf = 8.0   # いずれか中間（10–25% or −5〜0%）
        else:
            ev_s_fair_rdcf = 6.0   # g_fwd<10% or OPM_fwd≤−5%
        
        # EV/S_fair_base = max(ピア中央値, rDCF帯)
        ev_s_fair_base = max(ev_s_peer_median, ev_s_fair_rdcf)
        
        # Disc% = (EV/S_fair_base − EV/S_actual) / EV/S_fair_base
        if ev_s_fair_base == 0:
            disc_pct = 0.0
        else:
            disc_pct = (ev_s_fair_base - ev_s_actual) / ev_s_fair_base
        
        # 色判定
        abs_disc = abs(disc_pct)
        if abs_disc <= 0.10:
            color = "Green"    # |Disc%| ≤ 10%
        elif abs_disc <= 0.25:
            color = "Amber"    # 10% < |Disc%| ≤ 25%
        else:
            color = "Red"      # |Disc%| > 25%
        
        # Vmult
        vmult = self.vmult.get(color, 0.90)
        
        return {
            "ev_s_actual": ev_s_actual,
            "ev_s_peer_median": ev_s_peer_median,
            "ev_s_fair_rdcf": ev_s_fair_rdcf,
            "ev_s_fair_base": ev_s_fair_base,
            "disc_pct": disc_pct,
            "color": color,
            "vmult": vmult
        }
    
    def calculate_step2_axis3(self, step1_result: Dict, g_fwd: float, g_peer_median: float, 
                             evidence: str) -> Dict:
        """③Step-2：Δg と 認知フラグ(+/−) で Verdict（色は変えない）"""
        # 期待成長の相対差
        delta_g = g_fwd - g_peer_median
        
        # 認知フラグ（±）
        evidence_lower = evidence.lower()
        positive_count = sum(1 for flag in self.positive_flags if flag in evidence_lower)
        negative_count = sum(1 for flag in self.negative_flags if flag in evidence_lower)
        
        # Verdict判定
        disc_pct = step1_result["disc_pct"]
        
        if disc_pct > 0.10:  # 割安
            if delta_g >= 10 or positive_count >= 2:
                verdict = "Underpriced / 不適正（割安すぎ）"
            elif abs(delta_g) < 10 and abs(positive_count - negative_count) <= 1:
                verdict = "Underpriced / ほぼ適正"
            else:
                verdict = "Underpriced / ほぼ適正"
        
        elif disc_pct < -0.10:  # 割高
            if delta_g <= -10 or negative_count >= 2:
                verdict = "Overpriced / 不適正（割高すぎ）"
            elif abs(delta_g) < 10 and abs(positive_count - negative_count) <= 1:
                verdict = "Overpriced / ほぼ適正"
            else:
                verdict = "Overpriced / ほぼ適正"
        
        else:  # 中立
            verdict = "中立"
        
        return {
            "delta_g": delta_g,
            "positive_flags": positive_count,
            "negative_flags": negative_count,
            "verdict": verdict
        }
    
    def run_lint_strict(self, axis1_data: Dict, axis2_data: Dict, axis3_data: Dict) -> Tuple[bool, List[str]]:
        """Lintで止める：③にRo40が出たらFAIL／Step-1/2以外の項目が混入してもFAIL"""
        errors = []
        
        # 軸名固定チェック
        for axis, data in [("axis1", axis1_data), ("axis2", axis2_data), ("axis3", axis3_data)]:
            axis_name = data.get("axis_name", "")
            expected_name = self.axis_names.get(axis, "")
            if axis_name != expected_name:
                errors.append(f"軸名固定違反: {axis}の軸名が{expected_name}でない")
        
        # T1厳守チェック
        for axis, data in [("axis1", axis1_data), ("axis2", axis2_data), ("axis3", axis3_data)]:
            evidence = data.get("evidence", "")
            t1_pass, t1_msg = self.validate_t1_strict(evidence)
            if not t1_pass:
                errors.append(f"T1厳守違反: {axis}の{t1_msg}")
        
        # ②の式固定チェック
        axis2_formula = axis2_data.get("formula", "")
        if axis2_formula != self.nes_formula:
            errors.append(f"②の式固定違反: NES式が{self.nes_formula}でない")
        
        # ③にRo40が出たらFAIL
        axis3_evidence = axis3_data.get("evidence", "").lower()
        if "ro40" in axis3_evidence or "ro 40" in axis3_evidence:
            errors.append("③にRo40が混入（Ro40は②のみ）")
        
        # ③Step-1/2以外の項目が混入してもFAIL
        forbidden_terms = ["ro40", "ro 40", "margin", "opm", "growth", "成長", "マージン", "roic", "wacc"]
        for term in forbidden_terms:
            if term in axis3_evidence:
                errors.append(f"③Step-1/2以外の項目混入: {term}が混入")
        
        return len(errors) == 0, errors
    
    def get_axis1_display(self, evidence: str, score: int, confidence: float) -> str:
        """①長期EV確度の表示"""
        return f"""
①長期EV確度:
証拠: {evidence}
スコア: ★{score}/5
確信度: {confidence:.2f}
要素: 流動性・負債・希薄化・CapEx・運転資本回転・大型契約の有無（すべてT1）
"""
    
    def get_axis2_display(self, q_q_pct: float, guidance_revision_pct: float = 0, 
                         order_backlog_pct: float = 0, margin_change_bps: float = 0, 
                         ro40: float = 0) -> str:
        """②長期EV勾配の表示"""
        nes, stars, details = self.calculate_nes_axis2(q_q_pct, guidance_revision_pct, 
                                                     order_backlog_pct, margin_change_bps, ro40)
        
        return f"""
②長期EV勾配:
式: {self.nes_formula}
入力: q/q={q_q_pct:.2f}%, 改定%={guidance_revision_pct:.2f}%, 受注%={order_backlog_pct:.2f}%, Margin_change={margin_change_bps:.1f}bps, Ro40={ro40:.1f}
計算: NES = 0.5×{q_q_pct:.2f} + 0.3×{guidance_revision_pct:.2f} + 0.2×{order_backlog_pct:.2f} + {details['margin_term']} + {details['health_term']} = {nes:.2f}
結果: NES={nes:.2f} → ★{stars}

Health_term条件（Ro40）:
- Ro40≥40→+1
- 30–40→0
- <30→−1
"""
    
    def get_axis3_display(self, ev_s_actual: float, ev_s_peer_median: float, 
                         g_fwd: float, opm_fwd: float, g_peer_median: float, 
                         evidence: str) -> str:
        """③バリュエーション＋認知ギャップの表示"""
        # Step-1
        step1_result = self.calculate_step1_axis3(ev_s_actual, ev_s_peer_median, g_fwd, opm_fwd)
        
        # Step-2
        step2_result = self.calculate_step2_axis3(step1_result, g_fwd, g_peer_median, evidence)
        
        return f"""
③バリュエーション＋認知ギャップ:

[Step-1] EV/S_actual = {step1_result['ev_s_actual']:.1f}×
        EV/S_peer_median = {step1_result['ev_s_peer_median']:.1f}×, EV/S_fair_rDCF = {step1_result['ev_s_fair_rdcf']:.1f}× → EV/S_fair_base = {step1_result['ev_s_fair_base']:.1f}×
        Disc% = {step1_result['disc_pct']:.1f}%
        色 = {step1_result['color']}（Vmult={step1_result['vmult']:.2f}）

[Step-2] 期待成長Δg = {step2_result['delta_g']:.1f}pp, 認知フラグ [+{step2_result['positive_flags']} / −{step2_result['negative_flags']}]
        Verdict = {step2_result['verdict']}
"""
    
    def get_contract_summary(self) -> str:
        """運用契約 v1.0の要約"""
        return f"""
=== 運用契約 v1.0（過実装なし） ===

軸名固定:
- ①長期EV確度
- ②長期EV勾配  
- ③バリュエーション＋認知ギャップ

T1厳守:
- 逐語≤25語＋#:~:text=
- 欠測はn/a（推測で埋めない）

②の式（変更不可）:
{self.nes_formula}

③の二段:
- Step-1: EV/S_fair_base = max(ピア中央値, rDCF帯) → Disc% → 色/Vmult決定
- Step-2: Δg と 認知フラグ(+/−) で Verdict（色は変えない）

Lintで止める:
- ③にRo40が出たらFAIL
- Step-1/2以外の項目が混入してもFAIL
"""

def main():
    """テスト実行"""
    s3 = S3ContractV1()
    
    # ①長期EV確度のテスト
    print("=== ①長期EV確度のテスト ===")
    axis1_display = s3.get_axis1_display(
        "completed the ATM… ~$98M #:~:text=completed%20the%20ATM",
        3, 0.72
    )
    print(axis1_display)
    
    # ②長期EV勾配のテスト
    print("=== ②長期EV勾配のテスト ===")
    axis2_display = s3.get_axis2_display(17.48, 0, 0, 0, 45.0)
    print(axis2_display)
    
    # ③バリュエーション＋認知ギャップのテスト
    print("=== ③バリュエーション＋認知ギャップのテスト ===")
    axis3_display = s3.get_axis3_display(5.0, 5.0, 15.0, 5.0, 12.0, 
                                        "raises guidance, began volume shipments #:~:text=raises%20guidance")
    print(axis3_display)
    
    # Lintで止めるテスト
    print("=== Lintで止めるテスト ===")
    axis1_data = {
        "axis_name": "①長期EV確度",
        "evidence": "completed the ATM… ~$98M #:~:text=completed%20the%20ATM"
    }
    axis2_data = {
        "axis_name": "②長期EV勾配",
        "formula": "NES = 0.5·q/q + 0.3·改定% + 0.2·受注% + Margin_term + Health_term(Ro40)"
    }
    axis3_data = {
        "axis_name": "③バリュエーション＋認知ギャップ",
        "evidence": "ro40=45, margin改善 #:~:text=ro40"  # Ro40混入でエラー
    }
    
    lint_pass, errors = s3.run_lint_strict(axis1_data, axis2_data, axis3_data)
    print(f"Lint結果: {'PASS' if lint_pass else 'FAIL'}")
    if errors:
        print("エラー:", errors)
    
    # 契約要約
    print("=== 運用契約 v1.0の要約 ===")
    contract_summary = s3.get_contract_summary()
    print(contract_summary)

if __name__ == "__main__":
    main()
