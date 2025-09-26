#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AHF v0.7.2β 完全統合版（3パッチ適用）
①右肩「Fwdブースト」パッチ + ②勾配Now‑castパッチ + ③認知ギャップNow‑castパッチ
"""

import json
import os
import sys
import yaml
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path

# 3パッチのインポート
sys.path.append(os.path.dirname(__file__))
from ahf_rss_fwd_boost_v072 import process_rss_fwd_boost
from ahf_alpha_nowcast_v072 import process_alpha_nowcast
from ahf_tri3_v_overlay_v072 import process_tri3_v_overlay_v072

def process_v072_complete_integrated(triage_file: str, facts_file: str, 
                                   alpha_scoring_file: str) -> Dict[str, Any]:
    """
    v0.7.2β完全統合処理（3パッチ適用）
    """
    
    # ①右肩「Fwdブースト」パッチ実行
    rss_result = process_rss_fwd_boost(triage_file, facts_file)
    
    # ②勾配Now‑castパッチ実行
    alpha_result = process_alpha_nowcast(triage_file, facts_file)
    
    # ③認知ギャップNow‑castパッチ実行
    tri3_result = process_tri3_v_overlay_v072(triage_file, alpha_scoring_file)
    
    # Decision判定
    decision = calculate_decision(alpha_result, tri3_result)
    
    # 統合結果
    return {
        "as_of": rss_result["as_of"],
        "ticker": tri3_result.get("ticker", ""),
        "version": "v0.7.2β-complete-integrated",
        
        # ①右肩（Fwdブーストパッチ適用）
        "rss_fwd_boost": rss_result["rss_fwd_boost"],
        "star_1": rss_result["rss_fwd_boost"]["star_1_final"],
        "confidence_1": rss_result["confidence"],
        
        # ②勾配（Now‑castパッチ適用）
        "alpha_nowcast": alpha_result["alpha_nowcast"],
        "star_2": alpha_result["alpha_nowcast"]["star_2"],
        "confidence_2": alpha_result["confidence"],
        
        # ③認知ギャップ（Now‑castパッチ適用）
        "tri3": tri3_result["tri3"],
        "star_3": tri3_result["tri3"]["star"],
        "confidence_3": tri3_result["confidence"],
        
        # 統合評価
        "decision": decision,
        "decision_logic": {
            "star_1": rss_result["rss_fwd_boost"]["star_1_final"],
            "star_2": alpha_result["alpha_nowcast"]["star_2"],
            "star_3": tri3_result["tri3"]["star"],
            "go_condition": "②★3以上×③★2以上=GO"
        },
        
        # 詳細情報
        "valuation_overlay": tri3_result["valuation_overlay"],
        "rss_explanation": rss_result["explanation"],
        "alpha_explanation": alpha_result["explanation"],
        
        # メタデータ
        "patches_applied": [
            "①右肩「Fwdブースト」パッチ",
            "②勾配Now‑castパッチ",
            "③認知ギャップNow‑castパッチ"
        ],
        "notes": {
            "rss.fwd_boost_rule": "実績ベース+先行シグナル薄味注入",
            "alpha.nowcast_rule": "α3_ncast+α5_ncast+Gap_safe",
            "tri3.star_rule": "V_base_plus_TR_adders"
        }
    }

def calculate_decision(alpha_result: Dict[str, Any], 
                      tri3_result: Dict[str, Any]) -> str:
    """
    Decision判定（②★3以上×③★2以上=GO）
    """
    star_2 = alpha_result["alpha_nowcast"]["star_2"]
    star_3 = tri3_result["tri3"]["star"]
    
    if star_2 >= 3 and star_3 >= 2:
        return "GO"
    elif star_2 >= 2 and star_3 >= 1:
        return "WATCH"
    else:
        return "NO-GO"

def generate_summary_report(result: Dict[str, Any]) -> str:
    """統合レポート生成"""
    lines = []
    
    lines.append(f"=== AHF v0.7.2β 完全統合評価結果 ===")
    lines.append(f"銘柄: {result['ticker']}")
    lines.append(f"As of: {result['as_of']}")
    lines.append("")
    
    # 各軸の評価
    lines.append("【①右肩（Fwdブーストパッチ適用）】")
    lines.append(f"  ★: {result['star_1']}")
    lines.append(f"  RSS: {result['rss_fwd_boost']['rss_base']}")
    if result['rss_fwd_boost']['boost_applied']:
        lines.append(f"  Fwdブースト: +{result['rss_fwd_boost']['fwd_boost']}")
        lines.append(f"  ブースト根拠: {', '.join(result['rss_fwd_boost']['boost_reasons'])}")
    lines.append(f"  確信度: {result['confidence_1']:.0f}%")
    lines.append("")
    
    lines.append("【②勾配（Now‑castパッチ適用）】")
    lines.append(f"  ★: {result['star_2']}")
    lines.append(f"  α3_ncast: {result['alpha_nowcast']['alpha3_ncast']}")
    lines.append(f"  α5_ncast: {result['alpha_nowcast']['alpha5_ncast']}")
    lines.append(f"  Gap‑safe: {result['alpha_nowcast']['gap_safe_applied']}")
    lines.append(f"  確信度: {result['confidence_2']:.0f}%")
    lines.append("")
    
    lines.append("【③認知ギャップ（Now‑castパッチ適用）】")
    lines.append(f"  ★: {result['star_3']}")
    lines.append(f"  V: {result['tri3']['V']}")
    lines.append(f"  T/R: {result['tri3']['T']}/{result['tri3']['R']}")
    lines.append(f"  確信度: {result['confidence_3']:.0f}%")
    lines.append("")
    
    # Decision
    lines.append("【Decision】")
    lines.append(f"  {result['decision']}")
    lines.append(f"  ロジック: {result['decision_logic']['go_condition']}")
    lines.append(f"  ①★{result['decision_logic']['star_1']} × ②★{result['decision_logic']['star_2']} × ③★{result['decision_logic']['star_3']}")
    lines.append("")
    
    # パッチ適用状況
    lines.append("【適用パッチ】")
    for patch in result['patches_applied']:
        lines.append(f"  ✅ {patch}")
    
    return "\n".join(lines)

def generate_one_line_summary(result: Dict[str, Any]) -> str:
    """1行要約生成"""
    decision = result['decision']
    star_1 = result['star_1']
    star_2 = result['star_2']
    star_3 = result['star_3']
    
    # 各軸の特徴を簡潔に表現
    rss_desc = f"右肩★{star_1}"
    alpha_desc = f"勾配★{star_2}"
    tri3_desc = f"認知★{star_3}"
    
    # Decisionに基づく要約
    if decision == "GO":
        summary = f"Decision: {decision}. {rss_desc}×{alpha_desc}×{tri3_desc}。"
        if result['rss_fwd_boost']['boost_applied']:
            summary += " ①は先行シグナルで強化。"
    elif decision == "WATCH":
        summary = f"Decision: {decision}. {rss_desc}×{alpha_desc}×{tri3_desc}。"
        summary += " 実績は堅調だが一部軸で改善余地あり。"
    else:
        summary = f"Decision: {decision}. {rss_desc}×{alpha_desc}×{tri3_desc}。"
        summary += " 全体的に改善が必要。"
    
    return summary

def main():
    if len(sys.argv) != 4:
        print("使用方法: python ahf_v072_complete_integrated.py <triage.jsonのパス> <facts.mdのパス> <alpha_scoring.jsonのパス>")
        sys.exit(1)
    
    triage_file = sys.argv[1]
    facts_file = sys.argv[2]
    alpha_scoring_file = sys.argv[3]
    
    # ファイル存在チェック
    for file_path, name in [(triage_file, "triage.json"), 
                           (facts_file, "facts.md"), 
                           (alpha_scoring_file, "alpha_scoring.json")]:
        if not os.path.exists(file_path):
            print(f"[ERROR] {name}が見つかりません: {file_path}")
            sys.exit(1)
    
    try:
        # 完全統合処理実行
        results = process_v072_complete_integrated(triage_file, facts_file, alpha_scoring_file)
        
        # レポート出力
        report = generate_summary_report(results)
        print(report)
        
        # 結果をJSONファイルに保存
        output_file = triage_file.replace("triage.json", "v072_complete_integrated.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"[INFO] 完全統合結果を保存しました: {output_file}")
        
        # 1行要約生成
        summary = generate_one_line_summary(results)
        print(f"\n【1行要約】")
        print(summary)
        
    except Exception as e:
        print(f"[ERROR] 処理エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

