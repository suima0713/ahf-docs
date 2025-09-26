#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AHF v0.6.3 統合実行スクリプト
T1限定・Star整数評価・Edge管理・AnchorLint v1対応の統合実行
"""

import json
import sys
import subprocess
import argparse
from pathlib import Path
from typing import Dict, Any

class AHFV063Integrated:
    def __init__(self, config_path: str, state_path: str):
        self.config_path = config_path
        self.state_path = state_path
        self.results = {}
    
    def run_alpha_bridge(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """αブリッジ標準実行"""
        try:
            # αブリッジ評価実行
            p = subprocess.run(
                [sys.executable, "ahf/mvp4/alpha_bridge_v063.py", self.config_path],
                input=json.dumps(data).encode("utf-8"),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            return json.loads(p.stdout.decode("utf-8"))
        except Exception as e:
            return {"error": f"αブリッジ実行エラー: {e}"}
    
    def run_edge_management(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Edge管理実行"""
        try:
            # Edge管理実行
            p = subprocess.run(
                [sys.executable, "ahf/mvp4/edge_management_v063.py", self.config_path],
                input=json.dumps(data).encode("utf-8"),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            return json.loads(p.stdout.decode("utf-8"))
        except Exception as e:
            return {"error": f"Edge管理実行エラー: {e}"}
    
    def run_anchor_lint(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """AnchorLint v1実行"""
        try:
            # AnchorLint実行
            p = subprocess.run(
                [sys.executable, "ahf/mvp4/anchor_lint_v1.py", "--config", "ahf/config/anchorlint.yaml"],
                input=json.dumps(data).encode("utf-8"),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            return json.loads(p.stdout.decode("utf-8"))
        except Exception as e:
            return {"error": f"AnchorLint実行エラー: {e}"}
    
    def run_operational_validation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """運用検証実行"""
        try:
            # 運用検証実行
            p = subprocess.run(
                [sys.executable, "ahf/mvp4/operational_validation_v063.py", self.config_path],
                input=json.dumps(data).encode("utf-8"),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            return json.loads(p.stdout.decode("utf-8"))
        except Exception as e:
            return {"error": f"運用検証実行エラー: {e}"}
    
    def run_ahf_min(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """AHF Min実行"""
        try:
            # AHF Min実行
            p = subprocess.run(
                [sys.executable, "ahf/src/ahf_min.py", "--config", self.config_path, "--state", self.state_path, "--out", "/dev/stdout"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            return json.loads(p.stdout.decode("utf-8"))
        except Exception as e:
            return {"error": f"AHF Min実行エラー: {e}"}
    
    def run_integrated_evaluation(self) -> Dict[str, Any]:
        """統合評価実行"""
        # 初期データ読み込み
        with open(self.state_path, 'r', encoding='utf-8') as f:
            initial_data = json.load(f)
        
        # 1. AHF Min実行（基本評価）
        print("🔄 AHF Min実行中...")
        ahf_min_results = self.run_ahf_min(initial_data)
        if "error" in ahf_min_results:
            return {"error": ahf_min_results["error"]}
        
        # 2. αブリッジ標準実行
        print("🔄 αブリッジ標準実行中...")
        alpha_bridge_results = self.run_alpha_bridge(initial_data)
        if "error" in alpha_bridge_results:
            return {"error": alpha_bridge_results["error"]}
        
        # 3. Edge管理実行
        print("🔄 Edge管理実行中...")
        edge_results = self.run_edge_management(initial_data)
        if "error" in edge_results:
            return {"error": edge_results["error"]}
        
        # 4. AnchorLint v1実行
        print("🔄 AnchorLint v1実行中...")
        anchor_lint_results = self.run_anchor_lint(initial_data)
        if "error" in anchor_lint_results:
            return {"error": anchor_lint_results["error"]}
        
        # 5. 運用検証実行
        print("🔄 運用検証実行中...")
        validation_results = self.run_operational_validation(initial_data)
        if "error" in validation_results:
            return {"error": validation_results["error"]}
        
        # 統合結果
        integrated_results = {
            "meta": {
                "version": "v0.6.3",
                "as_of": initial_data.get("as_of", ""),
                "ticker": initial_data.get("ticker", ""),
                "generator": "AHF v0.6.3 Integrated",
                "auditor": "AHF v0.6.3 Integrated",
                "tiebreak": "AHF v0.6.3 Integrated"
            },
            "ahf_min_results": ahf_min_results,
            "alpha_bridge_results": alpha_bridge_results,
            "edge_management_results": edge_results,
            "anchor_lint_results": anchor_lint_results,
            "operational_validation_results": validation_results
        }
        
        return integrated_results
    
    def display_results(self, results: Dict[str, Any]):
        """結果表示"""
        print("\n" + "="*80)
        print("📊 AHF v0.6.3 統合評価結果")
        print("="*80)
        
        # メタ情報
        meta = results.get("meta", {})
        print(f"📅 評価日時: {meta.get('as_of', 'N/A')}")
        print(f"🏷️  銘柄: {meta.get('ticker', 'N/A')}")
        print(f"🔧 バージョン: {meta.get('version', 'N/A')}")
        
        # AHF Min結果
        ahf_min = results.get("ahf_min_results", {})
        if ahf_min:
            print(f"\n🎯 AHF Min評価:")
            print(f"  α4 Gate: {ahf_min.get('alpha4_gate', {}).get('description', 'N/A')}")
            print(f"  α5 Band: {ahf_min.get('alpha5_bands', {}).get('description', 'N/A')}")
            print(f"  ★評価: {ahf_min.get('star_rating', {}).get('description', 'N/A')}")
            print(f"  確信度: {ahf_min.get('confidence_level', {}).get('description', 'N/A')}")
        
        # αブリッジ結果
        alpha_bridge = results.get("alpha_bridge_results", {})
        if alpha_bridge:
            print(f"\n🔗 αブリッジ標準:")
            for key, value in alpha_bridge.items():
                if isinstance(value, dict) and 'description' in value:
                    print(f"  {key}: {value['description']}")
        
        # Edge管理結果
        edge_mgmt = results.get("edge_management_results", {})
        if edge_mgmt:
            edge_summary = edge_mgmt.get("edge_summary", {})
            print(f"\n📈 Edge管理:")
            print(f"  総Edge数: {edge_summary.get('total_edges', 0)}")
            print(f"  Star調整: {edge_summary.get('star_adjustment', 0):+d}")
            print(f"  確信度調整: {edge_summary.get('confidence_adjustment', 0):+d}pp")
        
        # 運用検証結果
        validation = results.get("operational_validation_results", {})
        if validation:
            overall_score = validation.get("overall_score", {})
            print(f"\n🔍 運用検証:")
            print(f"  全体スコア: {overall_score.get('description', 'N/A')}")
            
            # アラート表示
            alerts = overall_score.get("alerts", [])
            if alerts:
                print(f"  🚨 アラート:")
                for alert in alerts:
                    print(f"    - {alert}")

def main():
    parser = argparse.ArgumentParser(description='AHF v0.6.3 統合実行')
    parser.add_argument('--config', required=True, help='設定ファイルパス')
    parser.add_argument('--state', required=True, help='状態ファイルパス')
    parser.add_argument('--out', required=True, help='出力ファイルパス')
    
    args = parser.parse_args()
    
    try:
        # 統合実行
        ahf = AHFV063Integrated(args.config, args.state)
        results = ahf.run_integrated_evaluation()
        
        if "error" in results:
            print(f"❌ エラー: {results['error']}")
            sys.exit(1)
        
        # 結果保存
        with open(args.out, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # 結果表示
        ahf.display_results(results)
        
        print(f"\n✅ AHF v0.6.3 統合評価完了")
        print(f"📊 結果保存: {args.out}")
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

