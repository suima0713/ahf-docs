#!/usr/bin/env python3
"""
AHF TRI-4 バリュエーション織込み度（V）判定機能
V：バリュエーション織込み度（Amber/Red/Green）

判定基準：
Green: EV/Sales(Fwd) ≤ 10× and Rule-of-40 ≥ 40
Amber: 10×＜ EV/Sales(Fwd) ≤ 14× or Rule-of-40 ∈ [35,40)
Red: EV/Sales(Fwd) > 14× or Rule-of-40 < 35
※VはT1外だが④にのみ反映
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from enum import Enum

class VLevel(Enum):
    """バリュエーション織込み度"""
    GREEN = "Green"
    AMBER = "Amber"
    RED = "Red"

class ValuationIntegrationAnalyzer:
    """バリュエーション織込み度分析器"""
    
    def __init__(self):
        # V-Overlay しきい値（TRI-4仕様）
        self.thresholds = {
            "ev_sales_fwd": {
                "green_max": 10.0,    # ≤ 10×
                "amber_max": 14.0,    # ≤ 14×
                "red_min": 14.0       # > 14×
            },
            "rule_of_40": {
                "green_min": 40.0,    # ≥ 40
                "amber_min": 35.0,    # ∈ [35,40)
                "red_max": 35.0       # < 35
            }
        }
    
    def calculate_ev_sales_fwd(self, market_data: Dict[str, Any]) -> Optional[float]:
        """EV/Sales(Fwd) 計算"""
        try:
            enterprise_value = market_data.get("enterprise_value")
            sales_fwd = market_data.get("sales_fwd_12m")
            
            if enterprise_value and sales_fwd and sales_fwd > 0:
                return enterprise_value / sales_fwd
            return None
        except (TypeError, ZeroDivisionError):
            return None
    
    def calculate_rule_of_40(self, financial_data: Dict[str, Any]) -> Optional[float]:
        """Rule-of-40 計算: 成長率 + Adj.EBITDA%"""
        try:
            growth_rate = financial_data.get("revenue_growth_rate", 0)
            adj_ebitda_margin = financial_data.get("adj_ebitda_margin", 0)
            
            if growth_rate is not None and adj_ebitda_margin is not None:
                return growth_rate + adj_ebitda_margin
            return None
        except (TypeError, ValueError):
            return None
    
    def analyze_valuation_integration(self, ev_sales_fwd: Optional[float], rule_of_40: Optional[float]) -> VLevel:
        """バリュエーション織込み度（V）を判定"""
        
        # Red判定（最優先）
        if ev_sales_fwd is not None:
            if ev_sales_fwd > self.thresholds["ev_sales_fwd"]["red_min"]:
                return VLevel.RED
        
        if rule_of_40 is not None:
            if rule_of_40 < self.thresholds["rule_of_40"]["red_max"]:
                return VLevel.RED
        
        # Amber判定
        amber_conditions = []
        
        if ev_sales_fwd is not None:
            if (self.thresholds["ev_sales_fwd"]["green_max"] < ev_sales_fwd <= 
                self.thresholds["ev_sales_fwd"]["amber_max"]):
                amber_conditions.append(f"EV/Sales(Fwd) {ev_sales_fwd:.1f}×")
        
        if rule_of_40 is not None:
            if (self.thresholds["rule_of_40"]["amber_min"] <= rule_of_40 < 
                self.thresholds["rule_of_40"]["green_min"]):
                amber_conditions.append(f"Rule-of-40 {rule_of_40:.1f}%")
        
        if amber_conditions:
            return VLevel.AMBER
        
        # Green判定（デフォルト）
        return VLevel.GREEN
    
    def generate_v_analysis_report(self, ev_sales_fwd: Optional[float], rule_of_40: Optional[float], V_level: VLevel) -> str:
        """V分析レポート生成"""
        
        report_lines = [
            "=== バリュエーション織込み度（V）分析 ===",
            "",
            f"V = {V_level.value}",
            ""
        ]
        
        # 指標値
        if ev_sales_fwd is not None:
            report_lines.append(f"EV/Sales(Fwd): {ev_sales_fwd:.1f}×")
        else:
            report_lines.append("EV/Sales(Fwd): N/A")
        
        if rule_of_40 is not None:
            report_lines.append(f"Rule-of-40: {rule_of_40:.1f}%")
        else:
            report_lines.append("Rule-of-40: N/A")
        
        report_lines.extend([
            "",
            "判定基準:",
            f"Green: EV/Sales(Fwd) ≤ {self.thresholds['ev_sales_fwd']['green_max']}× and Rule-of-40 ≥ {self.thresholds['rule_of_40']['green_min']}",
            f"Amber: {self.thresholds['ev_sales_fwd']['green_max']}×＜ EV/Sales(Fwd) ≤ {self.thresholds['ev_sales_fwd']['amber_max']}× or Rule-of-40 ∈ [{self.thresholds['rule_of_40']['amber_min']}, {self.thresholds['rule_of_40']['green_min']})",
            f"Red: EV/Sales(Fwd) > {self.thresholds['ev_sales_fwd']['red_min']}× or Rule-of-40 < {self.thresholds['rule_of_40']['red_max']}",
            ""
        ])
        
        # 判定理由
        if V_level == VLevel.RED:
            report_lines.append("判定理由: Red条件に該当")
            if ev_sales_fwd and ev_sales_fwd > self.thresholds["ev_sales_fwd"]["red_min"]:
                report_lines.append(f"  - EV/Sales(Fwd) {ev_sales_fwd:.1f}× > {self.thresholds['ev_sales_fwd']['red_min']}×")
            if rule_of_40 and rule_of_40 < self.thresholds["rule_of_40"]["red_max"]:
                report_lines.append(f"  - Rule-of-40 {rule_of_40:.1f}% < {self.thresholds['rule_of_40']['red_max']}%")
        
        elif V_level == VLevel.AMBER:
            report_lines.append("判定理由: Amber条件に該当")
            if ev_sales_fwd and (self.thresholds["ev_sales_fwd"]["green_max"] < ev_sales_fwd <= self.thresholds["ev_sales_fwd"]["amber_max"]):
                report_lines.append(f"  - {self.thresholds['ev_sales_fwd']['green_max']}× < EV/Sales(Fwd) {ev_sales_fwd:.1f}× ≤ {self.thresholds['ev_sales_fwd']['amber_max']}×")
            if rule_of_40 and (self.thresholds["rule_of_40"]["amber_min"] <= rule_of_40 < self.thresholds["rule_of_40"]["green_min"]):
                report_lines.append(f"  - {self.thresholds['rule_of_40']['amber_min']}% ≤ Rule-of-40 {rule_of_40:.1f}% < {self.thresholds['rule_of_40']['green_min']}%")
        
        else:  # GREEN
            report_lines.append("判定理由: Green条件に該当")
            if ev_sales_fwd:
                report_lines.append(f"  - EV/Sales(Fwd) {ev_sales_fwd:.1f}× ≤ {self.thresholds['ev_sales_fwd']['green_max']}×")
            if rule_of_40:
                report_lines.append(f"  - Rule-of-40 {rule_of_40:.1f}% ≥ {self.thresholds['rule_of_40']['green_min']}%")
        
        return "\n".join(report_lines)

def analyze_duol_v_valuation():
    """DUOLのバリュエーション織込み度分析"""
    
    # DUOLの実際のデータ（参考レンジから）
    # EV/Sales(Fwd) ≈ 12×、Rule-of-40 ≈ 41%+31% ≈ 72
    
    market_data = {
        "enterprise_value": 12000,  # 推定値（12× × 1000M売上）
        "sales_fwd_12m": 1000,      # 推定値（FY25ガイダンス$1,011-1,019Mの中央値）
    }
    
    financial_data = {
        "revenue_growth_rate": 41.0,  # YoY成長率
        "adj_ebitda_margin": 31.2,    # Adjusted EBITDA margin
    }
    
    # バリュエーション織込み度分析
    analyzer = ValuationIntegrationAnalyzer()
    ev_sales_fwd = analyzer.calculate_ev_sales_fwd(market_data)
    rule_of_40 = analyzer.calculate_rule_of_40(financial_data)
    V_level = analyzer.analyze_valuation_integration(ev_sales_fwd, rule_of_40)
    
    # レポート生成
    report = analyzer.generate_v_analysis_report(ev_sales_fwd, rule_of_40, V_level)
    
    print(report)
    
    return {
        "V": V_level,
        "ev_sales_fwd": ev_sales_fwd,
        "rule_of_40": rule_of_40,
        "report": report
    }

def main():
    """メイン実行"""
    print("=== DUOL バリュエーション織込み度（V）分析 ===")
    
    result = analyze_duol_v_valuation()
    
    if result:
        print(f"\nDUOLのV値: {result['V'].value}")
        
        # 結果をJSONで保存
        output_path = Path("duol_v_analysis.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                "V": result["V"].value,
                "ev_sales_fwd": result["ev_sales_fwd"],
                "rule_of_40": result["rule_of_40"]
            }, f, ensure_ascii=False, indent=2)
        
        print(f"結果を保存: {output_path}")

if __name__ == "__main__":
    main()
