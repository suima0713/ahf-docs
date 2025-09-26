#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Valuation System - ③バリュエーション＋認知ギャップの機械判定システム
PM+rDCFによる色判定とDI倍率適用
"""

from typing import Dict, Tuple, Optional
import math

class ValuationSystem:
    """③バリュエーション＋認知ギャップの機械判定システム"""
    
    def __init__(self):
        self.di_multipliers = {
            "Green": 1.05,
            "Amber": 0.90,
            "Red": 0.75
        }
    
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
    
    def calculate_fair_ev_s(self, g_fwd: float, opm_fwd: float, fcf_rate: float, 
                           wacc: float = 0.10, terminal_growth: float = 0.02) -> float:
        """フェアEV/S逆算（rDCFライト）"""
        # 簡易DCFモデル（永続成長モデル）
        # EV/S = (1 + g) * OPM * FCF率 / (WACC - g)
        if wacc <= terminal_growth:
            return 0.0
        
        fair_ev_s = (1 + g_fwd) * opm_fwd * fcf_rate / (wacc - terminal_growth)
        return fair_ev_s
    
    def determine_color(self, pm: float, rdcf: float) -> str:
        """色判定（機械）"""
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
    
    def get_di_multiplier(self, color: str) -> float:
        """DI倍率取得"""
        return self.di_multipliers.get(color, 0.90)  # デフォルトはAmber
    
    def evaluate_valuation(self, ev_s_actual: float, ev_s_peer_median: float, 
                          ev_s_fair: float) -> Dict:
        """バリュエーション評価"""
        # PM計算
        pm = self.calculate_peer_multiple(ev_s_actual, ev_s_peer_median)
        
        # rDCF計算
        rdcf = self.calculate_reverse_dcf(ev_s_actual, ev_s_fair)
        
        # 色判定
        color = self.determine_color(pm, rdcf)
        
        # 認知ギャップ
        cognitive_gap = self.calculate_cognitive_gap(pm, rdcf)
        
        # DI倍率
        di_multiplier = self.get_di_multiplier(color)
        
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
    
    def get_valuation_display(self, ev_s_actual: float, ev_s_peer_median: float, 
                             ev_s_fair: float) -> str:
        """バリュエーション表示"""
        result = self.evaluate_valuation(ev_s_actual, ev_s_peer_median, ev_s_fair)
        
        return f"""
③バリュエーション＋認知ギャップ評価:
EV/S_actual: {ev_s_actual:.2f}
EV/S_peer_median: {ev_s_peer_median:.2f}
EV/S_fair: {ev_s_fair:.2f}

PM（Peer Multiple）: {result['pm_pct']:.1f}%
rDCF（逆DCFライト）: {result['rdcf_pct']:.1f}%

色判定: {result['color']}
認知ギャップ（Δ = P − R）: {result['cognitive_gap_pct']:.1f}%
DI倍率: {result['di_multiplier']:.2f}

判定基準:
- Green: |P|≤10% かつ |R|≤15%
- Amber: それ以外でどちらかが±25%以内
- Red: P>+25% または R>+25%（割高）、もしくは P<−25% & R<−25%（割安だが成長裏付け不足）
"""
    
    def get_color_explanation(self, pm: float, rdcf: float) -> str:
        """色判定の説明"""
        color = self.determine_color(pm, rdcf)
        
        explanations = {
            "Green": "|P|≤10% かつ |R|≤15% - 適正価格",
            "Amber": "どちらかが±25%以内 - 注意が必要",
            "Red": "P>+25% または R>+25%（割高）、もしくは P<−25% & R<−25%（割安だが成長裏付け不足）"
        }
        
        return f"色判定: {color} - {explanations.get(color, '不明')}"
    
    def validate_inputs(self, ev_s_actual: float, ev_s_peer_median: float, 
                       ev_s_fair: float) -> Tuple[bool, str]:
        """入力値検証"""
        errors = []
        
        if ev_s_actual <= 0:
            errors.append("EV/S_actualは正の値である必要があります")
        
        if ev_s_peer_median <= 0:
            errors.append("EV/S_peer_medianは正の値である必要があります")
        
        if ev_s_fair <= 0:
            errors.append("EV/S_fairは正の値である必要があります")
        
        if errors:
            return False, " / ".join(errors)
        else:
            return True, "OK"

def main():
    """テスト実行"""
    valuation = ValuationSystem()
    
    # テストケース1（Green）
    print("=== テストケース1（Green） ===")
    result1 = valuation.get_valuation_display(5.0, 5.0, 5.0)
    print(result1)
    
    # テストケース2（Amber）
    print("=== テストケース2（Amber） ===")
    result2 = valuation.get_valuation_display(6.0, 5.0, 5.5)
    print(result2)
    
    # テストケース3（Red - 割高）
    print("=== テストケース3（Red - 割高） ===")
    result3 = valuation.get_valuation_display(8.0, 5.0, 5.0)
    print(result3)
    
    # テストケース4（Red - 割安だが成長裏付け不足）
    print("=== テストケース4（Red - 割安だが成長裏付け不足） ===")
    result4 = valuation.get_valuation_display(3.0, 5.0, 5.0)
    print(result4)
    
    # フェアEV/S計算テスト
    print("=== フェアEV/S計算テスト ===")
    fair_ev_s = valuation.calculate_fair_ev_s(0.15, 0.20, 0.80, 0.10, 0.02)
    print(f"フェアEV/S: {fair_ev_s:.2f}")
    
    # 入力検証テスト
    print("=== 入力検証テスト ===")
    is_valid, message = valuation.validate_inputs(5.0, 5.0, 5.0)
    print(f"検証結果: {is_valid}, メッセージ: {message}")

if __name__ == "__main__":
    main()
