#!/usr/bin/env python3
"""
AHF v0.8.1-r2 ワークフロー
固定4軸評価のワークフロー実装

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

class WorkflowStage(Enum):
    """ワークフローステージ"""
    INTAKE = "intake"
    STAGE1_FAST_SCREEN = "stage1_fast_screen"
    STAGE2_MINI_CONFIRM = "stage2_mini_confirm"
    STAGE3_ALPHA_MAXIMIZATION = "stage3_alpha_maximization"
    DECISION = "decision"

class AHFv081R2Workflow:
    """AHF v0.8.1-r2 ワークフロー"""
    
    def __init__(self, ticker: str):
        self.ticker = ticker
        self.current_stage = WorkflowStage.INTAKE
        self.stage_results = {}
        
    def _run_intake(self) -> Dict[str, Any]:
        """Intake実行"""
        result = {
            "stage": "intake",
            "ticker": self.ticker,
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
            "t1_availability": self._check_t1_availability(),
            "t1star_availability": self._check_t1star_availability(),
            "data_sources": self._identify_data_sources(),
            "data_gap": {},
            "gap_reason": {}
        }
        
        # データギャップチェック
        if not result["t1_availability"]:
            result["data_gap"]["t1"] = True
            result["gap_reason"]["t1"] = "T1証拠不足"
        
        if not result["t1star_availability"]:
            result["data_gap"]["t1star"] = True
            result["gap_reason"]["t1star"] = "T1*証拠不足"
        
        self.stage_results["intake"] = result
        return result
    
    def _run_stage1_fast_screen(self) -> Dict[str, Any]:
        """Stage-1 Fast-Screen実行"""
        result = {
            "stage": "stage1_fast_screen",
            "ticker": self.ticker,
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
            "t1_verbatim": self._extract_t1_verbatim(),
            "t1star_verbatim": self._extract_t1star_verbatim(),
            "anchor_validation": self._validate_anchors(),
            "evidence_ladder": self._build_evidence_ladder(),
            "data_gap": {},
            "gap_reason": {}
        }
        
        # T1逐語≤25語＋#:~:text=検証
        for item in result["t1_verbatim"]:
            if len(item.get("verbatim", "")) > 25:
                result["data_gap"]["verbatim_length"] = True
                result["gap_reason"]["verbatim_length"] = "逐語が25語を超過"
            
            if not item.get("anchor", "").startswith("#:~:text="):
                result["data_gap"]["anchor_format"] = True
                result["gap_reason"]["anchor_format"] = "アンカー形式が不正"
        
        self.stage_results["stage1"] = result
        return result
    
    def _run_stage2_mini_confirm(self) -> Dict[str, Any]:
        """Stage-2 Mini-Confirm実行"""
        result = {
            "stage": "stage2_mini_confirm",
            "ticker": self.ticker,
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
            "alpha3_confirmation": self._confirm_alpha3(),
            "alpha5_confirmation": self._confirm_alpha5(),
            "t1_consistency": self._check_t1_consistency(),
            "t1star_consistency": self._check_t1star_consistency(),
            "data_gap": {},
            "gap_reason": {}
        }
        
        # α3/α5確認
        if not result["alpha3_confirmation"]:
            result["data_gap"]["alpha3"] = True
            result["gap_reason"]["alpha3"] = "α3確認失敗"
        
        if not result["alpha5_confirmation"]:
            result["data_gap"]["alpha5"] = True
            result["gap_reason"]["alpha5"] = "α5確認失敗"
        
        self.stage_results["stage2"] = result
        return result
    
    def _run_stage3_alpha_maximization(self) -> Dict[str, Any]:
        """Stage-3 Alpha-Maximization実行"""
        result = {
            "stage": "stage3_alpha_maximization",
            "ticker": self.ticker,
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
            "s3_cards": self._generate_s3_cards(),
            "s3_tests": self._run_s3_tests(),
            "alpha_adjustments": self._calculate_alpha_adjustments(),
            "data_gap": {},
            "gap_reason": {}
        }
        
        # S3-MinSpec検証
        for card in result["s3_cards"]:
            if len(card.get("verbatim", "")) > 25:
                result["data_gap"]["s3_verbatim_length"] = True
                result["gap_reason"]["s3_verbatim_length"] = "S3逐語が25語を超過"
            
            if not card.get("url_anchor", "").startswith("#:~:text="):
                result["data_gap"]["s3_anchor_format"] = True
                result["gap_reason"]["s3_anchor_format"] = "S3アンカー形式が不正"
        
        self.stage_results["stage3"] = result
        return result
    
    def _run_decision(self) -> Dict[str, Any]:
        """Decision実行"""
        result = {
            "stage": "decision",
            "ticker": self.ticker,
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
            "di_calculation": self._calculate_di(),
            "action_determination": self._determine_action(),
            "size_calculation": self._calculate_size(),
            "soft_overlay": self._calculate_soft_overlay(),
            "data_gap": {},
            "gap_reason": {}
        }
        
        # DI計算: DI = (0.6·s2 + 0.4·s1) · Vmult(③)
        if result["di_calculation"]["di"] == 0.0:
            result["data_gap"]["di_calculation"] = True
            result["gap_reason"]["di_calculation"] = "DI計算失敗"
        
        self.stage_results["decision"] = result
        return result
    
    def _check_t1_availability(self) -> bool:
        """T1可用性チェック"""
        # 実際の実装では、facts.mdやtriage.jsonから確認
        return True  # サンプル
    
    def _check_t1star_availability(self) -> bool:
        """T1*可用性チェック"""
        # 実際の実装では、triage.jsonから確認
        return False  # サンプル
    
    def _identify_data_sources(self) -> List[str]:
        """データソース特定"""
        sources = []
        
        # SEC EDGAR
        if self._check_sec_availability():
            sources.append("SEC_EDGAR")
        
        # Company IR
        if self._check_ir_availability():
            sources.append("Company_IR")
        
        # Internal ETL
        if self._check_internal_etl_availability():
            sources.append("Internal_ETL")
        
        # Polygon
        if self._check_polygon_availability():
            sources.append("Polygon")
        
        return sources
    
    def _check_sec_availability(self) -> bool:
        """SEC可用性チェック"""
        return True  # サンプル
    
    def _check_ir_availability(self) -> bool:
        """IR可用性チェック"""
        return True  # サンプル
    
    def _check_internal_etl_availability(self) -> bool:
        """Internal ETL可用性チェック"""
        return True  # サンプル
    
    def _check_polygon_availability(self) -> bool:
        """Polygon可用性チェック"""
        return False  # サンプル
    
    def _extract_t1_verbatim(self) -> List[Dict[str, Any]]:
        """T1逐語抽出"""
        # 実際の実装では、facts.mdから抽出
        return [
            {
                "id": "T1-001",
                "verbatim": "Free cash flow $150M for the quarter.",
                "url": "https://sec.gov/edgar/...",
                "anchor": "#:~:text=Free%20cash%20flow",
                "source_domain": "sec.gov",
                "ttl_days": 14
            }
        ]
    
    def _extract_t1star_verbatim(self) -> List[Dict[str, Any]]:
        """T1*逐語抽出"""
        # 実際の実装では、triage.jsonから抽出
        return [
            {
                "id": "T1STAR-001",
                "verbatim": "Revenue guidance raised to $2.5B",
                "url": "https://investor.company.com/...",
                "anchor": "#:~:text=Revenue%20guidance",
                "source_domain": "investor.company.com",
                "ttl_days": 14,
                "two_sources": True,
                "independent": True
            }
        ]
    
    def _validate_anchors(self) -> Dict[str, Any]:
        """アンカー検証"""
        return {
            "t1_anchors_valid": True,
            "t1star_anchors_valid": True,
            "anchor_lint_pass": True,
            "anchor_lint_t1star_pass": True
        }
    
    def _build_evidence_ladder(self) -> Dict[str, Any]:
        """証拠階層構築"""
        return {
            "T1": {
                "count": 1,
                "sources": ["SEC_EDGAR"],
                "domains": ["sec.gov"]
            },
            "T1*": {
                "count": 0,
                "sources": [],
                "domains": []
            },
            "T2": {
                "count": 0,
                "sources": [],
                "domains": []
            }
        }
    
    def _confirm_alpha3(self) -> bool:
        """α3確認"""
        # 実際の実装では、T1データからα3計算
        return True  # サンプル
    
    def _confirm_alpha5(self) -> bool:
        """α5確認"""
        # 実際の実装では、T1データからα5計算
        return True  # サンプル
    
    def _check_t1_consistency(self) -> bool:
        """T1一貫性チェック"""
        return True  # サンプル
    
    def _check_t1star_consistency(self) -> bool:
        """T1*一貫性チェック"""
        return True  # サンプル
    
    def _generate_s3_cards(self) -> List[Dict[str, Any]]:
        """S3カード生成"""
        return [
            {
                "id": "S3-001",
                "hypothesis": "ガイダンス上方修正は成長加速を示唆",
                "t1_verbatim": "Guidance raised to $2.5B",
                "url_anchor": "https://sec.gov/...#:~:text=Guidance%20raised",
                "test_formula": "guidance_fy26_mid >= 2500",
                "ttl_days": 30,
                "reasoning": "ガイダンス上方修正は成長加速を示唆"
            }
        ]
    
    def _run_s3_tests(self) -> List[Dict[str, Any]]:
        """S3テスト実行"""
        return [
            {
                "id": "S3-001",
                "result": True,
                "value": 2500,
                "threshold": 2500,
                "ttl_days": 30,
                "reflection": "★+1"
            }
        ]
    
    def _calculate_alpha_adjustments(self) -> Dict[str, Any]:
        """α調整計算"""
        return {
            "lec_adjustment": 0.0,
            "nes_adjustment": 1.0,  # ★+1
            "current_val_adjustment": 0.0,
            "future_val_adjustment": 0.0,
            "total_adjustment": 1.0
        }
    
    def _calculate_di(self) -> Dict[str, Any]:
        """DI計算"""
        # 実際の実装では、4軸評価結果から計算
        s1 = 0.6  # ①LEC正規化スコア
        s2 = 0.8  # ②NES正規化スコア
        vmult = 1.05  # ③Vmult
        
        di = (0.6 * s2 + 0.4 * s1) * vmult
        
        return {
            "di": di,
            "s1": s1,
            "s2": s2,
            "vmult": vmult,
            "formula": "DI = (0.6·s2 + 0.4·s1) · Vmult(③)"
        }
    
    def _determine_action(self) -> Dict[str, Any]:
        """アクション決定"""
        di = self.stage_results.get("decision", {}).get("di_calculation", {}).get("di", 0.0)
        
        if di >= 0.55:
            action = "GO"
        elif di >= 0.32:
            action = "WATCH"
        else:
            action = "NO-GO"
        
        return {
            "action": action,
            "threshold": 0.55 if action == "GO" else 0.32,
            "reasoning": f"DI={di:.2f} → {action}"
        }
    
    def _calculate_size(self) -> Dict[str, Any]:
        """サイズ計算"""
        di = self.stage_results.get("decision", {}).get("di_calculation", {}).get("di", 0.0)
        size_percentage = 1.2 * di
        
        if size_percentage >= 2.0:
            size_category = "High"
        elif size_percentage >= 1.0:
            size_category = "Med"
        else:
            size_category = "Low"
        
        return {
            "size_percentage": size_percentage,
            "size_category": size_category,
            "formula": "Size% ≈ 1.2% × DI"
        }
    
    def _calculate_soft_overlay(self) -> Dict[str, Any]:
        """SoftOverlay計算"""
        # T1*由来の加点は±0.03以内
        t1star_bonus = 0.0
        
        # ④将来EVバリュの補助（必要時±0.05のみ）
        future_val_overlay = 0.0
        
        total_overlay = t1star_bonus + future_val_overlay
        
        return {
            "t1star_bonus": t1star_bonus,
            "future_val_overlay": future_val_overlay,
            "total_overlay": total_overlay,
            "t1star_limit": 0.03,
            "future_val_limit": 0.05
        }
    
    def get_stage_result(self, stage: WorkflowStage) -> Optional[Dict[str, Any]]:
        """ステージ結果取得"""
        return self.stage_results.get(stage.value)
    
    def get_all_results(self) -> Dict[str, Any]:
        """全結果取得"""
        return self.stage_results

def main():
    """メイン実行"""
    if len(sys.argv) < 2:
        print("Usage: python ahf_v081_r2_workflow.py <TICKER>")
        sys.exit(1)
    
    ticker = sys.argv[1]
    
    # ワークフロー実行
    workflow = AHFv081R2Workflow(ticker)
    
    # 全ステージ実行
    workflow._run_intake()
    workflow._run_stage1_fast_screen()
    workflow._run_stage2_mini_confirm()
    workflow._run_stage3_alpha_maximization()
    workflow._run_decision()
    
    # 結果出力
    result = workflow.get_all_results()
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
