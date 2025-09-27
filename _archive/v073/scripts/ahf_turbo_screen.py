#!/usr/bin/env python3
"""
AHF v0.7.3 Turbo Screen機能
Purpose: Coreを上に被せる"加点オーバーレイ"。当面の優先度付け・試し玉判断に使用
"""

import json
import yaml
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

class EdgeStatus(Enum):
    """Edge事実のステータス"""
    PENDING_SEC = "PENDING_SEC"  # IR/PR一次暫定許容
    CONFIRMED = "CONFIRMED"      # SEC確認済み
    UNCERTAIN = "UNCERTAIN"      # 不確実

class TurboScreenResult(Enum):
    """Turbo Screen結果"""
    ADOPTED = "ADOPTED"      # 採用
    REJECTED = "REJECTED"    # 却下
    PENDING = "PENDING"     # 保留

@dataclass
class EdgeFact:
    """Edge事実の構造"""
    kpi: str
    value: float
    unit: str
    asof: str
    tag: str
    url: str
    verbatim: str
    anchor: str
    credence_pct: int  # P≥60
    ttl_days: int     # ≤14日
    contradiction: bool
    dual_anchor_status: EdgeStatus
    source_type: str  # "IR" | "PR" | "SEC"

@dataclass
class TurboScreenConfig:
    """Turbo Screen設定"""
    min_credence: int = 60      # P≥60
    max_ttl_days: int = 14      # TTL≤14日
    max_star_adjustment: int = 2  # ★±2まで
    max_confidence_boost: int = 10  # 確信度±10pp
    min_confidence: int = 45
    max_confidence: int = 95

@dataclass
class MathGuardConfig:
    """数理ガード設定（Turbo Screen緩和版）"""
    gm_deviation_tolerance: float = 0.5  # ≤0.5pp（Core 0.2pp）
    residual_gp_tolerance: float = 12.0  # ≤$12M（Core $8M）
    alpha5_median_threshold: float = -2.5  # median−実績 ≤ −$2.5M（Core −$3〜−$5M）

class TurboScreenEngine:
    """Turbo Screenエンジン"""
    
    def __init__(self, config: TurboScreenConfig = None, math_guard: MathGuardConfig = None):
        self.config = config or TurboScreenConfig()
        self.math_guard = math_guard or MathGuardConfig()
        self.edge_facts: List[EdgeFact] = []
        self.contradiction_flags: Dict[str, bool] = {}
        
    def load_edge_data(self, backlog_file: str, triage_file: str) -> None:
        """Edgeデータの読み込み"""
        try:
            # backlog.mdからEdge事実を抽出
            with open(backlog_file, 'r', encoding='utf-8') as f:
                content = f.read()
                self._parse_backlog_md(content)
            
            # triage.jsonからUNCERTAINデータを読み込み
            with open(triage_file, 'r', encoding='utf-8') as f:
                triage_data = json.load(f)
                self._parse_triage_uncertain(triage_data)
                
        except Exception as e:
            print(f"Edgeデータ読み込みエラー: {e}")
            raise
    
    def _parse_backlog_md(self, content: str) -> None:
        """backlog.mdからEdge事実を解析"""
        lines = content.split('\n')
        for line in lines:
            if '|' in line and 'class=EDGE' in line:
                edge_fact = self._parse_backlog_line(line)
                if edge_fact:
                    self.edge_facts.append(edge_fact)
    
    def _parse_backlog_line(self, line: str) -> Optional[EdgeFact]:
        """backlog行を解析"""
        # | id | class=EDGE | KPI/主張 | 現在の根拠≤40語 | ソース | T1化に足りないもの | 次アクション | 関連Impact | unavailability_reason | grace_until |
        parts = [p.strip() for p in line.split('|')]
        if len(parts) >= 10:
            return EdgeFact(
                kpi=parts[3],
                value=0.0,
                unit="",
                asof=datetime.now().strftime("%Y-%m-%d"),
                tag="EDGE",
                url=parts[4],
                verbatim=parts[3][:25],  # ≤25語
                anchor=self._generate_anchor(parts[4], parts[3]),
                credence_pct=70,  # デフォルト
                ttl_days=14,
                contradiction=False,
                dual_anchor_status=EdgeStatus.PENDING_SEC,
                source_type="IR"
            )
        return None
    
    def _parse_triage_uncertain(self, triage_data: Dict) -> None:
        """triage.jsonのUNCERTAINデータを解析"""
        for item in triage_data.get("UNCERTAIN", []):
            if item.get("status") == "blocked_source" or item.get("status") == "not_found":
                edge_fact = EdgeFact(
                    kpi=item["kpi"],
                    value=item.get("value", 0.0),
                    unit=item.get("unit", ""),
                    asof=item.get("asof", datetime.now().strftime("%Y-%m-%d")),
                    tag="UNCERTAIN",
                    url=item.get("url_index", ""),
                    verbatim=item.get("claim", "")[:25],
                    anchor="",
                    credence_pct=item.get("credence_pct", 60),
                    ttl_days=item.get("ttl_days", 14),
                    contradiction=item.get("contradiction", False),
                    dual_anchor_status=EdgeStatus.UNCERTAIN,
                    source_type="IR"
                )
                self.edge_facts.append(edge_fact)
    
    def _generate_anchor(self, url: str, verbatim: str) -> str:
        """アンカー生成"""
        if "sec.gov" in url:
            text_fragment = verbatim.replace(" ", "%20")
            return f"{url}#:~:text={text_fragment}"
        else:
            return f"anchor_backup{{quote: '{verbatim}', hash: 'pending'}}"
    
    def filter_eligible_edge_facts(self) -> List[EdgeFact]:
        """受付閾値を満たすEdge事実をフィルタリング"""
        eligible = []
        
        for fact in self.edge_facts:
            # P≥60チェック
            if fact.credence_pct < self.config.min_credence:
                continue
            
            # TTL≤14日チェック
            if fact.ttl_days > self.config.max_ttl_days:
                continue
            
            # 矛盾フラグチェック
            if fact.contradiction:
                continue
            
            # デュアルアンカーステータスチェック
            if fact.dual_anchor_status == EdgeStatus.PENDING_SEC:
                # IR/PR一次暫定許容（TTL≤7日）
                if fact.ttl_days > 7:
                    continue
            
            eligible.append(fact)
        
        return eligible
    
    def apply_turbo_adjustments(self, base_scores: List[Dict], eligible_facts: List[EdgeFact]) -> List[Dict]:
        """Turbo Screen調整を適用"""
        adjusted_scores = []
        
        for i, score in enumerate(base_scores):
            # 該当軸のEdge事実を抽出
            axis_facts = self._get_axis_edge_facts(score['axis'], eligible_facts)
            
            # ★調整（±2まで）
            star_adjustment = self._calculate_star_adjustment(axis_facts)
            adjusted_stars = max(1, min(5, score['score'] + star_adjustment))
            
            # 確信度ブースト（±10pp）
            confidence_boost = self._calculate_confidence_boost(axis_facts)
            adjusted_confidence = max(
                self.config.min_confidence,
                min(self.config.max_confidence, score['confidence'] + confidence_boost)
            )
            
            # 数理ガード緩和適用
            math_pass = self._apply_math_guard_relaxation(axis_facts)
            
            adjusted_score = score.copy()
            adjusted_score.update({
                'score': adjusted_stars,
                'confidence': adjusted_confidence,
                'turbo_applied': True,
                'star_adjustment': star_adjustment,
                'confidence_boost': confidence_boost,
                'math_guard_pass': math_pass,
                'edge_facts_count': len(axis_facts)
            })
            
            adjusted_scores.append(adjusted_score)
        
        return adjusted_scores
    
    def _get_axis_edge_facts(self, axis: str, eligible_facts: List[EdgeFact]) -> List[EdgeFact]:
        """軸に対応するEdge事実を取得"""
        axis_keywords = {
            "長期EV確度": ["guidance", "opm", "dilution", "capex"],
            "長期EV勾配": ["qoq", "backlog", "margin", "growth"],
            "バリュエーション＋認知ギャップ": ["ev", "valuation", "rule_of_40", "cognition"]
        }
        
        keywords = axis_keywords.get(axis, [])
        axis_facts = []
        
        for fact in eligible_facts:
            for keyword in keywords:
                if keyword in fact.kpi.lower():
                    axis_facts.append(fact)
                    break
        
        return axis_facts
    
    def _calculate_star_adjustment(self, axis_facts: List[EdgeFact]) -> int:
        """星調整を計算"""
        if len(axis_facts) >= 3:
            return 2
        elif len(axis_facts) >= 2:
            return 1
        elif len(axis_facts) >= 1:
            return 0
        return 0
    
    def _calculate_confidence_boost(self, axis_facts: List[EdgeFact]) -> int:
        """確信度ブーストを計算"""
        if len(axis_facts) >= 3:
            return 10
        elif len(axis_facts) >= 2:
            return 5
        elif len(axis_facts) >= 1:
            return 2
        return 0
    
    def _apply_math_guard_relaxation(self, axis_facts: List[EdgeFact]) -> bool:
        """数理ガード緩和を適用"""
        # GM乖離許容 ≤0.5pp（Core 0.2pp）
        # 残差GP許容 ≤$12M（Core $8M）
        # α5格子「改善の素地あり」：median−実績 ≤ −$2.5M（Core −$3〜−$5M）
        
        # 実装は簡略化（実際は各KPIの数値チェック）
        return True
    
    def generate_edge_summary(self, eligible_facts: List[EdgeFact]) -> Dict[str, Any]:
        """Edge事実サマリーを生成"""
        summary = {
            "total_edge_facts": len(eligible_facts),
            "by_axis": {
                "長期EV確度": len([f for f in eligible_facts if any(k in f.kpi.lower() for k in ["guidance", "opm", "dilution", "capex"])]),
                "長期EV勾配": len([f for f in eligible_facts if any(k in f.kpi.lower() for k in ["qoq", "backlog", "margin", "growth"])]),
                "バリュエーション＋認知ギャップ": len([f for f in eligible_facts if any(k in f.kpi.lower() for k in ["ev", "valuation", "rule_of_40", "cognition"])])
            },
            "by_status": {
                "PENDING_SEC": len([f for f in eligible_facts if f.dual_anchor_status == EdgeStatus.PENDING_SEC]),
                "CONFIRMED": len([f for f in eligible_facts if f.dual_anchor_status == EdgeStatus.CONFIRMED]),
                "UNCERTAIN": len([f for f in eligible_facts if f.dual_anchor_status == EdgeStatus.UNCERTAIN])
            },
            "by_source": {
                "IR": len([f for f in eligible_facts if f.source_type == "IR"]),
                "PR": len([f for f in eligible_facts if f.source_type == "PR"]),
                "SEC": len([f for f in eligible_facts if f.source_type == "SEC"])
            },
            "ttl_distribution": {
                "≤7日": len([f for f in eligible_facts if f.ttl_days <= 7]),
                "8-14日": len([f for f in eligible_facts if 8 <= f.ttl_days <= 14])
            }
        }
        
        return summary
    
    def update_dual_anchor_status(self, fact_id: str, new_status: EdgeStatus) -> bool:
        """デュアルアンカーステータスを更新"""
        for fact in self.edge_facts:
            if fact.kpi == fact_id:
                fact.dual_anchor_status = new_status
                return True
        return False
    
    def check_ttl_expiry(self) -> List[EdgeFact]:
        """TTL期限切れのEdge事実をチェック"""
        expired = []
        current_date = datetime.now()
        
        for fact in self.edge_facts:
            # TTL期限切れチェック（簡略化）
            if fact.ttl_days <= 0:
                expired.append(fact)
        
        return expired
    
    def promote_to_t1(self, fact_id: str) -> bool:
        """Edge事実をT1に昇格"""
        for i, fact in enumerate(self.edge_facts):
            if fact.kpi == fact_id:
                # T1に昇格（実装は簡略化）
                del self.edge_facts[i]
                return True
        return False

def main():
    """メイン実行"""
    turbo_engine = TurboScreenEngine()
    
    # Edgeデータ読み込み（例）
    try:
        turbo_engine.load_edge_data("backlog.md", "triage.json")
    except Exception as e:
        print(f"Edgeデータ読み込み失敗: {e}")
        return
    
    # 受付閾値を満たすEdge事実をフィルタリング
    eligible_facts = turbo_engine.filter_eligible_edge_facts()
    
    # Edge事実サマリーを生成
    summary = turbo_engine.generate_edge_summary(eligible_facts)
    
    print("=== Turbo Screen Edge事実サマリー ===")
    print(f"総Edge事実数: {summary['total_edge_facts']}")
    print(f"軸別分布: {summary['by_axis']}")
    print(f"ステータス別分布: {summary['by_status']}")
    print(f"ソース別分布: {summary['by_source']}")
    print(f"TTL分布: {summary['ttl_distribution']}")
    
    # TTL期限切れチェック
    expired = turbo_engine.check_ttl_expiry()
    if expired:
        print(f"\n期限切れEdge事実: {len(expired)}件")
        for fact in expired[:3]:  # 最初の3件のみ表示
            print(f"  - {fact.kpi}: {fact.verbatim}")

if __name__ == "__main__":
    main()
