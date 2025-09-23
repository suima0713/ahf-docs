#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AHF Now-cast Recalculation v0.7.1b
8-K/Ex.99.1検出時の②勾配ルーブリック再計算
次決算待ちを強制しないNow-castルール
"""

import json
import os
import sys
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

def detect_8k_updates(facts_file: str, days_back: int = 7) -> List[Dict[str, Any]]:
    """
    8-K/Ex.99.1の更新を検出
    """
    if not os.path.exists(facts_file):
        return []
    
    with open(facts_file, 'r', encoding='utf-8') as f:
        facts_content = f.read()
    
    updates = []
    lines = facts_content.split('\n')
    
    # 過去N日以内の8-K/Ex.99.1を検索
    cutoff_date = datetime.now() - timedelta(days=days_back)
    
    for line in lines:
        if '[8-K' in line or '[Ex.99.1' in line:
            # 日付を抽出
            date_match = re.search(r'\[(\d{4}-\d{2}-\d{2})\]', line)
            if date_match:
                update_date = datetime.strptime(date_match.group(1), '%Y-%m-%d')
                if update_date >= cutoff_date:
                    updates.append({
                        'date': date_match.group(1),
                        'line': line.strip(),
                        'type': '8-K' if '[8-K' in line else 'Ex.99.1'
                    })
    
    return updates

def extract_guidance_updates(facts_content: str) -> List[Dict[str, Any]]:
    """
    facts.mdからガイダンス更新を抽出
    """
    guidance_updates = []
    lines = facts_content.split('\n')
    
    for line in lines:
        if any(keyword in line.lower() for keyword in 
               ['guidance', 'outlook', 'forecast', 'expect', 'anticipate']):
            # T1タグがあるかチェック
            if '[T1-' in line:
                date_match = re.search(r'\[(\d{4}-\d{2}-\d{2})\]', line)
                if date_match:
                    guidance_updates.append({
                        'date': date_match.group(1),
                        'content': line.strip(),
                        'type': 'guidance_update'
                    })
    
    return guidance_updates

def recalculate_alpha_scores(triage_file: str, facts_file: str, 
                           updates: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    8-K/Ex.99.1更新時のα3_scoreとα5_score再計算
    """
    # 既存のahf_alpha_scoring.pyを呼び出し
    import subprocess
    
    try:
        result = subprocess.run([
            sys.executable, 
            os.path.join(os.path.dirname(__file__), 'ahf_alpha_scoring.py'),
            triage_file, 
            facts_file
        ], capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            # 結果をJSONで読み込み
            output_file = triage_file.replace("triage.json", "alpha_scoring.json")
            if os.path.exists(output_file):
                with open(output_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        else:
            print(f"[ERROR] αスコア算定エラー: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"[ERROR] 再計算処理エラー: {e}")
        return None

def update_b_yaml_with_nowcast(b_yaml_file: str, alpha_results: Dict[str, Any]) -> bool:
    """
    B.yamlの②部分をNow-cast結果で更新
    """
    if not os.path.exists(b_yaml_file):
        return False
    
    try:
        import yaml
        
        with open(b_yaml_file, 'r', encoding='utf-8') as f:
            b_data = yaml.safe_load(f)
        
        # ②勾配の更新
        if 'slope_quality' not in b_data:
            b_data['slope_quality'] = []
        
        # Now-cast結果を追加
        nowcast_entry = {
            'as_of': alpha_results['as_of'],
            'alpha3_score': alpha_results['alpha3_score'],
            'alpha5_score': alpha_results['alpha5_score'],
            'star_2': alpha_results['star_2'],
            'source': 'nowcast_recalc',
            'explanation': alpha_results['explanation']
        }
        
        b_data['slope_quality'].append(nowcast_entry)
        
        # ファイル更新
        with open(b_yaml_file, 'w', encoding='utf-8') as f:
            yaml.dump(b_data, f, default_flow_style=False, allow_unicode=True)
        
        return True
        
    except Exception as e:
        print(f"[ERROR] B.yaml更新エラー: {e}")
        return False

def process_nowcast_recalc(ticker: str) -> Dict[str, Any]:
    """
    Now-cast再計算のメイン処理
    """
    ticker_dir = os.path.join("tickers", ticker, "current")
    triage_file = os.path.join(ticker_dir, "triage.json")
    facts_file = os.path.join(ticker_dir, "facts.md")
    b_yaml_file = os.path.join(ticker_dir, "B.yaml")
    
    if not all(os.path.exists(f) for f in [triage_file, facts_file, b_yaml_file]):
        return {"error": "必要なファイルが見つかりません"}
    
    # 8-K/Ex.99.1更新を検出
    updates = detect_8k_updates(facts_file)
    guidance_updates = extract_guidance_updates(facts_file)
    
    if not updates and not guidance_updates:
        return {"message": "8-K/Ex.99.1更新は検出されませんでした"}
    
    # αスコア再計算
    alpha_results = recalculate_alpha_scores(triage_file, facts_file, updates)
    if not alpha_results:
        return {"error": "αスコア再計算に失敗しました"}
    
    # B.yaml更新
    update_success = update_b_yaml_with_nowcast(b_yaml_file, alpha_results)
    
    return {
        "ticker": ticker,
        "as_of": alpha_results['as_of'],
        "updates_detected": len(updates) + len(guidance_updates),
        "alpha3_score": alpha_results['alpha3_score'],
        "alpha5_score": alpha_results['alpha5_score'],
        "star_2": alpha_results['star_2'],
        "b_yaml_updated": update_success,
        "updates": updates + guidance_updates
    }

def main():
    if len(sys.argv) != 2:
        print("使用方法: python ahf_nowcast_recalc.py <TICKER>")
        sys.exit(1)
    
    ticker = sys.argv[1].upper()
    
    try:
        results = process_nowcast_recalc(ticker)
        
        if "error" in results:
            print(f"[ERROR] {results['error']}")
            sys.exit(1)
        
        if "message" in results:
            print(f"[INFO] {results['message']}")
            return
        
        # 結果出力
        print("=== AHF Now-cast Recalculation Results (v0.7.1b) ===")
        print(f"Ticker: {results['ticker']}")
        print(f"As of: {results['as_of']}")
        print(f"Updates detected: {results['updates_detected']}")
        print()
        print(f"α3_score: {results['alpha3_score']}")
        print(f"α5_score: {results['alpha5_score']}")
        print(f"★2判定: {results['star_2']}")
        print(f"B.yaml updated: {results['b_yaml_updated']}")
        print()
        
        if results['updates']:
            print("検出された更新:")
            for update in results['updates']:
                print(f"  - {update['date']}: {update['type']}")
        
        # 結果をJSONファイルに保存
        output_file = f"tickers/{ticker}/current/nowcast_recalc.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"[INFO] 結果を保存しました: {output_file}")
        
    except Exception as e:
        print(f"[ERROR] 処理エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
