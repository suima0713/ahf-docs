#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NES自動欄 - Stage-3常設NES計算システム
式＋★マッピング実装
"""

from typing import Dict, Tuple, Optional

class NESAuto:
    """NES自動欄実装"""
    
    def __init__(self):
        self.formula = "NES = 0.5·(次Q q/q%) + 0.3·(ガイド改定%) + 0.2·(受注/Backlog増勢%) + Margin_term + Health_term"
        self.margin_term_conditions = {
            "改善": {"threshold": 50, "value": 1, "description": "改善≥+50bps=+1"},
            "維持": {"threshold": 50, "value": 0, "description": "±50bps=0"},
            "悪化": {"threshold": 50, "value": -1, "description": "悪化≤−50bps=−1"}
        }
        self.health_term_conditions = {
            "高": {"threshold": 40, "value": 1, "description": "Ro40≥40→+1"},
            "中": {"threshold": 30, "value": 0, "description": "30–40→0"},
            "低": {"threshold": 0, "value": -1, "description": "<30→−1"}
        }
        self.star_mapping = {
            (8, float('inf')): 5,    # NES ≥ +8 → ★5
            (5, 8): 4,               # +5–8 → ★4
            (2, 5): 3,               # +2–5 → ★3
            (0, 2): 2,               # 0–2 → ★2
            (float('-inf'), 0): 1    # <0 → ★1
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
        """Health_term計算（Ro40）"""
        if ro40 >= 40:
            return 1  # Ro40≥40→+1
        elif ro40 >= 30:
            return 0  # 30–40→0
        else:
            return -1  # <30→−1
    
    def calculate_nes(self, q_q_pct: float, guidance_revision_pct: float = 0, 
                     order_backlog_pct: float = 0, margin_change_bps: float = 0, ro40: float = 0) -> Tuple[float, int, Dict]:
        """NES計算と★換算"""
        margin_term = self.calculate_margin_term(margin_change_bps)
        health_term = self.calculate_health_term(ro40)
        
        nes = (0.5 * q_q_pct + 
               0.3 * guidance_revision_pct + 
               0.2 * order_backlog_pct + 
               margin_term + 
               health_term)
        
        # ★換算
        stars = 1
        for (min_val, max_val), star in self.star_mapping.items():
            if min_val <= nes < max_val:
                stars = star
                break
        
        # 計算詳細
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
    
    def get_formula_display(self) -> str:
        """式表示"""
        return f"""
NES自動欄:
式: {self.formula}
Margin_term条件:
- 改善≥+50bps=+1
- ±50bps=0  
- 悪化≤−50bps=−1
Health_term条件（Ro40）:
- Ro40≥40→+1
- 30–40→0
- <30→−1

★換算:
- NES ≥ +8 → ★5
- +5–8 → ★4
- +2–5 → ★3
- 0–2 → ★2
- <0 → ★1
"""
    
    def get_calculation_display(self, q_q_pct: float, guidance_revision_pct: float = 0, 
                              order_backlog_pct: float = 0, margin_change_bps: float = 0, ro40: float = 0) -> str:
        """計算表示"""
        nes, stars, details = self.calculate_nes(q_q_pct, guidance_revision_pct, 
                                               order_backlog_pct, margin_change_bps, ro40)
        
        return f"""
NES計算結果:
入力: q/q={q_q_pct:.2f}%, 改定%={guidance_revision_pct:.2f}%, 受注%={order_backlog_pct:.2f}%, Margin_change={margin_change_bps:.1f}bps, Ro40={ro40:.1f}
計算: NES = 0.5×{q_q_pct:.2f} + 0.3×{guidance_revision_pct:.2f} + 0.2×{order_backlog_pct:.2f} + {details['margin_term']} + {details['health_term']} = {nes:.2f}
結果: NES={nes:.2f} → ★{stars}
"""
    
    def get_star_explanation(self, nes: float) -> str:
        """★説明"""
        for (min_val, max_val), star in self.star_mapping.items():
            if min_val <= nes < max_val:
                return f"NES={nes:.2f}は{min_val}≤NES<{max_val}の範囲なので★{star}"
        return f"NES={nes:.2f}の★換算が不明"
    
    def validate_inputs(self, q_q_pct: float, guidance_revision_pct: float = 0, 
                       order_backlog_pct: float = 0, margin_change_bps: float = 0) -> Tuple[bool, str]:
        """入力値検証"""
        errors = []
        
        if not isinstance(q_q_pct, (int, float)):
            errors.append("q_q_pctは数値である必要があります")
        
        if not isinstance(guidance_revision_pct, (int, float)):
            errors.append("guidance_revision_pctは数値である必要があります")
        
        if not isinstance(order_backlog_pct, (int, float)):
            errors.append("order_backlog_pctは数値である必要があります")
        
        if not isinstance(margin_change_bps, (int, float)):
            errors.append("margin_change_bpsは数値である必要があります")
        
        if errors:
            return False, " / ".join(errors)
        else:
            return True, "OK"
    
    def get_historical_comparison(self, current_nes: float, historical_data: list) -> str:
        """履歴比較表示"""
        if not historical_data:
            return "履歴データなし"
        
        avg_nes = sum(historical_data) / len(historical_data)
        max_nes = max(historical_data)
        min_nes = min(historical_data)
        
        return f"""
履歴比較:
現在: NES={current_nes:.2f}
平均: NES={avg_nes:.2f}
最大: NES={max_nes:.2f}
最小: NES={min_nes:.2f}
"""

def main():
    """テスト実行"""
    nes_auto = NESAuto()
    
    # 式表示
    print(nes_auto.get_formula_display())
    
    # 計算例1（現在のケース）
    print("=== 計算例1（現在のケース） ===")
    result1 = nes_auto.get_calculation_display(17.48, 0, 0, 0)
    print(result1)
    
    # 計算例2（改定あり）
    print("=== 計算例2（改定あり） ===")
    result2 = nes_auto.get_calculation_display(15.0, 5.0, 3.0, 75)
    print(result2)
    
    # 計算例3（悪化ケース）
    print("=== 計算例3（悪化ケース） ===")
    result3 = nes_auto.get_calculation_display(8.0, -2.0, -1.0, -60)
    print(result3)
    
    # 入力検証テスト
    print("=== 入力検証テスト ===")
    is_valid, message = nes_auto.validate_inputs(17.48, 0, 0, 0)
    print(f"検証結果: {is_valid}, メッセージ: {message}")
    
    # 履歴比較テスト
    print("=== 履歴比較テスト ===")
    historical = [8.5, 12.3, 6.7, 15.2, 9.8]
    comparison = nes_auto.get_historical_comparison(8.74, historical)
    print(comparison)

if __name__ == "__main__":
    main()
