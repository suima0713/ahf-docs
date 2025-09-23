#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AHF v0.6.3 αブリッジ標準実装
- α2: Loss controls（従前）
- α3: Stage-1（ミックス）・Stage-2（効率）
- α4: RPO基準（coverage=(RPO_12M/Quarterly_Rev)×3, Gate≥11.0）
- α5: OpEx/EBITDA三角測量（乖離検知閾値$8,000k）
"""

import json
import sys
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

class AlphaBridgeV063:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.results = {}
    
    def alpha2_loss_controls(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """α2: Loss controls（従前）"""
        # 既存のロス制御ロジック
        loss_controls = data.get('loss_controls', {})
        
        result = {
            'alpha2_status': 'PASS' if loss_controls.get('controls_active') else 'FAIL',
            'controls_count': loss_controls.get('controls_count', 0),
            'description': f"Loss controls: {loss_controls.get('controls_count', 0)} active"
        }
        return result
    
    def alpha3_stage_evaluation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """α3: Stage-1（ミックス）・Stage-2（効率）"""
        # SYM近似：ΔGM=0.60·ΔSW−0.18·ΔOps
        delta_sw = data.get('delta_sw_pp', 0)
        delta_ops = data.get('delta_ops_pp', 0)
        delta_gm = 0.60 * delta_sw - 0.18 * delta_ops
        
        # 1pp→EBITDA=Rev/100
        revenue = data.get('revenue_$k', 0)
        ebitda_impact = revenue / 100 if delta_gm >= 1.0 else 0
        
        result = {
            'alpha3_delta_gm_pp': delta_gm,
            'alpha3_ebitda_impact_$k': ebitda_impact,
            'stage1_mix': delta_sw,
            'stage2_efficiency': delta_ops,
            'description': f"ΔGM {delta_gm:+.1f}pp (SW {delta_sw:+.1f}, Ops {delta_ops:+.1f})"
        }
        return result
    
    def alpha4_rpo_coverage(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """α4: RPO基準（coverage=(RPO_12M/Quarterly_Rev)×3, Gate≥11.0）"""
        rpo_12m = data.get('rpo_12m_$k', 0)
        quarterly_rev = data.get('quarterly_revenue_$k', 0)
        
        if quarterly_rev == 0:
            coverage = 0
        else:
            coverage = (rpo_12m / quarterly_rev) * 3
        
        # Gate判定
        gate_threshold = self.config.get('alpha4', {}).get('pass_months', 11.0)
        gate_pass = coverage >= gate_threshold
        
        # Gate色判定
        amber_floor = self.config.get('alpha4', {}).get('amber_floor_months', 9.0)
        if coverage >= gate_threshold:
            gate_color = 'green'
        elif coverage >= amber_floor:
            gate_color = 'amber'
        else:
            gate_color = 'red'
        
        result = {
            'alpha4_coverage_months': coverage,
            'alpha4_gate_pass': gate_pass,
            'alpha4_gate_color': gate_color,
            'rpo_12m_$k': rpo_12m,
            'quarterly_revenue_$k': quarterly_rev,
            'description': f"RPO coverage {coverage:.1f}ヶ月 → {gate_color.upper()}"
        }
        return result
    
    def alpha5_opex_ebitda_triangulation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """α5: OpEx/EBITDA三角測量（乖離検知閾値$8,000k）"""
        opex_actual = data.get('opex_$k', 0)
        revenue = data.get('revenue_$k', 0)
        ng_gm_pct = data.get('ng_gm_pct', 0)
        adj_ebitda = data.get('adj_ebitda_$k', 0)
        
        # OpEx = Rev * NG_GM - KPI の整合性チェック
        calculated_opex = revenue * (ng_gm_pct / 100) - adj_ebitda
        deviation = abs(opex_actual - calculated_opex)
        
        # 乖離検知閾値
        tolerance = self.config.get('alpha5', {}).get('tolerance_$k', 8000)
        math_pass = deviation <= tolerance
        
        result = {
            'alpha5_opex_actual_$k': opex_actual,
            'alpha5_opex_calculated_$k': calculated_opex,
            'alpha5_deviation_$k': deviation,
            'alpha5_tolerance_$k': tolerance,
            'alpha5_math_pass': math_pass,
            'description': f"OpEx乖離 ${deviation:,.0f}k vs 許容${tolerance:,.0f}k"
        }
        return result
    
    def evaluate_all(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """全αブリッジ標準を評価"""
        results = {
            'alpha2_loss_controls': self.alpha2_loss_controls(data),
            'alpha3_stage_evaluation': self.alpha3_stage_evaluation(data),
            'alpha4_rpo_coverage': self.alpha4_rpo_coverage(data),
            'alpha5_opex_ebitda_triangulation': self.alpha5_opex_ebitda_triangulation(data)
        }
        
        # 自動チェック結果を統合
        auto_checks = {
            'alpha4_gate_pass': results['alpha4_rpo_coverage']['alpha4_gate_pass'],
            'alpha5_math_pass': results['alpha5_opex_ebitda_triangulation']['alpha5_math_pass'],
            'messages': []
        }
        
        # 警告メッセージ
        if not auto_checks['alpha4_gate_pass']:
            auto_checks['messages'].append("α4 Gate: RPO coverage不足")
        if not auto_checks['alpha5_math_pass']:
            auto_checks['messages'].append("α5 Math: OpEx乖離超過")
        
        results['auto_checks'] = auto_checks
        return results

def main():
    """CLI実行"""
    if len(sys.argv) < 2:
        print("Usage: python alpha_bridge_v063.py <config.json>")
        sys.exit(1)
    
    config_path = sys.argv[1]
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 標準入力からデータを読み込み
    data = json.load(sys.stdin)
    
    # αブリッジ評価実行
    bridge = AlphaBridgeV063(config)
    results = bridge.evaluate_all(data)
    
    # 結果出力
    json.dump(results, sys.stdout, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()

