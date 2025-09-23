#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AHF α3/α5ボーナス厳格判定エンジン
両PASSのみ＋MD&A逐語必須の条件で+1★付与

α3: |GM_drift| ≤ 0.2pp かつ Residual_GP ≤ $8M
α5: median(OpEx_grid) − OpEx_actual ≤ −$3M
MD&A逐語に一次説明（因果句）1本以上

上記すべて満たす時のみ +1★
どれか欠けたら +0（Watch→Go候補フラグは出力可、★は動かさない）
"""

import re
import yaml
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Alpha3Result:
    """α3判定結果"""
    gm_drift_abs: float
    residual_gp: float
    gm_drift_pass: bool
    residual_gp_pass: bool
    mda_quote_found: bool
    bonus_earned: bool
    details: Dict[str, str]

@dataclass
class Alpha5Result:
    """α5判定結果"""
    median_opex_grid: float
    opex_actual: float
    opex_savings: float
    opex_pass: bool
    mda_quote_found: bool
    bonus_earned: bool
    details: Dict[str, str]

class AlphaBonusEngine:
    """α3/α5ボーナス厳格判定エンジン"""
    
    def __init__(self, config_dir: str = "../config"):
        """初期化"""
        self.config_dir = Path(config_dir)
        self.lexicon = self._load_lexicon()
        
        # 厳格閾値（決定事項より）
        self.alpha3_gm_drift_threshold = 0.2  # pp
        self.alpha3_residual_gp_threshold = 8.0  # $M
        self.alpha5_opex_savings_threshold = 3.0  # $M
        
    def _load_lexicon(self) -> Dict:
        """辞書設定の読み込み"""
        try:
            with open(self.config_dir / "lexicon.yaml", 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise RuntimeError(f"辞書設定の読み込みエラー: {e}")
    
    def extract_mda_quotes(self, facts_content: str) -> List[str]:
        """MD&A逐語の抽出"""
        quotes = []
        
        # facts.mdの形式: [YYYY-MM-DD][T1-F|T1-P|T1-C][Core①|Core②|Core③|Time] "逐語" (impact: KPI)
        pattern = r'\[.*?\]\[.*?\]\[.*?\]\s*"([^"]+)"\s*\(impact:.*?\)'
        matches = re.findall(pattern, facts_content)
        
        for match in matches:
            quote = match.strip()
            if len(quote) >= 20:  # 最小長さチェック
                quotes.append(quote)
        
        return quotes
    
    def validate_causal_explanation(self, quote: str) -> bool:
        """因果説明の検証"""
        quote_lower = quote.lower()
        
        # 因果動詞の存在チェック
        causal_verbs = self.lexicon["causal_verbs"]
        has_causal = any(verb in quote_lower for verb in causal_verbs)
        
        # 除外リストチェック
        denylist = self.lexicon["denylist"]
        is_denied = any(denied in quote_lower for denied in denylist)
        
        # 一次説明の特徴（具体的数値、明確な要因）
        has_specific_factors = any(word in quote_lower for word in 
                                 ["pricing", "volume", "efficiency", "cost", "mix", "scale"])
        
        return has_causal and not is_denied and has_specific_factors
    
    def calculate_gm_drift(self, current_gm: float, previous_gm: float) -> float:
        """売上総利益ドリフトの計算"""
        return abs(current_gm - previous_gm)
    
    def calculate_residual_gp(self, revenue: float, current_gm: float, 
                            previous_gm: float, previous_revenue: float) -> float:
        """残差GPの計算"""
        # 前回GM率での期待売上総利益
        expected_gp = revenue * (previous_gm / 100.0)
        # 実際の売上総利益
        actual_gp = revenue * (current_gm / 100.0)
        # 残差（絶対値）
        return abs(actual_gp - expected_gp)
    
    def calculate_opex_savings(self, median_grid: float, actual: float) -> float:
        """オペレーティング費用削減の計算"""
        return median_grid - actual
    
    def evaluate_alpha3(self, 
                       current_gm: float,
                       previous_gm: float,
                       current_revenue: float,
                       previous_revenue: float,
                       facts_content: str) -> Alpha3Result:
        """α3判定の実行"""
        
        # GMドリフト計算
        gm_drift_abs = self.calculate_gm_drift(current_gm, previous_gm)
        gm_drift_pass = gm_drift_abs <= self.alpha3_gm_drift_threshold
        
        # 残差GP計算
        residual_gp = self.calculate_residual_gp(current_revenue, current_gm, 
                                               previous_gm, previous_revenue)
        residual_gp_pass = residual_gp <= self.alpha3_residual_gp_threshold
        
        # MD&A逐語の検証
        mda_quotes = self.extract_mda_quotes(facts_content)
        mda_quote_found = any(self.validate_causal_explanation(quote) 
                            for quote in mda_quotes)
        
        # ボーナス判定（すべて満たす時のみ）
        bonus_earned = gm_drift_pass and residual_gp_pass and mda_quote_found
        
        # 詳細情報
        details = {
            "gm_drift_threshold": self.alpha3_gm_drift_threshold,
            "residual_gp_threshold": self.alpha3_residual_gp_threshold,
            "mda_quotes_count": len(mda_quotes),
            "valid_causal_quotes": sum(1 for q in mda_quotes 
                                     if self.validate_causal_explanation(q))
        }
        
        return Alpha3Result(
            gm_drift_abs=gm_drift_abs,
            residual_gp=residual_gp,
            gm_drift_pass=gm_drift_pass,
            residual_gp_pass=residual_gp_pass,
            mda_quote_found=mda_quote_found,
            bonus_earned=bonus_earned,
            details=details
        )
    
    def evaluate_alpha5(self, 
                       median_opex_grid: float,
                       opex_actual: float,
                       facts_content: str) -> Alpha5Result:
        """α5判定の実行"""
        
        # オペレーティング費用削減計算
        opex_savings = self.calculate_opex_savings(median_opex_grid, opex_actual)
        opex_pass = opex_savings >= self.alpha5_opex_savings_threshold
        
        # MD&A逐語の検証
        mda_quotes = self.extract_mda_quotes(facts_content)
        mda_quote_found = any(self.validate_causal_explanation(quote) 
                            for quote in mda_quotes)
        
        # ボーナス判定（すべて満たす時のみ）
        bonus_earned = opex_pass and mda_quote_found
        
        # 詳細情報
        details = {
            "opex_savings_threshold": self.alpha5_opex_savings_threshold,
            "mda_quotes_count": len(mda_quotes),
            "valid_causal_quotes": sum(1 for q in mda_quotes 
                                     if self.validate_causal_explanation(q))
        }
        
        return Alpha5Result(
            median_opex_grid=median_opex_grid,
            opex_actual=opex_actual,
            opex_savings=opex_savings,
            opex_pass=opex_pass,
            mda_quote_found=mda_quote_found,
            bonus_earned=bonus_earned,
            details=details
        )
    
    def evaluate_combined(self, 
                         current_gm: float,
                         previous_gm: float,
                         current_revenue: float,
                         previous_revenue: float,
                         median_opex_grid: float,
                         opex_actual: float,
                         facts_content: str) -> Tuple[Alpha3Result, Alpha5Result]:
        """α3/α5の統合評価"""
        
        alpha3_result = self.evaluate_alpha3(
            current_gm, previous_gm, current_revenue, previous_revenue, facts_content
        )
        
        alpha5_result = self.evaluate_alpha5(
            median_opex_grid, opex_actual, facts_content
        )
        
        return alpha3_result, alpha5_result

def main():
    """テスト実行"""
    engine = AlphaBonusEngine()
    
    # テスト用facts.mdの内容
    test_facts = """
    [2024-01-01][T1-F][Core①] "Gross margin improved primarily due to higher pricing and operational efficiency gains" (impact: GM)
    [2024-01-01][T1-F][Core②] "Operating expenses decreased driven by cost optimization initiatives and vendor renegotiations" (impact: OpEx)
    """
    
    # テストケース1: α3ボーナス獲得条件
    print("=== α3判定テスト ===")
    alpha3_result = engine.evaluate_alpha3(
        current_gm=45.2,
        previous_gm=45.0,
        current_revenue=100.0,
        previous_revenue=95.0,
        facts_content=test_facts
    )
    
    print(f"GMドリフト: {alpha3_result.gm_drift_abs:.2f}pp (閾値: {engine.alpha3_gm_drift_threshold}pp)")
    print(f"残差GP: ${alpha3_result.residual_gp:.2f}M (閾値: ${engine.alpha3_residual_gp_threshold}M)")
    print(f"MD&A逐語: {alpha3_result.mda_quote_found}")
    print(f"ボーナス獲得: {alpha3_result.bonus_earned}")
    print(f"詳細: {alpha3_result.details}")
    
    # テストケース2: α5ボーナス獲得条件
    print("\n=== α5判定テスト ===")
    alpha5_result = engine.evaluate_alpha5(
        median_opex_grid=50.0,
        opex_actual=45.0,
        facts_content=test_facts
    )
    
    print(f"オペレーティング費用削減: ${alpha5_result.opex_savings:.2f}M (閾値: ${engine.alpha5_opex_savings_threshold}M)")
    print(f"MD&A逐語: {alpha5_result.mda_quote_found}")
    print(f"ボーナス獲得: {alpha5_result.bonus_earned}")
    print(f"詳細: {alpha5_result.details}")
    
    # テストケース3: 統合評価
    print("\n=== 統合評価テスト ===")
    alpha3, alpha5 = engine.evaluate_combined(
        current_gm=45.2,
        previous_gm=45.0,
        current_revenue=100.0,
        previous_revenue=95.0,
        median_opex_grid=50.0,
        opex_actual=45.0,
        facts_content=test_facts
    )
    
    total_bonus = (1 if alpha3.bonus_earned else 0) + (1 if alpha5.bonus_earned else 0)
    print(f"総ボーナス: +{total_bonus}★")
    print(f"α3: {'PASS' if alpha3.bonus_earned else 'FAIL'}")
    print(f"α5: {'PASS' if alpha5.bonus_earned else 'FAIL'}")

if __name__ == "__main__":
    main()
