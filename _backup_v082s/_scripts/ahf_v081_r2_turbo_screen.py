#!/usr/bin/env python3
"""
AHF v0.8.1-r2 Turbo Screen
最小差分のTurbo Screen実装

Purpose: 投資判断に直結する固定4軸で評価
MVP: ①②③④の名称と順序を絶対固定／T1 or T1*で確証（不足はn/a）／定型テーブル＋1行要約を即出力
"""

import json
import yaml
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum

class TurboScreenStatus(Enum):
    """Turbo Screenステータス"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"

@dataclass
class TurboScreenCard:
    """Turbo Screenカード"""
    id: str
    hypothesis: str
    evidence_level: str  # T1, T1*, T2
    verbatim: str
    url: str
    anchor: str
    ttl_days: int
    contradiction_flag: bool
    dual_anchor_status: str
    screen_score: float
    confidence_boost: float
    star_adjustment: int

class AHFv081R2TurboScreen:
    """AHF v0.8.1-r2 Turbo Screen"""
    
    def __init__(self, ticker: str):
        self.ticker = ticker
        self.cards: List[TurboScreenCard] = []
        self.status = TurboScreenStatus.PENDING
        
    def run_turbo_screen(self) -> Dict[str, Any]:
        """Turbo Screen実行"""
        result = {
            "ticker": self.ticker,
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
            "cards_processed": 0,
            "cards_approved": 0,
            "cards_rejected": 0,
            "cards_expired": 0,
            "total_adjustments": {},
            "data_gap": {},
            "gap_reason": {}
        }
        
        try:
            # カード生成
            self._generate_turbo_cards()
            
            # カード処理
            for card in self.cards:
                result["cards_processed"] += 1
                
                # 受付閾値チェック
                if not self._check_acceptance_threshold(card):
                    result["cards_rejected"] += 1
                    continue
                
                # TTLチェック
                if self._check_ttl_expired(card):
                    result["cards_expired"] += 1
                    continue
                
                # 矛盾フラグチェック
                if card.contradiction_flag:
                    result["cards_rejected"] += 1
                    continue
                
                # カード承認
                result["cards_approved"] += 1
                
                # 調整計算
                adjustments = self._calculate_adjustments(card)
                result["total_adjustments"][card.id] = adjustments
            
            # 総合調整計算
            result["final_adjustments"] = self._calculate_final_adjustments(result["total_adjustments"])
            
        except Exception as e:
            result["error"] = str(e)
            result["data_gap"]["error"] = True
            result["gap_reason"]["error"] = f"Turbo Screen実行エラー: {str(e)}"
            
        return result
    
    def _generate_turbo_cards(self):
        """Turbo Screenカード生成"""
        # 実際の実装では、Edgeデータから生成
        self.cards = [
            TurboScreenCard(
                id="TURBO-001",
                hypothesis="ガイダンス上方修正は成長加速を示唆",
                evidence_level="T1*",
                verbatim="Guidance raised to $2.5B",
                url="https://investor.company.com/...",
                anchor="#:~:text=Guidance%20raised",
                ttl_days=14,
                contradiction_flag=False,
                dual_anchor_status="PENDING_SEC",
                screen_score=0.75,
                confidence_boost=0.10,
                star_adjustment=2
            ),
            TurboScreenCard(
                id="TURBO-002",
                hypothesis="新製品投入は収益性向上を示唆",
                evidence_level="T2",
                verbatim="New product launch expected Q2",
                url="https://news.company.com/...",
                anchor="#:~:text=New%20product",
                ttl_days=7,
                contradiction_flag=False,
                dual_anchor_status="APPROVED",
                screen_score=0.60,
                confidence_boost=0.05,
                star_adjustment=1
            )
        ]
    
    def _check_acceptance_threshold(self, card: TurboScreenCard) -> bool:
        """受付閾値チェック"""
        # Edge採用 P≥60（CoreはP≥70）
        if card.evidence_level == "T1*":
            threshold = 0.60
        else:
            threshold = 0.70
        
        return card.screen_score >= threshold
    
    def _check_ttl_expired(self, card: TurboScreenCard) -> bool:
        """TTL期限チェック"""
        # TTL≤14日
        return card.ttl_days > 14
    
    def _calculate_adjustments(self, card: TurboScreenCard) -> Dict[str, Any]:
        """調整計算"""
        adjustments = {
            "star_adjustment": 0,
            "confidence_boost": 0.0,
            "di_adjustment": 0.0,
            "alpha_adjustment": 0.0
        }
        
        # Screen★は±2★まで（Coreは±1★）
        if card.evidence_level == "T1*":
            max_star_adjustment = 2
        else:
            max_star_adjustment = 1
        
        adjustments["star_adjustment"] = min(card.star_adjustment, max_star_adjustment)
        
        # 確信度ブースト±10ppを1回（Coreは±5pp）
        if card.evidence_level == "T1*":
            max_confidence_boost = 0.10
        else:
            max_confidence_boost = 0.05
        
        adjustments["confidence_boost"] = min(card.confidence_boost, max_confidence_boost)
        
        # 数理ガード（緩和）
        adjustments["math_guard_relaxed"] = self._check_math_guard_relaxed(card)
        
        return adjustments
    
    def _check_math_guard_relaxed(self, card: TurboScreenCard) -> Dict[str, Any]:
        """数理ガード（緩和）チェック"""
        # GM乖離≤0.5pp、残差GP≤$12M、α5格子≤−$2.5M
        return {
            "gm_deviation_limit": 0.005,  # 0.5pp
            "residual_gp_limit": 12000000,  # $12M
            "alpha5_grid_limit": -2500000,  # -$2.5M
            "relaxed": True
        }
    
    def _calculate_final_adjustments(self, total_adjustments: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """最終調整計算"""
        final = {
            "total_star_adjustment": 0,
            "total_confidence_boost": 0.0,
            "total_di_adjustment": 0.0,
            "total_alpha_adjustment": 0.0,
            "math_guard_status": "relaxed"
        }
        
        for card_id, adjustments in total_adjustments.items():
            final["total_star_adjustment"] += adjustments.get("star_adjustment", 0)
            final["total_confidence_boost"] += adjustments.get("confidence_boost", 0.0)
            final["total_di_adjustment"] += adjustments.get("di_adjustment", 0.0)
            final["total_alpha_adjustment"] += adjustments.get("alpha_adjustment", 0.0)
        
        # 上限チェック
        final["total_star_adjustment"] = min(final["total_star_adjustment"], 2)
        final["total_confidence_boost"] = min(final["total_confidence_boost"], 0.10)
        final["total_di_adjustment"] = min(final["total_di_adjustment"], 0.08)
        final["total_alpha_adjustment"] = min(final["total_alpha_adjustment"], 0.05)
        
        return final
    
    def add_card(self, card: TurboScreenCard):
        """カード追加"""
        self.cards.append(card)
    
    def remove_card(self, card_id: str):
        """カード削除"""
        self.cards = [card for card in self.cards if card.id != card_id]
    
    def get_card(self, card_id: str) -> Optional[TurboScreenCard]:
        """カード取得"""
        for card in self.cards:
            if card.id == card_id:
                return card
        return None
    
    def get_approved_cards(self) -> List[TurboScreenCard]:
        """承認済みカード取得"""
        return [card for card in self.cards if not card.contradiction_flag and card.ttl_days <= 14]
    
    def get_rejected_cards(self) -> List[TurboScreenCard]:
        """拒否済みカード取得"""
        return [card for card in self.cards if card.contradiction_flag or card.ttl_days > 14]
    
    def get_expired_cards(self) -> List[TurboScreenCard]:
        """期限切れカード取得"""
        return [card for card in self.cards if card.ttl_days > 14]
    
    def get_cards_by_evidence_level(self, level: str) -> List[TurboScreenCard]:
        """証拠階層別カード取得"""
        return [card for card in self.cards if card.evidence_level == level]
    
    def get_cards_by_dual_anchor_status(self, status: str) -> List[TurboScreenCard]:
        """二重アンカーステータス別カード取得"""
        return [card for card in self.cards if card.dual_anchor_status == status]
    
    def get_summary(self) -> Dict[str, Any]:
        """サマリー取得"""
        return {
            "total_cards": len(self.cards),
            "approved_cards": len(self.get_approved_cards()),
            "rejected_cards": len(self.get_rejected_cards()),
            "expired_cards": len(self.get_expired_cards()),
            "t1_cards": len(self.get_cards_by_evidence_level("T1")),
            "t1star_cards": len(self.get_cards_by_evidence_level("T1*")),
            "t2_cards": len(self.get_cards_by_evidence_level("T2")),
            "pending_sec_cards": len(self.get_cards_by_dual_anchor_status("PENDING_SEC")),
            "approved_sec_cards": len(self.get_cards_by_dual_anchor_status("APPROVED"))
        }

def main():
    """メイン実行"""
    if len(sys.argv) < 2:
        print("Usage: python ahf_v081_r2_turbo_screen.py <TICKER>")
        sys.exit(1)
    
    ticker = sys.argv[1]
    
    # Turbo Screen実行
    turbo_screen = AHFv081R2TurboScreen(ticker)
    result = turbo_screen.run_turbo_screen()
    
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
