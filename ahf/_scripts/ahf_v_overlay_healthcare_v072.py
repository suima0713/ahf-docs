#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AHF V-Overlay Healthcare v0.7.2β
③認知ギャップ（保険セクター用 V-Overlay）
NTM P/E × EPS成長（Next-Yr）× MCRトレンド
"""

import json
import os
import sys
import yaml
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass

@dataclass
class HealthcareVOverlayResult:
    """保険セクターV-Overlay評価結果"""
    v_score: float
    category: str  # Green, Amber, Red
    ntm_pe: float
    eps_growth: float
    mcr_trend: str  # improving, stable, deteriorating
    star_impact: int
    explanation: str

class HealthcareVOverlayEngine:
    """保険セクターV-Overlayエンジン"""
    
    def __init__(self, config_dir: str = "../config"):
        """初期化"""
        self.config_dir = os.path.join(os.path.dirname(__file__), config_dir)
        self.config = self._load_config()
        
    def _load_config(self) -> Dict:
        """設定の読み込み"""
        try:
            config_file = os.path.join(self.config_dir, "thresholds.yaml")
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                return config.get("healthcare_v_overlay", self._get_default_config())
        except Exception as e:
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """デフォルト設定"""
        return {
            "thresholds": {
                "green": {
                    "ntm_pe_max": 18.0,
                    "eps_growth_min": 10.0,
                    "mcr_trend": "improving"
                },
                "red": {
                    "ntm_pe_min": 22.0,
                    "eps_growth_max": 5.0,
                    "mcr_trend": "deteriorating"
                }
            },
            "weights": {
                "ntm_pe": 0.4,
                "eps_growth": 0.4,
                "mcr_trend": 0.2
            }
        }
    
    def calculate_ntm_pe_score(self, ntm_pe: float) -> float:
        """NTM P/Eスコアの計算"""
        green_max = self.config["thresholds"]["green"]["ntm_pe_max"]
        red_min = self.config["thresholds"]["red"]["ntm_pe_min"]
        
        if ntm_pe <= green_max:
            return 0.0  # 理想的
        elif ntm_pe >= red_min:
            return 1.0  # 問題的
        else:
            # 線形補間
            return (ntm_pe - green_max) / (red_min - green_max)
    
    def calculate_eps_growth_score(self, eps_growth: float) -> float:
        """EPS成長スコアの計算"""
        green_min = self.config["thresholds"]["green"]["eps_growth_min"]
        red_max = self.config["thresholds"]["red"]["eps_growth_max"]
        
        if eps_growth >= green_min:
            return 0.0  # 理想的
        elif eps_growth <= red_max:
            return 1.0  # 問題的
        else:
            # 線形補間（逆方向）
            return (green_min - eps_growth) / (green_min - red_max)
    
    def calculate_mcr_trend_score(self, mcr_trend: str) -> float:
        """MCRトレンドスコアの計算"""
        if mcr_trend == "improving":
            return 0.0  # 理想的
        elif mcr_trend == "stable":
            return 0.5  # 中立的
        elif mcr_trend == "deteriorating":
            return 1.0  # 問題的
        else:
            return 0.5  # デフォルト
    
    def calculate_v_score(self, ntm_pe: float, eps_growth: float, 
                         mcr_trend: str) -> Tuple[float, float, float, float]:
        """合成Vスコアの計算"""
        pe_score = self.calculate_ntm_pe_score(ntm_pe)
        eps_score = self.calculate_eps_growth_score(eps_growth)
        mcr_score = self.calculate_mcr_trend_score(mcr_trend)
        
        # 重み付き合成
        weights = self.config["weights"]
        v_score = (weights["ntm_pe"] * pe_score + 
                  weights["eps_growth"] * eps_score + 
                  weights["mcr_trend"] * mcr_score)
        
        return v_score, pe_score, eps_score, mcr_score
    
    def determine_category(self, v_score: float) -> str:
        """V区分の決定"""
        if v_score < 0.33:
            return "Green"
        elif v_score < 0.67:
            return "Amber"
        else:
            return "Red"
    
    def calculate_star_impact(self, category: str) -> int:
        """星への影響計算"""
        if category == "Green":
            return 3  # ★3
        elif category == "Amber":
            return 2  # ★2
        elif category == "Red":
            return 1  # ★1
        else:
            return 2  # デフォルト
    
    def evaluate(self, ntm_pe: float, eps_growth: float, 
                mcr_trend: str) -> HealthcareVOverlayResult:
        """保険セクターV-Overlay評価の実行"""
        
        # 合成スコア計算
        v_score, pe_score, eps_score, mcr_score = self.calculate_v_score(
            ntm_pe, eps_growth, mcr_trend)
        
        # 区分決定
        category = self.determine_category(v_score)
        
        # 星への影響計算
        star_impact = self.calculate_star_impact(category)
        
        # 説明文生成
        explanation = self._generate_explanation(
            category, ntm_pe, eps_growth, mcr_trend, v_score)
        
        return HealthcareVOverlayResult(
            v_score=v_score,
            category=category,
            ntm_pe=ntm_pe,
            eps_growth=eps_growth,
            mcr_trend=mcr_trend,
            star_impact=star_impact,
            explanation=explanation
        )
    
    def _generate_explanation(self, category: str, ntm_pe: float, 
                            eps_growth: float, mcr_trend: str, v_score: float) -> str:
        """説明文生成"""
        parts = []
        
        if category == "Green":
            parts.append("Green（理想的）")
        elif category == "Amber":
            parts.append("Amber（一部未達）")
        else:
            parts.append("Red（問題的）")
        
        parts.append(f"P/E:{ntm_pe:.1f}x")
        parts.append(f"EPS成長:{eps_growth:.1f}%")
        parts.append(f"MCR:{mcr_trend}")
        parts.append(f"→★{self.calculate_star_impact(category)}")
        
        return " ".join(parts)

def process_healthcare_v_overlay(triage_file: str, market_data_file: str) -> Dict[str, Any]:
    """保険セクターV-Overlay処理の実行"""
    
    # triage.json読み込み
    with open(triage_file, 'r', encoding='utf-8') as f:
        triage_data = json.load(f)
    
    # 市場データ読み込み（市況データ）
    if os.path.exists(market_data_file):
        with open(market_data_file, 'r', encoding='utf-8') as f:
            market_data = json.load(f)
    else:
        # デフォルト値（UNH例）
        market_data = {
            "ntm_pe": 18.5,  # フォワードP/E
            "eps_growth_next_year": 12.5,  # 来期EPS成長
            "mcr_trend": "improving"  # MCRトレンド
        }
    
    # エンジン初期化
    engine = HealthcareVOverlayEngine()
    
    # 評価実行
    result = engine.evaluate(
        market_data["ntm_pe"],
        market_data["eps_growth_next_year"],
        market_data["mcr_trend"]
    )
    
    return {
        "as_of": triage_data["as_of"],
        "ticker": triage_data.get("ticker", ""),
        "healthcare_v_overlay": {
            "v_score": result.v_score,
            "category": result.category,
            "ntm_pe": result.ntm_pe,
            "eps_growth": result.eps_growth,
            "mcr_trend": result.mcr_trend,
            "star_3": result.star_impact
        },
        "explanation": result.explanation,
        "inputs": market_data,
        "notes": {
            "healthcare.v_overlay_rule": "NTM_PE_x_EPS_growth_x_MCR_trend"
        }
    }

def main():
    if len(sys.argv) != 3:
        print("使用方法: python ahf_v_overlay_healthcare_v072.py <triage.jsonのパス> <market_data.jsonのパス>")
        sys.exit(1)
    
    triage_file = sys.argv[1]
    market_data_file = sys.argv[2]
    
    if not os.path.exists(triage_file):
        print(f"[ERROR] triage.jsonが見つかりません: {triage_file}")
        sys.exit(1)
    
    try:
        results = process_healthcare_v_overlay(triage_file, market_data_file)
        
        # 結果出力
        print("=== AHF Healthcare V-Overlay Results (v0.7.2β) ===")
        print(f"As of: {results['as_of']}")
        print(f"Ticker: {results['ticker']}")
        print()
        print(f"Vスコア: {results['healthcare_v_overlay']['v_score']:.3f}")
        print(f"区分: {results['healthcare_v_overlay']['category']}")
        print(f"NTM P/E: {results['healthcare_v_overlay']['ntm_pe']:.1f}x")
        print(f"EPS成長: {results['healthcare_v_overlay']['eps_growth']:.1f}%")
        print(f"MCRトレンド: {results['healthcare_v_overlay']['mcr_trend']}")
        print(f"★3: {results['healthcare_v_overlay']['star_3']}")
        print(f"説明: {results['explanation']}")
        
        # 結果をJSONファイルに保存
        output_file = triage_file.replace("triage.json", "healthcare_v_overlay.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"[INFO] 結果を保存しました: {output_file}")
        
    except Exception as e:
        print(f"[ERROR] 処理エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

