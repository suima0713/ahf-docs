#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AHF Matrix Calculator v0.3.2a
影レンジ算定のマトリクススクリプト
"""

import json
import os
import sys
from typing import Dict, List, Any, Tuple

def calculate_shadow_range(t1_value: float, uncertain_items: List[Dict[str, Any]], kpi_name: str) -> Tuple[float, float]:
    """
    影レンジ算定
    Floor_T1 = sum(T1項目)
    Floor_shadow = Floor_T1 + Σ(UNCERTAIN_i.value × credence_i)
    """
    shadow_contribution = 0.0
    
    for item in uncertain_items:
        if item.get("kpi") == kpi_name and item.get("status") == "Lead":
            value = item.get("value", 0)
            credence = item.get("credence_pct", 0) / 100.0
            shadow_contribution += value * credence
    
    floor_t1 = t1_value
    floor_shadow = floor_t1 + shadow_contribution
    
    return floor_t1, floor_shadow

def calculate_quality_shadow(t1_ratio: float, uncertain_items: List[Dict[str, Any]], kpi_name: str) -> Tuple[float, float]:
    """
    ②傾き（質）= Fixed-fee比率の影レンジ
    実線：T1比率
    影：T1比率 ±（UNCERTAIN寄与の方向×credence）
    """
    shadow_direction = 0.0
    
    for item in uncertain_items:
        if item.get("kpi") == kpi_name and item.get("status") == "Lead":
            value = item.get("value", 0)
            credence = item.get("credence_pct", 0) / 100.0
            # 方向性を仮定（正の値は上向き、負の値は下向き）
            shadow_direction += value * credence
    
    ratio_t1 = t1_ratio
    ratio_shadow_high = ratio_t1 + abs(shadow_direction)
    ratio_shadow_low = ratio_t1 - abs(shadow_direction)
    
    return ratio_shadow_low, ratio_shadow_high

def calculate_mispricing_shadow(ev: float, floor_t1: float, floor_shadow: float) -> Tuple[float, float]:
    """
    ④ミスプライス = EV / Floorの影レンジ
    実線：EV / Floor_T1
    影：EV / Floor_shadow（帯で表示）
    """
    mispricing_t1 = ev / floor_t1 if floor_t1 > 0 else 0
    mispricing_shadow = ev / floor_shadow if floor_shadow > 0 else 0
    
    return min(mispricing_t1, mispricing_shadow), max(mispricing_t1, mispricing_shadow)

def process_matrix_calculation(triage_file: str, impact_cards_file: str) -> Dict[str, Any]:
    """
    マトリクス算定処理
    """
    # triage.json読み込み
    with open(triage_file, 'r', encoding='utf-8') as f:
        triage_data = json.load(f)
    
    # impact_cards.json読み込み
    with open(impact_cards_file, 'r', encoding='utf-8') as f:
        impact_cards = json.load(f)
    
    confirmed_items = triage_data.get("CONFIRMED", [])
    uncertain_items = triage_data.get("UNCERTAIN", [])
    
    matrix_results = {
        "as_of": triage_data["as_of"],
        "calculations": {}
    }
    
    # ①右肩上がり（量）のKPI算定
    for card in impact_cards:
        kpi_name = card["id"]
        
        # T1値の取得
        t1_value = 0
        for item in confirmed_items:
            if item["kpi"] == kpi_name:
                t1_value = item["value"]
                break
        
        if t1_value > 0:
            # 影レンジ算定
            floor_t1, floor_shadow = calculate_shadow_range(t1_value, uncertain_items, kpi_name)
            
            matrix_results["calculations"][kpi_name] = {
                "type": "quantity",
                "t1_value": floor_t1,
                "shadow_range": [floor_t1, floor_shadow],
                "display": f"実線: {floor_t1:.2f}, 影帯: [{floor_t1:.2f}, {floor_shadow:.2f}]"
            }
    
    # ②傾き（質）のKPI算定
    quality_kpis = ["Fixed_fee_ratio", "ROIC", "ROIIC", "FCF_margin"]
    for kpi_name in quality_kpis:
        t1_ratio = 0
        for item in confirmed_items:
            if item["kpi"] == kpi_name:
                t1_ratio = item["value"]
                break
        
        if t1_ratio > 0:
            ratio_low, ratio_high = calculate_quality_shadow(t1_ratio, uncertain_items, kpi_name)
            
            matrix_results["calculations"][kpi_name] = {
                "type": "quality",
                "t1_ratio": t1_ratio,
                "shadow_range": [ratio_low, ratio_high],
                "display": f"実線: {t1_ratio:.2f}%, 影: [{ratio_low:.2f}%, {ratio_high:.2f}%]"
            }
    
    # ④ミスプライス算定
    ev = 0
    floor_t1 = 0
    for item in confirmed_items:
        if item["kpi"] == "EV":
            ev = item["value"]
        elif item["kpi"] == "FY26_Floor":
            floor_t1 = item["value"]
    
    if ev > 0 and floor_t1 > 0:
        mispricing_low, mispricing_high = calculate_mispricing_shadow(ev, floor_t1, floor_t1)
        
        matrix_results["calculations"]["Mispricing"] = {
            "type": "mispricing",
            "t1_ratio": ev / floor_t1,
            "shadow_range": [mispricing_low, mispricing_high],
            "display": f"実線: {ev/floor_t1:.2f}x, 影帯: [{mispricing_low:.2f}x, {mispricing_high:.2f}x]"
        }
    
    return matrix_results

def main():
    if len(sys.argv) != 3:
        print("使用方法: python ahf_matrix_calculator.py <triage.jsonのパス> <impact_cards.jsonのパス>")
        sys.exit(1)
    
    triage_file = sys.argv[1]
    impact_cards_file = sys.argv[2]
    
    if not os.path.exists(triage_file):
        print(f"[ERROR] triage.jsonが見つかりません: {triage_file}")
        sys.exit(1)
    
    if not os.path.exists(impact_cards_file):
        print(f"[ERROR] impact_cards.jsonが見つかりません: {impact_cards_file}")
        sys.exit(1)
    
    try:
        results = process_matrix_calculation(triage_file, impact_cards_file)
        
        # 結果出力
        print("=== AHF Matrix Calculation Results ===")
        print(f"As of: {results['as_of']}")
        print()
        
        for kpi, calc in results["calculations"].items():
            print(f"{kpi} ({calc['type']}):")
            print(f"  {calc['display']}")
            print()
        
        # 結果をJSONファイルに保存
        output_file = triage_file.replace("triage.json", "matrix_results.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"[INFO] 結果を保存しました: {output_file}")
        
    except Exception as e:
        print(f"[ERROR] 処理エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

