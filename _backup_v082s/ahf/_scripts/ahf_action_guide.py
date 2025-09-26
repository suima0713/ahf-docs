#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AHF Action Guide v0.7.1c
実務ガイド（星の組合せで即アクション）
ハイコントラスト版星判定システムの実務適用
"""

import json
import os
import sys
from typing import Dict, List, Any, Tuple

def load_star_results(ticker: str) -> Dict[str, Any]:
    """
    各段階の星判定結果を読み込み
    """
    ticker_dir = os.path.join("tickers", ticker, "current")
    
    results = {}
    
    # ①RSS結果
    rss_file = os.path.join(ticker_dir, "rss_calculation.json")
    if os.path.exists(rss_file):
        with open(rss_file, 'r', encoding='utf-8') as f:
            results["rss"] = json.load(f)
    
    # ②αスコア結果
    alpha_file = os.path.join(ticker_dir, "alpha_scoring.json")
    if os.path.exists(alpha_file):
        with open(alpha_file, 'r', encoding='utf-8') as f:
            results["alpha"] = json.load(f)
    
    # ③TRI-3+V-Overlay結果
    tri3_file = os.path.join(ticker_dir, "tri3_v_overlay.json")
    if os.path.exists(tri3_file):
        with open(tri3_file, 'r', encoding='utf-8') as f:
            results["tri3"] = json.load(f)
    
    return results

def determine_action(star_1: int, star_2: int, star_3: int, v_category: str) -> Dict[str, Any]:
    """
    星の組合せで即アクションを決定
    
    ①★4–5 × ②★4–5 × ③★2：小さくIN→証拠で追撃（Amberゆえ段階買い）
    ①★1–2 or ②★1：見送り/縮小（TWがなくても）
    ③がRed：最大★=3で上限管理（プレミアム剥落リスク高）
    """
    action = {
        "recommendation": "",
        "size": "",
        "reason": "",
        "risk_level": "",
        "next_steps": []
    }
    
    # 基本判定
    high_quality = star_1 >= 4 and star_2 >= 4
    low_quality = star_1 <= 2 or star_2 <= 1
    red_risk = v_category == "Red"
    
    # アクション決定
    if high_quality and star_3 >= 2 and not red_risk:
        # 高品質 + 適正価格 + リスク低
        action["recommendation"] = "BUY"
        action["size"] = "Medium"
        action["reason"] = "高品質（①★4-5 × ②★4-5）かつ適正価格（③★2+）"
        action["risk_level"] = "Low"
        action["next_steps"] = [
            "証拠で追撃",
            "段階的買い増し",
            "KPI監視継続"
        ]
    
    elif high_quality and star_3 >= 2 and red_risk:
        # 高品質 + 適正価格 + リスク高
        action["recommendation"] = "BUY"
        action["size"] = "Small"
        action["reason"] = "高品質だが価格リスク高（③Red）"
        action["risk_level"] = "High"
        action["next_steps"] = [
            "小さくIN",
            "価格監視強化",
            "上限管理（★3以下）"
        ]
    
    elif high_quality and star_3 < 2:
        # 高品質 + 高価格
        action["recommendation"] = "HOLD"
        action["size"] = "None"
        action["reason"] = "高品質だが価格が高すぎる（③★1）"
        action["risk_level"] = "Medium"
        action["next_steps"] = [
            "価格調整待ち",
            "KPI監視継続"
        ]
    
    elif low_quality:
        # 低品質
        action["recommendation"] = "AVOID"
        action["size"] = "None"
        action["reason"] = "品質不足（①★1-2 or ②★1）"
        action["risk_level"] = "High"
        action["next_steps"] = [
            "見送り/縮小",
            "TW待ち不要",
            "他銘柄検討"
        ]
    
    else:
        # その他（中品質）
        action["recommendation"] = "HOLD"
        action["size"] = "Small"
        action["reason"] = "中品質、追加証拠待ち"
        action["risk_level"] = "Medium"
        action["next_steps"] = [
            "証拠収集",
            "KPI監視",
            "次決算待ち"
        ]
    
    return action

def generate_risk_assessment(star_1: int, star_2: int, star_3: int, v_category: str) -> Dict[str, Any]:
    """
    リスク評価の生成
    """
    risks = []
    mitigations = []
    
    # 品質リスク
    if star_1 <= 2:
        risks.append("成長品質不足（①★1-2）")
        mitigations.append("成長指標の改善待ち")
    
    if star_2 <= 1:
        risks.append("収益性不足（②★1）")
        mitigations.append("収益性指標の改善待ち")
    
    # 価格リスク
    if star_3 <= 1:
        risks.append("価格過高（③★1）")
        mitigations.append("価格調整待ち")
    
    if v_category == "Red":
        risks.append("プレミアム剥落リスク高（V-Overlay Red）")
        mitigations.append("上限管理（★3以下）")
    
    # 総合リスクレベル
    risk_count = len(risks)
    if risk_count >= 3:
        risk_level = "High"
    elif risk_count >= 2:
        risk_level = "Medium"
    else:
        risk_level = "Low"
    
    return {
        "risk_level": risk_level,
        "risks": risks,
        "mitigations": mitigations,
        "risk_count": risk_count
    }

def process_action_guide(ticker: str) -> Dict[str, Any]:
    """
    アクションガイドのメイン処理
    """
    # 星判定結果読み込み
    star_results = load_star_results(ticker)
    
    if not star_results:
        return {"error": "星判定結果が見つかりません"}
    
    # 各段階の星を取得
    star_1 = star_results.get("rss", {}).get("star_1", 1)
    star_2 = star_results.get("alpha", {}).get("star_2", 1)
    star_3 = star_results.get("tri3", {}).get("final_star", 1)
    v_category = star_results.get("tri3", {}).get("v_overlay", {}).get("category", "Unknown")
    
    # アクション決定
    action = determine_action(star_1, star_2, star_3, v_category)
    
    # リスク評価
    risk_assessment = generate_risk_assessment(star_1, star_2, star_3, v_category)
    
    return {
        "ticker": ticker,
        "as_of": star_results.get("rss", {}).get("as_of", "Unknown"),
        "stars": {
            "star_1": star_1,
            "star_2": star_2,
            "star_3": star_3
        },
        "v_category": v_category,
        "action": action,
        "risk_assessment": risk_assessment,
        "summary": f"{ticker}: {action['recommendation']} {action['size']} ({action['reason']})"
    }

def main():
    if len(sys.argv) != 2:
        print("使用方法: python ahf_action_guide.py <TICKER>")
        sys.exit(1)
    
    ticker = sys.argv[1].upper()
    
    try:
        results = process_action_guide(ticker)
        
        if "error" in results:
            print(f"[ERROR] {results['error']}")
            sys.exit(1)
        
        # 結果出力
        print("=== AHF Action Guide Results (v0.7.1c) ===")
        print(f"Ticker: {results['ticker']}")
        print(f"As of: {results['as_of']}")
        print()
        print("星判定:")
        print(f"  ①RSS: ★{results['stars']['star_1']}")
        print(f"  ②α3/α5: ★{results['stars']['star_2']}")
        print(f"  ③TRI-3+V: ★{results['stars']['star_3']}")
        print(f"  V区分: {results['v_category']}")
        print()
        print("アクション:")
        print(f"  推奨: {results['action']['recommendation']}")
        print(f"  サイズ: {results['action']['size']}")
        print(f"  理由: {results['action']['reason']}")
        print(f"  リスク: {results['action']['risk_level']}")
        print()
        print("次のステップ:")
        for step in results['action']['next_steps']:
            print(f"  - {step}")
        print()
        print("リスク評価:")
        print(f"  レベル: {results['risk_assessment']['risk_level']}")
        print(f"  リスク数: {results['risk_assessment']['risk_count']}")
        if results['risk_assessment']['risks']:
            print("  リスク:")
            for risk in results['risk_assessment']['risks']:
                print(f"    - {risk}")
        if results['risk_assessment']['mitigations']:
            print("  対策:")
            for mitigation in results['risk_assessment']['mitigations']:
                print(f"    - {mitigation}")
        print()
        print(f"サマリー: {results['summary']}")
        
        # 結果をJSONファイルに保存
        output_file = f"tickers/{ticker}/current/action_guide.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"[INFO] 結果を保存しました: {output_file}")
        
    except Exception as e:
        print(f"[ERROR] 処理エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
