#!/usr/bin/env python3
"""
AHF v0.8.1-r2 統合スクリプト
固定4軸（①長期EV確度、②長期EV勾配、③現バリュエーション、④将来EVバリュ）の統合評価

Purpose: 投資判断に直結する固定4軸で評価
MVP: ①②③④の名称と順序を絶対固定／T1 or T1*で確証（不足はn/a）／定型テーブル＋1行要約を即出力

CHANGELOG（v0.8.1-c1 → v0.8.1-r2）
- T1*（Corroborated二次）を導入：★/DIに反映可、表示タグと即時降格規律を追加
- ③＝現在のみ（peer）／④＝将来のみ（rDCF×T1/T1*）を再強化
- Price-Lint／AnchorLint-T1* を追加、SoftOverlayにT1*上限（±0.03）を設定
"""

import json
import yaml
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum

# 内部モジュールのインポート
from ahf_v081_r2_workflow import AHFv081R2Workflow, WorkflowStage
from ahf_v081_r2_evaluator import AHFv081R2Evaluator
from ahf_v081_r2_turbo_screen import AHFv081R2TurboScreen
from ahf_v081_r2_anchor_lint import AHFv081R2AnchorLint
from ahf_v081_r2_math_guard import AHFv081R2MathGuard, GuardType
from ahf_v081_r2_s3_lint import AHFv081R2S3Lint

class EvidenceLevel(Enum):
    """証拠階層"""
    T1 = "T1"          # 一次（SEC/IR）
    T1_STAR = "T1*"    # Corroborated二次（独立2源以上）
    T2 = "T2"          # 二次1源

@dataclass
class EvidenceItem:
    """証拠アイテム"""
    id: str
    level: EvidenceLevel
    verbatim: str
    url: str
    anchor: str
    source_domain: str
    ttl_days: int = 14
    dual_anchor_status: str = "PENDING_SEC"
    contradiction_flag: bool = False

class AHFv081R2Integrated:
    """AHF v0.8.1-r2 統合評価システム"""
    
    def __init__(self, ticker: str, config: Dict[str, Any] = None):
        self.ticker = ticker
        self.config = config or self._get_default_config()
        self.workflow = AHFv081R2Workflow(ticker)
        self.evaluator = AHFv081R2Evaluator(ticker)
        self.turbo_screen = AHFv081R2TurboScreen(ticker)
        self.anchor_lint = AHFv081R2AnchorLint()
        self.math_guard = AHFv081R2MathGuard(GuardType.CORE)
        self.s3_lint = AHFv081R2S3Lint()
        
    def _get_default_config(self) -> Dict[str, Any]:
        """デフォルト設定取得"""
        return {
            "purpose": "投資判断に直結する固定4軸で評価",
            "mvp": "①②③④の名称と順序を絶対固定／T1 or T1*で確証（不足はn/a）／定型テーブル＋1行要約を即出力",
            "axes": {
                "LEC": "①長期EV確度",
                "NES": "②長期EV勾配", 
                "CURRENT_VAL": "③現バリュエーション（機械）",
                "FUTURE_VAL": "④将来EVバリュ（総合）"
            },
            "evidence_ladder": {
                "T1": "一次（SEC/IR）",
                "T1_STAR": "Corroborated二次（独立2源以上）",
                "T2": "二次1源"
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
                "anchor_lint_t1star": True,
                "price_lint": True,
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
            "action_log": [],
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
                result["action_log"].append("Intake完了")
            
            if self.config["workflow"]["stage1_fast_screen"]:
                result["workflow"]["stage1"] = self.workflow._run_stage1_fast_screen()
                result["action_log"].append("Stage-1 Fast-Screen完了")
            
            if self.config["workflow"]["stage2_mini_confirm"]:
                result["workflow"]["stage2"] = self.workflow._run_stage2_mini_confirm()
                result["action_log"].append("Stage-2 Mini-Confirm完了")
            
            if self.config["workflow"]["stage3_alpha_maximization"]:
                result["workflow"]["stage3"] = self.workflow._run_stage3_alpha_maximization()
                result["action_log"].append("Stage-3 Alpha-Maximization完了")
            
            if self.config["workflow"]["decision"]:
                result["workflow"]["decision"] = self.workflow._run_decision()
                result["action_log"].append("Decision完了")
            
            # 4軸評価実行
            result["evaluation"] = self.evaluator.evaluate_4_axes()
            
            # Turbo Screen実行
            result["turbo_screen"] = self.turbo_screen.run_turbo_screen()
            
            # バリデーション実行
            if self.config["validation"]["anchor_lint"]:
                result["validation"]["anchor_lint"] = self._run_anchor_lint()
                result["action_log"].append("AnchorLint完了")
            
            if self.config["validation"]["anchor_lint_t1star"]:
                result["validation"]["anchor_lint_t1star"] = self._run_anchor_lint_t1star()
                result["action_log"].append("AnchorLint-T1*完了")
            
            if self.config["validation"]["price_lint"]:
                result["validation"]["price_lint"] = self._run_price_lint()
                result["action_log"].append("Price-Lint完了")
            
            if self.config["validation"]["math_guard"]:
                result["validation"]["math_guard"] = self._run_math_guard()
                result["action_log"].append("Math-Guard完了")
            
            if self.config["validation"]["s3_lint"]:
                result["validation"]["s3_lint"] = self._run_s3_lint()
                result["action_log"].append("S3-Lint完了")
            
            # 最終意思決定
            result["decision"] = self._calculate_final_decision(result)
            
            # 出力生成
            if self.config["output"]["save_files"]:
                self._save_output_files(result)
            
        except Exception as e:
            result["error"] = str(e)
            result["data_gap"]["error"] = True
            result["gap_reason"]["error"] = f"統合評価実行エラー: {str(e)}"
            result["action_log"].append(f"エラー: {str(e)}")
            
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
    
    def _run_anchor_lint_t1star(self) -> Dict[str, Any]:
        """AnchorLint-T1*実行"""
        # T1*証拠の独立性テスト
        sample_data = [
            {
                "id": "T1STAR-001",
                "two_sources": True,
                "independent": True,
                "quote_len": 20,
                "url_has_text": True,
                "verbatim": "Revenue guidance raised to $2.5B",
                "url": "https://investor.company.com/...#:~:text=Revenue%20guidance",
                "source_domain": "investor.company.com"
            }
        ]
        
        return self.anchor_lint.lint_t1star_batch(sample_data)
    
    def _run_price_lint(self) -> Dict[str, Any]:
        """Price-Lint実行"""
        # 価格系隔離の検証
        sample_data = [
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
        
        return self.anchor_lint.lint_price_batch(sample_data)
    
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
        # 4軸評価結果からDI計算
        evaluation = result.get("evaluation", {})
        
        # 各軸のスコア取得
        lec_score = evaluation.get("lec", {}).get("star_score", 0) / 5.0
        nes_score = evaluation.get("nes", {}).get("star_score", 0) / 5.0
        current_val = evaluation.get("current_valuation", {})
        future_val = evaluation.get("future_valuation", {})
        
        # Vmult取得（③現バリュエーションから）
        vmult = current_val.get("vmult", 1.0)
        
        # DI計算: DI = (0.6·s2 + 0.4·s1) · Vmult(③)
        di = (0.6 * nes_score + 0.4 * lec_score) * vmult
        
        # SoftOverlay適用（T1*由来の加点は±0.03以内）
        soft_overlay = self._calculate_soft_overlay(result)
        di += soft_overlay
        
        # アクション決定
        if di >= 0.55:
            action = "GO"
        elif di >= 0.32:
            action = "WATCH"
        else:
            action = "NO-GO"
        
        # サイズ計算
        size_percentage = 1.2 * di
        
        return {
            "final_di": di,
            "action": action,
            "size_percentage": size_percentage,
            "size_category": self._determine_size_category(size_percentage),
            "confidence": self._calculate_confidence(result),
            "risk_factors": self._identify_risk_factors(result),
            "soft_overlay": soft_overlay,
            "axes_scores": {
                "lec": lec_score,
                "nes": nes_score,
                "current_val": current_val,
                "future_val": future_val
            }
        }
    
    def _calculate_soft_overlay(self, result: Dict[str, Any]) -> float:
        """SoftOverlay計算"""
        # T1*由来の加点は±0.03以内
        t1star_bonus = 0.0
        
        # ④将来EVバリュの補助（必要時±0.05のみ）
        future_val_overlay = 0.0
        
        return t1star_bonus + future_val_overlay
    
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
        
        # AnchorLint-T1*結果
        anchor_lint_t1star = result.get("validation", {}).get("anchor_lint_t1star", {})
        if anchor_lint_t1star.get("summary", {}).get("pass_rate", 0) > 0.8:
            confidence += 0.05
        
        # Price-Lint結果
        price_lint = result.get("validation", {}).get("price_lint", {})
        if price_lint.get("summary", {}).get("pass_rate", 0) > 0.8:
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
        with open(f"{output_dir}/evaluation_v081_r2.json", 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        # レポート生成
        report = self._generate_integrated_report(result)
        with open(f"{output_dir}/evaluation_v081_r2_report.md", 'w', encoding='utf-8') as f:
            f.write(report)
    
    def _generate_integrated_report(self, result: Dict[str, Any]) -> str:
        """統合レポート生成"""
        report = f"""
# AHF v0.8.1-r2 統合評価レポート

## 基本情報
- 銘柄: {result['ticker']}
- 評価日: {result['evaluation_date']}
- 目的: {result['purpose']}
- MVP: {result['mvp']}

## 4軸評価結果
"""
        
        # 4軸評価結果
        evaluation = result.get("evaluation", {})
        if evaluation:
            report += """
### ①長期EV確度（LEC）
"""
            lec = evaluation.get("lec", {})
            if lec:
                report += f"- スコア: {lec.get('score', 0):.1f}\n"
                report += f"- 星: {lec.get('star_score', 0)}/5\n"
                report += f"- 確信度: {lec.get('confidence', 0):.1%}\n"
            
            report += """
### ②長期EV勾配（NES）
"""
            nes = evaluation.get("nes", {})
            if nes:
                report += f"- スコア: {nes.get('score', 0):.1f}\n"
                report += f"- 星: {nes.get('star_score', 0)}/5\n"
                report += f"- 確信度: {nes.get('confidence', 0):.1%}\n"
            
            report += """
### ③現バリュエーション（機械）
"""
            current_val = evaluation.get("current_valuation", {})
            if current_val:
                report += f"- EV/S_actual: {current_val.get('evs_actual_ttm', 0):.1f}\n"
                report += f"- EV/S_peer_median: {current_val.get('evs_peer_median_ttm', 0):.1f}\n"
                report += f"- 乖離率: {current_val.get('disc_pct', 0):.1%}\n"
                report += f"- 色: {current_val.get('color', 'N/A')}\n"
                report += f"- Vmult: {current_val.get('vmult', 1.0):.2f}\n"
            
            report += """
### ④将来EVバリュ（総合）
"""
            future_val = evaluation.get("future_valuation", {})
            if future_val:
                report += f"- EVS_fair_12m: {future_val.get('evs_fair_12m', 0):.1f}\n"
                report += f"- FD%: {future_val.get('fd_pct', 0):.1%}\n"
                report += f"- 星: {future_val.get('star_score', 0)}/5\n"
                report += f"- 確信度: {future_val.get('confidence', 0):.1%}\n"
        
        # 意思決定結果
        decision = result.get("decision", {})
        if decision:
            report += f"""
## 意思決定
- 最終DI: {decision.get('final_di', 0.0):.2f}
- アクション: {decision.get('action', 'N/A')}
- サイズ: {decision.get('size_percentage', 0.0):.1f}% ({decision.get('size_category', 'N/A')})
- 確信度: {decision.get('confidence', 0.0):.1%}
- SoftOverlay: {decision.get('soft_overlay', 0.0):.3f}
"""
        
        # リスク要因
        risk_factors = decision.get("risk_factors", [])
        if risk_factors:
            report += f"""
## リスク要因
{chr(10).join(f"- {factor}" for factor in risk_factors)}
"""
        
        # バリデーション結果
        validation = result.get("validation", {})
        if validation:
            report += f"""
## バリデーション結果
"""
            for key, val in validation.items():
                if isinstance(val, dict) and "summary" in val:
                    pass_rate = val["summary"].get("pass_rate", 0)
                    report += f"- {key}: {pass_rate:.1%}\n"
        
        return report

def main():
    """メイン実行"""
    if len(sys.argv) < 2:
        print("Usage: python ahf_v081_r2_integrated.py <TICKER> [config_file]")
        sys.exit(1)
    
    ticker = sys.argv[1]
    config_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # 設定読み込み
    config = None
    if config_file and os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    
    # 統合評価実行
    integrated = AHFv081R2Integrated(ticker, config)
    result = integrated.run_integrated_evaluation()
    
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
