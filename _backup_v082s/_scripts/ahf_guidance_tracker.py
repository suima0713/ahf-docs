#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AHF Guidance Tracker v0.3.2a
ガイダンス → 実績 → 資金配分の一連の糸を追跡
"""

import json
import os
import sys
import re
from datetime import datetime
from typing import Dict, List, Any, Optional

def evaluate_impact_cards(triage_data: Dict[str, Any], impact_cards: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    impact_cardsの評価（全部T1で揃った時だけ実行）
    """
    confirmed_items = {item["kpi"]: item["value"] for item in triage_data.get("CONFIRMED", [])}
    
    results = {}
    
    for card in impact_cards:
        card_id = card["id"]
        inputs = card["inputs"]
        
        # 全入力がT1で揃っているかチェック
        if all(input_kpi in confirmed_items for input_kpi in inputs):
            try:
                # 式を評価
                expr = card["expr"]
                for input_kpi in inputs:
                    expr = expr.replace(input_kpi, str(confirmed_items[input_kpi]))
                
                result = eval(expr)
                
                # ゲート判定
                gates = card["gates"]
                gate_status = "neutral"
                
                if "up" in gates:
                    up_condition = gates["up"].replace(">=", ">=").replace("<=", "<=").replace(">", ">").replace("<", "<")
                    if eval(f"{result} {up_condition}"):
                        gate_status = "up"
                
                if "down" in gates:
                    down_condition = gates["down"].replace(">=", ">=").replace("<=", "<=").replace(">", ">").replace("<", "<")
                    if eval(f"{result} {down_condition}"):
                        gate_status = "down"
                
                results[card_id] = {
                    "value": result,
                    "gate_status": gate_status,
                    "inputs_available": True
                }
                
            except Exception as e:
                results[card_id] = {
                    "value": None,
                    "gate_status": "error",
                    "inputs_available": True,
                    "error": str(e)
                }
        else:
            missing_inputs = [inp for inp in inputs if inp not in confirmed_items]
            results[card_id] = {
                "value": None,
                "gate_status": "skipped",
                "inputs_available": False,
                "missing_inputs": missing_inputs
            }
    
    return results

def update_hypotheses_status(triage_data: Dict[str, Any], impact_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    HYPOTHESESのステータス更新
    """
    hypotheses = triage_data.get("HYPOTHESES", [])
    
    for hypothesis in hypotheses:
        hypothesis_id = hypothesis["id"]
        
        if hypothesis_id == "H6_guidance_adherence":
            # guidance_mapeの結果で判定
            guidance_mape_result = impact_results.get("guidance_mape", {})
            if guidance_mape_result.get("gate_status") == "up":
                hypothesis["status"] = "confirmed"
            elif guidance_mape_result.get("gate_status") == "down":
                hypothesis["status"] = "falsified"
            else:
                hypothesis["status"] = "pending"
        
        elif hypothesis_id == "H7_cash_conversion_and_allocation":
            # fcf_conversionとcapex_intensityの結果で判定
            fcf_result = impact_results.get("fcf_conversion", {})
            capex_result = impact_results.get("capex_intensity", {})
            
            if (fcf_result.get("gate_status") == "up" and 
                capex_result.get("gate_status") == "up"):
                hypothesis["status"] = "confirmed"
            elif (fcf_result.get("gate_status") == "down" or 
                  capex_result.get("gate_status") == "down"):
                hypothesis["status"] = "falsified"
            else:
                hypothesis["status"] = "pending"
    
    triage_data["HYPOTHESES"] = hypotheses
    return triage_data

def generate_insights(impact_results: Dict[str, Any], hypotheses: List[Dict[str, Any]]) -> List[str]:
    """
    インサイト生成
    """
    insights = []
    
    # ガイダンス信頼性
    guidance_mape = impact_results.get("guidance_mape", {})
    if guidance_mape.get("gate_status") == "up":
        insights.append("✅ 予測信頼性↑: guidance_mapeが5%以下で予測精度が高い")
    elif guidance_mape.get("gate_status") == "down":
        insights.append("⚠️ 予測信頼性↓: guidance_mapeが10%以上で予測精度に課題")
    
    # キャッシュ変換と資本配分
    fcf_conversion = impact_results.get("fcf_conversion", {})
    capex_intensity = impact_results.get("capex_intensity", {})
    
    if (fcf_conversion.get("gate_status") == "up" and 
        capex_intensity.get("gate_status") == "up"):
        insights.append("✅ 戦略の頑健性↑: FCF変換率70%以上かつCapEx強度5%以下で自社株/配当/戦略M&Aの余地")
    elif (fcf_conversion.get("gate_status") == "down" or 
          capex_intensity.get("gate_status") == "down"):
        insights.append("⚠️ 戦略の頑健性↓: 再投資/回収サイクルの歪みをC（反証）に回す")
    
    # 仮説ステータス
    for hypothesis in hypotheses:
        if hypothesis["status"] == "confirmed":
            insights.append(f"✅ 仮説確認: {hypothesis['id']}")
        elif hypothesis["status"] == "falsified":
            insights.append(f"❌ 仮説反証: {hypothesis['id']}")
    
    return insights

def process_guidance_tracking(ticker_path: str) -> None:
    """
    ガイダンス追跡のメイン処理
    """
    triage_file = os.path.join(ticker_path, "triage.json")
    impact_cards_file = os.path.join(ticker_path, "impact_cards.json")
    
    if not os.path.exists(triage_file):
        print(f"[ERROR] triage.jsonが見つかりません: {triage_file}")
        return
    
    if not os.path.exists(impact_cards_file):
        print(f"[ERROR] impact_cards.jsonが見つかりません: {impact_cards_file}")
        return
    
    try:
        # ファイル読み込み
        with open(triage_file, 'r', encoding='utf-8') as f:
            triage_data = json.load(f)
        
        with open(impact_cards_file, 'r', encoding='utf-8') as f:
            impact_cards = json.load(f)
        
        # impact_cards評価
        impact_results = evaluate_impact_cards(triage_data, impact_cards)
        
        # HYPOTHESESステータス更新
        triage_data = update_hypotheses_status(triage_data, impact_results)
        
        # インサイト生成
        insights = generate_insights(impact_results, triage_data.get("HYPOTHESES", []))
        
        # 結果表示
        print("=== AHF Guidance Tracking Results ===")
        print(f"As of: {triage_data['as_of']}")
        print()
        
        print("Impact Cards Evaluation:")
        for card_id, result in impact_results.items():
            if result["inputs_available"]:
                if result["gate_status"] == "skipped":
                    print(f"  {card_id}: スキップ（入力不足: {result['missing_inputs']}）")
                else:
                    print(f"  {card_id}: {result['value']:.2f} ({result['gate_status']})")
            else:
                print(f"  {card_id}: スキップ（入力不足: {result['missing_inputs']}）")
        
        print()
        print("Hypotheses Status:")
        for hypothesis in triage_data.get("HYPOTHESES", []):
            print(f"  {hypothesis['id']}: {hypothesis['status']}")
        
        print()
        print("Insights:")
        for insight in insights:
            print(f"  {insight}")
        
        # ファイル保存
        with open(triage_file, 'w', encoding='utf-8') as f:
            json.dump(triage_data, f, ensure_ascii=False, indent=2)
        
        # 結果をJSONファイルに保存
        results_file = os.path.join(ticker_path, "guidance_tracking_results.json")
        tracking_results = {
            "as_of": triage_data["as_of"],
            "impact_results": impact_results,
            "hypotheses": triage_data.get("HYPOTHESES", []),
            "insights": insights
        }
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(tracking_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n[INFO] 結果を保存しました: {results_file}")
        
    except Exception as e:
        print(f"[ERROR] 処理エラー: {e}")
        sys.exit(1)

def main():
    if len(sys.argv) != 2:
        print("使用方法: python ahf_guidance_tracker.py <ticker_path>")
        print("例: python ahf_guidance_tracker.py ahf/tickers/WOLF/current")
        sys.exit(1)
    
    ticker_path = sys.argv[1]
    process_guidance_tracking(ticker_path)

if __name__ == "__main__":
    main()
