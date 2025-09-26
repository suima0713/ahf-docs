#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AHF v0.7.2β LEC統合版（5パッチ適用）
①LEC反証モード分析 + ②勾配Now‑castパッチ + ③認知ギャップNow‑castパッチ + ④セクター対応V-Overlay + ⑤右肩Fwdブースト
"""

import json
import os
import sys
import yaml
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path

# 5パッチのインポート
sys.path.append(os.path.dirname(__file__))
from ahf_lec_analysis_v072 import process_lec_analysis
from ahf_alpha_nowcast_v072 import process_alpha_nowcast
from ahf_v_overlay_sector_aware_v072 import process_sector_aware_v_overlay
from ahf_rss_fwd_boost_v072 import process_rss_fwd_boost

def process_v072_lec_integrated(triage_file: str, facts_file: str, 
                              alpha_scoring_file: str, market_data_file: Optional[str] = None) -> Dict[str, Any]:
    """
    v0.7.2β LEC統合処理（5パッチ適用）
    """
    
    # ①LEC反証モード分析実行
    lec_result = process_lec_analysis(triage_file, facts_file)
    
    # ②勾配Now‑castパッチ実行
    alpha_result = process_alpha_nowcast(triage_file, facts_file)
    
    # ④セクター対応V-Overlay実行（③認知ギャップを含む）
    sector_v_result = process_sector_aware_v_overlay(triage_file, market_data_file)
    
    # ⑤右肩Fwdブーストパッチ実行
    rss_result = process_rss_fwd_boost(triage_file, facts_file)
    
    # T/R加点システム適用
    tr_adders = calculate_tr_adders(triage_file)
    
    # ③認知ギャップ最終計算
    tri3_final = calculate_tri3_final(sector_v_result, tr_adders)
    
    # Decision判定
    decision = calculate_decision(alpha_result, tri3_final)
    
    # 統合結果
    return {
        "as_of": lec_result["as_of"],
        "ticker": lec_result["ticker"],
        "version": "v0.7.2β-lec-integrated",
        
        # ①長期EV成長の確かさ（LEC反証モード分析）
        "lec_analysis": lec_result["lec_analysis"],
        "star_1_lec": lec_result["lec_analysis"]["star_1"],
        "confidence_1_lec": lec_result["confidence"],
        
        # ⑤右肩（Fwdブーストパッチ適用）
        "rss_fwd_boost": rss_result["rss_fwd_boost"],
        "star_1_rss": rss_result["rss_fwd_boost"]["star_1_final"],
        "confidence_1_rss": rss_result["confidence"],
        
        # ①統合（LEC vs RSS）
        "star_1_final": max(lec_result["lec_analysis"]["star_1"], 
                           rss_result["rss_fwd_boost"]["star_1_final"]),
        
        # ②勾配（Now‑castパッチ適用）
        "alpha_nowcast": alpha_result["alpha_nowcast"],
        "star_2": alpha_result["alpha_nowcast"]["star_2"],
        "confidence_2": alpha_result["confidence"],
        
        # ③認知ギャップ（セクター対応V-Overlay + T/R加点）
        "tri3": tri3_final,
        "star_3": tri3_final["star"],
        "confidence_3": tri3_final["confidence"],
        "sector_aware_v": sector_v_result["sector_aware_v"],
        
        # 統合評価
        "decision": decision,
        "decision_logic": {
            "star_1_lec": lec_result["lec_analysis"]["star_1"],
            "star_1_rss": rss_result["rss_fwd_boost"]["star_1_final"],
            "star_1_final": max(lec_result["lec_analysis"]["star_1"], 
                               rss_result["rss_fwd_boost"]["star_1_final"]),
            "star_2": alpha_result["alpha_nowcast"]["star_2"],
            "star_3": tri3_final["star"],
            "go_condition": "②★3以上×③★2以上=GO"
        },
        
        # 詳細情報
        "lec_explanation": lec_result["explanation"],
        "rss_explanation": rss_result["explanation"],
        "alpha_explanation": alpha_result["explanation"],
        "sector_v_explanation": sector_v_result["explanation"],
        
        # メタデータ
        "patches_applied": [
            "①LEC反証モード分析",
            "②勾配Now‑castパッチ",
            "③認知ギャップNow‑castパッチ",
            "④セクター対応V-Overlay",
            "⑤右肩Fwdブースト"
        ],
        "notes": {
            "lec.analysis_rule": "3ゲート反証モード分析",
            "rss.fwd_boost_rule": "実績ベース+先行シグナル薄味注入",
            "alpha.nowcast_rule": "α3_ncast+α5_ncast+Gap_safe",
            "tri3.star_rule": "セクター対応V基準+TR加点",
            "sector_aware.v_overlay_rule": "セクター別V-Overlay統合"
        }
    }

def calculate_tr_adders(triage_file: str) -> int:
    """T/R加点システム計算"""
    with open(triage_file, 'r', encoding='utf-8') as f:
        triage_data = json.load(f)
    
    confirmed_items = triage_data.get("CONFIRMED", [])
    
    t_score = 0
    r_score = 0
    
    for item in confirmed_items:
        if item["kpi"] == "T_score":
            t_score = item["value"]
        elif item["kpi"] == "R_score":
            r_score = item["value"]
    
    total_score = t_score + r_score
    
    if total_score >= 4:
        return 2  # T+R=4 → +2★
    elif total_score >= 3:
        return 1  # T+R≥3 → +1★
    else:
        return 0  # 加点なし

def calculate_tri3_final(sector_v_result: Dict[str, Any], tr_adders: int) -> Dict[str, Any]:
    """③認知ギャップ最終計算"""
    v_star = sector_v_result["sector_aware_v"]["star_3"]
    final_star = min(5, v_star + tr_adders)
    
    return {
        "T": 0,  # 簡略化
        "R": 0,  # 簡略化
        "V": sector_v_result["sector_aware_v"]["category"],
        "star": final_star,
        "bonus_applied": False,
        "v_base": v_star,
        "tr_adders": tr_adders,
        "confidence": sector_v_result["confidence"]
    }

def calculate_decision(alpha_result: Dict[str, Any], 
                      tri3_final: Dict[str, Any]) -> str:
    """
    Decision判定（②★3以上×③★2以上=GO）
    """
    star_2 = alpha_result["alpha_nowcast"]["star_2"]
    star_3 = tri3_final["star"]
    
    if star_2 >= 3 and star_3 >= 2:
        return "GO"
    elif star_2 >= 2 and star_3 >= 1:
        return "WATCH"
    else:
        return "NO-GO"

def generate_summary_report(result: Dict[str, Any]) -> str:
    """統合レポート生成"""
    lines = []
    
    lines.append(f"=== AHF v0.7.2β LEC統合評価結果 ===")
    lines.append(f"銘柄: {result['ticker']}")
    lines.append(f"As of: {result['as_of']}")
    lines.append("")
    
    # ①統合評価
    lines.append("【①長期EV成長の確かさ（LEC統合）】")
    lines.append(f"  ★: {result['star_1_final']}")
    lines.append(f"  LEC分析: ★{result['star_1_lec']} ({result['lec_analysis']['final_score']:.1f})")
    lines.append(f"  RSS分析: ★{result['star_1_rss']} ({result['rss_fwd_boost']['rss_base']})")
    lines.append("")
    lines.append("  【LEC反証ゲート】")
    lines.append(f"    生存性: {result['lec_analysis']['survival_score']:.1f}")
    lines.append(f"    優位性: {result['lec_analysis']['moat_score']:.1f}")
    lines.append(f"    ニーズ: {result['lec_analysis']['demand_score']:.1f}")
    lines.append("")
    
    # ②勾配
    lines.append("【②勾配（Now‑castパッチ適用）】")
    lines.append(f"  ★: {result['star_2']}")
    lines.append(f"  α3_ncast: {result['alpha_nowcast']['alpha3_ncast']}")
    lines.append(f"  α5_ncast: {result['alpha_nowcast']['alpha5_ncast']}")
    lines.append(f"  Gap‑safe: {result['alpha_nowcast']['gap_safe_applied']}")
    lines.append(f"  確信度: {result['confidence_2']:.0f}%")
    lines.append("")
    
    # ③認知ギャップ
    lines.append("【③認知ギャップ（セクター対応V-Overlay適用）】")
    lines.append(f"  ★: {result['star_3']}")
    lines.append(f"  セクター: {result['sector_aware_v']['sector']}")
    lines.append(f"  V: {result['tri3']['V']}")
    lines.append(f"  V基準★: {result['tri3']['v_base']}")
    lines.append(f"  T/R加点: +{result['tri3']['tr_adders']}")
    lines.append(f"  使用エンジン: {result['sector_aware_v']['engine_used']}")
    lines.append(f"  確信度: {result['confidence_3']:.0f}%")
    lines.append("")
    
    # Decision
    lines.append("【Decision】")
    lines.append(f"  {result['decision']}")
    lines.append(f"  ロジック: {result['decision_logic']['go_condition']}")
    lines.append(f"  ①★{result['decision_logic']['star_1_final']} × ②★{result['decision_logic']['star_2']} × ③★{result['decision_logic']['star_3']}")
    lines.append("")
    
    # パッチ適用状況
    lines.append("【適用パッチ】")
    for patch in result['patches_applied']:
        lines.append(f"  ✅ {patch}")
    
    return "\n".join(lines)

def generate_one_line_summary(result: Dict[str, Any]) -> str:
    """1行要約生成"""
    decision = result['decision']
    star_1 = result['star_1_final']
    star_2 = result['star_2']
    star_3 = result['star_3']
    sector = result['sector_aware_v']['sector']
    
    # 各軸の特徴を簡潔に表現
    lec_desc = f"LEC★{star_1}"
    alpha_desc = f"勾配★{star_2}"
    tri3_desc = f"認知★{star_3}"
    
    # Decisionに基づく要約
    if decision == "GO":
        summary = f"Decision: {decision}. {lec_desc}×{alpha_desc}×{tri3_desc}。"
        if result['star_1_lec'] > result['star_1_rss']:
            summary += " ①はLEC反証で強化。"
        elif result['star_1_rss'] > result['star_1_lec']:
            summary += " ①はFwdブーストで強化。"
        if sector != "standard":
            summary += f" ③は{sector}セクター対応。"
    elif decision == "WATCH":
        summary = f"Decision: {decision}. {lec_desc}×{alpha_desc}×{tri3_desc}。"
        summary += " 実績は堅調だが一部軸で改善余地あり。"
        if sector != "standard":
            summary += f" ③は{sector}セクター対応。"
    else:
        summary = f"Decision: {decision}. {lec_desc}×{alpha_desc}×{tri3_desc}。"
        summary += " 全体的に改善が必要。"
    
    return summary

def main():
    if len(sys.argv) < 4:
        print("使用方法: python ahf_v072_lec_integrated.py <triage.jsonのパス> <facts.mdのパス> <alpha_scoring.jsonのパス> [market_data.jsonのパス]")
        sys.exit(1)
    
    triage_file = sys.argv[1]
    facts_file = sys.argv[2]
    alpha_scoring_file = sys.argv[3]
    market_data_file = sys.argv[4] if len(sys.argv) > 4 else None
    
    # ファイル存在チェック
    for file_path, name in [(triage_file, "triage.json"), 
                           (facts_file, "facts.md"), 
                           (alpha_scoring_file, "alpha_scoring.json")]:
        if not os.path.exists(file_path):
            print(f"[ERROR] {name}が見つかりません: {file_path}")
            sys.exit(1)
    
    try:
        # LEC統合処理実行
        results = process_v072_lec_integrated(triage_file, facts_file, alpha_scoring_file, market_data_file)
        
        # レポート出力
        report = generate_summary_report(results)
        print(report)
        
        # 結果をJSONファイルに保存
        output_file = triage_file.replace("triage.json", "v072_lec_integrated.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"[INFO] LEC統合結果を保存しました: {output_file}")
        
        # 1行要約生成
        summary = generate_one_line_summary(results)
        print(f"\n【1行要約】")
        print(summary)
        
    except Exception as e:
        print(f"[ERROR] 処理エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()






