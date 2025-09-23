#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AHF 三段化抽出パイプライン
facts.md → 前処理YAML → 正規化JSON の自動化フロー

1. AnchorLint → 2. 因果文抽出 → 3. 数値正規化 → 4. α3/α5算出 → 5. TRI-3＋V-Overlay → 6. マトリクス出力
"""

import re
import yaml
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime

# 既存エンジンのインポート
import sys
sys.path.append(str(Path(__file__).parent))
from ahf_t_judgment_engine import TJudgmentEngine
from ahf_v_overlay_v2 import VOverlayEngine
from ahf_alpha_bonus_strict import AlphaBonusEngine

@dataclass
class ExtractionResult:
    """抽出結果"""
    ticker: str
    as_of: str
    status: str  # success, data_gap, error
    reason: Optional[str]
    metrics: Dict[str, Any]
    anchors: List[Dict[str, str]]
    auto_checks: Dict[str, Any]
    tri3_result: Dict[str, Any]

class ExtractionPipeline:
    """三段化抽出パイプライン"""
    
    def __init__(self, config_dir: str = "../config"):
        """初期化"""
        self.config_dir = Path(config_dir)
        self.t_engine = TJudgmentEngine(config_dir)
        self.v_engine = VOverlayEngine(config_dir)
        self.alpha_engine = AlphaBonusEngine(config_dir)
        self.ticker_config = self._load_ticker_config()
        
    def _load_ticker_config(self) -> Dict:
        """ティッカー設定の読み込み"""
        try:
            with open(self.config_dir / "tickers.yaml", 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise RuntimeError(f"ティッカー設定の読み込みエラー: {e}")
    
    def extract_facts_entries(self, facts_content: str) -> List[Dict[str, str]]:
        """facts.mdからのエントリ抽出"""
        entries = []
        
        # facts.mdの形式: [YYYY-MM-DD][T1-F|T1-P|T1-C][Core①|Core②|Core③|Time] "逐語" (impact: KPI)
        pattern = r'\[([^\]]+)\]\[([^\]]+)\]\[([^\]]+)\]\s*"([^"]+)"\s*\(impact:\s*([^)]+)\)'
        matches = re.findall(pattern, facts_content)
        
        for match in matches:
            date, source, category, quote, impact = match
            entries.append({
                "date": date.strip(),
                "source": source.strip(),
                "category": category.strip(),
                "quote": quote.strip(),
                "impact": impact.strip()
            })
        
        return entries
    
    def normalize_metrics(self, raw_metrics: Dict[str, Any], ticker: str) -> Dict[str, Any]:
        """数値の正規化（$k/pp）"""
        if ticker not in self.ticker_config["tickers"]:
            return raw_metrics
        
        config = self.ticker_config["tickers"][ticker]["reporting_units"]
        normalized = {}
        
        for key, value in raw_metrics.items():
            if isinstance(value, (int, float)):
                # 単位変換のロジック（簡易版）
                if "revenue" in key.lower() and config.get("revenue") == "millions":
                    normalized[key] = value / 1000.0 if value > 1000 else value
                elif "margin" in key.lower() and config.get("gross_margin") == "percentage_points":
                    normalized[key] = value
                elif "expense" in key.lower() and config.get("operating_expense") == "millions":
                    normalized[key] = value / 1000.0 if value > 1000 else value
                else:
                    normalized[key] = value
            else:
                normalized[key] = value
        
        return normalized
    
    def run_anchor_lint(self, facts_entries: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """AnchorLint実行"""
        validated_anchors = []
        
        for entry in facts_entries:
            quote = entry["quote"]
            
            # 基本的な検証
            has_quote = '"' in quote or "'" in quote
            has_source = any(word in quote.lower() for word in 
                           ["management", "we", "company", "our", "according"])
            has_specific = any(word in quote.lower() for word in 
                             ["pricing", "volume", "efficiency", "cost", "mix"])
            
            if has_quote and has_source and has_specific:
                validated_anchors.append({
                    "quote": quote,
                    "category": entry["category"],
                    "impact": entry["impact"],
                    "validation_status": "valid"
                })
            else:
                validated_anchors.append({
                    "quote": quote,
                    "category": entry["category"],
                    "impact": entry["impact"],
                    "validation_status": "invalid",
                    "reason": "missing_anchor_elements"
                })
        
        return validated_anchors
    
    def calculate_tri3_metrics(self, facts_content: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """TRI-3メトリクスの計算"""
        # T判定
        t_result = self.t_engine.judge_t_value(facts_content)
        
        # V-Overlay評価（仮の値で実行）
        ev_sales = metrics.get("ev_sales", 10.0)
        rule_of_40 = metrics.get("rule_of_40", 40.0)
        v_result = self.v_engine.evaluate(ev_sales, rule_of_40)
        
        # α3/α5評価（仮の値で実行）
        current_gm = metrics.get("current_gm", 45.0)
        previous_gm = metrics.get("previous_gm", 44.0)
        current_revenue = metrics.get("current_revenue", 100.0)
        previous_revenue = metrics.get("previous_revenue", 95.0)
        median_opex_grid = metrics.get("median_opex_grid", 50.0)
        opex_actual = metrics.get("opex_actual", 48.0)
        
        alpha3, alpha5 = self.alpha_engine.evaluate_combined(
            current_gm, previous_gm, current_revenue, previous_revenue,
            median_opex_grid, opex_actual, facts_content
        )
        
        return {
            "t_value": t_result.t_value,
            "t_qoq_score": t_result.qoq_score,
            "t_yoy_score": t_result.yoy_score,
            "t_direction_consistent": t_result.direction_consistent,
            "t_anchor_valid": t_result.anchor_valid,
            "v_score": v_result.v_score,
            "v_category": v_result.category,
            "v_star_impact": v_result.star_impact,
            "alpha3_bonus": 1 if alpha3.bonus_earned else 0,
            "alpha5_bonus": 1 if alpha5.bonus_earned else 0,
            "total_bonus": (1 if alpha3.bonus_earned else 0) + (1 if alpha5.bonus_earned else 0)
        }
    
    def process_facts_file(self, facts_file_path: str, ticker: str, 
                          raw_metrics: Dict[str, Any]) -> ExtractionResult:
        """facts.mdファイルの処理"""
        try:
            # facts.mdの読み込み
            with open(facts_file_path, 'r', encoding='utf-8') as f:
                facts_content = f.read()
            
            # エントリ抽出
            facts_entries = self.extract_facts_entries(facts_content)
            
            if not facts_entries:
                return ExtractionResult(
                    ticker=ticker,
                    as_of=datetime.now().strftime("%Y-%m-%d"),
                    status="data_gap",
                    reason="NOT_DISCLOSED",
                    metrics={},
                    anchors=[],
                    auto_checks={},
                    tri3_result={}
                )
            
            # 数値正規化
            normalized_metrics = self.normalize_metrics(raw_metrics, ticker)
            
            # AnchorLint実行
            validated_anchors = self.run_anchor_lint(facts_entries)
            
            # TRI-3メトリクス計算
            tri3_result = self.calculate_tri3_metrics(facts_content, normalized_metrics)
            
            # 自動チェック
            auto_checks = {
                "facts_entries_count": len(facts_entries),
                "valid_anchors_count": sum(1 for a in validated_anchors 
                                         if a["validation_status"] == "valid"),
                "t_judgment_available": True,
                "v_overlay_available": True,
                "alpha_bonus_available": True
            }
            
            return ExtractionResult(
                ticker=ticker,
                as_of=datetime.now().strftime("%Y-%m-%d"),
                status="success",
                reason=None,
                metrics=normalized_metrics,
                anchors=validated_anchors,
                auto_checks=auto_checks,
                tri3_result=tri3_result
            )
            
        except Exception as e:
            return ExtractionResult(
                ticker=ticker,
                as_of=datetime.now().strftime("%Y-%m-%d"),
                status="error",
                reason=str(e),
                metrics={},
                anchors=[],
                auto_checks={},
                tri3_result={}
            )
    
    def generate_preprocessing_yaml(self, result: ExtractionResult) -> str:
        """前処理YAMLの生成"""
        yaml_data = {
            "meta": {
                "ticker": result.ticker,
                "as_of": result.as_of,
                "status": result.status,
                "reason": result.reason
            },
            "metrics": result.metrics,
            "anchors": result.anchors,
            "auto_checks": result.auto_checks
        }
        
        return yaml.dump(yaml_data, default_flow_style=False, allow_unicode=True)
    
    def generate_normalized_json(self, result: ExtractionResult) -> str:
        """正規化JSONの生成"""
        json_data = {
            "ticker": result.ticker,
            "as_of": result.as_of,
            "status": result.status,
            "reason": result.reason,
            "tri3": result.tri3_result,
            "metrics": result.metrics,
            "anchors": result.anchors,
            "auto_checks": result.auto_checks,
            "pipeline_version": "2.0",
            "generated_at": datetime.now().isoformat()
        }
        
        return json.dumps(json_data, indent=2, ensure_ascii=False)

def main():
    """テスト実行"""
    pipeline = ExtractionPipeline()
    
    # テスト用facts.mdの内容
    test_facts_content = """
    [2024-01-01][T1-F][Core①] "Gross margin improved quarter over quarter primarily due to higher pricing and operational efficiency gains" (impact: GM)
    [2024-01-01][T1-F][Core②] "Operating expenses decreased year over year driven by cost optimization initiatives and vendor renegotiations" (impact: OpEx)
    [2024-01-01][T1-P][Core③] "Revenue growth accelerated driven by strong demand in key markets and new product launches" (impact: Revenue)
    """
    
    # テスト用メトリクス
    test_metrics = {
        "current_gm": 45.2,
        "previous_gm": 45.0,
        "current_revenue": 100000,  # 100M
        "previous_revenue": 95000,  # 95M
        "median_opex_grid": 50000,  # 50M
        "opex_actual": 48000,       # 48M
        "ev_sales": 12.0,
        "rule_of_40": 38.0
    }
    
    # テストファイルの作成
    test_facts_file = "test_facts.md"
    with open(test_facts_file, 'w', encoding='utf-8') as f:
        f.write(test_facts_content)
    
    try:
        # パイプライン実行
        result = pipeline.process_facts_file(test_facts_file, "DUOL", test_metrics)
        
        print(f"=== 抽出結果 ===")
        print(f"ティッカー: {result.ticker}")
        print(f"ステータス: {result.status}")
        print(f"理由: {result.reason}")
        print(f"メトリクス数: {len(result.metrics)}")
        print(f"アンカー数: {len(result.anchors)}")
        print(f"TRI-3結果: {result.tri3_result}")
        
        # 前処理YAML生成
        yaml_output = pipeline.generate_preprocessing_yaml(result)
        print(f"\n=== 前処理YAML ===")
        print(yaml_output[:500] + "...")
        
        # 正規化JSON生成
        json_output = pipeline.generate_normalized_json(result)
        print(f"\n=== 正規化JSON ===")
        print(json_output[:500] + "...")
        
    finally:
        # テストファイルの削除
        Path(test_facts_file).unlink(missing_ok=True)

if __name__ == "__main__":
    main()
