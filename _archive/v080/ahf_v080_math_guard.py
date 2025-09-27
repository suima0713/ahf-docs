#!/usr/bin/env python3
"""
AHF v0.8.0 数理ガード
数理検算（Core基準）：GM乖離≤0.2pp、残差GP≤$8,000k、GP/OpEx/ERC/D&Aクロス、OT∈[46.8,61.0]

Purpose: 投資判断に直結する固定3軸で評価する
MVP: ①②③の名称と順序を固定／T1で確証（不足は n/a）／定型テーブル＋1行要約を即時出力
"""

import json
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class GuardType(Enum):
    CORE = "core"      # Core基準
    TURBO = "turbo"    # Turbo Screen（緩和）

@dataclass
class MathGuardResult:
    """数理ガード結果"""
    pass: bool
    gm_deviation: float
    residual_gp: float
    alpha5_grid: float
    cross_validation: bool
    ot_range: bool
    messages: List[str]

class AHFv080MathGuard:
    """AHF v0.8.0 数理ガード実装"""
    
    def __init__(self, guard_type: GuardType = GuardType.CORE):
        self.guard_type = guard_type
        
        # Core基準の閾値
        if guard_type == GuardType.CORE:
            self.gm_deviation_threshold = 0.2    # GM乖離 ≤0.2pp
            self.residual_gp_threshold = 8000    # 残差GP ≤$8,000k
            self.alpha5_grid_threshold = -3.0    # α5格子 ≤−$3〜−$5M
        else:  # TURBO
            self.gm_deviation_threshold = 0.5    # GM乖離 ≤0.5pp
            self.residual_gp_threshold = 12000   # 残差GP ≤$12M
            self.alpha5_grid_threshold = -2.5   # α5格子 ≤−$2.5M
        
        # OT範囲
        self.ot_min = 46.8
        self.ot_max = 61.0
    
    def check_math_guards(self, data: Dict[str, Any]) -> MathGuardResult:
        """数理ガード実行"""
        result = MathGuardResult(
            pass=False,
            gm_deviation=0.0,
            residual_gp=0.0,
            alpha5_grid=0.0,
            cross_validation=False,
            ot_range=False,
            messages=[]
        )
        
        # GM乖離チェック
        gm_deviation = self._calculate_gm_deviation(data)
        result.gm_deviation = gm_deviation
        
        if gm_deviation <= self.gm_deviation_threshold:
            result.messages.append(f"GM乖離 PASS: {gm_deviation:.1f}pp ≤ {self.gm_deviation_threshold}pp")
        else:
            result.messages.append(f"GM乖離 FAIL: {gm_deviation:.1f}pp > {self.gm_deviation_threshold}pp")
        
        # 残差GPチェック
        residual_gp = self._calculate_residual_gp(data)
        result.residual_gp = residual_gp
        
        if residual_gp <= self.residual_gp_threshold:
            result.messages.append(f"残差GP PASS: ${residual_gp:,.0f}k ≤ ${self.residual_gp_threshold:,.0f}k")
        else:
            result.messages.append(f"残差GP FAIL: ${residual_gp:,.0f}k > ${self.residual_gp_threshold:,.0f}k")
        
        # α5格子チェック
        alpha5_grid = self._calculate_alpha5_grid(data)
        result.alpha5_grid = alpha5_grid
        
        if alpha5_grid <= self.alpha5_grid_threshold:
            result.messages.append(f"α5格子 PASS: ${alpha5_grid:,.1f}M ≤ ${self.alpha5_grid_threshold:,.1f}M")
        else:
            result.messages.append(f"α5格子 FAIL: ${alpha5_grid:,.1f}M > {self.alpha5_grid_threshold:,.1f}M")
        
        # クロスバリデーション
        cross_validation = self._check_cross_validation(data)
        result.cross_validation = cross_validation
        
        if cross_validation:
            result.messages.append("クロスバリデーション PASS: GP/OpEx/ERC/D&A整合")
        else:
            result.messages.append("クロスバリデーション FAIL: GP/OpEx/ERC/D&A不整合")
        
        # OT範囲チェック
        ot_range = self._check_ot_range(data)
        result.ot_range = ot_range
        
        if ot_range:
            result.messages.append(f"OT範囲 PASS: {self.ot_min} ≤ OT ≤ {self.ot_max}")
        else:
            result.messages.append(f"OT範囲 FAIL: OT ∉ [{self.ot_min}, {self.ot_max}]")
        
        # 全体パス判定
        result.pass = (
            gm_deviation <= self.gm_deviation_threshold and
            residual_gp <= self.residual_gp_threshold and
            alpha5_grid <= self.alpha5_grid_threshold and
            cross_validation and
            ot_range
        )
        
        if result.pass:
            result.messages.append("数理ガード OVERALL PASS: 全チェック通過")
        else:
            result.messages.append("数理ガード OVERALL FAIL: チェック失敗")
        
        return result
    
    def _calculate_gm_deviation(self, data: Dict[str, Any]) -> float:
        """GM乖離計算"""
        # 実装時は実際のGM乖離計算
        # 例: |GM_actual - GM_expected|
        gm_actual = data.get("gm_actual", 0.0)
        gm_expected = data.get("gm_expected", 0.0)
        return abs(gm_actual - gm_expected)
    
    def _calculate_residual_gp(self, data: Dict[str, Any]) -> float:
        """残差GP計算"""
        # 実装時は実際の残差GP計算
        # 例: GP - (Rev × GM) - OpEx
        gp = data.get("gp", 0.0)
        rev = data.get("revenue", 0.0)
        gm = data.get("gm", 0.0)
        opex = data.get("opex", 0.0)
        
        expected_gp = rev * gm - opex
        return gp - expected_gp
    
    def _calculate_alpha5_grid(self, data: Dict[str, Any]) -> float:
        """α5格子計算"""
        # 実装時は実際のα5格子計算
        # 例: OpEx - (Rev × (NG-GM) - KPI)
        opex = data.get("opex", 0.0)
        rev = data.get("revenue", 0.0)
        ng_gm = data.get("ng_gm", 0.0)
        kpi = data.get("kpi", 0.0)
        
        return opex - (rev * ng_gm - kpi)
    
    def _check_cross_validation(self, data: Dict[str, Any]) -> bool:
        """クロスバリデーション（GP/OpEx/ERC/D&A）"""
        # 実装時は実際のクロスバリデーション
        # 例: GP + OpEx + ERC + D&A の整合性チェック
        gp = data.get("gp", 0.0)
        opex = data.get("opex", 0.0)
        erc = data.get("erc", 0.0)
        da = data.get("da", 0.0)
        
        # 簡易的な整合性チェック
        total = gp + opex + erc + da
        return abs(total - data.get("total", 0.0)) < 1000  # $1M以内の誤差
    
    def _check_ot_range(self, data: Dict[str, Any]) -> bool:
        """OT範囲チェック"""
        ot = data.get("ot", 0.0)
        return self.ot_min <= ot <= self.ot_max
    
    def check_batch(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """バッチ数理ガード実行"""
        results = {
            "guard_type": self.guard_type.value,
            "total_items": len(items),
            "passed_items": 0,
            "failed_items": 0,
            "results": [],
            "summary": {}
        }
        
        for item in items:
            result = self.check_math_guards(item)
            
            if result.pass:
                results["passed_items"] += 1
            else:
                results["failed_items"] += 1
            
            results["results"].append({
                "item_id": item.get("id", ""),
                "result": result
            })
        
        # サマリー生成
        results["summary"] = {
            "pass_rate": results["passed_items"] / results["total_items"] if results["total_items"] > 0 else 0,
            "common_failures": self._analyze_common_failures(results["results"])
        }
        
        return results
    
    def _analyze_common_failures(self, results: List[Dict[str, Any]]) -> List[str]:
        """共通の失敗パターン分析"""
        failure_patterns = []
        
        for result_item in results:
            result = result_item["result"]
            if not result.pass:
                if result.gm_deviation > self.gm_deviation_threshold:
                    failure_patterns.append("GM乖離超過")
                if result.residual_gp > self.residual_gp_threshold:
                    failure_patterns.append("残差GP超過")
                if result.alpha5_grid > self.alpha5_grid_threshold:
                    failure_patterns.append("α5格子超過")
                if not result.cross_validation:
                    failure_patterns.append("クロスバリデーション失敗")
                if not result.ot_range:
                    failure_patterns.append("OT範囲外")
        
        # 頻度順にソート
        from collections import Counter
        counter = Counter(failure_patterns)
        return [pattern for pattern, count in counter.most_common()]
    
    def generate_guard_report(self, results: Dict[str, Any]) -> str:
        """数理ガードレポート生成"""
        report = f"""
# 数理ガード レポート

## サマリー
- ガードタイプ: {results['guard_type']}
- 総項目数: {results['total_items']}
- 通過項目数: {results['passed_items']}
- 失敗項目数: {results['failed_items']}
- 通過率: {results['summary']['pass_rate']:.1%}

## 共通の失敗パターン
{chr(10).join(f"- {pattern}" for pattern in results['summary']['common_failures'])}

## 詳細結果
"""
        
        for result_item in results["results"]:
            item_id = result_item["item_id"]
            result = result_item["result"]
            
            report += f"\n### {item_id}\n"
            report += f"- 通過: {'✅' if result.pass else '❌'}\n"
            report += f"- GM乖離: {result.gm_deviation:.1f}pp\n"
            report += f"- 残差GP: ${result.residual_gp:,.0f}k\n"
            report += f"- α5格子: ${result.alpha5_grid:,.1f}M\n"
            report += f"- クロスバリデーション: {'✅' if result.cross_validation else '❌'}\n"
            report += f"- OT範囲: {'✅' if result.ot_range else '❌'}\n"
            
            for message in result.messages:
                report += f"- {message}\n"
        
        return report

def main():
    """メイン実行"""
    if len(sys.argv) < 3:
        print("Usage: python ahf_v080_math_guard.py <input_file> <guard_type>")
        print("guard_type: core|turbo")
        sys.exit(1)
    
    input_file = sys.argv[1]
    guard_type_str = sys.argv[2]
    
    try:
        guard_type = GuardType.CORE if guard_type_str == "core" else GuardType.TURBO
        
        with open(input_file, 'r', encoding='utf-8') as f:
            if input_file.endswith('.json'):
                data = json.load(f)
            else:
                data = json.loads(f.read())
        
        math_guard = AHFv080MathGuard(guard_type)
        results = math_guard.check_batch(data)
        
        print(json.dumps(results, indent=2, ensure_ascii=False))
        
        # レポート生成
        report = math_guard.generate_guard_report(results)
        print("\n" + "="*50)
        print(report)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

