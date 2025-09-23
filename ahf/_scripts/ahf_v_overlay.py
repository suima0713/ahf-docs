#!/usr/bin/env python3
"""
AHF V-Overlay (Valuation Overlay) v1.0
バリュエーション専用オーバーレイ判定システム

事業T1の星評価は維持し、価格面を別レイヤーで判定・表示する仕組み
"""

import json
import yaml
import sys
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class VLevel(Enum):
    """V-Overlay レベル定義"""
    GREEN = "Green"    # 割安フラグ
    AMBER = "Amber"    # 割高フラグ  
    RED = "Red"        # 過熱フラグ

@dataclass
class VOverlayResult:
    """V-Overlay 判定結果"""
    level: VLevel
    reason: str
    ev_sales_fwd: Optional[float] = None
    rule_of_40: Optional[float] = None
    guidance_upside: bool = False
    star_cap_applied: bool = False

class VOverlayCalculator:
    """V-Overlay 計算エンジン"""
    
    def __init__(self):
        # V-Overlay ルール定義（固定しきい値）
        self.thresholds = {
            "ev_sales_fwd": {
                "green_max": 6.0,    # V3: 割安フラグ
                "amber_max": 10.0,   # V1: 割高フラグ
                "red_min": 14.0      # V2: 過熱フラグ
            },
            "rule_of_40_min": 40.0   # V4: 耐性チェック
        }
    
    def calculate_ev_sales_fwd(self, market_data: Dict[str, Any]) -> Optional[float]:
        """EV/Sales(Fwd) 計算"""
        try:
            enterprise_value = market_data.get("enterprise_value")
            sales_fwd = market_data.get("sales_fwd_12m")
            
            if enterprise_value and sales_fwd and sales_fwd > 0:
                return enterprise_value / sales_fwd
            return None
        except (TypeError, ZeroDivisionError):
            return None
    
    def calculate_rule_of_40(self, financial_data: Dict[str, Any]) -> Optional[float]:
        """Rule-of-40 計算: 成長率 + Adj.EBITDA%"""
        try:
            growth_rate = financial_data.get("revenue_growth_rate", 0)
            adj_ebitda_margin = financial_data.get("adj_ebitda_margin", 0)
            
            if growth_rate is not None and adj_ebitda_margin is not None:
                return growth_rate + adj_ebitda_margin
            return None
        except (TypeError, ValueError):
            return None
    
    def check_guidance_upside(self, guidance_data: Dict[str, Any]) -> bool:
        """V5: ガイダンス上方修正チェック"""
        try:
            # 売上またはEBITDAのいずれかが上方修正されているかチェック
            revenue_upside = guidance_data.get("revenue_guidance_upside", False)
            ebitda_upside = guidance_data.get("ebitda_guidance_upside", False)
            
            return revenue_upside or ebitda_upside
        except (TypeError, AttributeError):
            return False
    
    def apply_v_overlay_rules(self, market_data: Dict[str, Any], 
                            financial_data: Dict[str, Any],
                            guidance_data: Dict[str, Any]) -> VOverlayResult:
        """V-Overlay ルール適用"""
        
        # 基本指標計算
        ev_sales_fwd = self.calculate_ev_sales_fwd(market_data)
        rule_of_40 = self.calculate_rule_of_40(financial_data)
        guidance_upside = self.check_guidance_upside(guidance_data)
        
        # V1-V3: EV/Sales(Fwd) ベース判定
        initial_level = VLevel.GREEN
        reason_parts = []
        
        if ev_sales_fwd is not None:
            if ev_sales_fwd >= self.thresholds["ev_sales_fwd"]["red_min"]:
                initial_level = VLevel.RED
                reason_parts.append(f"EV/Sales(Fwd) {ev_sales_fwd:.1f}× (過熱域)")
            elif ev_sales_fwd >= self.thresholds["ev_sales_fwd"]["amber_max"]:
                initial_level = VLevel.AMBER
                reason_parts.append(f"EV/Sales(Fwd) {ev_sales_fwd:.1f}× (割高域)")
            elif ev_sales_fwd <= self.thresholds["ev_sales_fwd"]["green_max"]:
                initial_level = VLevel.GREEN
                reason_parts.append(f"EV/Sales(Fwd) {ev_sales_fwd:.1f}× (割安域)")
        
        # V4: Rule-of-40 耐性チェック（一段悪化）
        final_level = initial_level
        if rule_of_40 is not None and rule_of_40 < self.thresholds["rule_of_40_min"]:
            if initial_level == VLevel.GREEN:
                final_level = VLevel.AMBER
                reason_parts.append(f"Rule-of-40 {rule_of_40:.1f}% (耐性不足)")
            elif initial_level == VLevel.AMBER:
                final_level = VLevel.RED
                reason_parts.append(f"Rule-of-40 {rule_of_40:.1f}% (耐性不足)")
        
        # V5: ガイダンス上方修正（一段改善）
        if guidance_upside:
            if final_level == VLevel.RED:
                final_level = VLevel.AMBER
                reason_parts.append("ガイダンス上方修正")
            elif final_level == VLevel.AMBER:
                final_level = VLevel.GREEN
                reason_parts.append("ガイダンス上方修正")
        
        # 理由の組み立て
        reason = " / ".join(reason_parts) if reason_parts else "データ不足"
        
        # ★上限自動キャップ判定
        star_cap_applied = (final_level == VLevel.RED)
        
        return VOverlayResult(
            level=final_level,
            reason=reason,
            ev_sales_fwd=ev_sales_fwd,
            rule_of_40=rule_of_40,
            guidance_upside=guidance_upside,
            star_cap_applied=star_cap_applied
        )
    
    def generate_v_badge(self, result: VOverlayResult) -> str:
        """Vバッジ表示用文字列生成"""
        level_symbols = {
            VLevel.GREEN: "🟢",
            VLevel.AMBER: "🟡", 
            VLevel.RED: "🔴"
        }
        
        symbol = level_symbols.get(result.level, "⚪")
        return f"{symbol} V={result.level.value}"

def load_ticker_data(ticker_path: str) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    """ティッカーデータ読み込み"""
    ticker_dir = Path(ticker_path)
    
    # B.yaml (マーケットデータ含む)
    b_yaml_path = ticker_dir / "current" / "B.yaml"
    market_data = {}
    if b_yaml_path.exists():
        with open(b_yaml_path, 'r', encoding='utf-8') as f:
            b_data = yaml.safe_load(f)
            # マーケットデータの抽出（実際の構造に応じて調整）
            market_data = b_data.get("market", {})
    
    # facts.md から財務データ抽出
    facts_path = ticker_dir / "current" / "facts.md"
    financial_data = {}
    if facts_path.exists():
        with open(facts_path, 'r', encoding='utf-8') as f:
            facts_content = f.read()
            # 簡易的な財務データ抽出（実際はより詳細な解析が必要）
            financial_data = extract_financial_metrics(facts_content)
    
    # ガイダンスデータ（簡易実装）
    guidance_data = {
        "revenue_guidance_upside": False,  # 実際のガイダンス解析結果
        "ebitda_guidance_upside": False
    }
    
    return market_data, financial_data, guidance_data

def extract_financial_metrics(facts_content: str) -> Dict[str, Any]:
    """facts.md から財務メトリクス抽出"""
    metrics = {}
    
    # 簡易的な数値抽出（実際はより詳細な解析が必要）
    lines = facts_content.split('\n')
    for line in lines:
        if '成長率' in line or 'growth' in line.lower():
            # 成長率抽出ロジック
            pass
        elif 'EBITDA' in line:
            # EBITDAマージン抽出ロジック
            pass
    
    return metrics

def main():
    """メイン実行"""
    if len(sys.argv) != 2:
        print("使用法: python ahf_v_overlay.py <ticker_path>")
        sys.exit(1)
    
    ticker_path = sys.argv[1]
    
    try:
        # データ読み込み
        market_data, financial_data, guidance_data = load_ticker_data(ticker_path)
        
        # V-Overlay 計算
        calculator = VOverlayCalculator()
        result = calculator.apply_v_overlay_rules(market_data, financial_data, guidance_data)
        
        # 結果表示
        v_badge = calculator.generate_v_badge(result)
        print(f"V-Overlay判定: {v_badge}")
        print(f"理由: {result.reason}")
        
        if result.ev_sales_fwd is not None:
            print(f"EV/Sales(Fwd): {result.ev_sales_fwd:.1f}×")
        
        if result.rule_of_40 is not None:
            print(f"Rule-of-40: {result.rule_of_40:.1f}%")
        
        if result.guidance_upside:
            print("ガイダンス上方修正: あり")
        
        if result.star_cap_applied:
            print("[CRITICAL] ★上限=3の自動キャップ発動")
        
        # JSON形式で結果保存
        output_path = Path(ticker_path) / "current" / "v_overlay_result.json"
        result_dict = {
            "as_of": str(Path().cwd()),
            "v_level": result.level.value,
            "reason": result.reason,
            "ev_sales_fwd": result.ev_sales_fwd,
            "rule_of_40": result.rule_of_40,
            "guidance_upside": result.guidance_upside,
            "star_cap_applied": result.star_cap_applied,
            "v_badge": v_badge
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=2)
        
        print(f"結果を保存: {output_path}")
        
    except Exception as e:
        print(f"エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
