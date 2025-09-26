#!/usr/bin/env python3
"""
Turbo Screen Edge管理機能
P再採点とTTL調整、Edge採用基準の緩和
"""

import json
import yaml
import sys
from datetime import datetime, timedelta
from pathlib import Path

class TurboScreenEdgeManager:
    def __init__(self, ticker_path):
        self.ticker_path = Path(ticker_path)
        self.triage_json_path = self.ticker_path / "current" / "triage.json"
        self.b_yaml_path = self.ticker_path / "current" / "B.yaml"
        
        # Turbo Screen基準
        self.min_p_threshold = 60  # 従来70→60
        self.max_ttl_days = 14     # 最大14日
        self.confidence_boost = 10  # ±10pp（従来±5pp）
        self.confidence_clip_min = 45  # 45-95%（従来50-90%）
        self.confidence_clip_max = 95
        
    def load_triage_data(self):
        """triage.jsonを読み込み"""
        try:
            with open(self.triage_json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"WARNING: triage.json not found at {self.triage_json_path}")
            return {"CONFIRMED": [], "UNCERTAIN": []}
    
    def rescore_edges(self, triage_data):
        """EdgeのP再採点（Turbo Screen基準）"""
        rescored_edges = []
        
        # UNCERTAINからTurbo Screen基準で再評価
        for item in triage_data.get('UNCERTAIN', []):
            # P値の推定（実装例）
            estimated_p = self.estimate_p_value(item)
            
            if estimated_p >= self.min_p_threshold:
                # Turbo Screen基準で採用
                edge_info = {
                    'name': item.get('kpi', 'Unknown'),
                    'p': estimated_p,
                    'ttl': f"{self.max_ttl_days}d",
                    'source': item.get('url_index', ''),
                    'status': 'TURBO_ADOPTED',
                    'original_status': 'UNCERTAIN'
                }
                rescored_edges.append(edge_info)
        
        return rescored_edges
    
    def estimate_p_value(self, item):
        """P値の推定（簡易実装）"""
        # 実際の実装では、より複雑なロジックを使用
        kpi = item.get('kpi', '').lower()
        
        # キーワードベースの推定
        if 'guidance' in kpi or 'revenue' in kpi:
            return 75
        elif 'margin' in kpi or 'gm' in kpi:
            return 70
        elif 'contract' in kpi or 'backlog' in kpi:
            return 65
        else:
            return 60  # 最小閾値
    
    def adjust_ttl(self, edges):
        """TTL調整（最大14日）"""
        adjusted_edges = []
        
        for edge in edges:
            ttl_days = int(edge.get('ttl', '14d').replace('d', ''))
            
            # TTL調整
            if ttl_days > self.max_ttl_days:
                ttl_days = self.max_ttl_days
                
            edge['ttl'] = f"{ttl_days}d"
            edge['ttl_adjusted'] = True
            adjusted_edges.append(edge)
            
        return adjusted_edges
    
    def calculate_confidence_boost(self, base_confidence):
        """確信度ブースト計算（±10pp）"""
        try:
            # パーセント記号を除去
            if isinstance(base_confidence, str):
                conf_value = float(base_confidence.replace('%', ''))
            else:
                conf_value = float(base_confidence)
                
            # Turbo Screen基準で+10pp
            boosted_confidence = min(conf_value + 10, self.confidence_clip_max)
            boosted_confidence = max(boosted_confidence, self.confidence_clip_min)
            
            return f"{boosted_confidence}%"
            
        except (ValueError, TypeError):
            return "70%"  # デフォルト値
    
    def update_b_yaml(self, rescored_edges):
        """B.yamlをTurbo Screen基準で更新"""
        try:
            with open(self.b_yaml_path, 'r', encoding='utf-8') as f:
                b_data = yaml.safe_load(f)
        except FileNotFoundError:
            print(f"ERROR: B.yaml not found at {self.b_yaml_path}")
            return False
            
        # Turbo Screen Edge評価を追加
        if 'edge_evaluation' not in b_data:
            b_data['edge_evaluation'] = {}
            
        # Turbo Screen基準のEdge評価を追加
        b_data['edge_evaluation']['turbo_screen_edges'] = {
            'rescore_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'min_p_threshold': self.min_p_threshold,
            'max_ttl_days': self.max_ttl_days,
            'confidence_boost': f"+{self.confidence_boost}pp",
            'adopted_edges': rescored_edges
        }
        
        # ファイル保存
        try:
            with open(self.b_yaml_path, 'w', encoding='utf-8') as f:
                yaml.dump(b_data, f, default_flow_style=False, allow_unicode=True)
            return True
        except Exception as e:
            print(f"ERROR: Failed to save B.yaml: {e}")
            return False
    
    def process_turbo_screen_edges(self):
        """Turbo Screen Edge処理のメイン関数"""
        print("Turbo Screen Edge処理を開始...")
        
        # triage.json読み込み
        triage_data = self.load_triage_data()
        
        # Edge再採点
        rescored_edges = self.rescore_edges(triage_data)
        print(f"再採点完了: {len(rescored_edges)}件のEdgeがTurbo Screen基準で採用")
        
        # TTL調整
        adjusted_edges = self.adjust_ttl(rescored_edges)
        print(f"TTL調整完了: 最大{self.max_ttl_days}日に調整")
        
        # B.yaml更新
        if self.update_b_yaml(adjusted_edges):
            print("B.yaml更新完了")
        else:
            print("ERROR: B.yaml更新失敗")
            return False
            
        # 結果表示
        self.print_results(adjusted_edges)
        return True
    
    def print_results(self, edges):
        """結果表示"""
        print(f"\n{'='*50}")
        print("TURBO SCREEN EDGE 処理結果")
        print(f"{'='*50}")
        
        print(f"処理時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"採用基準: P≥{self.min_p_threshold}, TTL≤{self.max_ttl_days}日")
        print(f"確信度ブースト: +{self.confidence_boost}pp")
        print(f"確信度クリップ: {self.confidence_clip_min}-{self.confidence_clip_max}%")
        
        print(f"\n採用Edge ({len(edges)}件):")
        for i, edge in enumerate(edges, 1):
            print(f"  {i}. {edge['name']}")
            print(f"     P={edge['p']}, TTL={edge['ttl']}")
            print(f"     ソース: {edge.get('source', 'N/A')}")
            print(f"     元ステータス: {edge.get('original_status', 'N/A')}")
            print()

def main():
    if len(sys.argv) != 2:
        print("Usage: python turbo_screen_edge_manager.py <ticker_path>")
        print("Example: python turbo_screen_edge_manager.py ahf/tickers/RKLB")
        sys.exit(1)
        
    ticker_path = sys.argv[1]
    manager = TurboScreenEdgeManager(ticker_path)
    
    if manager.process_turbo_screen_edges():
        print("\n✅ Turbo Screen Edge処理が正常に完了しました")
    else:
        print("\n❌ Turbo Screen Edge処理でエラーが発生しました")
        sys.exit(1)

if __name__ == "__main__":
    main()





