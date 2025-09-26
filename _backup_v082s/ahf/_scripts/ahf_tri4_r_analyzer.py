#!/usr/bin/env python3
"""
AHF TRI-4 T1シグナル社会化度（R）判定機能
R：T1シグナルの社会化度（0–2）

判定基準：
0 = Item1A変更あり or 説明欠落
1 = Item1A=No changeだが開示に粒度不足（単一セグメント等）
2 = No changeかつ注記・指標が十分
"""

import json
import yaml
import re
from pathlib import Path
from typing import Dict, Any, Optional, List

class T1SocializationAnalyzer:
    """T1シグナル社会化度分析器"""
    
    def __init__(self):
        # Item1A変更を示すキーワード（実際の変更）
        self.item1a_change_keywords = [
            "material changes from", "significant changes from", "substantial changes from",
            "重要な変更", "実質的変更", "重大な変更"
        ]
        
        # Item1A=No changeを示すキーワード
        self.item1a_no_change_keywords = [
            "no material changes", "no significant changes", "no substantial changes",
            "変更なし", "重要変更なし", "実質変更なし"
        ]
        
        # 単一セグメントを示すキーワード
        self.single_segment_keywords = [
            "single operating segment", "single segment", "one operating segment",
            "単一セグメント", "一つのセグメント"
        ]
        
        # 開示粒度不足を示すキーワード
        self.granularity_insufficient_keywords = [
            "granularity", "breakdown", "disaggregation", "detailed",
            "粒度", "内訳", "詳細", "分類"
        ]
        
        # 十分な注記・指標を示すキーワード
        self.sufficient_disclosure_keywords = [
            "detailed breakdown", "comprehensive", "thorough", "extensive",
            "詳細内訳", "包括的", "徹底的", "広範囲"
        ]
    
    def extract_socialization_indicators_from_facts(self, facts_content: str) -> Dict[str, Any]:
        """facts.mdからT1社会化指標を抽出"""
        
        lines = facts_content.split('\n')
        socialization_data = {
            "item1a_changes": [],
            "item1a_no_changes": [],
            "single_segment_mentions": [],
            "granularity_issues": [],
            "sufficient_disclosures": []
        }
        
        for line in lines:
            # T1タグがある行のみ分析
            if '[T1-F]' in line or '[T1-P]' in line or '[T1-C]' in line:
                
                # Item1A=No changeの検出（優先）
                if any(keyword in line.lower() for keyword in self.item1a_no_change_keywords):
                    socialization_data["item1a_no_changes"].append(line.strip())
                # Item1A変更の検出（No changeでない場合のみ）
                elif any(keyword in line.lower() for keyword in self.item1a_change_keywords):
                    socialization_data["item1a_changes"].append(line.strip())
                
                # 単一セグメントの検出
                if any(keyword in line.lower() for keyword in self.single_segment_keywords):
                    socialization_data["single_segment_mentions"].append(line.strip())
                
                # 粒度不足の検出
                if any(keyword in line.lower() for keyword in self.granularity_insufficient_keywords):
                    socialization_data["granularity_issues"].append(line.strip())
                
                # 十分な開示の検出
                if any(keyword in line.lower() for keyword in self.sufficient_disclosure_keywords):
                    socialization_data["sufficient_disclosures"].append(line.strip())
        
        return socialization_data
    
    def analyze_socialization_degree(self, socialization_data: Dict[str, Any]) -> int:
        """T1シグナル社会化度（R）を判定"""
        
        item1a_changes = socialization_data["item1a_changes"]
        item1a_no_changes = socialization_data["item1a_no_changes"]
        single_segment_mentions = socialization_data["single_segment_mentions"]
        granularity_issues = socialization_data["granularity_issues"]
        sufficient_disclosures = socialization_data["sufficient_disclosures"]
        
        print(f"DEBUG: item1a_changes={len(item1a_changes)}, item1a_no_changes={len(item1a_no_changes)}")
        print(f"DEBUG: single_segment={len(single_segment_mentions)}, granularity={len(granularity_issues)}")
        
        # R=0: Item1A変更あり or 説明欠落
        if len(item1a_changes) > 0:
            return 0
        
        # R=1: Item1A=No changeだが開示に粒度不足（単一セグメント等）
        # DUOLのケース：Item1A=No change + 単一セグメント
        if (len(item1a_no_changes) > 0 and 
            (len(single_segment_mentions) > 0 or len(granularity_issues) > 0)):
            return 1
        
        # R=2: No changeかつ注記・指標が十分
        if (len(item1a_no_changes) > 0 and 
            len(sufficient_disclosures) > 0 and
            len(granularity_issues) == 0 and
            len(single_segment_mentions) == 0):
            return 2
        
        # デフォルト: R=0（説明欠落）
        return 0
    
    def generate_r_analysis_report(self, socialization_data: Dict[str, Any], R_score: int) -> str:
        """R分析レポート生成"""
        
        report_lines = [
            "=== T1シグナル社会化度（R）分析 ===",
            "",
            f"R = {R_score}/2",
            ""
        ]
        
        # R=2の場合
        if R_score == 2:
            report_lines.extend([
                "判定: No changeかつ注記・指標が十分",
                "",
                "Item1A=No change:",
            ])
            for item in socialization_data["item1a_no_changes"]:
                report_lines.append(f"  - {item}")
            
            report_lines.extend([
                "",
                "十分な開示:",
            ])
            for item in socialization_data["sufficient_disclosures"]:
                report_lines.append(f"  - {item}")
        
        # R=1の場合
        elif R_score == 1:
            report_lines.extend([
                "判定: Item1A=No changeだが開示に粒度不足",
                ""
            ])
            
            if socialization_data["item1a_no_changes"]:
                report_lines.extend([
                    "Item1A=No change:",
                ])
                for item in socialization_data["item1a_no_changes"]:
                    report_lines.append(f"  - {item}")
            
            if socialization_data["single_segment_mentions"]:
                report_lines.extend([
                    "",
                    "単一セグメント:",
                ])
                for item in socialization_data["single_segment_mentions"]:
                    report_lines.append(f"  - {item}")
            
            if socialization_data["granularity_issues"]:
                report_lines.extend([
                    "",
                    "粒度不足:",
                ])
                for item in socialization_data["granularity_issues"]:
                    report_lines.append(f"  - {item}")
        
        # R=0の場合
        else:
            report_lines.extend([
                "判定: Item1A変更あり or 説明欠落",
                ""
            ])
            
            if socialization_data["item1a_changes"]:
                report_lines.extend([
                    "Item1A変更:",
                ])
                for item in socialization_data["item1a_changes"]:
                    report_lines.append(f"  - {item}")
            else:
                report_lines.append("説明欠落")
        
        return "\n".join(report_lines)

def analyze_duol_r_socialization():
    """DUOLのT1シグナル社会化度分析"""
    
    # DUOLのfacts.md読み込み
    facts_path = Path("ahf/tickers/DUOL/current/facts.md")
    
    if not facts_path.exists():
        print(f"facts.mdが見つかりません: {facts_path}")
        return None
    
    with open(facts_path, 'r', encoding='utf-8') as f:
        facts_content = f.read()
    
    # T1社会化度分析
    analyzer = T1SocializationAnalyzer()
    socialization_data = analyzer.extract_socialization_indicators_from_facts(facts_content)
    
    # R値判定
    R_score = analyzer.analyze_socialization_degree(socialization_data)
    
    # レポート生成
    report = analyzer.generate_r_analysis_report(socialization_data, R_score)
    
    print(report)
    
    return {
        "R": R_score,
        "socialization_data": socialization_data,
        "report": report
    }

def main():
    """メイン実行"""
    print("=== DUOL T1シグナル社会化度（R）分析 ===")
    
    result = analyze_duol_r_socialization()
    
    if result:
        print(f"\nDUOLのR値: {result['R']}/2")
        
        # 結果をJSONで保存
        output_path = Path("duol_r_analysis.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                "R": result["R"],
                "socialization_data": result["socialization_data"]
            }, f, ensure_ascii=False, indent=2)
        
        print(f"結果を保存: {output_path}")

if __name__ == "__main__":
    main()
