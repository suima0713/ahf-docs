#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AHF v0.6.3 Fast-Screen（1銘柄あたり8-12分）
目的: ①右肩・②勾配の"落第"を早期に弾く
入力: T1のみ／逐語≤25w＋アンカー必須
"""

import json
import sys
import argparse
from typing import Dict, Any, List, Optional
from datetime import datetime

class FastScreenV063:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.results = {}
    
    def extract_baseline_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """直近10-Q/8-K(Ex.99.1)から基本データ抽出"""
        baseline = {
            'revenue_$k': data.get('revenue_$k', 0),
            'gaap_gp_$k': data.get('gaap_gp_$k', 0),
            'gaap_gm_pct': data.get('gaap_gm_pct', 0),
            'adj_ebitda_$k': data.get('adj_ebitda_$k', 0),
            'guidance': {
                'rev': data.get('guidance_rev', {}),
                'gaap_gm': data.get('guidance_gaap_gm', {}),
                'nongaap_gm': data.get('guidance_nongaap_gm', {})
            }
        }
        return baseline
    
    def extract_contract_balances(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """契約バランス（CA/CL）方向抽出"""
        ca_current = data.get('contract_assets_$k', 0)
        cl_current = data.get('contract_liabilities_$k', 0)
        ca_previous = data.get('contract_assets_prev_$k', 0)
        cl_previous = data.get('contract_liabilities_prev_$k', 0)
        
        ca_direction = '↑' if ca_current > ca_previous else '↓' if ca_current < ca_previous else '→'
        cl_direction = '↑' if cl_current > cl_previous else '↓' if cl_current < cl_previous else '→'
        
        return {
            'ca_$k': ca_current,
            'cl_$k': cl_current,
            'direction': f"CA{ca_direction}/CL{cl_direction}"
        }
    
    def extract_backlog_rpo_12m(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Backlog or RPOの12M比率抽出"""
        rpo_12m_pct = data.get('rpo_12m_pct', 0)
        backlog_12m_pct = data.get('backlog_12m_pct', 0)
        
        # 12M比率の有無判定
        has_12m_data = rpo_12m_pct > 0 or backlog_12m_pct > 0
        pct_or_months = max(rpo_12m_pct, backlog_12m_pct)
        
        return {
            'pct_or_months': pct_or_months,
            'has_12m_data': has_12m_data,
            'anchor': data.get('backlog_rpo_anchor', '')
        }
    
    def extract_item1a_nochange(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Item 1A「No material changes」有無"""
        item1a_text = data.get('item1a_text', '')
        no_change_phrases = ['no material changes', 'no significant changes', 'no substantial changes']
        
        has_no_change = any(phrase.lower() in item1a_text.lower() for phrase in no_change_phrases)
        
        # 25語以内の引用抽出
        quote = item1a_text[:100] if item1a_text else ""
        if len(quote.split()) > 25:
            quote = " ".join(quote.split()[:25])
        
        return {
            'pass': has_no_change,
            'quote': quote,
            'anchor': data.get('item1a_anchor', '')
        }
    
    def extract_ot_pt_note3(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """OT/PT Note3抽出（あれば）"""
        ot_pt_data = data.get('ot_pt_note3', {})
        
        if not ot_pt_data:
            return {'available': False}
        
        return {
            'available': True,
            'total': {
                'ot': ot_pt_data.get('total_ot', 0),
                'pt': ot_pt_data.get('total_pt', 0)
            },
            'launch': {
                'ot': ot_pt_data.get('launch_ot', 0),
                'pt': ot_pt_data.get('launch_pt', 0)
            },
            'space': {
                'ot': ot_pt_data.get('space_ot', 0),
                'pt': ot_pt_data.get('space_pt', 0)
            }
        }
    
    def calculate_quick_stars(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """即席スコア（★＝整数）計算"""
        baseline = self.extract_baseline_data(data)
        contract_balances = self.extract_contract_balances(data)
        backlog_rpo = self.extract_backlog_rpo_12m(data)
        item1a = self.extract_item1a_nochange(data)
        ot_pt = self.extract_ot_pt_note3(data)
        
        # ①右肩：YoY売上＆GMがともに+
        revenue_yoy = data.get('revenue_yoy_pct', 0)
        gm_yoy = data.get('gm_yoy_pct', 0)
        
        if revenue_yoy > 0 and gm_yoy > 0:
            axis1_stars = 4 if revenue_yoy >= 10 and gm_yoy >= 2 else 3
            axis1_rationale = f"Revenue +{revenue_yoy:.1f}% and GM +{gm_yoy:.1f}pp both positive"
        elif revenue_yoy > 0 or gm_yoy > 0:
            axis1_stars = 2
            axis1_rationale = f"Mixed performance: Revenue +{revenue_yoy:.1f}%, GM +{gm_yoy:.1f}pp"
        else:
            axis1_stars = 1
            axis1_rationale = f"Both Revenue {revenue_yoy:.1f}% and GM {gm_yoy:.1f}pp negative or flat"
        
        # ②勾配：ガイダンス改善 or OT/PT改善示唆
        guidance_improvement = data.get('guidance_improvement', False)
        ot_pt_improvement = ot_pt.get('available', False) and (
            ot_pt.get('total', {}).get('ot', 0) > 0 or ot_pt.get('total', {}).get('pt', 0) > 0
        )
        
        if guidance_improvement or ot_pt_improvement:
            axis2_stars = 4 if guidance_improvement and ot_pt_improvement else 3
            axis2_rationale = f"Guidance improvement: {guidance_improvement}, OT/PT: {ot_pt_improvement}"
        else:
            axis2_stars = 2
            axis2_rationale = "No clear guidance or OT/PT improvement signals"
        
        # ③時間軸：RPO12M or Backlog12M≧9ヶ月換算
        months_equivalent = backlog_rpo.get('pct_or_months', 0) / 100 * 12  # パーセントを月数に変換
        
        if months_equivalent >= 9:
            axis3_stars = 3
            axis3_rationale = f"12M coverage {months_equivalent:.1f} months >= 9 months threshold"
        elif contract_balances.get('direction', '').count('↑') >= 1:  # CL↑ or CA↓
            axis3_stars = 2
            axis3_rationale = f"Limited visibility but contract direction {contract_balances.get('direction')}"
        else:
            axis3_stars = 1
            axis3_rationale = f"Low visibility: {months_equivalent:.1f} months, direction {contract_balances.get('direction')}"
        
        # ④認知ギャップ：GMブリッジが明確＋市場ノイズ誤認の余地
        gm_bridge_clarity = data.get('gm_bridge_clarity', False)
        market_noise_risk = data.get('market_noise_risk', False)
        
        if gm_bridge_clarity and not market_noise_risk:
            axis4_stars = 4
            axis4_rationale = "Clear GM bridge with low market noise risk"
        elif gm_bridge_clarity or not market_noise_risk:
            axis4_stars = 3
            axis4_rationale = "Moderate clarity in GM bridge or noise management"
        else:
            axis4_stars = 2
            axis4_rationale = "Unclear GM bridge with potential market noise"
        
        return {
            'axis1': axis1_stars,
            'axis2': axis2_stars,
            'axis3': axis3_stars,
            'axis4': axis4_stars,
            'rationale': {
                'axis1': axis1_rationale,
                'axis2': axis2_rationale,
                'axis3': axis3_rationale,
                'axis4': axis4_rationale
            }
        }
    
    def determine_pass_criteria(self, quick_stars: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """通過基準判定"""
        axis1_stars = quick_stars['axis1']
        axis2_stars = quick_stars['axis2']
        
        # Hard pass：①≥3★ かつ ②≥3★
        hard_pass = axis1_stars >= 3 and axis2_stars >= 3
        
        # Soft救済：①または②が2★でも、Edge P≥75（TTL≤14d）で穴埋め可
        edge_items = data.get('edge_items', [])
        high_confidence_edges = [e for e in edge_items if e.get('confidence', 0) >= 75 and e.get('ttl_days', 0) <= 14]
        
        soft_rescue = (axis1_stars == 2 or axis2_stars == 2) and len(high_confidence_edges) > 0
        
        if hard_pass:
            decision = 'PASS'
            reason = 'Hard pass: Both axis1 and axis2 >= 3 stars'
        elif soft_rescue:
            decision = 'PASS'
            reason = f'Soft rescue: Edge P≥75 with {len(high_confidence_edges)} items'
        elif axis1_stars >= 2 or axis2_stars >= 2:
            decision = 'WATCH'
            reason = 'Watch: Moderate performance, needs monitoring'
        else:
            decision = 'DROP'
            reason = 'Drop: Low performance on key axes'
        
        return {
            'decision': decision,
            'reason': reason,
            'hard_pass': hard_pass,
            'soft_rescue': soft_rescue,
            'edge_count': len(high_confidence_edges)
        }
    
    def run_fast_screen(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Fast-Screen実行"""
        # データ抽出
        baseline = self.extract_baseline_data(data)
        contract_balances = self.extract_contract_balances(data)
        backlog_rpo = self.extract_backlog_rpo_12m(data)
        item1a = self.extract_item1a_nochange(data)
        ot_pt = self.extract_ot_pt_note3(data)
        
        # 即席スコア計算
        quick_stars = self.calculate_quick_stars(data)
        
        # 通過基準判定
        pass_criteria = self.determine_pass_criteria(quick_stars, data)
        
        # 結果統合
        results = {
            'meta': {
                'ticker': data.get('ticker', ''),
                'as_of': data.get('as_of', ''),
                'screening_time': '8-12min',
                'version': 'v0.6.3-fast-screen'
            },
            'baseline': baseline,
            'contract_balances': contract_balances,
            'backlog_or_rpo_12m': backlog_rpo,
            'item1a_nochange': item1a,
            'ot_pt_note3': ot_pt,
            'quick_stars': quick_stars,
            'pass_criteria': pass_criteria,
            'anchors': self.extract_anchors(data),
            'data_gaps': self.identify_data_gaps(data)
        }
        
        return results
    
    def extract_anchors(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """アンカー抽出（#:~:text=フラグメント必須）"""
        anchors = []
        
        # 各データソースからアンカーを抽出
        for key, value in data.items():
            if isinstance(value, dict) and 'anchor' in value:
                anchor_url = value.get('anchor', '')
                if ':#:~:text=' in anchor_url:
                    anchors.append({
                        'field': key,
                        'anchor': anchor_url,
                        'anchor_backup': value.get('anchor_backup', {}),
                        'verbatim': value.get('verbatim', '')[:25]
                    })
        
        return anchors
    
    def identify_data_gaps(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """データギャップ特定"""
        gaps = []
        required_fields = [
            'revenue_$k', 'gaap_gm_pct', 'adj_ebitda_$k',
            'contract_assets_$k', 'contract_liabilities_$k'
        ]
        
        for field in required_fields:
            if not data.get(field):
                gaps.append({
                    'field': field,
                    'status': 'data_gap',
                    'reason': 'NOT_DISCLOSED',
                    'ttl_days': 30
                })
        
        return gaps

def main():
    parser = argparse.ArgumentParser(description='AHF v0.6.3 Fast-Screen')
    parser.add_argument('--config', required=True, help='設定ファイルパス')
    args = parser.parse_args()
    
    try:
        with open(args.config, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 標準入力からデータを読み込み
        data = json.load(sys.stdin)
        
        # Fast-Screen実行
        screen = FastScreenV063(config)
        results = screen.run_fast_screen(data)
        
        # 結果出力
        json.dump(results, sys.stdout, ensure_ascii=False, indent=2)
        
        # 簡易表示
        print(f"\n🚀 Fast-Screen結果:", file=sys.stderr)
        print(f"  銘柄: {results['meta']['ticker']}", file=sys.stderr)
        print(f"  判定: {results['pass_criteria']['decision']}", file=sys.stderr)
        print(f"  理由: {results['pass_criteria']['reason']}", file=sys.stderr)
        print(f"  ★評価: {results['quick_stars']['axis1']}/{results['quick_stars']['axis2']}/{results['quick_stars']['axis3']}/{results['quick_stars']['axis4']}", file=sys.stderr)
        
    except Exception as e:
        print(f"❌ エラー: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()

