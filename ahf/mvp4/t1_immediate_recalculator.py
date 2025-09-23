#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T1新規時の即時再計算システム
GMブリッジ・Note3・Backlog12M・契約バランスの即時分析
"""
import json
from typing import Dict, List, Any, Tuple
from datetime import datetime
from confidence_component_calculator import ConfidenceComponentCalculator

class T1ImmediateRecalculator:
    def __init__(self):
        self.confidence_calculator = ConfidenceComponentCalculator()
        
    def detect_new_t1(self, t1_sources: List[str]) -> bool:
        """T1新規検出"""
        # 8-K/10-Q/Ex.99.1/公式IR補足の新規発行を監視
        new_sources = [
            '8-K', '10-Q', '10-K', 'Ex.99.1', 
            '公式IR補足', 'BusinessWire', 'SEC_EDGAR'
        ]
        
        for source in t1_sources:
            if any(new_source in source for new_source in new_sources):
                return True
        return False
    
    def analyze_gm_bridge(self, t1_data: Dict[str, Any]) -> Dict[str, Any]:
        """GMブリッジ分析"""
        bridge_analysis = {
            'recognition_consistency': False,
            'segment_mix_alignment': False,
            'cost_efficiency_improvement': False,
            'contract_normalization': False,
            'bridge_score': 0.0
        }
        
        # recognition（認識モデル）
        recognition_data = t1_data.get('revenue_recognition', {})
        if recognition_data.get('ot_pt_ratio_consistent', False):
            bridge_analysis['recognition_consistency'] = True
            bridge_analysis['bridge_score'] += 0.25
        
        # segment_mix（セグメント比率）
        segment_data = t1_data.get('segment_mix', {})
        if segment_data.get('space_systems_dominant', False):
            bridge_analysis['segment_mix_alignment'] = True
            bridge_analysis['bridge_score'] += 0.25
        
        # cost_eff（コスト効率）
        cost_data = t1_data.get('cost_efficiency', {})
        if cost_data.get('launch_unit_economics_improvement', False):
            bridge_analysis['cost_efficiency_improvement'] = True
            bridge_analysis['bridge_score'] += 0.25
        
        # contract_norm（契約正規化）
        contract_data = t1_data.get('contract_normalization', {})
        if contract_data.get('contract_liabilities_growth', False):
            bridge_analysis['contract_normalization'] = True
            bridge_analysis['bridge_score'] += 0.25
        
        return bridge_analysis
    
    def analyze_note3(self, t1_data: Dict[str, Any]) -> Dict[str, Any]:
        """Note3分析"""
        note3_analysis = {
            'ot_pt_ratio': 0.0,
            'ss_ratio': 0.0,
            'backlog_12m_pct': 0.0,
            'contract_balance_ca': 0.0,
            'contract_balance_cl': 0.0,
            'loss_controls_recurrence': False
        }
        
        # OT/PT比率
        revenue_recognition = t1_data.get('revenue_recognition', {})
        total_pt = revenue_recognition.get('total_pt', 0)
        total_ot = revenue_recognition.get('total_ot', 0)
        if total_pt + total_ot > 0:
            note3_analysis['ot_pt_ratio'] = total_ot / (total_pt + total_ot)
        
        # SS比（Space Systems比率）
        segment_mix = t1_data.get('segment_mix', {})
        space_systems = segment_mix.get('space_systems_revenue', 0)
        total_revenue = segment_mix.get('total_revenue', 0)
        if total_revenue > 0:
            note3_analysis['ss_ratio'] = space_systems / total_revenue
        
        # Backlog12M%
        backlog_data = t1_data.get('backlog', {})
        note3_analysis['backlog_12m_pct'] = backlog_data.get('twelve_month_pct', 0)
        
        # 契約バランス（CA/CL）
        contract_balance = t1_data.get('contract_balance', {})
        note3_analysis['contract_balance_ca'] = contract_balance.get('contract_assets', 0)
        note3_analysis['contract_balance_cl'] = contract_balance.get('contract_liabilities', 0)
        
        # Loss controls再発
        loss_controls = t1_data.get('loss_controls', {})
        note3_analysis['loss_controls_recurrence'] = loss_controls.get('revenue_downward_adjustment', 0) > 0
        
        return note3_analysis
    
    def analyze_backlog_12m(self, t1_data: Dict[str, Any]) -> Dict[str, Any]:
        """Backlog12M分析"""
        backlog_analysis = {
            'total_backlog': 0,
            'twelve_month_pct': 0.0,
            'twelve_month_amount': 0,
            'visibility_score': 0.0
        }
        
        backlog_data = t1_data.get('backlog', {})
        backlog_analysis['total_backlog'] = backlog_data.get('total', 0)
        backlog_analysis['twelve_month_pct'] = backlog_data.get('twelve_month_pct', 0)
        backlog_analysis['twelve_month_amount'] = backlog_data.get('twelve_month_amount', 0)
        
        # 可視性スコア計算
        if backlog_analysis['twelve_month_pct'] >= 58.0:
            backlog_analysis['visibility_score'] = 1.0
        elif backlog_analysis['twelve_month_pct'] >= 50.0:
            backlog_analysis['visibility_score'] = 0.5
        else:
            backlog_analysis['visibility_score'] = 0.0
        
        return backlog_analysis
    
    def analyze_contract_balance(self, t1_data: Dict[str, Any]) -> Dict[str, Any]:
        """契約バランス分析"""
        balance_analysis = {
            'contract_assets': 0,
            'contract_liabilities': 0,
            'ca_change': 0,
            'cl_change': 0,
            'balance_improvement': False
        }
        
        contract_balance = t1_data.get('contract_balance', {})
        balance_analysis['contract_assets'] = contract_balance.get('contract_assets', 0)
        balance_analysis['contract_liabilities'] = contract_balance.get('contract_liabilities', 0)
        balance_analysis['ca_change'] = contract_balance.get('ca_change', 0)
        balance_analysis['cl_change'] = contract_balance.get('cl_change', 0)
        
        # バランス改善チェック（CA↓/CL↑）
        if balance_analysis['ca_change'] < 0 and balance_analysis['cl_change'] > 0:
            balance_analysis['balance_improvement'] = True
        
        return balance_analysis
    
    def immediate_recalculation(self, t1_data: Dict[str, Any]) -> Dict[str, Any]:
        """即時再計算実行"""
        # 各分析を実行
        gm_bridge = self.analyze_gm_bridge(t1_data)
        note3 = self.analyze_note3(t1_data)
        backlog_12m = self.analyze_backlog_12m(t1_data)
        contract_balance = self.analyze_contract_balance(t1_data)
        
        # 確信度計算
        confidence_result = self.confidence_calculator.calculate_confidence_components(t1_data)
        
        # 結果統合
        result = {
            'timestamp': datetime.now().isoformat(),
            'gm_bridge': gm_bridge,
            'note3': note3,
            'backlog_12m': backlog_12m,
            'contract_balance': contract_balance,
            'confidence': confidence_result,
            'recalculation_triggered': True
        }
        
        return result
    
    def format_recalculation_summary(self, result: Dict[str, Any]) -> str:
        """再計算サマリを2行で表示"""
        confidence = result['confidence']
        gm_bridge = result['gm_bridge']
        backlog_12m = result['backlog_12m']
        
        # 1行目: 主要指標
        line1_parts = []
        if gm_bridge['bridge_score'] >= 0.75:
            line1_parts.append("Bridge整合+10pp")
        if backlog_12m['twelve_month_pct'] >= 58.0:
            line1_parts.append("Backlog12M≥58% +5pp")
        
        # 2行目: 確信度変動
        line2 = f"確信度: {confidence['total_clipped']:.1f}%"
        if confidence['clipped']:
            line2 += f" (クリップ適用)"
        
        lines = []
        if line1_parts:
            lines.append(", ".join(line1_parts))
        lines.append(line2)
        
        return "\n".join(lines)

def main():
    """テスト実行"""
    recalculator = T1ImmediateRecalculator()
    
    # テストデータ
    t1_data = {
        'revenue_recognition': {
            'total_pt': 70.3,
            'total_ot': 74.2,
            'ot_pt_ratio_consistent': True
        },
        'segment_mix': {
            'space_systems_revenue': 97.9,
            'total_revenue': 144.5,
            'space_systems_dominant': True
        },
        'cost_efficiency': {
            'launch_unit_economics_improvement': True
        },
        'contract_normalization': {
            'contract_liabilities_growth': True
        },
        'backlog': {
            'total': 995410,
            'twelve_month_pct': 58.0,
            'twelve_month_amount': 577338
        },
        'contract_balance': {
            'contract_assets': 50000,
            'contract_liabilities': 223432,
            'ca_change': -5000,
            'cl_change': 16565
        },
        'guidance': {
            'revenue_range_clarity': True,
            'gm_range_clarity': True,
            'opex_range_clarity': True
        },
        'quarter_status': {
            'new_quarter_uncertainty': False
        }
    }
    
    result = recalculator.immediate_recalculation(t1_data)
    summary = recalculator.format_recalculation_summary(result)
    
    print("=== T1即時再計算 ===")
    print(summary)
    print(f"\n詳細:")
    print(f"GMブリッジスコア: {result['gm_bridge']['bridge_score']:.2f}")
    print(f"Backlog12M%: {result['backlog_12m']['twelve_month_pct']:.1f}%")
    print(f"契約バランス改善: {result['contract_balance']['balance_improvement']}")

if __name__ == "__main__":
    main()
