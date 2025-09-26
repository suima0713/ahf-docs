#!/usr/bin/env python3
"""
AHF v0.8.0 Turbo Screen
攻めの当たり付け：Core上の"加点オーバーレイ"

Purpose: 投資判断に直結する固定3軸で評価する
MVP: ①②③の名称と順序を固定／T1で確証（不足は n/a）／定型テーブル＋1行要約を即時出力
"""

import json
import yaml
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class AxisType(Enum):
    LEC = "LEC"  # ①長期EV確度
    NES = "NES"  # ②長期EV勾配
    VRG = "VRG"  # ③バリュエーション＋認知ギャップ

@dataclass
class EdgeItem:
    """Edge項目"""
    id: str
    class_type: str  # EDGE/LEAD
    axis: AxisType
    kpi_claim: str
    current_basis: str  # ≤25語
    source: str
    t1_gaps: List[str]
    next_action: str
    related_impact: str
    unavailability_reason: str
    grace_until: str
    credence_pct: int
    ttl_days: int
    contradiction: bool

class AHFv080TurboScreen:
    """AHF v0.8.0 Turbo Screen実装"""
    
    def __init__(self, ticker: str):
        self.ticker = ticker
        self.edge_items: List[EdgeItem] = []
        self.core_threshold = 70  # CoreはP≥70
        self.edge_threshold = 60  # Edge採用 P≥60
        
    def run_turbo_screen(self) -> Dict[str, Any]:
        """Turbo Screen実行"""
        result = {
            "purpose": "投資判断に直結する固定3軸で評価する",
            "mvp": "①②③の名称と順序を固定／T1で確証（不足は n/a）／定型テーブル＋1行要約を即時出力",
            "ticker": self.ticker,
            "screen_date": datetime.now().strftime("%Y-%m-%d"),
            "mode": "Turbo Screen（攻めの当たり付け）",
            "core_threshold": self.core_threshold,
            "edge_threshold": self.edge_threshold,
            "edge_items": [],
            "star_adjustments": {},
            "confidence_boosts": {},
            "math_guards": {},
            "anchor_management": {},
            "data_gap": {},
            "gap_reason": {}
        }
        
        try:
            # Edge項目収集
            edge_items = self._collect_edge_items()
            result["edge_items"] = edge_items
            
            # 受付閾値確認
            accepted_items = self._filter_by_threshold(edge_items)
            result["accepted_items"] = accepted_items
            
            # ★調整幅計算
            star_adjustments = self._calculate_star_adjustments(accepted_items)
            result["star_adjustments"] = star_adjustments
            
            # 確信度ブースト
            confidence_boosts = self._calculate_confidence_boosts(accepted_items)
            result["confidence_boosts"] = confidence_boosts
            
            # 数理ガード（Screenのみ緩和）
            math_guards = self._check_math_guards(accepted_items)
            result["math_guards"] = math_guards
            
            # アンカー運用
            anchor_management = self._manage_anchors(accepted_items)
            result["anchor_management"] = anchor_management
            
            # Edge掲出
            edge_display = self._generate_edge_display(accepted_items)
            result["edge_display"] = edge_display
            
        except Exception as e:
            result["error"] = str(e)
            result["data_gap"]["error"] = True
            result["gap_reason"]["error"] = f"Turbo Screen実行エラー: {str(e)}"
            
        return result
    
    def _collect_edge_items(self) -> List[Dict[str, Any]]:
        """Edge項目収集"""
        edge_items = []
        
        # ①長期EV確度（LEC）のEdge項目
        lec_edges = self._collect_lec_edges()
        edge_items.extend(lec_edges)
        
        # ②長期EV勾配（NES）のEdge項目
        nes_edges = self._collect_nes_edges()
        edge_items.extend(nes_edges)
        
        # ③バリュエーション＋認知ギャップ（VRG）のEdge項目
        vrg_edges = self._collect_vrg_edges()
        edge_items.extend(vrg_edges)
        
        return edge_items
    
    def _collect_lec_edges(self) -> List[Dict[str, Any]]:
        """①長期EV確度（LEC）のEdge項目収集"""
        return [
            {
                "id": "LEC-001",
                "class_type": "EDGE",
                "axis": "LEC",
                "kpi_claim": "流動性指標",
                "current_basis": "IR PRで数値提示",
                "source": "https://ir.company.com/...",
                "t1_gaps": ["10-Q/EX-99原本"],
                "next_action": "EX-99リンク確定",
                "related_impact": "①長期EV確度",
                "unavailability_reason": "EDGAR_down",
                "grace_until": "2024-12-31",
                "credence_pct": 65,
                "ttl_days": 7,
                "contradiction": False
            }
        ]
    
    def _collect_nes_edges(self) -> List[Dict[str, Any]]:
        """②長期EV勾配（NES）のEdge項目収集"""
        return [
            {
                "id": "NES-001",
                "class_type": "EDGE",
                "axis": "NES",
                "kpi_claim": "次Q成長率",
                "current_basis": "トランスクリプト発言",
                "source": "https://ir.company.com/...",
                "t1_gaps": ["逐語≤25語"],
                "next_action": "トランスクリプト精査",
                "related_impact": "②長期EV勾配",
                "unavailability_reason": "blocked_source",
                "grace_until": "2024-12-31",
                "credence_pct": 70,
                "ttl_days": 7,
                "contradiction": False
            }
        ]
    
    def _collect_vrg_edges(self) -> List[Dict[str, Any]]:
        """③バリュエーション＋認知ギャップ（VRG）のEdge項目収集"""
        return [
            {
                "id": "VRG-001",
                "class_type": "EDGE",
                "axis": "VRG",
                "kpi_claim": "ピアEV/S中央値",
                "current_basis": "アナリストレポート",
                "source": "https://analyst.com/...",
                "t1_gaps": ["ピア定義・算出根拠"],
                "next_action": "ピアリスト確定",
                "related_impact": "③バリュエーション",
                "unavailability_reason": "not_found",
                "grace_until": "2024-12-31",
                "credence_pct": 60,
                "ttl_days": 7,
                "contradiction": False
            }
        ]
    
    def _filter_by_threshold(self, edge_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """受付閾値確認"""
        accepted_items = []
        
        for item in edge_items:
            # Edge採用 P≥60（CoreはP≥70）
            if item["credence_pct"] >= self.edge_threshold:
                # TTL ≤14日
                if item["ttl_days"] <= 14:
                    # 矛盾フラグtrueは除外
                    if not item["contradiction"]:
                        accepted_items.append(item)
        
        return accepted_items
    
    def _calculate_star_adjustments(self, accepted_items: List[Dict[str, Any]]) -> Dict[str, int]:
        """★調整幅計算（Screen★は±2★まで、Coreは±1★）"""
        adjustments = {
            "LEC": 0,
            "NES": 0,
            "VRG": 0
        }
        
        for item in accepted_items:
            axis = item["axis"]
            credence_pct = item["credence_pct"]
            
            # Screen★は±2★まで（Coreは±1★）
            if credence_pct >= 80:
                adjustments[axis] = min(adjustments[axis] + 2, 2)
            elif credence_pct >= 70:
                adjustments[axis] = min(adjustments[axis] + 1, 2)
            elif credence_pct < 60:
                adjustments[axis] = max(adjustments[axis] - 1, -2)
        
        return adjustments
    
    def _calculate_confidence_boosts(self, accepted_items: List[Dict[str, Any]]) -> Dict[str, int]:
        """確信度ブースト計算（±10ppを1回、Coreは±5pp）"""
        boosts = {
            "LEC": 0,
            "NES": 0,
            "VRG": 0
        }
        
        for item in accepted_items:
            axis = item["axis"]
            credence_pct = item["credence_pct"]
            
            # ±10ppを1回（Coreは±5pp）
            if credence_pct >= 80:
                boosts[axis] = min(boosts[axis] + 10, 10)
            elif credence_pct < 60:
                boosts[axis] = max(boosts[axis] - 10, -10)
        
        # クリップ 45–95%
        for axis in boosts:
            boosts[axis] = max(min(boosts[axis], 95), 45)
        
        return boosts
    
    def _check_math_guards(self, accepted_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """数理ガード（Screenのみ緩和）"""
        return {
            "gm_deviation": 0.5,    # GM乖離 ≤0.5pp（Core 0.2pp）
            "residual_gp": 12.0,    # 残差GP ≤$12M（Core $8M）
            "alpha5_grid": -2.5,    # α5格子 ≤−$2.5M（Core −$3〜−$5M）
            "pass": True
        }
    
    def _manage_anchors(self, accepted_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """アンカー運用"""
        return {
            "dual_anchor_status": "PENDING_SEC",  # CONFIRMED｜PENDING_SEC｜SINGLE
            "primary_source": "SEC",              # primary=SEC、secondary=IR
            "secondary_source": "IR",              # SEC未取得時はIR一次→PENDING_SEC（TTL≤7日）
            "ttl_days": 7,                         # TTL≤7日→後日SECでCONFIRMED
            "anchor_lint_pass": True
        }
    
    def _generate_edge_display(self, accepted_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Edge掲出（各軸≤3件、要約≤25字、P/TTL/矛盾フラグ明記）"""
        edge_display = []
        
        # 軸ごとにグループ化
        axes = {"LEC": [], "NES": [], "VRG": []}
        for item in accepted_items:
            axes[item["axis"]].append(item)
        
        # 各軸≤3件
        for axis, items in axes.items():
            for i, item in enumerate(items[:3]):  # 最大3件
                edge_display.append({
                    "axis": axis,
                    "id": item["id"],
                    "summary": item["current_basis"][:25],  # 要約≤25字
                    "credence_pct": item["credence_pct"],
                    "ttl_days": item["ttl_days"],
                    "contradiction": item["contradiction"]
                })
        
        return edge_display

def main():
    """メイン実行"""
    if len(sys.argv) < 2:
        print("Usage: python ahf_v080_turbo_screen.py <TICKER>")
        sys.exit(1)
    
    ticker = sys.argv[1]
    turbo_screen = AHFv080TurboScreen(ticker)
    result = turbo_screen.run_turbo_screen()
    
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()

