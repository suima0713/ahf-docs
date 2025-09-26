#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
S3-Enhanced - Stage-3拡張システム
NES+Health_term + ③バリュエーション＋認知ギャップの統合実装
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from nes_auto import NESAuto
from valuation_system import ValuationSystem

class S3Enhanced:
    """S3拡張システム実装"""
    
    def __init__(self):
        self.nes_auto = NESAuto()
        self.valuation = ValuationSystem()
        self.cards = []
    
    def create_card(self, card_id: str, hypothesis: str, evidence: str, 
                   test_formula: str, ttl_days: int, impact_notes: str = "",
                   q_q_pct: float = 0, guidance_revision_pct: float = 0,
                   order_backlog_pct: float = 0, margin_change_bps: float = 0,
                   ro40: float = 0, ev_s_actual: float = 0, ev_s_peer_median: float = 0,
                   ev_s_fair: float = 0) -> Dict:
        """カード作成（拡張版）"""
        card = {
            "id": card_id,
            "hypothesis": hypothesis,
            "evidence": evidence,
            "test_formula": test_formula,
            "ttl_days": ttl_days,
            "impact_notes": impact_notes,
            "created_at": datetime.now().isoformat(),
            "status": "CREATED",
            "nes_inputs": {
                "q_q_pct": q_q_pct,
                "guidance_revision_pct": guidance_revision_pct,
                "order_backlog_pct": order_backlog_pct,
                "margin_change_bps": margin_change_bps,
                "ro40": ro40
            },
            "valuation_inputs": {
                "ev_s_actual": ev_s_actual,
                "ev_s_peer_median": ev_s_peer_median,
                "ev_s_fair": ev_s_fair
            }
        }
        return card
    
    def run_s3_lint(self, card: Dict) -> Tuple[bool, str]:
        """S3-Lint実行（最小5チェック）"""
        errors = []
        
        # L1: 逐語が≤25語か
        evidence = card.get("evidence", "")
        word_count = len(evidence.split())
        if word_count > 25:
            errors.append("L1(逐語{0}語>25語)".format(word_count))
        
        # L2: URLが#:~:text=付きか
        if not ("#:~:text=" in evidence or "anchor_backup" in evidence):
            errors.append("L2(anchor missing #:)")
        
        # L3: テスト式が1行で四則のみか
        test_formula = card.get("test_formula", "")
        if not test_formula:
            errors.append("L3(test formula absent)")
        elif len(test_formula.split('\n')) > 1:
            errors.append("L3(multi-line formula)")
        else:
            allowed_chars = r'[0-9+\-*/%≤≥=().\s]'
            if not re.match(f'^{allowed_chars}+$', test_formula):
                errors.append("L3(invalid formula chars)")
        
        # L4: TTLが7-90dか
        ttl_days = card.get("ttl_days", 0)
        if not (7 <= ttl_days <= 90):
            errors.append("L4(TTL{0}d not in 7-90d)".format(ttl_days))
        
        # L5: 推論段数≤1
        inference_count = evidence.count("だから") + evidence.count("→")
        if inference_count > 1:
            errors.append("L5(inference steps {0}>1)".format(inference_count))
        
        if errors:
            return False, "Lint FAIL: " + " / ".join(errors)
        else:
            return True, "Lint PASS"
    
    def check_contra(self, card: Dict) -> bool:
        """CONTRA判定（T1同士の明白な矛盾）"""
        evidence = card.get("evidence", "").lower()
        for existing in self.cards:
            existing_evidence = existing.get("evidence", "").lower()
            if self._has_contradiction(evidence, existing_evidence):
                return True
        return False
    
    def _has_contradiction(self, evidence1: str, evidence2: str) -> bool:
        """矛盾チェック"""
        increase_words = ["増加", "上昇", "改善", "成長"]
        decrease_words = ["減少", "下降", "悪化", "縮小"]
        
        has_increase1 = any(word in evidence1 for word in increase_words)
        has_decrease1 = any(word in evidence1 for word in decrease_words)
        has_increase2 = any(word in evidence2 for word in increase_words)
        has_decrease2 = any(word in evidence2 for word in decrease_words)
        
        return (has_increase1 and has_decrease2) or (has_decrease1 and has_increase2)
    
    def calculate_nes_enhanced(self, card: Dict) -> Dict:
        """拡張NES計算"""
        inputs = card.get("nes_inputs", {})
        nes, stars, details = self.nes_auto.calculate_nes(
            inputs.get("q_q_pct", 0),
            inputs.get("guidance_revision_pct", 0),
            inputs.get("order_backlog_pct", 0),
            inputs.get("margin_change_bps", 0),
            inputs.get("ro40", 0)
        )
        
        return {
            "nes": nes,
            "stars": stars,
            "details": details,
            "display": self.nes_auto.get_calculation_display(
                inputs.get("q_q_pct", 0),
                inputs.get("guidance_revision_pct", 0),
                inputs.get("order_backlog_pct", 0),
                inputs.get("margin_change_bps", 0),
                inputs.get("ro40", 0)
            )
        }
    
    def calculate_valuation_enhanced(self, card: Dict) -> Dict:
        """拡張バリュエーション計算"""
        inputs = card.get("valuation_inputs", {})
        result = self.valuation.evaluate_valuation(
            inputs.get("ev_s_actual", 0),
            inputs.get("ev_s_peer_median", 0),
            inputs.get("ev_s_fair", 0)
        )
        
        return {
            "result": result,
            "display": self.valuation.get_valuation_display(
                inputs.get("ev_s_actual", 0),
                inputs.get("ev_s_peer_median", 0),
                inputs.get("ev_s_fair", 0)
            )
        }
    
    def process_card_workflow(self, card: Dict) -> Dict:
        """拡張カード処理フロー"""
        # 1. S3-Lint実行
        lint_pass, lint_msg = self.run_s3_lint(card)
        card["lint_result"] = {"pass": lint_pass, "message": lint_msg}
        
        if not lint_pass:
            card["status"] = "LINT_FAIL"
            card["evaluation"] = "LINT_FAIL"
            return card
        
        # 2. CONTRA判定
        if self.check_contra(card):
            card["status"] = "CONTRA"
            card["evaluation"] = "CONTRA"
            return card
        
        # 3. 拡張NES計算
        nes_result = self.calculate_nes_enhanced(card)
        card["nes_result"] = nes_result
        
        # 4. 拡張バリュエーション計算
        valuation_result = self.calculate_valuation_enhanced(card)
        card["valuation_result"] = valuation_result
        
        # 5. RUN登録
        card["status"] = "RUN"
        card["evaluation"] = "PENDING"
        card["registered_at"] = datetime.now().isoformat()
        
        # 6. カードリストに追加
        self.cards.append(card)
        
        return card
    
    def evaluate_card(self, card_id: str, test_result: bool) -> Dict:
        """カード評価"""
        card = self.get_card_by_id(card_id)
        if not card:
            return {"error": "カードが見つかりません"}
        
        if test_result:
            card["evaluation"] = "VALID"
        else:
            card["evaluation"] = "WEAK"
        
        card["evaluated_at"] = datetime.now().isoformat()
        card["test_result"] = test_result
        
        return card
    
    def get_card_by_id(self, card_id: str) -> Optional[Dict]:
        """IDでカード取得"""
        for card in self.cards:
            if card["id"] == card_id:
                return card
        return None
    
    def get_workflow_status(self) -> Dict:
        """ワークフロー状況"""
        return {
            "total_cards": len(self.cards),
            "card_ids": [card["id"] for card in self.cards],
            "status_counts": {
                "CREATED": len([c for c in self.cards if c.get("status") == "CREATED"]),
                "RUN": len([c for c in self.cards if c.get("status") == "RUN"]),
                "LINT_FAIL": len([c for c in self.cards if c.get("status") == "LINT_FAIL"]),
                "CONTRA": len([c for c in self.cards if c.get("status") == "CONTRA"])
            }
        }
    
    def get_card_summary(self, card_id: str) -> str:
        """拡張カード要約"""
        card = self.get_card_by_id(card_id)
        if not card:
            return f"カード {card_id} が見つかりません"
        
        summary = f"""
拡張カード要約: {card_id}
仮説: {card.get('hypothesis', 'N/A')}
証拠: {card.get('evidence', 'N/A')}
テスト式: {card.get('test_formula', 'N/A')}
TTL: {card.get('ttl_days', 'N/A')}日
ステータス: {card.get('status', 'N/A')}
評価: {card.get('evaluation', 'N/A')}
"""
        
        # NES結果
        if "nes_result" in card:
            nes = card["nes_result"]["nes"]
            stars = card["nes_result"]["stars"]
            summary += f"NES: {nes:.2f} → ★{stars}\n"
        
        # バリュエーション結果
        if "valuation_result" in card:
            val_result = card["valuation_result"]["result"]
            summary += f"バリュエーション: {val_result['color']} (DI倍率: {val_result['di_multiplier']:.2f})\n"
            summary += f"認知ギャップ: {val_result['cognitive_gap_pct']:.1f}%\n"
        
        # Lint結果
        if "lint_result" in card:
            lint_msg = card["lint_result"]["message"]
            summary += f"Lint: {lint_msg}\n"
        
        return summary
    
    def get_enhanced_display(self, card: Dict) -> str:
        """拡張表示"""
        display = f"""
=== S3拡張システム結果 ===
カードID: {card.get('id', 'N/A')}
仮説: {card.get('hypothesis', 'N/A')}
"""
        
        # NES結果
        if "nes_result" in card:
            display += card["nes_result"]["display"]
        
        # バリュエーション結果
        if "valuation_result" in card:
            display += card["valuation_result"]["display"]
        
        return display

def main():
    """テスト実行"""
    s3 = S3Enhanced()
    
    # テストカード作成（拡張版）
    test_card = s3.create_card(
        card_id="TEST001",
        hypothesis="Q3売上成長率が17%を超える",
        evidence="ガイダンス中点$121M、直前Q$103Mだから→q/q%=17.48% #:~:text=Revenue",
        test_formula="q_q_pct >= 17",
        ttl_days=30,
        impact_notes="①②③への影響(+1★), α_base(+0.05)",
        q_q_pct=17.48,
        guidance_revision_pct=0,
        order_backlog_pct=0,
        margin_change_bps=0,
        ro40=45.0,  # Ro40≥40→+1
        ev_s_actual=5.0,
        ev_s_peer_median=5.0,
        ev_s_fair=5.0
    )
    
    # カード処理フロー実行
    result = s3.process_card_workflow(test_card)
    print(f"カード処理結果: {result['status']}")
    print(f"評価: {result.get('evaluation', 'N/A')}")
    
    # 拡張表示
    enhanced_display = s3.get_enhanced_display(result)
    print(enhanced_display)
    
    # ワークフロー状況
    status = s3.get_workflow_status()
    print(f"ワークフロー状況: {status}")
    
    # カード要約
    summary = s3.get_card_summary("TEST001")
    print(summary)

if __name__ == "__main__":
    main()
