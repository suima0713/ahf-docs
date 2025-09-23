#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AHF High Contrast Evaluation v0.7.1c
ハイコントラスト版星判定システムの統合実行
①RSS + ②α3/α5 + ③TRI-3+V-Overlay 2.0
"""

import json
import os
import sys
import subprocess
from typing import Dict, Any

def run_evaluation_pipeline(ticker: str) -> Dict[str, Any]:
    """
    ハイコントラスト版評価パイプラインの実行
    """
    ticker_dir = os.path.join("tickers", ticker, "current")
    triage_file = os.path.join(ticker_dir, "triage.json")
    facts_file = os.path.join(ticker_dir, "facts.md")
    
    if not all(os.path.exists(f) for f in [triage_file, facts_file]):
        return {"error": "必要なファイルが見つかりません"}
    
    results = {
        "ticker": ticker,
        "pipeline": "high_contrast_v071c",
        "steps": []
    }
    
    try:
        # ①RSS算定
        print("=== ①RSS算定 ===")
        rss_result = subprocess.run([
            sys.executable, "ahf_rss_calculator.py", triage_file
        ], capture_output=True, text=True, encoding='utf-8')
        
        if rss_result.returncode == 0:
            results["steps"].append({"step": "RSS", "status": "success"})
            print("RSS算定完了")
        else:
            results["steps"].append({"step": "RSS", "status": "failed", "error": rss_result.stderr})
            print(f"RSS算定エラー: {rss_result.stderr}")
        
        # ②αスコア算定
        print("=== ②αスコア算定 ===")
        alpha_result = subprocess.run([
            sys.executable, "ahf_alpha_scoring.py", triage_file, facts_file
        ], capture_output=True, text=True, encoding='utf-8')
        
        if alpha_result.returncode == 0:
            results["steps"].append({"step": "Alpha", "status": "success"})
            print("αスコア算定完了")
        else:
            results["steps"].append({"step": "Alpha", "status": "failed", "error": alpha_result.stderr})
            print(f"αスコア算定エラー: {alpha_result.stderr}")
        
        # ③TRI-3+V-Overlay算定
        print("=== ③TRI-3+V-Overlay算定 ===")
        alpha_scoring_file = os.path.join(ticker_dir, "alpha_scoring.json")
        tri3_result = subprocess.run([
            sys.executable, "ahf_tri3_v_overlay.py", triage_file, alpha_scoring_file
        ], capture_output=True, text=True, encoding='utf-8')
        
        if tri3_result.returncode == 0:
            results["steps"].append({"step": "TRI3_V", "status": "success"})
            print("TRI-3+V-Overlay算定完了")
        else:
            results["steps"].append({"step": "TRI3_V", "status": "failed", "error": tri3_result.stderr})
            print(f"TRI-3+V-Overlay算定エラー: {tri3_result.stderr}")
        
        # ④アクションガイド生成
        print("=== ④アクションガイド生成 ===")
        action_result = subprocess.run([
            sys.executable, "ahf_action_guide.py", ticker
        ], capture_output=True, text=True, encoding='utf-8')
        
        if action_result.returncode == 0:
            results["steps"].append({"step": "Action", "status": "success"})
            print("アクションガイド生成完了")
        else:
            results["steps"].append({"step": "Action", "status": "failed", "error": action_result.stderr})
            print(f"アクションガイド生成エラー: {action_result.stderr}")
        
        # 結果サマリー生成
        results["summary"] = generate_summary(ticker_dir)
        
        return results
        
    except Exception as e:
        results["error"] = str(e)
        return results

def generate_summary(ticker_dir: str) -> Dict[str, Any]:
    """
    評価結果のサマリー生成
    """
    summary = {}
    
    # 各段階の結果を読み込み
    result_files = {
        "rss": "rss_calculation.json",
        "alpha": "alpha_scoring.json", 
        "tri3": "tri3_v_overlay.json",
        "action": "action_guide.json"
    }
    
    for key, filename in result_files.items():
        filepath = os.path.join(ticker_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                summary[key] = json.load(f)
    
    return summary

def main():
    if len(sys.argv) != 2:
        print("使用方法: python ahf_high_contrast_evaluation.py <TICKER>")
        sys.exit(1)
    
    ticker = sys.argv[1].upper()
    
    try:
        results = run_evaluation_pipeline(ticker)
        
        if "error" in results:
            print(f"[ERROR] {results['error']}")
            sys.exit(1)
        
        # 結果出力
        print("=== AHF High Contrast Evaluation Results (v0.7.1c) ===")
        print(f"Ticker: {results['ticker']}")
        print(f"Pipeline: {results['pipeline']}")
        print()
        
        print("実行ステップ:")
        for step in results["steps"]:
            status_icon = "✓" if step["status"] == "success" else "✗"
            print(f"  {status_icon} {step['step']}: {step['status']}")
            if step["status"] == "failed" and "error" in step:
                print(f"    エラー: {step['error']}")
        print()
        
        # サマリー表示
        if "summary" in results and results["summary"]:
            print("評価サマリー:")
            
            # RSS結果
            if "rss" in results["summary"]:
                rss = results["summary"]["rss"]
                print(f"  ①RSS: {rss['rss']} → ★{rss['star_1']}")
            
            # αスコア結果
            if "alpha" in results["summary"]:
                alpha = results["summary"]["alpha"]
                print(f"  ②α3/α5: α3={alpha['alpha3_score']}, α5={alpha['alpha5_score']} → ★{alpha['star_2']}")
            
            # TRI-3+V結果
            if "tri3" in results["summary"]:
                tri3 = results["summary"]["tri3"]
                print(f"  ③TRI-3+V: 基礎★{tri3['base_star']} → 最終★{tri3['final_star']} ({tri3['v_overlay']['category']})")
            
            # アクション結果
            if "action" in results["summary"]:
                action = results["summary"]["action"]
                print(f"  推奨アクション: {action['action']['recommendation']} {action['action']['size']}")
                print(f"  理由: {action['action']['reason']}")
        
        # 結果をJSONファイルに保存
        output_file = f"tickers/{ticker}/current/high_contrast_evaluation.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"[INFO] 結果を保存しました: {output_file}")
        
    except Exception as e:
        print(f"[ERROR] 処理エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
