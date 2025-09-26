#!/usr/bin/env python3
"""
AHF v0.8.0 テストスクリプト
固定3軸（①長期EV確度、②長期EV勾配、③バリュエーション＋認知ギャップ）のテスト実装

Purpose: 投資判断に直結する固定3軸で評価する
MVP: ①②③の名称と順序を固定／T1で確証（不足は n/a）／定型テーブル＋1行要約を即時出力
"""

import json
import unittest
import sys
import os
from datetime import datetime
from typing import Dict, List, Any

# テスト対象モジュールのインポート
from ahf_v080_workflow import AHFv080Workflow, WorkflowStage
from ahf_v080_evaluator import AHFv080Evaluator
from ahf_v080_turbo_screen import AHFv080TurboScreen
from ahf_v080_anchor_lint import AHFv080AnchorLint
from ahf_v080_math_guard import AHFv080MathGuard, GuardType
from ahf_v080_s3_lint import AHFv080S3Lint
from ahf_v080_integrated import AHFv080Integrated

class TestAHFv080Workflow(unittest.TestCase):
    """AHF v0.8.0 ワークフローテスト"""
    
    def setUp(self):
        self.workflow = AHFv080Workflow("TEST")
    
    def test_workflow_initialization(self):
        """ワークフロー初期化テスト"""
        self.assertEqual(self.workflow.ticker, "TEST")
        self.assertEqual(self.workflow.current_stage, WorkflowStage.INTAKE)
    
    def test_intake_stage(self):
        """Intakeステージテスト"""
        result = self.workflow._run_intake()
        self.assertIn("intake", result)
        self.assertEqual(result["intake"]["ticker"], "TEST")
    
    def test_stage1_fast_screen(self):
        """Stage-1 Fast-Screenテスト"""
        result = self.workflow._run_stage1_fast_screen()
        self.assertIn("stage1", result)
        self.assertIn("axes", result["stage1"])
        self.assertIn("LEC", result["stage1"]["axes"])
        self.assertIn("NES", result["stage1"]["axes"])
        self.assertIn("VRG", result["stage1"]["axes"])

class TestAHFv080Evaluator(unittest.TestCase):
    """AHF v0.8.0 評価器テスト"""
    
    def setUp(self):
        self.evaluator = AHFv080Evaluator("TEST")
    
    def test_evaluator_initialization(self):
        """評価器初期化テスト"""
        self.assertEqual(self.evaluator.ticker, "TEST")
    
    def test_lec_evaluation(self):
        """①長期EV確度評価テスト"""
        result = self.evaluator._evaluate_lec()
        self.assertIn("axis", result)
        self.assertIn("score", result)
        self.assertIn("star_rating", result)
        self.assertEqual(result["axis"], "①長期EV確度（LEC）")
    
    def test_nes_evaluation(self):
        """②長期EV勾配評価テスト"""
        result = self.evaluator._evaluate_nes()
        self.assertIn("axis", result)
        self.assertIn("score", result)
        self.assertIn("star_rating", result)
        self.assertEqual(result["axis"], "②長期EV勾配（NES）")
    
    def test_vrg_evaluation(self):
        """③バリュエーション＋認知ギャップ評価テスト"""
        result = self.evaluator._evaluate_vrg()
        self.assertIn("axis", result)
        self.assertIn("step1", result)
        self.assertIn("step2", result)
        self.assertEqual(result["axis"], "③バリュエーション＋認知ギャップ（VRG）")

class TestAHFv080TurboScreen(unittest.TestCase):
    """AHF v0.8.0 Turbo Screenテスト"""
    
    def setUp(self):
        self.turbo_screen = AHFv080TurboScreen("TEST")
    
    def test_turbo_screen_initialization(self):
        """Turbo Screen初期化テスト"""
        self.assertEqual(self.turbo_screen.ticker, "TEST")
        self.assertEqual(self.turbo_screen.core_threshold, 70)
        self.assertEqual(self.turbo_screen.edge_threshold, 60)
    
    def test_edge_items_collection(self):
        """Edge項目収集テスト"""
        lec_edges = self.turbo_screen._collect_lec_edges()
        self.assertIsInstance(lec_edges, list)
        self.assertGreater(len(lec_edges), 0)
        
        nes_edges = self.turbo_screen._collect_nes_edges()
        self.assertIsInstance(nes_edges, list)
        self.assertGreater(len(nes_edges), 0)
        
        vrg_edges = self.turbo_screen._collect_vrg_edges()
        self.assertIsInstance(vrg_edges, list)
        self.assertGreater(len(vrg_edges), 0)

class TestAHFv080AnchorLint(unittest.TestCase):
    """AHF v0.8.0 AnchorLintテスト"""
    
    def setUp(self):
        self.anchor_lint = AHFv080AnchorLint()
    
    def test_anchor_lint_initialization(self):
        """AnchorLint初期化テスト"""
        self.assertEqual(self.anchor_lint.max_verbatim_length, 25)
    
    def test_text_anchor_detection(self):
        """#:~:text=アンカー検出テスト"""
        self.assertTrue(self.anchor_lint._is_text_anchor("#:~:text=Free%20cash%20flow"))
        self.assertFalse(self.anchor_lint._is_text_anchor("invalid_anchor"))
    
    def test_pdf_backup_detection(self):
        """PDF anchor_backup検出テスト"""
        self.assertTrue(self.anchor_lint._is_pdf_backup("anchor_backup{pageno:5,quote:test,hash:abc123}"))
        self.assertFalse(self.anchor_lint._is_pdf_backup("invalid_backup"))
    
    def test_verbatim_length_check(self):
        """逐語長チェックテスト"""
        short_verbatim = "Free cash flow $150M"
        long_verbatim = "This is a very long verbatim that exceeds the maximum length of 25 characters"
        
        result_short = self.anchor_lint.lint_anchor(short_verbatim, "https://sec.gov/...", "#:~:text=Free%20cash%20flow")
        result_long = self.anchor_lint.lint_anchor(long_verbatim, "https://sec.gov/...", "#:~:text=Free%20cash%20flow")
        
        self.assertTrue(result_short.l1_verbatim_25w)
        self.assertFalse(result_long.l1_verbatim_25w)

class TestAHFv080MathGuard(unittest.TestCase):
    """AHF v0.8.0 数理ガードテスト"""
    
    def setUp(self):
        self.core_guard = AHFv080MathGuard(GuardType.CORE)
        self.turbo_guard = AHFv080MathGuard(GuardType.TURBO)
    
    def test_math_guard_initialization(self):
        """数理ガード初期化テスト"""
        self.assertEqual(self.core_guard.guard_type, GuardType.CORE)
        self.assertEqual(self.turbo_guard.guard_type, GuardType.TURBO)
        self.assertEqual(self.core_guard.gm_deviation_threshold, 0.2)
        self.assertEqual(self.turbo_guard.gm_deviation_threshold, 0.5)
    
    def test_gm_deviation_calculation(self):
        """GM乖離計算テスト"""
        data = {"gm_actual": 0.75, "gm_expected": 0.73}
        deviation = self.core_guard._calculate_gm_deviation(data)
        self.assertEqual(deviation, 0.02)
    
    def test_residual_gp_calculation(self):
        """残差GP計算テスト"""
        data = {"gp": 150000, "revenue": 200000, "gm": 0.75, "opex": 50000}
        residual_gp = self.core_guard._calculate_residual_gp(data)
        self.assertEqual(residual_gp, 50000)  # 150000 - (200000 * 0.75 - 50000)
    
    def test_ot_range_check(self):
        """OT範囲チェックテスト"""
        data_valid = {"ot": 50.0}
        data_invalid = {"ot": 40.0}
        
        self.assertTrue(self.core_guard._check_ot_range(data_valid))
        self.assertFalse(self.core_guard._check_ot_range(data_invalid))

class TestAHFv080S3Lint(unittest.TestCase):
    """AHF v0.8.0 S3-Lintテスト"""
    
    def setUp(self):
        self.s3_lint = AHFv080S3Lint()
    
    def test_s3_lint_initialization(self):
        """S3-Lint初期化テスト"""
        self.assertEqual(self.s3_lint.max_verbatim_length, 25)
        self.assertEqual(self.s3_lint.min_ttl_days, 7)
        self.assertEqual(self.s3_lint.max_ttl_days, 90)
    
    def test_single_formula_detection(self):
        """四則1行検出テスト"""
        self.assertTrue(self.s3_lint._is_single_formula("guidance_fy26_mid >= 2500"))
        self.assertTrue(self.s3_lint._is_single_formula("revenue * 0.15 + margin"))
        self.assertFalse(self.s3_lint._is_single_formula("line1\nline2"))
        self.assertFalse(self.s3_lint._is_single_formula(""))
    
    def test_single_step_reasoning_detection(self):
        """推論1段検出テスト"""
        self.assertTrue(self.s3_lint._is_single_step_reasoning("ガイダンス上方修正は成長加速を示唆"))
        self.assertFalse(self.s3_lint._is_single_step_reasoning("まず、ガイダンスを確認し、次に成長率を計算する"))
        self.assertFalse(self.s3_lint._is_single_step_reasoning(""))

class TestAHFv080Integrated(unittest.TestCase):
    """AHF v0.8.0 統合テスト"""
    
    def setUp(self):
        self.integrated = AHFv080Integrated("TEST")
    
    def test_integrated_initialization(self):
        """統合システム初期化テスト"""
        self.assertEqual(self.integrated.ticker, "TEST")
        self.assertIsNotNone(self.integrated.config)
        self.assertIn("purpose", self.integrated.config)
        self.assertIn("mvp", self.integrated.config)
    
    def test_size_category_determination(self):
        """サイズカテゴリ決定テスト"""
        self.assertEqual(self.integrated._determine_size_category(2.5), "High")
        self.assertEqual(self.integrated._determine_size_category(1.5), "Med")
        self.assertEqual(self.integrated._determine_size_category(0.5), "Low")
    
    def test_confidence_calculation(self):
        """確信度計算テスト"""
        result = {
            "validation": {
                "anchor_lint": {"summary": {"pass_rate": 0.9}},
                "math_guard": {"summary": {"pass_rate": 0.8}},
                "s3_lint": {"summary": {"pass_rate": 0.7}}
            }
        }
        confidence = self.integrated._calculate_confidence(result)
        self.assertGreater(confidence, 0.5)

def run_all_tests():
    """全テスト実行"""
    # テストスイート作成
    test_suite = unittest.TestSuite()
    
    # 各テストクラスを追加
    test_classes = [
        TestAHFv080Workflow,
        TestAHFv080Evaluator,
        TestAHFv080TurboScreen,
        TestAHFv080AnchorLint,
        TestAHFv080MathGuard,
        TestAHFv080S3Lint,
        TestAHFv080Integrated
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # テスト実行
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()

def main():
    """メイン実行"""
    print("AHF v0.8.0 テスト実行開始")
    print("=" * 50)
    
    success = run_all_tests()
    
    print("=" * 50)
    if success:
        print("✅ 全テスト通過")
        sys.exit(0)
    else:
        print("❌ テスト失敗")
        sys.exit(1)

if __name__ == "__main__":
    main()

