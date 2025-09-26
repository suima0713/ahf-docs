#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
S3-MinSpec v1.0 - Stage-3投資判断直結システム
固定ルール｜最小実装
"""

import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

class S3MinSpec:
    """S3-MinSpec v1.0 実装"""
    
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
                   test_formula: str, ttl_days: int, impact_notes: str = "") -> Dict:
        """カード作成"""
        card = {
            "id": card_id,
            "hypothesis": hypothesis,
            "evidence": evidence,
            "test_formula": test_formula,
            "ttl_days": ttl_days,
            "impact_notes": impact_notes,
            "created_at": datetime.now().isoformat(),
            "status": "PENDING"
        }
        return card
    
    def validate_run_conditions(self, card: Dict) -> Tuple[bool, List[str]]:
        """RUN条件チェック"""
        errors = []
        
        # T1逐語 ≤25語 + #:~:text=
        evidence = card.get("evidence", "")
        if len(evidence) > 25:
            errors.append("L1: 逐語が25語を超過")
        
        if not ("#:~:text=" in evidence or "anchor_backup" in evidence):
            errors.append("L2: URLが#:~:text=付きでない")
        
        # テスト式が1行で四則のみ
        test_formula = card.get("test_formula", "")
        if not self._is_valid_formula(test_formula):
            errors.append("L3: テスト式が1行で四則のみでない")
        
        # TTLが7-90d
        ttl = card.get("ttl_days", 0)
        if not (7 <= ttl <= 90):
            errors.append("L4: TTLが7-90dの範囲外")
        
        # 推論段数≤1（"だから→"が一回まで）
        if self._count_inference_steps(evidence) > 1:
            errors.append("L5: 推論段数が1を超過")
        
        return len(errors) == 0, errors
    
    def _is_valid_formula(self, formula: str) -> bool:
        """四則演算のみの1行式かチェック"""
        if not formula or len(formula.split('\n')) > 1:
            return False
        
        # 許可される文字: 数字、演算子、比較演算子、括弧
        allowed_chars = r'[0-9+\-*/%≤≥=().\s]'
        if not re.match(f'^{allowed_chars}+$', formula):
            return False
        
        return True
    
    def _count_inference_steps(self, text: str) -> int:
        """推論段数をカウント（"だから→"の回数）"""
        return text.count("だから") + text.count("→")
    
    def apply_s3_lint(self, card: Dict) -> Tuple[bool, str]:
        """S3-Lint実行"""
        is_valid, errors = self.validate_run_conditions(card)
        
        if is_valid:
            return True, "Lint PASS"
        else:
            error_msg = "Lint FAIL: " + " / ".join(errors)
            return False, error_msg
    
    def calculate_nes(self, q_q_pct: float, guidance_revision_pct: float = 0, 
                     order_backlog_pct: float = 0, margin_term: int = 0) -> Tuple[float, int]:
        """NES計算"""
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
        
        return nes, stars
    
    def evaluate_card(self, card: Dict, test_result: bool) -> str:
        """カード評価"""
        if test_result:
            return "VALID"
        else:
            return "WEAK"
    
    def check_contra(self, card: Dict, existing_cards: List[Dict]) -> bool:
        """CONTRA判定（T1同士の明白な矛盾）"""
        # 簡易実装：同じKPIで逆の方向性がある場合
        evidence = card.get("evidence", "").lower()
        for existing in existing_cards:
            existing_evidence = existing.get("evidence", "").lower()
            if self._has_contradiction(evidence, existing_evidence):
                return True
        return False
    
    def _has_contradiction(self, evidence1: str, evidence2: str) -> bool:
        """矛盾チェック（簡易実装）"""
        # 増加/減少の対立
        increase_words = ["増加", "上昇", "改善", "成長"]
        decrease_words = ["減少", "下降", "悪化", "縮小"]
        
        has_increase1 = any(word in evidence1 for word in increase_words)
        has_decrease1 = any(word in evidence1 for word in decrease_words)
        has_increase2 = any(word in evidence2 for word in increase_words)
        has_decrease2 = any(word in evidence2 for word in decrease_words)
        
        return (has_increase1 and has_decrease2) or (has_decrease1 and has_increase2)
    
    def apply_soft_overlay(self, base_di: float, alpha: float) -> float:
        """SoftOverlay適用（±0.08上限）"""
        alpha = max(-0.08, min(0.08, alpha))
        return base_di + alpha
    
    def process_card(self, card: Dict) -> Dict:
        """カード処理フロー"""
        # S3-Lint実行
        lint_pass, lint_msg = self.apply_s3_lint(card)
        
        if not lint_pass:
            card["status"] = "LINT_FAIL"
            card["lint_message"] = lint_msg
            return card
        
        # CONTRA判定
        if self.check_contra(card, self.cards):
            card["status"] = "CONTRA"
            card["evaluation"] = "CONTRA"
            return card
        
        # RUN登録
        card["status"] = "RUN"
        card["lint_message"] = lint_msg
        self.cards.append(card)
        
        return card
    
    def get_nes_display(self, q_q_pct: float, guidance_revision_pct: float = 0, 
                       order_backlog_pct: float = 0, margin_term: int = 0) -> str:
        """NES表示用文字列"""
        nes, stars = self.calculate_nes(q_q_pct, guidance_revision_pct, order_backlog_pct, margin_term)
        
        return f"""
NES自動欄:
式: {self.nes_formula}
入力: q/q={q_q_pct:.2f}%, 改定%={guidance_revision_pct:.2f}%, 受注%={order_backlog_pct:.2f}%, Margin_term={margin_term}
結果: NES={nes:.2f} → ★{stars}
"""

def main():
    """テスト実行"""
    s3 = S3MinSpec()
    
    # テストカード作成
    test_card = s3.create_card(
        card_id="TEST001",
        hypothesis="Q3売上成長率が17%を超える",
        evidence="ガイダンス中点$121M、直前Q$103Mだから→q/q%=17.48% #:~:text=Revenue",
        test_formula="q_q_pct >= 17",
        ttl_days=30,
        impact_notes="①②③への影響(+1★), α_base(+0.05)"
    )
    
    # カード処理
    result = s3.process_card(test_card)
    print(f"カード処理結果: {result['status']}")
    print(f"Lint結果: {result.get('lint_message', 'N/A')}")
    
    # NES計算例
    nes_display = s3.get_nes_display(17.48, 0, 0, 0)
    print(nes_display)

if __name__ == "__main__":
    main()
