#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
S3-Integrated - Stage-3統合システム
S3-MinSpec + S3-Lint + NES-Auto + S3-Workflow の統合実装
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

class S3Integrated:
    """S3統合システム実装"""
    
    def __init__(self):
        self.cards = []
        self.nes_formula = "NES = 0.5·(次Q q/q%) + 0.3·(ガイド改定%) + 0.2·(受注/Backlog増勢%) + Margin_term"
        self.nes_thresholds = {
            (8, float('inf')): 5,    # NES ≥ +8 → ★5
            (5, 8): 4,               # +5–8 → ★4
            (2, 5): 3,               # +2–5 → ★3
            (0, 2): 2,               # 0–2 → ★2
            (float('-inf'), 0): 1    # <0 → ★1
        }
    
    def create_card(self, card_id: str, hypothesis: str, evidence: str, 
                   test_formula: str, ttl_days: int, impact_notes: str = "",
                   q_q_pct: float = 0, guidance_revision_pct: float = 0,
                   order_backlog_pct: float = 0, margin_change_bps: float = 0) -> Dict:
        """カード作成"""
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
                "margin_change_bps": margin_change_bps
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
    
    def calculate_nes(self, q_q_pct: float, guidance_revision_pct: float = 0, 
                     order_backlog_pct: float = 0, margin_change_bps: float = 0) -> Tuple[float, int, Dict]:
        """NES計算と★換算"""
        # Margin_term計算
        if margin_change_bps >= 50:
            margin_term = 1  # 改善≥+50bps=+1
        elif margin_change_bps <= -50:
            margin_term = -1  # 悪化≤−50bps=−1
        else:
            margin_term = 0  # ±50bps=0
        
        nes = (0.5 * q_q_pct + 
               0.3 * guidance_revision_pct + 
               0.2 * order_backlog_pct + 
               margin_term)
        
        # ★換算
        stars = 1
        for (min_val, max_val), star in self.nes_thresholds.items():
            if min_val <= nes < max_val:
                stars = star
                break
        
        calculation_details = {
            "q_q_component": 0.5 * q_q_pct,
            "guidance_component": 0.3 * guidance_revision_pct,
            "order_component": 0.2 * order_backlog_pct,
            "margin_term": margin_term,
            "nes": nes,
            "stars": stars
        }
        
        return nes, stars, calculation_details
    
    def process_card_workflow(self, card: Dict) -> Dict:
        """カード処理フロー"""
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
        
        # 3. NES計算
        inputs = card.get("nes_inputs", {})
        nes, stars, details = self.calculate_nes(
            inputs.get("q_q_pct", 0),
            inputs.get("guidance_revision_pct", 0),
            inputs.get("order_backlog_pct", 0),
            inputs.get("margin_change_bps", 0)
        )
        card["nes_result"] = {"nes": nes, "stars": stars, "details": details}
        
        # 4. RUN登録
        card["status"] = "RUN"
        card["evaluation"] = "PENDING"
        card["registered_at"] = datetime.now().isoformat()
        
        # 5. カードリストに追加
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
        """カード要約"""
        card = self.get_card_by_id(card_id)
        if not card:
            return f"カード {card_id} が見つかりません"
        
        summary = f"""
カード要約: {card_id}
仮説: {card.get('hypothesis', 'N/A')}
証拠: {card.get('evidence', 'N/A')}
テスト式: {card.get('test_formula', 'N/A')}
TTL: {card.get('ttl_days', 'N/A')}日
ステータス: {card.get('status', 'N/A')}
評価: {card.get('evaluation', 'N/A')}
"""
        
        if "nes_result" in card:
            nes = card["nes_result"]["nes"]
            stars = card["nes_result"]["stars"]
            summary += f"NES: {nes:.2f} → ★{stars}\n"
        
        if "lint_result" in card:
            lint_msg = card["lint_result"]["message"]
            summary += f"Lint: {lint_msg}\n"
        
        return summary
    
    def get_nes_display(self, q_q_pct: float, guidance_revision_pct: float = 0, 
                       order_backlog_pct: float = 0, margin_change_bps: float = 0) -> str:
        """NES表示用文字列"""
        nes, stars, details = self.calculate_nes(q_q_pct, guidance_revision_pct, order_backlog_pct, margin_change_bps)
        
        return f"""
NES自動欄:
式: {self.nes_formula}
入力: q/q={q_q_pct:.2f}%, 改定%={guidance_revision_pct:.2f}%, 受注%={order_backlog_pct:.2f}%, Margin_change={margin_change_bps:.1f}bps
計算: NES = 0.5×{q_q_pct:.2f} + 0.3×{guidance_revision_pct:.2f} + 0.2×{order_backlog_pct:.2f} + {details['margin_term']} = {nes:.2f}
結果: NES={nes:.2f} → ★{stars}
"""

def main():
    """テスト実行"""
    s3 = S3Integrated()
    
    # テストカード作成（PASS例）
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
        margin_change_bps=0
    )
    
    # カード処理フロー実行
    result = s3.process_card_workflow(test_card)
    print(f"カード処理結果: {result['status']}")
    print(f"評価: {result.get('evaluation', 'N/A')}")
    
    # NES結果表示
    if "nes_result" in result:
        nes_display = s3.get_nes_display(17.48, 0, 0, 0)
        print(nes_display)
    
    # ワークフロー状況
    status = s3.get_workflow_status()
    print(f"ワークフロー状況: {status}")
    
    # カード要約
    summary = s3.get_card_summary("TEST001")
    print(summary)

if __name__ == "__main__":
    main()
