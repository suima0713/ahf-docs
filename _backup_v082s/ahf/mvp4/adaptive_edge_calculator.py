#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Adaptive Edge Influence Calculator v4.1
連続±2（0.5刻み）上限・累積±10pp逓減のEdge重み計算
"""
import math
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta

class AdaptiveEdgeCalculator:
    def __init__(self):
        self.base_confidence = 0.0
        self.weekly_decay = -1.0  # 週次-1pp減衰
        
    def calculate_edge_weight(self, p: float, impact: float, independence: float, 
                            freshness: float) -> float:
        """
        Edge重み計算: w_i = ((P_i-70)/25) * Impact_i(1~3) * (0.6+0.4*Independence_i) * Freshness_i(0~1)
        """
        p_factor = (p - 70) / 25
        impact_factor = impact  # 1~3の範囲
        independence_factor = 0.6 + 0.4 * independence  # 0.6~1.0の範囲
        freshness_factor = freshness  # 0~1の範囲
        
        weight = p_factor * impact_factor * independence_factor * freshness_factor
        return max(0.0, weight)  # 負の重みは0にクリップ
    
    def calculate_star_adjustment(self, w_pos: float, w_neg: float) -> float:
        """
        ★調整: Δ★ = clip(round_to_0.5( 0.5 * (W_pos - W_neg) ), -2, +2)
        """
        raw_adjustment = 0.5 * (w_pos - w_neg)
        rounded = round(raw_adjustment * 2) / 2  # 0.5刻み
        return max(-2.0, min(2.0, rounded))  # -2~+2の範囲にクリップ
    
    def calculate_confidence_adjustment(self, w_pos: float, w_neg: float) -> float:
        """
        確信度調整: ΔConf(%) = clip( 4 * (W_pos - W_neg), -10, +10 )
        """
        raw_adjustment = 4 * (w_pos - w_neg)
        return max(-10.0, min(10.0, raw_adjustment))  # -10~+10の範囲にクリップ
    
    def calculate_freshness(self, ttl_days: int, days_elapsed: int) -> float:
        """
        鮮度計算: TTL減衰でFreshness→0
        """
        if ttl_days <= 0:
            return 0.0
        
        remaining_ratio = max(0.0, (ttl_days - days_elapsed) / ttl_days)
        return remaining_ratio
    
    def calculate_weekly_decay(self, weeks_elapsed: int) -> float:
        """
        週次減衰: -1pp/週
        """
        return self.weekly_decay * weeks_elapsed
    
    def process_edge_list(self, edges: List[Dict[str, Any]], 
                         days_elapsed: int = 0) -> Dict[str, Any]:
        """
        Edgeリストを処理して重み・調整値を計算
        """
        w_pos = 0.0
        w_neg = 0.0
        processed_edges = []
        
        for edge in edges:
            # 矛盾チェック
            if edge.get('contradiction', False):
                edge['weight'] = 0.0
                edge['star_contribution'] = 0.0
                edge['confidence_contribution'] = 0.0
                processed_edges.append(edge)
                continue
            
            # パラメータ取得
            p = edge.get('p', 70)
            impact = edge.get('impact', 1.0)
            independence = edge.get('independence', 0.5)
            ttl_days = edge.get('ttl_days', 30)
            
            # 鮮度計算
            freshness = self.calculate_freshness(ttl_days, days_elapsed)
            
            # 重み計算
            weight = self.calculate_edge_weight(p, impact, independence, freshness)
            
            # 正負の重みに分類
            if weight > 0:
                w_pos += weight
            else:
                w_neg += abs(weight)
            
            # Edge情報更新
            edge['weight'] = weight
            edge['freshness'] = freshness
            edge['star_contribution'] = 0.5 * weight
            edge['confidence_contribution'] = 4 * weight
            
            processed_edges.append(edge)
        
        # 全体調整値計算
        star_adjustment = self.calculate_star_adjustment(w_pos, w_neg)
        confidence_adjustment = self.calculate_confidence_adjustment(w_pos, w_neg)
        
        return {
            'edges': processed_edges,
            'total_w_pos': w_pos,
            'total_w_neg': w_neg,
            'star_adjustment': star_adjustment,
            'confidence_adjustment': confidence_adjustment,
            'days_elapsed': days_elapsed
        }
    
    def apply_to_matrix(self, matrix_data: Dict[str, Any], 
                       edge_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        マトリクスに調整値を適用
        """
        updated_matrix = matrix_data.copy()
        
        # ★調整適用
        for axis in ['right_shoulder', 'slope_quality', 'time_profile', 'cognitive_gap']:
            if axis in updated_matrix:
                current_stars = updated_matrix[axis].get('core_rating', 0)
                if isinstance(current_stars, str):
                    current_stars = float(current_stars.replace('★', ''))
                
                new_stars = current_stars + edge_results['star_adjustment']
                updated_matrix[axis]['core_rating'] = f"★{new_stars:.1f}"
                updated_matrix[axis]['star_adjustment'] = edge_results['star_adjustment']
        
        # 確信度調整適用
        for axis in ['right_shoulder', 'slope_quality', 'time_profile', 'cognitive_gap']:
            if axis in updated_matrix:
                current_conf = updated_matrix[axis].get('core_confidence', 0)
                if isinstance(current_conf, str):
                    current_conf = float(current_conf.replace('%', ''))
                
                new_conf = current_conf + edge_results['confidence_adjustment']
                updated_matrix[axis]['core_confidence'] = f"{new_conf:.1f}%"
                updated_matrix[axis]['confidence_adjustment'] = edge_results['confidence_adjustment']
        
        return updated_matrix

def main():
    """テスト実行"""
    calculator = AdaptiveEdgeCalculator()
    
    # RKLB適用例
    edges = [
        {
            'name': 'AFRL REGAL契約',
            'p': 82,
            'impact': 2.0,
            'independence': 0.8,
            'ttl_days': 30,
            'contradiction': False
        },
        {
            'name': 'HASTE MACH-TB 2.0',
            'p': 76,
            'impact': 1.5,
            'independence': 0.7,
            'ttl_days': 30,
            'contradiction': False
        }
    ]
    
    result = calculator.process_edge_list(edges, days_elapsed=0)
    
    print("=== Adaptive Edge Influence v4.1 ===")
    print(f"W_pos: {result['total_w_pos']:.2f}")
    print(f"W_neg: {result['total_w_neg']:.2f}")
    print(f"★調整: {result['star_adjustment']:.1f}")
    print(f"確信度調整: {result['confidence_adjustment']:.1f}pp")
    
    for edge in result['edges']:
        print(f"\n{edge['name']}:")
        print(f"  重み: {edge['weight']:.2f}")
        print(f"  鮮度: {edge['freshness']:.2f}")
        print(f"  ★寄与: {edge['star_contribution']:.2f}")
        print(f"  確信度寄与: {edge['confidence_contribution']:.2f}pp")

if __name__ == "__main__":
    main()
