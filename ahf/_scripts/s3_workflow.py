#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
S3-Workflow - Stage-3即日運用フロー
カード作成→Lint→RUN登録の統合システム
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from s3_minspec import S3MinSpec
from s3_lint import S3Lint
from nes_auto import NESAuto

class S3Workflow:
    """S3即日運用フロー実装"""
    
    def __init__(self):
        self.minspec = S3MinSpec()
        self.lint = S3Lint()
        self.nes_auto = NESAuto()
        self.active_cards = []
        self.processed_cards = []
    
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
        """S3-Lint実行"""
        return self.lint.run_lint(card)
    
    def check_contra(self, card: Dict) -> bool:
        """CONTRA判定"""
        return self.minspec.check_contra(card, self.active_cards)
    
    def calculate_nes_for_card(self, card: Dict) -> Dict:
        """カード用NES計算"""
        inputs = card.get("nes_inputs", {})
        nes, stars, details = self.nes_auto.calculate_nes(
            inputs.get("q_q_pct", 0),
            inputs.get("guidance_revision_pct", 0),
            inputs.get("order_backlog_pct", 0),
            inputs.get("margin_change_bps", 0)
        )
        
        return {
            "nes": nes,
            "stars": stars,
            "details": details,
            "display": self.nes_auto.get_calculation_display(
                inputs.get("q_q_pct", 0),
                inputs.get("guidance_revision_pct", 0),
                inputs.get("order_backlog_pct", 0),
                inputs.get("margin_change_bps", 0)
            )
        }
    
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
        nes_result = self.calculate_nes_for_card(card)
        card["nes_result"] = nes_result
        
        # 4. RUN登録
        card["status"] = "RUN"
        card["evaluation"] = "PENDING"
        card["registered_at"] = datetime.now().isoformat()
        
        # 5. アクティブカードに追加
        self.active_cards.append(card)
        
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
        
        # 処理済みカードに移動
        self.active_cards.remove(card)
        self.processed_cards.append(card)
        
        return card
    
    def get_card_by_id(self, card_id: str) -> Optional[Dict]:
        """IDでカード取得"""
        for card in self.active_cards + self.processed_cards:
            if card["id"] == card_id:
                return card
        return None
    
    def apply_soft_overlay(self, base_di: float, alpha: float) -> float:
        """SoftOverlay適用"""
        return self.minspec.apply_soft_overlay(base_di, alpha)
    
    def get_workflow_status(self) -> Dict:
        """ワークフロー状況"""
        return {
            "active_cards": len(self.active_cards),
            "processed_cards": len(self.processed_cards),
            "total_cards": len(self.active_cards) + len(self.processed_cards),
            "active_card_ids": [card["id"] for card in self.active_cards],
            "processed_card_ids": [card["id"] for card in self.processed_cards]
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
    
    def export_cards(self, filepath: str) -> bool:
        """カードエクスポート"""
        try:
            export_data = {
                "exported_at": datetime.now().isoformat(),
                "active_cards": self.active_cards,
                "processed_cards": self.processed_cards,
                "workflow_status": self.get_workflow_status()
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"エクスポートエラー: {e}")
            return False
    
    def import_cards(self, filepath: str) -> bool:
        """カードインポート"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            self.active_cards = import_data.get("active_cards", [])
            self.processed_cards = import_data.get("processed_cards", [])
            
            return True
        except Exception as e:
            print(f"インポートエラー: {e}")
            return False

def main():
    """テスト実行"""
    workflow = S3Workflow()
    
    # テストカード作成
    test_card = workflow.create_card(
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
    result = workflow.process_card_workflow(test_card)
    print(f"カード処理結果: {result['status']}")
    print(f"評価: {result.get('evaluation', 'N/A')}")
    
    # NES結果表示
    if "nes_result" in result:
        nes_display = result["nes_result"]["display"]
        print(nes_display)
    
    # ワークフロー状況
    status = workflow.get_workflow_status()
    print(f"ワークフロー状況: {status}")
    
    # カード要約
    summary = workflow.get_card_summary("TEST001")
    print(summary)

if __name__ == "__main__":
    main()
