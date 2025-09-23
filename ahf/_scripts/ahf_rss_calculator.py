#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AHF RSS Calculator v0.7.1c
①長期右肩（★1–5）— Right-Shoulder Score（RSS）
ハイコントラスト版星判定システム
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

def calculate_rss(confirmed_items: List[Dict[str, Any]], thresholds: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
    """
    RSS = +2·I(DR_qoq ≥ +8%  or  Bookings_qoq ≥ +10%)
        +1·I(DR_qoq ∈ [0,+8%))
        +1·I(Paid↑ or ARPU↑)
        +1·I(CL↑ and CA↓)
        −1·I(DR_qoq < 0 or (Paid↓ and ARPU↓))
    """
    rss = 0
    details = {}
    
    # 各KPI値を取得
    dr_qoq = 0
    bookings_qoq = 0
    paid_change = 0
    arpu_change = 0
    cl_change = 0
    ca_change = 0
    
    for item in confirmed_items:
        if item["kpi"] == "DR_qoq_pct":
            dr_qoq = item["value"]
        elif item["kpi"] == "Bookings_qoq_pct":
            bookings_qoq = item["value"]
        elif item["kpi"] == "Paid_users_change_pct":
            paid_change = item["value"]
        elif item["kpi"] == "ARPU_change_pct":
            arpu_change = item["value"]
        elif item["kpi"] == "CL_change_pct":
            cl_change = item["value"]
        elif item["kpi"] == "CA_change_pct":
            ca_change = item["value"]
    
    # 閾値取得
    dr_high = thresholds["stage1"]["rs_dr_high"]
    bookings_high = thresholds["stage1"]["rs_bookings_high"]
    
    # +2点: DR_qoq ≥ +8% or Bookings_qoq ≥ +10%
    if dr_qoq >= dr_high or bookings_qoq >= bookings_high:
        rss += 2
        details["high_growth"] = True
    else:
        details["high_growth"] = False
    
    # +1点: DR_qoq ∈ [0,+8%)
    if 0 <= dr_qoq < dr_high:
        rss += 1
        details["moderate_growth"] = True
    else:
        details["moderate_growth"] = False
    
    # +1点: Paid↑ or ARPU↑
    if paid_change > 0 or arpu_change > 0:
        rss += 1
        details["user_metrics_up"] = True
    else:
        details["user_metrics_up"] = False
    
    # +1点: CL↑ and CA↓
    if cl_change > 0 and ca_change < 0:
        rss += 1
        details["balance_improvement"] = True
    else:
        details["balance_improvement"] = False
    
    # -1点: DR_qoq < 0 or (Paid↓ and ARPU↓)
    if dr_qoq < 0 or (paid_change < 0 and arpu_change < 0):
        rss -= 1
        details["negative_metrics"] = True
    else:
        details["negative_metrics"] = False
    
    return rss, details

def calculate_star_1(rss: int) -> int:
    """
    星割当：RSS≥4→★5／=3→★4／=2→★3／=1→★2／≤0→★1
    """
    if rss >= 4:
        return 5
    elif rss == 3:
        return 4
    elif rss == 2:
        return 3
    elif rss == 1:
        return 2
    else:
        return 1

def check_dr_guard(confirmed_items: List[Dict[str, Any]]) -> bool:
    """
    ガード：DR 2Q連続減 で★≤2に即降格
    """
    # 過去2四半期のDR_qoqを取得（実装では簡略化）
    dr_history = []
    for item in confirmed_items:
        if "DR_qoq" in item["kpi"] and "Q" in item["kpi"]:
            dr_history.append(item["value"])
    
    # 直近2Qが連続で負の場合
    if len(dr_history) >= 2:
        return dr_history[-1] < 0 and dr_history[-2] < 0
    
    return False

def process_rss_calculation(triage_file: str) -> Dict[str, Any]:
    """
    RSS算定処理
    """
    # triage.json読み込み
    with open(triage_file, 'r', encoding='utf-8') as f:
        triage_data = json.load(f)
    
    # 閾値設定読み込み
    thresholds = load_thresholds()
    
    confirmed_items = triage_data.get("CONFIRMED", [])
    
    # RSS算定
    rss, details = calculate_rss(confirmed_items, thresholds)
    
    # ★1算定
    star_1 = calculate_star_1(rss)
    
    # ガードチェック
    dr_guard = check_dr_guard(confirmed_items)
    if dr_guard and star_1 > 2:
        star_1 = 2
        details["dr_guard_triggered"] = True
    else:
        details["dr_guard_triggered"] = False
    
    return {
        "as_of": triage_data["as_of"],
        "rss": rss,
        "star_1": star_1,
        "details": details,
        "inputs": {
            "dr_qoq": next((item["value"] for item in confirmed_items if item["kpi"] == "DR_qoq_pct"), 0),
            "bookings_qoq": next((item["value"] for item in confirmed_items if item["kpi"] == "Bookings_qoq_pct"), 0),
            "paid_change": next((item["value"] for item in confirmed_items if item["kpi"] == "Paid_users_change_pct"), 0),
            "arpu_change": next((item["value"] for item in confirmed_items if item["kpi"] == "ARPU_change_pct"), 0),
            "cl_change": next((item["value"] for item in confirmed_items if item["kpi"] == "CL_change_pct"), 0),
            "ca_change": next((item["value"] for item in confirmed_items if item["kpi"] == "CA_change_pct"), 0)
        }
    }

def main():
    if len(sys.argv) != 2:
        print("使用方法: python ahf_rss_calculator.py <triage.jsonのパス>")
        sys.exit(1)
    
    triage_file = sys.argv[1]
    
    if not os.path.exists(triage_file):
        print(f"[ERROR] triage.jsonが見つかりません: {triage_file}")
        sys.exit(1)
    
    try:
        results = process_rss_calculation(triage_file)
        
        # 結果出力
        print("=== AHF RSS Calculation Results (v0.7.2) ===")
        print(f"As of: {results['as_of']}")
        print()
        print(f"RSS: {results['rss']}")
        print(f"★1判定: {results['star_1']}")
        print()
        print("詳細:")
        for key, value in results['details'].items():
            print(f"  {key}: {value}")
        print()
        print("入力値:")
        for key, value in results['inputs'].items():
            print(f"  {key}: {value}")
        
        # 結果をJSONファイルに保存
        output_file = triage_file.replace("triage.json", "rss_calculation.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"[INFO] 結果を保存しました: {output_file}")
        
    except Exception as e:
        print(f"[ERROR] 処理エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
