#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AHF設定検証エンジン
YAML設定ファイルの構造と値の妥当性チェック
"""

import yaml
from typing import Dict, List, Any
from pathlib import Path

class ConfigValidator:
    """設定検証エンジン"""
    
    def __init__(self, config_dir: str = "../config"):
        self.config_dir = Path(config_dir)
    
    def validate_v_overlay_config(self, config: Dict) -> List[str]:
        """V-Overlay設定の検証"""
        errors = []
        
        # 必須キーの存在チェック
        required_keys = ["evsales", "rule_of_40", "hysteresis", "v_thresholds", "star_impact"]
        for key in required_keys:
            if key not in config:
                errors.append(f"必須キー '{key}' が存在しません")
        
        # 閾値の妥当性チェック
        if "evsales" in config:
            evsales = config["evsales"]
            if evsales.get("green_max", 0) >= evsales.get("red_min", 0):
                errors.append("EV/Sales: green_max >= red_min は無効です")
            if not (0 <= evsales.get("weight", 0) <= 1):
                errors.append("EV/Sales: weight は 0-1 の範囲である必要があります")
        
        if "v_thresholds" in config:
            thresholds = config["v_thresholds"]
            if not (0 <= thresholds.get("green_max", 0) <= 1):
                errors.append("V区分: green_max は 0-1 の範囲である必要があります")
            if not (0 <= thresholds.get("amber_max", 0) <= 1):
                errors.append("V区分: amber_max は 0-1 の範囲である必要があります")
            if thresholds.get("green_max", 0) >= thresholds.get("amber_max", 0):
                errors.append("V区分: green_max >= amber_max は無効です")
        
        return errors
    
    def validate_lexicon_config(self, config: Dict) -> List[str]:
        """辞書設定の検証"""
        errors = []
        
        # 必須キーの存在チェック
        required_keys = ["causal_verbs", "gm_aliases", "direction_up", "direction_down"]
        for key in required_keys:
            if key not in config:
                errors.append(f"必須キー '{key}' が存在しません")
            elif not isinstance(config[key], list):
                errors.append(f"'{key}' はリストである必要があります")
        
        # 因果動詞の重複チェック
        if "causal_verbs" in config:
            verbs = config["causal_verbs"]
            if len(verbs) != len(set(verbs)):
                errors.append("因果動詞に重複があります")
        
        return errors
    
    def validate_ticker_config(self, config: Dict) -> List[str]:
        """ティッカー設定の検証"""
        errors = []
        
        if "tickers" not in config:
            errors.append("必須キー 'tickers' が存在しません")
            return errors
        
        tickers = config["tickers"]
        if not isinstance(tickers, dict):
            errors.append("'tickers' は辞書である必要があります")
            return errors
        
        # 各ティッカーの必須フィールドチェック
        required_fields = ["cik", "ir_domain", "sector", "currency", "segment_name"]
        for ticker, ticker_config in tickers.items():
            for field in required_fields:
                if field not in ticker_config:
                    errors.append(f"ティッカー '{ticker}': 必須フィールド '{field}' が存在しません")
        
        return errors
    
    def validate_all_configs(self) -> Dict[str, List[str]]:
        """全設定ファイルの検証"""
        results = {}
        
        # V-Overlay設定の検証
        try:
            with open(self.config_dir / "v_overlay.yaml", 'r', encoding='utf-8') as f:
                v_config = yaml.safe_load(f)
            results["v_overlay"] = self.validate_v_overlay_config(v_config)
        except Exception as e:
            results["v_overlay"] = [f"ファイル読み込みエラー: {e}"]
        
        # 辞書設定の検証
        try:
            with open(self.config_dir / "lexicon.yaml", 'r', encoding='utf-8') as f:
                lexicon_config = yaml.safe_load(f)
            results["lexicon"] = self.validate_lexicon_config(lexicon_config)
        except Exception as e:
            results["lexicon"] = [f"ファイル読み込みエラー: {e}"]
        
        # ティッカー設定の検証
        try:
            with open(self.config_dir / "tickers.yaml", 'r', encoding='utf-8') as f:
                ticker_config = yaml.safe_load(f)
            results["tickers"] = self.validate_ticker_config(ticker_config)
        except Exception as e:
            results["tickers"] = [f"ファイル読み込みエラー: {e}"]
        
        return results

def main():
    """テスト実行"""
    validator = ConfigValidator()
    results = validator.validate_all_configs()
    
    print("=== AHF設定検証結果 ===")
    for config_name, errors in results.items():
        print(f"\n【{config_name}】")
        if not errors:
            print("✅ 検証OK")
        else:
            print("❌ エラー:")
            for error in errors:
                print(f"  - {error}")

if __name__ == "__main__":
    main()
