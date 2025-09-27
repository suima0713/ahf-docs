#!/usr/bin/env python3
"""
AHF v0.7.3 MVP-4+出力スキーマ
Purpose: 固定3軸評価結果の統一出力フォーマット
"""

import json
import yaml
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum

class InterruptType(Enum):
    """割り込みタイプ"""
    A3_UNEXPLAINED = "A3_UNEXPLAINED"
    BALANCE_WEAK = "BALANCE_WEAK"
    ITEM1A_CHANGE = "ITEM1A_CHANGE"
    ANCHOR_FAIL = "ANCHOR_FAIL"

class GateColor(Enum):
    """ゲート色"""
    GREEN = "Green"
    AMBER = "Amber"
    RED = "Red"

@dataclass
class DirectionProbability:
    """方向確率"""
    up_pct: float
    down_pct: float

@dataclass
class AnchorBackup:
    """アンカーバックアップ"""
    pageno: Optional[int]
    quote: str
    hash: str
    source_type: str

@dataclass
class DataGap:
    """データギャップ"""
    reason: str
    impact: str
    ttl_days: int

@dataclass
class AutoChecks:
    """自動チェック結果"""
    alpha4_gate_pass: bool
    alpha5_math_pass: bool
    anchor_lint_pass: bool
    messages: List[str]

@dataclass
class ValuationOverlay:
    """バリュエーションオーバーレイ"""
    status: str  # Green/Amber/Red
    ev_sales_fwd: float
    rule_of_40: float
    hysteresis: Dict[str, float]

@dataclass
class AxisResult:
    """軸結果"""
    axis_name: str  # ①長期EV確度/②長期EV勾配/③バリュエーション＋認知ギャップ
    score: int  # ★1-5
    confidence: int  # 確信度 45-95%
    market_embedded: bool
    alpha_opacity: float
    direction_up_pct: float
    direction_down_pct: float
    t1_facts_count: int
    edge_facts_count: int
    representative_kpi: str
    t1_evidence: str  # T1根拠
    current_snapshot: str  # 現状スナップ

@dataclass
class DecisionResult:
    """意思決定結果"""
    decision_type: str  # GO/WATCH/NO-GO
    size_pct: float
    di_score: float
    reason: str
    kpi_watch: List[Dict[str, Any]]

@dataclass
class MVP4Output:
    """MVP-4+出力スキーマ"""
    # ヘッダー（必須）
    purpose: str
    mvp: str
    
    # 基本情報
    evaluation_date: str
    ticker: str
    
    # 固定3軸結果
    axes: List[AxisResult]
    
    # 意思決定
    decision: DecisionResult
    
    # バリュエーションオーバーレイ
    valuation_overlay: ValuationOverlay
    
    # 方向確率
    direction_prob_up_pct: float
    direction_prob_down_pct: float
    
    # ゲート色
    gate_color: str
    
    # アンカーバックアップ
    anchor_backup: Optional[AnchorBackup]
    
    # データギャップ
    data_gap: Optional[DataGap]
    gap_reason: Optional[Dict[str, str]]
    
    # 自動チェック
    auto_checks: AutoChecks
    
    # デュアルアンカーステータス
    dual_anchor_status: str  # CONFIRMED/PENDING_SEC/SINGLE
    
    # スコア
    rss_score: Optional[float]
    alpha3_score: Optional[float]
    alpha5_score: Optional[float]
    
    # 割り込み
    interrupts: List[str]
    
    # 追加メタデータ
    find_path: Optional[str]
    turbo_applied: bool
    core_priority: bool

class MVP4OutputGenerator:
    """MVP-4+出力ジェネレーター"""
    
    def __init__(self):
        self.output_schema = MVP4Output(
            purpose="投資判断に直結する固定3軸で評価する",
            mvp="①②③の名称と順序を毎回固定／T1で確証／定型テーブル＋1行要約で即時出力",
            evaluation_date="",
            ticker="",
            axes=[],
            decision=DecisionResult("", 0.0, 0.0, "", []),
            valuation_overlay=ValuationOverlay("", 0.0, 0.0, {}),
            direction_prob_up_pct=0.0,
            direction_prob_down_pct=0.0,
            gate_color="",
            anchor_backup=None,
            data_gap=None,
            gap_reason=None,
            auto_checks=AutoChecks(False, False, False, []),
            dual_anchor_status="",
            rss_score=None,
            alpha3_score=None,
            alpha5_score=None,
            interrupts=[],
            find_path=None,
            turbo_applied=False,
            core_priority=True
        )
    
    def generate_axis_result(self, axis_name: str, score: int, confidence: int, 
                           t1_facts: List[Dict], edge_facts: List[Dict] = None) -> AxisResult:
        """軸結果を生成"""
        edge_facts = edge_facts or []
        
        # 代表KPIを抽出
        representative_kpi = self._extract_representative_kpi(t1_facts)
        
        # T1根拠を生成
        t1_evidence = self._generate_t1_evidence(t1_facts)
        
        # 現状スナップを生成
        current_snapshot = self._generate_current_snapshot(t1_facts)
        
        # 方向確率を計算
        direction_up, direction_down = self._calculate_direction_probability(score, confidence)
        
        return AxisResult(
            axis_name=axis_name,
            score=score,
            confidence=confidence,
            market_embedded=True,
            alpha_opacity=0.3,
            direction_up_pct=direction_up,
            direction_down_pct=direction_down,
            t1_facts_count=len(t1_facts),
            edge_facts_count=len(edge_facts),
            representative_kpi=representative_kpi,
            t1_evidence=t1_evidence,
            current_snapshot=current_snapshot
        )
    
    def generate_decision_result(self, di_score: float, axis_scores: List[int]) -> DecisionResult:
        """意思決定結果を生成"""
        # 意思決定タイプ
        if di_score >= 0.55:
            decision_type = "GO"
            size_pct = min(5.0, 1.2 * di_score)
        elif di_score >= 0.32:
            decision_type = "WATCH"
            size_pct = 0.5
        else:
            decision_type = "NO-GO"
            size_pct = 0.0
        
        # 理由生成
        reason = f"DI={di_score:.2f}, LEC={axis_scores[0]}/5, NES={axis_scores[1]}/5, VRG={axis_scores[2]}/5"
        
        # KPI×2設定
        kpi_watch = [
            {"name": "coverage_ratio", "current": 0.0, "target": "≥0.90"},
            {"name": "contract_liabilities_roll", "current": 0.0, "target": "match"}
        ]
        
        return DecisionResult(
            decision_type=decision_type,
            size_pct=size_pct,
            di_score=di_score,
            reason=reason,
            kpi_watch=kpi_watch
        )
    
    def generate_valuation_overlay(self, ev_sales_fwd: float, rule_of_40: float) -> ValuationOverlay:
        """バリュエーションオーバーレイを生成"""
        # 色分け判定
        if ev_sales_fwd <= 10 and rule_of_40 >= 40:
            status = "Green"
        elif (ev_sales_fwd <= 14 and rule_of_40 >= 35) or (ev_sales_fwd <= 10 and rule_of_40 >= 35):
            status = "Amber"
        else:
            status = "Red"
        
        return ValuationOverlay(
            status=status,
            ev_sales_fwd=ev_sales_fwd,
            rule_of_40=rule_of_40,
            hysteresis={
                "evsales_delta": 0.5,
                "ro40_delta": 2.0,
                "upgrade_factor": 1.2
            }
        )
    
    def generate_auto_checks(self, t1_facts: List[Dict], edge_facts: List[Dict] = None) -> AutoChecks:
        """自動チェック結果を生成"""
        edge_facts = edge_facts or []
        
        # Alpha4ゲートチェック
        alpha4_pass = self._check_alpha4_gate(t1_facts)
        
        # Alpha5数理チェック
        alpha5_pass = self._check_alpha5_math(t1_facts)
        
        # AnchorLintチェック
        anchor_lint_pass = self._check_anchor_lint(t1_facts)
        
        # メッセージ生成
        messages = []
        if not alpha4_pass:
            messages.append("Alpha4: RPO coverage < 11.0")
        if not alpha5_pass:
            messages.append("Alpha5: 数理整合性NG")
        if not anchor_lint_pass:
            messages.append("AnchorLint: 逐語>25語またはアンカー形式不正")
        
        return AutoChecks(
            alpha4_gate_pass=alpha4_pass,
            alpha5_math_pass=alpha5_pass,
            anchor_lint_pass=anchor_lint_pass,
            messages=messages
        )
    
    def generate_interrupts(self, t1_facts: List[Dict]) -> List[str]:
        """割り込みを生成"""
        interrupts = []
        
        # A3_UNEXPLAINEDチェック
        if self._check_a3_unexplained(t1_facts):
            interrupts.append("A3_UNEXPLAINED")
        
        # BALANCE_WEAKチェック
        if self._check_balance_weak(t1_facts):
            interrupts.append("BALANCE_WEAK")
        
        # ITEM1A_CHANGEチェック
        if self._check_item1a_change(t1_facts):
            interrupts.append("ITEM1A_CHANGE")
        
        # ANCHOR_FAILチェック
        if self._check_anchor_fail(t1_facts):
            interrupts.append("ANCHOR_FAIL")
        
        return interrupts
    
    def generate_complete_output(self, ticker: str, axis_results: List[AxisResult], 
                               decision: DecisionResult, valuation: ValuationOverlay,
                               t1_facts: List[Dict], edge_facts: List[Dict] = None) -> Dict[str, Any]:
        """完全なMVP-4+出力を生成"""
        edge_facts = edge_facts or []
        
        # 方向確率を計算
        direction_up = sum(axis.direction_up_pct for axis in axis_results) / len(axis_results)
        direction_down = sum(axis.direction_down_pct for axis in axis_results) / len(axis_results)
        
        # ゲート色を決定
        gate_color = self._determine_gate_color(axis_results, valuation)
        
        # 自動チェック
        auto_checks = self.generate_auto_checks(t1_facts, edge_facts)
        
        # 割り込み
        interrupts = self.generate_interrupts(t1_facts)
        
        # デュアルアンカーステータス
        dual_anchor_status = self._determine_dual_anchor_status(t1_facts)
        
        # データギャップチェック
        data_gap, gap_reason = self._check_data_gaps(t1_facts)
        
        # スコア計算
        rss_score = self._calculate_rss_score(axis_results)
        alpha3_score = self._calculate_alpha3_score(axis_results)
        alpha5_score = self._calculate_alpha5_score(axis_results)
        
        # 出力生成
        output = {
            "purpose": self.output_schema.purpose,
            "mvp": self.output_schema.mvp,
            "evaluation_date": datetime.now().strftime("%Y-%m-%d"),
            "ticker": ticker,
            "axes": [asdict(axis) for axis in axis_results],
            "decision": asdict(decision),
            "valuation_overlay": asdict(valuation),
            "direction_prob_up_pct": direction_up,
            "direction_prob_down_pct": direction_down,
            "gate_color": gate_color,
            "anchor_backup": None,  # 必要に応じて設定
            "data_gap": asdict(data_gap) if data_gap else None,
            "gap_reason": gap_reason,
            "auto_checks": asdict(auto_checks),
            "dual_anchor_status": dual_anchor_status,
            "rss_score": rss_score,
            "alpha3_score": alpha3_score,
            "alpha5_score": alpha5_score,
            "interrupts": interrupts,
            "find_path": None,  # 必要に応じて設定
            "turbo_applied": len(edge_facts) > 0,
            "core_priority": True
        }
        
        return output
    
    def format_output_table(self, output: Dict[str, Any]) -> str:
        """出力テーブルをフォーマット"""
        table = []
        table.append("=== AHF v0.7.3 固定3軸評価結果 ===")
        table.append(f"Purpose: {output['purpose']}")
        table.append(f"MVP: {output['mvp']}")
        table.append(f"評価日: {output['evaluation_date']}")
        table.append(f"ティッカー: {output['ticker']}")
        table.append("")
        
        # 軸結果テーブル
        table.append("【固定3軸評価】")
        table.append("| 軸 | 代表KPI/根拠(T1) | 現状スナップ | ★/5 | 確信度 | 市場織込み | Alpha不透明度 | 上向/下向(%) |")
        table.append("|---|---|---|---|---|---|---|---|")
        
        for axis in output['axes']:
            table.append(f"| {axis['axis_name']} | {axis['representative_kpi']} | {axis['current_snapshot']} | {axis['score']} | {axis['confidence']}% | {'○' if axis['market_embedded'] else '×'} | {axis['alpha_opacity']:.1f} | {axis['direction_up_pct']:.0f}/{axis['direction_down_pct']:.0f} |")
        
        table.append("")
        
        # 意思決定
        table.append("【意思決定】")
        table.append(f"判定: {output['decision']['decision_type']} (DI={output['decision']['di_score']:.2f})")
        table.append(f"サイズ: {output['decision']['size_pct']:.1f}%")
        table.append(f"理由: {output['decision']['reason']}")
        table.append("")
        
        # バリュエーション
        table.append("【バリュエーション】")
        table.append(f"色: {output['valuation_overlay']['status']}")
        table.append(f"EV/S(Fwd): {output['valuation_overlay']['ev_sales_fwd']:.1f}x")
        table.append(f"Rule of 40: {output['valuation_overlay']['rule_of_40']:.0f}")
        table.append("")
        
        # 自動チェック
        if output['auto_checks']['messages']:
            table.append("【自動チェック警告】")
            for msg in output['auto_checks']['messages']:
                table.append(f"- {msg}")
            table.append("")
        
        # 割り込み
        if output['interrupts']:
            table.append("【割り込み】")
            for interrupt in output['interrupts']:
                table.append(f"- {interrupt}")
            table.append("")
        
        return "\n".join(table)
    
    # ヘルパーメソッド群
    def _extract_representative_kpi(self, t1_facts: List[Dict]) -> str:
        """代表KPIを抽出"""
        if not t1_facts:
            return "n/a"
        
        # 最初のT1事実のKPIを使用
        return t1_facts[0].get("kpi", "n/a")
    
    def _generate_t1_evidence(self, t1_facts: List[Dict]) -> str:
        """T1根拠を生成"""
        if not t1_facts:
            return "T1不足"
        
        # 最初のT1事実の逐語を使用
        verbatim = t1_facts[0].get("verbatim", "")
        return verbatim[:40] + "..." if len(verbatim) > 40 else verbatim
    
    def _generate_current_snapshot(self, t1_facts: List[Dict]) -> str:
        """現状スナップを生成"""
        if not t1_facts:
            return "データ不足"
        
        # 最新のT1事実の値を使用
        latest_fact = t1_facts[0]
        value = latest_fact.get("value", 0)
        unit = latest_fact.get("unit", "")
        return f"{value}{unit}"
    
    def _calculate_direction_probability(self, score: int, confidence: int) -> Tuple[float, float]:
        """方向確率を計算"""
        base_prob = 50.0
        score_adjustment = (score - 3) * 10  # 3を基準に±20%
        confidence_adjustment = (confidence - 70) * 0.5  # 70%を基準に±12.5%
        
        up_prob = min(90, max(10, base_prob + score_adjustment + confidence_adjustment))
        down_prob = 100 - up_prob
        
        return up_prob, down_prob
    
    def _check_alpha4_gate(self, t1_facts: List[Dict]) -> bool:
        """Alpha4ゲートチェック"""
        # RPO/Backlog coverage = (RPO_12M/Quarterly_Rev) × 3
        # Gate ≥ 11.0
        return True  # 実装は簡略化
    
    def _check_alpha5_math(self, t1_facts: List[Dict]) -> bool:
        """Alpha5数理チェック"""
        # OpEx/EBITDA三角測量
        return True  # 実装は簡略化
    
    def _check_anchor_lint(self, t1_facts: List[Dict]) -> bool:
        """AnchorLintチェック"""
        for fact in t1_facts:
            verbatim = fact.get("verbatim", "")
            if len(verbatim.split()) > 25:
                return False
        return True
    
    def _check_a3_unexplained(self, t1_facts: List[Dict]) -> bool:
        """A3_UNEXPLAINEDチェック"""
        return False  # 実装は簡略化
    
    def _check_balance_weak(self, t1_facts: List[Dict]) -> bool:
        """BALANCE_WEAKチェック"""
        return False  # 実装は簡略化
    
    def _check_item1a_change(self, t1_facts: List[Dict]) -> bool:
        """ITEM1A_CHANGEチェック"""
        return False  # 実装は簡略化
    
    def _check_anchor_fail(self, t1_facts: List[Dict]) -> bool:
        """ANCHOR_FAILチェック"""
        return False  # 実装は簡略化
    
    def _determine_gate_color(self, axis_results: List[AxisResult], valuation: ValuationOverlay) -> str:
        """ゲート色を決定"""
        if valuation.status == "Green":
            return "Green"
        elif valuation.status == "Amber":
            return "Amber"
        else:
            return "Red"
    
    def _determine_dual_anchor_status(self, t1_facts: List[Dict]) -> str:
        """デュアルアンカーステータスを決定"""
        sec_count = len([f for f in t1_facts if "sec.gov" in f.get("url", "")])
        if sec_count > 0:
            return "CONFIRMED"
        else:
            return "PENDING_SEC"
    
    def _check_data_gaps(self, t1_facts: List[Dict]) -> Tuple[Optional[DataGap], Optional[Dict[str, str]]]:
        """データギャップをチェック"""
        if len(t1_facts) < 3:
            return DataGap("T1不足", "評価精度低下", 7), {"reason": "T1事実不足", "impact": "評価精度低下"}
        return None, None
    
    def _calculate_rss_score(self, axis_results: List[AxisResult]) -> float:
        """RSSスコアを計算"""
        return sum(axis.score for axis in axis_results) / len(axis_results)
    
    def _calculate_alpha3_score(self, axis_results: List[AxisResult]) -> float:
        """Alpha3スコアを計算"""
        return sum(axis.confidence for axis in axis_results) / len(axis_results)
    
    def _calculate_alpha5_score(self, axis_results: List[AxisResult]) -> float:
        """Alpha5スコアを計算"""
        return sum(axis.alpha_opacity for axis in axis_results) / len(axis_results)

def main():
    """メイン実行"""
    generator = MVP4OutputGenerator()
    
    # サンプルデータ
    sample_t1_facts = [
        {"kpi": "guidance_fy26_mid", "value": 2500, "unit": "USD_millions", "verbatim": "FY26 revenue guidance midpoint $2.5B"},
        {"kpi": "opm_drift", "value": 2.5, "unit": "pp", "verbatim": "Operating margin improved 2.5pp"},
        {"kpi": "backlog_growth", "value": 15, "unit": "%", "verbatim": "Backlog grew 15% quarter-over-quarter"}
    ]
    
    # 軸結果生成
    axis_results = [
        generator.generate_axis_result("①長期EV確度", 4, 80, sample_t1_facts),
        generator.generate_axis_result("②長期EV勾配", 3, 75, sample_t1_facts),
        generator.generate_axis_result("③バリュエーション＋認知ギャップ", 2, 70, sample_t1_facts)
    ]
    
    # 意思決定生成
    decision = generator.generate_decision_result(0.45, [4, 3, 2])
    
    # バリュエーション生成
    valuation = generator.generate_valuation_overlay(12.5, 35)
    
    # 完全出力生成
    output = generator.generate_complete_output("SAMPLE", axis_results, decision, valuation, sample_t1_facts)
    
    # テーブル形式で表示
    table = generator.format_output_table(output)
    print(table)
    
    # JSON形式で保存
    with open("ahf_v073_output.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print("\n出力をahf_v073_output.jsonに保存しました。")

if __name__ == "__main__":
    main()
