#!/usr/bin/env python3
"""
Turbo Screen 二段表示機能
Core（安全）／Screen（攻め）の同時表示と自動格下げ機能
"""

import json
import yaml
import sys
from datetime import datetime, timedelta
from pathlib import Path

class TurboScreenDisplay:
    def __init__(self, ticker_path):
        self.ticker_path = Path(ticker_path)
        self.b_yaml_path = self.ticker_path / "current" / "B.yaml"
        self.triage_json_path = self.ticker_path / "current" / "triage.json"
        
    def load_data(self):
        """B.yamlとtriage.jsonを読み込み"""
        try:
            with open(self.b_yaml_path, 'r', encoding='utf-8') as f:
                self.b_data = yaml.safe_load(f)
        except FileNotFoundError:
            print(f"ERROR: B.yaml not found at {self.b_yaml_path}")
            return False
            
        try:
            with open(self.triage_json_path, 'r', encoding='utf-8') as f:
                self.triage_data = json.load(f)
        except FileNotFoundError:
            print(f"WARNING: triage.json not found at {self.triage_json_path}")
            self.triage_data = {"CONFIRMED": [], "UNCERTAIN": []}
            
        return True
    
    def calculate_turbo_screen_metrics(self):
        """Turbo Screen基準でのメトリクス計算"""
        if 'turbo_screen_matrix' not in self.b_data:
            return None
            
        matrix = self.b_data['turbo_screen_matrix']
        turbo_metrics = {}
        
        for axis_name, axis_data in matrix['axes'].items():
            # Core基準（従来）
            core_stars = axis_data.get('core_stars', 3)
            core_confidence = float(axis_data.get('confidence', '70%').replace('%', ''))
            
            # Screen基準（攻め）
            screen_stars = axis_data.get('screen_stars', core_stars)
            screen_confidence = min(core_confidence + 5, 95)  # +5pp上限
            
            turbo_metrics[axis_name] = {
                'core': {
                    'stars': core_stars,
                    'confidence': f"{core_confidence}%",
                    'adjustment': "±1★ (従来制限維持)"
                },
                'screen': {
                    'stars': screen_stars,
                    'confidence': f"{screen_confidence}%",
                    'adjustment': "±2★ (攻め基準)"
                },
                'market_incorporation': axis_data.get('market_incorporation', '中'),
                'alpha_opacity': axis_data.get('alpha_opacity', 0.6),
                'directional_bias': axis_data.get('directional_bias', '50/50')
            }
            
        return turbo_metrics
    
    def evaluate_turbo_edges(self):
        """Turbo Edge評価（P≥60, TTL≤14d）"""
        if 'turbo_screen_matrix' not in self.b_data:
            return []
            
        turbo_edges = self.b_data['turbo_screen_matrix'].get('turbo_edges', [])
        evaluated_edges = []
        
        for edge in turbo_edges:
            p_value = edge.get('p', 0)
            ttl_days = int(edge.get('ttl', '14d').replace('d', ''))
            
            # Turbo Screen基準: P≥60, TTL≤14d
            if p_value >= 60 and ttl_days <= 14:
                edge_info = {
                    'name': edge.get('name', ''),
                    'p': p_value,
                    'ttl': edge.get('ttl', '14d'),
                    'summary': edge.get('summary', ''),
                    'dual_anchor_status': edge.get('dual_anchor_status', ''),
                    'contradiction': edge.get('contradiction', False),
                    'status': 'ADOPTED' if not edge.get('contradiction', False) else 'EXCLUDED'
                }
                evaluated_edges.append(edge_info)
                
        return evaluated_edges
    
    def check_auto_downgrade_conditions(self):
        """Q3ドロップ時の自動格下げ条件チェック"""
        conditions = {
            'gm_deviation': False,
            'residual_gp': False,
            'alpha5_improvement': False
        }
        
        # 実際のデータに基づく条件チェック（実装例）
        # ここでは仮の条件を設定
        if 'turbo_notes' in self.b_data.get('turbo_screen_matrix', {}):
            notes = self.b_data['turbo_screen_matrix']['turbo_notes']
            
            # GM乖離チェック（仮の実装）
            if 'gm_deviation' in notes:
                conditions['gm_deviation'] = True
                
            # 残差GPチェック（仮の実装）
            if 'residual_gp' in notes:
                conditions['residual_gp'] = True
                
            # α5改善チェック（仮の実装）
            if 'alpha5_improvement' in notes:
                conditions['alpha5_improvement'] = True
                
        return conditions
    
    def generate_turbo_display(self):
        """Turbo Screen表示を生成"""
        if not self.load_data():
            return None
            
        turbo_metrics = self.calculate_turbo_screen_metrics()
        turbo_edges = self.evaluate_turbo_edges()
        downgrade_conditions = self.check_auto_downgrade_conditions()
        
        display = {
            'header': 'Turbo Screen Matrix (Core★/Screen★)',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'ticker': self.ticker_path.name,
            'axes': turbo_metrics,
            'edges': turbo_edges,
            'auto_downgrade': downgrade_conditions,
            'display_config': {
                'mode': 'turbo_screen',
                'show_core': True,
                'show_screen': True,
                'show_comparison': True
            }
        }
        
        return display
    
    def print_turbo_display(self):
        """Turbo Screen表示を出力"""
        display = self.generate_turbo_display()
        if not display:
            return
            
        print(f"\n{'='*60}")
        print(f"TURBO SCREEN MATRIX - {display['ticker']}")
        print(f"Timestamp: {display['timestamp']}")
        print(f"{'='*60}")
        
        # 軸別表示
        print("\n【軸別評価】")
        for axis_name, metrics in display['axes'].items():
            print(f"\n{axis_name.upper()}:")
            print(f"  Core（安全）:  ★{metrics['core']['stars']} 確信度{metrics['core']['confidence']}")
            print(f"  Screen（攻め）: ★{metrics['screen']['stars']} 確信度{metrics['screen']['confidence']}")
            print(f"  市場織込み: {metrics['market_incorporation']}")
            print(f"  Alpha不透明度: {metrics['alpha_opacity']}")
            print(f"  方向性バイアス: {metrics['directional_bias']}")
        
        # Edge表示
        print(f"\n【Turbo Edges (P≥60, TTL≤14d)】")
        for edge in display['edges']:
            status_icon = "✅" if edge['status'] == 'ADOPTED' else "❌"
            print(f"  {status_icon} {edge['name']}")
            print(f"    P={edge['p']}, TTL={edge['ttl']}, 要約: {edge['summary']}")
            if edge['dual_anchor_status']:
                print(f"    アンカー: {edge['dual_anchor_status']}")
        
        # 自動格下げ条件
        print(f"\n【自動格下げ条件】")
        for condition, triggered in display['auto_downgrade'].items():
            status = "⚠️" if triggered else "✅"
            print(f"  {status} {condition}: {'トリガー' if triggered else '正常'}")
        
        print(f"\n{'='*60}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python turbo_screen_display.py <ticker_path>")
        print("Example: python turbo_screen_display.py ahf/tickers/RKLB")
        sys.exit(1)
        
    ticker_path = sys.argv[1]
    display = TurboScreenDisplay(ticker_path)
    display.print_turbo_display()

if __name__ == "__main__":
    main()


