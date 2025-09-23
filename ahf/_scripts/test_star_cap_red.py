#!/usr/bin/env python3
"""
★上限自動キャップ機能テスト（V=Redケース）
"""

import json
import yaml
from pathlib import Path

def create_red_test_case():
    """V=Redテストケース作成"""
    
    # V=Redのテストデータ
    red_test_data = {
        "as_of": "2025-01-15",
        "ticker": "DUOL",
        "v_level": "Red",
        "reason": "EV/Sales(Fwd) 15.0× (過熱域) / Rule-of-40 35.0% (耐性不足)",
        "ev_sales_fwd": 15.0,
        "rule_of_40": 35.0,
        "guidance_upside": False,
        "star_cap_applied": True,
        "v_badge": "🔴 V=Red",
        "half_price_scenario": {
            "current_multiple": 15.0,
            "target_multiple": 6.0,
            "compression_rate": 60.0,
            "feasible": True
        },
        "triggers": {
            "improvement": ["ガイダンス上方修正", "EV/Sales(Fwd) ≤ 10×"],
            "deterioration": ["EV/Sales(Fwd) ≥ 14×", "Rule-of-40 < 40"]
        }
    }
    
    # テスト用V-Overlay結果ファイル作成
    output_path = Path("../../ahf/tickers/DUOL/current/v_overlay_result_red_test.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(red_test_data, f, ensure_ascii=False, indent=2)
    
    print(f"V=Redテストケースを作成: {output_path}")
    
    # テスト用B.yaml作成
    b_test_data = {
        "horizon": {
            "6M": {"verdict": "Go", "ΔIRRbp": 200},
            "1Y": {"verdict": "Go", "ΔIRRbp": 300},
            "3Y": {"verdict": "保留", "ΔIRRbp": 100},
            "5Y": {"verdict": "No-Go", "ΔIRRbp": -100}
        },
        "stance": {
            "decision": "Proceed",
            "size": "Med",
            "reason": "事業T1で健在だが、V=Redで価格過熱"
        },
        "kpi_watch": [
            {
                "name": "Revenue Growth Momentum",
                "current": "+41% YoY / +9.3% QoQ",
                "target": "Q3ガイダンス$257-261M達成・FY25$1,011-1,019M軌道"
            },
            {
                "name": "GM Optimization (AI Cost)",
                "current": "72.4% (+130bps QoQ)",
                "target": "AIコスト最適化継続・広告ビジネス堅調維持"
            }
        ]
    }
    
    b_test_path = Path("../../ahf/tickers/DUOL/current/B_red_test.yaml")
    with open(b_test_path, 'w', encoding='utf-8') as f:
        yaml.dump(b_test_data, f, default_flow_style=False, allow_unicode=True, indent=2)
    
    print(f"B.yamlテストケースを作成: {b_test_path}")
    
    return output_path, b_test_path

def test_star_cap_red():
    """V=Redでの★上限自動キャップテスト"""
    
    print("=== V=Red ★上限自動キャップテスト ===")
    
    # テストケース作成
    v_overlay_path, b_yaml_path = create_red_test_case()
    
    # V-Overlay結果読み込み
    with open(v_overlay_path, 'r', encoding='utf-8') as f:
        v_overlay = json.load(f)
    
    # B.yaml読み込み
    with open(b_yaml_path, 'r', encoding='utf-8') as f:
        b_data = yaml.safe_load(f)
    
    # ★上限自動キャップ適用
    v_level = v_overlay.get("v_level")
    star_cap_applied = v_overlay.get("star_cap_applied", False)
    
    if v_level == "Red" and star_cap_applied:
        # ★上限=3の自動キャップ発動
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
        b_data["stance"]["star_cap_note"] = "★上限=3（V=Red自動キャップ）"
        
        print("[CRITICAL] ★上限=3の自動キャップ発動")
        print(f"理由: {v_overlay.get('reason', 'N/A')}")
    
    # 結果表示
    print(f"\nV-Overlay: {v_overlay.get('v_badge')}")
    print(f"理由: {v_overlay.get('reason')}")
    print(f"EV/Sales(Fwd): {v_overlay.get('ev_sales_fwd')}×")
    print(f"Rule-of-40: {v_overlay.get('rule_of_40')}%")
    
    print(f"\n★キャップ状態:")
    star_cap = b_data.get("star_cap", {})
    print(f"  有効: {'Yes' if star_cap.get('enabled') else 'No'}")
    print(f"  上限: {star_cap.get('max_stars', 5)}★")
    print(f"  理由: {star_cap.get('reason', 'なし')}")
    
    print(f"\nスタンス:")
    stance = b_data.get("stance", {})
    print(f"  決定: {stance.get('decision')}")
    print(f"  サイズ: {stance.get('size')}")
    print(f"  理由: {stance.get('reason')}")
    if "star_cap_note" in stance:
        print(f"  キャップ注記: {stance['star_cap_note']}")
    
    # 更新されたB.yamlを保存
    with open(b_yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(b_data, f, default_flow_style=False, allow_unicode=True, indent=2)
    
    print(f"\nテスト結果を保存: {b_yaml_path}")
    
    # クリーンアップ
    print("\n=== クリーンアップ ===")
    print("テストファイルを削除...")
    v_overlay_path.unlink()
    b_yaml_path.unlink()
    print("テスト完了")

if __name__ == "__main__":
    test_star_cap_red()
