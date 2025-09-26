#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AHF v0.6.3a 認知ギャップ★の再定義
- デフォルト★=3維持
- オプション種（option seeds）で±1★調整
- priced_in（市場織込み）とalpha不透明度で可能性を残す
- 方向確率の可変幅拡大（±5pp → ±10pp）
"""

import json
import sys
import argparse
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

class CognitiveGapV063A:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.results = {}
    
    def identify_option_seeds(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """オプション種（option seeds）の特定"""
        option_seeds = []
        
        # ① 非常に大きい新規契約/許認可/供給能力の数値開示
        large_contracts = data.get('large_contracts', [])
        for contract in large_contracts:
            if contract.get('value_$k', 0) >= 100000:  # $100M以上
                option_seeds.append({
                    'type': 'large_contract',
                    'description': f"Large contract ${contract['value_$k']:,.0f}k",
                    'verbatim': contract.get('verbatim', '')[:25],
                    'anchor': contract.get('anchor', ''),
                    'strength': 'high' if contract.get('value_$k', 0) >= 500000 else 'medium'
                })
        
        # ② coverage≥9か月（α4でGreen/Amber）
        coverage_months = data.get('coverage_months', 0)
        if coverage_months >= 9:
            option_seeds.append({
                'type': 'coverage_strength',
                'description': f"Coverage {coverage_months:.1f} months",
                'verbatim': data.get('coverage_verbatim', '')[:25],
                'anchor': data.get('coverage_anchor', ''),
                'strength': 'high' if coverage_months >= 12 else 'medium'
            })
        
        # ③ ガイダンスの段差上げ
        guidance_upgrade = data.get('guidance_upgrade', {})
        if guidance_upgrade.get('upgraded', False):
            option_seeds.append({
                'type': 'guidance_upgrade',
                'description': f"Guidance upgrade: {guidance_upgrade.get('description', '')}",
                'verbatim': guidance_upgrade.get('verbatim', '')[:25],
                'anchor': guidance_upgrade.get('anchor', ''),
                'strength': 'high' if guidance_upgrade.get('magnitude', 0) >= 10 else 'medium'
            })
        
        # ④ セグメント再編で高粗利の顕在化
        segment_restructure = data.get('segment_restructure', {})
        if segment_restructure.get('restructured', False):
            option_seeds.append({
                'type': 'segment_restructure',
                'description': f"Segment restructure: {segment_restructure.get('description', '')}",
                'verbatim': segment_restructure.get('verbatim', '')[:25],
                'anchor': segment_restructure.get('anchor', ''),
                'strength': 'high' if segment_restructure.get('margin_improvement', 0) >= 5 else 'medium'
            })
        
        return option_seeds[:3]  # 最大3つまで
    
    def identify_validation_hooks(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validation Hooks（後段で検証する一点）の特定"""
        validation_hooks = []
        
        # オプション種に基づく検証ポイント
        option_seeds = self.identify_option_seeds(data)
        
        for seed in option_seeds:
            if seed['type'] == 'large_contract':
                validation_hooks.append({
                    'seed_type': 'large_contract',
                    'validation_point': 'Next quarter revenue recognition and cash flow impact',
                    'timeline': '1-2 quarters',
                    'key_metrics': ['Revenue recognition', 'Cash flow', 'Backlog growth']
                })
            elif seed['type'] == 'coverage_strength':
                validation_hooks.append({
                    'seed_type': 'coverage_strength',
                    'validation_point': 'RPO conversion to revenue and margin expansion',
                    'timeline': '2-3 quarters',
                    'key_metrics': ['RPO conversion rate', 'Margin expansion', 'Customer retention']
                })
            elif seed['type'] == 'guidance_upgrade':
                validation_hooks.append({
                    'seed_type': 'guidance_upgrade',
                    'validation_point': 'Guidance execution and underlying drivers',
                    'timeline': '1 quarter',
                    'key_metrics': ['Guidance execution', 'Driver sustainability', 'Market response']
                })
            elif seed['type'] == 'segment_restructure':
                validation_hooks.append({
                    'seed_type': 'segment_restructure',
                    'validation_point': 'Segment margin improvement and market share',
                    'timeline': '2-4 quarters',
                    'key_metrics': ['Segment margins', 'Market share', 'Competitive position']
                })
        
        return validation_hooks
    
    def calculate_cognitive_gap_stars(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """認知ギャップ★の再定義計算"""
        base_stars = 3  # デフォルト★=3維持
        
        # オプション種の影響
        option_seeds = self.identify_option_seeds(data)
        option_adjustment = 0
        
        for seed in option_seeds:
            if seed['strength'] == 'high':
                option_adjustment += 1
            elif seed['strength'] == 'medium':
                option_adjustment += 0.5
        
        # キルスイッチの影響
        kill_switch_adjustment = 0
        
        # ① 収益認識の後ろ向き会計イベントの定量
        revenue_recognition_issues = data.get('revenue_recognition_issues', [])
        if revenue_recognition_issues:
            kill_switch_adjustment -= 1
        
        # ② 開示統制"not effective"が収益認識に直結
        disclosure_control_issues = data.get('disclosure_control_issues', [])
        if any(issue.get('revenue_related', False) for issue in disclosure_control_issues):
            kill_switch_adjustment -= 1
        
        # ③ coverageが連続悪化
        coverage_trend = data.get('coverage_trend', [])
        if len(coverage_trend) >= 2 and all(coverage_trend[i] > coverage_trend[i+1] for i in range(len(coverage_trend)-1)):
            kill_switch_adjustment -= 1
        
        # 最終★計算
        final_stars = max(1, min(5, base_stars + option_adjustment + kill_switch_adjustment))
        
        return {
            'base_stars': base_stars,
            'option_adjustment': option_adjustment,
            'kill_switch_adjustment': kill_switch_adjustment,
            'final_stars': final_stars,
            'option_seeds_count': len(option_seeds),
            'description': f"認知ギャップ★{final_stars} (Base{base_stars}+Option{option_adjustment:+.1f}+Kill{kill_switch_adjustment:+.1f})"
        }
    
    def calculate_priced_in_alpha_opacity(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """priced_in（市場織込み）とalpha不透明度の計算"""
        option_seeds = self.identify_option_seeds(data)
        
        # オプション種の強さに基づく計算
        total_strength = sum(1 if seed['strength'] == 'high' else 0.5 for seed in option_seeds)
        
        # priced_in（市場織込み）: オプション種が強いほど低い
        if total_strength >= 2:
            priced_in = 'low'
        elif total_strength >= 1:
            priced_in = 'medium'
        else:
            priced_in = 'high'
        
        # alpha不透明度: オプション種が強いほど高い
        if total_strength >= 2:
            alpha_opacity = 'high'
        elif total_strength >= 1:
            alpha_opacity = 'medium'
        else:
            alpha_opacity = 'low'
        
        return {
            'priced_in': priced_in,
            'alpha_opacity': alpha_opacity,
            'total_strength': total_strength,
            'description': f"織込み={priced_in}, 不透明度={alpha_opacity}"
        }
    
    def calculate_direction_probability_expanded(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """方向確率の可変幅拡大（±5pp → ±10pp）"""
        base_up_pct = data.get('direction_prob_up_pct', 50)
        base_down_pct = data.get('direction_prob_down_pct', 50)
        
        # オプション種の影響
        option_seeds = self.identify_option_seeds(data)
        total_strength = sum(1 if seed['strength'] == 'high' else 0.5 for seed in option_seeds)
        
        # 拡大調整（±10ppまで）
        expansion_factor = min(2.0, total_strength)  # 最大2倍まで
        adjustment_range = 5 * expansion_factor  # ±5pp → ±10pp
        
        # 上向き確率の調整
        if total_strength > 0:
            up_adjustment = min(adjustment_range, total_strength * 5)
            expanded_up_pct = min(100, base_up_pct + up_adjustment)
            expanded_down_pct = max(0, 100 - expanded_up_pct)
        else:
            expanded_up_pct = base_up_pct
            expanded_down_pct = base_down_pct
        
        return {
            'base_up_pct': base_up_pct,
            'base_down_pct': base_down_pct,
            'expanded_up_pct': expanded_up_pct,
            'expanded_down_pct': expanded_down_pct,
            'adjustment_range': adjustment_range,
            'total_strength': total_strength,
            'description': f"方向確率: {expanded_up_pct}%/{expanded_down_pct}% (調整幅±{adjustment_range:.1f}pp)"
        }
    
    def run_cognitive_gap_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """認知ギャップ分析実行"""
        
        # オプション種特定
        option_seeds = self.identify_option_seeds(data)
        
        # Validation Hooks特定
        validation_hooks = self.identify_validation_hooks(data)
        
        # 認知ギャップ★計算
        cognitive_gap_stars = self.calculate_cognitive_gap_stars(data)
        
        # priced_inとalpha不透明度計算
        priced_in_alpha = self.calculate_priced_in_alpha_opacity(data)
        
        # 方向確率拡大計算
        direction_probability = self.calculate_direction_probability_expanded(data)
        
        # 結果統合
        results = {
            'meta': {
                'ticker': data.get('ticker', ''),
                'as_of': data.get('as_of', ''),
                'version': 'v0.6.3a-cognitive-gap'
            },
            'option_seeds': option_seeds,
            'validation_hooks': validation_hooks,
            'cognitive_gap_stars': cognitive_gap_stars,
            'priced_in_alpha_opacity': priced_in_alpha,
            'direction_probability_expanded': direction_probability,
            'summary': {
                'option_seeds_count': len(option_seeds),
                'validation_hooks_count': len(validation_hooks),
                'final_stars': cognitive_gap_stars['final_stars'],
                'priced_in': priced_in_alpha['priced_in'],
                'alpha_opacity': priced_in_alpha['alpha_opacity'],
                'direction_expansion': direction_probability['adjustment_range']
            }
        }
        
        return results

def main():
    parser = argparse.ArgumentParser(description='AHF v0.6.3a 認知ギャップ分析')
    parser.add_argument('--config', required=True, help='設定ファイルパス')
    args = parser.parse_args()
    
    try:
        with open(args.config, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 標準入力からデータを読み込み
        data = json.load(sys.stdin)
        
        # 認知ギャップ分析実行
        analyzer = CognitiveGapV063A(config)
        results = analyzer.run_cognitive_gap_analysis(data)
        
        # 結果出力
        json.dump(results, sys.stdout, ensure_ascii=False, indent=2)
        
        # 簡易表示
        print(f"\n🧠 認知ギャップ分析結果:", file=sys.stderr)
        print(f"  銘柄: {results['meta']['ticker']}", file=sys.stderr)
        print(f"  ★評価: {results['cognitive_gap_stars']['description']}", file=sys.stderr)
        print(f"  オプション種: {results['summary']['option_seeds_count']}件", file=sys.stderr)
        print(f"  織込み/不透明度: {results['priced_in_alpha_opacity']['description']}", file=sys.stderr)
        print(f"  方向確率: {results['direction_probability_expanded']['description']}", file=sys.stderr)
        
    except Exception as e:
        print(f"❌ エラー: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()

