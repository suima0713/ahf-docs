#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AHF LEC Analysis Fail-safe v0.7.2β
①長期EV成長の確かさ（LEC）反証優先・減点のみ
"""

import json
import os
import sys
import yaml
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass

@dataclass
class LECFailSafeResult:
    """LEC Fail-safe結果"""
    survival_gate: str  # PASS/FAIL
    moat_gate: str      # PASS/FAIL  
    demand_gate: str    # PASS/FAIL
    final_star: int     # min{機械式ベース, 3ゲート判定}（上振れ不可）
    explanation: str
    gate_details: Dict[str, Any]

class LECFailSafeEngine:
    """LEC Fail-safeエンジン（反証優先・減点のみ）"""
    
    def __init__(self, config_dir: str = "../config"):
        """初期化"""
        self.config_dir = os.path.join(os.path.dirname(__file__), config_dir)
        self.config = self._load_config()
        
    def _load_config(self) -> Dict:
        """設定の読み込み"""
        try:
            config_file = os.path.join(self.config_dir, "thresholds.yaml")
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            return {
                "lec_failsafe": {
                    "survival_thresholds": {
                        "cash_min": 100000000,      # $100M
                        "working_capital_min": 0,   # 正数
                        "ebitda_min": 0,           # 正数
                        "rcf_min": 50000000        # $50M
                    },
                    "moat_penalties": {
                        "asp_decline": -1.0,       # ASP下落
                        "price_pressure": -0.5,    # 価格圧力
                        "competitive_threat": -0.5 # 競合脅威
                    },
                    "demand_penalties": {
                        "policy_risk": -1.0,       # 政策リスク
                        "project_delay": -0.5,     # 案件遅延
                        "regulatory_uncertainty": -0.5 # 規制不確実性
                    }
                }
            }
    
    def analyze_survival_gate(self, confirmed_items: List[Dict[str, Any]]) -> Tuple[str, Dict[str, Any]]:
        """
        Gate 1: 生存性（流動性・コベナンツ・利益）
        反証：最低条件をクリアしているか
        """
        details = {}
        penalties = 0
        
        # 現金残高チェック
        cash_balance = 0
        for item in confirmed_items:
            if "cash" in item["kpi"].lower() and "balance" in item["kpi"].lower():
                cash_balance = item["value"]
                break
        
        threshold = self.config.get("lec_failsafe", {}).get("survival_thresholds", {}).get("cash_min", 100000000)
        if cash_balance < threshold:
            penalties += 1
            details["cash_insufficient"] = True
        
        # 運転資本チェック
        working_capital = 0
        for item in confirmed_items:
            if "working_capital" in item["kpi"].lower():
                working_capital = item["value"]
                break
        
        if working_capital <= 0:
            penalties += 1
            details["working_capital_negative"] = True
        
        # EBITDAチェック
        ebitda = 0
        for item in confirmed_items:
            if "ebitda" in item["kpi"].lower():
                ebitda = item["value"]
                break
        
        if ebitda <= 0:
            penalties += 1
            details["ebitda_negative"] = True
        
        # RCF利用可能額チェック
        rcf_available = 0
        for item in confirmed_items:
            if "rcf" in item["kpi"].lower() or "credit_facility" in item["kpi"].lower():
                rcf_available = item["value"]
                break
        
        threshold = self.config.get("lec_failsafe", {}).get("survival_thresholds", {}).get("rcf_min", 50000000)
        if rcf_available < threshold:
            penalties += 0.5  # 軽微な減点
            details["rcf_limited"] = True
        
        # コベナンツ順守チェック
        covenant_compliance = any("covenant" in item["kpi"].lower() or "compliance" in item["kpi"].lower() 
                                for item in confirmed_items)
        if not covenant_compliance:
            penalties += 0.5
            details["covenant_risk"] = True
        
        # 判定
        if penalties >= 2:
            gate_result = "FAIL"
        else:
            gate_result = "PASS"
        
        details["penalties"] = penalties
        return gate_result, details
    
    def analyze_moat_gate(self, confirmed_items: List[Dict[str, Any]], 
                         facts_content: str) -> Tuple[str, Dict[str, Any]]:
        """
        Gate 2: 優位性（価格転嫁力/構造）
        反証：価格圧力・競合脅威による減点
        """
        details = {}
        penalties = 0
        
        # ASP下落チェック
        asp_decline = False
        for item in confirmed_items:
            if "asp" in item["kpi"].lower() and item["value"] < 0:
                asp_decline = True
                break
        
        if asp_decline:
            penalty = self.config.get("lec_failsafe", {}).get("moat_penalties", {}).get("asp_decline", -1.0)
            penalties += abs(penalty)
            details["asp_decline"] = True
        
        # 価格圧力の言及チェック
        price_pressure = "competitive" in facts_content.lower() or "pricing" in facts_content.lower()
        if price_pressure:
            penalty = self.config.get("lec_failsafe", {}).get("moat_penalties", {}).get("price_pressure", -0.5)
            penalties += abs(penalty)
            details["price_pressure"] = True
        
        # 競合脅威チェック
        competitive_threat = "competitor" in facts_content.lower() or "threat" in facts_content.lower()
        if competitive_threat:
            penalty = self.config.get("lec_failsafe", {}).get("moat_penalties", {}).get("competitive_threat", -0.5)
            penalties += abs(penalty)
            details["competitive_threat"] = True
        
        # 判定
        if penalties >= 1.5:
            gate_result = "FAIL"
        elif penalties >= 0.5:
            gate_result = "WARN"  # 警告レベル
        else:
            gate_result = "PASS"
        
        details["penalties"] = penalties
        return gate_result, details
    
    def analyze_demand_gate(self, confirmed_items: List[Dict[str, Any]], 
                           facts_content: str) -> Tuple[str, Dict[str, Any]]:
        """
        Gate 3: 需要粘着性（政策/顧客遅延）
        反証：政策リスク・規制不確実性による減点
        """
        details = {}
        penalties = 0
        
        # 政策リスクチェック
        policy_risk = ("uncertainty" in facts_content.lower() or 
                      "policy" in facts_content.lower() or
                      "domestic_content" in facts_content.lower())
        
        if policy_risk:
            penalty = self.config.get("lec_failsafe", {}).get("demand_penalties", {}).get("policy_risk", -1.0)
            penalties += abs(penalty)
            details["policy_risk"] = True
        
        # 案件遅延リスクチェック
        project_delay = "delay" in facts_content.lower() or "postpone" in facts_content.lower()
        if project_delay:
            penalty = self.config.get("lec_failsafe", {}).get("demand_penalties", {}).get("project_delay", -0.5)
            penalties += abs(penalty)
            details["project_delay"] = True
        
        # 規制不確実性チェック
        regulatory_uncertainty = ("guidance" in facts_content.lower() and "modify" in facts_content.lower()) or \
                               "foec" in facts_content.lower()
        if regulatory_uncertainty:
            penalty = self.config.get("lec_failsafe", {}).get("demand_penalties", {}).get("regulatory_uncertainty", -0.5)
            penalties += abs(penalty)
            details["regulatory_uncertainty"] = True
        
        # 判定
        if penalties >= 1.5:
            gate_result = "FAIL"
        elif penalties >= 0.5:
            gate_result = "WARN"
        else:
            gate_result = "PASS"
        
        details["penalties"] = penalties
        return gate_result, details
    
    def calculate_final_star(self, survival_result: str, moat_result: str, 
                           demand_result: str, mechanical_base: int) -> int:
        """
        最終★計算：min{機械式ベース, 3ゲート判定}（上振れ不可）
        """
        # ゲート結果をスコア化
        gate_scores = {
            "PASS": 3,
            "WARN": 2,
            "FAIL": 1
        }
        
        survival_score = gate_scores.get(survival_result, 1)
        moat_score = gate_scores.get(moat_result, 1)
        demand_score = gate_scores.get(demand_result, 1)
        
        # 重み付き平均（生存性重視）
        gate_star = int((0.5 * survival_score + 0.3 * moat_score + 0.2 * demand_score))
        
        # min{機械式ベース, 3ゲート判定}
        final_star = min(mechanical_base, gate_star)
        
        return final_star
    
    def evaluate(self, triage_file: str, facts_file: str, 
                mechanical_base_star: int = 5) -> LECFailSafeResult:
        """LEC Fail-safe分析の実行"""
        
        # ファイル読み込み
        with open(triage_file, 'r', encoding='utf-8') as f:
            triage_data = json.load(f)
        
        with open(facts_file, 'r', encoding='utf-8') as f:
            facts_content = f.read()
        
        confirmed_items = triage_data.get("CONFIRMED", [])
        
        # 3つのゲート分析（反証優先・減点のみ）
        survival_result, survival_details = self.analyze_survival_gate(confirmed_items)
        moat_result, moat_details = self.analyze_moat_gate(confirmed_items, facts_content)
        demand_result, demand_details = self.analyze_demand_gate(confirmed_items, facts_content)
        
        # 最終★計算
        final_star = self.calculate_final_star(survival_result, moat_result, 
                                             demand_result, mechanical_base_star)
        
        # 説明文生成
        explanation = self._generate_explanation(survival_result, moat_result, 
                                               demand_result, final_star)
        
        return LECFailSafeResult(
            survival_gate=survival_result,
            moat_gate=moat_result,
            demand_gate=demand_result,
            final_star=final_star,
            explanation=explanation,
            gate_details={
                "survival": survival_details,
                "moat": moat_details,
                "demand": demand_details
            }
        )

    def _generate_explanation(self, survival_result: str, moat_result: str, 
                            demand_result: str, final_star: int) -> str:
        """説明文生成"""
        parts = []
        
        parts.append(f"生存性:{survival_result}")
        parts.append(f"優位性:{moat_result}")
        parts.append(f"ニーズ:{demand_result}")
        parts.append(f"→★{final_star}")
        
        return " ".join(parts)

def process_lec_failsafe_analysis(triage_file: str, facts_file: str, 
                                mechanical_base_star: int = 5) -> Dict[str, Any]:
    """LEC Fail-safe分析処理の実行"""
    
    engine = LECFailSafeEngine()
    result = engine.evaluate(triage_file, facts_file, mechanical_base_star)
    
    return {
        "as_of": json.load(open(triage_file, 'r', encoding='utf-8'))["as_of"],
        "ticker": json.load(open(triage_file, 'r', encoding='utf-8')).get("ticker", ""),
        "lec_failsafe": {
            "survival_gate": result.survival_gate,
            "moat_gate": result.moat_gate,
            "demand_gate": result.demand_gate,
            "final_star": result.final_star,
            "mechanical_base": mechanical_base_star
        },
        "explanation": result.explanation,
        "gate_details": result.gate_details,
        "notes": {
            "lec.failsafe_rule": "反証優先・減点のみ・上振れ不可"
        }
    }

def main():
    if len(sys.argv) < 3:
        print("使用方法: python ahf_lec_analysis_failsafe_v072.py <triage.jsonのパス> <facts.mdのパス> [機械式ベース★]")
        sys.exit(1)
    
    triage_file = sys.argv[1]
    facts_file = sys.argv[2]
    mechanical_base_star = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    
    if not os.path.exists(triage_file):
        print(f"[ERROR] triage.jsonが見つかりません: {triage_file}")
        sys.exit(1)
    
    if not os.path.exists(facts_file):
        print(f"[ERROR] facts.mdが見つかりません: {facts_file}")
        sys.exit(1)
    
    try:
        results = process_lec_failsafe_analysis(triage_file, facts_file, mechanical_base_star)
        
        # 結果出力
        print("=== AHF LEC Fail-safe Analysis Results (v0.7.2β) ===")
        print(f"As of: {results['as_of']}")
        print(f"Ticker: {results['ticker']}")
        print()
        print("【3つの反証ゲート（減点のみ）】")
        print(f"1) 生存性: {results['lec_failsafe']['survival_gate']}")
        print(f"2) 優位性: {results['lec_failsafe']['moat_gate']}")
        print(f"3) ニーズ: {results['lec_failsafe']['demand_gate']}")
        print()
        print(f"機械式ベース: ★{results['lec_failsafe']['mechanical_base']}")
        print(f"最終★: {results['lec_failsafe']['final_star']} (上振れ不可)")
        print(f"説明: {results['explanation']}")
        
        # 結果をJSONファイルに保存
        output_file = triage_file.replace("triage.json", "lec_failsafe_analysis.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"[INFO] 結果を保存しました: {output_file}")
        
    except Exception as e:
        print(f"[ERROR] 処理エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
