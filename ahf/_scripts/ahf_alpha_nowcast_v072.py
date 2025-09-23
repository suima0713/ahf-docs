#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AHF Alpha Now‑cast v0.7.2β
②勾配のNow‑castパッチ（α3_ncast + α5_ncast + Gap‑safe）
"""

import json
import os
import sys
import yaml
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass

@dataclass
class NowcastResult:
    """Now‑cast評価結果"""
    alpha3_ncast: int
    alpha5_ncast: int
    gap_safe_applied: bool
    total_score: int
    star_2: int
    confidence: float
    explanation: str

class AlphaNowcastEngine:
    """α Now‑castエンジン"""
    
    def __init__(self, config_dir: str = "../config"):
        """初期化"""
        self.config_dir = os.path.join(os.path.dirname(__file__), config_dir)
        self.config = self._load_config()
        
    def _load_config(self) -> Dict:
        """設定の読み込み"""
        try:
            config_file = os.path.join(self.config_dir, "thresholds.yaml")
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            # デフォルト設定
            return {
                "nowcast": {
                    "alpha3_ncast": {
                        "sw_cloud_threshold": 200,  # bps
                        "hw_decline_threshold": 100,  # bps
                        "medium_threshold": 50  # bps
                    },
                    "alpha5_ncast": {
                        "oi_growth_advantage": 200,  # bps
                        "oi_rate_improvement": 50,  # bps
                        "tolerance_band": 200  # bps
                    }
                }
            }
    
    def calculate_alpha3_ncast(self, 
                              sw_cloud_mix_change: Optional[float],
                              hw_mix_change: Optional[float],
                              t1_explanations: List[str]) -> Tuple[int, bool]:
        """
        α3_ncast（Mix/因果）の計算
        
        2: SW/Cloud比↑≥+200bps または HW↓≥100bps + 一次因果
        1: SW↑50–200bps または 一次因果のみ
        0: 改善なし×一次因果なし
        """
        gap_safe_applied = False
        
        # 主要指標が欠落している場合のGap‑safe
        if sw_cloud_mix_change is None and hw_mix_change is None:
            gap_safe_applied = True
            return 1, gap_safe_applied  # 中立=1点
        
        # 強い改善（SW/Cloud比↑≥+200bps または HW↓≥100bps）
        if sw_cloud_mix_change is not None and sw_cloud_mix_change >= 200:
            if self._has_t1_explanation(t1_explanations):
                return 2, gap_safe_applied
        
        if hw_mix_change is not None and hw_mix_change <= -100:
            if self._has_t1_explanation(t1_explanations):
                return 2, gap_safe_applied
        
        # 中程度の改善（SW↑50–200bps）
        if sw_cloud_mix_change is not None and 50 <= sw_cloud_mix_change < 200:
            if self._has_t1_explanation(t1_explanations):
                return 1, gap_safe_applied
        
        # 一次因果のみ（数値改善なし）
        if self._has_t1_explanation(t1_explanations):
            return 1, gap_safe_applied
        
        # 改善なし×一次因果なし
        return 0, gap_safe_applied
    
    def calculate_alpha5_ncast(self,
                              revenue_yoy_pct: Optional[float],
                              oi_yoy_pct: Optional[float],
                              oi_rate_yoy_pp: Optional[float],
                              t1_text: str) -> Tuple[int, bool]:
        """
        α5_ncast（レバレッジ）の計算
        
        2: Non‑GAAP OI成長≧売上YoY+200bps または OI率YoY+≥50bps+効率フレーズ
        1: OI成長≒売上YoY±200bps または OI率横ばい+効率フレーズ
        0: 下回る または 効率フレーズなし
        """
        gap_safe_applied = False
        
        # 主要指標が欠落している場合のGap‑safe
        if (revenue_yoy_pct is None and oi_yoy_pct is None and 
            oi_rate_yoy_pp is None):
            gap_safe_applied = True
            return 1, gap_safe_applied  # 中立=1点
        
        efficiency_phrases = self.config.get("nowcast", {}).get("alpha5_ncast", {}).get(
            "efficiency_phrases", ["operating leverage", "discipline", "hiring pacing"])
        
        has_efficiency = self._has_efficiency_phrases(t1_text, efficiency_phrases)
        
        # 強い改善（OI成長≧売上YoY+200bps）
        if (revenue_yoy_pct is not None and oi_yoy_pct is not None):
            oi_advantage = oi_yoy_pct - revenue_yoy_pct
            if oi_advantage >= 200:  # 200bps
                return 2, gap_safe_applied
        
        # 強い改善（OI率YoY+≥50bps+効率フレーズ）
        if oi_rate_yoy_pp is not None and oi_rate_yoy_pp >= 50:
            if has_efficiency:
                return 2, gap_safe_applied
        
        # 中程度（OI成長≒売上YoY±200bps）
        if (revenue_yoy_pct is not None and oi_yoy_pct is not None):
            oi_advantage = oi_yoy_pct - revenue_yoy_pct
            if abs(oi_advantage) <= 200:  # ±200bps
                if has_efficiency:
                    return 1, gap_safe_applied
        
        # 中程度（OI率横ばい+効率フレーズ）
        if (oi_rate_yoy_pp is not None and abs(oi_rate_yoy_pp) < 50 and 
            has_efficiency):
            return 1, gap_safe_applied
        
        # 下回る または 効率フレーズなし
        return 0, gap_safe_applied
    
    def calculate_star_2(self, alpha3_ncast: int, alpha5_ncast: int) -> int:
        """
        S=α3_ncast+α5_ncast（0–4）→ ★
        0→★1, 1→★2, 2→★3, 3→★4, 4→★5
        """
        total_score = alpha3_ncast + alpha5_ncast
        
        if total_score == 4:
            return 5
        elif total_score == 3:
            return 4
        elif total_score == 2:
            return 3
        elif total_score == 1:
            return 2
        else:  # total_score == 0
            return 1
    
    def calculate_confidence(self, alpha3_ncast: int, alpha5_ncast: int, 
                           gap_safe_applied: bool) -> float:
        """確信度計算"""
        confidence = 70.0  # ベース70%
        
        # Gap‑safe適用時は確信度を下げる
        if gap_safe_applied:
            confidence -= 15.0
        
        # 両方のスコアが高い場合は確信度を上げる
        if alpha3_ncast >= 2 and alpha5_ncast >= 2:
            confidence += 10.0
        elif alpha3_ncast >= 1 and alpha5_ncast >= 1:
            confidence += 5.0
        
        # 50–95%でクリップ
        return max(50.0, min(95.0, confidence))
    
    def _has_t1_explanation(self, explanations: List[str]) -> bool:
        """T1逐語で一次説明があるかチェック"""
        if not explanations:
            return False
        
        explanation_text = " ".join(explanations).lower()
        keywords = ["qoq", "yoy", "quarter", "year", "sequential", "year-over-year",
                   "mix", "product", "segment", "margin"]
        return any(keyword in explanation_text for keyword in keywords)
    
    def _has_efficiency_phrases(self, t1_text: str, phrases: List[str]) -> bool:
        """T1テキストに運用効率フレーズがあるかチェック"""
        if not t1_text:
            return False
        
        text_lower = t1_text.lower()
        return any(phrase.lower() in text_lower for phrase in phrases)
    
    def evaluate(self, data: Dict[str, Any]) -> NowcastResult:
        """Now‑cast評価の実行"""
        
        # 必要なKPI値を取得
        sw_cloud_mix_change = data.get("sw_cloud_mix_change_bps")
        hw_mix_change = data.get("hw_mix_change_bps")
        revenue_yoy_pct = data.get("revenue_yoy_pct")
        oi_yoy_pct = data.get("oi_yoy_pct")
        oi_rate_yoy_pp = data.get("oi_rate_yoy_pp")
        t1_explanations = data.get("t1_explanations", [])
        t1_text = data.get("t1_text", "")
        
        # α3_ncast計算
        alpha3_ncast, gap_safe_3 = self.calculate_alpha3_ncast(
            sw_cloud_mix_change, hw_mix_change, t1_explanations)
        
        # α5_ncast計算
        alpha5_ncast, gap_safe_5 = self.calculate_alpha5_ncast(
            revenue_yoy_pct, oi_yoy_pct, oi_rate_yoy_pp, t1_text)
        
        # 総合判定
        gap_safe_applied = gap_safe_3 or gap_safe_5
        total_score = alpha3_ncast + alpha5_ncast
        star_2 = self.calculate_star_2(alpha3_ncast, alpha5_ncast)
        confidence = self.calculate_confidence(alpha3_ncast, alpha5_ncast, gap_safe_applied)
        
        # 説明文生成
        explanation = self._generate_explanation(
            alpha3_ncast, alpha5_ncast, gap_safe_applied, star_2)
        
        return NowcastResult(
            alpha3_ncast=alpha3_ncast,
            alpha5_ncast=alpha5_ncast,
            gap_safe_applied=gap_safe_applied,
            total_score=total_score,
            star_2=star_2,
            confidence=confidence,
            explanation=explanation
        )
    
    def _generate_explanation(self, alpha3_ncast: int, alpha5_ncast: int, 
                            gap_safe_applied: bool, star_2: int) -> str:
        """説明文生成"""
        parts = []
        
        if gap_safe_applied:
            parts.append("Gap‑safe適用")
        
        parts.append(f"α3_ncast={alpha3_ncast}")
        parts.append(f"α5_ncast={alpha5_ncast}")
        parts.append(f"→★{star_2}")
        
        return " ".join(parts)

def process_alpha_nowcast(triage_file: str, facts_file: str) -> Dict[str, Any]:
    """Now‑cast処理の実行"""
    
    # triage.json読み込み
    with open(triage_file, 'r', encoding='utf-8') as f:
        triage_data = json.load(f)
    
    # facts.md読み込み
    with open(facts_file, 'r', encoding='utf-8') as f:
        facts_content = f.read()
    
    # 必要なデータを抽出
    confirmed_items = triage_data.get("CONFIRMED", [])
    data = {}
    
    # KPI値の抽出
    for item in confirmed_items:
        kpi = item["kpi"]
        if kpi in ["SW_Cloud_Mix_Change_bps", "HW_Mix_Change_bps", 
                  "Revenue_YoY_pct", "OI_YoY_pct", "OI_Rate_YoY_pp"]:
            data[kpi.lower()] = item["value"]
    
    # T1説明の抽出
    data["t1_explanations"] = extract_t1_explanations(facts_content)
    data["t1_text"] = facts_content
    
    # Now‑cast評価実行
    engine = AlphaNowcastEngine()
    result = engine.evaluate(data)
    
    return {
        "as_of": triage_data["as_of"],
        "alpha_nowcast": {
            "alpha3_ncast": result.alpha3_ncast,
            "alpha5_ncast": result.alpha5_ncast,
            "gap_safe_applied": result.gap_safe_applied,
            "total_score": result.total_score,
            "star_2": result.star_2
        },
        "confidence": result.confidence,
        "explanation": result.explanation,
        "inputs": data,
        "notes": {
            "alpha.nowcast_rule": "α3_ncast+α5_ncast+Gap_safe"
        }
    }

def extract_t1_explanations(facts_content: str) -> List[str]:
    """facts.mdからT1説明を抽出"""
    explanations = []
    lines = facts_content.split('\n')
    
    for line in lines:
        if '[T1-' in line and 'Core②' in line:
            parts = line.split('"')
            if len(parts) > 1:
                explanation = parts[1]
                if len(explanation.split()) <= 40:
                    explanations.append(explanation)
    
    return explanations

def main():
    if len(sys.argv) != 3:
        print("使用方法: python ahf_alpha_nowcast_v072.py <triage.jsonのパス> <facts.mdのパス>")
        sys.exit(1)
    
    triage_file = sys.argv[1]
    facts_file = sys.argv[2]
    
    if not os.path.exists(triage_file):
        print(f"[ERROR] triage.jsonが見つかりません: {triage_file}")
        sys.exit(1)
    
    if not os.path.exists(facts_file):
        print(f"[ERROR] facts.mdが見つかりません: {facts_file}")
        sys.exit(1)
    
    try:
        results = process_alpha_nowcast(triage_file, facts_file)
        
        # 結果出力
        print("=== AHF Alpha Now‑cast Results (v0.7.2β) ===")
        print(f"As of: {results['as_of']}")
        print()
        print(f"α3_ncast: {results['alpha_nowcast']['alpha3_ncast']}")
        print(f"α5_ncast: {results['alpha_nowcast']['alpha5_ncast']}")
        print(f"Gap‑safe: {results['alpha_nowcast']['gap_safe_applied']}")
        print(f"★2: {results['alpha_nowcast']['star_2']}")
        print(f"確信度: {results['confidence']:.0f}%")
        print(f"説明: {results['explanation']}")
        
        # 結果をJSONファイルに保存
        output_file = triage_file.replace("triage.json", "alpha_nowcast.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"[INFO] 結果を保存しました: {output_file}")
        
    except Exception as e:
        print(f"[ERROR] 処理エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

