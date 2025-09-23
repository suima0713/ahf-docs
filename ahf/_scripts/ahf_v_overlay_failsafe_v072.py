#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AHF V-Overlay Fail-safe v0.7.2β
③評価＋認知（VRG）EV/S×Ro40のみ・未投入は未判定
"""

import json
import os
import sys
import yaml
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass

@dataclass
class VOverlayFailSafeResult:
    """V-Overlay Fail-safe結果"""
    ev_sales: Optional[float]
    rule_of_40: Optional[float]
    data_sufficiency: bool
    category: str  # Green/Amber/Red/UNDETERMINED
    star: int
    explanation: str

class VOverlayFailSafeEngine:
    """V-Overlay Fail-safeエンジン（EV/S×Ro40のみ）"""
    
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
                "v_overlay_failsafe": {
                    "thresholds": {
                        "ev_sales": {
                            "green_max": 8.0,
                            "amber_max": 15.0
                        },
                        "rule_of_40": {
                            "green_min": 40.0,
                            "amber_min": 20.0
                        }
                    }
                }
            }
    
    def extract_v_overlay_data(self, confirmed_items: List[Dict[str, Any]]) -> Tuple[Optional[float], Optional[float]]:
        """V-Overlayデータの抽出（EV/S×Ro40のみ）"""
        
        # EV/S
        ev_sales = None
        for item in confirmed_items:
            if "ev_sales" in item["kpi"].lower() or "ev/sales" in item["kpi"].lower():
                ev_sales = item["value"]
                break
        
        # Ro40
        rule_of_40 = None
        for item in confirmed_items:
            if "rule_of_40" in item["kpi"].lower() or "ro40" in item["kpi"].lower():
                rule_of_40 = item["value"]
                break
        
        return ev_sales, rule_of_40
    
    def check_data_sufficiency(self, ev_sales: Optional[float], 
                             rule_of_40: Optional[float]) -> bool:
        """データ充足度チェック"""
        # EV/S×Ro40の両方が必要
        return ev_sales is not None and rule_of_40 is not None
    
    def calculate_category(self, ev_sales: float, rule_of_40: float) -> str:
        """カテゴリ判定（Green/Amber/Red）"""
        thresholds = self.config.get("v_overlay_failsafe", {}).get("thresholds", {
            "ev_sales": {"green_max": 8.0, "amber_max": 15.0},
            "rule_of_40": {"green_min": 40.0, "amber_min": 20.0}
        })
        
        # EV/S閾値
        ev_sales_green = ev_sales <= thresholds["ev_sales"]["green_max"]
        ev_sales_amber = ev_sales <= thresholds["ev_sales"]["amber_max"]
        
        # Ro40閾値
        ro40_green = rule_of_40 >= thresholds["rule_of_40"]["green_min"]
        ro40_amber = rule_of_40 >= thresholds["rule_of_40"]["amber_min"]
        
        # カテゴリ判定
        if ev_sales_green and ro40_green:
            return "Green"
        elif ev_sales_amber and ro40_amber:
            return "Amber"
        else:
            return "Red"
    
    def calculate_star(self, category: str) -> int:
        """★計算"""
        if category == "Green":
            return 3
        elif category == "Amber":
            return 2
        elif category == "Red":
            return 1
        else:  # UNDETERMINED
            return 0
    
    def evaluate(self, triage_file: str, facts_file: str) -> VOverlayFailSafeResult:
        """V-Overlay Fail-safe分析の実行"""
        
        # ファイル読み込み
        with open(triage_file, 'r', encoding='utf-8') as f:
            triage_data = json.load(f)
        
        with open(facts_file, 'r', encoding='utf-8') as f:
            facts_content = f.read()
        
        confirmed_items = triage_data.get("CONFIRMED", [])
        
        # V-Overlayデータ抽出
        ev_sales, rule_of_40 = self.extract_v_overlay_data(confirmed_items)
        
        # データ充足度チェック
        data_sufficiency = self.check_data_sufficiency(ev_sales, rule_of_40)
        
        if not data_sufficiency:
            # データ不足時は未判定
            category = "UNDETERMINED"
            star = 0
            explanation = "EV/S×Ro40データ不足→未判定"
        else:
            # カテゴリ判定
            category = self.calculate_category(ev_sales, rule_of_40)
            star = self.calculate_star(category)
            explanation = self._generate_explanation(ev_sales, rule_of_40, category, star)
        
        return VOverlayFailSafeResult(
            ev_sales=ev_sales,
            rule_of_40=rule_of_40,
            data_sufficiency=data_sufficiency,
            category=category,
            star=star,
            explanation=explanation
        )
    
    def _generate_explanation(self, ev_sales: float, rule_of_40: float, 
                            category: str, star: int) -> str:
        """説明文生成"""
        parts = []
        
        parts.append(f"EV/S:{ev_sales:.1f}x")
        parts.append(f"Ro40:{rule_of_40:.1f}")
        parts.append(f"→{category}★{star}")
        
        return " ".join(parts)

def process_v_overlay_failsafe_analysis(triage_file: str, facts_file: str) -> Dict[str, Any]:
    """V-Overlay Fail-safe分析処理の実行"""
    
    engine = VOverlayFailSafeEngine()
    result = engine.evaluate(triage_file, facts_file)
    
    return {
        "as_of": json.load(open(triage_file, 'r', encoding='utf-8'))["as_of"],
        "ticker": json.load(open(triage_file, 'r', encoding='utf-8')).get("ticker", ""),
        "v_overlay_failsafe": {
            "ev_sales": result.ev_sales,
            "rule_of_40": result.rule_of_40,
            "data_sufficiency": result.data_sufficiency,
            "category": result.category,
            "star": result.star
        },
        "explanation": result.explanation,
        "notes": {
            "v_overlay.failsafe_rule": "EV/S×Ro40のみ・未投入は未判定"
        }
    }

def main():
    if len(sys.argv) != 3:
        print("使用方法: python ahf_v_overlay_failsafe_v072.py <triage.jsonのパス> <facts.mdのパス>")
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
        results = process_v_overlay_failsafe_analysis(triage_file, facts_file)
        
        # 結果出力
        print("=== AHF V-Overlay Fail-safe Analysis Results (v0.7.2β) ===")
        print(f"As of: {results['as_of']}")
        print(f"Ticker: {results['ticker']}")
        print()
        print("【V-Overlay（VRG）】")
        print(f"EV/S: {results['v_overlay_failsafe']['ev_sales']:.1f}x" if results['v_overlay_failsafe']['ev_sales'] else "EV/S: N/A")
        print(f"Ro40: {results['v_overlay_failsafe']['rule_of_40']:.1f}" if results['v_overlay_failsafe']['rule_of_40'] else "Ro40: N/A")
        print(f"データ充足度: {results['v_overlay_failsafe']['data_sufficiency']}")
        print(f"カテゴリ: {results['v_overlay_failsafe']['category']}")
        print(f"★: {results['v_overlay_failsafe']['star']}")
        print(f"説明: {results['explanation']}")
        
        # 結果をJSONファイルに保存
        output_file = triage_file.replace("triage.json", "v_overlay_failsafe_analysis.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"[INFO] 結果を保存しました: {output_file}")
        
    except Exception as e:
        print(f"[ERROR] 処理エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
