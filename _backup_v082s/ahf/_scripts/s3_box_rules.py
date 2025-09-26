#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
S3-Box Rules v1.0（最小・強制）
①②③の軸ルールに完全準拠（過実装排除、守るべきことだけを固定）
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

class S3BoxRules:
    """S3-Box Rules v1.0（最小・強制）実装"""
    
    def __init__(self):
        # 定型テーブルの見出し名（厳守）
        self.axis_names = {
            "axis1": "①長期EV確度",
            "axis2": "②長期EV勾配", 
            "axis3": "③バリュエーション＋認知ギャップ"
        }
        
        # NES式（固定）
        self.nes_formula = "NES = 0.5·q/q + 0.3·改定% + 0.2·受注% + Margin_term + Health_term"
        
        # NES★換算（固定）
        self.nes_thresholds = {
            (8, float('inf')): 5,    # NES≥8→★5
            (5, 8): 4,               # +5–8→★4
            (2, 5): 3,               # +2–5→★3
            (0, 2): 2,               # 0–2→★2
            (float('-inf'), 0): 1    # <0→★1
        }
        
        # DI倍率（変更不可）
        self.di_multipliers = {
            "Green": 1.05,
            "Amber": 0.90,
            "Red": 0.75
        }
    
    def validate_t1_evidence(self, evidence: str) -> Tuple[bool, str]:
        """T1限定チェック：SEC/IRのみ、逐語≤25語＋#:~:text=必須"""
        if not evidence:
            return False, "T1証拠が空"
        
        # 逐語≤25語
        word_count = len(evidence.split())
        if word_count > 25:
            return False, f"L1: 逐語{word_count}語>25語"
        
        # #:~:text=付き（PDFは anchor_backup）
        if not ("#:~:text=" in evidence or "anchor_backup" in evidence):
            return False, "L2: #:~:text=付きでない（PDFは anchor_backup）"
        
        return True, "T1証拠OK"
    
    def calculate_ro40(self, growth_pct: float, gaap_opm_pct: float) -> float:
        """Ro40計算：Ro40 = 成長% + GAAP OPM%"""
        return growth_pct + gaap_opm_pct
    
    def calculate_margin_term(self, margin_change_bps: float) -> int:
        """Margin_term計算"""
        if margin_change_bps >= 50:
            return 1  # GM改善≥+50bps=+1
        elif margin_change_bps <= -50:
            return -1  # 悪化≤−50bps=−1
        else:
            return 0  # ±50bps=0
    
    def calculate_health_term(self, ro40: float) -> int:
        """Health_term計算（Ro40）"""
        if ro40 >= 40:
            return 1  # Ro40≥40→+1
        elif ro40 >= 30:
            return 0  # 30–40→0
        else:
            return -1  # <30→−1
    
    def calculate_nes_axis2(self, q_q_pct: float, guidance_revision_pct: float = 0, 
                           order_backlog_pct: float = 0, margin_change_bps: float = 0, 
                           ro40: float = 0) -> Tuple[float, int, Dict]:
        """②長期EV勾配（NES）の計算"""
        margin_term = self.calculate_margin_term(margin_change_bps)
        health_term = self.calculate_health_term(ro40)
        
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
    
    def calculate_fair_ev_s(self, g_fwd: float, opm_fwd: float) -> float:
        """フェアEV/S計算（簡易3帯）"""
        if g_fwd >= 25 and opm_fwd >= 0:
            return 10.0  # g_fwd≥25% かつ OPM_fwd≥0%
        elif (g_fwd >= 10 and g_fwd < 25) or (opm_fwd >= -5 and opm_fwd < 0):
            return 8.0   # いずれか中間：10–25% or −5〜0%
        else:
            return 6.0   # g_fwd<10% or OPM_fwd≤−5%
    
    def calculate_peer_multiple(self, ev_s_actual: float, ev_s_peer_median: float) -> float:
        """PM（Peer Multiple）計算"""
        if ev_s_peer_median == 0:
            return 0.0
        return (ev_s_actual / ev_s_peer_median) - 1
    
    def calculate_reverse_dcf(self, ev_s_actual: float, ev_s_fair: float) -> float:
        """rDCF（逆DCFライト）計算"""
        if ev_s_fair == 0:
            return 0.0
        return (ev_s_actual / ev_s_fair) - 1
    
    def determine_color_axis3(self, pm: float, rdcf: float) -> str:
        """③バリュエーション＋認知ギャップの色判定（機械）"""
        # Green：|P|≤10% かつ |R|≤15%
        if abs(pm) <= 0.10 and abs(rdcf) <= 0.15:
            return "Green"
        
        # Amber：それ以外で、どちらかが±25%以内
        if abs(pm) <= 0.25 or abs(rdcf) <= 0.25:
            return "Amber"
        
        # Red：P>+25% または R>+25%（割高）／P<−25% 且つ R<−25%（割安だが成長裏付け不足）
        if (pm > 0.25 or rdcf > 0.25) or (pm < -0.25 and rdcf < -0.25):
            return "Red"
        
        return "Amber"
    
    def calculate_cognitive_gap(self, pm: float, rdcf: float) -> float:
        """認知ギャップ：Δ = P − R"""
        return pm - rdcf
    
    def evaluate_axis3_valuation(self, ev_s_actual: float, ev_s_peer_median: float, 
                                g_fwd: float, opm_fwd: float) -> Dict:
        """③バリュエーション＋認知ギャップ評価（体温計のみ）"""
        # フェアEV/S計算
        ev_s_fair = self.calculate_fair_ev_s(g_fwd, opm_fwd)
        
        # PM計算
        pm = self.calculate_peer_multiple(ev_s_actual, ev_s_peer_median)
        
        # rDCF計算
        rdcf = self.calculate_reverse_dcf(ev_s_actual, ev_s_fair)
        
        # 色判定
        color = self.determine_color_axis3(pm, rdcf)
        
        # 認知ギャップ
        cognitive_gap = self.calculate_cognitive_gap(pm, rdcf)
        
        # DI倍率
        di_multiplier = self.di_multipliers.get(color, 0.90)
        
        return {
            "ev_s_actual": ev_s_actual,
            "ev_s_peer_median": ev_s_peer_median,
            "ev_s_fair": ev_s_fair,
            "pm": pm,
            "rdcf": rdcf,
            "color": color,
            "cognitive_gap": cognitive_gap,
            "di_multiplier": di_multiplier,
            "pm_pct": pm * 100,
            "rdcf_pct": rdcf * 100,
            "cognitive_gap_pct": cognitive_gap * 100
        }
    
    def run_s3_lint_strict(self, axis1_data: Dict, axis2_data: Dict, axis3_data: Dict) -> Tuple[bool, List[str]]:
        """S3-Lint（強制チェック）"""
        errors = []
        
        # L1: 逐語≤25語
        for axis, data in [("axis1", axis1_data), ("axis2", axis2_data), ("axis3", axis3_data)]:
            evidence = data.get("evidence", "")
            word_count = len(evidence.split())
            if word_count > 25:
                errors.append(f"L1: {axis}の逐語{word_count}語>25語")
        
        # L2: #:~:text=付き
        for axis, data in [("axis1", axis1_data), ("axis2", axis2_data), ("axis3", axis3_data)]:
            evidence = data.get("evidence", "")
            if not ("#:~:text=" in evidence or "anchor_backup" in evidence):
                errors.append(f"L2: {axis}の#:~:text=付きでない")
        
        # L3: ②の式に余計な項目が無い
        axis2_formula = axis2_data.get("formula", "")
        if axis2_formula and "NES" not in axis2_formula:
            errors.append("L3: ②の式に余計な項目がある")
        
        # L4: Ro40は②のみ（①③内に出現したらFAIL）
        for axis, data in [("axis1", axis1_data), ("axis3", axis3_data)]:
            evidence = data.get("evidence", "").lower()
            if "ro40" in evidence or "ro 40" in evidence:
                errors.append(f"L4: {axis}にRo40が混入")
        
        # L5: ③はPMとrDCFのみ（他指標が混入したらFAIL）
        axis3_evidence = axis3_data.get("evidence", "").lower()
        forbidden_terms = ["ro40", "ro 40", "margin", "opm", "growth", "成長", "マージン"]
        for term in forbidden_terms:
            if term in axis3_evidence:
                errors.append(f"L5: ③に{term}が混入（PMとrDCFのみ）")
        
        # L6: Price-Mode使用時は日付＋出典名明記
        for axis, data in [("axis1", axis1_data), ("axis2", axis2_data), ("axis3", axis3_data)]:
            evidence = data.get("evidence", "")
            if "price" in evidence.lower() or "yahoo" in evidence.lower():
                if not any(date_pattern in evidence for date_pattern in ["2025", "2024", "2023"]):
                    errors.append(f"L6: {axis}のPrice-Mode使用時に日付が不明記")
        
        # L7: 欠測はn/a表記
        for axis, data in [("axis1", axis1_data), ("axis2", axis2_data), ("axis3", axis3_data)]:
            evidence = data.get("evidence", "")
            if "未確定" in evidence or "不明" in evidence:
                if "n/a" not in evidence:
                    errors.append(f"L7: {axis}の欠測がn/a表記でない")
        
        return len(errors) == 0, errors
    
    def get_axis1_display(self, evidence: str, score: int, confidence: float) -> str:
        """①長期EV確度（LEC）の表示"""
        return f"""
①長期EV確度（LEC）:
証拠: {evidence}
スコア: ★{score}/5
確信度: {confidence:.2f}
要素: 流動性・負債・希薄化・CapEx・運転資本回転・大型契約の有無（すべてT1）
"""
    
    def get_axis2_display(self, q_q_pct: float, guidance_revision_pct: float = 0, 
                         order_backlog_pct: float = 0, margin_change_bps: float = 0, 
                         ro40: float = 0) -> str:
        """②長期EV勾配（NES）の表示"""
        nes, stars, details = self.calculate_nes_axis2(q_q_pct, guidance_revision_pct, 
                                                      order_backlog_pct, margin_change_bps, ro40)
        
        return f"""
②長期EV勾配（NES）:
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
                         g_fwd: float, opm_fwd: float) -> str:
        """③バリュエーション＋認知ギャップ（体温計のみ）の表示"""
        result = self.evaluate_axis3_valuation(ev_s_actual, ev_s_peer_median, g_fwd, opm_fwd)
        
        return f"""
③バリュエーション＋認知ギャップ（体温計のみ）:
EV/S_actual: {ev_s_actual:.2f}
EV/S_peer_median: {ev_s_peer_median:.2f}
EV/S_fair: {result['ev_s_fair']:.2f}

PM（Peer Multiple）: {result['pm_pct']:.1f}%
rDCF（逆DCFライト）: {result['rdcf_pct']:.1f}%

色判定: {result['color']}
認知ギャップ（Δ = P − R）: {result['cognitive_gap_pct']:.1f}%
DI倍率: {result['di_multiplier']:.2f}

判定基準（体温計のみ）:
- Green: |P|≤10% かつ |R|≤15%
- Amber: それ以外で、どちらかが±25%以内
- Red: P>+25% または R>+25%（割高）／P<−25% 且つ R<−25%（割安だが成長裏付け不足）
"""
    
    def get_data_gap_display(self, missing_data: Dict) -> str:
        """data_gap表示（欠測はn/aで可視化）"""
        return f"""
data_gap（最小）:
{missing_data.get('peer_ev_s', 'n/a')}（TTL 7d）
{missing_data.get('rdcf_inputs', 'n/a')}（TTL 7d）
{missing_data.get('price_mode', 'n/a')}（次回更新時に併記）
"""

def main():
    """テスト実行"""
    s3 = S3BoxRules()
    
    # ①長期EV確度のテスト
    print("=== ①長期EV確度（LEC）のテスト ===")
    axis1_display = s3.get_axis1_display(
        "completed the ATM… ~$98M #:~:text=completed%20the%20ATM",
        3, 0.72
    )
    print(axis1_display)
    
    # ②長期EV勾配のテスト
    print("=== ②長期EV勾配（NES）のテスト ===")
    axis2_display = s3.get_axis2_display(17.48, 0, 0, 0, 45.0)
    print(axis2_display)
    
    # ③バリュエーション＋認知ギャップのテスト
    print("=== ③バリュエーション＋認知ギャップ（体温計のみ）のテスト ===")
    axis3_display = s3.get_axis3_display(5.0, 5.0, 15.0, 5.0)
    print(axis3_display)
    
    # S3-Lint（強制チェック）のテスト
    print("=== S3-Lint（強制チェック）のテスト ===")
    axis1_data = {
        "evidence": "completed the ATM… ~$98M #:~:text=completed%20the%20ATM",
        "score": 3
    }
    axis2_data = {
        "evidence": "Revenue $115–$127M #:~:text=Revenue%20in%20the%20range",
        "formula": "NES = 0.5·q/q + 0.3·改定% + 0.2·受注% + Margin_term + Health_term"
    }
    axis3_data = {
        "evidence": "EV/S_actual=5.0, EV/S_peer=5.0 #:~:text=EV%2FS"
    }
    
    lint_pass, errors = s3.run_s3_lint_strict(axis1_data, axis2_data, axis3_data)
    print(f"Lint結果: {'PASS' if lint_pass else 'FAIL'}")
    if errors:
        print("エラー:", errors)
    
    # data_gap表示
    print("=== data_gap表示 ===")
    missing_data = {
        "peer_ev_s": "ピアEV/S中央値（光学/トランシーバ）: n/a",
        "rdcf_inputs": "逆DCFライト入力（g_fwd, OPM_fwd, FCF率）: n/a",
        "price_mode": "Price-Mode出典の定点化: n/a"
    }
    data_gap_display = s3.get_data_gap_display(missing_data)
    print(data_gap_display)

if __name__ == "__main__":
    main()
