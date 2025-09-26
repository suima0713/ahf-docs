#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AHF v0.6.3 Mini-Confirm（15-25分）
目的: α3/α5の"機械的"確認だけ先にやって当たり外れを早めに判定
"""

import json
import sys
import argparse
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

class MiniConfirmV063:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.results = {}
    
    def calculate_alpha3_bridge(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """α3：Stage-1（Mix=OT/PT＋Seg）→ Stage-2（残差コスト）でGM乖離≤0.2pp／残差GP≤$8Mチェック"""
        
        # ガイダンス目標GM取得
        guidance_gm = data.get('guidance_gm_pct', 0)
        if not guidance_gm:
            return {
                'alpha3_status': 'FAIL',
                'reason': 'No guidance GM provided',
                'gm_deviation_pp': 0,
                'residual_gp_$k': 0,
                'description': 'α3: No guidance GM for bridge calculation'
            }
        
        # Stage-1: Mix (OT/PT + Seg)
        ot_pt_mix = data.get('ot_pt_mix_pp', 0)
        segment_mix = data.get('segment_mix_pp', 0)
        stage1_mix_pp = ot_pt_mix + segment_mix
        
        # Stage-2: 残差コスト
        residual_cost_pp = data.get('residual_cost_pp', 0)
        stage2_eff_pp = residual_cost_pp
        
        # 合計GM乖離
        total_gm_deviation_pp = stage1_mix_pp + stage2_eff_pp
        
        # 残差GP計算
        revenue = data.get('revenue_$k', 0)
        residual_gp_$k = revenue * abs(total_gm_deviation_pp) / 100
        
        # 判定基準
        gm_deviation_ok = abs(total_gm_deviation_pp) <= 0.2
        residual_gp_ok = residual_gp_$k <= 8000
        
        alpha3_pass = gm_deviation_ok and residual_gp_ok
        
        return {
            'alpha3_status': 'PASS' if alpha3_pass else 'FAIL',
            'guidance_gm_pct': guidance_gm,
            'stage1_mix_pp': stage1_mix_pp,
            'stage2_eff_pp': stage2_eff_pp,
            'total_gm_deviation_pp': total_gm_deviation_pp,
            'gm_deviation_ok': gm_deviation_ok,
            'residual_gp_$k': residual_gp_$k,
            'residual_gp_ok': residual_gp_ok,
            'description': f"α3: GM deviation {total_gm_deviation_pp:+.1f}pp, residual GP ${residual_gp_$k:,.0f}k"
        }
    
    def calculate_alpha5_grid(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """α5：Ex.99.1ベースで OpEx = Rev×NG-GM − Adj.EBITDA を18通り（Rev×GM×EBITDAの格子）で帯域化"""
        
        # ガイダンス範囲取得
        guidance_rev = data.get('guidance_rev', {})
        guidance_gm = data.get('guidance_gm', {})
        guidance_ebitda = data.get('guidance_ebitda', {})
        
        # 3×3×2 = 18通りの格子計算
        rev_scenarios = [
            guidance_rev.get('low', 0),
            guidance_rev.get('mid', 0),
            guidance_rev.get('high', 0)
        ]
        gm_scenarios = [
            guidance_gm.get('low', 0),
            guidance_gm.get('mid', 0),
            guidance_gm.get('high', 0)
        ]
        ebitda_scenarios = [
            guidance_ebitda.get('low', 0),
            guidance_ebitda.get('high', 0)
        ]
        
        # 18通りのOpEx計算
        opex_calculations = []
        for rev in rev_scenarios:
            for gm in gm_scenarios:
                for ebitda in ebitda_scenarios:
                    if rev > 0 and gm > 0:  # 有効な値のみ
                        opex = rev * (gm / 100) - ebitda
                        opex_calculations.append(opex)
        
        if not opex_calculations:
            return {
                'alpha5_status': 'FAIL',
                'reason': 'No valid guidance scenarios',
                'opex_band': {'min': 0, 'median': 0, 'max': 0},
                'delta_vs_prev_q': 0,
                'math_pass': False,
                'description': 'α5: No valid guidance for grid calculation'
            }
        
        # 帯域計算
        opex_band = {
            'min': min(opex_calculations),
            'median': sorted(opex_calculations)[len(opex_calculations)//2],
            'max': max(opex_calculations)
        }
        
        # Q2実績との比較
        q2_opex = data.get('q2_opex_$k', 0)
        delta_vs_prev_q = opex_band['median'] - q2_opex
        
        # 改善判定（中央値が−$3〜5M以上なら「改善の素地あり」）
        improvement_threshold = -3000  # -$3M
        has_improvement = delta_vs_prev_q <= improvement_threshold
        
        # 数理チェック（乖離≤$8,000k）
        tolerance = 8000
        math_pass = all(abs(opex - opex_band['median']) <= tolerance for opex in opex_calculations)
        
        return {
            'alpha5_status': 'PASS' if (has_improvement and math_pass) else 'FAIL',
            'opex_band': opex_band,
            'delta_vs_prev_q': delta_vs_prev_q,
            'improvement_threshold': improvement_threshold,
            'has_improvement': has_improvement,
            'math_pass': math_pass,
            'tolerance_$k': tolerance,
            'scenario_count': len(opex_calculations),
            'description': f"α5: OpEx band ${opex_band['min']:,.0f}k-${opex_band['max']:,.0f}k, ΔQ2 ${delta_vs_prev_q:+,.0f}k"
        }
    
    def determine_pass_criteria(self, alpha3_result: Dict[str, Any], alpha5_result: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """通過基準判定（Deepへ）"""
        
        # α3合格＋α5帯域がQ2比で中央値改善 ⇒ GO
        alpha3_pass = alpha3_result.get('alpha3_status') == 'PASS'
        alpha5_pass = alpha5_result.get('alpha5_status') == 'PASS'
        
        # 片方NGでも、Item1AがNo-change & CL↑/CA↓なら保留昇格
        item1a_nochange = data.get('item1a_nochange', {}).get('pass', False)
        contract_direction = data.get('contract_balances', {}).get('direction', '')
        cl_up_ca_down = 'CL↑' in contract_direction or 'CA↓' in contract_direction
        
        soft_pass = (not alpha3_pass or not alpha5_pass) and item1a_nochange and cl_up_ca_down
        
        if alpha3_pass and alpha5_pass:
            decision = 'GO'
            reason = 'Both α3 and α5 passed'
        elif soft_pass:
            decision = 'GO'
            reason = 'Soft pass: Item1A no-change with contract direction improvement'
        elif alpha3_pass or alpha5_pass:
            decision = 'WATCH'
            reason = 'Partial pass: One of α3 or α5 passed'
        else:
            decision = 'DROP'
            reason = 'Both α3 and α5 failed'
        
        return {
            'decision': decision,
            'reason': reason,
            'alpha3_pass': alpha3_pass,
            'alpha5_pass': alpha5_pass,
            'soft_pass': soft_pass,
            'item1a_nochange': item1a_nochange,
            'contract_direction': contract_direction
        }
    
    def identify_edge_candidates(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Edge候補特定（P/TTL/contradiction）"""
        edge_candidates = []
        
        # 既存のEdge項目から候補を抽出
        existing_edges = data.get('edge_items', [])
        for edge in existing_edges:
            if edge.get('confidence', 0) >= 70 and not edge.get('contradiction', False):
                edge_candidates.append({
                    'kpi': edge.get('kpi', ''),
                    'confidence': edge.get('confidence', 0),
                    'direction': edge.get('direction', 'neutral'),
                    'ttl_days': edge.get('ttl_days', 30),
                    'contradiction': edge.get('contradiction', False),
                    'source': edge.get('source', '')
                })
        
        return edge_candidates
    
    def run_mini_confirm(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mini-Confirm実行"""
        
        # α3ブリッジ計算
        alpha3_result = self.calculate_alpha3_bridge(data)
        
        # α5グリッド計算
        alpha5_result = self.calculate_alpha5_grid(data)
        
        # 通過基準判定
        pass_criteria = self.determine_pass_criteria(alpha3_result, alpha5_result, data)
        
        # Edge候補特定
        edge_candidates = self.identify_edge_candidates(data)
        
        # 結果統合
        results = {
            'meta': {
                'ticker': data.get('ticker', ''),
                'as_of': data.get('as_of', ''),
                'confirmation_time': '15-25min',
                'version': 'v0.6.3-mini-confirm'
            },
            'alpha3_bridge': alpha3_result,
            'alpha5_grid': alpha5_result,
            'pass_criteria': pass_criteria,
            'edge_candidates': edge_candidates,
            'summary': {
                'alpha3_status': alpha3_result.get('alpha3_status'),
                'alpha5_status': alpha5_result.get('alpha5_status'),
                'decision': pass_criteria.get('decision'),
                'edge_count': len(edge_candidates)
            }
        }
        
        return results

def main():
    parser = argparse.ArgumentParser(description='AHF v0.6.3 Mini-Confirm')
    parser.add_argument('--config', required=True, help='設定ファイルパス')
    args = parser.parse_args()
    
    try:
        with open(args.config, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 標準入力からデータを読み込み
        data = json.load(sys.stdin)
        
        # Mini-Confirm実行
        confirm = MiniConfirmV063(config)
        results = confirm.run_mini_confirm(data)
        
        # 結果出力
        json.dump(results, sys.stdout, ensure_ascii=False, indent=2)
        
        # 簡易表示
        print(f"\n🔍 Mini-Confirm結果:", file=sys.stderr)
        print(f"  銘柄: {results['meta']['ticker']}", file=sys.stderr)
        print(f"  判定: {results['pass_criteria']['decision']}", file=sys.stderr)
        print(f"  理由: {results['pass_criteria']['reason']}", file=sys.stderr)
        print(f"  α3: {results['alpha3_bridge']['alpha3_status']}", file=sys.stderr)
        print(f"  α5: {results['alpha5_grid']['alpha5_status']}", file=sys.stderr)
        print(f"  Edge候補: {results['summary']['edge_count']}件", file=sys.stderr)
        
    except Exception as e:
        print(f"❌ エラー: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()

