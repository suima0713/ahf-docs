#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AHF V-Overlay Sector-Aware v0.7.2β
③認知ギャップ（セクター別V-Overlay統合システム）
"""

import json
import os
import sys
import yaml
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass

# 各V-Overlayエンジンのインポート
sys.path.append(os.path.dirname(__file__))
from ahf_v_overlay_v2 import VOverlayEngine, VOverlayResult
from ahf_v_overlay_healthcare_v072 import HealthcareVOverlayEngine, HealthcareVOverlayResult

@dataclass
class SectorAwareVResult:
    """セクター対応V評価結果"""
    sector: str
    v_score: float
    category: str
    star_3: int
    engine_used: str
    explanation: str
    confidence: float

class SectorAwareVOverlayEngine:
    """セクター対応V-Overlayエンジン"""
    
    def __init__(self, config_dir: str = "../config"):
        """初期化"""
        self.config_dir = os.path.join(os.path.dirname(__file__), config_dir)
        self.config = self._load_config()
        
        # 各エンジンの初期化
        self.standard_engine = VOverlayEngine(config_dir)
        self.healthcare_engine = HealthcareVOverlayEngine(config_dir)
        
    def _load_config(self) -> Dict:
        """設定の読み込み"""
        try:
            config_file = os.path.join(self.config_dir, "thresholds.yaml")
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            return {"sector_mapping": {}}
    
    def determine_sector(self, ticker: str, triage_data: Dict[str, Any]) -> str:
        """セクター判定"""
        # 設定ファイルからセクターマッピングを取得
        sector_mapping = self.config.get("sector_mapping", {})
        
        # ティッカー別マッピング
        if ticker in sector_mapping:
            return sector_mapping[ticker]
        
        # 業種別判定（KPIやfacts.mdから推測）
        confirmed_items = triage_data.get("CONFIRMED", [])
        
        # ヘルスケア・保険関連のKPIをチェック
        healthcare_keywords = ["MCR", "medical_cost_ratio", "healthcare", "insurance"]
        for item in confirmed_items:
            if any(keyword.lower() in item["kpi"].lower() for keyword in healthcare_keywords):
                return "healthcare"
        
        # 公益事業関連のKPIをチェック
        utility_keywords = ["regulated", "rate_base", "utility"]
        for item in confirmed_items:
            if any(keyword.lower() in item["kpi"].lower() for keyword in utility_keywords):
                return "utility"
        
        # デフォルトは標準（テック/一般企業）
        return "standard"
    
    def evaluate_standard(self, ev_sales: float, rule_of_40: float) -> VOverlayResult:
        """標準V-Overlay評価"""
        return self.standard_engine.evaluate(ev_sales, rule_of_40)
    
    def evaluate_healthcare(self, ntm_pe: float, eps_growth: float, 
                          mcr_trend: str) -> HealthcareVOverlayResult:
        """保険セクターV-Overlay評価"""
        return self.healthcare_engine.evaluate(ntm_pe, eps_growth, mcr_trend)
    
    def calculate_confidence(self, sector: str, data_availability: Dict[str, bool]) -> float:
        """確信度計算"""
        confidence = 70.0  # ベース70%
        
        # セクター別の確信度調整
        if sector == "healthcare":
            # 保険セクターは市況データ依存
            if data_availability.get("market_data", False):
                confidence += 10.0
            else:
                confidence -= 15.0
        elif sector == "utility":
            # 公益事業は規制データ依存
            if data_availability.get("regulatory_data", False):
                confidence += 5.0
            else:
                confidence -= 10.0
        else:
            # 標準セクターはT1データ依存
            if data_availability.get("t1_data", False):
                confidence += 10.0
            else:
                confidence -= 10.0
        
        # 50–95%でクリップ
        return max(50.0, min(95.0, confidence))
    
    def evaluate(self, ticker: str, triage_data: Dict[str, Any], 
                market_data: Optional[Dict[str, Any]] = None) -> SectorAwareVResult:
        """セクター対応V評価の実行"""
        
        # セクター判定
        sector = self.determine_sector(ticker, triage_data)
        
        # セクター別評価実行
        if sector == "healthcare":
            # 保険セクター用評価
            if market_data:
                result = self.evaluate_healthcare(
                    market_data.get("ntm_pe", 18.5),
                    market_data.get("eps_growth_next_year", 12.5),
                    market_data.get("mcr_trend", "improving")
                )
                v_score = result.v_score
                category = result.category
                star_3 = result.star_impact
                explanation = result.explanation
                engine_used = "healthcare_v_overlay"
            else:
                # データ不足の場合はデフォルト値
                v_score = 0.5
                category = "Amber"
                star_3 = 2
                explanation = "保険セクター（データ不足）→★2"
                engine_used = "healthcare_v_overlay_default"
        
        elif sector == "utility":
            # 公益事業用評価（簡略化）
            v_score = 0.4
            category = "Amber"
            star_3 = 2
            explanation = "公益事業（規制制約考慮）→★2"
            engine_used = "utility_v_overlay"
        
        else:
            # 標準評価（EV/Sales + Rule of 40）
            confirmed_items = triage_data.get("CONFIRMED", [])
            ev_sales = 0
            rule_of_40 = 0
            
            for item in confirmed_items:
                if item["kpi"] == "EV_Sales_ratio":
                    ev_sales = item["value"]
                elif item["kpi"] == "Rule_of_40_pct":
                    rule_of_40 = item["value"]
            
            result = self.evaluate_standard(ev_sales, rule_of_40)
            v_score = result.v_score
            category = result.category
            star_3 = 3 if category == "Green" else (2 if category == "Amber" else 1)
            explanation = f"標準V-Overlay（{category}）→★{star_3}"
            engine_used = "standard_v_overlay"
        
        # 確信度計算
        data_availability = {
            "market_data": market_data is not None,
            "t1_data": len(triage_data.get("CONFIRMED", [])) > 0,
            "regulatory_data": sector == "utility"
        }
        confidence = self.calculate_confidence(sector, data_availability)
        
        return SectorAwareVResult(
            sector=sector,
            v_score=v_score,
            category=category,
            star_3=star_3,
            engine_used=engine_used,
            explanation=explanation,
            confidence=confidence
        )

def process_sector_aware_v_overlay(triage_file: str, 
                                 market_data_file: Optional[str] = None) -> Dict[str, Any]:
    """セクター対応V-Overlay処理の実行"""
    
    # triage.json読み込み
    with open(triage_file, 'r', encoding='utf-8') as f:
        triage_data = json.load(f)
    
    # 市場データ読み込み
    market_data = None
    if market_data_file and os.path.exists(market_data_file):
        with open(market_data_file, 'r', encoding='utf-8') as f:
            market_data = json.load(f)
    
    # エンジン初期化
    engine = SectorAwareVOverlayEngine()
    
    # 評価実行
    ticker = triage_data.get("ticker", "")
    result = engine.evaluate(ticker, triage_data, market_data)
    
    return {
        "as_of": triage_data["as_of"],
        "ticker": ticker,
        "sector_aware_v": {
            "sector": result.sector,
            "v_score": result.v_score,
            "category": result.category,
            "star_3": result.star_3,
            "engine_used": result.engine_used
        },
        "confidence": result.confidence,
        "explanation": result.explanation,
        "inputs": {
            "triage_data_available": len(triage_data.get("CONFIRMED", [])) > 0,
            "market_data_available": market_data is not None
        },
        "notes": {
            "sector_aware.v_overlay_rule": "セクター別V-Overlay統合"
        }
    }

def main():
    if len(sys.argv) < 2:
        print("使用方法: python ahf_v_overlay_sector_aware_v072.py <triage.jsonのパス> [market_data.jsonのパス]")
        sys.exit(1)
    
    triage_file = sys.argv[1]
    market_data_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(triage_file):
        print(f"[ERROR] triage.jsonが見つかりません: {triage_file}")
        sys.exit(1)
    
    try:
        results = process_sector_aware_v_overlay(triage_file, market_data_file)
        
        # 結果出力
        print("=== AHF Sector-Aware V-Overlay Results (v0.7.2β) ===")
        print(f"As of: {results['as_of']}")
        print(f"Ticker: {results['ticker']}")
        print()
        print(f"セクター: {results['sector_aware_v']['sector']}")
        print(f"Vスコア: {results['sector_aware_v']['v_score']:.3f}")
        print(f"区分: {results['sector_aware_v']['category']}")
        print(f"★3: {results['sector_aware_v']['star_3']}")
        print(f"使用エンジン: {results['sector_aware_v']['engine_used']}")
        print(f"確信度: {results['confidence']:.0f}%")
        print(f"説明: {results['explanation']}")
        
        # 結果をJSONファイルに保存
        output_file = triage_file.replace("triage.json", "sector_aware_v_overlay.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"[INFO] 結果を保存しました: {output_file}")
        
    except Exception as e:
        print(f"[ERROR] 処理エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

