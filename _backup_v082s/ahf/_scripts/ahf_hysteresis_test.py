#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AHFヒステリシステスト
プロパティテスト：ヒステリシスで±0.3x／±1ppの揺れではV区分が変わらないことを検証
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from ahf_v_overlay_v2 import VOverlayEngine

class HysteresisTester:
    """ヒステリシステスト"""
    
    def __init__(self):
        self.engine = VOverlayEngine()
    
    def calculate_raw_bucket(self, ev_sales: float, ro40: float) -> str:
        """生区分の計算（V-Overlayエンジンと同じロジック）"""
        # V-Overlayエンジンの合成スコア計算を使用
        v_score, _, _ = self.engine.calculate_v_score(ev_sales, ro40)
        return self.engine.determine_category(v_score)
    
    def test_hysteresis_property(self, base_ev_sales: float, base_ro40: float, 
                                previous_category: str, test_cases: list) -> dict:
        """ヒステリシスプロパティのテスト"""
        results = {
            "base_values": {"ev_sales": base_ev_sales, "ro40": base_ro40},
            "previous_category": previous_category,
            "tests": [],
            "summary": {"passed": 0, "failed": 0, "total": 0}
        }
        
        for test_case in test_cases:
            ev_sales = base_ev_sales + test_case["ev_delta"]
            ro40 = base_ro40 + test_case["ro40_delta"]
            
            # Step1: raw区分と前回区分を計算
            raw_bucket = self.calculate_raw_bucket(ev_sales, ro40)
            prev_bucket = self.calculate_raw_bucket(base_ev_sales, base_ro40)
            
            # ヒステリシス有りでの評価
            result_with_hyst = self.engine.evaluate(
                ev_sales, ro40, 
                previous_category, base_ev_sales, base_ro40
            )
            
            # Step2&3: 期待値の計算
            if raw_bucket == prev_bucket:
                # Step2: raw == prev → 期待＝変更なし
                expected_no_change = True
            else:
                # Step3: raw != prev → アップグレード判定
                upgrading = ((prev_bucket == "Amber" and raw_bucket == "Green") or
                           (prev_bucket == "Red" and raw_bucket in ["Amber", "Green"]))
                
                if upgrading:
                    # アップグレード: |ΔEV| < 0.6 AND |ΔRo40| < 2.4 → 期待＝変更なし
                    expected_no_change = (abs(test_case["ev_delta"]) < 0.6 and 
                                        abs(test_case["ro40_delta"]) < 2.4)
                else:
                    # ダウングレード: |ΔEV| < 0.5 AND |ΔRo40| < 2.0 → 期待＝変更なし
                    expected_no_change = (abs(test_case["ev_delta"]) < 0.5 and 
                                        abs(test_case["ro40_delta"]) < 2.0)
            
            actual_no_change = (result_with_hyst.category == previous_category)
            
            test_result = {
                "ev_delta": test_case["ev_delta"],
                "ro40_delta": test_case["ro40_delta"],
                "raw_bucket": raw_bucket,
                "prev_bucket": prev_bucket,
                "expected_no_change": expected_no_change,
                "actual_no_change": actual_no_change,
                "result_with_hyst": result_with_hyst.category,
                "hysteresis_applied": result_with_hyst.hysteresis_applied,
                "passed": expected_no_change == actual_no_change
            }
            
            results["tests"].append(test_result)
            if test_result["passed"]:
                results["summary"]["passed"] += 1
            else:
                results["summary"]["failed"] += 1
            results["summary"]["total"] += 1
        
        return results
    
    def run_comprehensive_test(self):
        """包括的ヒステリシステスト"""
        print("=== AHFヒステリシスプロパティテスト ===")
        
        # テストケース1: Green境界でのテスト
        print("\n【テストケース1: Green境界】")
        base_ev_sales, base_ro40 = 9.5, 42.0
        previous_category = "Green"
        
        test_cases = [
            {"ev_delta": 0.2, "ro40_delta": 0.5},  # 両方範囲内 → 変更なし期待
            {"ev_delta": 0.4, "ro40_delta": 0.8},  # 両方範囲内 → 変更なし期待
            {"ev_delta": -0.3, "ro40_delta": -1.0}, # 両方範囲内 → 変更なし期待
            {"ev_delta": -0.4, "ro40_delta": -1.2}, # 両方範囲内 → 変更なし期待
            {"ev_delta": 0.1, "ro40_delta": 0.2},  # 両方範囲内 → 変更なし期待
            {"ev_delta": 0.6, "ro40_delta": 0.8},  # EV範囲外 → 変更あり期待
            {"ev_delta": 0.2, "ro40_delta": 2.5},  # Ro40範囲外 → 変更あり期待
        ]
        
        result1 = self.test_hysteresis_property(
            base_ev_sales, base_ro40, previous_category, test_cases
        )
        
        self.print_test_results("Green境界", result1)
        
        # テストケース2: Amber境界でのテスト
        print("\n【テストケース2: Amber境界】")
        base_ev_sales, base_ro40 = 12.0, 38.0
        previous_category = "Amber"
        
        test_cases = [
            {"ev_delta": 0.25, "ro40_delta": 0.8},  # 両方範囲内 → 変更なし期待
            {"ev_delta": 0.6, "ro40_delta": 1.5},   # 両方範囲内 → 変更なし期待
            {"ev_delta": -0.3, "ro40_delta": -1.0}, # 両方範囲内 → 変更なし期待
            {"ev_delta": -0.5, "ro40_delta": -2.0}, # 両方範囲内 → 変更なし期待
            {"ev_delta": 0.7, "ro40_delta": 0.8},   # EV範囲外 → 変更あり期待
            {"ev_delta": 0.2, "ro40_delta": 2.5},   # Ro40範囲外 → 変更あり期待
        ]
        
        result2 = self.test_hysteresis_property(
            base_ev_sales, base_ro40, previous_category, test_cases
        )
        
        self.print_test_results("Amber境界", result2)
        
        # テストケース3: Red境界でのテスト
        print("\n【テストケース3: Red境界】")
        base_ev_sales, base_ro40 = 15.0, 33.0
        previous_category = "Red"
        
        test_cases = [
            {"ev_delta": 0.2, "ro40_delta": 0.7},  # 両方範囲内 → 変更なし期待
            {"ev_delta": 0.4, "ro40_delta": 1.2},  # 両方範囲内 → 変更なし期待
            {"ev_delta": -0.3, "ro40_delta": -1.0}, # 両方範囲内 → 変更なし期待
            {"ev_delta": -0.6, "ro40_delta": -2.5}, # 両方範囲内 → 変更なし期待
            {"ev_delta": 0.7, "ro40_delta": 0.8},   # EV範囲外 → 変更あり期待
            {"ev_delta": 0.2, "ro40_delta": 2.5},   # Ro40範囲外 → 変更あり期待
        ]
        
        result3 = self.test_hysteresis_property(
            base_ev_sales, base_ro40, previous_category, test_cases
        )
        
        self.print_test_results("Red境界", result3)
        
        # 総合結果
        total_passed = result1["summary"]["passed"] + result2["summary"]["passed"] + result3["summary"]["passed"]
        total_failed = result1["summary"]["failed"] + result2["summary"]["failed"] + result3["summary"]["failed"]
        total_tests = total_passed + total_failed
        
        print(f"\n=== 総合結果 ===")
        print(f"総テスト数: {total_tests}")
        print(f"成功: {total_passed}")
        print(f"失敗: {total_failed}")
        print(f"成功率: {total_passed/total_tests*100:.1f}%")
        
        if total_failed == 0:
            print("✅ すべてのヒステリシスプロパティテストが成功しました")
        else:
            print("❌ 一部のヒステリシスプロパティテストが失敗しました")
    
    def print_test_results(self, test_name: str, results: dict):
        """テスト結果の表示"""
        print(f"ベース値: EV/Sales={results['base_values']['ev_sales']}, Ro40={results['base_values']['ro40']}")
        print(f"前回区分: {results['previous_category']}")
        
        for i, test in enumerate(results["tests"], 1):
            status = "✅" if test["passed"] else "❌"
            print(f"  テスト{i}: EV+{test['ev_delta']:.1f}, Ro40+{test['ro40_delta']:.1f} → "
                  f"{test['result_with_hyst']} (期待: {'変更なし' if test['expected_no_change'] else '変更あり'}) {status}")
        
        print(f"結果: {results['summary']['passed']}/{results['summary']['total']} 成功")

def main():
    """メイン実行"""
    tester = HysteresisTester()
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main()
