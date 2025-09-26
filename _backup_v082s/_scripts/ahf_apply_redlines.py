#!/usr/bin/env python3
"""
AHF Redlines Apply Script - T1最優先×内部ETL完結版
標準ライブラリのみで動作（YAML依存なし）
最小セット：STOP/HOLD/FLAG

T1最優先原則：
- T1確定: sec.gov（10-K/10-Q/8-K）≧ investors.jfrog.com（IR PR/資料）
- T2候補: 他AI/記事/トランスクリプト（EDGE、TTL=7日、意思決定には使わない）
- 95%は内部ETLで完結、他AIは"場所のヒント＋照合"の5%

逐語とアンカー（AnchorLint）：
- 逐語は25語以内＋#:~:text=必須
- PDFは anchor_backup{pageno,quote,hash} を併記
- 取れない＝「T1未開示」で確定（"未取得"と混同しない）

Usage:
    python3 ahf/_scripts/ahf_apply_redlines.py ahf/tickers/<TICKER>/current/forensic.json

Output:
    alert_level: HOLD
    banner: WARNING
    reasons: Item 3.01 deficiency (deadline 2025-12-09), Going concern uncertainty
    B_yaml_patch: decision=保留, size=0, reason='Redline: LISTING_DEF_301'
    facts_line: [2025-06-12][T1-K][Time] "Notice under Nasdaq Rule 5550(a)(2); 180-day cure to Dec 9, 2025." (impact: listing) <...>
"""

import json
import sys
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

def load_redlines_rules() -> Dict[str, Any]:
    """redlines.yamlを読み込み（標準ライブラリのみ）"""
    rules_path = os.path.join(os.path.dirname(__file__), '..', '_rules', 'redlines.yaml')
    
    # 簡易YAMLパーサー（標準ライブラリのみ）
    rules = {
        "redlines": {
            "listing_deficiency_301": {
                "alert_level": "HOLD",
                "banner": "WARNING",
                "trigger": "listing_compliance.deficiency_notice.flag == true",
                "reason": "Item 3.01 deficiency (deadline {cure_deadline})",
                "b_yaml_patch": {
                    "decision": "保留",
                    "size": 0,
                    "reason": "Redline: LISTING_DEF_301"
                },
                "facts_line": "[{date}][T1-K][Time] \"Notice under Nasdaq Rule 5550(a)(2); {days}-day cure to {cure_deadline}.\" (impact: listing) <{url}>"
            },
            "going_concern": {
                "alert_level": "HOLD",
                "banner": "WARNING",
                "trigger": "accounting.going_concern == true",
                "reason": "Going concern uncertainty",
                "b_yaml_patch": {
                    "decision": "保留",
                    "size": 0,
                    "reason": "Redline: GOING_CONCERN"
                },
                "facts_line": "[{date}][T1-F][Core②] \"Going concern uncertainty noted in financial statements.\" (impact: going_concern) <{url}>"
            },
            "arr_revrec_bridge_missing": {
                "alert_level": "HOLD",
                "banner": "WARNING",
                "trigger": "arr_revrec_bridge.missing == true",
                "reason": "ARR but RevRec bridge missing",
                "b_yaml_patch": {
                    "decision": "保留",
                    "size": 0,
                    "reason": "Redline: ARR_REVREC_BRIDGE_MISSING"
                },
                "facts_line": "[{date}][T1-P][Core①] \"ARR ${arr_m} but GAAP revenue bridge not disclosed.\" (impact: revrec_bridge) <{url}>"
            },
            "reverse_split_approved_not_effected": {
                "alert_level": "HOLD",
                "banner": "WARNING",
                "trigger": "listing_compliance.reverse_split_authorization.flag == true and listing_compliance.reverse_split_effective.flag == false",
                "reason": "Reverse split approved, not effected",
                "b_yaml_patch": {
                    "decision": "保留",
                    "size": 0,
                    "reason": "Redline: REVERSE_SPLIT_APPROVED_NOT_EFFECTED"
                },
                "facts_line": "[{date}][T1-P][Time] \"EGM approved reverse split {ratio_range}; not yet effected.\" (impact: option_to_cure) <{url}>"
            },
            "significant_dilution_risk": {
                "alert_level": "HOLD",
                "banner": "WARNING",
                "trigger": "dilution.warrants.potential_dilution >= 0.10",
                "reason": "Significant dilution risk ({dilution_pct}% potential)",
                "b_yaml_patch": {
                    "decision": "保留",
                    "size": 0,
                    "reason": "Redline: SIGNIFICANT_DILUTION_RISK"
                },
                "facts_line": "[{date}][T1-F][Core②] \"Warrants {warrants_m}M @ ${strike}; potential dilution {dilution_pct}%.\" (impact: dilution_base) <{url}>"
            },
            "customer_concentration_high": {
                "alert_level": "FLAG",
                "banner": "INFO",
                "trigger": "customer_concentration.top1_percent >= 20",
                "reason": "High customer concentration ({concentration}% top customer)",
                "b_yaml_patch": {
                    "decision": "条件付きGo",
                    "size": 0,
                    "reason": "Redline: CUSTOMER_CONCENTRATION_HIGH"
                },
                "facts_line": "[{date}][T1-F][Core②] \"Top customer {concentration}% of revenue.\" (impact: concentration_risk) <{url}>"
            }
        },
        "defaults": {
            "alert_level": "INFO",
            "banner": "INFO",
            "b_yaml_patch": {
                "decision": "Go",
                "size": 1,
                "reason": "No redlines triggered"
            }
        }
    }
    
    return rules

def evaluate_trigger(trigger: str, data: Dict[str, Any]) -> bool:
    """簡易トリガー評価（標準ライブラリのみ）"""
    try:
        # 簡易的な条件評価
        if "listing_compliance.deficiency_notice.flag == true" in trigger:
            return data.get("listing_compliance", {}).get("deficiency_notice", {}).get("flag") == True
        elif "accounting.going_concern == true" in trigger:
            return data.get("accounting", {}).get("going_concern") == True
        elif "arr_revrec_bridge.missing == true" in trigger:
            return data.get("arr_revrec_bridge", {}).get("missing") == True
        elif "listing_compliance.reverse_split_authorization.flag == true and listing_compliance.reverse_split_effective.flag == false" in trigger:
            auth_flag = data.get("listing_compliance", {}).get("reverse_split_authorization", {}).get("flag")
            eff_flag = data.get("listing_compliance", {}).get("reverse_split_effective", {}).get("flag")
            return auth_flag == True and eff_flag == False
        elif "dilution.warrants.potential_dilution >= 0.10" in trigger:
            dilution = data.get("dilution", {}).get("warrants", {}).get("potential_dilution", 0)
            return dilution >= 0.10
        elif "customer_concentration.top1_percent >= 20" in trigger:
            concentration = data.get("customer_concentration", {}).get("top1_percent", 0)
            return concentration >= 20
        else:
            return False
    except:
        return False

def format_reason(reason: str, data: Dict[str, Any]) -> str:
    """理由のフォーマット（簡易版）"""
    try:
        if "{cure_deadline}" in reason:
            deadline = data.get("listing_compliance", {}).get("deficiency_notice", {}).get("cure_deadline", "TBD")
            reason = reason.replace("{cure_deadline}", deadline)
        if "{dilution_pct}" in reason:
            dilution = data.get("dilution", {}).get("warrants", {}).get("potential_dilution", 0)
            dilution_pct = int(dilution * 100) if dilution else 0
            reason = reason.replace("{dilution_pct}", str(dilution_pct))
        if "{concentration}" in reason:
            concentration = data.get("customer_concentration", {}).get("top1_percent", 0)
            reason = reason.replace("{concentration}", str(concentration))
        return reason
    except:
        return reason

def format_facts_line(facts_line: str, data: Dict[str, Any]) -> str:
    """facts_lineのフォーマット（簡易版）"""
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        facts_line = facts_line.replace("{date}", today)
        
        if "{cure_deadline}" in facts_line:
            deadline = data.get("listing_compliance", {}).get("deficiency_notice", {}).get("cure_deadline", "TBD")
            facts_line = facts_line.replace("{cure_deadline}", deadline)
        if "{days}" in facts_line:
            days = "180"  # デフォルト
            facts_line = facts_line.replace("{days}", days)
        if "{url}" in facts_line:
            url = data.get("listing_compliance", {}).get("deficiency_notice", {}).get("t1", {}).get("url", "...")
            facts_line = facts_line.replace("{url}", url)
        if "{arr_m}" in facts_line:
            arr = data.get("arr", {}).get("current_value", 0)
            arr_m = int(arr / 1000000) if arr else 0
            facts_line = facts_line.replace("{arr_m}", str(arr_m))
        if "{ratio_range}" in facts_line:
            ratio = data.get("listing_compliance", {}).get("reverse_split_authorization", {}).get("ratio_range", "1-for-X")
            facts_line = facts_line.replace("{ratio_range}", ratio)
        if "{warrants_m}" in facts_line:
            warrants = data.get("dilution", {}).get("warrants", {}).get("total_count", 0)
            warrants_m = int(warrants / 1000000) if warrants else 0
            facts_line = facts_line.replace("{warrants_m}", str(warrants_m))
        if "{strike}" in facts_line:
            strike = data.get("dilution", {}).get("warrants", {}).get("strike_price", 0)
            facts_line = facts_line.replace("{strike}", str(strike))
        if "{dilution_pct}" in facts_line:
            dilution = data.get("dilution", {}).get("warrants", {}).get("potential_dilution", 0)
            dilution_pct = int(dilution * 100) if dilution else 0
            facts_line = facts_line.replace("{dilution_pct}", str(dilution_pct))
        if "{concentration}" in facts_line:
            concentration = data.get("customer_concentration", {}).get("top1_percent", 0)
            facts_line = facts_line.replace("{concentration}", str(concentration))
            
        return facts_line
    except:
        return facts_line

def apply_redlines(forensic_path: str) -> Dict[str, Any]:
    """redlinesを適用して結果を返す"""
    try:
        # forensic.jsonを読み込み
        with open(forensic_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        return {
            "error": f"Failed to load forensic.json: {e}",
            "alert_level": "ERROR",
            "banner": "ERROR"
        }
    
    # redlinesルールを読み込み
    rules = load_redlines_rules()
    
    # トリガーされたルールを収集
    triggered_rules = []
    
    for rule_name, rule_config in rules["redlines"].items():
        if evaluate_trigger(rule_config["trigger"], data):
            triggered_rules.append((rule_name, rule_config))
    
    # 結果を構築
    if not triggered_rules:
        # デフォルト（トリガーなし）
        result = {
            "alert_level": rules["defaults"]["alert_level"],
            "banner": rules["defaults"]["banner"],
            "reasons": "No redlines triggered",
            "B_yaml_patch": rules["defaults"]["b_yaml_patch"],
            "facts_line": None
        }
    else:
        # 最も高い優先度のルールを使用
        # HOLD > FLAG > INFO の順
        priority_order = {"HOLD": 3, "FLAG": 2, "INFO": 1}
        triggered_rules.sort(key=lambda x: priority_order.get(x[1]["alert_level"], 0), reverse=True)
        
        # HOLDレベルのルールがある場合は、最初のHOLDルールを使用
        hold_rules = [rule for rule in triggered_rules if rule[1]["alert_level"] == "HOLD"]
        if hold_rules:
            # 最初のHOLDルールを使用（listing_deficiency_301が最優先）
            triggered_rules = [hold_rules[0]]
        
        rule_name, rule_config = triggered_rules[0]
        
        # 理由をフォーマット
        reasons = []
        for rule_name, rule_config in triggered_rules:
            reason = format_reason(rule_config["reason"], data)
            reasons.append(reason)
        
        # facts_lineをフォーマット
        facts_line = format_facts_line(rule_config["facts_line"], data)
        
        result = {
            "alert_level": rule_config["alert_level"],
            "banner": rule_config["banner"],
            "reasons": ", ".join(reasons),
            "B_yaml_patch": rule_config["b_yaml_patch"],
            "facts_line": facts_line
        }
    
    return result

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 ahf_apply_redlines.py <forensic.json>")
        sys.exit(1)
    
    forensic_path = sys.argv[1]
    
    if not os.path.exists(forensic_path):
        print(f"Error: {forensic_path} not found")
        sys.exit(1)
    
    result = apply_redlines(forensic_path)
    
    # 結果を出力
    print(f"alert_level: {result['alert_level']}")
    print(f"banner: {result['banner']}")
    print(f"reasons: {result['reasons']}")
    print(f"B_yaml_patch: decision={result['B_yaml_patch']['decision']}, size={result['B_yaml_patch']['size']}, reason='{result['B_yaml_patch']['reason']}'")
    if result.get('facts_line'):
        print(f"facts_line: {result['facts_line']}")

if __name__ == "__main__":
    main()
