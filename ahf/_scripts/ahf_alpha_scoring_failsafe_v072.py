#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AHF Alpha Scoring Fail-safe v0.7.2β
②勾配（短期傾きのみ・プロキシ不足は★2）
"""

import json
import os
import sys
import yaml
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass

@dataclass
class AlphaFailSafeResult:
    """Alpha Fail-safe結果"""
    guidance_qoq: Optional[float]
    book_to_bill: Optional[float]
    margin_trend: Optional[float]
    proxy_sufficiency: bool
    final_star: int
    explanation: str

class AlphaFailSafeEngine:
    """Alpha Fail-safeエンジン（短期傾きのみ）"""
    
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
            return {
                "alpha_failsafe": {
                    "thresholds": {
                        "guidance_qoq_strong": 12.0,    # 強気
                        "guidance_qoq_positive": 0.0,   # 正数
                        "book_to_bill_strong": 1.1,     # 強気
                        "book_to_bill_adequate": 1.0,   # 適正
                        "margin_trend_positive": 0.0    # 正数
                    },
                    "weights": {
                        "guidance": 0.5,
                        "book_to_bill": 0.3,
                        "margin_trend": 0.2
                    }
                }
            }
    
    def extract_short_term_signals(self, confirmed_items: List[Dict[str, Any]], 
                                  facts_content: str) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        """短期傾きシグナルの抽出"""
        
        # ガイダンスq/q
        guidance_qoq = None
        for item in confirmed_items:
            if "guidance" in item["kpi"].lower() and "qoq" in item["kpi"].lower():
                guidance_qoq = item["value"]
                break
        
        # B/B
        book_to_bill = None
        for item in confirmed_items:
            if "book_to_bill" in item["kpi"].lower() or "book_to_bill" in item["kpi"].lower():
                book_to_bill = item["value"]
                break
        
        # マージン漂移
        margin_trend = None
        for item in confirmed_items:
            if "margin" in item["kpi"].lower() and "change" in item["kpi"].lower():
                margin_trend = item["value"]
                break
        
        return guidance_qoq, book_to_bill, margin_trend
    
    def calculate_proxy_sufficiency(self, guidance_qoq: Optional[float], 
                                  book_to_bill: Optional[float], 
                                  margin_trend: Optional[float]) -> bool:
        """プロキシ充足度判定"""
        # 最低2つ以上のデータが必要
        data_count = sum([
            guidance_qoq is not None,
            book_to_bill is not None,
            margin_trend is not None
        ])
        
        return data_count >= 2
    
    def calculate_short_term_score(self, guidance_qoq: Optional[float], 
                                 book_to_bill: Optional[float], 
                                 margin_trend: Optional[float]) -> float:
        """短期傾きスコア計算"""
        score = 0.0
        weights = self.config.get("alpha_failsafe", {}).get("weights", {"guidance": 0.5, "book_to_bill": 0.3, "margin_trend": 0.2})
        thresholds = self.config.get("alpha_failsafe", {}).get("thresholds", {
            "guidance_qoq_strong": 12.0,
            "guidance_qoq_positive": 0.0,
            "book_to_bill_strong": 1.1,
            "book_to_bill_adequate": 1.0,
            "margin_trend_positive": 0.0
        })
        
        # ガイダンスq/q評価
        if guidance_qoq is not None:
            if guidance_qoq >= thresholds["guidance_qoq_strong"]:
                score += weights["guidance"] * 2.0  # 強気
            elif guidance_qoq >= thresholds["guidance_qoq_positive"]:
                score += weights["guidance"] * 1.0  # 正数
            else:
                score += weights["guidance"] * 0.0  # マイナス
        else:
            # データ欠落時は中立
            score += weights["guidance"] * 1.0
        
        # B/B評価
        if book_to_bill is not None:
            if book_to_bill >= thresholds["book_to_bill_strong"]:
                score += weights["book_to_bill"] * 2.0  # 強気
            elif book_to_bill >= thresholds["book_to_bill_adequate"]:
                score += weights["book_to_bill"] * 1.0  # 適正
            else:
                score += weights["book_to_bill"] * 0.0  # 弱気
        else:
            # データ欠落時は中立
            score += weights["book_to_bill"] * 1.0
        
        # マージン漂移評価
        if margin_trend is not None:
            if margin_trend >= thresholds["margin_trend_positive"]:
                score += weights["margin_trend"] * 1.0  # 正数
            else:
                score += weights["margin_trend"] * 0.0  # マイナス
        else:
            # データ欠落時は中立
            score += weights["margin_trend"] * 0.5
        
        return score
    
    def synthesize_star(self, score: float, proxy_sufficiency: bool) -> int:
        """★合成（プロキシ不足は★2）"""
        if not proxy_sufficiency:
            return 2  # プロキシ不足は★2（中立寄り）
        
        # スコアから★計算
        if score >= 1.8:
            return 5
        elif score >= 1.5:
            return 4
        elif score >= 1.2:
            return 3
        elif score >= 0.8:
            return 2
        else:
            return 1
    
    def evaluate(self, triage_file: str, facts_file: str) -> AlphaFailSafeResult:
        """Alpha Fail-safe分析の実行"""
        
        # ファイル読み込み
        with open(triage_file, 'r', encoding='utf-8') as f:
            triage_data = json.load(f)
        
        with open(facts_file, 'r', encoding='utf-8') as f:
            facts_content = f.read()
        
        confirmed_items = triage_data.get("CONFIRMED", [])
        
        # 短期傾きシグナル抽出
        guidance_qoq, book_to_bill, margin_trend = self.extract_short_term_signals(confirmed_items, facts_content)
        
        # プロキシ充足度判定
        proxy_sufficiency = self.calculate_proxy_sufficiency(guidance_qoq, book_to_bill, margin_trend)
        
        # 短期傾きスコア計算
        score = self.calculate_short_term_score(guidance_qoq, book_to_bill, margin_trend)
        
        # ★合成
        final_star = self.synthesize_star(score, proxy_sufficiency)
        
        # 説明文生成
        explanation = self._generate_explanation(guidance_qoq, book_to_bill, margin_trend, 
                                              proxy_sufficiency, final_star)
        
        return AlphaFailSafeResult(
            guidance_qoq=guidance_qoq,
            book_to_bill=book_to_bill,
            margin_trend=margin_trend,
            proxy_sufficiency=proxy_sufficiency,
            final_star=final_star,
            explanation=explanation
        )
    
    def _generate_explanation(self, guidance_qoq: Optional[float], 
                            book_to_bill: Optional[float], 
                            margin_trend: Optional[float],
                            proxy_sufficiency: bool, 
                            final_star: int) -> str:
        """説明文生成"""
        parts = []
        
        if not proxy_sufficiency:
            parts.append("プロキシ不足→★2")
        else:
            parts.append(f"ガイダンス:{guidance_qoq:.1f}%" if guidance_qoq else "ガイダンス:N/A")
            parts.append(f"B/B:{book_to_bill:.1f}x" if book_to_bill else "B/B:N/A")
            parts.append(f"マージン:{margin_trend:.1f}" if margin_trend else "マージン:N/A")
            parts.append(f"→★{final_star}")
        
        return " ".join(parts)

def process_alpha_failsafe_analysis(triage_file: str, facts_file: str) -> Dict[str, Any]:
    """Alpha Fail-safe分析処理の実行"""
    
    engine = AlphaFailSafeEngine()
    result = engine.evaluate(triage_file, facts_file)
    
    return {
        "as_of": json.load(open(triage_file, 'r', encoding='utf-8'))["as_of"],
        "ticker": json.load(open(triage_file, 'r', encoding='utf-8')).get("ticker", ""),
        "alpha_failsafe": {
            "guidance_qoq": result.guidance_qoq,
            "book_to_bill": result.book_to_bill,
            "margin_trend": result.margin_trend,
            "proxy_sufficiency": result.proxy_sufficiency,
            "final_star": result.final_star
        },
        "explanation": result.explanation,
        "notes": {
            "alpha.failsafe_rule": "短期傾きのみ・プロキシ不足は★2"
        }
    }

def main():
    if len(sys.argv) != 3:
        print("使用方法: python ahf_alpha_scoring_failsafe_v072.py <triage.jsonのパス> <facts.mdのパス>")
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
        results = process_alpha_failsafe_analysis(triage_file, facts_file)
        
        # 結果出力
        print("=== AHF Alpha Fail-safe Analysis Results (v0.7.2β) ===")
        print(f"As of: {results['as_of']}")
        print(f"Ticker: {results['ticker']}")
        print()
        print("【短期傾きシグナル】")
        print(f"ガイダンスq/q: {results['alpha_failsafe']['guidance_qoq']:.1f}%" if results['alpha_failsafe']['guidance_qoq'] else "ガイダンスq/q: N/A")
        print(f"B/B: {results['alpha_failsafe']['book_to_bill']:.1f}x" if results['alpha_failsafe']['book_to_bill'] else "B/B: N/A")
        print(f"マージン漂移: {results['alpha_failsafe']['margin_trend']:.1f}" if results['alpha_failsafe']['margin_trend'] else "マージン漂移: N/A")
        print()
        print(f"プロキシ充足度: {results['alpha_failsafe']['proxy_sufficiency']}")
        print(f"最終★: {results['alpha_failsafe']['final_star']}")
        print(f"説明: {results['explanation']}")
        
        # 結果をJSONファイルに保存
        output_file = triage_file.replace("triage.json", "alpha_failsafe_analysis.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"[INFO] 結果を保存しました: {output_file}")
        
    except Exception as e:
        print(f"[ERROR] 処理エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
