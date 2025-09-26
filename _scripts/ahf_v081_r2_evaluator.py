#!/usr/bin/env python3
"""
AHF v0.8.1-r2 評価器
固定4軸（①長期EV確度、②長期EV勾配、③現バリュエーション、④将来EVバリュ）の評価

Purpose: 投資判断に直結する固定4軸で評価
MVP: ①②③④の名称と順序を絶対固定／T1 or T1*で確証（不足はn/a）／定型テーブル＋1行要約を即出力
"""

import json
import yaml
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum

class EvidenceLevel(Enum):
    """証拠階層"""
    T1 = "T1"          # 一次（SEC/IR）
    T1_STAR = "T1*"    # Corroborated二次（独立2源以上）
    T2 = "T2"          # 二次1源

@dataclass
class ValuationData:
    """バリュエーションデータ"""
    evs_actual_ttm: float
    evs_peer_median_ttm: float
    date: str
    source: str
    peer_set: List[str]

@dataclass
class ForwardValuationData:
    """将来バリュエーションデータ"""
    evs_actual_today: float
    g_fwd: float
    opm_fwd: float
    rdcf_bands: Dict[str, float]  # {"10x": 0.1, "8x": 0.08, "6x": 0.06}

class AHFv081R2Evaluator:
    """AHF v0.8.1-r2 4軸評価器"""
    
    def __init__(self, ticker: str):
        self.ticker = ticker
        self.evidence_items: List[Dict[str, Any]] = []
        
    def evaluate_4_axes(self) -> Dict[str, Any]:
        """4軸評価実行"""
        result = {
            "ticker": self.ticker,
            "evaluation_date": datetime.now().strftime("%Y-%m-%d"),
            "lec": self._evaluate_lec(),
            "nes": self._evaluate_nes(),
            "current_valuation": self._evaluate_current_valuation(),
            "future_valuation": self._evaluate_future_valuation(),
            "evidence_summary": self._summarize_evidence()
        }
        
        return result
    
    def _evaluate_lec(self) -> Dict[str, Any]:
        """①長期EV確度（LEC）評価"""
        # LEC ≈ g_fwd + ΔOPM_fwd − Dilution − Capex_intensity
        # 価格は不使用
        
        # T1/T1*データから取得
        g_fwd = self._get_t1_value("g_fwd", 0.0)
        delta_opm_fwd = self._get_t1_value("delta_opm_fwd", 0.0)
        dilution = self._get_t1_value("dilution", 0.0)
        capex_intensity = self._get_t1_value("capex_intensity", 0.0)
        
        # LEC計算
        lec_score = g_fwd + delta_opm_fwd - dilution - capex_intensity
        
        # 星割当: ≥20pp→★5／15–20→★4／8–15→★3／3–8→★2／<3→★1
        if lec_score >= 0.20:
            star_score = 5
        elif lec_score >= 0.15:
            star_score = 4
        elif lec_score >= 0.08:
            star_score = 3
        elif lec_score >= 0.03:
            star_score = 2
        else:
            star_score = 1
        
        return {
            "score": lec_score,
            "star_score": star_score,
            "confidence": self._calculate_confidence("lec"),
            "inputs": {
                "g_fwd": g_fwd,
                "delta_opm_fwd": delta_opm_fwd,
                "dilution": dilution,
                "capex_intensity": capex_intensity
            },
            "evidence_level": self._get_evidence_level("lec"),
            "direction_prob_up_pct": self._calculate_direction_prob("lec", "up"),
            "direction_prob_down_pct": self._calculate_direction_prob("lec", "down")
        }
    
    def _evaluate_nes(self) -> Dict[str, Any]:
        """②長期EV勾配（NES）評価"""
        # NES = 0.5·(次Q q/q%) + 0.3·(ガイド改定%) + 0.2·(受注/Backlog増勢%) + Margin_term + Health_term
        
        # T1/T1*データから取得
        next_q_qoq = self._get_t1_value("next_q_qoq_pct", 0.0)
        guidance_revision = self._get_t1_value("guidance_revision_pct", 0.0)
        backlog_growth = self._get_t1_value("backlog_growth_pct", 0.0)
        
        # Margin_term計算
        margin_term = self._calculate_margin_term()
        
        # Health_term計算（Ro40=成長%+GAAP OPM%）
        health_term = self._calculate_health_term()
        
        # NES計算
        nes_score = (0.5 * next_q_qoq + 
                     0.3 * guidance_revision + 
                     0.2 * backlog_growth + 
                     margin_term + 
                     health_term)
        
        # 星割当: NES≥8→★5／5–8→★4／2–5→★3／0–2→★2／<0→★1
        if nes_score >= 8:
            star_score = 5
        elif nes_score >= 5:
            star_score = 4
        elif nes_score >= 2:
            star_score = 3
        elif nes_score >= 0:
            star_score = 2
        else:
            star_score = 1
        
        return {
            "score": nes_score,
            "star_score": star_score,
            "confidence": self._calculate_confidence("nes"),
            "inputs": {
                "next_q_qoq_pct": next_q_qoq,
                "guidance_revision_pct": guidance_revision,
                "backlog_growth_pct": backlog_growth,
                "margin_term": margin_term,
                "health_term": health_term
            },
            "evidence_level": self._get_evidence_level("nes"),
            "direction_prob_up_pct": self._calculate_direction_prob("nes", "up"),
            "direction_prob_down_pct": self._calculate_direction_prob("nes", "down")
        }
    
    def _evaluate_current_valuation(self) -> Dict[str, Any]:
        """③現バリュエーション（機械）評価"""
        # 現在のみ／peer基準
        # EV/S_actual_TTM vs EV/S_peer_median_TTM（同日・同ソース）
        
        # 価格データ取得
        valuation_data = self._get_valuation_data()
        
        if not valuation_data:
            return {
                "status": "data_gap",
                "reason": "価格データ不足",
                "evs_actual_ttm": None,
                "evs_peer_median_ttm": None,
                "disc_pct": None,
                "color": "N/A",
                "vmult": 1.0,
                "lint": {"ev_used": False, "ps_used": False, "same_day": False, "same_source": False}
            }
        
        # 乖離率計算
        disc_pct = ((valuation_data.evs_peer_median_ttm - valuation_data.evs_actual_ttm) / 
                   valuation_data.evs_peer_median_ttm)
        
        # 色/Vmult決定
        if disc_pct >= 0.10 or abs(disc_pct) <= 0.10:
            color = "Green"
            vmult = 1.05
        elif disc_pct > -0.25:
            color = "Amber"
            vmult = 0.90
        else:
            color = "Red"
            vmult = 0.75
        
        # Step-2（注釈のみ）
        step2 = self._calculate_step2_annotation(valuation_data)
        
        return {
            "status": "evaluated",
            "evs_actual_ttm": valuation_data.evs_actual_ttm,
            "evs_peer_median_ttm": valuation_data.evs_peer_median_ttm,
            "disc_pct": disc_pct,
            "color": color,
            "vmult": vmult,
            "lint": {
                "ev_used": True,
                "ps_used": False,
                "same_day": True,
                "same_source": True
            },
            "step2": step2,
            "date": valuation_data.date,
            "source": valuation_data.source,
            "peer_set": valuation_data.peer_set
        }
    
    def _evaluate_future_valuation(self) -> Dict[str, Any]:
        """④将来EVバリュ（総合）評価"""
        # 将来のみ／rDCF×T1/T1*
        # FD% = (EVS_fair_12m − EVS_actual_today) / EVS_fair_12m
        
        # T1/T1*データから取得
        g_fwd = self._get_t1_value("g_fwd", 0.0)
        opm_fwd = self._get_t1_value("opm_fwd", 0.0)
        evs_actual_today = self._get_t1_value("evs_actual_today", 0.0)
        
        if not g_fwd or not opm_fwd or not evs_actual_today:
            return {
                "status": "data_gap",
                "reason": "T1/T1*データ不足",
                "evs_fair_12m": None,
                "fd_pct": None,
                "star_score": 0,
                "confidence": 0.0
            }
        
        # rDCF帯計算（10/8/6×）
        rdcf_bands = {"10x": 0.10, "8x": 0.08, "6x": 0.06}
        evs_fair_12m = self._calculate_evs_fair_12m(g_fwd, opm_fwd, rdcf_bands)
        
        # FD%計算
        fd_pct = (evs_fair_12m - evs_actual_today) / evs_fair_12m
        
        # 星割当: FD%≥+15%→★5／+5〜+15→★4／−5〜+5→★3／−15〜−5→★2／≤−15→★1
        if fd_pct >= 0.15:
            star_score = 5
        elif fd_pct >= 0.05:
            star_score = 4
        elif fd_pct >= -0.05:
            star_score = 3
        elif fd_pct >= -0.15:
            star_score = 2
        else:
            star_score = 1
        
        return {
            "status": "evaluated",
            "evs_fair_12m": evs_fair_12m,
            "fd_pct": fd_pct,
            "star_score": star_score,
            "confidence": self._calculate_confidence("future_valuation"),
            "inputs": {
                "g_fwd": g_fwd,
                "opm_fwd": opm_fwd,
                "evs_actual_today": evs_actual_today,
                "rdcf_bands": rdcf_bands
            },
            "evidence_level": self._get_evidence_level("future_valuation")
        }
    
    def _get_t1_value(self, key: str, default: float = 0.0) -> float:
        """T1/T1*値取得"""
        # 実際の実装では、facts.mdやtriage.jsonから取得
        # ここではサンプル値を返す
        sample_values = {
            "g_fwd": 0.15,
            "delta_opm_fwd": 0.05,
            "dilution": 0.02,
            "capex_intensity": 0.08,
            "next_q_qoq_pct": 0.12,
            "guidance_revision_pct": 0.08,
            "backlog_growth_pct": 0.20,
            "opm_fwd": 0.25,
            "evs_actual_today": 15.2
        }
        
        return sample_values.get(key, default)
    
    def _calculate_margin_term(self) -> float:
        """Margin_term計算"""
        # GM+50bps=+1／±50bps=0／−50bps=−1
        gm_actual = self._get_t1_value("gm_actual", 0.0)
        gm_expected = self._get_t1_value("gm_expected", 0.0)
        
        gm_diff = gm_actual - gm_expected
        
        if gm_diff >= 0.005:  # +50bps
            return 1.0
        elif gm_diff >= -0.005:  # ±50bps
            return 0.0
        else:  # -50bps
            return -1.0
    
    def _calculate_health_term(self) -> float:
        """Health_term計算"""
        # Ro40=成長%+GAAP OPM%：≥40=+1／30–40=0／<30=−1
        growth_pct = self._get_t1_value("growth_pct", 0.0)
        gaap_opm = self._get_t1_value("gaap_opm", 0.0)
        
        ro40 = growth_pct + gaap_opm
        
        if ro40 >= 0.40:
            return 1.0
        elif ro40 >= 0.30:
            return 0.0
        else:
            return -1.0
    
    def _get_valuation_data(self) -> Optional[ValuationData]:
        """バリュエーションデータ取得"""
        # 実際の実装では、価格データソースから取得
        # ここではサンプルデータを返す
        return ValuationData(
            evs_actual_ttm=15.2,
            evs_peer_median_ttm=18.5,
            date="2024-01-15",
            source="internal_etl",
            peer_set=["AAPL", "MSFT", "GOOGL", "AMZN", "META"]
        )
    
    def _calculate_step2_annotation(self, valuation_data: ValuationData) -> Dict[str, Any]:
        """Step-2注釈計算"""
        # Δg = g_fwd − g_peer_median（T1/T1*がある時）
        g_fwd = self._get_t1_value("g_fwd", 0.0)
        g_peer_median = self._get_t1_value("g_peer_median", 0.0)
        
        delta_g = g_fwd - g_peer_median
        
        # 認知フラグ
        flags_pos = []
        flags_neg = []
        
        if delta_g > 0.05:
            flags_pos.append("成長率優位")
        elif delta_g < -0.05:
            flags_neg.append("成長率劣位")
        
        return {
            "delta_g_pp": delta_g * 100,
            "flags_pos": flags_pos,
            "flags_neg": flags_neg,
            "verdict": "適正" if not flags_neg else "要監視"
        }
    
    def _calculate_evs_fair_12m(self, g_fwd: float, opm_fwd: float, rdcf_bands: Dict[str, float]) -> float:
        """EVS_fair_12m計算"""
        # rDCF帯（10/8/6×）× T1/T1*の g_fwd・OPM_fwd（中点）
        # 簡略化した計算
        base_multiple = 15.0  # ベースマルチプル
        growth_adjustment = g_fwd * 2.0  # 成長率調整
        margin_adjustment = opm_fwd * 1.5  # マージン調整
        
        evs_fair = base_multiple + growth_adjustment + margin_adjustment
        
        # rDCF帯の重み付き平均
        weighted_evs = (evs_fair * 0.4 +  # 10x帯
                      evs_fair * 0.4 +   # 8x帯
                      evs_fair * 0.2)    # 6x帯
        
        return weighted_evs
    
    def _calculate_confidence(self, axis: str) -> float:
        """確信度計算"""
        # T1/T1*充足度で50–95%
        base_confidence = 0.5
        
        # T1*証拠がある場合は加点
        if self._has_t1star_evidence(axis):
            base_confidence += 0.2
        
        # T1証拠がある場合は加点
        if self._has_t1_evidence(axis):
            base_confidence += 0.25
        
        return min(base_confidence, 0.95)
    
    def _has_t1_evidence(self, axis: str) -> bool:
        """T1証拠の有無確認"""
        # 実際の実装では、facts.mdから確認
        return True  # サンプル
    
    def _has_t1star_evidence(self, axis: str) -> bool:
        """T1*証拠の有無確認"""
        # 実際の実装では、triage.jsonから確認
        return False  # サンプル
    
    def _get_evidence_level(self, axis: str) -> str:
        """証拠階層取得"""
        if self._has_t1_evidence(axis):
            return "T1"
        elif self._has_t1star_evidence(axis):
            return "T1*"
        else:
            return "T2"
    
    def _calculate_direction_prob(self, axis: str, direction: str) -> float:
        """方向確率計算"""
        # 実際の実装では、過去データから計算
        if direction == "up":
            return 0.6  # サンプル
        else:
            return 0.4  # サンプル
    
    def _summarize_evidence(self) -> Dict[str, Any]:
        """証拠サマリー"""
        return {
            "total_items": len(self.evidence_items),
            "t1_count": sum(1 for item in self.evidence_items if item.get("level") == "T1"),
            "t1star_count": sum(1 for item in self.evidence_items if item.get("level") == "T1*"),
            "t2_count": sum(1 for item in self.evidence_items if item.get("level") == "T2"),
            "contradiction_count": sum(1 for item in self.evidence_items if item.get("contradiction_flag", False))
        }

def main():
    """メイン実行"""
    if len(sys.argv) < 2:
        print("Usage: python ahf_v081_r2_evaluator.py <TICKER>")
        sys.exit(1)
    
    ticker = sys.argv[1]
    
    # 4軸評価実行
    evaluator = AHFv081R2Evaluator(ticker)
    result = evaluator.evaluate_4_axes()
    
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
