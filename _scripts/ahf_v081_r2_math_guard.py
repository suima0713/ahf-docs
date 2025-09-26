#!/usr/bin/env python3
"""
AHF v0.8.1-r2 Math Guard
数理ガードの実装

Purpose: 投資判断に直結する固定4軸で評価
MVP: ①②③④の名称と順序を絶対固定／T1 or T1*で確証（不足はn/a）／定型テーブル＋1行要約を即出力
"""

import json
import yaml
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum

class GuardType(Enum):
    """ガードタイプ"""
    CORE = "core"
    SCREEN = "screen"

class GuardStatus(Enum):
    """ガードステータス"""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"

@dataclass
class GuardResult:
    """ガード結果"""
    status: GuardStatus
    message: str
    details: Dict[str, Any]

class AHFv081R2MathGuard:
    """AHF v0.8.1-r2 数理ガード"""
    
    def __init__(self, guard_type: GuardType):
        self.guard_type = guard_type
        self.thresholds = self._load_thresholds()
        
    def _load_thresholds(self) -> Dict[str, Any]:
        """閾値読み込み"""
        if self.guard_type == GuardType.CORE:
            return {
                "gm_deviation_limit": 0.002,  # 0.2pp
                "residual_gp_limit": 8000000,  # $8M
                "gp_opex_ratio_min": 0.5,
                "gp_opex_ratio_max": 2.0,
                "ot_min": 46.8,
                "ot_max": 61.0
            }
        else:  # SCREEN
            return {
                "gm_deviation_limit": 0.005,  # 0.5pp (緩和)
                "residual_gp_limit": 12000000,  # $12M (緩和)
                "gp_opex_ratio_min": 0.3,
                "gp_opex_ratio_max": 3.0,
                "ot_min": 40.0,
                "ot_max": 70.0
            }
    
    def check_batch(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """バッチガードチェック"""
        results = []
        summary = {
            "total_items": len(data),
            "pass_count": 0,
            "fail_count": 0,
            "warning_count": 0,
            "pass_rate": 0.0
        }
        
        for item in data:
            result = self._check_item(item)
            results.append(result)
            
            if result.status == GuardStatus.PASS:
                summary["pass_count"] += 1
            elif result.status == GuardStatus.FAIL:
                summary["fail_count"] += 1
            else:
                summary["warning_count"] += 1
        
        summary["pass_rate"] = summary["pass_count"] / summary["total_items"] if summary["total_items"] > 0 else 0.0
        
        return {
            "results": results,
            "summary": summary,
            "guard_type": self.guard_type.value,
            "timestamp": datetime.now().isoformat()
        }
    
    def _check_item(self, item: Dict[str, Any]) -> GuardResult:
        """アイテムガードチェック"""
        issues = []
        
        # GM乖離チェック
        gm_actual = item.get("gm_actual", 0.0)
        gm_expected = item.get("gm_expected", 0.0)
        gm_deviation = abs(gm_actual - gm_expected)
        
        if gm_deviation > self.thresholds["gm_deviation_limit"]:
            issues.append(f"GM乖離が閾値を超過: {gm_deviation:.3f} > {self.thresholds['gm_deviation_limit']:.3f}")
        
        # 残差GPチェック
        gp = item.get("gp", 0)
        if gp > self.thresholds["residual_gp_limit"]:
            issues.append(f"残差GPが閾値を超過: ${gp:,} > ${self.thresholds['residual_gp_limit']:,}")
        
        # GP/OpEx比率チェック
        opex = item.get("opex", 0)
        if opex > 0:
            gp_opex_ratio = gp / opex
            if gp_opex_ratio < self.thresholds["gp_opex_ratio_min"]:
                issues.append(f"GP/OpEx比率が下限を下回る: {gp_opex_ratio:.2f} < {self.thresholds['gp_opex_ratio_min']:.2f}")
            elif gp_opex_ratio > self.thresholds["gp_opex_ratio_max"]:
                issues.append(f"GP/OpEx比率が上限を上回る: {gp_opex_ratio:.2f} > {self.thresholds['gp_opex_ratio_max']:.2f}")
        
        # OT範囲チェック
        ot = item.get("ot", 0.0)
        if ot < self.thresholds["ot_min"] or ot > self.thresholds["ot_max"]:
            issues.append(f"OTが範囲外: {ot:.1f} (範囲: {self.thresholds['ot_min']:.1f}-{self.thresholds['ot_max']:.1f})")
        
        # クロスチェック
        cross_check_issues = self._cross_check(item)
        issues.extend(cross_check_issues)
        
        if issues:
            return GuardResult(
                status=GuardStatus.FAIL,
                message="; ".join(issues),
                details={"issues": issues}
            )
        else:
            return GuardResult(
                status=GuardStatus.PASS,
                message="数理ガード通過",
                details={}
            )
    
    def _cross_check(self, item: Dict[str, Any]) -> List[str]:
        """クロスチェック"""
        issues = []
        
        # GP/OpEx/ERC/D&Aクロスチェック
        gp = item.get("gp", 0)
        opex = item.get("opex", 0)
        erc = item.get("erc", 0)
        da = item.get("da", 0)
        
        # GP = Revenue - COGS
        revenue = item.get("revenue", 0)
        cogs = item.get("cogs", 0)
        if revenue > 0 and cogs > 0:
            calculated_gp = revenue - cogs
            gp_diff = abs(gp - calculated_gp)
            if gp_diff > 1000:  # $1k tolerance
                issues.append(f"GP計算不一致: 実際={gp:,}, 計算={calculated_gp:,}")
        
        # OpEx = ERC + D&A + Other
        if opex > 0 and erc > 0 and da > 0:
            calculated_opex = erc + da
            opex_diff = abs(opex - calculated_opex)
            if opex_diff > 1000:  # $1k tolerance
                issues.append(f"OpEx計算不一致: 実際={opex:,}, 計算={calculated_opex:,}")
        
        return issues
    
    def check_gm_deviation(self, gm_actual: float, gm_expected: float) -> bool:
        """GM乖離チェック"""
        deviation = abs(gm_actual - gm_expected)
        return deviation <= self.thresholds["gm_deviation_limit"]
    
    def check_residual_gp(self, gp: float) -> bool:
        """残差GPチェック"""
        return gp <= self.thresholds["residual_gp_limit"]
    
    def check_gp_opex_ratio(self, gp: float, opex: float) -> bool:
        """GP/OpEx比率チェック"""
        if opex <= 0:
            return False
        
        ratio = gp / opex
        return (self.thresholds["gp_opex_ratio_min"] <= ratio <= self.thresholds["gp_opex_ratio_max"])
    
    def check_ot_range(self, ot: float) -> bool:
        """OT範囲チェック"""
        return self.thresholds["ot_min"] <= ot <= self.thresholds["ot_max"]
    
    def get_thresholds(self) -> Dict[str, Any]:
        """閾値取得"""
        return self.thresholds
    
    def update_thresholds(self, thresholds: Dict[str, Any]):
        """閾値更新"""
        self.thresholds.update(thresholds)
    
    def get_guard_type(self) -> GuardType:
        """ガードタイプ取得"""
        return self.guard_type
    
    def set_guard_type(self, guard_type: GuardType):
        """ガードタイプ設定"""
        self.guard_type = guard_type
        self.thresholds = self._load_thresholds()

def main():
    """メイン実行"""
    if len(sys.argv) < 3:
        print("Usage: python ahf_v081_r2_math_guard.py <input_file> <guard_type>")
        print("guard_type: core | screen")
        sys.exit(1)
    
    input_file = sys.argv[1]
    guard_type_str = sys.argv[2]
    
    # ガードタイプ設定
    guard_type = GuardType.CORE if guard_type_str == "core" else GuardType.SCREEN
    
    # 入力データ読み込み
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 数理ガード実行
    math_guard = AHFv081R2MathGuard(guard_type)
    result = math_guard.check_batch(data)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
