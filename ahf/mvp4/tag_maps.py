# -*- coding: utf-8 -*-
"""タグ別名マップ（Facts吸い上げ）
EDGAR Company FactsからRPO/CL/CAを安定取得
"""
from typing import Dict, Any, Optional, List

# RPO合計のタグ別名
RPO_TOTAL_KEYS = [
    "us-gaap:RemainingPerformanceObligation",
    "us-gaap:RemainingPerformanceObligations",
    "us-gaap:ContractWithCustomerLiability"  # フォールバック
]

# 契約負債のタグ別名
CL_KEYS = [
    "us-gaap:ContractWithCustomerLiabilityCurrent",
    "us-gaap:ContractWithCustomerLiabilityNoncurrent"
]

# 契約資産のタグ別名
CA_KEYS = [
    "us-gaap:ContractWithCustomerAsset", 
    "us-gaap:UnbilledReceivables"
]

# 売上のタグ別名
REVENUE_KEYS = [
    "us-gaap:Revenues",
    "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax"
]

def pick_fact(facts: Dict[str, Any], keys: List[str], unit: str = "USD") -> Optional[int]:
    """Company Factsから指定タグの最新値を取得"""
    facts_data = facts.get("facts", {})
    
    for key in keys:
        if key not in facts_data:
            continue
            
        tag_data = facts_data[key]
        units = tag_data.get("units", {})
        
        # 指定単位で検索
        for unit_key, items in units.items():
            if unit in unit_key.upper():
                if not items:
                    continue
                    
                # 最新期（endが最大）の値を取得
                try:
                    latest = max(items, key=lambda x: (
                        x.get("end", ""), 
                        x.get("fy", 0), 
                        x.get("fp", "")
                    ))
                    return int(round(latest["val"]))
                except (ValueError, KeyError):
                    continue
    
    return None

def get_rpo_total(facts: Dict[str, Any]) -> Optional[int]:
    """RPO合計を取得"""
    return pick_fact(facts, RPO_TOTAL_KEYS)

def get_contract_liability(facts: Dict[str, Any]) -> Optional[int]:
    """契約負債を取得"""
    return pick_fact(facts, CL_KEYS)

def get_contract_asset(facts: Dict[str, Any]) -> Optional[int]:
    """契約資産を取得"""
    return pick_fact(facts, CA_KEYS)

def get_revenue(facts: Dict[str, Any]) -> Optional[int]:
    """売上を取得"""
    return pick_fact(facts, REVENUE_KEYS)

def get_all_financials(facts: Dict[str, Any]) -> Dict[str, Optional[int]]:
    """全財務データを一括取得"""
    return {
        "rpo_total": get_rpo_total(facts),
        "contract_liability": get_contract_liability(facts),
        "contract_asset": get_contract_asset(facts),
        "revenue": get_revenue(facts)
    }
