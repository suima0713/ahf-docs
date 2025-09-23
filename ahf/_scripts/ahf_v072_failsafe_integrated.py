#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AHF v0.7.2β Fail-safe統合版
①LEC反証優先 + ②勾配短期傾き + ③V-Overlay（VRG）+ Fail-safe運用
"""

import json
import os
import sys
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path

# Fail-safeエンジンのインポート
sys.path.append(os.path.dirname(__file__))
from ahf_lec_analysis_failsafe_v072 import process_lec_failsafe_analysis
from ahf_alpha_scoring_failsafe_v072 import process_alpha_failsafe_analysis
from ahf_v_overlay_failsafe_v072 import process_v_overlay_failsafe_analysis
from ahf_failsafe_engine_v072 import apply_failsafe_logic

def process_v072_failsafe_integrated(triage_file: str, facts_file: str) -> Dict[str, Any]:
    """
    v0.7.2β Fail-safe統合処理
    """
    
    # ①LEC反証優先分析実行
    lec_result = process_lec_failsafe_analysis(triage_file, facts_file)
    
    # ②勾配短期傾き分析実行
    alpha_result = process_alpha_failsafe_analysis(triage_file, facts_file)
    
    # ③V-Overlay（VRG）分析実行
    v_overlay_result = process_v_overlay_failsafe_analysis(triage_file, facts_file)
    
    # Fail-safe論理適用
    failsafe_result = apply_failsafe_logic(
        triage_file, facts_file,
        lec_result["lec_failsafe"]["final_star"],
        alpha_result["alpha_failsafe"]["final_star"],
        v_overlay_result["v_overlay_failsafe"]["star"]
    )
    
    # 統合結果
    return {
        "as_of": lec_result["as_of"],
        "ticker": lec_result["ticker"],
        "version": "v0.7.2β-failsafe-integrated",
        
        # ①長期EV成長の確かさ（LEC反証優先）
        "lec_failsafe": lec_result["lec_failsafe"],
        "star_1": lec_result["lec_failsafe"]["final_star"],
        "lec_explanation": lec_result["explanation"],
        
        # ②勾配（短期傾きのみ）
        "alpha_failsafe": alpha_result["alpha_failsafe"],
        "star_2": alpha_result["alpha_failsafe"]["final_star"],
        "alpha_explanation": alpha_result["explanation"],
        
        # ③評価＋認知（V-Overlay VRG）
        "v_overlay_failsafe": v_overlay_result["v_overlay_failsafe"],
        "star_3": v_overlay_result["v_overlay_failsafe"]["star"],
        "v_overlay_explanation": v_overlay_result["explanation"],
        
        # Fail-safe判定
        "failsafe": failsafe_result,
        "decision": failsafe_result["decision"],
        "missing_keys": failsafe_result["missing_keys"],
        "failsafe_triggered": failsafe_result["failsafe_triggered"],
        
        # 統合評価
        "decision_logic": {
            "star_1": lec_result["lec_failsafe"]["final_star"],
            "star_2": alpha_result["alpha_failsafe"]["final_star"],
            "star_3": v_overlay_result["v_overlay_failsafe"]["star"],
            "failsafe_rule": "欠落時はWATCH固定・GOは出さない"
        },
        
        # メタデータ
        "analysis_rules": {
            "lec": "反証優先・減点のみ・上振れ不可",
            "alpha": "短期傾きのみ・プロキシ不足は★2",
            "v_overlay": "EV/S×Ro40のみ・未投入は未判定"
        },
        "notes": {
            "failsafe.applied": failsafe_result["failsafe_triggered"],
            "decision.final": failsafe_result["decision"],
            "missing.data": failsafe_result["missing_keys"]
        }
    }

def generate_summary_report(result: Dict[str, Any]) -> str:
    """統合レポート生成"""
    lines = []
    
    lines.append(f"=== AHF v0.7.2β Fail-safe統合評価結果 ===")
    lines.append(f"銘柄: {result['ticker']}")
    lines.append(f"As of: {result['as_of']}")
    lines.append("")
    
    # ①LEC反証優先評価
    lines.append("【①長期EV成長の確かさ（LEC反証優先）】")
    lines.append(f"  ★: {result['star_1']}")
    lines.append(f"  生存性: {result['lec_failsafe']['survival_gate']}")
    lines.append(f"  優位性: {result['lec_failsafe']['moat_gate']}")
    lines.append(f"  ニーズ: {result['lec_failsafe']['demand_gate']}")
    lines.append(f"  説明: {result['lec_explanation']}")
    lines.append("")
    
    # ②勾配短期傾き評価
    lines.append("【②勾配（短期傾きのみ）】")
    lines.append(f"  ★: {result['star_2']}")
    lines.append(f"  ガイダンスq/q: {result['alpha_failsafe']['guidance_qoq']:.1f}%" if result['alpha_failsafe']['guidance_qoq'] else "  ガイダンスq/q: N/A")
    lines.append(f"  B/B: {result['alpha_failsafe']['book_to_bill']:.1f}x" if result['alpha_failsafe']['book_to_bill'] else "  B/B: N/A")
    lines.append(f"  プロキシ充足度: {result['alpha_failsafe']['proxy_sufficiency']}")
    lines.append(f"  説明: {result['alpha_explanation']}")
    lines.append("")
    
    # ③V-Overlay評価
    lines.append("【③評価＋認知（V-Overlay VRG）】")
    lines.append(f"  ★: {result['star_3']}")
    lines.append(f"  EV/S: {result['v_overlay_failsafe']['ev_sales']:.1f}x" if result['v_overlay_failsafe']['ev_sales'] else "  EV/S: N/A")
    lines.append(f"  Ro40: {result['v_overlay_failsafe']['rule_of_40']:.1f}" if result['v_overlay_failsafe']['rule_of_40'] else "  Ro40: N/A")
    lines.append(f"  カテゴリ: {result['v_overlay_failsafe']['category']}")
    lines.append(f"  データ充足度: {result['v_overlay_failsafe']['data_sufficiency']}")
    lines.append(f"  説明: {result['v_overlay_explanation']}")
    lines.append("")
    
    # Fail-safe判定
    lines.append("【Fail-safe判定】")
    lines.append(f"  Decision: {result['decision']}")
    lines.append(f"  Fail-safe適用: {result['failsafe_triggered']}")
    if result['missing_keys']:
        lines.append(f"  欠落キー: {', '.join(result['missing_keys'])}")
    lines.append(f"  ①★{result['decision_logic']['star_1']} × ②★{result['decision_logic']['star_2']} × ③★{result['decision_logic']['star_3']}")
    lines.append("")
    
    # 分析ルール
    lines.append("【分析ルール】")
    lines.append(f"  LEC: {result['analysis_rules']['lec']}")
    lines.append(f"  Alpha: {result['analysis_rules']['alpha']}")
    lines.append(f"  V-Overlay: {result['analysis_rules']['v_overlay']}")
    
    return "\n".join(lines)

def generate_one_line_summary(result: Dict[str, Any]) -> str:
    """1行要約生成"""
    decision = result['decision']
    star_1 = result['star_1']
    star_2 = result['star_2']
    star_3 = result['star_3']
    
    # Decisionに基づく要約
    if decision == "WATCH" and result['failsafe_triggered']:
        summary = f"Decision: {decision} (Fail-safe適用). {star_1}×{star_2}×{star_3}。"
        summary += f" 欠落キー: {', '.join(result['missing_keys'])}"
    elif decision == "GO":
        summary = f"Decision: {decision}. {star_1}×{star_2}×{star_3}。"
        summary += " 全軸データ充足・Fail-safe通過。"
    elif decision == "WATCH":
        summary = f"Decision: {decision}. {star_1}×{star_2}×{star_3}。"
        summary += " 一部軸で改善余地あり。"
    else:
        summary = f"Decision: {decision}. {star_1}×{star_2}×{star_3}。"
        summary += " 全体的に改善が必要。"
    
    return summary

def main():
    if len(sys.argv) != 3:
        print("使用方法: python ahf_v072_failsafe_integrated.py <triage.jsonのパス> <facts.mdのパス>")
        sys.exit(1)
    
    triage_file = sys.argv[1]
    facts_file = sys.argv[2]
    
    # ファイル存在チェック
    for file_path, name in [(triage_file, "triage.json"), (facts_file, "facts.md")]:
        if not os.path.exists(file_path):
            print(f"[ERROR] {name}が見つかりません: {file_path}")
            sys.exit(1)
    
    try:
        # Fail-safe統合処理実行
        results = process_v072_failsafe_integrated(triage_file, facts_file)
        
        # レポート出力
        report = generate_summary_report(results)
        print(report)
        
        # 結果をJSONファイルに保存
        output_file = triage_file.replace("triage.json", "v072_failsafe_integrated.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"[INFO] Fail-safe統合結果を保存しました: {output_file}")
        
        # 1行要約生成
        summary = generate_one_line_summary(results)
        print(f"\n【1行要約】")
        print(summary)
        
    except Exception as e:
        print(f"[ERROR] 処理エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()



