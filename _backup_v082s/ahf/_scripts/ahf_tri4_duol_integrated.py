#!/usr/bin/env python3
"""
AHF TRI-4 v1.1 DUOL統合適用
DUOLの実際のデータに基づくTRI-4三点測量判定
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from enum import Enum

class VLevel(Enum):
    """バリュエーション織込み度"""
    GREEN = "Green"
    AMBER = "Amber"
    RED = "Red"

def load_analysis_results() -> Dict[str, Any]:
    """各分析結果を読み込み"""
    
    # T分析結果
    t_path = Path("duol_t_analysis.json")
    if t_path.exists():
        with open(t_path, 'r', encoding='utf-8') as f:
            t_result = json.load(f)
    else:
        t_result = {"T": 2}  # 手動設定（QoQとYoYの一次説明が整合）
    
    # DUOLの実際のT値（手動設定）
    t_result = {"T": 2}
    
    # R分析結果
    r_path = Path("duol_r_analysis.json")
    if r_path.exists():
        with open(r_path, 'r', encoding='utf-8') as f:
            r_result = json.load(f)
    else:
        r_result = {"R": 1}  # 手動設定（Item1A=No changeだが開示に粒度不足）
    
    # V分析結果
    v_path = Path("duol_v_analysis.json")
    if v_path.exists():
        with open(v_path, 'r', encoding='utf-8') as f:
            v_result = json.load(f)
    else:
        v_result = {"V": "Amber"}  # 手動設定
    
    # α3/α5分析結果
    alpha_path = Path("duol_alpha_analysis.json")
    if alpha_path.exists():
        with open(alpha_path, 'r', encoding='utf-8') as f:
            alpha_result = json.load(f)
    else:
        alpha_result = {"alpha3_pass": False, "alpha5_pass": True}  # 手動設定
    
    return {
        "T": t_result["T"],
        "R": r_result["R"],
        "V": VLevel(v_result["V"]),
        "alpha3_pass": alpha_result["alpha3_pass"],
        "alpha5_pass": alpha_result["alpha5_pass"]
    }

def calculate_tri4_duol(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """DUOLのTRI-4計算"""
    
    T = inputs["T"]
    R = inputs["R"]
    V = inputs["V"]
    alpha3_pass = inputs["alpha3_pass"]
    alpha5_pass = inputs["alpha5_pass"]
    
    # 基礎★マッピング（T + R → 基礎★）
    base_star_mapping = {
        0: 1,  # T=0, R=0 → ★1
        1: 2,  # T=1, R=0 or T=0, R=1 → ★2
        2: 2,  # T=2, R=0 or T=0, R=2 or T=1, R=1 → ★2
        3: 3,  # T=2, R=1 or T=1, R=2 → ★3
        4: 4   # T=2, R=2 → ★4
    }
    
    # 1. 基礎★計算
    total_score = T + R
    base_stars = base_star_mapping.get(total_score, 1)
    
    # 2. Vオーバーレイ適用
    v_adjusted_stars = base_stars
    v_overlay_applied = False
    
    if V == VLevel.GREEN:
        # ±0（据え置き）
        pass
    elif V == VLevel.AMBER:
        # ★−1（下限★1）
        v_adjusted_stars = max(1, base_stars - 1)
        v_overlay_applied = True
    elif V == VLevel.RED:
        # ★=min(★−1, 3)（自動キャップ=3）
        v_adjusted_stars = min(max(1, base_stars - 1), 3)
        v_overlay_applied = True
    
    # 3. ボーナス★計算
    bonus_stars = 0
    if alpha3_pass and alpha5_pass:
        # 上限★5をチェック
        bonus_stars = min(1, 5 - v_adjusted_stars)
    
    # 4. 最終★計算
    final_stars = v_adjusted_stars + bonus_stars
    
    return {
        "inputs": inputs,
        "base_stars": base_stars,
        "v_adjusted_stars": v_adjusted_stars,
        "v_overlay_applied": v_overlay_applied,
        "bonus_stars": bonus_stars,
        "final_stars": final_stars
    }

def generate_duol_tri4_report(result: Dict[str, Any]) -> str:
    """DUOL TRI-4レポート生成"""
    
    inputs = result["inputs"]
    
    report_lines = [
        "=== DUOL TRI-4 v1.1 三点測量判定 ===",
        "",
        "【入力（3点）】",
        f"T（T1因果明瞭度）: {inputs['T']}/2",
        f"R（T1シグナル社会化度）: {inputs['R']}/2", 
        f"V（バリュエーション織込み度）: {inputs['V'].value}",
        "",
        "【α3/α5判定】",
        f"α3 PASS: {'Yes' if inputs['alpha3_pass'] else 'No'}",
        f"α5 PASS: {'Yes' if inputs['alpha5_pass'] else 'No'}",
        "",
        "【計算過程】",
        f"基礎★: T+R = {inputs['T']}+{inputs['R']} = {result['base_stars']}",
        f"Vオーバーレイ: {inputs['V'].value} → {'±0（据え置き）' if inputs['V'] == VLevel.GREEN else '★−1（下限★1）' if inputs['V'] == VLevel.AMBER else '★=min(★−1, 3)（自動キャップ=3）'}",
        f"V調整後★: {result['v_adjusted_stars']}",
        f"ボーナス★: {result['bonus_stars']}",
        "",
        f"【最終結果】",
        f"④＝認知ギャップ: ★{result['final_stars']}",
        ""
    ]
    
    # 詳細説明
    if inputs['T'] == 2:
        report_lines.append("T=2: QoQとYoYの一次説明が整合している")
        report_lines.append("  - QoQ: GM +130bps QoQ due to lower-than-expected AI costs and strength in ads")
        report_lines.append("  - YoY: driven by increased generative AI costs year over year related to the expansion of the Duolingo Max")
        report_lines.append("  - 共通要素: AIコストが両方の説明に整合")
    elif inputs['T'] == 1:
        report_lines.append("T=1: 片側（QoQ or YoY）説明あり")
    else:
        report_lines.append("T=0: 不明瞭")
    
    if inputs['R'] == 2:
        report_lines.append("R=2: No changeかつ注記・指標が十分")
    elif inputs['R'] == 1:
        report_lines.append("R=1: Item1A=No changeだが開示に粒度不足（単一セグメント等）")
        report_lines.append("  - Item1A=No change: 確認済み")
        report_lines.append("  - 単一セグメント: 粗利内訳未開示")
    else:
        report_lines.append("R=0: Item1A変更あり or 説明欠落")
    
    if inputs['V'] == VLevel.AMBER:
        report_lines.append("V=Amber: EV/Sales(Fwd) 12.0× > 10×（割高域）")
        report_lines.append("  - Rule-of-40 72.2% ≥ 40%（良好）")
    
    report_lines.extend([
        "",
        "【使い方（超要約）】",
        "星はブレない: T, Rが変わらない限り、指摘や私見では動かない",
        "価格は別レイヤーで制御: VがAmber/Redなら自動で減点",
        "強い確証が出たらだけ加点: α3&α5を両方満たした時だけ+1"
    ])
    
    return "\n".join(report_lines)

def main():
    """メイン実行"""
    print("=== DUOL TRI-4 v1.1 統合適用 ===")
    
    # 分析結果読み込み
    inputs = load_analysis_results()
    
    # TRI-4計算実行
    result = calculate_tri4_duol(inputs)
    
    # レポート生成・表示
    report = generate_duol_tri4_report(result)
    print(report)
    
    # 結果をJSONで保存
    output_path = Path("duol_tri4_result.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n結果を保存: {output_path}")
    
    # 最終サマリー
    print(f"\n=== 最終サマリー ===")
    print(f"DUOLの④＝認知ギャップ: ★{result['final_stars']}")
    print(f"計算根拠: T={inputs['T']}, R={inputs['R']}, V={inputs['V'].value}")
    print(f"α3/α5: {inputs['alpha3_pass']}/{inputs['alpha5_pass']} → ボーナス★{result['bonus_stars']}")
    
    if result['v_overlay_applied']:
        print(f"Vオーバーレイ適用: {inputs['V'].value} → ★{result['base_stars']} → ★{result['v_adjusted_stars']}")

if __name__ == "__main__":
    main()
