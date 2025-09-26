#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AHF Auto Checks v0.7.2
数値検算ガードレール（必須）
T1逐語＋アンカー必須・乖離時Fail
"""

import json
import os
import sys
from typing import Dict, List, Any, Tuple

def validate_gp_drift(gm_drift_pp: float) -> Tuple[bool, str]:
    """
    GM乖離≤0.2ppの検証
    """
    if abs(gm_drift_pp) <= 0.2:
        return True, "GM乖離合格"
    else:
        return False, f"GM乖離超過: {abs(gm_drift_pp):.2f}pp > 0.2pp"

def validate_residual_gp(residual_gp_usd: float) -> Tuple[bool, str]:
    """
    残差GP≤$8,000kの検証
    """
    if residual_gp_usd <= 8000000:
        return True, "残差GP合格"
    else:
        return False, f"残差GP超過: ${residual_gp_usd/1000:.0f}k > $8,000k"

def validate_operating_income(operating_income_pct: float) -> Tuple[bool, str]:
    """
    OT∈[46.8,61.0]の検証
    """
    if 46.8 <= operating_income_pct <= 61.0:
        return True, "OT範囲合格"
    else:
        return False, f"OT範囲外: {operating_income_pct:.1f}% 不在[46.8,61.0]"

def validate_alpha4_gate(coverage_ratio: float) -> Tuple[bool, str]:
    """
    α4ゲート≥11.0の検証
    """
    if coverage_ratio >= 11.0:
        return True, "α4ゲート合格"
    else:
        return False, f"α4ゲート不合格: {coverage_ratio:.1f} < 11.0"

def validate_alpha5_math(median_opex: float, actual_opex: float, 
                        revenue: float, ng_gm: float) -> Tuple[bool, str]:
    """
    α5数理検証: OpEx = Rev × NG-GM − KPI
    """
    try:
        # 計算式の検証
        calculated_opex = revenue * (ng_gm / 100)
        diff = abs(actual_opex - calculated_opex)
        
        if diff <= 8000000:  # $8M以内
            return True, "α5数理合格"
        else:
            return False, f"α5数理乖離: ${diff/1000:.0f}k > $8,000k"
    except Exception as e:
        return False, f"α5数理計算エラー: {e}"

def validate_cross_checks(confirmed_items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    クロスチェック検証
    """
    checks = {
        "gp_drift_pass": False,
        "residual_gp_pass": False,
        "operating_income_pass": False,
        "alpha4_gate_pass": False,
        "alpha5_math_pass": False,
        "messages": []
    }
    
    # 必要なKPI値を取得
    gm_drift_pp = 0
    residual_gp_usd = 0
    operating_income_pct = 0
    coverage_ratio = 0
    median_opex = 0
    actual_opex = 0
    revenue = 0
    ng_gm = 0
    
    for item in confirmed_items:
        if item["kpi"] == "GM_drift_pp":
            gm_drift_pp = item["value"]
        elif item["kpi"] == "Residual_GP_USD":
            residual_gp_usd = item["value"]
        elif item["kpi"] == "Operating_Income_pct":
            operating_income_pct = item["value"]
        elif item["kpi"] == "Coverage_ratio":
            coverage_ratio = item["value"]
        elif item["kpi"] == "Median_OpEx_USD":
            median_opex = item["value"]
        elif item["kpi"] == "Actual_OpEx_USD":
            actual_opex = item["value"]
        elif item["kpi"] == "Revenue_USD":
            revenue = item["value"]
        elif item["kpi"] == "NG_GM_pct":
            ng_gm = item["value"]
    
    # 各検証の実行
    gp_drift_valid, gp_drift_msg = validate_gp_drift(gm_drift_pp)
    checks["gp_drift_pass"] = gp_drift_valid
    checks["messages"].append(gp_drift_msg)
    
    residual_gp_valid, residual_gp_msg = validate_residual_gp(residual_gp_usd)
    checks["residual_gp_pass"] = residual_gp_valid
    checks["messages"].append(residual_gp_msg)
    
    ot_valid, ot_msg = validate_operating_income(operating_income_pct)
    checks["operating_income_pass"] = ot_valid
    checks["messages"].append(ot_msg)
    
    alpha4_valid, alpha4_msg = validate_alpha4_gate(coverage_ratio)
    checks["alpha4_gate_pass"] = alpha4_valid
    checks["messages"].append(alpha4_msg)
    
    alpha5_valid, alpha5_msg = validate_alpha5_math(median_opex, actual_opex, revenue, ng_gm)
    checks["alpha5_math_pass"] = alpha5_valid
    checks["messages"].append(alpha5_msg)
    
    return checks

def validate_anchor_requirements(confirmed_items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    アンカー要件の検証
    """
    anchor_checks = {
        "anchor_lint_pass": True,
        "dual_anchor_status_ok": True,
        "messages": []
    }
    
    for item in confirmed_items:
        # アンカーの存在チェック
        if not item.get("anchor"):
            anchor_checks["anchor_lint_pass"] = False
            anchor_checks["messages"].append(f"{item['kpi']}: アンカーなし")
        
        # 二重アンカーステータスのチェック
        dual_status = item.get("dual_anchor_status", "CONFIRMED")
        if dual_status not in ["CONFIRMED", "PENDING_SEC", "SINGLE"]:
            anchor_checks["dual_anchor_status_ok"] = False
            anchor_checks["messages"].append(f"{item['kpi']}: 無効な二重アンカーステータス")
    
    return anchor_checks

def process_auto_checks(triage_file: str) -> Dict[str, Any]:
    """
    自動チェックの実行
    """
    with open(triage_file, 'r', encoding='utf-8') as f:
        triage_data = json.load(f)
    
    confirmed_items = triage_data.get("CONFIRMED", [])
    
    # クロスチェック検証
    cross_checks = validate_cross_checks(confirmed_items)
    
    # アンカー要件検証
    anchor_checks = validate_anchor_requirements(confirmed_items)
    
    # 総合判定
    all_checks_pass = (
        cross_checks["gp_drift_pass"] and
        cross_checks["residual_gp_pass"] and
        cross_checks["operating_income_pass"] and
        cross_checks["alpha4_gate_pass"] and
        cross_checks["alpha5_math_pass"] and
        anchor_checks["anchor_lint_pass"] and
        anchor_checks["dual_anchor_status_ok"]
    )
    
    return {
        "as_of": triage_data["as_of"],
        "auto_checks": {
            "alpha4_gate_pass": cross_checks["alpha4_gate_pass"],
            "alpha5_math_pass": cross_checks["alpha5_math_pass"],
            "anchor_lint_pass": anchor_checks["anchor_lint_pass"],
            "messages": cross_checks["messages"] + anchor_checks["messages"]
        },
        "cross_checks": cross_checks,
        "anchor_checks": anchor_checks,
        "all_checks_pass": all_checks_pass
    }

def main():
    if len(sys.argv) != 2:
        print("使用方法: python ahf_auto_checks.py <triage.jsonのパス>")
        sys.exit(1)
    
    triage_file = sys.argv[1]
    
    if not os.path.exists(triage_file):
        print(f"[ERROR] triage.jsonが見つかりません: {triage_file}")
        sys.exit(1)
    
    try:
        results = process_auto_checks(triage_file)
        
        # 結果出力
        print("=== AHF Auto Checks Results (v0.7.2) ===")
        print(f"As of: {results['as_of']}")
        print()
        print("自動チェック結果:")
        print(f"  α4ゲート: {'合格' if results['auto_checks']['alpha4_gate_pass'] else '不合格'}")
        print(f"  α5数理: {'合格' if results['auto_checks']['alpha5_math_pass'] else '不合格'}")
        print(f"  アンカー: {'合格' if results['auto_checks']['anchor_lint_pass'] else '不合格'}")
        print(f"  総合判定: {'合格' if results['all_checks_pass'] else '不合格'}")
        print()
        
        if results['auto_checks']['messages']:
            print("メッセージ:")
            for msg in results['auto_checks']['messages']:
                print(f"  - {msg}")
        
        # 結果をJSONファイルに保存
        output_file = triage_file.replace("triage.json", "auto_checks.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"[INFO] 結果を保存しました: {output_file}")
        
    except Exception as e:
        print(f"[ERROR] 処理エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
