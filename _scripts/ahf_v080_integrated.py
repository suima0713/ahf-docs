#!/usr/bin/env python3
"""
AHF v0.8.0 統合スクリプト
固定3軸（①長期EV確度、②長期EV勾配、③バリュエーション＋認知ギャップ）の統合評価

Purpose: 投資判断に直結する固定3軸で評価する
MVP: ①②③の名称と順序を固定／T1で確証（不足は n/a）／定型テーブル＋1行要約を即時出力
"""

import json
import yaml
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# 内部モジュールのインポート
from ahf_v080_workflow import AHFv080Workflow, WorkflowStage
from ahf_v080_evaluator import AHFv080Evaluator
from ahf_v080_turbo_screen import AHFv080TurboScreen
from ahf_v080_anchor_lint import AHFv080AnchorLint
from ahf_v080_math_guard import AHFv080MathGuard, GuardType
from ahf_v080_s3_lint import AHFv080S3Lint

class AHFv080Integrated:
    """AHF v0.8.0 統合評価システム"""
    
    def __init__(self, ticker: str, config: Dict[str, Any] = None):
        self.ticker = ticker
        self.config = config or self._get_default_config()
        self.workflow = AHFv080Workflow(ticker)
        self.evaluator = AHFv080Evaluator(ticker)
        self.turbo_screen = AHFv080TurboScreen(ticker)
        self.anchor_lint = AHFv080AnchorLint()
        self.math_guard = AHFv080MathGuard(GuardType.CORE)
        self.s3_lint = AHFv080S3Lint()
        
    def _get_default_config(self) -> Dict[str, Any]:
        """デフォルト設定取得"""
        return {
            "purpose": "投資判断に直結する固定3軸で評価する",
            "mvp": "①②③の名称と順序を固定／T1で確証（不足は n/a）／定型テーブル＋1行要約を即時出力",
            "axes": {
                "LEC": "①長期EV確度",
                "NES": "②長期EV勾配", 
                "VRG": "③バリュエーション＋認知ギャップ"
            },
            "workflow": {
                "intake": True,
                "stage1_fast_screen": True,
                "stage2_mini_confirm": True,
                "stage3_alpha_maximization": True,
                "decision": True
            },
            "validation": {
                "anchor_lint": True,
                "math_guard": True,
                "s3_lint": True
            },
            "output": {
                "format": "json",
                "include_reports": True,
                "save_files": True
            }
        }
    
    def run_integrated_evaluation(self) -> Dict[str, Any]:
        """統合評価実行"""
        result = {
            "purpose": self.config["purpose"],
            "mvp": self.config["mvp"],
            "ticker": self.ticker,
            "evaluation_date": datetime.now().strftime("%Y-%m-%d"),
            "mode": "統合評価",
            "workflow": {},
            "evaluation": {},
            "turbo_screen": {},
            "validation": {},
            "decision": {},
            "data_gap": {},
            "gap_reason": {}
        }
        
        try:
            # ワークフロー実行
            if self.config["workflow"]["intake"]:
                result["workflow"]["intake"] = self.workflow._run_intake()
            
            if self.config["workflow"]["stage1_fast_screen"]:
                result["workflow"]["stage1"] = self.workflow._run_stage1_fast_screen()
            
            if self.config["workflow"]["stage2_mini_confirm"]:
                result["workflow"]["stage2"] = self.workflow._run_stage2_mini_confirm()
            
            if self.config["workflow"]["stage3_alpha_maximization"]:
                result["workflow"]["stage3"] = self.workflow._run_stage3_alpha_maximization()
            
            if self.config["workflow"]["decision"]:
                result["workflow"]["decision"] = self.workflow._run_decision()
            
            # 評価実行
            result["evaluation"] = self.evaluator.evaluate_ticker()
            
            # Turbo Screen実行
            result["turbo_screen"] = self.turbo_screen.run_turbo_screen()
            
            # バリデーション実行
            if self.config["validation"]["anchor_lint"]:
                result["validation"]["anchor_lint"] = self._run_anchor_lint()
            
            if self.config["validation"]["math_guard"]:
                result["validation"]["math_guard"] = self._run_math_guard()
            
            if self.config["validation"]["s3_lint"]:
                result["validation"]["s3_lint"] = self._run_s3_lint()
            
            # 最終意思決定
            result["decision"] = self._calculate_final_decision(result)
            
            # 出力生成
            if self.config["output"]["save_files"]:
                self._save_output_files(result)
            
        except Exception as e:
            result["error"] = str(e)
            result["data_gap"]["error"] = True
            result["gap_reason"]["error"] = f"統合評価実行エラー: {str(e)}"
            
        return result
    
    def _run_anchor_lint(self) -> Dict[str, Any]:
        """AnchorLint実行"""
        # サンプルデータ（実際はT1データから取得）
        sample_data = [
            {
                "id": "T1-001",
                "verbatim": "Free cash flow $150M for the quarter.",
                "url": "https://sec.gov/edgar/...",
                "anchor": "#:~:text=Free%20cash%20flow"
            }
        ]
        
        return self.anchor_lint.lint_batch(sample_data)
    
    def _run_math_guard(self) -> Dict[str, Any]:
        """数理ガード実行"""
        # サンプルデータ（実際は評価データから取得）
        sample_data = [
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
        
        return self.math_guard.check_batch(sample_data)
    
    def _run_s3_lint(self) -> Dict[str, Any]:
        """S3-Lint実行"""
        # サンプルデータ（実際はStage-3カードから取得）
        sample_data = [
            {
                "id": "S3-001",
                "t1_verbatim": "Guidance raised to $2.5B",
                "url_anchor": "https://sec.gov/...#:~:text=Guidance%20raised",
                "test_formula": "guidance_fy26_mid >= 2500",
                "ttl_days": 30,
                "reasoning": "ガイダンス上方修正は成長加速を示唆"
            }
        ]
        
        return self.s3_lint.lint_batch(sample_data)
    
    def _calculate_final_decision(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """最終意思決定計算"""
        # ワークフロー結果からDI取得
        workflow_decision = result["workflow"].get("decision", {})
        evaluation_decision = result["evaluation"].get("decision", {})
        
        # 最終DI計算
        final_di = workflow_decision.get("di_score", 0.0)
        if final_di == 0.0:
            final_di = evaluation_decision.get("di", 0.0)
        
        # アクション決定
        if final_di >= 0.55:
            action = "GO"
        elif final_di >= 0.32:
            action = "WATCH"
        else:
            action = "NO-GO"
        
        # サイズ計算
        size_percentage = 1.2 * final_di
        
        return {
            "final_di": final_di,
            "action": action,
            "size_percentage": size_percentage,
            "size_category": self._determine_size_category(size_percentage),
            "confidence": self._calculate_confidence(result),
            "risk_factors": self._identify_risk_factors(result)
        }
    
    def _determine_size_category(self, size_percentage: float) -> str:
        """サイズカテゴリ決定"""
        if size_percentage >= 2.0:
            return "High"
        elif size_percentage >= 1.0:
            return "Med"
        else:
            return "Low"
    
    def _calculate_confidence(self, result: Dict[str, Any]) -> float:
        """確信度計算"""
        # バリデーション結果から確信度計算
        confidence = 0.5  # ベース確信度
        
        # AnchorLint結果
        anchor_lint = result.get("validation", {}).get("anchor_lint", {})
        if anchor_lint.get("summary", {}).get("pass_rate", 0) > 0.8:
            confidence += 0.1
        
        # 数理ガード結果
        math_guard = result.get("validation", {}).get("math_guard", {})
        if math_guard.get("summary", {}).get("pass_rate", 0) > 0.8:
            confidence += 0.1
        
        # S3-Lint結果
        s3_lint = result.get("validation", {}).get("s3_lint", {})
        if s3_lint.get("summary", {}).get("pass_rate", 0) > 0.8:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _identify_risk_factors(self, result: Dict[str, Any]) -> List[str]:
        """リスク要因特定"""
        risk_factors = []
        
        # データギャップ
        if result.get("data_gap", {}):
            risk_factors.append("データギャップ")
        
        # バリデーション失敗
        validation = result.get("validation", {})
        for key, val in validation.items():
            if isinstance(val, dict) and val.get("summary", {}).get("pass_rate", 0) < 0.5:
                risk_factors.append(f"{key}失敗")
        
        return risk_factors
    
    def _save_output_files(self, result: Dict[str, Any]):
        """出力ファイル保存"""
        output_dir = f"ahf/tickers/{self.ticker}/current"
        os.makedirs(output_dir, exist_ok=True)
        
        # JSON出力
        with open(f"{output_dir}/evaluation_v080.json", 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        # レポート生成
        report = self._generate_integrated_report(result)
        with open(f"{output_dir}/evaluation_v080_report.md", 'w', encoding='utf-8') as f:
            f.write(report)
    
    def _generate_integrated_report(self, result: Dict[str, Any]) -> str:
        """統合レポート生成"""
        report = f"""
# AHF v0.8.0 統合評価レポート

## 基本情報
- 銘柄: {result['ticker']}
- 評価日: {result['evaluation_date']}
- 目的: {result['purpose']}
- MVP: {result['mvp']}

## 評価結果
"""
        
        # 意思決定結果
        decision = result.get("decision", {})
        if decision:
            report += f"""
### 意思決定
- 最終DI: {decision.get('final_di', 0.0):.2f}
- アクション: {decision.get('action', 'N/A')}
- サイズ: {decision.get('size_percentage', 0.0):.1f}% ({decision.get('size_category', 'N/A')})
- 確信度: {decision.get('confidence', 0.0):.1%}
"""
        
        # リスク要因
        risk_factors = decision.get("risk_factors", [])
        if risk_factors:
            report += f"""
### リスク要因
{chr(10).join(f"- {factor}" for factor in risk_factors)}
"""
        
        # バリデーション結果
        validation = result.get("validation", {})
        if validation:
            report += f"""
### バリデーション結果
"""
            for key, val in validation.items():
                if isinstance(val, dict) and "summary" in val:
                    pass_rate = val["summary"].get("pass_rate", 0)
                    report += f"- {key}: {pass_rate:.1%}\n"
        
        return report

def main():
    """メイン実行"""
    if len(sys.argv) < 2:
        print("Usage: python ahf_v080_integrated.py <TICKER> [config_file]")
        sys.exit(1)
    
    ticker = sys.argv[1]
    config_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # 設定読み込み
    config = None
    if config_file and os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    
    # 統合評価実行
    integrated = AHFv080Integrated(ticker, config)
    result = integrated.run_integrated_evaluation()
    
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()

