#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AHF RSS Fwd-Boost v0.7.2β
①右肩（RSS）—「Fwdブースト」パッチ（最小改修）
実績主義を維持しつつ将来の先行シグナルを薄く注入
"""

import json
import os
import sys
import yaml
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass

@dataclass
class FwdBoostResult:
    """Fwdブースト評価結果"""
    rss_base: int
    fwd_boost: int
    star_1_final: int
    boost_applied: bool
    boost_reasons: List[str]
    confidence: float
    explanation: str

class RSSFwdBoostEngine:
    """RSS Fwdブーストエンジン"""
    
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
                "fwd_boost": {
                    "guidance_threshold": 12.0,  # %
                    "cl_growth_threshold": 10.0,  # %
                    "guidance_negative_penalty": -1
                }
            }
    
    def calculate_rss_base(self, confirmed_items: List[Dict[str, Any]]) -> Tuple[int, Dict[str, Any]]:
        """
        従来のRSS計算（実績ベース）
        RSS = +2·I(DR_qoq ≥ +8% or Bookings_qoq ≥ +10%)
            +1·I(DR_qoq ∈ [0,+8%))
            +1·I(Paid↑ or ARPU↑)
            +1·I(CL↑ and CA↓)
            −1·I(DR_qoq < 0 or (Paid↓ and ARPU↓))
        """
        rss = 0
        details = {}
        
        # 各KPI値を取得
        dr_qoq = 0
        bookings_qoq = 0
        paid_change = 0
        arpu_change = 0
        cl_change = 0
        ca_change = 0
        
        for item in confirmed_items:
            if item["kpi"] == "DR_qoq_pct":
                dr_qoq = item["value"]
            elif item["kpi"] == "Bookings_qoq_pct":
                bookings_qoq = item["value"]
            elif item["kpi"] == "Paid_users_change_pct":
                paid_change = item["value"]
            elif item["kpi"] == "ARPU_change_pct":
                arpu_change = item["value"]
            elif item["kpi"] == "CL_change_pct":
                cl_change = item["value"]
            elif item["kpi"] == "CA_change_pct":
                ca_change = item["value"]
        
        # +2点: DR_qoq ≥ +8% or Bookings_qoq ≥ +10%
        if dr_qoq >= 8.0 or bookings_qoq >= 10.0:
            rss += 2
            details["high_growth"] = True
        else:
            details["high_growth"] = False
        
        # +1点: DR_qoq ∈ [0,+8%)
        if 0 <= dr_qoq < 8.0:
            rss += 1
            details["moderate_growth"] = True
        else:
            details["moderate_growth"] = False
        
        # +1点: Paid↑ or ARPU↑
        if paid_change > 0 or arpu_change > 0:
            rss += 1
            details["user_metrics_up"] = True
        else:
            details["user_metrics_up"] = False
        
        # +1点: CL↑ and CA↓
        if cl_change > 0 and ca_change < 0:
            rss += 1
            details["balance_improvement"] = True
        else:
            details["balance_improvement"] = False
        
        # -1点: DR_qoq < 0 or (Paid↓ and ARPU↓)
        if dr_qoq < 0 or (paid_change < 0 and arpu_change < 0):
            rss -= 1
            details["negative_metrics"] = True
        else:
            details["negative_metrics"] = False
        
        return rss, details
    
    def calculate_fwd_boost(self, confirmed_items: List[Dict[str, Any]], 
                          facts_content: str) -> Tuple[int, List[str]]:
        """
        Fwdブースト計算（最大+1、どれか満たせばOK）
        
        1. ガイダンスq/q ≥ +12%（次Q売上ガイダンスの中央値ベース）
        2. 前受けの積み上がり（CL≡Deferred revenue）q/q ≥ +10%
        3. "次Qの牽引源"が逐語で明示（例：Blackwellの増産・出荷前倒し等）
        """
        boost = 0
        reasons = []
        
        # 1. ガイダンスq/q ≥ +12%
        guidance_qoq = self._extract_guidance_qoq(confirmed_items, facts_content)
        if guidance_qoq is not None and guidance_qoq >= 12.0:
            boost = 1
            reasons.append(f"ガイダンスq/q {guidance_qoq:.1f}%≥12%")
            return boost, reasons
        
        # 2. 前受けの積み上がり（CL）q/q ≥ +10%
        cl_qoq = self._extract_cl_qoq(confirmed_items)
        if cl_qoq is not None and cl_qoq >= 10.0:
            boost = 1
            reasons.append(f"CL q/q {cl_qoq:.1f}%≥10%")
            return boost, reasons
        
        # 3. "次Qの牽引源"が逐語で明示
        if self._has_next_q_driver(facts_content):
            boost = 1
            reasons.append("次Q牽引源の逐語明示")
            return boost, reasons
        
        return boost, reasons
    
    def apply_safety_guards(self, rss_base: int, fwd_boost: int, 
                          confirmed_items: List[Dict[str, Any]]) -> Tuple[int, bool]:
        """
        安全装置の適用
        1. ダウン側ガード：ガイダンスがマイナスなら −1（最低★1）
        2. 上限：Fwdブースト適用後の①は★4まで（★5は"実績"でのみ到達）
        """
        adjusted_boost = fwd_boost
        guard_applied = False
        
        # ダウン側ガード：ガイダンスがマイナスなら −1
        guidance_qoq = self._extract_guidance_qoq(confirmed_items, "")
        if guidance_qoq is not None and guidance_qoq < 0:
            adjusted_boost -= 1
            guard_applied = True
        
        # 上限：★4まで（★5は実績でのみ）
        final_rss = rss_base + adjusted_boost
        final_star = self._calculate_star_from_rss(final_rss)
        
        if final_star > 4:
            adjusted_boost = 4 - rss_base
            guard_applied = True
        
        return adjusted_boost, guard_applied
    
    def _extract_guidance_qoq(self, confirmed_items: List[Dict[str, Any]], 
                            facts_content: str) -> Optional[float]:
        """ガイダンスq/qの抽出"""
        # まずtriage.jsonから探す
        for item in confirmed_items:
            if item["kpi"] == "Guidance_qoq_pct":
                return item["value"]
        
        # facts.mdから抽出（簡略化）
        if "guidance" in facts_content.lower() and "%" in facts_content:
            # 簡易的な抽出ロジック（実際の実装ではより精密に）
            lines = facts_content.split('\n')
            for line in lines:
                if "guidance" in line.lower() and "%" in line:
                    # 数値を抽出（簡略化）
                    import re
                    numbers = re.findall(r'(\d+(?:\.\d+)?)%', line)
                    if numbers:
                        return float(numbers[0])
        
        return None
    
    def _extract_cl_qoq(self, confirmed_items: List[Dict[str, Any]]) -> Optional[float]:
        """CL q/qの抽出"""
        for item in confirmed_items:
            if item["kpi"] == "CL_qoq_pct":
                return item["value"]
        return None
    
    def _has_next_q_driver(self, facts_content: str) -> bool:
        """次Qの牽引源が逐語で明示されているかチェック"""
        if not facts_content:
            return False
        
        content_lower = facts_content.lower()
        
        # 牽引源を示すキーワード
        driver_keywords = [
            "blackwell", "increased production", "accelerated delivery",
            "next quarter", "upcoming quarter", "guidance raised",
            "increased capacity", "new product launch", "demand acceleration"
        ]
        
        return any(keyword in content_lower for keyword in driver_keywords)
    
    def _calculate_star_from_rss(self, rss: int) -> int:
        """RSSから★を計算"""
        if rss >= 4:
            return 5
        elif rss == 3:
            return 4
        elif rss == 2:
            return 3
        elif rss == 1:
            return 2
        else:
            return 1
    
    def calculate_confidence(self, rss_base: int, fwd_boost: int, 
                          boost_reasons: List[str]) -> float:
        """確信度計算"""
        confidence = 70.0  # ベース70%
        
        # Fwdブースト適用時は確信度を調整
        if fwd_boost > 0:
            if len(boost_reasons) >= 2:  # 複数の根拠
                confidence += 10.0
            elif len(boost_reasons) == 1:  # 単一の根拠
                confidence += 5.0
        
        # 実績ベースの強さ
        if rss_base >= 3:
            confidence += 10.0
        elif rss_base >= 1:
            confidence += 5.0
        
        # 50–95%でクリップ
        return max(50.0, min(95.0, confidence))
    
    def evaluate(self, triage_file: str, facts_file: str) -> FwdBoostResult:
        """RSS Fwdブースト評価の実行"""
        
        # ファイル読み込み
        with open(triage_file, 'r', encoding='utf-8') as f:
            triage_data = json.load(f)
        
        with open(facts_file, 'r', encoding='utf-8') as f:
            facts_content = f.read()
        
        confirmed_items = triage_data.get("CONFIRMED", [])
        
        # 従来のRSS計算
        rss_base, details = self.calculate_rss_base(confirmed_items)
        
        # Fwdブースト計算
        fwd_boost, boost_reasons = self.calculate_fwd_boost(confirmed_items, facts_content)
        
        # 安全装置適用
        adjusted_boost, guard_applied = self.apply_safety_guards(
            rss_base, fwd_boost, confirmed_items)
        
        # 最終★計算
        final_rss = rss_base + adjusted_boost
        star_1_final = self._calculate_star_from_rss(final_rss)
        
        # 確信度計算
        confidence = self.calculate_confidence(rss_base, adjusted_boost, boost_reasons)
        
        # 説明文生成
        explanation = self._generate_explanation(
            rss_base, adjusted_boost, boost_reasons, guard_applied, star_1_final)
        
        return FwdBoostResult(
            rss_base=rss_base,
            fwd_boost=adjusted_boost,
            star_1_final=star_1_final,
            boost_applied=adjusted_boost > 0,
            boost_reasons=boost_reasons,
            confidence=confidence,
            explanation=explanation
        )
    
    def _generate_explanation(self, rss_base: int, fwd_boost: int, 
                            boost_reasons: List[str], guard_applied: bool, 
                            star_1_final: int) -> str:
        """説明文生成"""
        parts = [f"RSS={rss_base}"]
        
        if fwd_boost > 0:
            parts.append(f"+Fwdブースト{fwd_boost}")
            parts.append(f"({', '.join(boost_reasons)})")
        elif fwd_boost < 0:
            parts.append(f"安全装置{fwd_boost}")
        
        parts.append(f"→★{star_1_final}")
        
        if guard_applied:
            parts.append("(安全装置適用)")
        
        return " ".join(parts)

def process_rss_fwd_boost(triage_file: str, facts_file: str) -> Dict[str, Any]:
    """RSS Fwdブースト処理の実行"""
    
    engine = RSSFwdBoostEngine()
    result = engine.evaluate(triage_file, facts_file)
    
    return {
        "as_of": json.load(open(triage_file, 'r', encoding='utf-8'))["as_of"],
        "rss_fwd_boost": {
            "rss_base": result.rss_base,
            "fwd_boost": result.fwd_boost,
            "star_1_final": result.star_1_final,
            "boost_applied": result.boost_applied,
            "boost_reasons": result.boost_reasons
        },
        "confidence": result.confidence,
        "explanation": result.explanation,
        "notes": {
            "rss.fwd_boost_rule": "実績ベース+先行シグナル薄味注入"
        }
    }

def main():
    if len(sys.argv) != 3:
        print("使用方法: python ahf_rss_fwd_boost_v072.py <triage.jsonのパス> <facts.mdのパス>")
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
        results = process_rss_fwd_boost(triage_file, facts_file)
        
        # 結果出力
        print("=== AHF RSS Fwd-Boost Results (v0.7.2β) ===")
        print(f"As of: {results['as_of']}")
        print()
        print(f"RSS基礎: {results['rss_fwd_boost']['rss_base']}")
        print(f"Fwdブースト: {results['rss_fwd_boost']['fwd_boost']}")
        print(f"★1: {results['rss_fwd_boost']['star_1_final']}")
        print(f"ブースト適用: {results['rss_fwd_boost']['boost_applied']}")
        if results['rss_fwd_boost']['boost_reasons']:
            print(f"ブースト根拠: {', '.join(results['rss_fwd_boost']['boost_reasons'])}")
        print(f"確信度: {results['confidence']:.0f}%")
        print(f"説明: {results['explanation']}")
        
        # 結果をJSONファイルに保存
        output_file = triage_file.replace("triage.json", "rss_fwd_boost.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"[INFO] 結果を保存しました: {output_file}")
        
    except Exception as e:
        print(f"[ERROR] 処理エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

