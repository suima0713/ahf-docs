#!/usr/bin/env python3
"""
AHF TRI-4 α3/α5ボーナス★判定機能
α3/α5ボーナス★（最大+1）：α3 PASS（pp≤0.2 かつ 残差≤$8M）かつ α5 PASS（中央値−実績 ≤ −$3M）なら +1（上限★5）
"""

import json
import yaml
import re
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

class AlphaBonusAnalyzer:
    """α3/α5ボーナス★分析器"""
    
    def __init__(self):
        # α3判定基準
        self.alpha3_thresholds = {
            "pp_threshold": 0.2,      # pp ≤ 0.2
            "residual_threshold": 8.0  # 残差 ≤ $8M
        }
        
        # α5判定基準
        self.alpha5_thresholds = {
            "gap_threshold": -3.0     # 中央値−実績 ≤ −$3M
        }
        
        # α3関連キーワード
        self.alpha3_keywords = [
            "α3", "alpha3", "GM drift", "pp drift", "残差", "residual",
            "予測", "prediction", "モデル", "model"
        ]
        
        # α5関連キーワード
        self.alpha5_keywords = [
            "α5", "alpha5", "OpEx gap", "中央値", "median", "実績", "actual",
            "効率", "efficiency", "改善", "improvement"
        ]
    
    def extract_alpha_indicators_from_facts(self, facts_content: str) -> Dict[str, Any]:
        """facts.mdからα3/α5指標を抽出"""
        
        lines = facts_content.split('\n')
        alpha_data = {
            "alpha3_indicators": [],
            "alpha5_indicators": [],
            "alpha3_pp_values": [],
            "alpha3_residual_values": [],
            "alpha5_gap_values": []
        }
        
        for line in lines:
            # T1タグがある行のみ分析
            if '[T1-F]' in line or '[T1-P]' in line or '[T1-C]' in line:
                
                # α3指標の検出
                if any(keyword in line.lower() for keyword in self.alpha3_keywords):
                    alpha_data["alpha3_indicators"].append(line.strip())
                    
                    # pp値の抽出
                    pp_match = re.search(r'([+-]?\d+\.?\d*)\s*pp', line)
                    if pp_match:
                        pp_value = float(pp_match.group(1))
                        alpha_data["alpha3_pp_values"].append(pp_value)
                    
                    # 残差値の抽出（$記号付き）
                    residual_match = re.search(r'\$([+-]?\d+\.?\d*)[Mm]', line)
                    if residual_match:
                        residual_value = float(residual_match.group(1))
                        alpha_data["alpha3_residual_values"].append(residual_value)
                
                # α5指標の検出
                if any(keyword in line.lower() for keyword in self.alpha5_keywords):
                    alpha_data["alpha5_indicators"].append(line.strip())
                    
                    # ギャップ値の抽出（$記号付き、負の値も含む）
                    gap_match = re.search(r'([+-]?\d+\.?\d*)\s*[Mm]', line)
                    if gap_match:
                        gap_value = float(gap_match.group(1))
                        # 負の値の場合はそのまま、正の値の場合は符号を調整
                        if "−" in line or "-$" in line:
                            gap_value = -abs(gap_value)
                        alpha_data["alpha5_gap_values"].append(gap_value)
                        print(f"DEBUG: α5ギャップ値抽出: {gap_value} from {line.strip()}")
        
        return alpha_data
    
    def analyze_alpha3_pass(self, alpha_data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """α3 PASS判定"""
        
        pp_values = alpha_data["alpha3_pp_values"]
        residual_values = alpha_data["alpha3_residual_values"]
        
        # 最新の値を使用（最後の値）
        latest_pp = pp_values[-1] if pp_values else None
        latest_residual = residual_values[-1] if residual_values else None
        
        # α3判定基準チェック
        pp_pass = latest_pp is not None and abs(latest_pp) <= self.alpha3_thresholds["pp_threshold"]
        residual_pass = latest_residual is not None and abs(latest_residual) <= self.alpha3_thresholds["residual_threshold"]
        
        alpha3_pass = pp_pass and residual_pass
        
        analysis_result = {
            "pp_value": latest_pp,
            "pp_pass": pp_pass,
            "pp_threshold": self.alpha3_thresholds["pp_threshold"],
            "residual_value": latest_residual,
            "residual_pass": residual_pass,
            "residual_threshold": self.alpha3_thresholds["residual_threshold"],
            "alpha3_pass": alpha3_pass
        }
        
        return alpha3_pass, analysis_result
    
    def analyze_alpha5_pass(self, alpha_data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """α5 PASS判定"""
        
        gap_values = alpha_data["alpha5_gap_values"]
        
        # 最新の値を使用（最後の値）
        latest_gap = gap_values[-1] if gap_values else None
        
        # α5判定基準チェック（中央値−実績 ≤ −$3M）
        alpha5_pass = latest_gap is not None and latest_gap <= self.alpha5_thresholds["gap_threshold"]
        
        analysis_result = {
            "gap_value": latest_gap,
            "gap_pass": alpha5_pass,
            "gap_threshold": self.alpha5_thresholds["gap_threshold"],
            "alpha5_pass": alpha5_pass
        }
        
        return alpha5_pass, analysis_result
    
    def calculate_bonus_stars(self, alpha3_pass: bool, alpha5_pass: bool, current_stars: int) -> int:
        """ボーナス★計算：α3&α5両方PASSなら+1（上限★5）"""
        if alpha3_pass and alpha5_pass:
            # 上限★5をチェック
            return min(1, 5 - current_stars)
        return 0
    
    def generate_alpha_analysis_report(self, alpha_data: Dict[str, Any], alpha3_result: Dict[str, Any], alpha5_result: Dict[str, Any]) -> str:
        """α3/α5分析レポート生成"""
        
        report_lines = [
            "=== α3/α5ボーナス★分析 ===",
            "",
            f"α3 PASS: {'Yes' if alpha3_result['alpha3_pass'] else 'No'}",
            f"α5 PASS: {'Yes' if alpha5_result['alpha5_pass'] else 'No'}",
            ""
        ]
        
        # α3詳細
        report_lines.extend([
            "α3判定:",
            f"  pp値: {alpha3_result['pp_value']} (閾値: ≤{alpha3_result['pp_threshold']})",
            f"  pp判定: {'PASS' if alpha3_result['pp_pass'] else 'FAIL'}",
            f"  残差値: ${alpha3_result['residual_value']}M (閾値: ≤${alpha3_result['residual_threshold']}M)",
            f"  残差判定: {'PASS' if alpha3_result['residual_pass'] else 'FAIL'}",
            f"  α3総合: {'PASS' if alpha3_result['alpha3_pass'] else 'FAIL'}",
            ""
        ])
        
        # α5詳細
        report_lines.extend([
            "α5判定:",
            f"  ギャップ値: ${alpha5_result['gap_value']}M (閾値: ≤${alpha5_result['gap_threshold']}M)",
            f"  α5判定: {'PASS' if alpha5_result['alpha5_pass'] else 'FAIL'}",
            ""
        ])
        
        # ボーナス★判定
        bonus_stars = self.calculate_bonus_stars(
            alpha3_result['alpha3_pass'], 
            alpha5_result['alpha5_pass'], 
            3  # 仮の現在★数
        )
        
        report_lines.extend([
            "ボーナス★判定:",
            f"  条件: α3 PASS かつ α5 PASS",
            f"  結果: {'+1★' if bonus_stars > 0 else '+0★'}",
            f"  上限: ★5",
            ""
        ])
        
        # 抽出された指標
        if alpha_data["alpha3_indicators"]:
            report_lines.extend([
                "α3関連指標:",
            ])
            for indicator in alpha_data["alpha3_indicators"][:3]:  # 最初の3つのみ表示
                report_lines.append(f"  - {indicator}")
            report_lines.append("")
        
        if alpha_data["alpha5_indicators"]:
            report_lines.extend([
                "α5関連指標:",
            ])
            for indicator in alpha_data["alpha5_indicators"][:3]:  # 最初の3つのみ表示
                report_lines.append(f"  - {indicator}")
        
        return "\n".join(report_lines)

def analyze_duol_alpha_bonus():
    """DUOLのα3/α5ボーナス★分析"""
    
    # DUOLのfacts.md読み込み
    facts_path = Path("ahf/tickers/DUOL/current/facts.md")
    
    if not facts_path.exists():
        print(f"facts.mdが見つかりません: {facts_path}")
        return None
    
    with open(facts_path, 'r', encoding='utf-8') as f:
        facts_content = f.read()
    
    # α3/α5分析
    analyzer = AlphaBonusAnalyzer()
    alpha_data = analyzer.extract_alpha_indicators_from_facts(facts_content)
    
    # α3/α5判定
    alpha3_pass, alpha3_result = analyzer.analyze_alpha3_pass(alpha_data)
    alpha5_pass, alpha5_result = analyzer.analyze_alpha5_pass(alpha_data)
    
    # レポート生成
    report = analyzer.generate_alpha_analysis_report(alpha_data, alpha3_result, alpha5_result)
    
    print(report)
    
    return {
        "alpha3_pass": alpha3_pass,
        "alpha5_pass": alpha5_pass,
        "alpha3_result": alpha3_result,
        "alpha5_result": alpha5_result,
        "alpha_data": alpha_data,
        "report": report
    }

def main():
    """メイン実行"""
    print("=== DUOL α3/α5ボーナス★分析 ===")
    
    result = analyze_duol_alpha_bonus()
    
    if result:
        print(f"\nDUOLのα3/α5判定:")
        print(f"  α3 PASS: {result['alpha3_pass']}")
        print(f"  α5 PASS: {result['alpha5_pass']}")
        
        # 結果をJSONで保存
        output_path = Path("duol_alpha_analysis.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                "alpha3_pass": result["alpha3_pass"],
                "alpha5_pass": result["alpha5_pass"],
                "alpha3_result": result["alpha3_result"],
                "alpha5_result": result["alpha5_result"]
            }, f, ensure_ascii=False, indent=2)
        
        print(f"結果を保存: {output_path}")

if __name__ == "__main__":
    main()
