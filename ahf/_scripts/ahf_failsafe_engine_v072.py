#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AHF Fail-safe Engine v0.7.2β
Stage-1での誤判定防止・欠落時はWATCH固定運用
"""

import json
import os
import sys
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass

@dataclass
class FailSafeResult:
    """Fail-safe結果"""
    decision: str
    missing_keys: List[str]
    failsafe_triggered: bool
    explanation: str

class FailSafeEngine:
    """Fail-safeエンジン"""
    
    def __init__(self):
        """初期化"""
        self.required_keys = {
            "alpha": ["guidance_qoq", "book_to_bill", "margin_trend"],
            "v_overlay": ["ev_sales", "rule_of_40"],
            "lec": ["survival_data", "moat_data", "demand_data"]
        }
    
    def check_missing_keys(self, triage_data: Dict[str, Any], 
                          facts_content: str) -> List[str]:
        """欠落キーのチェック"""
        missing = []
        confirmed_items = triage_data.get("CONFIRMED", [])
        
        # ②勾配の欠落チェック
        alpha_missing = self._check_alpha_keys(confirmed_items, facts_content)
        if alpha_missing:
            missing.extend([f"②{key}" for key in alpha_missing])
        
        # ③V-Overlayの欠落チェック
        v_overlay_missing = self._check_v_overlay_keys(confirmed_items)
        if v_overlay_missing:
            missing.extend([f"③{key}" for key in v_overlay_missing])
        
        # ①LECの欠落チェック
        lec_missing = self._check_lec_keys(confirmed_items, facts_content)
        if lec_missing:
            missing.extend([f"①{key}" for key in lec_missing])
        
        return missing
    
    def _check_alpha_keys(self, confirmed_items: List[Dict[str, Any]], 
                         facts_content: str) -> List[str]:
        """②勾配のキーチェック"""
        missing = []
        
        # 次Q q/q（ガイダンス）
        has_guidance = any("guidance" in item["kpi"].lower() or "qoq" in item["kpi"].lower() 
                          for item in confirmed_items)
        if not has_guidance:
            missing.append("次Q q/q")
        
        # B/B
        has_book_to_bill = any("book_to_bill" in item["kpi"].lower() or "book_to_bill" in item["kpi"].lower()
                              for item in confirmed_items)
        if not has_book_to_bill:
            missing.append("B/B")
        
        # マージン漂移
        has_margin_trend = any("margin" in item["kpi"].lower() or "gross_margin" in item["kpi"].lower()
                              for item in confirmed_items)
        if not has_margin_trend:
            missing.append("マージン漂移")
        
        return missing
    
    def _check_v_overlay_keys(self, confirmed_items: List[Dict[str, Any]]) -> List[str]:
        """③V-Overlayのキーチェック"""
        missing = []
        
        # EV/S
        has_ev_sales = any("ev_sales" in item["kpi"].lower() or "ev/sales" in item["kpi"].lower()
                          for item in confirmed_items)
        if not has_ev_sales:
            missing.append("EV/S(Fwd)")
        
        # Ro40
        has_ro40 = any("rule_of_40" in item["kpi"].lower() or "ro40" in item["kpi"].lower()
                      for item in confirmed_items)
        if not has_ro40:
            missing.append("Ro40")
        
        return missing
    
    def _check_lec_keys(self, confirmed_items: List[Dict[str, Any]], 
                       facts_content: str) -> List[str]:
        """①LECのキーチェック"""
        missing = []
        
        # 生存性データ
        has_survival = any(item["kpi"].lower() in ["cash_balance", "working_capital", "ebitda", "rcf_available"]
                          for item in confirmed_items)
        if not has_survival:
            missing.append("生存性データ")
        
        # 優位性データ
        has_moat = any(item["kpi"].lower() in ["asp_change", "product_differentiation", "backlog"]
                      for item in confirmed_items)
        if not has_moat:
            missing.append("優位性データ")
        
        # 需要データ
        has_demand = any(item["kpi"].lower() in ["volume_growth", "book_to_bill", "policy_risk"]
                        for item in confirmed_items) or "uncertainty" in facts_content.lower()
        if not has_demand:
            missing.append("需要データ")
        
        return missing
    
    def evaluate_failsafe(self, triage_data: Dict[str, Any], 
                         facts_content: str,
                         star_1: int, star_2: int, star_3: int) -> FailSafeResult:
        """Fail-safe評価"""
        
        # 欠落キーのチェック
        missing_keys = self.check_missing_keys(triage_data, facts_content)
        
        # Fail-safe判定
        failsafe_triggered = len(missing_keys) > 0
        
        if failsafe_triggered:
            decision = "WATCH"
            explanation = f"Fail-safe適用: 欠落キー={', '.join(missing_keys)}"
        else:
            # 通常のDecision判定
            if star_2 >= 3 and star_3 >= 2:
                decision = "GO"
            elif star_2 >= 2 and star_3 >= 1:
                decision = "WATCH"
            else:
                decision = "NO-GO"
            explanation = "通常判定適用"
        
        return FailSafeResult(
            decision=decision,
            missing_keys=missing_keys,
            failsafe_triggered=failsafe_triggered,
            explanation=explanation
        )

def apply_failsafe_logic(triage_file: str, facts_file: str,
                        star_1: int, star_2: int, star_3: int) -> Dict[str, Any]:
    """Fail-safe論理適用"""
    
    # ファイル読み込み
    with open(triage_file, 'r', encoding='utf-8') as f:
        triage_data = json.load(f)
    
    with open(facts_file, 'r', encoding='utf-8') as f:
        facts_content = f.read()
    
    # Fail-safe評価
    engine = FailSafeEngine()
    result = engine.evaluate_failsafe(triage_data, facts_content, star_1, star_2, star_3)
    
    return {
        "decision": result.decision,
        "missing_keys": result.missing_keys,
        "failsafe_triggered": result.failsafe_triggered,
        "explanation": result.explanation,
        "original_stars": {
            "star_1": star_1,
            "star_2": star_2,
            "star_3": star_3
        },
        "failsafe_rule": "欠落時はWATCH固定・GOは出さない"
    }

def main():
    if len(sys.argv) != 6:
        print("使用方法: python ahf_failsafe_engine_v072.py <triage.jsonのパス> <facts.mdのパス> <star_1> <star_2> <star_3>")
        sys.exit(1)
    
    triage_file = sys.argv[1]
    facts_file = sys.argv[2]
    star_1 = int(sys.argv[3])
    star_2 = int(sys.argv[4])
    star_3 = int(sys.argv[5])
    
    if not os.path.exists(triage_file):
        print(f"[ERROR] triage.jsonが見つかりません: {triage_file}")
        sys.exit(1)
    
    if not os.path.exists(facts_file):
        print(f"[ERROR] facts.mdが見つかりません: {facts_file}")
        sys.exit(1)
    
    try:
        result = apply_failsafe_logic(triage_file, facts_file, star_1, star_2, star_3)
        
        print("=== AHF Fail-safe Engine Results ===")
        print(f"Decision: {result['decision']}")
        print(f"Fail-safe適用: {result['failsafe_triggered']}")
        print(f"欠落キー: {result['missing_keys']}")
        print(f"説明: {result['explanation']}")
        print(f"元の★: {result['original_stars']['star_1']}×{result['original_stars']['star_2']}×{result['original_stars']['star_3']}")
        
    except Exception as e:
        print(f"[ERROR] 処理エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()






