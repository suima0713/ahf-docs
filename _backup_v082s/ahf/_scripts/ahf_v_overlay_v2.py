#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AHF V-Overlay 2.0
EV/SalesとRule-of-40の合成評価 + ヒステリシス制御

合成スコア: V_score = 0.7*score_EV + 0.3*score_Ro40
区分: Green < 0.25 < Amber < 0.6 < Red
ヒステリシス: 前回区分からの切替は閾値±余裕帯を超えた時のみ更新
"""

import yaml
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

@dataclass
class VOverlayResult:
    """V-Overlay評価結果"""
    v_score: float
    category: str  # Green, Amber, Red
    ev_score: float
    ro40_score: float
    ev_sales: float
    rule_of_40: float
    hysteresis_applied: bool
    previous_category: Optional[str]
    star_impact: int

class VOverlayEngine:
    """V-Overlay 2.0エンジン"""
    
    def __init__(self, config_dir: str = "../config"):
        """初期化"""
        self.config_dir = Path(config_dir)
        self.config = self._load_config()
        
    def _load_config(self) -> Dict:
        """V-Overlay設定の読み込み"""
        try:
            with open(self.config_dir / "v_overlay.yaml", 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise RuntimeError(f"V-Overlay設定の読み込みエラー: {e}")
    
    def calculate_ev_score(self, ev_sales: float) -> float:
        """EV/Salesスコアの計算"""
        ev_config = self.config["evsales"]
        green_max = ev_config["green_max"]
        red_min = ev_config["red_min"]
        
        # 正規化: (EV/Sales - 6) / (14 - 6) → 0-1範囲
        # Green上限10.0, Red下限14.0を使用
        if ev_sales <= green_max:
            return 0.0
        elif ev_sales >= red_min:
            return 1.0
        else:
            # 線形補間
            return (ev_sales - green_max) / (red_min - green_max)
    
    def calculate_ro40_score(self, rule_of_40: float) -> float:
        """Rule-of-40スコアの計算"""
        ro40_config = self.config["rule_of_40"]
        green_min = ro40_config["green_min"]
        red_max = ro40_config["red_max"]
        
        # Ro40 ≥ 40でscore = 0, Ro40 ≤ 35でscore = 1
        if rule_of_40 >= green_min:
            return 0.0
        elif rule_of_40 <= red_max:
            return 1.0
        else:
            # 線形補間（逆方向）
            return (green_min - rule_of_40) / (green_min - red_max)
    
    def calculate_v_score(self, ev_sales: float, rule_of_40: float) -> Tuple[float, float, float]:
        """合成Vスコアの計算"""
        ev_score = self.calculate_ev_score(ev_sales)
        ro40_score = self.calculate_ro40_score(rule_of_40)
        
        # 重み付き合成
        weight_ev = self.config["evsales"]["weight"]
        weight_ro40 = 1.0 - weight_ev
        
        v_score = weight_ev * ev_score + weight_ro40 * ro40_score
        
        return v_score, ev_score, ro40_score
    
    def determine_category(self, v_score: float) -> str:
        """V区分の決定"""
        thresholds = self.config["v_thresholds"]
        
        if v_score < thresholds["green_max"]:
            return "Green"
        elif v_score < thresholds["amber_max"]:
            return "Amber"
        else:
            return "Red"
    
    def apply_hysteresis(self, 
                        current_category: str, 
                        previous_category: Optional[str],
                        ev_sales: float,
                        rule_of_40: float,
                        previous_ev_sales: Optional[float],
                        previous_ro40: Optional[float]) -> Tuple[str, bool]:
        """V-Overlay 2.0ヒステリシス制御（v0.7.2）"""
        if previous_category is None or previous_ev_sales is None or previous_ro40 is None:
            return current_category, False
        
        # ① 生区分が同じ→即維持
        if current_category == previous_category:
            return previous_category, False
        
        hysteresis = self.config["hysteresis"]
        ev_delta = hysteresis["evsales_delta"]  # 0.5x
        ro40_delta = hysteresis["ro40_delta"]    # 2.0pp
        upgrade_factor = hysteresis.get("upgrade_factor", 1.2)
        
        # 変化量の計算
        ev_change = abs(ev_sales - previous_ev_sales)
        ro40_change = abs(rule_of_40 - previous_ro40)
        
        # ② ダウングレード/アップグレードを判定
        upgrading = ((previous_category == "Amber" and current_category == "Green") or
                    (previous_category == "Red" and current_category in ["Amber", "Green"]))
        
        # ③ 維持条件（AND＋厳密不等号）
        keep_base = (ev_change < ev_delta) and (ro40_change < ro40_delta)
        keep_up = (ev_change < ev_delta * upgrade_factor) and (ro40_change < ro40_delta * upgrade_factor)
        
        if upgrading and keep_up:       # アップグレードのみ粘る（1.2倍まで許容）
            return previous_category, True
        if (not upgrading) and keep_base:  # ダウンは通常閾値
            return previous_category, True
        
        return current_category, False
    
    def calculate_star_impact(self, category: str) -> int:
        """V-Overlay 2.0星への影響計算（v0.7.2）"""
        # Green=据置／Amber=★−1（下限★1）／Red=★−1 & ★上限=3
        if category == "Green":
            return 0  # 据置
        elif category == "Amber":
            return -1  # ★−1（下限★1）
        elif category == "Red":
            return -1  # ★−1 & ★上限=3
        else:
            return 0
    
    def evaluate(self, 
                ev_sales: float, 
                rule_of_40: float,
                previous_category: Optional[str] = None,
                previous_ev_sales: Optional[float] = None,
                previous_ro40: Optional[float] = None) -> VOverlayResult:
        """V-Overlay評価の実行"""
        
        # 合成スコア計算
        v_score, ev_score, ro40_score = self.calculate_v_score(ev_sales, rule_of_40)
        
        # 区分決定
        initial_category = self.determine_category(v_score)
        
        # ヒステリシス適用
        final_category, hysteresis_applied = self.apply_hysteresis(
            initial_category, previous_category, 
            ev_sales, rule_of_40,
            previous_ev_sales, previous_ro40
        )
        
        # 星への影響計算
        star_impact = self.calculate_star_impact(final_category)
        
        return VOverlayResult(
            v_score=v_score,
            category=final_category,
            ev_score=ev_score,
            ro40_score=ro40_score,
            ev_sales=ev_sales,
            rule_of_40=rule_of_40,
            hysteresis_applied=hysteresis_applied,
            previous_category=previous_category,
            star_impact=star_impact
        )

def main():
    """テスト実行"""
    engine = VOverlayEngine()
    
    # テストケース1: 典型的なGreen
    result1 = engine.evaluate(ev_sales=8.5, rule_of_40=45.0)
    print(f"テスト1 - EV/Sales: 8.5, Ro40: 45.0")
    print(f"  Vスコア: {result1.v_score:.3f}, 区分: {result1.category}, 星影響: {result1.star_impact}")
    
    # テストケース2: 典型的なAmber
    result2 = engine.evaluate(ev_sales=12.0, rule_of_40=38.0)
    print(f"テスト2 - EV/Sales: 12.0, Ro40: 38.0")
    print(f"  Vスコア: {result2.v_score:.3f}, 区分: {result2.category}, 星影響: {result2.star_impact}")
    
    # テストケース3: 典型的なRed
    result3 = engine.evaluate(ev_sales=16.0, rule_of_40=32.0)
    print(f"テスト3 - EV/Sales: 16.0, Ro40: 32.0")
    print(f"  Vスコア: {result3.v_score:.3f}, 区分: {result3.category}, 星影響: {result3.star_impact}")
    
    # テストケース4: ヒステリシステスト
    result4a = engine.evaluate(ev_sales=9.5, rule_of_40=42.0)  # Green境界
    result4b = engine.evaluate(ev_sales=9.8, rule_of_40=41.8,  # ヒステリシス範囲内
                              previous_category=result4a.category,
                              previous_ev_sales=result4a.ev_sales,
                              previous_ro40=result4a.rule_of_40)
    print(f"テスト4 - ヒステリシス")
    print(f"  前回: {result4a.category}, 今回: {result4b.category}, 適用: {result4b.hysteresis_applied}")

if __name__ == "__main__":
    main()
