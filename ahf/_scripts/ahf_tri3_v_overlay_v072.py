#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AHF TRI-3 + V-Overlay 2.0 Integration v0.7.2β
③認知ギャップ（★1–5）— V基準星付け + T/R加点システム + 確信度表示
ナウキャスト化：データ欠落≠低評価の歪み解消
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

def calculate_tri3_tr_scores(confirmed_items: List[Dict[str, Any]]) -> Tuple[int, int]:
    """
    T/Rスコアの取得（0-2の数値）
    """
    t_score = 0
    r_score = 0
    
    for item in confirmed_items:
        if item["kpi"] == "T_score":
            t_score = item["value"]
        elif item["kpi"] == "R_score":
            r_score = item["value"]
    
    return t_score, r_score

def calculate_v_based_stars(v_result: VOverlayResult) -> int:
    """
    V基準の星付け（v0.7.2β）
    Green → ★3 / Amber → ★2 / Red → ★1
    """
    if v_result.category == "Green":
        return 3
    elif v_result.category == "Amber":
        return 2
    elif v_result.category == "Red":
        return 1
    else:
        return 2  # デフォルト

def calculate_tr_adders(t_score: int, r_score: int) -> int:
    """
    T+R加点システム（v0.7.2β）
    T+R≥3 → +1★、T+R=4 → さらに +1★（上限★5）
    """
    total_score = t_score + r_score
    
    if total_score >= 4:
        return 2  # T+R=4 → +2★
    elif total_score >= 3:
        return 1  # T+R≥3 → +1★
    else:
        return 0  # 加点なし

def calculate_confidence(t_score: int, r_score: int, v_result: VOverlayResult, 
                        confirmed_items: List[Dict[str, Any]]) -> float:
    """
    確信度計算（v0.7.2β）
    Base60% + Bridge整合+10pp + (CL↑&CA↓)+5pp + ガイダンス明瞭+5pp − 新四半期未着地−10pp
    50–95%でクリップ
    """
    confidence = 60.0  # ベース60%
    
    # Bridge整合チェック（簡略化：T/R両方が1以上）
    if t_score >= 1 and r_score >= 1:
        confidence += 10.0
    
    # CL↑&CA↓チェック（簡略化：収益向上指標）
    revenue_growth_items = [item for item in confirmed_items 
                           if "revenue" in item["kpi"].lower() and "growth" in item["kpi"].lower()]
    if revenue_growth_items:
        confidence += 5.0
    
    # ガイダンス明瞭チェック
    guidance_items = [item for item in confirmed_items 
                     if "guidance" in item["kpi"].lower()]
    if guidance_items:
        confidence += 5.0
    
    # 新四半期未着地チェック（簡略化：最新データが3ヶ月以上古い）
    # 実際の実装では日付比較を行う
    confidence -= 10.0  # 仮の減点
    
    # 50–95%でクリップ
    return max(50.0, min(95.0, confidence))

def apply_alpha_bonus(final_star: int, alpha3_score: int, alpha5_score: int) -> Tuple[int, bool]:
    """
    既存のボーナス★（α3=2 かつ α5=2 → +1★、上限★5）維持
    """
    if alpha3_score == 2 and alpha5_score == 2:
        bonus_star = min(5, final_star + 1)
        return bonus_star, True
    else:
        return final_star, False

def process_tri3_v_overlay_v072(triage_file: str, alpha_scoring_file: str) -> Dict[str, Any]:
    """
    TRI-3 + V-Overlay 2.0統合処理（v0.7.2β）
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
    
    # T/Rスコア取得
    t_score, r_score = calculate_tri3_tr_scores(confirmed_items)
    
    # V基準の星付け
    v_base_stars = calculate_v_based_stars(v_result)
    
    # T/R加点システム
    tr_adders = calculate_tr_adders(t_score, r_score)
    
    # 最終★計算
    final_star = min(5, v_base_stars + tr_adders)
    
    # αボーナス適用
    final_star_with_bonus, bonus_applied = apply_alpha_bonus(
        final_star, 
        alpha_results["alpha3_score"], 
        alpha_results["alpha5_score"]
    )
    
    # 確信度計算
    confidence = calculate_confidence(t_score, r_score, v_result, confirmed_items)
    
    return {
        "as_of": triage_data["as_of"],
        "tri3": {
            "T": t_score,
            "R": r_score,
            "V": v_result.category,
            "star": final_star_with_bonus,
            "bonus_applied": bonus_applied
        },
        "valuation_overlay": {
            "status": v_result.category,
            "v_score": v_result.v_score,
            "ev_sales": v_result.ev_sales,
            "rule_of_40": v_result.rule_of_40,
            "hysteresis_applied": v_result.hysteresis_applied
        },
        "confidence": confidence,
        "star_calculation": {
            "v_base": v_base_stars,
            "tr_adders": tr_adders,
            "alpha_bonus": 1 if bonus_applied else 0,
            "final": final_star_with_bonus
        },
        "inputs": {
            "ev_sales": ev_sales,
            "rule_of_40": rule_of_40,
            "alpha3_score": alpha_results["alpha3_score"],
            "alpha5_score": alpha_results["alpha5_score"]
        },
        "notes": {
            "tri3.star_rule": "V_base_plus_TR_adders"
        }
    }

def main():
    if len(sys.argv) != 3:
        print("使用方法: python ahf_tri3_v_overlay_v072.py <triage.jsonのパス> <alpha_scoring.jsonのパス>")
        sys.exit(1)
    
    triage_file = sys.argv[1]
    alpha_scoring_file = sys.argv[2]
    
    if not os.path.exists(triage_file):
        print(f"[ERROR] triage.jsonが見つかりません: {triage_file}")
        sys.exit(1)
    
    try:
        results = process_tri3_v_overlay_v072(triage_file, alpha_scoring_file)
        
        # 結果出力
        print("=== AHF TRI-3 + V-Overlay 2.0 Results (v0.7.2β) ===")
        print(f"As of: {results['as_of']}")
        print()
        print("③認知ギャップ（ナウキャスト化）:")
        print(f"  ★: {results['tri3']['star']} (V基準{results['star_calculation']['v_base']}+TR加点{results['star_calculation']['tr_adders']}+αボーナス{results['star_calculation']['alpha_bonus']})")
        print(f"  確信度: {results['confidence']:.0f}%")
        print(f"  T/R: {results['tri3']['T']}/{results['tri3']['R']}")
        print(f"  V: {results['tri3']['V']}")
        print()
        print("V-Overlay:")
        print(f"  Vスコア: {results['valuation_overlay']['v_score']:.3f}")
        print(f"  EV/Sales: {results['valuation_overlay']['ev_sales']:.1f}")
        print(f"  Rule-of-40: {results['valuation_overlay']['rule_of_40']:.1f}")
        print(f"  ヒステリシス適用: {results['valuation_overlay']['hysteresis_applied']}")
        
        # 結果をJSONファイルに保存
        output_file = triage_file.replace("triage.json", "tri3_v_overlay_v072.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"[INFO] 結果を保存しました: {output_file}")
        
    except Exception as e:
        print(f"[ERROR] 処理エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

