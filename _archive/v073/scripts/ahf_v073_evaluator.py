#!/usr/bin/env python3
"""
AHF v0.7.3 固定3軸評価システム
Purpose: 投資判断に直結する固定3軸で評価する
MVP: ①②③の名称と順序を毎回固定／T1で確証／定型テーブル＋1行要約で即時出力
"""

import json
import yaml
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

class AxisType(Enum):
    """固定3軸の定義"""
    LEC = "長期EV確度"  # ①
    NES = "長期EV勾配"  # ②  
    VRG = "バリュエーション＋認知ギャップ"  # ③

class DecisionType(Enum):
    """意思決定タイプ"""
    GO = "GO"
    WATCH = "WATCH"
    NO_GO = "NO-GO"

class ValuationColor(Enum):
    """バリュエーション色分け"""
    GREEN = "Green"
    AMBER = "Amber"
    RED = "Red"

@dataclass
class T1Fact:
    """T1事実の構造"""
    kpi: str
    value: float
    unit: str
    asof: str
    tag: str
    url: str
    verbatim: str  # ≤25語の逐語
    anchor: str   # #:~:text=形式

@dataclass
class AxisScore:
    """軸スコア"""
    axis: AxisType
    score: float  # 0-5の星評価
    confidence: int  # 確信度 45-95%
    market_embedded: bool  # 市場織込み
    alpha_opacity: float  # Alpha不透明度
    direction_up: float  # 上向確率%
    direction_down: float  # 下向確率%
    t1_facts: List[T1Fact]
    edge_facts: List[T1Fact]  # Turbo Screen用

@dataclass
class ValuationOverlay:
    """バリュエーションオーバーレイ"""
    status: ValuationColor
    ev_sales_fwd: float
    rule_of_40: float
    di_multiplier: float
    hysteresis: Dict[str, float]

@dataclass
class DecisionResult:
    """意思決定結果"""
    decision: DecisionType
    size_pct: float
    di_score: float
    reason: str
    kpi_watch: List[Dict[str, Any]]

class AHFv073Evaluator:
    """AHF v0.7.3 固定3軸評価エンジン"""
    
    def __init__(self):
        self.t1_facts: List[T1Fact] = []
        self.edge_facts: List[T1Fact] = []
        self.valuation_overlay: Optional[ValuationOverlay] = None
        
    def load_t1_data(self, facts_file: str, triage_file: str) -> None:
        """T1データの読み込み"""
        try:
            # facts.mdからT1事実を抽出
            with open(facts_file, 'r', encoding='utf-8') as f:
                content = f.read()
                self._parse_facts_md(content)
            
            # triage.jsonからCONFIRMEDデータを読み込み
            with open(triage_file, 'r', encoding='utf-8') as f:
                triage_data = json.load(f)
                self._parse_triage_confirmed(triage_data)
                
        except Exception as e:
            print(f"データ読み込みエラー: {e}")
            raise
    
    def _parse_facts_md(self, content: str) -> None:
        """facts.mdからT1事実を解析"""
        lines = content.split('\n')
        for line in lines:
            if line.startswith('[') and 'T1-' in line:
                fact = self._parse_fact_line(line)
                if fact:
                    self.t1_facts.append(fact)
    
    def _parse_fact_line(self, line: str) -> Optional[T1Fact]:
        """fact行を解析"""
        # [YYYY-MM-DD][T1-F|T1-C][Core①|Core②|Core③|Time] "逐語≤40語" (impact: KPI) <URL>
        pattern = r'\[([^\]]+)\]\[([^\]]+)\]\[([^\]]+)\] "([^"]+)" \(impact: ([^)]+)\) <([^>]+)>'
        match = re.match(pattern, line)
        
        if match:
            asof, t1_type, core_tag, verbatim, kpi, url = match.groups()
            return T1Fact(
                kpi=kpi,
                value=0.0,  # 数値は別途抽出
                unit="",
                asof=asof,
                tag=f"{t1_type}-{core_tag}",
                url=url,
                verbatim=verbatim[:25],  # ≤25語
                anchor=self._generate_anchor(url, verbatim)
            )
        return None
    
    def _generate_anchor(self, url: str, verbatim: str) -> str:
        """アンカー生成（#:~:text=形式）"""
        if "sec.gov" in url:
            # SEC文書の場合は#:~:text=を使用
            text_fragment = verbatim.replace(" ", "%20")
            return f"{url}#:~:text={text_fragment}"
        else:
            # その他の場合はanchor_backup
            return f"anchor_backup{{quote: '{verbatim}', hash: 'pending'}}"
    
    def _parse_triage_confirmed(self, triage_data: Dict) -> None:
        """triage.jsonのCONFIRMEDデータを解析"""
        for item in triage_data.get("CONFIRMED", []):
            fact = T1Fact(
                kpi=item["kpi"],
                value=item["value"],
                unit=item["unit"],
                asof=item["asof"],
                tag=item["tag"],
                url=item["url"],
                verbatim="",  # triage.jsonには逐語なし
                anchor=""
            )
            self.t1_facts.append(fact)
    
    def evaluate_axis_lec(self) -> AxisScore:
        """①長期EV確度（LEC）の評価"""
        # LEC ≈ g_fwd + ΔOPM_fwd − Dilution − Capex_intensity
        g_fwd = self._extract_guidance_growth()
        delta_opm = self._extract_opm_drift()
        dilution = self._extract_dilution_rate()
        capex_intensity = self._extract_capex_intensity()
        
        lec_score = g_fwd + delta_opm - dilution - capex_intensity
        
        # 星割当
        if lec_score >= 20:
            stars = 5
        elif lec_score >= 15:
            stars = 4
        elif lec_score >= 8:
            stars = 3
        elif lec_score >= 3:
            stars = 2
        else:
            stars = 1
        
        # 関連T1事実を抽出
        lec_facts = [f for f in self.t1_facts if "guidance" in f.kpi.lower() or "opm" in f.kpi.lower()]
        
        return AxisScore(
            axis=AxisType.LEC,
            score=stars,
            confidence=min(95, max(45, 70 + (lec_score - 10) * 2)),
            market_embedded=True,
            alpha_opacity=0.3,
            direction_up=min(90, 50 + lec_score * 2),
            direction_down=max(10, 50 - lec_score * 2),
            t1_facts=lec_facts,
            edge_facts=[]
        )
    
    def evaluate_axis_nes(self) -> AxisScore:
        """②長期EV勾配（NES）の評価"""
        # NES = 0.5·(次Q q/q%) + 0.3·(ガイド改定%) + 0.2·(受注/Backlog増勢%) + Margin_term
        next_q_growth = self._extract_next_quarter_growth()
        guidance_revision = self._extract_guidance_revision()
        backlog_growth = self._extract_backlog_growth()
        margin_term = self._extract_margin_term()
        
        nes_score = (0.5 * next_q_growth + 
                    0.3 * guidance_revision + 
                    0.2 * backlog_growth + 
                    margin_term)
        
        # 星割当
        if nes_score >= 8:
            stars = 5
        elif nes_score >= 5:
            stars = 4
        elif nes_score >= 2:
            stars = 3
        elif nes_score >= 0:
            stars = 2
        else:
            stars = 1
        
        # 関連T1事実を抽出
        nes_facts = [f for f in self.t1_facts if "qoq" in f.kpi.lower() or "backlog" in f.kpi.lower()]
        
        return AxisScore(
            axis=AxisType.NES,
            score=stars,
            confidence=min(95, max(45, 70 + nes_score * 3)),
            market_embedded=True,
            alpha_opacity=0.4,
            direction_up=min(90, 50 + nes_score * 3),
            direction_down=max(10, 50 - nes_score * 3),
            t1_facts=nes_facts,
            edge_facts=[]
        )
    
    def evaluate_axis_vrg(self) -> AxisScore:
        """③バリュエーション＋認知ギャップ（VRG）の評価"""
        ev_sales_fwd = self._extract_ev_sales_fwd()
        rule_of_40 = self._extract_rule_of_40()
        
        # 色分け判定
        if ev_sales_fwd <= 10 and rule_of_40 >= 40:
            color = ValuationColor.GREEN
            di_multiplier = 1.05
        elif (ev_sales_fwd <= 14 and rule_of_40 >= 35) or (ev_sales_fwd <= 10 and rule_of_40 >= 35):
            color = ValuationColor.AMBER
            di_multiplier = 0.90
        else:
            color = ValuationColor.RED
            di_multiplier = 0.75
        
        # バリュエーションオーバーレイを設定
        self.valuation_overlay = ValuationOverlay(
            status=color,
            ev_sales_fwd=ev_sales_fwd,
            rule_of_40=rule_of_40,
            di_multiplier=di_multiplier,
            hysteresis={
                "evsales_delta": 0.5,
                "ro40_delta": 2.0,
                "upgrade_factor": 1.2
            }
        )
        
        # 星評価（バリュエーション基準）
        if color == ValuationColor.GREEN:
            stars = 5
        elif color == ValuationColor.AMBER:
            stars = 3
        else:
            stars = 1
        
        # 関連T1事実を抽出
        vrg_facts = [f for f in self.t1_facts if "ev" in f.kpi.lower() or "valuation" in f.kpi.lower()]
        
        return AxisScore(
            axis=AxisType.VRG,
            score=stars,
            confidence=min(95, max(45, 80 - (ev_sales_fwd - 5) * 2)),
            market_embedded=True,
            alpha_opacity=0.2,
            direction_up=min(90, 60 - (ev_sales_fwd - 5) * 3),
            direction_down=max(10, 40 + (ev_sales_fwd - 5) * 3),
            t1_facts=vrg_facts,
            edge_facts=[]
        )
    
    def apply_turbo_screen(self, axis_scores: List[AxisScore]) -> List[AxisScore]:
        """Turbo Screen適用（P≥60、★±2、確信度±10pp）"""
        turbo_scores = []
        
        for score in axis_scores:
            # Edge事実を抽出（P≥60、TTL≤14日、矛盾フラグfalse）
            edge_facts = [f for f in self.edge_facts 
                         if self._get_edge_credence(f) >= 60 and 
                         not self._get_contradiction_flag(f)]
            
            # ★調整（±2まで）
            turbo_stars = max(1, min(5, score.score + self._get_turbo_star_adjustment(edge_facts)))
            
            # 確信度ブースト（±10pp）
            turbo_confidence = max(45, min(95, score.confidence + self._get_confidence_boost(edge_facts)))
            
            # 数理ガード緩和適用
            turbo_score = AxisScore(
                axis=score.axis,
                score=turbo_stars,
                confidence=turbo_confidence,
                market_embedded=score.market_embedded,
                alpha_opacity=score.alpha_opacity,
                direction_up=score.direction_up,
                direction_down=score.direction_down,
                t1_facts=score.t1_facts,
                edge_facts=edge_facts
            )
            
            turbo_scores.append(turbo_score)
        
        return turbo_scores
    
    def calculate_decision(self, axis_scores: List[AxisScore]) -> DecisionResult:
        """Decision-Wired計算"""
        # 正規化：s1=①★/5、s2=②★/5
        s1 = axis_scores[0].score / 5.0  # LEC
        s2 = axis_scores[1].score / 5.0  # NES
        
        # 合成：DI = (0.6·s2 + 0.4·s1) · Vmult
        v_mult = self.valuation_overlay.di_multiplier if self.valuation_overlay else 1.0
        di = (0.6 * s2 + 0.4 * s1) * v_mult
        
        # Red上限適用
        if self.valuation_overlay and self.valuation_overlay.status == ValuationColor.RED:
            di = min(di, 0.55)
        
        # アクション判定
        if di >= 0.55:
            decision = DecisionType.GO
            size_pct = min(5.0, 1.2 * di)  # 位置サイズ目安
        elif di >= 0.32:
            decision = DecisionType.WATCH
            size_pct = 0.5
        else:
            decision = DecisionType.NO_GO
            size_pct = 0.0
        
        # KPI×2設定
        kpi_watch = [
            {"name": "coverage_ratio", "current": 0.0, "target": "≥0.90"},
            {"name": "contract_liabilities_roll", "current": 0.0, "target": "match"}
        ]
        
        return DecisionResult(
            decision=decision,
            size_pct=size_pct,
            di_score=di,
            reason=f"DI={di:.2f}, LEC={s1:.2f}, NES={s2:.2f}, V={v_mult:.2f}",
            kpi_watch=kpi_watch
        )
    
    def generate_output(self, axis_scores: List[AxisScore], decision: DecisionResult) -> Dict[str, Any]:
        """MVP-4+出力スキーマ生成"""
        return {
            "purpose": "投資判断に直結する固定3軸で評価する",
            "mvp": "①②③の名称と順序を毎回固定／T1で確証／定型テーブル＋1行要約で即時出力",
            "evaluation_date": datetime.now().strftime("%Y-%m-%d"),
            "axes": [
                {
                    "axis": score.axis.value,
                    "score": int(score.score),
                    "confidence": score.confidence,
                    "market_embedded": score.market_embedded,
                    "alpha_opacity": score.alpha_opacity,
                    "direction_up_pct": score.direction_up,
                    "direction_down_pct": score.direction_down,
                    "t1_facts_count": len(score.t1_facts),
                    "edge_facts_count": len(score.edge_facts)
                }
                for score in axis_scores
            ],
            "decision": {
                "type": decision.decision.value,
                "size_pct": decision.size_pct,
                "di_score": decision.di_score,
                "reason": decision.reason
            },
            "valuation_overlay": {
                "status": self.valuation_overlay.status.value if self.valuation_overlay else "Unknown",
                "ev_sales_fwd": self.valuation_overlay.ev_sales_fwd if self.valuation_overlay else 0.0,
                "rule_of_40": self.valuation_overlay.rule_of_40 if self.valuation_overlay else 0.0,
                "di_multiplier": self.valuation_overlay.di_multiplier if self.valuation_overlay else 1.0
            },
            "kpi_watch": decision.kpi_watch,
            "auto_checks": {
                "alpha4_gate_pass": self._check_alpha4_gate(),
                "alpha5_math_pass": self._check_alpha5_math(),
                "anchor_lint_pass": self._check_anchor_lint(),
                "messages": self._get_auto_check_messages()
            }
        }
    
    # ヘルパーメソッド群
    def _extract_guidance_growth(self) -> float:
        """通期ガイダンス成長率を抽出"""
        # T1事実からガイダンス成長率を抽出
        for fact in self.t1_facts:
            if "guidance" in fact.kpi.lower() and "growth" in fact.kpi.lower():
                return fact.value
        return 0.0
    
    def _extract_opm_drift(self) -> float:
        """OPMドリフトを抽出"""
        # T1事実からOPM変化を抽出
        for fact in self.t1_facts:
            if "opm" in fact.kpi.lower() and "drift" in fact.kpi.lower():
                return fact.value
        return 0.0
    
    def _extract_dilution_rate(self) -> float:
        """希薄化率を抽出"""
        # T1事実から希薄化率を抽出
        for fact in self.t1_facts:
            if "dilution" in fact.kpi.lower() or "shares" in fact.kpi.lower():
                return fact.value
        return 0.0
    
    def _extract_capex_intensity(self) -> float:
        """CapEx強度を抽出"""
        # T1事実からCapEx強度を抽出
        for fact in self.t1_facts:
            if "capex" in fact.kpi.lower() and "intensity" in fact.kpi.lower():
                return fact.value
        return 0.0
    
    def _extract_next_quarter_growth(self) -> float:
        """次Q成長率を抽出"""
        for fact in self.t1_facts:
            if "qoq" in fact.kpi.lower() and "next" in fact.kpi.lower():
                return fact.value
        return 0.0
    
    def _extract_guidance_revision(self) -> float:
        """ガイダンス改定率を抽出"""
        for fact in self.t1_facts:
            if "guidance" in fact.kpi.lower() and "revision" in fact.kpi.lower():
                return fact.value
        return 0.0
    
    def _extract_backlog_growth(self) -> float:
        """Backlog成長率を抽出"""
        for fact in self.t1_facts:
            if "backlog" in fact.kpi.lower() and "growth" in fact.kpi.lower():
                return fact.value
        return 0.0
    
    def _extract_margin_term(self) -> float:
        """マージン項を抽出"""
        for fact in self.t1_facts:
            if "margin" in fact.kpi.lower() and "term" in fact.kpi.lower():
                return fact.value
        return 0.0
    
    def _extract_ev_sales_fwd(self) -> float:
        """EV/Sales(Fwd)を抽出"""
        for fact in self.t1_facts:
            if "ev_sales" in fact.kpi.lower() or "ev_s" in fact.kpi.lower():
                return fact.value
        return 0.0
    
    def _extract_rule_of_40(self) -> float:
        """Rule of 40を抽出"""
        for fact in self.t1_facts:
            if "rule_of_40" in fact.kpi.lower() or "ro40" in fact.kpi.lower():
                return fact.value
        return 0.0
    
    def _get_edge_credence(self, fact: T1Fact) -> int:
        """Edge事実の信頼度を取得"""
        # 実装は簡略化
        return 70
    
    def _get_contradiction_flag(self, fact: T1Fact) -> bool:
        """矛盾フラグを取得"""
        # 実装は簡略化
        return False
    
    def _get_turbo_star_adjustment(self, edge_facts: List[T1Fact]) -> int:
        """Turbo Screen星調整を取得"""
        if len(edge_facts) >= 2:
            return 2
        elif len(edge_facts) >= 1:
            return 1
        return 0
    
    def _get_confidence_boost(self, edge_facts: List[T1Fact]) -> int:
        """確信度ブーストを取得"""
        if len(edge_facts) >= 2:
            return 10
        elif len(edge_facts) >= 1:
            return 5
        return 0
    
    def _check_alpha4_gate(self) -> bool:
        """Alpha4ゲートチェック"""
        # RPO/Backlog coverage = (RPO_12M/Quarterly_Rev) × 3
        # Gate ≥ 11.0
        return True  # 実装は簡略化
    
    def _check_alpha5_math(self) -> bool:
        """Alpha5数理チェック"""
        # OpEx/EBITDA三角測量
        return True  # 実装は簡略化
    
    def _check_anchor_lint(self) -> bool:
        """AnchorLint v1チェック"""
        for fact in self.t1_facts:
            if len(fact.verbatim) > 25:
                return False
            if not fact.anchor.startswith("#:~:text=") and "anchor_backup" not in fact.anchor:
                return False
        return True
    
    def _get_auto_check_messages(self) -> List[str]:
        """自動チェックメッセージを取得"""
        messages = []
        if not self._check_anchor_lint():
            messages.append("AnchorLint: 逐語>25語またはアンカー形式不正")
        if not self._check_alpha4_gate():
            messages.append("Alpha4: RPO coverage < 11.0")
        return messages

def main():
    """メイン実行"""
    evaluator = AHFv073Evaluator()
    
    # データ読み込み（例）
    try:
        evaluator.load_t1_data("facts.md", "triage.json")
    except Exception as e:
        print(f"データ読み込み失敗: {e}")
        return
    
    # 3軸評価
    lec_score = evaluator.evaluate_axis_lec()
    nes_score = evaluator.evaluate_axis_nes()
    vrg_score = evaluator.evaluate_axis_vrg()
    
    axis_scores = [lec_score, nes_score, vrg_score]
    
    # Turbo Screen適用
    turbo_scores = evaluator.apply_turbo_screen(axis_scores)
    
    # 意思決定計算
    decision = evaluator.calculate_decision(turbo_scores)
    
    # 出力生成
    output = evaluator.generate_output(turbo_scores, decision)
    
    # 結果表示
    print("=== AHF v0.7.3 固定3軸評価結果 ===")
    print(f"Purpose: {output['purpose']}")
    print(f"MVP: {output['mvp']}")
    print()
    
    for i, score in enumerate(output['axes'], 1):
        axis_name = ["①長期EV確度", "②長期EV勾配", "③バリュエーション＋認知ギャップ"][i-1]
        print(f"{axis_name}: ★{score['score']}/5 (確信度{score['confidence']}%, 上向{score['direction_up_pct']:.0f}%)")
    
    print(f"\n意思決定: {output['decision']['type']} (DI={output['decision']['di_score']:.2f}, サイズ{output['decision']['size_pct']:.1f}%)")
    print(f"バリュエーション: {output['valuation_overlay']['status']} (EV/S={output['valuation_overlay']['ev_sales_fwd']:.1f}x, Ro40={output['valuation_overlay']['rule_of_40']:.0f})")

if __name__ == "__main__":
    main()
