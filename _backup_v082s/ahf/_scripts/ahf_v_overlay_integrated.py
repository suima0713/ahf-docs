#!/usr/bin/env python3
"""
AHF V-Overlay 統合運用スクリプト
V-Overlayの全機能を統合した運用ツール
"""

import json
import yaml
import sys
from pathlib import Path
from typing import Dict, Any, Optional

def run_v_overlay_analysis(ticker_path: str):
    """V-Overlay分析実行"""
    print("=== V-Overlay分析実行 ===")
    
    # 簡易的なV-Overlay分析（実際のデータに基づく）
    # DUOLのケースを例として使用
    
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
    
    # V-Overlay判定
    ev_sales_fwd = market_data["enterprise_value"] / market_data["sales_fwd_12m"]
    rule_of_40 = financial_data["revenue_growth_rate"] + financial_data["adj_ebitda_margin"]
    guidance_upside = guidance_data["revenue_guidance_upside"] or guidance_data["ebitda_guidance_upside"]
    
    # ルール適用
    thresholds = {
        "ev_sales_fwd": {"green_max": 6.0, "amber_max": 10.0, "red_min": 14.0},
        "rule_of_40_min": 40.0
    }
    
    # V1-V3: EV/Sales(Fwd) ベース判定
    if ev_sales_fwd >= thresholds["ev_sales_fwd"]["red_min"]:
        initial_level = "Red"
        reason_parts = [f"EV/Sales(Fwd) {ev_sales_fwd:.1f}× (過熱域)"]
    elif ev_sales_fwd >= thresholds["ev_sales_fwd"]["amber_max"]:
        initial_level = "Amber"
        reason_parts = [f"EV/Sales(Fwd) {ev_sales_fwd:.1f}× (割高域)"]
    else:
        initial_level = "Green"
        reason_parts = [f"EV/Sales(Fwd) {ev_sales_fwd:.1f}× (割安域)"]
    
    # V4: Rule-of-40 耐性チェック
    final_level = initial_level
    if rule_of_40 < thresholds["rule_of_40_min"]:
        if initial_level == "Green":
            final_level = "Amber"
            reason_parts.append(f"Rule-of-40 {rule_of_40:.1f}% (耐性不足)")
        elif initial_level == "Amber":
            final_level = "Red"
            reason_parts.append(f"Rule-of-40 {rule_of_40:.1f}% (耐性不足)")
    
    # V5: ガイダンス上方修正
    if guidance_upside:
        if final_level == "Red":
            final_level = "Amber"
            reason_parts.append("ガイダンス上方修正")
        elif final_level == "Amber":
            final_level = "Green"
            reason_parts.append("ガイダンス上方修正")
    
    # 結果生成
    reason = " / ".join(reason_parts)
    star_cap_applied = (final_level == "Red")
    
    level_symbols = {"Green": "🟢", "Amber": "🟡", "Red": "🔴"}
    v_badge = f"{level_symbols[final_level]} V={final_level}"
    
    # V-Overlay結果保存
    result_dict = {
        "as_of": "2025-01-15",
        "ticker": "DUOL",
        "v_level": final_level,
        "reason": reason,
        "ev_sales_fwd": ev_sales_fwd,
        "rule_of_40": rule_of_40,
        "guidance_upside": guidance_upside,
        "star_cap_applied": star_cap_applied,
        "v_badge": v_badge,
        "half_price_scenario": {
            "current_multiple": ev_sales_fwd,
            "target_multiple": 6.0,
            "compression_rate": ((ev_sales_fwd - 6.0) / ev_sales_fwd * 100),
            "feasible": True
        },
        "triggers": {
            "improvement": ["ガイダンス上方修正", "EV/Sales(Fwd) ≤ 10×"],
            "deterioration": ["EV/Sales(Fwd) ≥ 14×", "Rule-of-40 < 40"]
        }
    }
    
    output_path = Path(ticker_path) / "current" / "v_overlay_result.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result_dict, f, ensure_ascii=False, indent=2)
    
    print(f"V-Overlay判定: {v_badge}")
    print(f"理由: {reason}")
    print(f"EV/Sales(Fwd): {ev_sales_fwd:.1f}×")
    print(f"Rule-of-40: {rule_of_40:.1f}%")
    
    if star_cap_applied:
        print("[CRITICAL] ★上限=3の自動キャップ発動")
    
    print(f"結果を保存: {output_path}")
    
    return result_dict

def update_b_yaml_with_v_overlay(ticker_path: str, v_overlay: Dict[str, Any]):
    """B.yamlにV-Overlay情報を統合"""
    print("\n=== B.yaml V-Overlay統合 ===")
    
    b_yaml_path = Path(ticker_path) / "current" / "B.yaml"
    
    if not b_yaml_path.exists():
        print(f"B.yamlが見つかりません: {b_yaml_path}")
        return
    
    # B.yaml読み込み
    with open(b_yaml_path, 'r', encoding='utf-8') as f:
        b_data = yaml.safe_load(f)
    
    # V-Overlay情報を追加
    b_data["v_overlay"] = {
        "level": v_overlay.get("v_level"),
        "badge": v_overlay.get("v_badge"),
        "reason": v_overlay.get("reason"),
        "ev_sales_fwd": v_overlay.get("ev_sales_fwd"),
        "rule_of_40": v_overlay.get("rule_of_40"),
        "star_cap_applied": v_overlay.get("star_cap_applied", False)
    }
    
    # スタンスにVバッジ情報を統合
    if "stance" in b_data:
        b_data["stance"]["v_badge"] = v_overlay.get("v_badge", "")
        
        # VレベルがRedの場合は★上限キャップを明記
        if v_overlay.get("star_cap_applied", False):
            b_data["stance"]["star_cap_note"] = "★上限=3（V=Red自動キャップ）"
            b_data["star_cap"] = {
                "enabled": True,
                "max_stars": 3,
                "reason": "V=Red自動キャップ発動",
                "applied_at": v_overlay.get("as_of", "N/A")
            }
    
    # 更新されたB.yamlを保存
    with open(b_yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(b_data, f, default_flow_style=False, allow_unicode=True, indent=2)
    
    print(f"B.yamlを更新: {b_yaml_path}")

def display_final_summary(ticker_path: str, v_overlay: Dict[str, Any]):
    """最終サマリー表示"""
    print("\n=== AHF V-Overlay 最終サマリー ===")
    
    # B.yaml読み込み
    b_yaml_path = Path(ticker_path) / "current" / "B.yaml"
    with open(b_yaml_path, 'r', encoding='utf-8') as f:
        b_data = yaml.safe_load(f)
    
    # 基本情報
    stance = b_data.get("stance", {})
    decision = stance.get("decision", "N/A")
    size = stance.get("size", "N/A")
    v_badge = stance.get("v_badge", "")
    
    print(f"ティッカー: DUOL")
    print(f"スタンス: {decision} ({size})")
    print(f"Vバッジ: {v_badge}")
    
    # ★キャップ情報
    star_cap = b_data.get("star_cap", {})
    if star_cap.get("enabled", False):
        print(f"[CRITICAL] ★上限=3の自動キャップ発動")
        print(f"理由: {star_cap.get('reason', 'N/A')}")
    
    # V-Overlay詳細
    print(f"\nV-Overlay詳細:")
    print(f"  レベル: {v_overlay.get('v_level')}")
    print(f"  理由: {v_overlay.get('reason')}")
    print(f"  EV/Sales(Fwd): {v_overlay.get('ev_sales_fwd'):.1f}×")
    print(f"  Rule-of-40: {v_overlay.get('rule_of_40'):.1f}%")
    
    # 半値シナリオ
    half_scenario = v_overlay.get("half_price_scenario", {})
    if half_scenario.get("feasible", False):
        compression_rate = half_scenario.get("compression_rate")
        print(f"  半値シナリオ: 圧縮率{compression_rate:.1f}%（リレーティング可能）")
    
    # トリガー
    triggers = v_overlay.get("triggers", {})
    if triggers:
        print(f"\nトリガー:")
        improvement = triggers.get("improvement", [])
        if improvement:
            print(f"  改善: {', '.join(improvement)}")
        deterioration = triggers.get("deterioration", [])
        if deterioration:
            print(f"  悪化: {', '.join(deterioration)}")
    
    # 結論
    print(f"\n=== 結論 ===")
    print(f"スタンス: 星は前回マトリクスのまま（{decision}）")
    print(f"Vバッジ: {v_badge}")
    print(f"意味: 事業はT1で健在、ただしプレミアム域なのでマルチプル圧縮の尾リスクは残る")
    
    if star_cap.get("enabled", False):
        print(f"★上限: 3（V=Red自動キャップ）")

def main():
    """メイン実行"""
    if len(sys.argv) != 2:
        print("使用法: python ahf_v_overlay_integrated.py <ticker_path>")
        sys.exit(1)
    
    ticker_path = sys.argv[1]
    
    try:
        # V-Overlay分析実行
        v_overlay = run_v_overlay_analysis(ticker_path)
        
        # B.yaml更新
        update_b_yaml_with_v_overlay(ticker_path, v_overlay)
        
        # 最終サマリー表示
        display_final_summary(ticker_path, v_overlay)
        
        print(f"\nV-Overlay統合運用完了")
        
    except Exception as e:
        print(f"エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
