#!/usr/bin/env python3
"""
AHF v0.8.1-r2 テストスイート
固定4軸評価システムのテスト

Purpose: 投資判断に直結する固定4軸で評価
MVP: ①②③④の名称と順序を絶対固定／T1 or T1*で確証（不足はn/a）／定型テーブル＋1行要約を即出力
"""

import json
import yaml
import sys
import os
import unittest
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union

# テスト対象モジュールのインポート
from ahf_v081_r2_integrated import AHFv081R2Integrated
from ahf_v081_r2_evaluator import AHFv081R2Evaluator
from ahf_v081_r2_workflow import AHFv081R2Workflow, WorkflowStage
from ahf_v081_r2_turbo_screen import AHFv081R2TurboScreen, TurboScreenCard
from ahf_v081_r2_anchor_lint import AHFv081R2AnchorLint
from ahf_v081_r2_math_guard import AHFv081R2MathGuard, GuardType
from ahf_v081_r2_s3_lint import AHFv081R2S3Lint

class TestAHFv081R2Integrated(unittest.TestCase):
    """AHF v0.8.1-r2 統合テスト"""
    
    def setUp(self):
        """テストセットアップ"""
        self.ticker = "TEST"
        self.integrated = AHFv081R2Integrated(self.ticker)
    
    def test_integrated_evaluation(self):
        """統合評価テスト"""
        result = self.integrated.run_integrated_evaluation()
        
        # 基本構造チェック
        self.assertIn("purpose", result)
        self.assertIn("mvp", result)
        self.assertIn("ticker", result)
        self.assertIn("evaluation_date", result)
        self.assertIn("mode", result)
        self.assertIn("action_log", result)
        
        # 4軸評価チェック
        self.assertIn("evaluation", result)
        evaluation = result["evaluation"]
        self.assertIn("lec", evaluation)
        self.assertIn("nes", evaluation)
        self.assertIn("current_valuation", evaluation)
        self.assertIn("future_valuation", evaluation)
        
        # 意思決定チェック
        self.assertIn("decision", result)
        decision = result["decision"]
        self.assertIn("final_di", decision)
        self.assertIn("action", decision)
        self.assertIn("size_percentage", decision)
        
        print("✓ 統合評価テスト通過")

class TestAHFv081R2Evaluator(unittest.TestCase):
    """AHF v0.8.1-r2 評価器テスト"""
    
    def setUp(self):
        """テストセットアップ"""
        self.ticker = "TEST"
        self.evaluator = AHFv081R2Evaluator(self.ticker)
    
    def test_4_axes_evaluation(self):
        """4軸評価テスト"""
        result = self.evaluator.evaluate_4_axes()
        
        # 基本構造チェック
        self.assertIn("ticker", result)
        self.assertIn("evaluation_date", result)
        self.assertIn("lec", result)
        self.assertIn("nes", result)
        self.assertIn("current_valuation", result)
        self.assertIn("future_valuation", result)
        
        # ①LECチェック
        lec = result["lec"]
        self.assertIn("score", lec)
        self.assertIn("star_score", lec)
        self.assertIn("confidence", lec)
        self.assertIn("inputs", lec)
        self.assertIn("evidence_level", lec)
        
        # ②NESチェック
        nes = result["nes"]
        self.assertIn("score", nes)
        self.assertIn("star_score", nes)
        self.assertIn("confidence", nes)
        self.assertIn("inputs", nes)
        self.assertIn("evidence_level", nes)
        
        # ③現バリュエーションチェック
        current_val = result["current_valuation"]
        self.assertIn("status", current_val)
        if current_val["status"] == "evaluated":
            self.assertIn("evs_actual_ttm", current_val)
            self.assertIn("evs_peer_median_ttm", current_val)
            self.assertIn("disc_pct", current_val)
            self.assertIn("color", current_val)
            self.assertIn("vmult", current_val)
        
        # ④将来EVバリュチェック
        future_val = result["future_valuation"]
        self.assertIn("status", future_val)
        if future_val["status"] == "evaluated":
            self.assertIn("evs_fair_12m", future_val)
            self.assertIn("fd_pct", future_val)
            self.assertIn("star_score", future_val)
            self.assertIn("confidence", future_val)
        
        print("✓ 4軸評価テスト通過")
    
    def test_lec_calculation(self):
        """LEC計算テスト"""
        lec = self.evaluator._evaluate_lec()
        
        # スコア範囲チェック
        self.assertIsInstance(lec["score"], (int, float))
        self.assertGreaterEqual(lec["score"], -1.0)
        self.assertLessEqual(lec["score"], 1.0)
        
        # 星スコア範囲チェック
        self.assertIn(lec["star_score"], [1, 2, 3, 4, 5])
        
        # 確信度範囲チェック
        self.assertGreaterEqual(lec["confidence"], 0.0)
        self.assertLessEqual(lec["confidence"], 1.0)
        
        print("✓ LEC計算テスト通過")
    
    def test_nes_calculation(self):
        """NES計算テスト"""
        nes = self.evaluator._evaluate_nes()
        
        # スコア範囲チェック
        self.assertIsInstance(nes["score"], (int, float))
        self.assertGreaterEqual(nes["score"], -10.0)
        self.assertLessEqual(nes["score"], 20.0)
        
        # 星スコア範囲チェック
        self.assertIn(nes["star_score"], [1, 2, 3, 4, 5])
        
        # 確信度範囲チェック
        self.assertGreaterEqual(nes["confidence"], 0.0)
        self.assertLessEqual(nes["confidence"], 1.0)
        
        print("✓ NES計算テスト通過")

class TestAHFv081R2Workflow(unittest.TestCase):
    """AHF v0.8.1-r2 ワークフローテスト"""
    
    def setUp(self):
        """テストセットアップ"""
        self.ticker = "TEST"
        self.workflow = AHFv081R2Workflow(self.ticker)
    
    def test_workflow_stages(self):
        """ワークフローステージテスト"""
        # Intake
        intake_result = self.workflow._run_intake()
        self.assertIn("stage", intake_result)
        self.assertEqual(intake_result["stage"], "intake")
        self.assertIn("t1_availability", intake_result)
        self.assertIn("t1star_availability", intake_result)
        
        # Stage-1
        stage1_result = self.workflow._run_stage1_fast_screen()
        self.assertIn("stage", stage1_result)
        self.assertEqual(stage1_result["stage"], "stage1_fast_screen")
        self.assertIn("t1_verbatim", stage1_result)
        self.assertIn("t1star_verbatim", stage1_result)
        
        # Stage-2
        stage2_result = self.workflow._run_stage2_mini_confirm()
        self.assertIn("stage", stage2_result)
        self.assertEqual(stage2_result["stage"], "stage2_mini_confirm")
        self.assertIn("alpha3_confirmation", stage2_result)
        self.assertIn("alpha5_confirmation", stage2_result)
        
        # Stage-3
        stage3_result = self.workflow._run_stage3_alpha_maximization()
        self.assertIn("stage", stage3_result)
        self.assertEqual(stage3_result["stage"], "stage3_alpha_maximization")
        self.assertIn("s3_cards", stage3_result)
        self.assertIn("s3_tests", stage3_result)
        
        # Decision
        decision_result = self.workflow._run_decision()
        self.assertIn("stage", decision_result)
        self.assertEqual(decision_result["stage"], "decision")
        self.assertIn("di_calculation", decision_result)
        self.assertIn("action_determination", decision_result)
        
        print("✓ ワークフローステージテスト通過")
    
    def test_di_calculation(self):
        """DI計算テスト"""
        # ステージ結果を設定
        self.workflow.stage_results = {
            "decision": {
                "di_calculation": {
                    "di": 0.45,
                    "s1": 0.6,
                    "s2": 0.8,
                    "vmult": 1.05
                }
            }
        }
        
        di_result = self.workflow._calculate_di()
        
        # DI計算チェック
        self.assertIn("di", di_result)
        self.assertIn("s1", di_result)
        self.assertIn("s2", di_result)
        self.assertIn("vmult", di_result)
        self.assertIn("formula", di_result)
        
        # 計算式チェック
        expected_di = (0.6 * 0.8 + 0.4 * 0.6) * 1.05
        self.assertAlmostEqual(di_result["di"], expected_di, places=3)
        
        print("✓ DI計算テスト通過")

class TestAHFv081R2TurboScreen(unittest.TestCase):
    """AHF v0.8.1-r2 Turbo Screenテスト"""
    
    def setUp(self):
        """テストセットアップ"""
        self.ticker = "TEST"
        self.turbo_screen = AHFv081R2TurboScreen(self.ticker)
    
    def test_turbo_screen_execution(self):
        """Turbo Screen実行テスト"""
        result = self.turbo_screen.run_turbo_screen()
        
        # 基本構造チェック
        self.assertIn("ticker", result)
        self.assertIn("timestamp", result)
        self.assertIn("status", result)
        self.assertIn("cards_processed", result)
        self.assertIn("cards_approved", result)
        self.assertIn("cards_rejected", result)
        self.assertIn("cards_expired", result)
        
        print("✓ Turbo Screen実行テスト通過")
    
    def test_turbo_screen_card_management(self):
        """Turbo Screenカード管理テスト"""
        # カード追加
        card = TurboScreenCard(
            id="TEST-001",
            hypothesis="テスト仮説",
            evidence_level="T1*",
            verbatim="テスト逐語",
            url="https://test.com",
            anchor="#:~:text=テスト",
            ttl_days=14,
            contradiction_flag=False,
            dual_anchor_status="PENDING_SEC",
            screen_score=0.75,
            confidence_boost=0.10,
            star_adjustment=2
        )
        
        self.turbo_screen.add_card(card)
        self.assertEqual(len(self.turbo_screen.cards), 1)
        
        # カード取得
        retrieved_card = self.turbo_screen.get_card("TEST-001")
        self.assertIsNotNone(retrieved_card)
        self.assertEqual(retrieved_card.id, "TEST-001")
        
        # カード削除
        self.turbo_screen.remove_card("TEST-001")
        self.assertEqual(len(self.turbo_screen.cards), 0)
        
        print("✓ Turbo Screenカード管理テスト通過")

class TestAHFv081R2AnchorLint(unittest.TestCase):
    """AHF v0.8.1-r2 AnchorLintテスト"""
    
    def setUp(self):
        """テストセットアップ"""
        self.anchor_lint = AHFv081R2AnchorLint()
    
    def test_anchor_lint_batch(self):
        """AnchorLintバッチテスト"""
        test_data = [
            {
                "id": "T1-001",
                "verbatim": "Free cash flow $150M for the quarter.",
                "url": "https://sec.gov/edgar/...",
                "anchor": "#:~:text=Free%20cash%20flow",
                "evidence_level": "T1"
            }
        ]
        
        result = self.anchor_lint.lint_batch(test_data)
        
        # 基本構造チェック
        self.assertIn("results", result)
        self.assertIn("summary", result)
        self.assertIn("timestamp", result)
        
        # サマリーチェック
        summary = result["summary"]
        self.assertIn("total_items", summary)
        self.assertIn("pass_count", summary)
        self.assertIn("fail_count", summary)
        self.assertIn("pass_rate", summary)
        
        print("✓ AnchorLintバッチテスト通過")
    
    def test_t1star_lint(self):
        """T1*Lintテスト"""
        test_data = [
            {
                "id": "T1STAR-001",
                "two_sources": True,
                "independent": True,
                "quote_len": 20,
                "url_has_text": True,
                "verbatim": "Revenue guidance raised to $2.5B",
                "url": "https://investor.company.com/...",
                "anchor": "#:~:text=Revenue%20guidance"
            }
        ]
        
        result = self.anchor_lint.lint_t1star_batch(test_data)
        
        # 基本構造チェック
        self.assertIn("results", result)
        self.assertIn("summary", result)
        self.assertIn("timestamp", result)
        
        print("✓ T1*Lintテスト通過")
    
    def test_price_lint(self):
        """価格Lintテスト"""
        test_data = [
            {
                "id": "PRICE-001",
                "ev_used": True,
                "ps_used": False,
                "same_day": True,
                "same_source": True,
                "evs_actual_ttm": 15.2,
                "evs_peer_median_ttm": 18.5,
                "date": "2024-01-15",
                "source": "internal_etl"
            }
        ]
        
        result = self.anchor_lint.lint_price_batch(test_data)
        
        # 基本構造チェック
        self.assertIn("results", result)
        self.assertIn("summary", result)
        self.assertIn("timestamp", result)
        
        print("✓ 価格Lintテスト通過")

class TestAHFv081R2MathGuard(unittest.TestCase):
    """AHF v0.8.1-r2 数理ガードテスト"""
    
    def setUp(self):
        """テストセットアップ"""
        self.math_guard_core = AHFv081R2MathGuard(GuardType.CORE)
        self.math_guard_screen = AHFv081R2MathGuard(GuardType.SCREEN)
    
    def test_math_guard_core(self):
        """数理ガード（Core）テスト"""
        test_data = [
            {
                "id": "MATH-001",
                "gm_actual": 0.75,
                "gm_expected": 0.73,
                "gp": 150000,
                "revenue": 200000,
                "gm": 0.75,
                "opex": 50000,
                "ot": 50.0
            }
        ]
        
        result = self.math_guard_core.check_batch(test_data)
        
        # 基本構造チェック
        self.assertIn("results", result)
        self.assertIn("summary", result)
        self.assertIn("guard_type", result)
        self.assertIn("timestamp", result)
        
        # ガードタイプチェック
        self.assertEqual(result["guard_type"], "core")
        
        print("✓ 数理ガード（Core）テスト通過")
    
    def test_math_guard_screen(self):
        """数理ガード（Screen）テスト"""
        test_data = [
            {
                "id": "MATH-002",
                "gm_actual": 0.75,
                "gm_expected": 0.73,
                "gp": 150000,
                "revenue": 200000,
                "gm": 0.75,
                "opex": 50000,
                "ot": 50.0
            }
        ]
        
        result = self.math_guard_screen.check_batch(test_data)
        
        # 基本構造チェック
        self.assertIn("results", result)
        self.assertIn("summary", result)
        self.assertIn("guard_type", result)
        self.assertIn("timestamp", result)
        
        # ガードタイプチェック
        self.assertEqual(result["guard_type"], "screen")
        
        print("✓ 数理ガード（Screen）テスト通過")

class TestAHFv081R2S3Lint(unittest.TestCase):
    """AHF v0.8.1-r2 S3-Lintテスト"""
    
    def setUp(self):
        """テストセットアップ"""
        self.s3_lint = AHFv081R2S3Lint()
    
    def test_s3_lint_batch(self):
        """S3-Lintバッチテスト"""
        test_data = [
            {
                "id": "S3-001",
                "t1_verbatim": "Guidance raised to $2.5B",
                "url_anchor": "https://sec.gov/...#:~:text=Guidance%20raised",
                "test_formula": "guidance_fy26_mid >= 2500",
                "ttl_days": 30,
                "reasoning": "ガイダンス上方修正は成長加速を示唆"
            }
        ]
        
        result = self.s3_lint.lint_batch(test_data)
        
        # 基本構造チェック
        self.assertIn("results", result)
        self.assertIn("summary", result)
        self.assertIn("timestamp", result)
        
        # サマリーチェック
        summary = result["summary"]
        self.assertIn("total_items", summary)
        self.assertIn("pass_count", summary)
        self.assertIn("fail_count", summary)
        self.assertIn("pass_rate", summary)
        
        print("✓ S3-Lintバッチテスト通過")
    
    def test_s3_min_spec(self):
        """S3-MinSpecテスト"""
        test_item = {
            "t1_verbatim": "Guidance raised to $2.5B",
            "url_anchor": "https://sec.gov/...#:~:text=Guidance%20raised",
            "test_formula": "guidance_fy26_mid >= 2500",
            "ttl_days": 30,
            "reasoning": "ガイダンス上方修正は成長加速を示唆"
        }
        
        result = self.s3_lint.check_s3_min_spec(test_item)
        self.assertTrue(result)
        
        print("✓ S3-MinSpecテスト通過")

def run_all_tests():
    """全テスト実行"""
    print("AHF v0.8.1-r2 テストスイート開始")
    print("=" * 50)
    
    # テストスイート作成
    test_suite = unittest.TestSuite()
    
    # テストケース追加
    test_classes = [
        TestAHFv081R2Integrated,
        TestAHFv081R2Evaluator,
        TestAHFv081R2Workflow,
        TestAHFv081R2TurboScreen,
        TestAHFv081R2AnchorLint,
        TestAHFv081R2MathGuard,
        TestAHFv081R2S3Lint
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # テスト実行
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    print("=" * 50)
    print(f"テスト実行結果: {result.testsRun}件")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}件")
    print(f"失敗: {len(result.failures)}件")
    print(f"エラー: {len(result.errors)}件")
    
    if result.failures:
        print("\n失敗したテスト:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nエラーが発生したテスト:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    return result.wasSuccessful()

def main():
    """メイン実行"""
    if len(sys.argv) < 2:
        print("Usage: python test_ahf_v081_r2.py <TICKER>")
        sys.exit(1)
    
    ticker = sys.argv[1]
    
    # 全テスト実行
    success = run_all_tests()
    
    if success:
        print("\n✓ 全テスト通過")
        sys.exit(0)
    else:
        print("\n✗ テスト失敗")
        sys.exit(1)

if __name__ == "__main__":
    main()
