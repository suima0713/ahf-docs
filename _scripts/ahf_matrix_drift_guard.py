#!/usr/bin/env python3
"""
AHF Matrix Drift Guard - マトリクス軸名のドリフト防止システム
固定軸名の正規表現ロック、出力検査、語彙禁止を実装
"""

import re
import json
import sys
from typing import Dict, List, Tuple

class MatrixDriftGuard:
    def __init__(self):
        # 固定軸名の正規表現パターン（完全一致ロック）
        self.fixed_axis_patterns = {
            r"^① 長期EV確度$": "① 長期EV確度",
            r"^② 長期EV勾配$": "② 長期EV勾配", 
            r"^③ バリュエーション＋認知ギャップ$": "③ バリュエーション＋認知ギャップ"
        }
        
        # 禁止語彙リスト
        self.forbidden_terms = [
            "近傾き", "VRG単独表記", "短期勾配", "Q/Q勾配",
            "NTMS", "VRG", "近期的", "短期"
        ]
        
        # 軸名の正規化マッピング
        self.axis_normalization = {
            "① 長期EV確度": "① 長期EV確度",
            "② 長期EV勾配": "② 長期EV勾配",
            "③ バリュエーション＋認知ギャップ": "③ バリュエーション＋認知ギャップ"
        }
    
    def validate_axis_name(self, axis_name: str) -> Tuple[bool, str]:
        """
        軸名の妥当性を検証
        Returns: (is_valid, error_message)
        """
        # 完全一致チェック
        for pattern, expected in self.fixed_axis_patterns.items():
            if re.match(pattern, axis_name):
                return True, ""
        
        return False, f"data_gap:name_drift - 軸名が固定パターンに一致しません: '{axis_name}'"
    
    def check_forbidden_terms(self, content: str) -> List[str]:
        """
        禁止語彙の検出
        Returns: 検出された禁止語彙のリスト
        """
        detected_terms = []
        for term in self.forbidden_terms:
            if term in content:
                detected_terms.append(term)
        return detected_terms
    
    def validate_matrix_output(self, matrix_data: Dict) -> Tuple[bool, List[str]]:
        """
        マトリクス出力の全体検証
        Returns: (is_valid, error_messages)
        """
        errors = []
        
        # 軸名の検証
        if "axes" in matrix_data:
            for axis in matrix_data["axes"]:
                if "name" in axis:
                    is_valid, error = self.validate_axis_name(axis["name"])
                    if not is_valid:
                        errors.append(error)
        
        # 禁止語彙の検出
        content_str = json.dumps(matrix_data, ensure_ascii=False)
        forbidden = self.check_forbidden_terms(content_str)
        if forbidden:
            errors.append(f"data_gap:forbidden_terms - 禁止語彙が検出されました: {forbidden}")
        
        return len(errors) == 0, errors
    
    def generate_matrix_template(self) -> Dict:
        """
        固定軸名のマトリクステンプレートを生成
        """
        template = {
            "meta": {
                "version": "v1.0",
                "drift_guard": "enabled",
                "fixed_axes": True
            },
            "axes": [
                {
                    "name": "① 長期EV確度",
                    "description": "長期EV確度",
                    "kpi": "g_fwd, ΔOPM_fwd",
                    "locked": True
                },
                {
                    "name": "② 長期EV勾配", 
                    "description": "長期EV勾配（12–24M）",
                    "kpi": "通期上方修正, RPO積み上がり, NDR高位",
                    "locked": True
                },
                {
                    "name": "③ バリュエーション＋認知ギャップ",
                    "description": "バリュエーション＋認知ギャップ",
                    "kpi": "Ro40, 価格層",
                    "locked": True
                }
            ],
            "decision_framework": {
                "s1_range": [0.0, 1.0],
                "s2_range": [0.0, 1.0], 
                "v_multiplier": {"Red": 0.75, "Yellow": 0.85, "Green": 1.0},
                "di_thresholds": {
                    "GO": 0.55,
                    "WATCH": 0.32,
                    "HOLD": 0.0
                }
            }
        }
        
        # テンプレートの検証
        is_valid, errors = self.validate_matrix_output(template)
        if not is_valid:
            print(f"テンプレート生成エラー: {errors}")
            sys.exit(1)
        
        return template

def main():
    guard = MatrixDriftGuard()
    
    # マトリクステンプレートの生成と検証
    template = guard.generate_matrix_template()
    
    # 出力ファイルの保存
    output_file = "ahf_matrix_template.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(template, f, ensure_ascii=False, indent=2)
    
    print(f"ドリフト防止マトリクステンプレートを生成しました: {output_file}")
    print("固定軸名:")
    for axis in template["axes"]:
        print(f"  - {axis['name']}")
    print("禁止語彙:")
    for term in guard.forbidden_terms:
        print(f"  - {term}")

if __name__ == "__main__":
    main()
