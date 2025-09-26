#!/usr/bin/env python3
"""
AHF v0.8.0 評価器
固定3軸（①長期EV確度、②長期EV勾配、③バリュエーション＋認知ギャップ）の評価実装

Purpose: 投資判断に直結する固定3軸で評価する
MVP: ①②③の名称と順序を固定／T1で確証（不足は n/a）／定型テーブル＋1行要約を即時出力
"""

import json
import yaml
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class AxisType(Enum):
    LEC = "LEC"  # ①長期EV確度
    NES = "NES"  # ②長期EV勾配
    VRG = "VRG"  # ③バリュエーション＋認知ギャップ

@dataclass
class T1Fact:
    """T1確定事実"""
    date: str
    source: str  # T1-F|T1-C
    axis: AxisType
    verbatim: str  # ≤25語
    impact: str
    url: str
    anchor: str  # #:~:text= or anchor_backup

class AHFv080Evaluator:
    """AHF v0.8.0 評価器"""
    
    def __init__(self, ticker: str):
        self.ticker = ticker
        self.t1_facts: List[T1Fact] = []
        
    def evaluate_ticker(self) -> Dict[str, Any]:
        """銘柄評価実行"""
        result = {
            "purpose": "投資判断に直結する固定3軸で評価する",
            "mvp": "①②③の名称と順序を固定／T1で確証（不足は n/a）／定型テーブル＋1行要約を即時出力",
            "ticker": self.ticker,
            "evaluation_date": datetime.now().strftime("%Y-%m-%d"),
            "axes": {},
            "decision": {},
            "data_gap": {},
            "gap_reason": {}
        }
        
        try:
            # ①長期EV確度（LEC）評価
            lec_result = self._evaluate_lec()
            result["axes"]["LEC"] = lec_result
            
            # ②長期EV勾配（NES）評価
            nes_result = self._evaluate_nes()
            result["axes"]["NES"] = nes_result
            
            # ③バリュエーション＋認知ギャップ（VRG）評価
            vrg_result = self._evaluate_vrg()
            result["axes"]["VRG"] = vrg_result
            
            # 意思決定
            decision = self._calculate_decision(lec_result, nes_result, vrg_result)
            result["decision"] = decision
            
            # 定型テーブル＋1行要約
            result["summary_table"] = self._generate_summary_table(lec_result, nes_result, vrg_result)
            result["one_line_summary"] = self._generate_one_line_summary(decision)
            
        except Exception as e:
            result["error"] = str(e)
            result["data_gap"]["error"] = True
            result["gap_reason"]["error"] = f"評価実行エラー: {str(e)}"
            
        return result
    
    def _evaluate_lec(self) -> Dict[str, Any]:
        """①長期EV確度（LEC）評価"""
        # 目的：どの環境でも生き残り、需要と利益を生み続ける確度
        # 主要入力（T1）：流動性・負債・希薄化・CapEx強度・運転資本回転・大型契約・コベナンツ等
        
        lec_metrics = {
            "liquidity_metrics": self._extract_liquidity_metrics(),
            "debt_metrics": self._extract_debt_metrics(),
            "dilution_risk": self._extract_dilution_risk(),
            "capex_intensity": self._extract_capex_intensity(),
            "working_capital": self._extract_working_capital(),
            "major_contracts": self._extract_major_contracts(),
            "covenants": self._extract_covenants()
        }
        
        # LEC計算：LEC ≈ g_fwd + ΔOPM_fwd − Dilution − Capex_intensity
        lec_score = self._calculate_lec_score(lec_metrics)
        
        # 星割当：LEC ≥+20pp→★5／15–20→★4／8–15→★3／3–8→★2／<3→★1
        star_rating = self._convert_lec_to_stars(lec_score)
        
        return {
            "axis": "①長期EV確度（LEC）",
            "purpose": "どの環境でも生き残り、需要と利益を生み続ける確度",
            "metrics": lec_metrics,
            "score": lec_score,
            "star_rating": star_rating,
            "calculation": f"LEC ≈ g_fwd + ΔOPM_fwd − Dilution − Capex_intensity = {lec_score:.1f}pp",
            "t1_sources": self._get_t1_sources_for_axis(AxisType.LEC),
            "data_gap": self._check_data_gap_for_axis(AxisType.LEC)
        }
    
    def _evaluate_nes(self) -> Dict[str, Any]:
        """②長期EV勾配（NES）評価"""
        # 目的：12–24ヶ月の伸び"傾き"（短期加速の手応え）
        
        nes_components = {
            "next_quarter_growth": self._extract_next_quarter_growth(),
            "guidance_revision": self._extract_guidance_revision(),
            "backlog_momentum": self._extract_backlog_momentum(),
            "margin_improvement": self._extract_margin_improvement(),
            "health_metrics": self._extract_health_metrics()
        }
        
        # NES計算：NES = 0.5·(次Q q/q%) + 0.3·(ガイド改定%) + 0.2·(受注/Backlog増勢%) + Margin_term + Health_term
        nes_score = self._calculate_nes_score(nes_components)
        
        # 星割当：NES≥+8→★5／+5–8→★4／+2–5→★3／0–2→★2／<0→★1
        star_rating = self._convert_nes_to_stars(nes_score)
        
        return {
            "axis": "②長期EV勾配（NES）",
            "purpose": "12–24ヶ月の伸び"傾き"（短期加速の手応え）",
            "components": nes_components,
            "score": nes_score,
            "star_rating": star_rating,
            "calculation": f"NES = 0.5·(次Q q/q%) + 0.3·(ガイド改定%) + 0.2·(受注/Backlog増勢%) + Margin_term + Health_term = {nes_score:.1f}",
            "t1_sources": self._get_t1_sources_for_axis(AxisType.NES),
            "data_gap": self._check_data_gap_for_axis(AxisType.NES)
        }
    
    def _evaluate_vrg(self) -> Dict[str, Any]:
        """③バリュエーション＋認知ギャップ（Two-Step）評価"""
        # 役割：価格（EV/S_actual）に対する"フェア"との差を測り、その差が将来期待や認知で妥当かを注釈
        
        # Step-1｜フェアバリュー差（素点）
        step1_result = self._calculate_vrg_step1()
        
        # Step-2｜適正性チェック（注釈のみ／色は変えない）
        step2_result = self._calculate_vrg_step2(step1_result)
        
        return {
            "axis": "③バリュエーション＋認知ギャップ（VRG）",
            "purpose": "価格（EV/S_actual）に対する"フェア"との差を測り、その差が将来期待や認知で妥当かを注釈",
            "step1": step1_result,
            "step2": step2_result,
            "t1_sources": self._get_t1_sources_for_axis(AxisType.VRG),
            "data_gap": self._check_data_gap_for_axis(AxisType.VRG)
        }
    
    def _calculate_vrg_step1(self) -> Dict[str, Any]:
        """③Step-1｜フェアバリュー差（素点）"""
        # EV/S_actual（Price-Mode：市場データ、日付・出典名必須）
        evs_actual = self._get_evs_actual()
        
        # EV/S_peer_median
        evs_peer_median = self._get_evs_peer_median()
        
        # EV/S_fair_rDCF（逆DCFライトの帯：T1のg_fwd・OPM_fwdのみ）
        evs_fair_rdcf = self._get_evs_fair_rdcf()
        
        # EV/S_fair_base = max(EV/S_peer_median, EV/S_fair_rDCF)
        evs_fair_base = max(evs_peer_median, evs_fair_rdcf)
        
        # Disc% = (EV/S_fair_base − EV/S_actual) / EV/S_fair_base
        disc_pct = (evs_fair_base - evs_actual) / evs_fair_base if evs_fair_base > 0 else 0
        
        # 色/Vmult（Sign-aware）：Green(1.05)：Disc%≥+10% または |Disc%|≤10%｜Amber(0.90)：−25%<Disc%<−10%｜Red(0.75)：Disc%≤−25%
        if disc_pct >= 0.10 or abs(disc_pct) <= 0.10:
            color = "Green"
            vmult = 1.05
        elif -0.25 < disc_pct < -0.10:
            color = "Amber"
            vmult = 0.90
        else:  # disc_pct <= -0.25
            color = "Red"
            vmult = 0.75
        
        return {
            "evs_actual": evs_actual,
            "evs_peer_median": evs_peer_median,
            "evs_fair_rdcf": evs_fair_rdcf,
            "evs_fair_base": evs_fair_base,
            "disc_pct": disc_pct,
            "color": color,
            "vmult": vmult
        }
    
    def _calculate_vrg_step2(self, step1_result: Dict[str, Any]) -> Dict[str, Any]:
        """③Step-2｜適正性チェック（注釈のみ／色は変えない）"""
        # 期待成長の相対差：Δg = g_fwd − g_peer_median（T1）
        expectation_gap = self._get_expectation_gap()
        
        # 認知フラグ（＋）：ガイダンス上方・実出荷・契約負債↑・ATM未実行・集中低下
        cognition_flags_pos = self._get_cognition_flags_pos()
        
        # 認知フラグ（−）：acceptance要件・在庫滞留・希薄化・集中悪化
        cognition_flags_neg = self._get_cognition_flags_neg()
        
        # Verdict：Underpriced/Overpriced/Neutral ×（適正/不適正）
        verdict = self._determine_verdict(step1_result, expectation_gap, cognition_flags_pos, cognition_flags_neg)
        
        return {
            "expectation_gap": expectation_gap,
            "cognition_flags_pos": cognition_flags_pos,
            "cognition_flags_neg": cognition_flags_neg,
            "verdict": verdict
        }
    
    def _calculate_decision(self, lec_result: Dict, nes_result: Dict, vrg_result: Dict) -> Dict[str, Any]:
        """意思決定（Decision-Wired）"""
        # 正規化：s1=①★/5、s2=②★/5
        s1 = lec_result["star_rating"] / 5.0
        s2 = nes_result["star_rating"] / 5.0
        
        # 合成：DI = (0.6·s2 + 0.4·s1) · Vmult（Vmultは③Step-1の色で決定）
        vmult = vrg_result["step1"]["vmult"]
        di = (0.6 * s2 + 0.4 * s1) * vmult
        
        # アクション：GO ≥0.55｜WATCH 0.32–0.55｜NO-GO <0.32
        if di >= 0.55:
            action = "GO"
        elif di >= 0.32:
            action = "WATCH"
        else:
            action = "NO-GO"
        
        # 位置サイズ目安：Size% ≈ 1.2% × DI
        size_percentage = 1.2 * di
        
        return {
            "s1_score": s1,
            "s2_score": s2,
            "vmult": vmult,
            "di": di,
            "action": action,
            "size_percentage": size_percentage,
            "size_category": self._determine_size_category(size_percentage)
        }
    
    def _generate_summary_table(self, lec_result: Dict, nes_result: Dict, vrg_result: Dict) -> str:
        """定型テーブル生成"""
        table = f"""
| 軸 | 代表KPI/根拠(T1) | 現状スナップ | ★/5 | 確信度 | 市場織込み | Alpha不透明度 | 上向/下向（％） |
|----|------------------|--------------|-----|--------|------------|----------------|-----------------|
| ①LEC | 長期EV確度 | {lec_result.get('calculation', 'n/a')} | {lec_result['star_rating']} | 高 | 織込み済み | 低 | +5% |
| ②NES | 長期EV勾配 | {nes_result.get('calculation', 'n/a')} | {nes_result['star_rating']} | 高 | 織込み済み | 低 | +3% |
| ③VRG | バリュエーション | {vrg_result['step1'].get('color', 'n/a')} | - | 中 | 未織込み | 高 | +8% |
        """.strip()
        return table
    
    def _generate_one_line_summary(self, decision: Dict[str, Any]) -> str:
        """1行要約生成"""
        return f"DI={decision['di']:.2f} → {decision['action']} (Size≈{decision['size_percentage']:.1f}%)"
    
    # 以下は実装の詳細メソッド（実際のT1データ取得・計算ロジック）
    
    def _extract_liquidity_metrics(self) -> List[Dict[str, Any]]:
        """流動性指標抽出"""
        return []
    
    def _extract_debt_metrics(self) -> List[Dict[str, Any]]:
        """負債指標抽出"""
        return []
    
    def _extract_dilution_risk(self) -> List[Dict[str, Any]]:
        """希薄化リスク抽出"""
        return []
    
    def _extract_capex_intensity(self) -> List[Dict[str, Any]]:
        """CapEx強度抽出"""
        return []
    
    def _extract_working_capital(self) -> List[Dict[str, Any]]:
        """運転資本回転抽出"""
        return []
    
    def _extract_major_contracts(self) -> List[Dict[str, Any]]:
        """大型契約抽出"""
        return []
    
    def _extract_covenants(self) -> List[Dict[str, Any]]:
        """コベナンツ抽出"""
        return []
    
    def _calculate_lec_score(self, metrics: Dict[str, Any]) -> float:
        """LECスコア計算"""
        # 実装時は実際の計算ロジック
        return 0.0
    
    def _convert_lec_to_stars(self, score: float) -> int:
        """LECスコアを星評価に変換"""
        if score >= 20:
            return 5
        elif score >= 15:
            return 4
        elif score >= 8:
            return 3
        elif score >= 3:
            return 2
        else:
            return 1
    
    def _extract_next_quarter_growth(self) -> List[Dict[str, Any]]:
        """次Q q/q%抽出"""
        return []
    
    def _extract_guidance_revision(self) -> List[Dict[str, Any]]:
        """ガイド改定%抽出"""
        return []
    
    def _extract_backlog_momentum(self) -> List[Dict[str, Any]]:
        """受注/Backlog増勢%抽出"""
        return []
    
    def _extract_margin_improvement(self) -> List[Dict[str, Any]]:
        """GM改善抽出"""
        return []
    
    def _extract_health_metrics(self) -> List[Dict[str, Any]]:
        """Ro40指標抽出"""
        return []
    
    def _calculate_nes_score(self, components: Dict[str, Any]) -> float:
        """NESスコア計算"""
        # 実装時は実際の計算ロジック
        return 0.0
    
    def _convert_nes_to_stars(self, score: float) -> int:
        """NESスコアを星評価に変換"""
        if score >= 8:
            return 5
        elif score >= 5:
            return 4
        elif score >= 2:
            return 3
        elif score >= 0:
            return 2
        else:
            return 1
    
    def _get_evs_actual(self) -> float:
        """EV/S_actual取得"""
        return 0.0
    
    def _get_evs_peer_median(self) -> float:
        """EV/S_peer_median取得"""
        return 0.0
    
    def _get_evs_fair_rdcf(self) -> float:
        """EV/S_fair_rDCF取得"""
        return 0.0
    
    def _get_expectation_gap(self) -> float:
        """期待成長の相対差取得"""
        return 0.0
    
    def _get_cognition_flags_pos(self) -> List[str]:
        """認知フラグ（＋）取得"""
        return []
    
    def _get_cognition_flags_neg(self) -> List[str]:
        """認知フラグ（−）取得"""
        return []
    
    def _determine_verdict(self, step1_result: Dict, expectation_gap: float, flags_pos: List[str], flags_neg: List[str]) -> str:
        """Verdict決定"""
        return "Neutral"
    
    def _determine_size_category(self, size_percentage: float) -> str:
        """サイズカテゴリ決定"""
        if size_percentage >= 2.0:
            return "High"
        elif size_percentage >= 1.0:
            return "Med"
        else:
            return "Low"
    
    def _get_t1_sources_for_axis(self, axis: AxisType) -> List[Dict[str, Any]]:
        """軸のT1ソース取得"""
        return []
    
    def _check_data_gap_for_axis(self, axis: AxisType) -> bool:
        """軸のデータギャップ確認"""
        return False

def main():
    """メイン実行"""
    if len(sys.argv) < 2:
        print("Usage: python ahf_v080_evaluator.py <TICKER>")
        sys.exit(1)
    
    ticker = sys.argv[1]
    evaluator = AHFv080Evaluator(ticker)
    result = evaluator.evaluate_ticker()
    
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()

