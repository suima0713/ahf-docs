#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
失敗ケースの詳細デバッグ
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from ahf_hysteresis_test import HysteresisTester

def debug_failing_case():
    """失敗ケースの詳細デバッグ"""
    tester = HysteresisTester()
    
    # 失敗ケースの詳細
    base_ev_sales, base_ro40 = 9.5, 42.0
    previous_category = "Green"
    ev_delta, ro40_delta = 0.6, 0.8
    
    ev_sales = base_ev_sales + ev_delta
    ro40 = base_ro40 + ro40_delta
    
    print(f"=== 失敗ケース詳細デバッグ ===")
    print(f"ベース値: EV/Sales={base_ev_sales}, Ro40={base_ro40}")
    print(f"変化量: EV+{ev_delta}, Ro40+{ro40_delta}")
    print(f"新値: EV/Sales={ev_sales}, Ro40={ro40}")
    print(f"前回区分: {previous_category}")
    print()
    
    # 生区分の計算
    raw_bucket = tester.calculate_raw_bucket(ev_sales, ro40)
    prev_bucket = tester.calculate_raw_bucket(base_ev_sales, base_ro40)
    
    print(f"生区分計算:")
    print(f"  前回区分: {prev_bucket}")
    print(f"  新区分: {raw_bucket}")
    print(f"  区分変更: {'Yes' if raw_bucket != prev_bucket else 'No'}")
    print()
    
    # ヒステリシス判定
    upgrading = ((prev_bucket == "Amber" and raw_bucket == "Green") or
                (prev_bucket == "Red" and raw_bucket in ["Amber", "Green"]))
    
    print(f"ヒステリシス判定:")
    print(f"  アップグレード: {upgrading}")
    
    if raw_bucket == prev_bucket:
        expected_no_change = True
        print(f"  期待値: 変更なし (raw == prev)")
    else:
        if upgrading:
            expected_no_change = (abs(ev_delta) < 0.6 and abs(ro40_delta) < 2.4)
            print(f"  期待値計算: |{ev_delta}| < 0.6 AND |{ro40_delta}| < 2.4")
            print(f"  → {abs(ev_delta) < 0.6} AND {abs(ro40_delta) < 2.4} = {expected_no_change}")
        else:
            expected_no_change = (abs(ev_delta) < 0.5 and abs(ro40_delta) < 2.0)
            print(f"  期待値計算: |{ev_delta}| < 0.5 AND |{ro40_delta}| < 2.0")
            print(f"  → {abs(ev_delta) < 0.5} AND {abs(ro40_delta) < 2.0} = {expected_no_change}")
    
    print(f"  期待: {'変更なし' if expected_no_change else '変更あり'}")
    print()
    
    # 実際の結果
    result = tester.engine.evaluate(ev_sales, ro40, previous_category, base_ev_sales, base_ro40)
    actual_no_change = (result.category == previous_category)
    
    print(f"実際の結果:")
    print(f"  結果区分: {result.category}")
    print(f"  ヒステリシス適用: {result.hysteresis_applied}")
    print(f"  実際: {'変更なし' if actual_no_change else '変更あり'}")
    print()
    
    print(f"判定: {'✅ 成功' if expected_no_change == actual_no_change else '❌ 失敗'}")

if __name__ == "__main__":
    debug_failing_case()
