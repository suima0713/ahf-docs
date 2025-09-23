#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AHF Alpha Scoring v0.7.1b
②勾配ルーブリックのα3_scoreとα5_score機械判定
Now-castルール対応（次決算待ちを強制しない）
"""

import json
import os
import sys
import yaml
from typing import Dict, List, Any, Tuple

def load_thresholds() -> Dict[str, Any]:
    """thresholds.yamlから閾値設定を読み込み"""
    thresholds_file = os.path.join(os.path.dirname(__file__), "..", "config", "thresholds.yaml")
    with open(thresholds_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def calculate_alpha3_score(gm_drift_pp: float, residual_usd: float, 
                          t1_explanations: List[str], thresholds: Dict[str, Any]) -> int:
    """
    α3_score（0/1/2）の機械判定（v0.7.2）
    
    2：|GM_drift| ≤ 0.2pp かつ Residual_GP ≤ $8M
    1：|GM_drift| ≤ 0.8pp かつ Residual_GP ≤ $8M かつ MD&Aの一次説明逐語（QoQ/YoYいずれか）
    0：上記以外
    """
    drift_threshold = thresholds["stage2"]["alpha3"]["drift_pp_threshold"]
    near_threshold = thresholds["stage2"]["alpha3"]["alpha3_near_pp"]
    residual_threshold = thresholds["stage2"]["alpha3"]["residual_gp_max_usd"]
    
    # 機械PASS条件
    if abs(gm_drift_pp) <= drift_threshold and residual_usd <= residual_threshold:
        return 2
    
    # 説明付き近接条件
    if (abs(gm_drift_pp) <= near_threshold and 
        residual_usd <= residual_threshold and 
        has_t1_explanation(t1_explanations)):
        return 1
    
    return 0

def calculate_alpha5_score(median_opex: float, actual_opex: float, 
                          t1_text: str, thresholds: Dict[str, Any]) -> int:
    """
    α5_score（0/1/2）の機械判定（v0.7.2）
    
    2：median(OpEx_grid) − OpEx_actual ≤ −$3M（改善の素地あり）
    1：−$3M < 差 ≤ −$1M かつ 効率フレーズ逐語（operating leverage/discipline/hiring pacing）
    0：上記以外
    """
    diff = median_opex - actual_opex
    strong_threshold = thresholds["stage2"]["alpha5"]["median_minus_actual_max_usd"]
    weak_band = thresholds["stage2"]["alpha5"]["alpha5_weak_band"]
    efficiency_phrases = thresholds["stage2"]["alpha5"]["efficiency_phrases"]
    
    # 改善の素地あり
    if diff <= strong_threshold:
        return 2
    
    # 弱い改善＋運用効率フレーズ
    if (weak_band[0] < diff <= weak_band[1] and 
        has_efficiency_phrases(t1_text, efficiency_phrases)):
        return 1
    
    return 0

def has_t1_explanation(explanations: List[str]) -> bool:
    """T1逐語で一次説明があるかチェック"""
    if not explanations:
        return False
    
    # QoQ/YoYの説明があるかチェック
    explanation_text = " ".join(explanations).lower()
    return any(keyword in explanation_text for keyword in 
               ["qoq", "yoy", "quarter", "year", "sequential", "year-over-year"])

def has_efficiency_phrases(t1_text: str, phrases: List[str]) -> bool:
    """T1テキストに運用効率フレーズがあるかチェック"""
    if not t1_text:
        return False
    
    text_lower = t1_text.lower()
    return any(phrase.lower() in text_lower for phrase in phrases)

def synthesize_star_2(alpha3_score: int, alpha5_score: int) -> int:
    """
    α3_scoreとα5_scoreから★2を合成（ハイコントラスト版）
    
    合計S=α3+α5：4→★5、3→★4、2→★3、1→★2、0→★1
    """
    total_score = alpha3_score + alpha5_score
    
    if total_score == 4:
        return 5
    elif total_score == 3:
        return 4
    elif total_score == 2:
        return 3
    elif total_score == 1:
        return 2
    else:  # total_score == 0
        return 1

def process_alpha_scoring(triage_file: str, facts_file: str) -> Dict[str, Any]:
    """
    α3_scoreとα5_scoreの算定処理
    """
    # triage.json読み込み
    with open(triage_file, 'r', encoding='utf-8') as f:
        triage_data = json.load(f)
    
    # facts.md読み込み
    with open(facts_file, 'r', encoding='utf-8') as f:
        facts_content = f.read()
    
    # 閾値設定読み込み
    thresholds = load_thresholds()
    
    confirmed_items = triage_data.get("CONFIRMED", [])
    
    # 必要なKPI値を取得
    gm_drift_pp = 0
    residual_usd = 0
    median_opex = 0
    actual_opex = 0
    
    for item in confirmed_items:
        if item["kpi"] == "GM_drift_pp":
            gm_drift_pp = item["value"]
        elif item["kpi"] == "Residual_USD":
            residual_usd = item["value"]
        elif item["kpi"] == "Median_OpEx_USD":
            median_opex = item["value"]
        elif item["kpi"] == "Actual_OpEx_USD":
            actual_opex = item["value"]
    
    # T1説明の抽出（facts.mdから）
    t1_explanations = extract_t1_explanations(facts_content)
    
    # α3_score算定
    alpha3_score = calculate_alpha3_score(gm_drift_pp, residual_usd, t1_explanations, thresholds)
    
    # α5_score算定
    alpha5_score = calculate_alpha5_score(median_opex, actual_opex, facts_content, thresholds)
    
    # ★2合成
    star_2 = synthesize_star_2(alpha3_score, alpha5_score)
    
    return {
        "as_of": triage_data["as_of"],
        "alpha3_score": alpha3_score,
        "alpha5_score": alpha5_score,
        "star_2": star_2,
        "inputs": {
            "gm_drift_pp": gm_drift_pp,
            "residual_usd": residual_usd,
            "median_opex": median_opex,
            "actual_opex": actual_opex
        },
        "explanation": {
            "alpha3": f"GM drift: {gm_drift_pp:.2f}pp, Residual: ${residual_usd/1000000:.1f}M",
            "alpha5": f"OpEx diff: ${(median_opex-actual_opex)/1000000:.1f}M",
            "star_2": f"α3={alpha3_score}, α5={alpha5_score} → ★{star_2}"
        }
    }

def extract_t1_explanations(facts_content: str) -> List[str]:
    """facts.mdからT1説明を抽出"""
    explanations = []
    lines = facts_content.split('\n')
    
    for line in lines:
        if '[T1-' in line and 'Core②' in line:
            # T1逐語を抽出（40語以内）
            parts = line.split('"')
            if len(parts) > 1:
                explanation = parts[1]
                if len(explanation.split()) <= 40:
                    explanations.append(explanation)
    
    return explanations

def main():
    if len(sys.argv) != 3:
        print("使用方法: python ahf_alpha_scoring.py <triage.jsonのパス> <facts.mdのパス>")
        sys.exit(1)
    
    triage_file = sys.argv[1]
    facts_file = sys.argv[2]
    
    if not os.path.exists(triage_file):
        print(f"[ERROR] triage.jsonが見つかりません: {triage_file}")
        sys.exit(1)
    
    if not os.path.exists(facts_file):
        print(f"[ERROR] facts.mdが見つかりません: {facts_file}")
        sys.exit(1)
    
    try:
        results = process_alpha_scoring(triage_file, facts_file)
        
        # 結果出力
        print("=== AHF Alpha Scoring Results (v0.7.2) ===")
        print(f"As of: {results['as_of']}")
        print()
        print(f"α3_score: {results['alpha3_score']} ({results['explanation']['alpha3']})")
        print(f"α5_score: {results['alpha5_score']} ({results['explanation']['alpha5']})")
        print(f"★2判定: {results['star_2']} ({results['explanation']['star_2']})")
        print()
        
        # 結果をJSONファイルに保存
        output_file = triage_file.replace("triage.json", "alpha_scoring.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"[INFO] 結果を保存しました: {output_file}")
        
    except Exception as e:
        print(f"[ERROR] 処理エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
