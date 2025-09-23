#!/usr/bin/env python3
"""
AHF V-Overlay 表示機能
VバッジをB.yamlに統合し、マトリクス表示を更新する
"""

import json
import yaml
import sys
from pathlib import Path
from typing import Dict, Any, Optional

def load_v_overlay_result(ticker_path: str) -> Optional[Dict[str, Any]]:
    """V-Overlay結果読み込み"""
    v_overlay_path = Path(ticker_path) / "current" / "v_overlay_result.json"
    
    if not v_overlay_path.exists():
        return None
    
    try:
        with open(v_overlay_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return None

def load_b_yaml(ticker_path: str) -> Optional[Dict[str, Any]]:
    """B.yaml読み込み"""
    b_yaml_path = Path(ticker_path) / "current" / "B.yaml"
    
    if not b_yaml_path.exists():
        return None
    
    try:
        with open(b_yaml_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except (yaml.YAMLError, FileNotFoundError):
        return None

def update_b_yaml_with_v_overlay(b_data: Dict[str, Any], v_overlay: Dict[str, Any]) -> Dict[str, Any]:
    """B.yamlにV-Overlay情報を統合"""
    
    # V-Overlay情報を追加
    if "v_overlay" not in b_data:
        b_data["v_overlay"] = {}
    
    b_data["v_overlay"] = {
        "level": v_overlay.get("v_level"),
        "badge": v_overlay.get("v_badge"),
        "reason": v_overlay.get("reason"),
        "ev_sales_fwd": v_overlay.get("ev_sales_fwd"),
        "rule_of_40": v_overlay.get("rule_of_40"),
        "star_cap_applied": v_overlay.get("star_cap_applied", False),
        "half_price_scenario": v_overlay.get("half_price_scenario", {}),
        "triggers": v_overlay.get("triggers", {})
    }
    
    # スタンスにVバッジ情報を統合
    if "stance" in b_data:
        original_reason = b_data["stance"].get("reason", "")
        v_badge = v_overlay.get("v_badge", "")
        
        # Vバッジ情報を理由に追加
        b_data["stance"]["v_badge"] = v_badge
        
        # VレベルがRedの場合は★上限キャップを明記
        if v_overlay.get("star_cap_applied", False):
            b_data["stance"]["star_cap_note"] = "★上限=3（V=Red自動キャップ）"
    
    return b_data

def generate_v_overlay_summary(v_overlay: Dict[str, Any]) -> str:
    """V-Overlay要約生成"""
    level = v_overlay.get("v_level", "Unknown")
    badge = v_overlay.get("v_badge", "")
    reason = v_overlay.get("reason", "")
    ev_sales = v_overlay.get("ev_sales_fwd")
    rule_40 = v_overlay.get("rule_of_40")
    
    summary_lines = [
        f"V-Overlay: {badge}",
        f"理由: {reason}",
    ]
    
    if ev_sales is not None:
        summary_lines.append(f"EV/Sales(Fwd): {ev_sales:.1f}×")
    
    if rule_40 is not None:
        summary_lines.append(f"Rule-of-40: {rule_40:.1f}%")
    
    # 半値シナリオ情報
    half_scenario = v_overlay.get("half_price_scenario", {})
    if half_scenario.get("feasible", False):
        compression_rate = half_scenario.get("compression_rate")
        if compression_rate is not None:
            summary_lines.append(f"半値シナリオ: 圧縮率{compression_rate:.1f}%（リレーティング可能）")
    
    return "\n".join(summary_lines)

def display_enhanced_matrix(b_data: Dict[str, Any], v_overlay: Dict[str, Any]):
    """拡張マトリクス表示"""
    print("=== AHF 拡張マトリクス（V-Overlay統合） ===")
    
    # 基本情報
    print(f"ティッカー: {b_data.get('ticker', 'N/A')}")
    print(f"As-of: {b_data.get('as_of', 'N/A')}")
    
    # スタンス情報
    stance = b_data.get("stance", {})
    decision = stance.get("decision", "N/A")
    size = stance.get("size", "N/A")
    reason = stance.get("reason", "N/A")
    v_badge = stance.get("v_badge", "")
    
    print(f"\nスタンス: {decision} ({size})")
    if v_badge:
        print(f"Vバッジ: {v_badge}")
    
    # ★上限キャップ情報
    star_cap_note = stance.get("star_cap_note")
    if star_cap_note:
        print(f"[CRITICAL] {star_cap_note}")
    
    # V-Overlay要約
    v_summary = generate_v_overlay_summary(v_overlay)
    print(f"\n{v_summary}")
    
    # Horizon情報
    horizon = b_data.get("horizon", {})
    if horizon:
        print("\nHorizon:")
        for period, data in horizon.items():
            verdict = data.get("verdict", "N/A")
            delta_irr = data.get("ΔIRRbp", "N/A")
            print(f"  {period}: {verdict} (ΔIRR: {delta_irr}bp)")
    
    # KPI Watch
    kpi_watch = b_data.get("kpi_watch", [])
    if kpi_watch:
        print("\nKPI Watch:")
        for kpi in kpi_watch[:2]:  # 最初の2つのみ表示
            name = kpi.get("name", "N/A")
            current = kpi.get("current", "N/A")
            target = kpi.get("target", "N/A")
            print(f"  {name}: {current} → {target}")

def main():
    """メイン実行"""
    if len(sys.argv) != 2:
        print("使用法: python ahf_v_overlay_display.py <ticker_path>")
        sys.exit(1)
    
    ticker_path = sys.argv[1]
    
    try:
        # V-Overlay結果読み込み
        v_overlay = load_v_overlay_result(ticker_path)
        if not v_overlay:
            print(f"V-Overlay結果が見つかりません: {ticker_path}/current/v_overlay_result.json")
            sys.exit(1)
        
        # B.yaml読み込み
        b_data = load_b_yaml(ticker_path)
        if not b_data:
            print(f"B.yamlが見つかりません: {ticker_path}/current/B.yaml")
            sys.exit(1)
        
        # B.yamlにV-Overlay情報を統合
        updated_b_data = update_b_yaml_with_v_overlay(b_data, v_overlay)
        
        # 拡張マトリクス表示
        display_enhanced_matrix(updated_b_data, v_overlay)
        
        # 更新されたB.yamlを保存
        b_yaml_path = Path(ticker_path) / "current" / "B.yaml"
        with open(b_yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(updated_b_data, f, default_flow_style=False, allow_unicode=True, indent=2)
        
        print(f"\nB.yamlを更新: {b_yaml_path}")
        
    except Exception as e:
        print(f"エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
