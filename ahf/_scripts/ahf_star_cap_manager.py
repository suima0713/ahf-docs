#!/usr/bin/env python3
"""
AHF ★上限自動キャップ機能
V=Redの時に★上限=3の自動キャップを発動する
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

def apply_star_cap(b_data: Dict[str, Any], v_overlay: Dict[str, Any]) -> Dict[str, Any]:
    """★上限自動キャップ適用"""
    
    v_level = v_overlay.get("v_level")
    star_cap_applied = v_overlay.get("star_cap_applied", False)
    
    if v_level == "Red" and star_cap_applied:
        # ★上限=3の自動キャップ発動
        if "star_cap" not in b_data:
            b_data["star_cap"] = {}
        
        b_data["star_cap"] = {
            "enabled": True,
            "max_stars": 3,
            "reason": "V=Red自動キャップ発動",
            "applied_at": v_overlay.get("as_of", "N/A"),
            "v_level": v_level,
            "trigger_conditions": [
                "EV/Sales(Fwd) ≥ 14×",
                "Rule-of-40 < 40"
            ]
        }
        
        # スタンスにキャップ情報を追加
        if "stance" in b_data:
            if "star_cap_note" not in b_data["stance"]:
                b_data["stance"]["star_cap_note"] = "★上限=3（V=Red自動キャップ）"
        
        print("[CRITICAL] ★上限=3の自動キャップ発動")
        print(f"理由: {v_overlay.get('reason', 'N/A')}")
        
    else:
        # キャップ解除
        if "star_cap" in b_data:
            if b_data["star_cap"].get("enabled", False):
                print("[INFO] ★上限キャップ解除")
                print(f"理由: V={v_level}（キャップ条件不該当）")
            
            b_data["star_cap"]["enabled"] = False
            b_data["star_cap"]["reason"] = f"V={v_level}でキャップ解除"
        
        # スタンスからキャップ情報を削除
        if "stance" in b_data and "star_cap_note" in b_data["stance"]:
            del b_data["stance"]["star_cap_note"]
    
    return b_data

def check_star_cap_status(b_data: Dict[str, Any]) -> Dict[str, Any]:
    """★キャップ状態チェック"""
    star_cap = b_data.get("star_cap", {})
    
    status = {
        "enabled": star_cap.get("enabled", False),
        "max_stars": star_cap.get("max_stars", 5),  # デフォルト5
        "reason": star_cap.get("reason", "なし"),
        "applied_at": star_cap.get("applied_at", "N/A")
    }
    
    return status

def generate_star_cap_report(b_data: Dict[str, Any], v_overlay: Dict[str, Any]) -> str:
    """★キャップレポート生成"""
    report_lines = []
    
    # 現在の状態
    status = check_star_cap_status(b_data)
    
    report_lines.append("=== ★上限自動キャップ状態 ===")
    report_lines.append(f"有効: {'Yes' if status['enabled'] else 'No'}")
    report_lines.append(f"上限: {status['max_stars']}★")
    report_lines.append(f"理由: {status['reason']}")
    report_lines.append(f"適用日: {status['applied_at']}")
    
    # V-Overlay情報
    v_level = v_overlay.get("v_level", "N/A")
    v_reason = v_overlay.get("reason", "N/A")
    
    report_lines.append(f"\nV-Overlay: {v_level}")
    report_lines.append(f"V理由: {v_reason}")
    
    # トリガー条件
    triggers = v_overlay.get("triggers", {})
    if triggers:
        report_lines.append("\nトリガー条件:")
        
        improvement = triggers.get("improvement", [])
        if improvement:
            report_lines.append("  改善トリガー:")
            for trigger in improvement:
                report_lines.append(f"    - {trigger}")
        
        deterioration = triggers.get("deterioration", [])
        if deterioration:
            report_lines.append("  悪化トリガー:")
            for trigger in deterioration:
                report_lines.append(f"    - {trigger}")
    
    return "\n".join(report_lines)

def main():
    """メイン実行"""
    if len(sys.argv) != 2:
        print("使用法: python ahf_star_cap_manager.py <ticker_path>")
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
        
        # ★上限自動キャップ適用
        updated_b_data = apply_star_cap(b_data, v_overlay)
        
        # ★キャップレポート生成・表示
        report = generate_star_cap_report(updated_b_data, v_overlay)
        print(report)
        
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
