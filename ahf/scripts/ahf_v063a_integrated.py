#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AHF v0.6.3a 統合システム
認知ギャップ★の再定義 + 高速ファネル + 既存v0.6.3
"""

import json
import sys
import subprocess
import argparse
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

class AHFV063AIntegrated:
    def __init__(self, config_path: str, state_path: str):
        self.config_path = config_path
        self.state_path = state_path
        self.results = {}
    
    def run_cognitive_gap_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """認知ギャップ分析実行"""
        try:
            p = subprocess.run(
                [sys.executable, "ahf/mvp4/cognitive_gap_v063a.py", "--config", self.config_path],
                input=json.dumps(data).encode("utf-8"),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            return json.loads(p.stdout.decode("utf-8"))
        except Exception as e:
            return {"error": f"認知ギャップ分析エラー: {e}"}
    
    def run_fast_screen(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Fast-Screen実行"""
        try:
            p = subprocess.run(
                [sys.executable, "ahf/mvp4/fast_screen_v063.py", "--config", self.config_path],
                input=json.dumps(data).encode("utf-8"),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            return json.loads(p.stdout.decode("utf-8"))
        except Exception as e:
            return {"error": f"Fast-Screen実行エラー: {e}"}
    
    def run_mini_confirm(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mini-Confirm実行"""
        try:
            p = subprocess.run(
                [sys.executable, "ahf/mvp4/mini_confirm_v063.py", "--config", self.config_path],
                input=json.dumps(data).encode("utf-8"),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            return json.loads(p.stdout.decode("utf-8"))
        except Exception as e:
            return {"error": f"Mini-Confirm実行エラー: {e}"}
    
    def run_deep_dive(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Deep-Dive実行（既存v0.6.3）"""
        try:
            p = subprocess.run(
                [sys.executable, "ahf/scripts/ahf_v063_integrated.py", 
                 "--config", self.config_path,
                 "--state", "/dev/stdin",
                 "--out", "/dev/stdout"],
                input=json.dumps(data).encode("utf-8"),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            return json.loads(p.stdout.decode("utf-8"))
        except Exception as e:
            return {"error": f"Deep-Dive実行エラー: {e}"}
    
    def run_integrated_evaluation(self) -> Dict[str, Any]:
        """統合評価実行"""
        # 初期データ読み込み
        with open(self.state_path, 'r', encoding='utf-8') as f:
            initial_data = json.load(f)
        
        # 1. 認知ギャップ分析実行
        print("🔄 認知ギャップ分析実行中...")
        cognitive_gap_results = self.run_cognitive_gap_analysis(initial_data)
        if "error" in cognitive_gap_results:
            return {"error": cognitive_gap_results["error"]}
        
        # 2. Fast-Screen実行
        print("🔄 Fast-Screen実行中...")
        fast_screen_results = self.run_fast_screen(initial_data)
        if "error" in fast_screen_results:
            return {"error": fast_screen_results["error"]}
        
        # 3. Mini-Confirm実行
        print("🔄 Mini-Confirm実行中...")
        mini_confirm_results = self.run_mini_confirm(initial_data)
        if "error" in mini_confirm_results:
            return {"error": mini_confirm_results["error"]}
        
        # 4. Deep-Dive実行（通過銘柄のみ）
        deep_dive_results = None
        if (fast_screen_results.get('pass_criteria', {}).get('decision') in ['PASS', 'WATCH'] and
            mini_confirm_results.get('pass_criteria', {}).get('decision') == 'GO'):
            print("🔄 Deep-Dive実行中...")
            deep_dive_results = self.run_deep_dive(initial_data)
            if "error" in deep_dive_results:
                return {"error": deep_dive_results["error"]}
        
        # 統合結果
        integrated_results = {
            "meta": {
                "version": "v0.6.3a",
                "as_of": initial_data.get("as_of", ""),
                "ticker": initial_data.get("ticker", ""),
                "generator": "AHF v0.6.3a Integrated",
                "auditor": "AHF v0.6.3a Integrated",
                "tiebreak": "AHF v0.6.3a Integrated"
            },
            "cognitive_gap_analysis": cognitive_gap_results,
            "fast_screen_results": fast_screen_results,
            "mini_confirm_results": mini_confirm_results,
            "deep_dive_results": deep_dive_results,
            "funnel_decision": self.determine_funnel_decision(fast_screen_results, mini_confirm_results, deep_dive_results)
        }
        
        return integrated_results
    
    def determine_funnel_decision(self, fast_screen: Dict[str, Any], mini_confirm: Dict[str, Any], deep_dive: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """ファネル判定"""
        fast_decision = fast_screen.get('pass_criteria', {}).get('decision', 'DROP')
        mini_decision = mini_confirm.get('pass_criteria', {}).get('decision', 'DROP')
        
        if fast_decision == 'DROP':
            return {
                'final_decision': 'DROP',
                'reason': 'Fast-Screen failed',
                'stage': 'fast_screen'
            }
        elif mini_decision == 'DROP':
            return {
                'final_decision': 'WATCH',
                'reason': 'Mini-Confirm failed',
                'stage': 'mini_confirm'
            }
        elif deep_dive is not None:
            return {
                'final_decision': 'GO',
                'reason': 'All stages passed',
                'stage': 'deep_dive'
            }
        else:
            return {
                'final_decision': 'WATCH',
                'reason': 'Deep-Dive not executed',
                'stage': 'mini_confirm'
            }
    
    def display_results(self, results: Dict[str, Any]):
        """結果表示"""
        print("\n" + "="*80)
        print("📊 AHF v0.6.3a 統合評価結果")
        print("="*80)
        
        # メタ情報
        meta = results.get("meta", {})
        print(f"📅 評価日時: {meta.get('as_of', 'N/A')}")
        print(f"🏷️  銘柄: {meta.get('ticker', 'N/A')}")
        print(f"🔧 バージョン: {meta.get('version', 'N/A')}")
        
        # 認知ギャップ分析結果
        cognitive_gap = results.get("cognitive_gap_analysis", {})
        if cognitive_gap:
            print(f"\n🧠 認知ギャップ分析:")
            print(f"  ★評価: {cognitive_gap.get('cognitive_gap_stars', {}).get('description', 'N/A')}")
            print(f"  オプション種: {cognitive_gap.get('summary', {}).get('option_seeds_count', 0)}件")
            print(f"  織込み/不透明度: {cognitive_gap.get('priced_in_alpha_opacity', {}).get('description', 'N/A')}")
            print(f"  方向確率: {cognitive_gap.get('direction_probability_expanded', {}).get('description', 'N/A')}")
        
        # Fast-Screen結果
        fast_screen = results.get("fast_screen_results", {})
        if fast_screen:
            print(f"\n🚀 Fast-Screen:")
            print(f"  判定: {fast_screen.get('pass_criteria', {}).get('decision', 'N/A')}")
            print(f"  理由: {fast_screen.get('pass_criteria', {}).get('reason', 'N/A')}")
            quick_stars = fast_screen.get('quick_stars', {})
            print(f"  ★評価: {quick_stars.get('axis1', 0)}/{quick_stars.get('axis2', 0)}/{quick_stars.get('axis3', 0)}/{quick_stars.get('axis4', 0)}")
        
        # Mini-Confirm結果
        mini_confirm = results.get("mini_confirm_results", {})
        if mini_confirm:
            print(f"\n🔍 Mini-Confirm:")
            print(f"  判定: {mini_confirm.get('pass_criteria', {}).get('decision', 'N/A')}")
            print(f"  理由: {mini_confirm.get('pass_criteria', {}).get('reason', 'N/A')}")
            print(f"  α3: {mini_confirm.get('alpha3_bridge', {}).get('alpha3_status', 'N/A')}")
            print(f"  α5: {mini_confirm.get('alpha5_grid', {}).get('alpha5_status', 'N/A')}")
        
        # Deep-Dive結果
        deep_dive = results.get("deep_dive_results")
        if deep_dive:
            print(f"\n🔬 Deep-Dive:")
            print(f"  実行: 完了")
            ahf_min = deep_dive.get("ahf_min_results", {})
            print(f"  ★評価: {ahf_min.get('star_rating', {}).get('description', 'N/A')}")
            print(f"  確信度: {ahf_min.get('confidence_level', {}).get('description', 'N/A')}")
        
        # ファネル判定
        funnel_decision = results.get("funnel_decision", {})
        print(f"\n🎯 ファネル判定:")
        print(f"  最終判定: {funnel_decision.get('final_decision', 'N/A')}")
        print(f"  理由: {funnel_decision.get('reason', 'N/A')}")
        print(f"  段階: {funnel_decision.get('stage', 'N/A')}")

def main():
    parser = argparse.ArgumentParser(description='AHF v0.6.3a 統合実行')
    parser.add_argument('--config', required=True, help='設定ファイルパス')
    parser.add_argument('--state', required=True, help='状態ファイルパス')
    parser.add_argument('--out', required=True, help='出力ファイルパス')
    
    args = parser.parse_args()
    
    try:
        # 統合実行
        ahf = AHFV063AIntegrated(args.config, args.state)
        results = ahf.run_integrated_evaluation()
        
        if "error" in results:
            print(f"❌ エラー: {results['error']}")
            sys.exit(1)
        
        # 結果保存
        with open(args.out, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # 結果表示
        ahf.display_results(results)
        
        print(f"\n✅ AHF v0.6.3a 統合評価完了")
        print(f"📊 結果保存: {args.out}")
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()



