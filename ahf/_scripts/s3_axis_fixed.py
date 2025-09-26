#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
S3-Axis-Fixed - ①②③の軸ルールに完全準拠
Ro40は②のみ、③は"ピア×逆DCFの体温計だけ"に統一
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

class S3AxisFixed:
    """①②③の軸ルールに完全準拠したS3システム"""
    
    def __init__(self):
        self.nes_formula = "NES = 0.5·q/q + 0.3·改定% + 0.2·受注% + Margin_term + Health_term(Ro40)"
        self.nes_thresholds = {
            (8, float('inf')): 5,    # NES ≥ +8 → ★5
            (5, 8): 4,               # +5–8 → ★4
            (2, 5): 3,               # +2–5 → ★3
            (0, 2): 2,               # 0–2 → ★2
            (float('-inf'), 0): 1    # <0 → ★1
        }
        self.di_multipliers = {
            "Green": 1.05,
            "Amber": 0.90,
            "Red": 0.75
        }
    
    def calculate_margin_term(self, margin_change_bps: float) -> int:
        """Margin_term計算"""
        if margin_change_bps >= 50:
            return 1  # 改善≥+50bps=+1
        elif margin_change_bps <= -50:
            return -1  # 悪化≤−50bps=−1
        else:
            return 0  # ±50bps=0
    
    def calculate_health_term(self, ro40: float) -> int:
        """Health_term計算（Ro40） - ②のみに限定"""
        if ro40 >= 40:
            return 1  # Ro40≥40→+1
        elif ro40 >= 30:
            return 0  # 30–40→0
        else:
            return -1  # <30→−1
    
    def calculate_nes_axis2(self, q_q_pct: float, guidance_revision_pct: float = 0, 
                           order_backlog_pct: float = 0, margin_change_bps: float = 0, 
                           ro40: float = 0) -> Tuple[float, int, Dict]:
        """②長期EV勾配のNES計算（Ro40はここにのみ影響）"""
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
        
        calculation_details = {
            "q_q_component": 0.5 * q_q_pct,
            "guidance_component": 0.3 * guidance_revision_pct,
            "order_component": 0.2 * order_backlog_pct,
            "margin_term": margin_term,
            "health_term": health_term,
            "nes": nes,
            "stars": stars
        }
        
        return nes, stars, calculation_details
    
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
        """③バリュエーション＋認知ギャップの色判定（体温計：ピア×逆DCFのみ）"""
        # Green：|P|≤10% かつ |R|≤15%
        if abs(pm) <= 0.10 and abs(rdcf) <= 0.15:
            return "Green"
        
        # Amber：それ以外でどちらかが±25%以内
        if abs(pm) <= 0.25 or abs(rdcf) <= 0.25:
            return "Amber"
        
        # Red：P>+25% または R>+25%（割高）、もしくは P<−25% & R<−25%（割安だが成長裏付け不足）
        if (pm > 0.25 or rdcf > 0.25) or (pm < -0.25 and rdcf < -0.25):
            return "Red"
        
        # その他はAmber
        return "Amber"
    
    def calculate_cognitive_gap(self, pm: float, rdcf: float) -> float:
        """認知ギャップの表示：Δ = P − R"""
        return pm - rdcf
    
    def evaluate_axis3_valuation(self, ev_s_actual: float, ev_s_peer_median: float, 
                               ev_s_fair: float) -> Dict:
        """③バリュエーション＋認知ギャップ評価（体温計：ピア×逆DCFのみ）"""
        # PM計算
        pm = self.calculate_peer_multiple(ev_s_actual, ev_s_peer_median)
        
        # rDCF計算
        rdcf = self.calculate_reverse_dcf(ev_s_actual, ev_s_fair)
        
        # 色判定（体温計：ピア×逆DCFのみ）
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
    
    def get_axis2_display(self, q_q_pct: float, guidance_revision_pct: float = 0, 
                         order_backlog_pct: float = 0, margin_change_bps: float = 0, 
                         ro40: float = 0) -> str:
        """②長期EV勾配の表示"""
        nes, stars, details = self.calculate_nes_axis2(q_q_pct, guidance_revision_pct, 
                                                      order_backlog_pct, margin_change_bps, ro40)
        
        return f"""
②長期EV勾配（NES計算）:
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
                         ev_s_fair: float) -> str:
        """③バリュエーション＋認知ギャップの表示"""
        result = self.evaluate_axis3_valuation(ev_s_actual, ev_s_peer_median, ev_s_fair)
        
        return f"""
③バリュエーション＋認知ギャップ（体温計：ピア×逆DCFのみ）:
EV/S_actual: {ev_s_actual:.2f}
EV/S_peer_median: {ev_s_peer_median:.2f}
EV/S_fair: {ev_s_fair:.2f}

PM（Peer Multiple）: {result['pm_pct']:.1f}%
rDCF（逆DCFライト）: {result['rdcf_pct']:.1f}%

色判定: {result['color']}
認知ギャップ（Δ = P − R）: {result['cognitive_gap_pct']:.1f}%
DI倍率: {result['di_multiplier']:.2f}

判定基準（体温計：ピア×逆DCFのみ）:
- Green: |P|≤10% かつ |R|≤15%
- Amber: それ以外でどちらかが±25%以内
- Red: P>+25% または R>+25%（割高）、もしくは P<−25% & R<−25%（割安だが成長裏付け不足）
"""
    
    def get_data_gap_display(self, peer_ev_s_median: str = "n/a", 
                           rdcf_inputs: str = "n/a", price_mode_date: str = "n/a") -> str:
        """data_gap表示（不足はn/aで可視化）"""
        return f"""
data_gap（最小）:
ピアEV/S中央値（光学/トランシーバ）: {peer_ev_s_median}（TTL 7d）
逆DCFライト入力（g_fwd, OPM_fwd, FCF率）: {rdcf_inputs}（TTL 7d）
Price-Mode出典の定点化: {price_mode_date}（次回更新時に併記）
"""
    
    def get_axis_summary(self, axis1_data: Dict, axis2_data: Dict, axis3_data: Dict) -> str:
        """①②③軸の統合要約"""
        return f"""
=== ①②③軸の統合要約 ===

①長期EV確度:
代表KPI: {axis1_data.get('kpi', 'N/A')}
現状スナップ: {axis1_data.get('snapshot', 'N/A')}
★/5: {axis1_data.get('stars', 'N/A')}
確信度: {axis1_data.get('confidence', 'N/A')}
市場織込み: {axis1_data.get('market_pricing', 'N/A')}
Alpha不透明度: {axis1_data.get('alpha_opacity', 'N/A')}
上向/下向: {axis1_data.get('direction', 'N/A')}

②長期EV勾配:
代表KPI: NES計算（Ro40はここにのみ影響）
現状スナップ: {axis2_data.get('snapshot', 'N/A')}
★/5: {axis2_data.get('stars', 'N/A')}
確信度: {axis2_data.get('confidence', 'N/A')}
市場織込み: {axis2_data.get('market_pricing', 'N/A')}
Alpha不透明度: {axis2_data.get('alpha_opacity', 'N/A')}
上向/下向: {axis2_data.get('direction', 'N/A')}

③バリュエーション＋認知ギャップ:
代表KPI: 体温計（ピア×逆DCFのみ）
現状スナップ: {axis3_data.get('snapshot', 'N/A')}
★/5: {axis3_data.get('stars', 'N/A')}
確信度: {axis3_data.get('confidence', 'N/A')}
市場織込み: {axis3_data.get('market_pricing', 'N/A')}
Alpha不透明度: {axis3_data.get('alpha_opacity', 'N/A')}
上向/下向: {axis3_data.get('direction', 'N/A')}
"""

def main():
    """テスト実行"""
    s3 = S3AxisFixed()
    
    # ②長期EV勾配のテスト
    print("=== ②長期EV勾配のテスト ===")
    axis2_display = s3.get_axis2_display(17.48, 0, 0, 0, 45.0)
    print(axis2_display)
    
    # ③バリュエーション＋認知ギャップのテスト
    print("=== ③バリュエーション＋認知ギャップのテスト ===")
    axis3_display = s3.get_axis3_display(5.0, 5.0, 5.0)
    print(axis3_display)
    
    # data_gap表示
    print("=== data_gap表示 ===")
    data_gap_display = s3.get_data_gap_display("n/a", "n/a", "n/a")
    print(data_gap_display)
    
    # 軸統合要約
    print("=== 軸統合要約 ===")
    axis1_data = {
        "kpi": "流動性○（ATM完了）／前受0継続／運転資本は重い",
        "snapshot": "流動性○（ATM完了）／前受0継続／運転資本は重い",
        "stars": 3,
        "confidence": 0.72,
        "market_pricing": "部分織込み",
        "alpha_opacity": "中",
        "direction": "60 / 40"
    }
    
    axis2_data = {
        "snapshot": "NES計算：q/q=17.48%、改定%/受注%=0、Margin=0、Health（Ro40≥40）=+1 ⇒ NES=9.74→★5",
        "stars": 5,
        "confidence": 0.80,
        "market_pricing": "一部未織込み",
        "alpha_opacity": "中",
        "direction": "70 / 30"
    }
    
    axis3_data = {
        "snapshot": "P（PM）＝n/a（ピアEV/S中央値 未確定）／R（rDCF）＝n/a（g_fwd・OPM_fwd・FCF率 未確定）／色= n/a",
        "stars": "n/a",
        "confidence": 0.55,
        "market_pricing": "過少評価の可能性",
        "alpha_opacity": "中",
        "direction": "65 / 35"
    }
    
    axis_summary = s3.get_axis_summary(axis1_data, axis2_data, axis3_data)
    print(axis_summary)

if __name__ == "__main__":
    main()
