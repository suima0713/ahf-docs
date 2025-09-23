#!/usr/bin/env python3
"""
AHF Loss Controls Monitor - 契約品質監視システム
T1限定で契約損失・下方調整を自動検出
"""

import re
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class LossControlsResult:
    """契約品質監視結果"""
    period: str
    downward_adjustment: Dict
    contract_loss_provision: Dict
    subsequent_events: Dict
    verdict: str
    confidence: str

class LossControlsDetector:
    """契約品質監視検出器"""
    
    def __init__(self):
        self.keywords = {
            "downward_adjustment": [
                r"downward\s+adjustment",
                r"cumulative\s+catch-up",
                r"change\s+in\s+estimate",
                r"constraint",
                r"reduce\s+revenue"
            ],
            "contract_losses": [
                r"provision\s+for\s+contract\s+losses",
                r"loss\s+on\s+contracts",
                r"onerous",
                r"expected\s+costs\s+exceed\s+consideration"
            ],
            "subsequent_events": [
                r"Subsequent\s+Events",
                r"no\s+subsequent\s+events",
                r"material\s+subsequent"
            ]
        }
        
        self.false_positive_guards = [
            r"upward\s+adjustment",
            r"accounting\s+policy",
            r"general\s+risk\s+factors"
        ]
        
        self.thresholds = {
            "minor": 2000,
            "moderate": 5000,
            "major": float('inf')
        }
    
    def extract_amount(self, text: str) -> Optional[float]:
        """金額抽出（$000単位に正規化）"""
        # $6,421, $6,421k, $6,421 thousand等のパターン
        patterns = [
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:k|thousand|000)?',
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
            r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:k|thousand|000)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # 最大の金額を返す（複数ある場合）
                amounts = []
                for match in matches:
                    try:
                        amount = float(match.replace(',', ''))
                        amounts.append(amount)
                    except ValueError:
                        continue
                if amounts:
                    return max(amounts)
        return None
    
    def check_false_positive(self, text: str) -> bool:
        """誤検知ガード"""
        for guard in self.false_positive_guards:
            if re.search(guard, text, re.IGNORECASE):
                return True
        return False
    
    def extract_downward_adjustment(self, text: str) -> Dict:
        """下方調整抽出"""
        result = {
            "value_$k": 0,
            "pct_of_revenue": 0.0,
            "quote": None,
            "anchor": None,
            "status": "none"
        }
        
        for keyword in self.keywords["downward_adjustment"]:
            pattern = rf"({keyword}[^.]*?)(\$\d{{1,3}}(?:,\d{{3}})*(?:\.\d+)?\s*(?:k|thousand|000)?)"
            matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
            
            for match in matches:
                if self.check_false_positive(match.group(0)):
                    continue
                    
                amount = self.extract_amount(match.group(0))
                if amount:
                    result["value_$k"] = amount
                    result["quote"] = match.group(0).strip()
                    result["status"] = self._classify_severity(amount)
                    break
        
        return result
    
    def extract_contract_loss_provision(self, text: str) -> Dict:
        """契約損失引当抽出"""
        result = {
            "begin_$k": 0,
            "charges_$k": 0,
            "releases_$k": 0,
            "ending_$k": 0,
            "delta_$k": 0,
            "ending_pct_of_revenue": 0.0,
            "quote": None,
            "anchor": None,
            "status": "none"
        }
        
        for keyword in self.keywords["contract_losses"]:
            pattern = rf"({keyword}[^.]*?)(\$\d{{1,3}}(?:,\d{{3}})*(?:\.\d+)?\s*(?:k|thousand|000)?)"
            matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
            
            for match in matches:
                amount = self.extract_amount(match.group(0))
                if amount:
                    result["ending_$k"] = amount
                    result["charges_$k"] = amount  # 新規計上と仮定
                    result["delta_$k"] = amount
                    result["quote"] = match.group(0).strip()
                    result["status"] = self._classify_severity(amount)
                    break
        
        return result
    
    def extract_subsequent_events(self, text: str) -> Dict:
        """後発事象抽出"""
        result = {
            "blanket": None,
            "exceptions": [],
            "anchor": None
        }
        
        for keyword in self.keywords["subsequent_events"]:
            pattern = rf"({keyword}[^.]*?)(?:\.|$)"
            matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
            
            for match in matches:
                result["blanket"] = match.group(0).strip()
                break
        
        return result
    
    def _classify_severity(self, amount: float) -> str:
        """重要度分類"""
        if amount < self.thresholds["minor"]:
            return "minor"
        elif amount < self.thresholds["moderate"]:
            return "moderate"
        else:
            return "major"
    
    def determine_verdict(self, downward: Dict, provision: Dict) -> str:
        """判定ロジック"""
        downward_amount = downward.get("value_$k", 0)
        provision_amount = provision.get("ending_$k", 0)
        
        if downward_amount == 0 and provision_amount == 0:
            return "no_recurrence"
        elif downward_amount < 2000 and provision_amount < 2000:
            return "recurrence_minor"
        else:
            return "recurrence_material"
    
    def analyze_document(self, text: str, period: str) -> LossControlsResult:
        """文書分析実行"""
        downward = self.extract_downward_adjustment(text)
        provision = self.extract_contract_loss_provision(text)
        subsequent = self.extract_subsequent_events(text)
        
        verdict = self.determine_verdict(downward, provision)
        
        return LossControlsResult(
            period=period,
            downward_adjustment=downward,
            contract_loss_provision=provision,
            subsequent_events=subsequent,
            verdict=verdict,
            confidence="T1" if verdict != "no_recurrence" else "T1"
        )

def main():
    """メイン実行"""
    detector = LossControlsDetector()
    
    # Q2ベースライン検証
    q2_text = """
    During the three months ended June 30, 2025, the Company recorded a downward adjustment to revenue of $6,421 related to an individual contract.
    The Company recorded a provision for contract losses of $5,953 as of June 30, 2025.
    Management has evaluated subsequent events through August 7, 2025, the date these condensed consolidated financial statements were issued, and has determined that no subsequent events have occurred that require recognition or disclosure in the condensed consolidated financial statements.
    """
    
    result = detector.analyze_document(q2_text, "Q2 2025")
    
    print("=== AHF Loss Controls Monitor ===")
    print(f"Period: {result.period}")
    print(f"Verdict: {result.verdict}")
    print(f"Confidence: {result.confidence}")
    print(f"Downward Adjustment: ${result.downward_adjustment['value_$k']:,.0f}k ({result.downward_adjustment['status']})")
    print(f"Contract Loss Provision: ${result.contract_loss_provision['ending_$k']:,.0f}k ({result.contract_loss_provision['status']})")
    
    return result

if __name__ == "__main__":
    main()
