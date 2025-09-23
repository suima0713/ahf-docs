#!/usr/bin/env python3
"""
AHF TRI-4 v1.1（三点測量で★を決める）
④＝認知ギャップの機械化システム

入力（3点）：
- T：T1因果の明瞭度（0–2）
- R：T1シグナルの社会化度（0–2）  
- V：バリュエーション織込み度（Amber/Red/Green）

手順：
1. 基礎★ = T + R（0–4）→ 0→★1、1–2→★2、3→★3、4→★4
2. Vオーバーレイ適用
3. ボーナス★（α3&α5両方PASSなら+1、上限★5）
"""

import json
import yaml
import sys
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class VLevel(Enum):
    """バリュエーション織込み度"""
    GREEN = "Green"
    AMBER = "Amber"
    RED = "Red"

@dataclass
class TRI4Inputs:
    """TRI-4入力データ"""
    T: int  # T1因果の明瞭度（0–2）
    R: int  # T1シグナルの社会化度（0–2）
    V: VLevel  # バリュエーション織込み度
    alpha3_pass: bool  # α3 PASS判定
    alpha5_pass: bool  # α5 PASS判定

@dataclass
class TRI4Result:
    """TRI-4判定結果"""
    final_stars: int  # 最終★（1–5）
    base_stars: int   # 基礎★
    v_overlay_applied: bool  # Vオーバーレイ適用フラグ
    bonus_stars: int  # ボーナス★
    calculation_log: Dict[str, Any]  # 計算ログ

class TRI4Calculator:
    """TRI-4計算エンジン"""
    
    def __init__(self):
        # 基礎★マッピング（T + R → 基礎★）
        self.base_star_mapping = {
            0: 1,  # T=0, R=0 → ★1
            1: 2,  # T=1, R=0 or T=0, R=1 → ★2
            2: 2,  # T=2, R=0 or T=0, R=2 or T=1, R=1 → ★2
            3: 3,  # T=2, R=1 or T=1, R=2 → ★3
            4: 4   # T=2, R=2 → ★4
        }
        
        # Vオーバーレイルール
        self.v_overlay_rules = {
            VLevel.GREEN: {"adjustment": 0, "description": "±0（据え置き）"},
            VLevel.AMBER: {"adjustment": -1, "description": "★−1（下限★1）"},
            VLevel.RED: {"adjustment": -1, "cap": 3, "description": "★=min(★−1, 3)（自動キャップ=3）"}
        }
    
    def calculate_base_stars(self, T: int, R: int) -> int:
        """基礎★計算：T + R → 基礎★"""
        total_score = T + R
        return self.base_star_mapping.get(total_score, 1)
    
    def apply_v_overlay(self, base_stars: int, V: VLevel) -> Tuple[int, bool]:
        """Vオーバーレイ適用"""
        rule = self.v_overlay_rules[V]
        adjustment = rule["adjustment"]
        
        # 調整後の★
        adjusted_stars = max(1, base_stars + adjustment)  # 下限★1
        
        # Redの場合は自動キャップ=3を適用
        if V == VLevel.RED and "cap" in rule:
            adjusted_stars = min(adjusted_stars, rule["cap"])
        
        # Vオーバーレイが適用されたかチェック
        v_overlay_applied = (adjusted_stars != base_stars)
        
        return adjusted_stars, v_overlay_applied
    
    def calculate_bonus_stars(self, alpha3_pass: bool, alpha5_pass: bool, current_stars: int) -> int:
        """ボーナス★計算：α3&α5両方PASSなら+1（上限★5）"""
        if alpha3_pass and alpha5_pass:
            # 上限★5をチェック
            return min(1, 5 - current_stars)
        return 0
    
    def calculate_tri4(self, inputs: TRI4Inputs) -> TRI4Result:
        """TRI-4計算実行"""
        
        # 1. 基礎★計算
        base_stars = self.calculate_base_stars(inputs.T, inputs.R)
        
        # 2. Vオーバーレイ適用
        v_adjusted_stars, v_overlay_applied = self.apply_v_overlay(base_stars, inputs.V)
        
        # 3. ボーナス★計算
        bonus_stars = self.calculate_bonus_stars(inputs.alpha3_pass, inputs.alpha5_pass, v_adjusted_stars)
        
        # 4. 最終★計算
        final_stars = v_adjusted_stars + bonus_stars
        
        # 計算ログ生成
        calculation_log = {
            "inputs": {
                "T": inputs.T,
                "R": inputs.R,
                "V": inputs.V.value,
                "alpha3_pass": inputs.alpha3_pass,
                "alpha5_pass": inputs.alpha5_pass
            },
            "base_stars": base_stars,
            "v_overlay": {
                "applied": v_overlay_applied,
                "rule": self.v_overlay_rules[inputs.V]["description"],
                "adjusted_stars": v_adjusted_stars
            },
            "bonus_stars": bonus_stars,
            "final_stars": final_stars
        }
        
        return TRI4Result(
            final_stars=final_stars,
            base_stars=base_stars,
            v_overlay_applied=v_overlay_applied,
            bonus_stars=bonus_stars,
            calculation_log=calculation_log
        )
    
    def generate_report(self, result: TRI4Result) -> str:
        """TRI-4レポート生成"""
        log = result.calculation_log
        inputs = log["inputs"]
        
        report_lines = [
            "=== TRI-4 v1.1 三点測量判定 ===",
            "",
            "【入力（3点）】",
            f"T（T1因果明瞭度）: {inputs['T']}/2",
            f"R（T1シグナル社会化度）: {inputs['R']}/2", 
            f"V（バリュエーション織込み度）: {inputs['V']}",
            "",
            "【α3/α5判定】",
            f"α3 PASS: {'Yes' if inputs['alpha3_pass'] else 'No'}",
            f"α5 PASS: {'Yes' if inputs['alpha5_pass'] else 'No'}",
            "",
            "【計算過程】",
            f"基礎★: T+R = {inputs['T']}+{inputs['R']} = {log['base_stars']}",
            f"Vオーバーレイ: {log['v_overlay']['rule']}",
            f"V調整後★: {log['v_overlay']['adjusted_stars']}",
            f"ボーナス★: {result.bonus_stars}",
            "",
            f"【最終結果】",
            f"④＝認知ギャップ: ★{result.final_stars}",
            ""
        ]
        
        # 詳細説明
        if inputs['T'] == 2:
            report_lines.append("T=2: QoQとYoYの一次説明が整合している")
        elif inputs['T'] == 1:
            report_lines.append("T=1: 片側（QoQ or YoY）説明あり")
        else:
            report_lines.append("T=0: 不明瞭")
        
        if inputs['R'] == 2:
            report_lines.append("R=2: No changeかつ注記・指標が十分")
        elif inputs['R'] == 1:
            report_lines.append("R=1: Item1A=No changeだが開示に粒度不足")
        else:
            report_lines.append("R=0: Item1A変更あり or 説明欠落")
        
        report_lines.extend([
            "",
            "【使い方（超要約）】",
            "星はブレない: T, Rが変わらない限り、指摘や私見では動かない",
            "価格は別レイヤーで制御: VがAmber/Redなら自動で減点",
            "強い確証が出たらだけ加点: α3&α5を"両方"満たした時だけ+1"
        ])
        
        return "\n".join(report_lines)

def main():
    """メイン実行"""
    if len(sys.argv) < 6:
        print("使用法: python ahf_tri4_v11.py <T> <R> <V> <alpha3_pass> <alpha5_pass>")
        print("  T: T1因果の明瞭度（0-2）")
        print("  R: T1シグナルの社会化度（0-2）")
        print("  V: バリュエーション織込み度（Green/Amber/Red）")
        print("  alpha3_pass: α3 PASS（true/false）")
        print("  alpha5_pass: α5 PASS（true/false）")
        sys.exit(1)
    
    try:
        # 引数解析
        T = int(sys.argv[1])
        R = int(sys.argv[2])
        V_str = sys.argv[3].title()
        alpha3_pass = sys.argv[4].lower() == 'true'
        alpha5_pass = sys.argv[5].lower() == 'true'
        
        # 入力値検証
        if not (0 <= T <= 2):
            raise ValueError("T must be 0-2")
        if not (0 <= R <= 2):
            raise ValueError("R must be 0-2")
        if V_str not in ["Green", "Amber", "Red"]:
            raise ValueError("V must be Green/Amber/Red")
        
        V = VLevel(V_str)
        
        # TRI-4入力作成
        inputs = TRI4Inputs(
            T=T,
            R=R,
            V=V,
            alpha3_pass=alpha3_pass,
            alpha5_pass=alpha5_pass
        )
        
        # TRI-4計算実行
        calculator = TRI4Calculator()
        result = calculator.calculate_tri4(inputs)
        
        # レポート生成・表示
        report = calculator.generate_report(result)
        print(report)
        
        # 結果をJSONで保存
        output_path = Path("tri4_result.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result.calculation_log, f, ensure_ascii=False, indent=2)
        
        print(f"\n結果を保存: {output_path}")
        
    except Exception as e:
        print(f"エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
