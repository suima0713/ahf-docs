#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AHF TRI-3 + V-Overlay 2.0 Integration v0.7.1c
③認知ギャップ（★1–5）— TRI-3＋V-Overlay（ハイコントラスト版）
"""

import json
import os
import sys
import yaml
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

# V-Overlay 2.0のインポート
sys.path.append(os.path.dirname(__file__))
from ahf_v_overlay_v2 import VOverlayEngine, VOverlayResult

def load_thresholds() -> Dict[str, Any]:
    """thresholds.yamlから閾値設定を読み込み"""
    thresholds_file = os.path.join(os.path.dirname(__file__), "..", "config", "thresholds.yaml")
    with open(thresholds_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def calculate_tri3_base_star(confirmed_items: List[Dict[str, Any]]) -> int:
    """
    T/Rで基礎★（0→1★、1–2→2★、3→3★、4→4★）
    """
    # T/Rスコアを取得（実装では簡略化）
    t_score = 0
    r_score = 0
    
    for item in confirmed_items:
        if item["kpi"] == "T_score":
            t_score = item["value"]
        elif item["kpi"] == "R_score":
            r_score = item["value"]
    
    total_score = t_score + r_score
    
    if total_score == 0:
        return 1
    elif total_score in [1, 2]:
        return 2
    elif total_score == 3:
        return 3
    elif total_score == 4:
        return 4
    else:
        return 1  # デフォルト

def apply_v_overlay_adjustment(base_star: int, v_result: VOverlayResult, 
                              alpha3_score: int, alpha5_score: int) -> Tuple[int, Dict[str, Any]]:
    """
    V-Overlay 2.0（AND＋厳密不等号＋ヒステリシス）の適用
    Amber → ★−1、Red → ★−1 & ★上限=3
    ボーナス：α3=2 かつ α5=2 の時のみ +1★（上限★5）
    """
    adjusted_star = base_star
    adjustments = {}
    
    # V-Overlay調整
    if v_result.category == "Amber":
        adjusted_star -= 1
        adjustments["v_amber"] = -1
    elif v_result.category == "Red":
        adjusted_star -= 1
        adjusted_star = min(adjusted_star, 3)  # 上限3
        adjustments["v_red"] = -1
        adjustments["v_red_cap"] = 3
    
    # ボーナス：α3=2 かつ α5=2 の時のみ +1★
    if alpha3_score == 2 and alpha5_score == 2:
        adjusted_star += 1
        adjusted_star = min(adjusted_star, 5)  # 上限5
        adjustments["alpha_bonus"] = 1
    
    # 下限チェック
    adjusted_star = max(adjusted_star, 1)
    
    return adjusted_star, adjustments

def process_tri3_v_overlay(triage_file: str, alpha_scoring_file: str) -> Dict[str, Any]:
    """
    TRI-3 + V-Overlay 2.0統合処理
    """
    # triage.json読み込み
    with open(triage_file, 'r', encoding='utf-8') as f:
        triage_data = json.load(f)
    
    # αスコア結果読み込み
    if os.path.exists(alpha_scoring_file):
        with open(alpha_scoring_file, 'r', encoding='utf-8') as f:
            alpha_results = json.load(f)
    else:
        alpha_results = {"alpha3_score": 0, "alpha5_score": 0}
    
    confirmed_items = triage_data.get("CONFIRMED", [])
    
    # 必要なKPI値を取得
    ev_sales = 0
    rule_of_40 = 0
    
    for item in confirmed_items:
        if item["kpi"] == "EV_Sales_ratio":
            ev_sales = item["value"]
        elif item["kpi"] == "Rule_of_40_pct":
            rule_of_40 = item["value"]
    
    # V-Overlay 2.0評価
    v_engine = VOverlayEngine()
    v_result = v_engine.evaluate(ev_sales, rule_of_40)
    
    # TRI-3基礎★算定
    base_star = calculate_tri3_base_star(confirmed_items)
    
    # V-Overlay調整適用
    final_star, adjustments = apply_v_overlay_adjustment(
        base_star, v_result, 
        alpha_results["alpha3_score"], 
        alpha_results["alpha5_score"]
    )
    
    return {
        "as_of": triage_data["as_of"],
        "base_star": base_star,
        "final_star": final_star,
        "v_overlay": {
            "v_score": v_result.v_score,
            "category": v_result.category,
            "ev_sales": v_result.ev_sales,
            "rule_of_40": v_result.rule_of_40,
            "star_impact": v_result.star_impact,
            "hysteresis_applied": v_result.hysteresis_applied
        },
        "adjustments": adjustments,
        "inputs": {
            "ev_sales": ev_sales,
            "rule_of_40": rule_of_40,
            "alpha3_score": alpha_results["alpha3_score"],
            "alpha5_score": alpha_results["alpha5_score"]
        }
    }

def main():
    if len(sys.argv) != 3:
        print("使用方法: python ahf_tri3_v_overlay.py <triage.jsonのパス> <alpha_scoring.jsonのパス>")
        sys.exit(1)
    
    triage_file = sys.argv[1]
    alpha_scoring_file = sys.argv[2]
    
    if not os.path.exists(triage_file):
        print(f"[ERROR] triage.jsonが見つかりません: {triage_file}")
        sys.exit(1)
    
    try:
        results = process_tri3_v_overlay(triage_file, alpha_scoring_file)
        
        # 結果出力
        print("=== AHF TRI-3 + V-Overlay 2.0 Results (v0.7.1c) ===")
        print(f"As of: {results['as_of']}")
        print()
        print(f"基礎★: {results['base_star']}")
        print(f"最終★: {results['final_star']}")
        print()
        print("V-Overlay:")
        print(f"  Vスコア: {results['v_overlay']['v_score']:.3f}")
        print(f"  区分: {results['v_overlay']['category']}")
        print(f"  EV/Sales: {results['v_overlay']['ev_sales']:.1f}")
        print(f"  Rule-of-40: {results['v_overlay']['rule_of_40']:.1f}")
        print(f"  星影響: {results['v_overlay']['star_impact']}")
        print(f"  ヒステリシス適用: {results['v_overlay']['hysteresis_applied']}")
        print()
        print("調整:")
        for key, value in results['adjustments'].items():
            print(f"  {key}: {value}")
        
        # 結果をJSONファイルに保存
        output_file = triage_file.replace("triage.json", "tri3_v_overlay.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"[INFO] 結果を保存しました: {output_file}")
        
    except Exception as e:
        print(f"[ERROR] 処理エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
