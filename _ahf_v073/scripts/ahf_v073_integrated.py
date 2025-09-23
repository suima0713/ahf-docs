#!/usr/bin/env python3
"""
AHF v0.7.3 統合実行スクリプト
Purpose: 固定3軸評価システムの統合実行
MVP: ①②③の名称と順序を毎回固定／T1で確証／定型テーブル＋1行要約で即時出力
"""

import sys
import os
import json
import yaml
from datetime import datetime
from typing import Dict, List, Optional, Any

# 相対インポート用のパス設定
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ahf_v073_evaluator import AHFv073Evaluator
from ahf_turbo_screen import TurboScreenEngine
from ahf_anchor_lint import AnchorLintEngine
from ahf_mvp4_output import MVP4OutputGenerator

class AHFv073Integrated:
    """AHF v0.7.3 統合実行エンジン"""
    
    def __init__(self, ticker: str, data_dir: str = "tickers"):
        self.ticker = ticker
        self.data_dir = data_dir
        self.ticker_path = os.path.join(data_dir, ticker, "current")
        
        # 各エンジンを初期化
        self.evaluator = AHFv073Evaluator()
        self.turbo_engine = TurboScreenEngine()
        self.lint_engine = AnchorLintEngine()
        self.output_generator = MVP4OutputGenerator()
        
        # ファイルパス
        self.facts_file = os.path.join(self.ticker_path, "facts.md")
        self.triage_file = os.path.join(self.ticker_path, "triage.json")
        self.backlog_file = os.path.join(self.ticker_path, "backlog.md")
        self.a_file = os.path.join(self.ticker_path, "A.yaml")
        self.b_file = os.path.join(self.ticker_path, "B.yaml")
        self.c_file = os.path.join(self.ticker_path, "C.yaml")
    
    def run_evaluation(self) -> Dict[str, Any]:
        """統合評価を実行"""
        print(f"=== AHF v0.7.3 統合評価開始: {self.ticker} ===")
        print(f"Purpose: 投資判断に直結する固定3軸で評価する")
        print(f"MVP: ①②③の名称と順序を毎回固定／T1で確証／定型テーブル＋1行要約で即時出力")
        print()
        
        try:
            # 1. T1データ読み込み
            print("1. T1データ読み込み中...")
            self.evaluator.load_t1_data(self.facts_file, self.triage_file)
            print(f"   T1事実数: {len(self.evaluator.t1_facts)}")
            
            # 2. 固定3軸評価
            print("2. 固定3軸評価実行中...")
            lec_score = self.evaluator.evaluate_axis_lec()
            nes_score = self.evaluator.evaluate_axis_nes()
            vrg_score = self.evaluator.evaluate_axis_vrg()
            
            axis_scores = [lec_score, nes_score, vrg_score]
            print(f"   LEC: ★{lec_score.score}/5 (確信度{lec_score.confidence}%)")
            print(f"   NES: ★{nes_score.score}/5 (確信度{nes_score.confidence}%)")
            print(f"   VRG: ★{vrg_score.score}/5 (確信度{vrg_score.confidence}%)")
            
            # 3. Turbo Screen適用
            print("3. Turbo Screen適用中...")
            try:
                self.turbo_engine.load_edge_data(self.backlog_file, self.triage_file)
                eligible_edge_facts = self.turbo_engine.filter_eligible_edge_facts()
                print(f"   受付Edge事実数: {len(eligible_edge_facts)}")
                
                # Turbo Screen調整を適用
                turbo_scores = self.turbo_engine.apply_turbo_adjustments(
                    [{"axis": "①長期EV確度", "score": lec_score.score, "confidence": lec_score.confidence},
                     {"axis": "②長期EV勾配", "score": nes_score.score, "confidence": nes_score.confidence},
                     {"axis": "③バリュエーション＋認知ギャップ", "score": vrg_score.score, "confidence": vrg_score.confidence}],
                    eligible_edge_facts
                )
                
                # 軸スコアを更新
                for i, turbo_score in enumerate(turbo_scores):
                    if turbo_score.get('turbo_applied', False):
                        axis_scores[i].score = turbo_score['score']
                        axis_scores[i].confidence = turbo_score['confidence']
                        axis_scores[i].edge_facts = eligible_edge_facts
                        print(f"   {axis_scores[i].axis.value}: ★{turbo_score['score']}/5 (Turbo適用)")
                
            except Exception as e:
                print(f"   Turbo Screen適用エラー: {e}")
                print("   Core評価のみで継続")
            
            # 4. 意思決定計算
            print("4. 意思決定計算中...")
            decision = self.evaluator.calculate_decision(axis_scores)
            print(f"   判定: {decision.decision.value} (DI={decision.di_score:.2f})")
            print(f"   サイズ: {decision.size_pct:.1f}%")
            
            # 5. AnchorLint実行
            print("5. AnchorLint実行中...")
            t1_facts_data = [{"kpi": f.kpi, "verbatim": f.verbatim, "anchor": f.anchor, "url": f.url} 
                           for f in self.evaluator.t1_facts]
            lint_results = self.lint_engine.batch_lint_facts(t1_facts_data)
            lint_report = self.lint_engine.generate_lint_report(lint_results)
            print(f"   AnchorLint有効率: {lint_report['summary']['validity_rate']:.1f}%")
            
            # 6. MVP-4+出力生成
            print("6. MVP-4+出力生成中...")
            
            # 軸結果を生成
            axis_results = []
            axis_names = ["①長期EV確度", "②長期EV勾配", "③バリュエーション＋認知ギャップ"]
            for i, score in enumerate(axis_scores):
                axis_result = self.output_generator.generate_axis_result(
                    axis_names[i], 
                    int(score.score), 
                    score.confidence,
                    [{"kpi": f.kpi, "value": f.value, "unit": f.unit, "verbatim": f.verbatim} for f in score.t1_facts],
                    [{"kpi": f.kpi, "value": f.value, "unit": f.unit, "verbatim": f.verbatim} for f in score.edge_facts]
                )
                axis_results.append(axis_result)
            
            # バリュエーション生成
            valuation = self.output_generator.generate_valuation_overlay(
                self.evaluator.valuation_overlay.ev_sales_fwd if self.evaluator.valuation_overlay else 0.0,
                self.evaluator.valuation_overlay.rule_of_40 if self.evaluator.valuation_overlay else 0.0
            )
            
            # 完全出力生成
            output = self.output_generator.generate_complete_output(
                self.ticker, axis_results, decision, valuation, t1_facts_data
            )
            
            # 7. 結果表示
            print("\n" + "="*60)
            table = self.output_generator.format_output_table(output)
            print(table)
            
            # 8. ファイル保存
            self._save_output_files(output, axis_scores, decision, lint_report)
            
            return output
            
        except Exception as e:
            print(f"統合評価エラー: {e}")
            return {"error": str(e)}
    
    def _save_output_files(self, output: Dict[str, Any], axis_scores: List, 
                          decision, lint_report: Dict[str, Any]) -> None:
        """出力ファイルを保存"""
        try:
            # JSON出力
            output_file = os.path.join(self.ticker_path, "ahf_v073_output.json")
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(output, f, ensure_ascii=False, indent=2)
            print(f"\n出力を{output_file}に保存しました。")
            
            # A.yaml更新
            self._update_a_yaml(axis_scores)
            
            # B.yaml更新
            self._update_b_yaml(decision, output)
            
            # C.yaml更新
            self._update_c_yaml()
            
            # facts.md更新
            self._update_facts_md(axis_scores)
            
            # triage.json更新
            self._update_triage_json(lint_report)
            
        except Exception as e:
            print(f"ファイル保存エラー: {e}")
    
    def _update_a_yaml(self, axis_scores: List) -> None:
        """A.yamlを更新"""
        try:
            a_data = {
                "meta": {"asof": datetime.now().strftime("%Y-%m-%d")},
                "core": {
                    "right_shoulder": [f.verbatim for f in axis_scores[0].t1_facts[:2]],  # LEC
                    "slope_quality": [f.verbatim for f in axis_scores[1].t1_facts[:2]],  # NES
                    "time_profile": [f.verbatim for f in axis_scores[2].t1_facts[:2]],    # VRG
                    "cognition_gap": []
                },
                "fast_screen_mode": False,
                "timeline_metrics": {
                    "coverage_months": 0,
                    "rpo_12m_millions": 0,
                    "guidance_clarity": "明確",
                    "recognition_timeline": "Q1",
                    "timeline_star": axis_scores[0].score,
                    "coverage_calculable": True,
                    "strong_trigger_met": True
                },
                "cognition_metrics": {
                    "market_expectation_gap": "上振れ",
                    "trigger_a_quantity": True,
                    "trigger_b_timing": True,
                    "trigger_ab_combined": True,
                    "negative_triggers": False,
                    "cognition_star": axis_scores[2].score,
                    "ab_trigger_met": True,
                    "market_assessment": "評価済み"
                }
            }
            
            with open(self.a_file, "w", encoding="utf-8") as f:
                yaml.dump(a_data, f, default_flow_style=False, allow_unicode=True)
            
        except Exception as e:
            print(f"A.yaml更新エラー: {e}")
    
    def _update_b_yaml(self, decision, output: Dict[str, Any]) -> None:
        """B.yamlを更新"""
        try:
            b_data = {
                "horizon": {
                    "6M": {"verdict": "保留", "ΔIRRbp": 0},
                    "1Y": {"verdict": "保留", "ΔIRRbp": 0},
                    "3Y": {"verdict": "保留", "ΔIRRbp": 0},
                    "5Y": {"verdict": "保留", "ΔIRRbp": 0}
                },
                "stance": {
                    "decision": decision.decision.value,
                    "size": "Low" if decision.size_pct < 1.0 else "Med" if decision.size_pct < 3.0 else "High",
                    "reason": decision.reason
                },
                "decision_gates": {
                    "structure_quality": "右肩上がり確認",
                    "slope_quality": "傾きの質確認",
                    "time_profile": "時間軸確認",
                    "time_annotation": "カタリスト確認",
                    "irr_threshold": f"ΔIRR≥+300–500bp"
                },
                "hold_override_gate": "S高×Q中以上×ΔIRR≥+700bp → Pilot Buy（1/4）",
                "kpi_watch": output["decision"]["kpi_watch"],
                "diff_summary": f"DI={decision.di_score:.2f}で{decision.decision.value}判定",
                "t1_coverage_targets": {
                    "6M": "≥70%",
                    "1Y": "≥80%",
                    "3Y_plus": "≥90%"
                }
            }
            
            with open(self.b_file, "w", encoding="utf-8") as f:
                yaml.dump(b_data, f, default_flow_style=False, allow_unicode=True)
            
        except Exception as e:
            print(f"B.yaml更新エラー: {e}")
    
    def _update_c_yaml(self) -> None:
        """C.yamlを更新"""
        try:
            c_data = {
                "tests": {
                    "time_off": "〔Time〕無効化テスト",
                    "delay_plus_0_5Q": "t1+0.5Qテスト",
                    "alignment_sales_pnl": "売上↔GM/CF/在庫の整合"
                }
            }
            
            with open(self.c_file, "w", encoding="utf-8") as f:
                yaml.dump(c_data, f, default_flow_style=False, allow_unicode=True)
            
        except Exception as e:
            print(f"C.yaml更新エラー: {e}")
    
    def _update_facts_md(self, axis_scores: List) -> None:
        """facts.mdを更新"""
        try:
            facts_content = ["# T1確定事実（AUST満たすもののみ）", ""]
            
            for i, score in enumerate(axis_scores):
                axis_name = ["①長期EV確度", "②長期EV勾配", "③バリュエーション＋認知ギャップ"][i]
                for fact in score.t1_facts:
                    facts_content.append(
                        f"[{fact.asof}][T1-F][Core{axis_name}] \"{fact.verbatim}\" (impact: {fact.kpi}) <{fact.url}>"
                    )
            
            with open(self.facts_file, "w", encoding="utf-8") as f:
                f.write("\n".join(facts_content))
            
        except Exception as e:
            print(f"facts.md更新エラー: {e}")
    
    def _update_triage_json(self, lint_report: Dict[str, Any]) -> None:
        """triage.jsonを更新"""
        try:
            triage_data = {
                "as_of": datetime.now().strftime("%Y-%m-%d"),
                "CONFIRMED": [
                    {
                        "kpi": fact.kpi,
                        "value": fact.value,
                        "unit": fact.unit,
                        "asof": fact.asof,
                        "tag": "T1-core",
                        "url": fact.url
                    }
                    for fact in self.evaluator.t1_facts
                ],
                "UNCERTAIN": [],
                "HYPOTHESES": []
            }
            
            with open(self.triage_file, "w", encoding="utf-8") as f:
                json.dump(triage_data, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            print(f"triage.json更新エラー: {e}")

def main():
    """メイン実行"""
    if len(sys.argv) < 2:
        print("使用方法: python ahf_v073_integrated.py <TICKER> [DATA_DIR]")
        print("例: python ahf_v073_integrated.py WOLF tickers")
        sys.exit(1)
    
    ticker = sys.argv[1].upper()
    data_dir = sys.argv[2] if len(sys.argv) > 2 else "tickers"
    
    # 統合実行
    integrated = AHFv073Integrated(ticker, data_dir)
    result = integrated.run_evaluation()
    
    if "error" in result:
        print(f"実行失敗: {result['error']}")
        sys.exit(1)
    else:
        print("\n=== AHF v0.7.3 統合評価完了 ===")
        print(f"ティッカー: {ticker}")
        print(f"判定: {result['decision']['decision_type']}")
        print(f"DI: {result['decision']['di_score']:.2f}")

if __name__ == "__main__":
    main()
