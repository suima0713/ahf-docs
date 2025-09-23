#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AHF LEC Analysis v0.7.2β
①長期EV成長の確かさ（LEC）反証モード分析
"""

import json
import os
import sys
import yaml
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass

@dataclass
class LECResult:
    """LEC分析結果"""
    survival_score: float
    moat_score: float
    demand_score: float
    final_score: float
    star_1: int
    confidence: float
    explanation: str
    gate_results: Dict[str, Any]

class LECAnalysisEngine:
    """LEC分析エンジン"""
    
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
                "lec_analysis": {
                    "weights": {"survival": 0.4, "moat": 0.3, "demand": 0.3},
                    "thresholds": {
                        "survival_pass": 3.0,
                        "moat_pass": 3.0,
                        "demand_pass": 3.0
                    }
                }
            }
    
    def analyze_survival_gate(self, confirmed_items: List[Dict[str, Any]]) -> Tuple[float, Dict[str, Any]]:
        """
        Gate 1: 企業が生き続けられるか？（サバイバビリティ）
        """
        score = 0.0
        details = {}
        
        # 現金残高チェック
        cash_balance = 0
        for item in confirmed_items:
            if "cash" in item["kpi"].lower() and "balance" in item["kpi"].lower():
                cash_balance = item["value"]
                break
        
        if cash_balance > 300000000:  # $300M以上
            score += 2.0
            details["cash_strong"] = True
        elif cash_balance > 100000000:  # $100M以上
            score += 1.0
            details["cash_adequate"] = True
        else:
            details["cash_weak"] = True
        
        # 運転資本チェック
        working_capital = 0
        for item in confirmed_items:
            if "working_capital" in item["kpi"].lower():
                working_capital = item["value"]
                break
        
        if working_capital > 500000000:  # $500M以上
            score += 1.5
            details["working_capital_strong"] = True
        elif working_capital > 0:
            score += 1.0
            details["working_capital_positive"] = True
        else:
            details["working_capital_negative"] = True
        
        # RCF利用可能額チェック
        rcf_available = 0
        for item in confirmed_items:
            if "rcf" in item["kpi"].lower() or "credit_facility" in item["kpi"].lower():
                rcf_available = item["value"]
                break
        
        if rcf_available > 100000000:  # $100M以上
            score += 1.0
            details["rcf_available"] = True
        
        # EBITDAチェック
        ebitda = 0
        for item in confirmed_items:
            if "ebitda" in item["kpi"].lower():
                ebitda = item["value"]
                break
        
        if ebitda > 50000000:  # $50M以上
            score += 1.0
            details["ebitda_positive"] = True
        
        # コベナンツ順守チェック（簡略化）
        covenant_compliance = any("covenant" in item["kpi"].lower() or "compliance" in item["kpi"].lower() 
                                for item in confirmed_items)
        if covenant_compliance:
            score += 0.5
            details["covenant_compliance"] = True
        
        details["score"] = score
        return score, details
    
    def analyze_moat_gate(self, confirmed_items: List[Dict[str, Any]], 
                         facts_content: str) -> Tuple[float, Dict[str, Any]]:
        """
        Gate 2: 長期持続的な優位性はあるか？
        """
        score = 0.0
        details = {}
        
        # 製品差別化チェック
        product_differentiation = any("omnitrack" in facts_content.lower() or 
                                    "skylink" in facts_content.lower() or
                                    "orderbook" in facts_content.lower() 
                                    for _ in [facts_content])
        
        if product_differentiation:
            score += 2.0
            details["product_differentiation"] = True
        
        # 価格競争の影響チェック
        price_pressure = any("asp" in item["kpi"].lower() or "selling_price" in item["kpi"].lower() 
                           for item in confirmed_items)
        
        if price_pressure:
            # ASP下落があれば減点
            for item in confirmed_items:
                if "asp" in item["kpi"].lower() and item["value"] < 0:
                    score -= 1.0
                    details["asp_decline"] = True
                    break
        
        # 競合への言及チェック
        competitive_pressure = "competitor" in facts_content.lower() or "competitive" in facts_content.lower()
        if competitive_pressure:
            score -= 0.5
            details["competitive_pressure"] = True
        
        # 技術優位性チェック
        tech_advantage = any("technology" in item["kpi"].lower() or "innovation" in item["kpi"].lower() 
                           for item in confirmed_items)
        if tech_advantage:
            score += 1.0
            details["tech_advantage"] = True
        
        # 受注構成の高度化チェック
        order_sophistication = "35%" in facts_content or "orderbook" in facts_content.lower()
        if order_sophistication:
            score += 1.0
            details["order_sophistication"] = True
        
        details["score"] = score
        return score, details
    
    def analyze_demand_gate(self, confirmed_items: List[Dict[str, Any]], 
                           facts_content: str) -> Tuple[float, Dict[str, Any]]:
        """
        Gate 3: 長期持続的なニーズはあるか？（粘着性）
        """
        score = 0.0
        details = {}
        
        # 受注残チェック
        backlog = 0
        for item in confirmed_items:
            if "backlog" in item["kpi"].lower():
                backlog = item["value"]
                break
        
        if backlog > 1800000000:  # $1.8B以上
            score += 2.0
            details["backlog_strong"] = True
        elif backlog > 1000000000:  # $1.0B以上
            score += 1.5
            details["backlog_good"] = True
        else:
            details["backlog_weak"] = True
        
        # Book-to-Billチェック
        book_to_bill = 1.0  # デフォルト
        for item in confirmed_items:
            if "book_to_bill" in item["kpi"].lower() or "book_to_bill" in item["kpi"].lower():
                book_to_bill = item["value"]
                break
        
        if book_to_bill >= 1.0:
            score += 1.0
            details["book_to_bill_good"] = True
        else:
            score -= 0.5
            details["book_to_bill_weak"] = True
        
        # ボリューム成長チェック
        volume_growth = 0
        for item in confirmed_items:
            if "volume" in item["kpi"].lower() and "growth" in item["kpi"].lower():
                volume_growth = item["value"]
                break
        
        if volume_growth > 50:  # 50%以上
            score += 1.0
            details["volume_growth_strong"] = True
        elif volume_growth > 0:
            score += 0.5
            details["volume_growth_positive"] = True
        
        # 政策リスクチェック
        policy_risk = ("uncertainty" in facts_content.lower() or 
                      "delay" in facts_content.lower() or
                      "domestic_content" in facts_content.lower() or
                      "foec" in facts_content.lower())
        
        if policy_risk:
            score -= 1.0
            details["policy_risk"] = True
        
        # 規制リスクチェック
        regulatory_risk = ("guidance" in facts_content.lower() and "modify" in facts_content.lower())
        if regulatory_risk:
            score -= 0.5
            details["regulatory_risk"] = True
        
        details["score"] = score
        return score, details
    
    def calculate_confidence(self, gate_results: Dict[str, Any]) -> float:
        """確信度計算"""
        confidence = 70.0  # ベース70%
        
        # データ充足度による調整
        data_quality = 0
        if gate_results.get("survival", {}).get("score", 0) > 0:
            data_quality += 1
        if gate_results.get("moat", {}).get("score", 0) > 0:
            data_quality += 1
        if gate_results.get("demand", {}).get("score", 0) > 0:
            data_quality += 1
        
        if data_quality == 3:
            confidence += 15.0
        elif data_quality == 2:
            confidence += 5.0
        else:
            confidence -= 10.0
        
        # 50–95%でクリップ
        return max(50.0, min(95.0, confidence))
    
    def evaluate(self, triage_file: str, facts_file: str) -> LECResult:
        """LEC分析の実行"""
        
        # ファイル読み込み
        with open(triage_file, 'r', encoding='utf-8') as f:
            triage_data = json.load(f)
        
        with open(facts_file, 'r', encoding='utf-8') as f:
            facts_content = f.read()
        
        confirmed_items = triage_data.get("CONFIRMED", [])
        
        # 3つのゲート分析
        survival_score, survival_details = self.analyze_survival_gate(confirmed_items)
        moat_score, moat_details = self.analyze_moat_gate(confirmed_items, facts_content)
        demand_score, demand_details = self.analyze_demand_gate(confirmed_items, facts_content)
        
        # 重み付き総合スコア計算
        weights = self.config.get("lec_analysis", {}).get("weights", {"survival": 0.4, "moat": 0.3, "demand": 0.3})
        final_score = (weights["survival"] * survival_score + 
                      weights["moat"] * moat_score + 
                      weights["demand"] * demand_score)
        
        # 最終★計算（反証モード：切り下げ）
        if final_score >= 4.0:
            star_1 = 4
        elif final_score >= 3.0:
            star_1 = 3
        elif final_score >= 2.0:
            star_1 = 2
        else:
            star_1 = 1
        
        # 確信度計算
        gate_results = {
            "survival": survival_details,
            "moat": moat_details,
            "demand": demand_details
        }
        confidence = self.calculate_confidence(gate_results)
        
        # 説明文生成
        explanation = self._generate_explanation(survival_score, moat_score, demand_score, final_score, star_1)
        
        return LECResult(
            survival_score=survival_score,
            moat_score=moat_score,
            demand_score=demand_score,
            final_score=final_score,
            star_1=star_1,
            confidence=confidence,
            explanation=explanation,
            gate_results=gate_results
        )
    
    def _generate_explanation(self, survival_score: float, moat_score: float, 
                            demand_score: float, final_score: float, star_1: int) -> str:
        """説明文生成"""
        parts = []
        
        parts.append(f"生存性:{survival_score:.1f}")
        parts.append(f"優位性:{moat_score:.1f}")
        parts.append(f"ニーズ:{demand_score:.1f}")
        parts.append(f"総合:{final_score:.1f}")
        parts.append(f"→★{star_1}")
        
        return " ".join(parts)

def process_lec_analysis(triage_file: str, facts_file: str) -> Dict[str, Any]:
    """LEC分析処理の実行"""
    
    engine = LECAnalysisEngine()
    result = engine.evaluate(triage_file, facts_file)
    
    return {
        "as_of": json.load(open(triage_file, 'r', encoding='utf-8'))["as_of"],
        "ticker": json.load(open(triage_file, 'r', encoding='utf-8')).get("ticker", ""),
        "lec_analysis": {
            "survival_score": result.survival_score,
            "moat_score": result.moat_score,
            "demand_score": result.demand_score,
            "final_score": result.final_score,
            "star_1": result.star_1
        },
        "confidence": result.confidence,
        "explanation": result.explanation,
        "gate_results": result.gate_results,
        "notes": {
            "lec.analysis_rule": "3ゲート反証モード分析"
        }
    }

def main():
    if len(sys.argv) != 3:
        print("使用方法: python ahf_lec_analysis_v072.py <triage.jsonのパス> <facts.mdのパス>")
        sys.exit(1)
    
    triage_file = sys.argv[1]
    facts_file = sys.argv[2]
    
    if not os.path.exists(triage_file):
        print(f"[ERROR] triage.jsonが見つかりません: {triage_file}")
        sys.exit(1)
    
    if not os.path.exists(facts_file):
        print(f"[ERROR] facts.mdが見つかりません: {facts_file}")
        sys.exit(1)
    
    try:
        results = process_lec_analysis(triage_file, facts_file)
        
        # 結果出力
        print("=== AHF LEC Analysis Results (v0.7.2β) ===")
        print(f"As of: {results['as_of']}")
        print(f"Ticker: {results['ticker']}")
        print()
        print("【3つの反証ゲート】")
        print(f"1) 生存性: {results['lec_analysis']['survival_score']:.1f}")
        print(f"2) 優位性: {results['lec_analysis']['moat_score']:.1f}")
        print(f"3) ニーズ: {results['lec_analysis']['demand_score']:.1f}")
        print()
        print(f"総合スコア: {results['lec_analysis']['final_score']:.1f}")
        print(f"★1: {results['lec_analysis']['star_1']}")
        print(f"確信度: {results['confidence']:.0f}%")
        print(f"説明: {results['explanation']}")
        
        # 結果をJSONファイルに保存
        output_file = triage_file.replace("triage.json", "lec_analysis.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"[INFO] 結果を保存しました: {output_file}")
        
    except Exception as e:
        print(f"[ERROR] 処理エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()



