#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
確信度変動追跡システム
何で何pp動いたかを最大2行で明記・履歴管理
"""
import json
from typing import Dict, List, Any, Tuple
from datetime import datetime
from confidence_component_calculator import ConfidenceComponentCalculator

class ConfidenceChangeTracker:
    def __init__(self):
        self.confidence_calculator = ConfidenceComponentCalculator()
        self.change_history = []
        
    def track_confidence_change(self, old_t1_data: Dict[str, Any], 
                              new_t1_data: Dict[str, Any]) -> Dict[str, Any]:
        """確信度変動を追跡"""
        # 旧・新の確信度計算
        old_confidence = self.confidence_calculator.calculate_confidence_components(old_t1_data)
        new_confidence = self.confidence_calculator.calculate_confidence_components(new_t1_data)
        
        # 変動計算
        change = new_confidence['total_clipped'] - old_confidence['total_clipped']
        
        # 変動要因を特定
        change_factors = self._identify_change_factors(
            old_confidence['components'], 
            new_confidence['components']
        )
        
        # 変動記録
        change_record = {
            'timestamp': datetime.now().isoformat(),
            'old_confidence': old_confidence['total_clipped'],
            'new_confidence': new_confidence['total_clipped'],
            'change': change,
            'change_factors': change_factors,
            'summary': self._format_change_summary(old_confidence, new_confidence, change_factors)
        }
        
        # 履歴に追加
        self.change_history.append(change_record)
        
        return change_record
    
    def _identify_change_factors(self, old_components: Dict[str, float], 
                               new_components: Dict[str, float]) -> List[Dict[str, Any]]:
        """変動要因を特定"""
        factors = []
        
        for key in old_components:
            old_val = old_components[key]
            new_val = new_components[key]
            
            if old_val != new_val:
                change_val = new_val - old_val
                factors.append({
                    'component': key,
                    'old_value': old_val,
                    'new_value': new_val,
                    'change': change_val,
                    'description': self._get_component_description(key)
                })
        
        return factors
    
    def _get_component_description(self, component: str) -> str:
        """コンポーネント説明を取得"""
        descriptions = {
            'base': 'Base60pp',
            'bridge_alignment': 'Bridge整合',
            'backlog_12m': 'Backlog12M≥58%',
            'guidance_clarity': 'Guidance明瞭',
            'contract_balance': '契約バランス',
            'new_quarter_uncertainty': '新四半期未着地'
        }
        return descriptions.get(component, component)
    
    def _format_change_summary(self, old_confidence: Dict[str, Any], 
                             new_confidence: Dict[str, Any], 
                             change_factors: List[Dict[str, Any]]) -> str:
        """変動サマリを最大2行で表示"""
        if not change_factors:
            return f"確信度: {old_confidence['total_clipped']:.1f}% → {new_confidence['total_clipped']:.1f}% (変動なし)"
        
        # 正の変動と負の変動を分離
        positive_changes = [f for f in change_factors if f['change'] > 0]
        negative_changes = [f for f in change_factors if f['change'] < 0]
        
        lines = []
        
        # 1行目: 正の変動（最大2つ）
        if positive_changes:
            line1_parts = []
            for factor in positive_changes[:2]:
                line1_parts.append(f"{factor['description']}+{factor['change']:.0f}pp")
            lines.append(", ".join(line1_parts))
        
        # 2行目: 負の変動 + 合計
        line2_parts = []
        if negative_changes:
            for factor in negative_changes:
                line2_parts.append(f"{factor['description']}{factor['change']:.0f}pp")
        
        # 合計変動
        total_change = new_confidence['total_clipped'] - old_confidence['total_clipped']
        line2_parts.append(f"合計{total_change:+.1f}pp")
        
        if line2_parts:
            lines.append(", ".join(line2_parts))
        
        return "\n".join(lines)
    
    def get_recent_changes(self, limit: int = 5) -> List[Dict[str, Any]]:
        """最近の変動履歴を取得"""
        return self.change_history[-limit:]
    
    def get_confidence_trend(self, days: int = 30) -> Dict[str, Any]:
        """確信度トレンド分析"""
        recent_changes = [c for c in self.change_history 
                         if self._is_within_days(c['timestamp'], days)]
        
        if not recent_changes:
            return {'trend': 'stable', 'volatility': 0.0, 'direction': 'neutral'}
        
        # 変動幅計算
        changes = [c['change'] for c in recent_changes]
        volatility = sum(abs(c) for c in changes) / len(changes)
        
        # トレンド方向
        total_change = sum(changes)
        if total_change > 1.0:
            direction = 'upward'
        elif total_change < -1.0:
            direction = 'downward'
        else:
            direction = 'stable'
        
        return {
            'trend': direction,
            'volatility': volatility,
            'total_change': total_change,
            'change_count': len(recent_changes)
        }
    
    def _is_within_days(self, timestamp: str, days: int) -> bool:
        """指定日数以内かチェック"""
        try:
            change_time = datetime.fromisoformat(timestamp)
            days_ago = datetime.now().timestamp() - (days * 24 * 60 * 60)
            return change_time.timestamp() >= days_ago
        except:
            return False
    
    def export_change_history(self, filepath: str):
        """変動履歴をエクスポート"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.change_history, f, ensure_ascii=False, indent=2)

def main():
    """テスト実行"""
    tracker = ConfidenceChangeTracker()
    
    # テストデータ（旧）
    old_t1_data = {
        'gm_bridge': {
            'recognition_consistency': False,
            'segment_mix_alignment': False,
            'cost_efficiency_improvement': False,
            'contract_normalization': False
        },
        'backlog': {'twelve_month_pct': 50.0},
        'guidance': {
            'revenue_range_clarity': False,
            'gm_range_clarity': False,
            'opex_range_clarity': False
        },
        'contract_balance': {
            'contract_assets_decrease': False,
            'contract_liabilities_increase': False
        },
        'quarter_status': {'new_quarter_uncertainty': True}
    }
    
    # テストデータ（新）
    new_t1_data = {
        'gm_bridge': {
            'recognition_consistency': True,
            'segment_mix_alignment': True,
            'cost_efficiency_improvement': True,
            'contract_normalization': True
        },
        'backlog': {'twelve_month_pct': 58.0},
        'guidance': {
            'revenue_range_clarity': True,
            'gm_range_clarity': True,
            'opex_range_clarity': True
        },
        'contract_balance': {
            'contract_assets_decrease': True,
            'contract_liabilities_increase': True
        },
        'quarter_status': {'new_quarter_uncertainty': False}
    }
    
    # 変動追跡
    change_record = tracker.track_confidence_change(old_t1_data, new_t1_data)
    
    print("=== 確信度変動追跡 ===")
    print(change_record['summary'])
    print(f"\n詳細:")
    print(f"旧確信度: {change_record['old_confidence']:.1f}%")
    print(f"新確信度: {change_record['new_confidence']:.1f}%")
    print(f"変動: {change_record['change']:+.1f}pp")
    
    # トレンド分析
    trend = tracker.get_confidence_trend()
    print(f"\nトレンド分析:")
    print(f"方向: {trend['trend']}")
    print(f"変動性: {trend['volatility']:.1f}pp")

if __name__ == "__main__":
    main()
