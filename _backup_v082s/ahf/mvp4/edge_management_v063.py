#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AHF v0.6.3 Edge管理システム
- P付き先行仮説で意思決定を加速
- 出自明示＋P/TTL/contradiction必須
- 採用基準：P≥70 & 矛盾なし
- 各軸Edge最大2件・脚注≤35字
"""

import json
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

class EdgeItem:
    def __init__(self, data: Dict[str, Any]):
        self.kpi = data.get('kpi', '')
        self.value = data.get('value', 0)
        self.unit = data.get('unit', '')
        self.asof = data.get('asof', '')
        self.confidence = data.get('confidence', 0)  # P値
        self.direction = data.get('direction', 'neutral')  # bullish/bearish/neutral
        self.source = data.get('source', '')
        self.ttl_days = data.get('ttl_days', 30)
        self.contradiction = data.get('contradiction', False)
        self.footnote = data.get('footnote', '')
        self.axis = data.get('axis', '')  # ①右肩/②勾配/③時間軸/④認知ギャップ
    
    def is_valid(self) -> bool:
        """採用基準：P≥70 & 矛盾なし"""
        return self.confidence >= 70 and not self.contradiction
    
    def is_expired(self) -> bool:
        """TTL期限チェック"""
        if not self.asof:
            return False
        try:
            asof_date = datetime.fromisoformat(self.asof.replace('Z', '+00:00'))
            expiry_date = asof_date + timedelta(days=self.ttl_days)
            return datetime.now() > expiry_date
        except:
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'kpi': self.kpi,
            'value': self.value,
            'unit': self.unit,
            'asof': self.asof,
            'confidence': self.confidence,
            'direction': self.direction,
            'source': self.source,
            'ttl_days': self.ttl_days,
            'contradiction': self.contradiction,
            'footnote': self.footnote,
            'axis': self.axis
        }

class EdgeManager:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.edges: List[EdgeItem] = []
        self.max_edges_per_axis = 2
        self.max_footnote_length = 35
    
    def add_edge(self, edge_data: Dict[str, Any]) -> bool:
        """Edge項目を追加"""
        edge = EdgeItem(edge_data)
        
        # 基本検証
        if not edge.kpi or not edge.source:
            return False
        
        # 脚注長さチェック
        if len(edge.footnote) > self.max_footnote_length:
            return False
        
        # 軸別Edge数制限
        axis_edges = [e for e in self.edges if e.axis == edge.axis]
        if len(axis_edges) >= self.max_edges_per_axis:
            return False
        
        # 重複チェック
        for existing in self.edges:
            if (existing.kpi == edge.kpi and 
                existing.source == edge.source and 
                existing.asof == edge.asof):
                return False
        
        self.edges.append(edge)
        return True
    
    def get_valid_edges(self) -> List[EdgeItem]:
        """有効なEdge項目を取得"""
        return [e for e in self.edges if e.is_valid() and not e.is_expired()]
    
    def get_edges_by_axis(self, axis: str) -> List[EdgeItem]:
        """軸別Edge項目を取得"""
        return [e for e in self.get_valid_edges() if e.axis == axis]
    
    def calculate_star_adjustment(self) -> int:
        """Star調整値計算（±1★）"""
        valid_edges = self.get_valid_edges()
        adjustment = 0
        
        for edge in valid_edges:
            if edge.direction == 'bullish':
                adjustment += 1
            elif edge.direction == 'bearish':
                adjustment -= 1
        
        # 相殺可能
        return max(-1, min(1, adjustment))
    
    def calculate_confidence_adjustment(self) -> int:
        """確信度調整値計算（±5pp、1回のみ）"""
        valid_edges = self.get_valid_edges()
        if not valid_edges:
            return 0
        
        # 強気Edgeが1つでもあれば+5pp、そうでなければ-5pp
        has_bullish = any(e.direction == 'bullish' for e in valid_edges)
        return 5 if has_bullish else -5
    
    def get_edge_summary(self) -> Dict[str, Any]:
        """Edge要約情報"""
        valid_edges = self.get_valid_edges()
        
        summary = {
            'total_edges': len(valid_edges),
            'by_axis': {},
            'star_adjustment': self.calculate_star_adjustment(),
            'confidence_adjustment': self.calculate_confidence_adjustment(),
            'expired_count': len([e for e in self.edges if e.is_expired()]),
            'invalid_count': len([e for e in self.edges if not e.is_valid()])
        }
        
        # 軸別集計
        for axis in ['①右肩', '②勾配', '③時間軸', '④認知ギャップ']:
            axis_edges = self.get_edges_by_axis(axis)
            summary['by_axis'][axis] = {
                'count': len(axis_edges),
                'bullish': len([e for e in axis_edges if e.direction == 'bullish']),
                'bearish': len([e for e in axis_edges if e.direction == 'bearish'])
            }
        
        return summary
    
    def export_to_backlog(self) -> List[Dict[str, Any]]:
        """backlog.md用のEdge項目をエクスポート"""
        backlog_items = []
        
        for edge in self.edges:
            if not edge.is_valid() or edge.is_expired():
                backlog_items.append({
                    'id': f"edge_{edge.kpi}_{edge.asof}",
                    'class': 'EDGE',
                    'kpi': edge.kpi,
                    'current_evidence': edge.footnote[:40],  # ≤40語
                    'source': edge.source,
                    'missing_for_t1': f"P<70 or contradiction" if not edge.is_valid() else "TTL expired",
                    'next_action': 'Re-validate or upgrade to T1',
                    'related_impact': edge.axis,
                    'unavailability_reason': 'edge_insufficient_confidence' if not edge.is_valid() else 'edge_ttl_expired',
                    'grace_until': (datetime.now() + timedelta(days=7)).isoformat()
                })
        
        return backlog_items
    
    def export_to_triage(self) -> Dict[str, Any]:
        """triage.json用のEdge項目をエクスポート"""
        triage = {
            'as_of': datetime.now().isoformat()[:10],
            'CONFIRMED': [],
            'UNCERTAIN': []
        }
        
        for edge in self.edges:
            if edge.is_valid() and not edge.is_expired():
                # T1に昇格可能なEdge
                triage['CONFIRMED'].append({
                    'kpi': edge.kpi,
                    'value': edge.value,
                    'unit': edge.unit,
                    'asof': edge.asof,
                    'tag': 'T1-adj',
                    'url': edge.source,
                    'confidence': edge.confidence
                })
            else:
                # UNCERTAINとして保持
                triage['UNCERTAIN'].append({
                    'kpi': edge.kpi,
                    'status': 'blocked_source' if not edge.is_valid() else 'not_found',
                    'url_index': edge.source,
                    'confidence': edge.confidence,
                    'ttl_days': edge.ttl_days
                })
        
        return triage

def main():
    """CLI実行"""
    if len(sys.argv) < 2:
        print("Usage: python edge_management_v063.py <config.json>")
        sys.exit(1)
    
    config_path = sys.argv[1]
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 標準入力からEdgeデータを読み込み
    edge_data = json.load(sys.stdin)
    
    # Edge管理実行
    manager = EdgeManager(config)
    
    # Edge項目を追加
    for edge in edge_data.get('edges', []):
        manager.add_edge(edge)
    
    # 結果出力
    results = {
        'edge_summary': manager.get_edge_summary(),
        'backlog_items': manager.export_to_backlog(),
        'triage_data': manager.export_to_triage()
    }
    
    json.dump(results, sys.stdout, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()

