#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AHF T判定エンジン v2.0
辞書×正規化による機械ルールでT値を一意判定

T=2: QoQとYoYの両方で因果句が逐語で存在し、方向一致
T=1: 片側のみ満たす
T=0: いずれも無い／方向矛盾／アンカー不成立
"""

import re
import yaml
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class TJudgmentResult:
    """T判定結果"""
    t_value: int  # 0, 1, 2
    qoq_score: float  # 0.0-1.0
    yoy_score: float  # 0.0-1.0
    direction_consistent: bool
    anchor_valid: bool
    details: Dict[str, str]

class TJudgmentEngine:
    """T判定エンジン"""
    
    def __init__(self, config_dir: str = "../config"):
        """初期化"""
        self.config_dir = Path(config_dir)
        self.lexicon = self._load_lexicon()
        self.ticker_config = self._load_ticker_config()
        
    def _load_lexicon(self) -> Dict:
        """辞書設定の読み込み"""
        try:
            with open(self.config_dir / "lexicon.yaml", 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise RuntimeError(f"辞書設定の読み込みエラー: {e}")
    
    def _load_ticker_config(self) -> Dict:
        """ティッカー設定の読み込み"""
        try:
            with open(self.config_dir / "tickers.yaml", 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise RuntimeError(f"ティッカー設定の読み込みエラー: {e}")
    
    def extract_causal_sentences(self, facts_content: str, period_type: str) -> List[str]:
        """因果文の抽出"""
        sentences = []
        
        # 期間パターンの特定
        period_patterns = self.lexicon["period_patterns"][period_type]
        
        # 因果動詞とGM関連語の組み合わせで検索
        causal_verbs = self.lexicon["causal_verbs"]
        gm_aliases = self.lexicon["gm_aliases"]
        
        # 文章を分割（簡易版：句点で分割）
        text_sentences = re.split(r'[.!?]+', facts_content)
        
        for sentence in text_sentences:
            sentence = sentence.strip()
            if len(sentence) < 20:  # 短すぎる文章は除外
                continue
                
            # 期間パターンとの一致チェック
            period_match = any(pattern.lower() in sentence.lower() 
                             for pattern in period_patterns)
            
            # 因果動詞との一致チェック
            causal_match = any(verb.lower() in sentence.lower() 
                             for verb in causal_verbs)
            
            # GM関連語との一致チェック
            gm_match = any(gm.lower() in sentence.lower() 
                         for gm in gm_aliases)
            
            if period_match and causal_match and gm_match:
                sentences.append(sentence)
        
        return sentences
    
    def detect_direction(self, sentence: str) -> Optional[str]:
        """方向性の検出"""
        sentence_lower = sentence.lower()
        
        up_words = self.lexicon["direction_up"]
        down_words = self.lexicon["direction_down"]
        
        up_count = sum(1 for word in up_words if word in sentence_lower)
        down_count = sum(1 for word in down_words if word in sentence_lower)
        
        if up_count > down_count:
            return "up"
        elif down_count > up_count:
            return "down"
        else:
            return None  # 方向不明
    
    def validate_anchor(self, sentence: str) -> bool:
        """アンカーリングの検証"""
        sentence_lower = sentence.lower()
        
        # 引用符の存在チェック
        quote_indicators = self.lexicon["anchor_patterns"]["quote_indicators"]
        has_quote = any(indicator in sentence_lower for indicator in quote_indicators)
        
        # ソースの存在チェック
        source_indicators = self.lexicon["anchor_patterns"]["source_indicators"]
        has_source = any(indicator in sentence_lower for indicator in source_indicators)
        
        # 除外リストチェック
        denylist = self.lexicon["denylist"]
        is_denied = any(denied in sentence_lower for denied in denylist)
        
        return (has_quote or has_source) and not is_denied
    
    def calculate_period_score(self, sentences: List[str]) -> Tuple[float, bool]:
        """期間スコアの計算"""
        if not sentences:
            return 0.0, False
        
        valid_sentences = [s for s in sentences if self.validate_anchor(s)]
        if not valid_sentences:
            return 0.0, False
        
        # 方向性の検出
        directions = [self.detect_direction(s) for s in valid_sentences]
        directions = [d for d in directions if d is not None]
        
        if not directions:
            return 0.0, False
        
        # 方向の一貫性チェック
        direction_consistent = len(set(directions)) == 1
        
        # スコア計算（有効文数と方向一貫性の重み付き）
        base_score = len(valid_sentences) / max(len(sentences), 1)
        consistency_bonus = 0.3 if direction_consistent else 0.0
        
        return min(base_score + consistency_bonus, 1.0), direction_consistent
    
    def judge_t_value(self, facts_content: str) -> TJudgmentResult:
        """T値の判定"""
        # QoQとYoYの因果文抽出
        qoq_sentences = self.extract_causal_sentences(facts_content, "quarter_over_quarter")
        yoy_sentences = self.extract_causal_sentences(facts_content, "year_over_year")
        
        # スコア計算
        qoq_score, qoq_consistent = self.calculate_period_score(qoq_sentences)
        yoy_score, yoy_consistent = self.calculate_period_score(yoy_sentences)
        
        # 方向の一貫性チェック（全体）
        direction_consistent = qoq_consistent and yoy_consistent
        
        # アンカーリングの検証
        anchor_valid = any(self.validate_anchor(s) for s in qoq_sentences + yoy_sentences)
        
        # T値の決定
        if qoq_score >= 0.7 and yoy_score >= 0.7 and direction_consistent:
            t_value = 2
        elif qoq_score >= 0.7 or yoy_score >= 0.7:
            t_value = 1
        else:
            t_value = 0
        
        # 詳細情報
        details = {
            "qoq_sentences_found": len(qoq_sentences),
            "yoy_sentences_found": len(yoy_sentences),
            "qoq_direction_consistent": qoq_consistent,
            "yoy_direction_consistent": yoy_consistent,
            "anchor_validation_passed": anchor_valid
        }
        
        return TJudgmentResult(
            t_value=t_value,
            qoq_score=qoq_score,
            yoy_score=yoy_score,
            direction_consistent=direction_consistent,
            anchor_valid=anchor_valid,
            details=details
        )

def main():
    """テスト実行"""
    engine = TJudgmentEngine()
    
    # テスト用facts.mdの内容
    test_facts = """
    [2024-01-01][T1-F][Core①] "Gross margin increased quarter over quarter primarily due to higher pricing and improved operational efficiency" (impact: GM)
    [2024-01-01][T1-F][Core②] "Cost of revenues decreased year over year driven by supply chain optimization and vendor negotiations" (impact: CoR)
    """
    
    result = engine.judge_t_value(test_facts)
    
    print(f"T値: {result.t_value}")
    print(f"QoQスコア: {result.qoq_score:.2f}")
    print(f"YoYスコア: {result.yoy_score:.2f}")
    print(f"方向一貫性: {result.direction_consistent}")
    print(f"アンカー有効: {result.anchor_valid}")
    print(f"詳細: {result.details}")

if __name__ == "__main__":
    main()
