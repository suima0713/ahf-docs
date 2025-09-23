#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Edge逓減加点システム
ハード上限なし・最終★5クリップ・P/TTL/独立性係数併記
"""
import math
from typing import Dict, List, Any, Tuple
from datetime import datetime

class EdgeDegressiveScorer:
    def __init__(self):
        self.max_final_stars = 5.0  # 最終★5でクリップ
        
    def calculate_degressive_coefficient(self, edge_count: int) -> float:
        """
        逓減係数計算: 1.0 / (1.0 + Edge数 × 0.1)
        """
        return 1.0 / (1.0 + edge_count * 0.1)
    
    def calculate_edge_weight(self, p: float, ttl_days: int, independence: float, 
                            days_elapsed: int = 0) -> float:
        """
        Edge重み計算（P/TTL/独立性係数併記）
        """
        # P係数 (70-95の範囲を0-1に正規化)
        p_coefficient = (p - 70) / 25
        
        # TTL係数 (残り日数/総日数)
        ttl_coefficient = max(0.0, (ttl_days - days_elapsed) / ttl_days)
        
        # 独立性係数 (0-1の範囲)
        independence_coefficient = independence
        
        # 重み = P係数 × TTL係数 × 独立性係数
        weight = p_coefficient * ttl_coefficient * independence_coefficient
        
        return max(0.0, weight)  # 負の重みは0にクリップ
    
    def calculate_edge_bonus(self, edges: List[Dict[str, Any]], 
                           days_elapsed: int = 0) -> Dict[str, Any]:
        """
        Edge逓減加点計算
        """
        if not edges:
            return {
                'total_bonus': 0.0,
                'degressive_coefficient': 1.0,
                'final_bonus': 0.0,
                'edge_details': []
            }
        
        # 各Edgeの重み計算
        edge_details = []
        total_weight = 0.0
        
        for edge in edges:
            p = edge.get('p', 70)
            ttl_days = edge.get('ttl_days', 30)
            independence = edge.get('independence', 0.5)
            
            weight = self.calculate_edge_weight(p, ttl_days, independence, days_elapsed)
            total_weight += weight
            
            edge_details.append({
                'name': edge.get('name', 'Unknown'),
                'p': p,
                'ttl_days': ttl_days,
                'independence': independence,
                'weight': weight,
                'days_elapsed': days_elapsed
            })
        
        # 逓減係数計算
        edge_count = len(edges)
        degressive_coefficient = self.calculate_degressive_coefficient(edge_count)
        
        # 最終加点計算
        final_bonus = total_weight * degressive_coefficient
        
        return {
            'total_weight': total_weight,
            'degressive_coefficient': degressive_coefficient,
            'final_bonus': final_bonus,
            'edge_count': edge_count,
            'edge_details': edge_details
        }
    
    def apply_to_matrix(self, matrix_data: Dict[str, Any], 
                       edge_bonus: Dict[str, Any]) -> Dict[str, Any]:
        """
        マトリクスにEdge加点を適用
        """
        updated_matrix = matrix_data.copy()
        
        for axis in ['right_shoulder', 'slope_quality', 'time_profile', 'cognitive_gap']:
            if axis in updated_matrix:
                # 現在の★取得
                current_stars = updated_matrix[axis].get('core_rating', 0)
                if isinstance(current_stars, str):
                    current_stars = float(current_stars.replace('★', ''))
                
                # Edge加点適用
                new_stars = current_stars + edge_bonus['final_bonus']
                
                # 最終★5でクリップ
                final_stars = min(self.max_final_stars, new_stars)
                
                updated_matrix[axis]['core_rating'] = f"★{final_stars:.1f}"
                updated_matrix[axis]['edge_bonus'] = edge_bonus['final_bonus']
                updated_matrix[axis]['clipped'] = new_stars > self.max_final_stars
        
        return updated_matrix
    
    def format_edge_summary(self, edge_bonus: Dict[str, Any]) -> str:
        """Edge加点サマリを2行で表示"""
        if edge_bonus['edge_count'] == 0:
            return "Edge加点なし"
        
        # 1行目: 主要Edge
        top_edges = sorted(edge_bonus['edge_details'], 
                          key=lambda x: x['weight'], reverse=True)[:2]
        line1_parts = []
        for edge in top_edges:
            line1_parts.append(f"{edge['name']}(P{edge['p']}, 重み{edge['weight']:.2f})")
        
        # 2行目: 逓減係数と最終加点
        line2 = f"逓減係数{edge_bonus['degressive_coefficient']:.2f} → 最終加点+{edge_bonus['final_bonus']:.2f}★"
        
        return "\n".join([", ".join(line1_parts), line2])
    
    def simulate_edge_growth(self, base_edges: List[Dict[str, Any]], 
                           additional_edges: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Edge増加シミュレーション"""
        # 現在の加点
        current_bonus = self.calculate_edge_bonus(base_edges)
        
        # 追加後の加点
        all_edges = base_edges + additional_edges
        future_bonus = self.calculate_edge_bonus(all_edges)
        
        return {
            'current': current_bonus,
            'future': future_bonus,
            'improvement': future_bonus['final_bonus'] - current_bonus['final_bonus'],
            'efficiency_ratio': future_bonus['final_bonus'] / current_bonus['final_bonus'] if current_bonus['final_bonus'] > 0 else 0
        }

def main():
    """テスト実行"""
    scorer = EdgeDegressiveScorer()
    
    # RKLB Edge例
    edges = [
        {
            'name': 'AFRL REGAL契約',
            'p': 82,
            'ttl_days': 30,
            'independence': 0.8
        },
        {
            'name': 'VICTUS HAZE統合',
            'p': 78,
            'ttl_days': 21,
            'independence': 0.7
        },
        {
            'name': 'HASTE MACH-TB 2.0',
            'p': 76,
            'ttl_days': 30,
            'independence': 0.7
        }
    ]
    
    # 現在の加点計算
    current_bonus = scorer.calculate_edge_bonus(edges)
    summary = scorer.format_edge_summary(current_bonus)
    
    print("=== Edge逓減加点システム ===")
    print(summary)
    print(f"\n詳細:")
    print(f"Edge数: {current_bonus['edge_count']}")
    print(f"総重み: {current_bonus['total_weight']:.2f}")
    print(f"逓減係数: {current_bonus['degressive_coefficient']:.2f}")
    print(f"最終加点: +{current_bonus['final_bonus']:.2f}★")
    
    # 追加Edgeシミュレーション
    additional_edges = [
        {
            'name': '新規Edge④',
            'p': 85,
            'ttl_days': 30,
            'independence': 0.9
        }
    ]
    
    simulation = scorer.simulate_edge_growth(edges, additional_edges)
    print(f"\n追加Edge後:")
    print(f"改善幅: +{simulation['improvement']:.2f}★")
    print(f"効率比: {simulation['efficiency_ratio']:.2f}")

if __name__ == "__main__":
    main()
