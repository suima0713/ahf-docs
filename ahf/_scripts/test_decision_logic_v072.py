#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AHF v0.7.2β Decision Logic Test
②★3以上×③★2以上=GOの動作確認
"""

import json
import sys
import os
sys.path.append(os.path.dirname(__file__))
from ahf_tri3_v_overlay_v072 import process_tri3_v_overlay_v072

def test_decision_logic():
    """Decisionロジックのテスト"""
    
    test_cases = [
        {
            "name": "GO条件：②★3以上×③★2以上",
            "triage_file": "test_tri3_v072_sample.json",  # ③★5
            "alpha_file": "test_alpha_sample.json",
            "expected_decision": "GO",
            "description": "③★5なのでGO条件を満たす"
        },
        {
            "name": "ARRY例：V=Green、T+R=2",
            "triage_file": "test_arry_sample.json",  # ③★4
            "alpha_file": "test_alpha_sample.json",
            "expected_decision": "GO",
            "description": "③★4なのでGO条件を満たす"
        },
        {
            "name": "Amber例：V=Amber、T+R=3",
            "triage_file": "test_amber_sample.json",  # ③★4
            "alpha_file": "test_alpha_sample.json",
            "expected_decision": "GO",
            "description": "③★4なのでGO条件を満たす"
        },
        {
            "name": "Red例：V=Red、T+R=1",
            "triage_file": "test_red_sample.json",  # ③★2
            "alpha_file": "test_alpha_sample.json",
            "expected_decision": "GO",
            "description": "③★2なのでGO条件を満たす（境界値）"
        }
    ]
    
    print("=== AHF v0.7.2β Decision Logic Test ===")
    print("Decision基準：②★3以上×③★2以上=GO")
    print()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"テスト{i}: {test_case['name']}")
        print(f"説明: {test_case['description']}")
        
        try:
            # ③認知ギャップの評価実行
            result = process_tri3_v_overlay_v072(test_case['triage_file'], test_case['alpha_file'])
            
            # ③の★を取得
            cognitive_star = result['tri3']['star']
            
            # Decision判定（簡略化：③のみで判定）
            # 実際の実装では②の★も考慮する
            if cognitive_star >= 2:
                decision = "GO"
            elif cognitive_star >= 1:
                decision = "WATCH"
            else:
                decision = "NO-GO"
            
            print(f"  ③★: {cognitive_star}")
            print(f"  Decision: {decision}")
            print(f"  期待値: {test_case['expected_decision']}")
            
            if decision == test_case['expected_decision']:
                print("  ✅ PASS")
            else:
                print("  ❌ FAIL")
                
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
        
        print()
    
    print("=== テスト完了 ===")
    print("注意：実際のDecisionロジックでは②の★も考慮されます")
    print("このテストは③のみの動作確認です")

if __name__ == "__main__":
    test_decision_logic()

