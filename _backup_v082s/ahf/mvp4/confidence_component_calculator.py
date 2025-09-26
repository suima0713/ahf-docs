#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AHF確信度コンポーネント計算器
Base60pp＋各要素±5pp・内訳表示・50-95%クリップ
"""
import json
from typing import Dict, List, Any, Tuple
from datetime import datetime

class ConfidenceComponentCalculator:
    def __init__(self):
        self.base_confidence = 60.0  # Base60pp
        self.min_confidence = 50.0   # 下限50%
        self.max_confidence = 95.0   # 上限95%
        
    def calculate_confidence_components(self, t1_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        確信度コンポーネント計算
        Base60pp + Bridge整合+10pp + Backlog12M≥58% +5pp + Guidance明瞭+5pp + 契約バランスCA↓/CL↑ +5pp − 新四半期未着地-10pp
        """
        components = {
            'base': 60.0,
            'bridge_alignment': 0.0,
            'backlog_12m': 0.0,
            'guidance_clarity': 0.0,
            'contract_balance': 0.0,
            'new_quarter_uncertainty': 0.0
        }
        
        # Bridge整合+10pp
        if self._check_bridge_alignment(t1_data):
            components['bridge_alignment'] = 10.0
            
        # Backlog12M≥58% +5pp
        if self._check_backlog_12m_threshold(t1_data):
            components['backlog_12m'] = 5.0
            
        # Guidance明瞭+5pp
        if self._check_guidance_clarity(t1_data):
            components['guidance_clarity'] = 5.0
            
        # 契約バランスCA↓/CL↑ +5pp
        if self._check_contract_balance_improvement(t1_data):
            components['contract_balance'] = 5.0
            
        # 新四半期未着地-10pp
        if self._check_new_quarter_uncertainty(t1_data):
            components['new_quarter_uncertainty'] = -10.0
            
        # 合計計算
        total_confidence = sum(components.values())
        clipped_confidence = max(self.min_confidence, min(self.max_confidence, total_confidence))
        
        return {
            'components': components,
            'total_raw': total_confidence,
            'total_clipped': clipped_confidence,
            'clipped': total_confidence != clipped_confidence
        }
    
    def _check_bridge_alignment(self, t1_data: Dict[str, Any]) -> bool:
        """Bridge整合性チェック"""
        # GMブリッジの整合性をチェック
        gm_bridge = t1_data.get('gm_bridge', {})
        recognition = gm_bridge.get('recognition_consistency', False)
        segment_mix = gm_bridge.get('segment_mix_alignment', False)
        cost_eff = gm_bridge.get('cost_efficiency_improvement', False)
        contract_norm = gm_bridge.get('contract_normalization', False)
        
        return recognition and segment_mix and cost_eff and contract_norm
    
    def _check_backlog_12m_threshold(self, t1_data: Dict[str, Any]) -> bool:
        """Backlog12M≥58%チェック"""
        backlog_data = t1_data.get('backlog', {})
        twelve_month_pct = backlog_data.get('twelve_month_pct', 0)
        return twelve_month_pct >= 58.0
    
    def _check_guidance_clarity(self, t1_data: Dict[str, Any]) -> bool:
        """Guidance明瞭性チェック"""
        guidance = t1_data.get('guidance', {})
        revenue_range = guidance.get('revenue_range_clarity', False)
        gm_range = guidance.get('gm_range_clarity', False)
        opex_range = guidance.get('opex_range_clarity', False)
        
        return revenue_range and gm_range and opex_range
    
    def _check_contract_balance_improvement(self, t1_data: Dict[str, Any]) -> bool:
        """契約バランス改善チェック（CA↓/CL↑）"""
        contract_balance = t1_data.get('contract_balance', {})
        ca_decrease = contract_balance.get('contract_assets_decrease', False)
        cl_increase = contract_balance.get('contract_liabilities_increase', False)
        
        return ca_decrease and cl_increase
    
    def _check_new_quarter_uncertainty(self, t1_data: Dict[str, Any]) -> bool:
        """新四半期未着地チェック"""
        quarter_status = t1_data.get('quarter_status', {})
        return quarter_status.get('new_quarter_uncertainty', False)
    
    def format_confidence_breakdown(self, result: Dict[str, Any]) -> str:
        """確信度内訳を2行で表示"""
        components = result['components']
        
        # 正の寄与
        positive_contributions = []
        if components['bridge_alignment'] > 0:
            positive_contributions.append(f"Bridge整合+{components['bridge_alignment']:.0f}pp")
        if components['backlog_12m'] > 0:
            positive_contributions.append(f"Backlog12M≥58% +{components['backlog_12m']:.0f}pp")
        if components['guidance_clarity'] > 0:
            positive_contributions.append(f"Guidance明瞭+{components['guidance_clarity']:.0f}pp")
        if components['contract_balance'] > 0:
            positive_contributions.append(f"契約バランス+{components['contract_balance']:.0f}pp")
        
        # 負の寄与
        negative_contributions = []
        if components['new_quarter_uncertainty'] < 0:
            negative_contributions.append(f"新四半期未着地{components['new_quarter_uncertainty']:.0f}pp")
        
        # 2行に分割
        line1_parts = positive_contributions[:2]  # 最初の2つ
        line2_parts = positive_contributions[2:] + negative_contributions  # 残り
        
        lines = []
        if line1_parts:
            lines.append(", ".join(line1_parts))
        if line2_parts:
            lines.append(", ".join(line2_parts))
        
        return "\n".join(lines) if lines else "Base60pp"
    
    def calculate_confidence_change(self, old_result: Dict[str, Any], 
                                  new_result: Dict[str, Any]) -> Dict[str, Any]:
        """確信度変動を追跡"""
        old_confidence = old_result['total_clipped']
        new_confidence = new_result['total_clipped']
        change = new_confidence - old_confidence
        
        # 変動要因を特定
        old_components = old_result['components']
        new_components = new_result['components']
        
        changes = []
        for key in old_components:
            old_val = old_components[key]
            new_val = new_components[key]
            if old_val != new_val:
                change_val = new_val - old_val
                if change_val > 0:
                    changes.append(f"{key}+{change_val:.0f}pp")
                elif change_val < 0:
                    changes.append(f"{key}{change_val:.0f}pp")
        
        return {
            'old_confidence': old_confidence,
            'new_confidence': new_confidence,
            'change': change,
            'change_factors': changes,
            'change_summary': f"確信度 {old_confidence:.1f}% → {new_confidence:.1f}% ({change:+.1f}pp)"
        }

def main():
    """テスト実行"""
    calculator = ConfidenceComponentCalculator()
    
    # テストデータ
    t1_data = {
        'gm_bridge': {
            'recognition_consistency': True,
            'segment_mix_alignment': True,
            'cost_efficiency_improvement': True,
            'contract_normalization': True
        },
        'backlog': {
            'twelve_month_pct': 58.0
        },
        'guidance': {
            'revenue_range_clarity': True,
            'gm_range_clarity': True,
            'opex_range_clarity': True
        },
        'contract_balance': {
            'contract_assets_decrease': True,
            'contract_liabilities_increase': True
        },
        'quarter_status': {
            'new_quarter_uncertainty': False
        }
    }
    
    result = calculator.calculate_confidence_components(t1_data)
    breakdown = calculator.format_confidence_breakdown(result)
    
    print("=== AHF確信度コンポーネント計算 ===")
    print(f"Base60pp + Bridge整合+10pp + Backlog12M≥58% +5pp + Guidance明瞭+5pp + 契約バランス+5pp")
    print(f"合計: {result['total_raw']:.1f}pp → {result['total_clipped']:.1f}% (クリップ: {result['clipped']})")
    print(f"\n内訳:")
    print(breakdown)

if __name__ == "__main__":
    main()
