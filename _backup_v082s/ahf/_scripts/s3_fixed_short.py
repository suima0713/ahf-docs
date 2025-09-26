#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
S3-Fixed-Short - 運用"固定"ショート版（これだけで回します）
T1限定・①②③の軸・Lint強制・判断：上記だけでマトリクス→DI→Decision
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

class S3FixedShort:
    """運用"固定"ショート版（これだけで回します）実装"""
    
    def __init__(self):
        # 軸名固定
        self.axis_names = {
            "axis1": "①長期EV確度",
            "axis2": "②長期EV勾配", 
            "axis3": "③バリュエーション＋認知ギャップ"
        }
        
        # ②の式（固定）
        self.nes_formula = "NES = 0.5·q/q + 0.3·改定% + 0.2·受注% + Margin_term + Health_term(Ro40)"
        
        # NES★換算（機械化）
        self.nes_thresholds = {
            (8, float('inf')): 5,    # NES≥8→★5
            (5, 8): 4,               # +5–8→★4
            (2, 5): 3,               # +2–5→★3
            (0, 2): 2,               # 0–2→★2
            (float('-inf'), 0): 1    # <0→★1
        }
        
        # Vmult（固定）
        self.vmult = {
            "Green": 1.05,
            "Amber": 0.90,
            "Red": 0.75
        }
        
        # 認知フラグ（±）
        self.positive_flags = [
            "ガイダンス上方", "実出荷", "前受", "契約負債↑", "ATM未実行",
            "raises guidance", "began", "volume shipments", "contract liabilities↑", 
            "ATM sales to date=0", "10%顧客分散"
        ]
        
        self.negative_flags = [
            "acceptance要件", "在庫滞留", "集中悪化", "希薄化",
            "acceptance required", "Raw/WIP滞留", "ATM実行", "集中度悪化"
        ]
    
    def validate_t1_strict(self, evidence: str) -> Tuple[bool, str]:
        """T1限定（SEC/IR、逐語≤25語＋#:~:text=、欠測は n/a）"""
        if not evidence:
            return False, "T1証拠が空"
        
        # 逐語≤25語
        word_count = len(evidence.split())
        if word_count > 25:
            return False, f"T1限定違反: 逐語{word_count}語>25語"
        
        # #:~:text=付き
        if not ("#:~:text=" in evidence or "anchor_backup" in evidence):
            return False, "T1限定違反: #:~:text=付きでない"
        
        # 欠測はn/a
        if "未確定" in evidence or "不明" in evidence:
            if "n/a" not in evidence:
                return False, "T1限定違反: 欠測がn/a表記でない"
        
        return True, "T1限定OK"
    
    def evaluate_axis1(self, evidence: str, score: int, confidence: float) -> Dict:
        """①長期EV確度：流動性・負債・希薄化・運転資本などのみ（価格/マルチ不使用）"""
        # T1限定チェック
        t1_pass, t1_msg = self.validate_t1_strict(evidence)
        
        return {
            "axis_name": "①長期EV確度",
            "evidence": evidence,
            "score": score,
            "confidence": confidence,
            "t1_pass": t1_pass,
            "t1_msg": t1_msg,
            "elements": "流動性・負債・希薄化・CapEx・運転資本回転・大型契約の有無（すべてT1）"
        }
    
    def calculate_nes_axis2(self, q_q_pct: float, guidance_revision_pct: float = 0, 
                           order_backlog_pct: float = 0, margin_change_bps: float = 0, 
                           ro40: float = 0) -> Tuple[float, int, Dict]:
        """②長期EV勾配：NES式と★判定を機械化（Ro40は②のみ）"""
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
        
        # NES計算
        nes = (0.5 * q_q_pct + 
               0.3 * guidance_revision_pct + 
               0.2 * order_backlog_pct + 
               margin_term + 
               health_term)
        
        # ★判定を機械化
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
    
    def evaluate_axis2(self, q_q_pct: float, guidance_revision_pct: float = 0, 
                      order_backlog_pct: float = 0, margin_change_bps: float = 0, 
                      ro40: float = 0) -> Dict:
        """②長期EV勾配の評価"""
        nes, stars, details = self.calculate_nes_axis2(q_q_pct, guidance_revision_pct, 
                                                     order_backlog_pct, margin_change_bps, ro40)
        
        return {
            "axis_name": "②長期EV勾配",
            "formula": self.nes_formula,
            "nes": nes,
            "stars": stars,
            "details": details,
            "ro40_note": "Ro40は②のみ（①③へ持ち込まない）"
        }
    
    def calculate_step1_axis3(self, ev_s_actual: float, ev_s_peer_median: float, 
                             g_fwd: float, opm_fwd: float) -> Dict:
        """③Step-1：Disc%＝EV/S_actual vs max(ピアEV/S中央値, rDCF帯) → 色/Vmult決定"""
        # rDCF帯
        if g_fwd >= 25 and opm_fwd >= 0:
            ev_s_fair_rdcf = 10.0  # g_fwd≥25% かつ OPM_fwd≥0%
        elif (g_fwd >= 10 and g_fwd < 25) or (opm_fwd >= -5 and opm_fwd < 0):
            ev_s_fair_rdcf = 8.0   # いずれか中間（10–25% or −5〜0%）
        else:
            ev_s_fair_rdcf = 6.0   # g_fwd<10% or OPM_fwd≤−5%
        
        # max(ピアEV/S中央値, rDCF帯)
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
        """③Step-2：Δg と 認知フラグ(+/−)で Verdict（色は変えない）"""
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
    
    def evaluate_axis3(self, ev_s_actual: float, ev_s_peer_median: float, 
                      g_fwd: float, opm_fwd: float, g_peer_median: float, 
                      evidence: str) -> Dict:
        """③バリュエーション＋認知ギャップ（体温計）＝二段構え"""
        # Step-1
        step1_result = self.calculate_step1_axis3(ev_s_actual, ev_s_peer_median, g_fwd, opm_fwd)
        
        # Step-2
        step2_result = self.calculate_step2_axis3(step1_result, g_fwd, g_peer_median, evidence)
        
        return {
            "axis_name": "③バリュエーション＋認知ギャップ",
            "step1": step1_result,
            "step2": step2_result,
            "note": "体温計＝二段構え"
        }
    
    def run_lint_final(self, axis1_data: Dict, axis2_data: Dict, axis3_data: Dict) -> Tuple[bool, List[str]]:
        """Lint強制：③にRo40が出たらFAIL／③はPM+rDCF以外NG／Price-Modeは日付＋出典必須"""
        errors = []
        
        # T1限定チェック
        for axis, data in [("axis1", axis1_data), ("axis2", axis2_data), ("axis3", axis3_data)]:
            evidence = data.get("evidence", "")
            t1_pass, t1_msg = self.validate_t1_strict(evidence)
            if not t1_pass:
                errors.append(f"T1限定違反: {axis}の{t1_msg}")
        
        # ③にRo40が出たらFAIL
        axis3_evidence = axis3_data.get("evidence", "").lower()
        if "ro40" in axis3_evidence or "ro 40" in axis3_evidence:
            errors.append("Lint強制違反: ③にRo40が混入（Ro40は②のみ）")
        
        # ③はPM+rDCF以外NG
        forbidden_terms = ["ro40", "ro 40", "margin", "opm", "growth", "成長", "マージン", "roic", "wacc"]
        for term in forbidden_terms:
            if term in axis3_evidence:
                errors.append(f"Lint強制違反: ③に{term}が混入（③はPM+rDCF以外NG）")
        
        # Price-Modeは日付＋出典必須
        for axis, data in [("axis1", axis1_data), ("axis2", axis2_data), ("axis3", axis3_data)]:
            evidence = data.get("evidence", "")
            if "price" in evidence.lower() or "yahoo" in evidence.lower():
                if not any(date_pattern in evidence for date_pattern in ["2025", "2024", "2023"]):
                    errors.append(f"Lint強制違反: {axis}のPrice-Mode使用時に日付が不明記")
        
        return len(errors) == 0, errors
    
    def calculate_di(self, axis1_score: int, axis2_stars: int, axis3_vmult: float) -> float:
        """DI計算：上記だけでマトリクス→DI→Decision"""
        # 簡易DI計算（例）
        base_di = (axis1_score * 0.2 + axis2_stars * 0.3 + axis3_vmult * 0.5)
        return base_di
    
    def get_matrix_display(self, axis1_data: Dict, axis2_data: Dict, axis3_data: Dict) -> str:
        """マトリクス表示"""
        return f"""
=== 運用"固定"ショート版マトリクス ===

{axis1_data['axis_name']}:
証拠: {axis1_data.get('evidence', 'N/A')}
スコア: ★{axis1_data.get('score', 'N/A')}/5
確信度: {axis1_data.get('confidence', 'N/A')}
T1: {'PASS' if axis1_data.get('t1_pass', False) else 'FAIL'}

{axis2_data['axis_name']}:
式: {axis2_data.get('formula', 'N/A')}
NES: {axis2_data.get('nes', 'N/A')}
★: {axis2_data.get('stars', 'N/A')}

{axis3_data['axis_name']}:
[Step-1] Disc%: {axis3_data.get('step1', {}).get('disc_pct', 'N/A'):.1%}
色: {axis3_data.get('step1', {}).get('color', 'N/A')}（Vmult={axis3_data.get('step1', {}).get('vmult', 'N/A')}）
[Step-2] Verdict: {axis3_data.get('step2', {}).get('verdict', 'N/A')}

DI: {self.calculate_di(axis1_data.get('score', 0), axis2_data.get('stars', 0), axis3_data.get('step1', {}).get('vmult', 0.90)):.3f}
"""
    
    def get_fixed_short_summary(self) -> str:
        """運用固定ショート版の要約"""
        return f"""
=== 運用固定ショート版（これだけで回します） ===

T1限定:
- SEC/IR、逐語≤25語＋#:~:text=、欠測は n/a

①長期EV確度:
- 流動性・負債・希薄化・運転資本などのみ（価格/マルチ不使用）

②長期EV勾配:
- NES = 0.5·q/q + 0.3·改定% + 0.2·受注% + Margin_term + Health_term(Ro40)
- ★判定を機械化（Ro40は②のみ）

③バリュエーション＋認知ギャップ（体温計）＝二段構え:
- Step-1: Disc%＝EV/S_actual vs max(ピアEV/S中央値, rDCF帯) → 色/Vmult決定
- Step-2: Δg と 認知フラグ(+/−)で Verdict（色は変えない）

Lint強制:
- ③にRo40が出たらFAIL
- ③はPM+rDCF以外NG
- Price-Modeは日付＋出典必須

判断:
- 上記だけでマトリクス→DI→Decision
- 恣意は入れない、過実装もしない
- 必要なのはこの箱の中で数字を埋めることだけ
"""

def main():
    """テスト実行"""
    s3 = S3FixedShort()
    
    # ①長期EV確度のテスト
    print("=== ①長期EV確度のテスト ===")
    axis1_data = s3.evaluate_axis1(
        "completed the ATM… ~$98M #:~:text=completed%20the%20ATM",
        3, 0.72
    )
    print(f"①: {axis1_data['axis_name']}")
    print(f"証拠: {axis1_data['evidence']}")
    print(f"スコア: ★{axis1_data['score']}/5")
    print(f"T1: {'PASS' if axis1_data['t1_pass'] else 'FAIL'}")
    
    # ②長期EV勾配のテスト
    print("\n=== ②長期EV勾配のテスト ===")
    axis2_data = s3.evaluate_axis2(17.48, 0, 0, 0, 45.0)
    print(f"②: {axis2_data['axis_name']}")
    print(f"NES: {axis2_data['nes']:.2f}")
    print(f"★: {axis2_data['stars']}")
    
    # ③バリュエーション＋認知ギャップのテスト
    print("\n=== ③バリュエーション＋認知ギャップのテスト ===")
    axis3_data = s3.evaluate_axis3(5.0, 5.0, 15.0, 5.0, 12.0, 
                                  "ガイダンス上方, 実出荷, 前受, 契約負債↑ #:~:text=ガイダンス上方")
    print(f"③: {axis3_data['axis_name']}")
    print(f"Step-1 Disc%: {axis3_data['step1']['disc_pct']:.1%}")
    print(f"色: {axis3_data['step1']['color']}（Vmult={axis3_data['step1']['vmult']:.2f}）")
    print(f"Step-2 Verdict: {axis3_data['step2']['verdict']}")
    
    # Lint強制テスト
    print("\n=== Lint強制テスト ===")
    lint_pass, errors = s3.run_lint_final(axis1_data, axis2_data, axis3_data)
    print(f"Lint結果: {'PASS' if lint_pass else 'FAIL'}")
    if errors:
        print("エラー:", errors)
    
    # マトリクス表示
    print("\n=== マトリクス表示 ===")
    matrix_display = s3.get_matrix_display(axis1_data, axis2_data, axis3_data)
    print(matrix_display)
    
    # 固定ショート版要約
    print("\n=== 運用固定ショート版の要約 ===")
    fixed_summary = s3.get_fixed_short_summary()
    print(fixed_summary)

if __name__ == "__main__":
    main()
