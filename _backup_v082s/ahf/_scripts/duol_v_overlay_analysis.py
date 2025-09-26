#!/usr/bin/env python3
"""
DUOL V-Overlay 分析
DUOLの実際のデータに基づくV-Overlay判定
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class VLevel(Enum):
    """V-Overlay レベル定義"""
    GREEN = "Green"    # 割安フラグ
    AMBER = "Amber"    # 割高フラグ  
    RED = "Red"        # 過熱フラグ

@dataclass
class VOverlayResult:
    """V-Overlay 判定結果"""
    level: VLevel
    reason: str
    ev_sales_fwd: Optional[float] = None
    rule_of_40: Optional[float] = None
    guidance_upside: bool = False
    star_cap_applied: bool = False

def analyze_duol_v_overlay():
    """DUOLのV-Overlay分析"""
    
    # DUOLの実際のデータ（参考レンジから）
    # EV/Sales(Fwd) ≈ 12×、EV/Adj.EBITDA(Fwd) ≈ 42×、Rule-of-40 ≈ 41%+31% ≈ 72
    
    # 実際のデータ設定
    market_data = {
        "enterprise_value": 12000,  # 推定値（12× × 1000M売上）
        "sales_fwd_12m": 1000,      # 推定値（FY25ガイダンス$1,011-1,019Mの中央値）
    }
    
    financial_data = {
        "revenue_growth_rate": 41.0,  # YoY成長率
        "adj_ebitda_margin": 31.2,    # Adjusted EBITDA margin
    }
    
    guidance_data = {
        "revenue_guidance_upside": True,   # FY25 GM decline改善（100bps→100bps）
        "ebitda_guidance_upside": True,    # Q3 EBITDA margin 28.5%-29.0%
    }
    
    # V-Overlay ルール適用
    result = apply_v_overlay_rules(market_data, financial_data, guidance_data)
    
    return result

def apply_v_overlay_rules(market_data: Dict[str, Any], 
                        financial_data: Dict[str, Any],
                        guidance_data: Dict[str, Any]) -> VOverlayResult:
    """V-Overlay ルール適用"""
    
    # しきい値定義
    thresholds = {
        "ev_sales_fwd": {
            "green_max": 6.0,    # V3: 割安フラグ
            "amber_max": 10.0,   # V1: 割高フラグ
            "red_min": 14.0      # V2: 過熱フラグ
        },
        "rule_of_40_min": 40.0   # V4: 耐性チェック
    }
    
    # 基本指標計算
    ev_sales_fwd = market_data.get("enterprise_value", 0) / market_data.get("sales_fwd_12m", 1)
    rule_of_40 = financial_data.get("revenue_growth_rate", 0) + financial_data.get("adj_ebitda_margin", 0)
    guidance_upside = guidance_data.get("revenue_guidance_upside", False) or guidance_data.get("ebitda_guidance_upside", False)
    
    # V1-V3: EV/Sales(Fwd) ベース判定
    initial_level = VLevel.GREEN
    reason_parts = []
    
    if ev_sales_fwd >= thresholds["ev_sales_fwd"]["red_min"]:
        initial_level = VLevel.RED
        reason_parts.append(f"EV/Sales(Fwd) {ev_sales_fwd:.1f}× (過熱域)")
    elif ev_sales_fwd >= thresholds["ev_sales_fwd"]["amber_max"]:
        initial_level = VLevel.AMBER
        reason_parts.append(f"EV/Sales(Fwd) {ev_sales_fwd:.1f}× (割高域)")
    elif ev_sales_fwd <= thresholds["ev_sales_fwd"]["green_max"]:
        initial_level = VLevel.GREEN
        reason_parts.append(f"EV/Sales(Fwd) {ev_sales_fwd:.1f}× (割安域)")
    
    # V4: Rule-of-40 耐性チェック（一段悪化）
    final_level = initial_level
    if rule_of_40 < thresholds["rule_of_40_min"]:
        if initial_level == VLevel.GREEN:
            final_level = VLevel.AMBER
            reason_parts.append(f"Rule-of-40 {rule_of_40:.1f}% (耐性不足)")
        elif initial_level == VLevel.AMBER:
            final_level = VLevel.RED
            reason_parts.append(f"Rule-of-40 {rule_of_40:.1f}% (耐性不足)")
    
    # V5: ガイダンス上方修正（一段改善）
    if guidance_upside:
        if final_level == VLevel.RED:
            final_level = VLevel.AMBER
            reason_parts.append("ガイダンス上方修正")
        elif final_level == VLevel.AMBER:
            final_level = VLevel.GREEN
            reason_parts.append("ガイダンス上方修正")
    
    # 理由の組み立て
    reason = " / ".join(reason_parts) if reason_parts else "データ不足"
    
    # ★上限自動キャップ判定
    star_cap_applied = (final_level == VLevel.RED)
    
    return VOverlayResult(
        level=final_level,
        reason=reason,
        ev_sales_fwd=ev_sales_fwd,
        rule_of_40=rule_of_40,
        guidance_upside=guidance_upside,
        star_cap_applied=star_cap_applied
    )

def generate_v_badge(result: VOverlayResult) -> str:
    """Vバッジ表示用文字列生成"""
    level_symbols = {
        VLevel.GREEN: "🟢",
        VLevel.AMBER: "🟡", 
        VLevel.RED: "🔴"
    }
    
    symbol = level_symbols.get(result.level, "⚪")
    return f"{symbol} V={result.level.value}"

def main():
    """メイン実行"""
    print("=== DUOL V-Overlay 分析 ===")
    
    # DUOLのV-Overlay判定
    result = analyze_duol_v_overlay()
    
    # 結果表示
    v_badge = generate_v_badge(result)
    print(f"V-Overlay判定: {v_badge}")
    print(f"理由: {result.reason}")
    
    if result.ev_sales_fwd is not None:
        print(f"EV/Sales(Fwd): {result.ev_sales_fwd:.1f}×")
    
    if result.rule_of_40 is not None:
        print(f"Rule-of-40: {result.rule_of_40:.1f}%")
    
    if result.guidance_upside:
        print("ガイダンス上方修正: あり")
    
    if result.star_cap_applied:
        print("[CRITICAL] ★上限=3の自動キャップ発動")
    
    # 半値シナリオ分析
    print("\n=== 半値シナリオ分析 ===")
    if result.ev_sales_fwd:
        half_price_multiple = result.ev_sales_fwd / 2
        print(f"現在のEV/Sales(Fwd): {result.ev_sales_fwd:.1f}×")
        print(f"半値シナリオ（EV/Sales 6×）での圧縮率: {((result.ev_sales_fwd - 6.0) / result.ev_sales_fwd * 100):.1f}%")
        print(f"株価半減は「理屈としては」あり得る（リレーティング）")
    
    # トリガー分析
    print("\n=== V-Overlay トリガー ===")
    if result.level == VLevel.AMBER:
        print("V改善トリガー:")
        print("  - ガイダンス上方修正")
        print("  - 市場でEV/Sales(Fwd) ≤ 10×")
        print("V悪化トリガー:")
        print("  - EV/Sales(Fwd) ≥ 14×")
        print("  - Rule-of-40 < 40")
    
    # 出力まとめ
    print("\n=== 出力まとめ ===")
    print("スタンス: 星は前回マトリクスのまま（Proceed）")
    print(f"Vバッジ: {v_badge}")
    print("意味: 事業はT1で健在、ただしプレミアム域なのでマルチプル圧縮の尾リスクは残る")
    
    # JSON形式で結果保存
    output_path = Path("../../ahf/tickers/DUOL/current/v_overlay_result.json")
    result_dict = {
        "as_of": "2025-01-15",
        "ticker": "DUOL",
        "v_level": result.level.value,
        "reason": result.reason,
        "ev_sales_fwd": result.ev_sales_fwd,
        "rule_of_40": result.rule_of_40,
        "guidance_upside": result.guidance_upside,
        "star_cap_applied": result.star_cap_applied,
        "v_badge": v_badge,
        "half_price_scenario": {
            "current_multiple": result.ev_sales_fwd,
            "target_multiple": 6.0,
            "compression_rate": ((result.ev_sales_fwd - 6.0) / result.ev_sales_fwd * 100) if result.ev_sales_fwd else None,
            "feasible": True
        },
        "triggers": {
            "improvement": ["ガイダンス上方修正", "EV/Sales(Fwd) ≤ 10×"],
            "deterioration": ["EV/Sales(Fwd) ≥ 14×", "Rule-of-40 < 40"]
        }
    }
    
    # 出力ディレクトリ作成
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result_dict, f, ensure_ascii=False, indent=2)
    
    print(f"\n結果を保存: {output_path}")

if __name__ == "__main__":
    main()
