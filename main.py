"""
AHF（Analytic Homeostasis Framework）v0.1/MVP
合言葉: Facts in, balance out.
目的: 一次情報（T1）をA/B/Cマトリクスに流し、①右肩上がり × ②傾きの質 × ③時間を"一体で"評価
"""

import os
import sys
import yaml
import csv
import datetime
from pathlib import Path
from typing import Dict, List, Any

class AHFv01Manager:
    """AHF v0.1/MVP 管理システム"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.catalog_path = self.base_path / "_catalog"
        self.templates_path = self.base_path / "_templates"
        self.rules_path = self.base_path / "_rules"
        self.ingest_path = self.base_path / "_ingest"
        self.tickers_path = self.base_path / "tickers"
        self.scripts_path = self.base_path / "_scripts"
    
    def get_ticker_list(self) -> List[Dict[str, str]]:
        """銘柄一覧を取得"""
        tickers_file = self.catalog_path / "tickers.csv"
        if not tickers_file.exists():
            return []
        
        tickers = []
        with open(tickers_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                tickers.append(row)
        return tickers
    
    def get_horizon_index(self) -> List[Dict[str, str]]:
        """Horizon索引を取得"""
        horizon_file = self.catalog_path / "horizon_index.csv"
        if not horizon_file.exists():
            return []
        
        horizons = []
        with open(horizon_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                horizons.append(row)
        return horizons
    
    def get_kpi_watch(self) -> List[Dict[str, str]]:
        """KPI監視リストを取得"""
        kpi_file = self.catalog_path / "kpi_watch.csv"
        if not kpi_file.exists():
            return []
        
        kpis = []
        with open(kpi_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                kpis.append(row)
        return kpis
    
    def get_ticker_analysis(self, ticker: str) -> Dict[str, Any]:
        """銘柄の分析結果を取得"""
        current_path = self.tickers_path / ticker / "current"
        
        analysis = {
            'ticker': ticker,
            'A': None,
            'B': None,
            'C': None,
            'facts': None
        }
        
        # A.yaml
        a_file = current_path / "A.yaml"
        if a_file.exists():
            with open(a_file, 'r', encoding='utf-8') as f:
                analysis['A'] = yaml.safe_load(f)
        
        # B.yaml
        b_file = current_path / "B.yaml"
        if b_file.exists():
            with open(b_file, 'r', encoding='utf-8') as f:
                analysis['B'] = yaml.safe_load(f)
        
        # C.yaml
        c_file = current_path / "C.yaml"
        if c_file.exists():
            with open(c_file, 'r', encoding='utf-8') as f:
                analysis['C'] = yaml.safe_load(f)
        
        # facts.md
        facts_file = current_path / "facts.md"
        if facts_file.exists():
            with open(facts_file, 'r', encoding='utf-8') as f:
                analysis['facts'] = f.read()
        
        return analysis
    
    def add_fact(self, ticker: str, date: str, tag: str, category: str, 
                 verbatim: str, impact: str, source: str = ""):
        """facts.mdに新しい事実を追加"""
        facts_file = self.tickers_path / ticker / "current" / "facts.md"
        if not facts_file.exists():
            # currentにない場合は最新のスナップショットを探す
            snapshots_path = self.tickers_path / ticker / "snapshots"
            if snapshots_path.exists():
                latest_snapshot = max(snapshots_path.iterdir(), key=os.path.getctime)
                facts_file = latest_snapshot / "facts.md"
        
        if facts_file.exists():
            with open(facts_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 新しい事実を先頭に追加
            new_fact = f"- [{date}][{tag}][{category}] \"{verbatim}\" (impact: {impact}) <{source}>\n"
            
            # "# facts" の後に挿入
            lines = content.split('\n')
            insert_index = 0
            for i, line in enumerate(lines):
                if line.startswith('# facts'):
                    insert_index = i + 1
                    break
            
            lines.insert(insert_index, new_fact)
            
            with open(facts_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
    
    def print_analysis_report(self, ticker: str):
        """銘柄分析レポートを1ページで出力"""
        analysis = self.get_ticker_analysis(ticker)
        
        print(f"=== {ticker} 分析レポート ===")
        print(f"合言葉: Facts in, balance out.")
        print()
        
        # A: 材料
        if analysis['A']:
            print("【A: 材料】")
            core = analysis['A'].get('core', {})
            
            # ① 右肩上がり
            right_shoulder = core.get('right_shoulder', [])
            if right_shoulder:
                print("① 右肩上がり:")
                for item in right_shoulder:
                    print(f"  • [{item.get('date', 'N/A')}][{item.get('tag', 'N/A')}] {item.get('verbatim', 'N/A')}")
                    print(f"    impact: {', '.join(item.get('impact_kpi', []))}")
            
            # ② 傾きの質
            slope_quality = core.get('slope_quality', [])
            if slope_quality:
                print("② 傾きの質:")
                for item in slope_quality:
                    print(f"  • [{item.get('date', 'N/A')}][{item.get('tag', 'N/A')}] {item.get('verbatim', 'N/A')}")
                    print(f"    impact: {', '.join(item.get('impact_kpi', []))}")
            
            # ③ 時間
            time_profile = core.get('time_profile', [])
            if time_profile:
                print("③ 時間:")
                for item in time_profile:
                    print(f"  • [{item.get('date', 'N/A')}][{item.get('tag', 'N/A')}] {item.get('verbatim', 'N/A')}")
                    print(f"    impact: {', '.join(item.get('impact_kpi', []))}")
            
            # ④ 時間注釈
            time_annotation = analysis['A'].get('time_annotation', {})
            if time_annotation.get('note'):
                print(f"④ 〔Time〕注釈: {time_annotation.get('note')}")
                print(f"   Δt: {time_annotation.get('delta_t_quarters', 0)}Q, window: {time_annotation.get('window_quarters', 2)}Q")
        
        print()
        
        # B: 結論
        if analysis['B']:
            print("【B: 結論】")
            horizon = analysis['B'].get('horizon', {})
            stance = analysis['B'].get('stance', {})
            kpi_watch = analysis['B'].get('kpi_watch', [])
            
            # Horizon
            print("Horizon:")
            for period, data in horizon.items():
                if isinstance(data, dict):
                    verdict = data.get('verdict', 'N/A')
                    delta_irr = data.get('delta_irr_bp', 0)
                    print(f"  {period}: {verdict} (ΔIRR: {delta_irr}bp)")
            
            # Stance
            print(f"決定: {stance.get('decision', 'N/A')} ({stance.get('size', 'N/A')})")
            print(f"理由: {stance.get('reason', 'N/A')}")
            
            # KPI監視
            if kpi_watch:
                print("KPI監視:")
                for kpi in kpi_watch:
                    print(f"  • {kpi}")
        
        print()
        
        # C: 反証
        if analysis['C']:
            print("【C: 反証】")
            tests = analysis['C'].get('tests', {})
            
            for test_name, test_data in tests.items():
                if isinstance(test_data, dict):
                    result = test_data.get('result', 'N/A')
                    note = test_data.get('note', 'N/A')
                    print(f"  {test_name}: {result} - {note}")
        
        print()
        print("=" * 50)

def print_dashboard():
    """ダッシュボード表示"""
    manager = AHFv01Manager()
    
    print("=== AHF v0.1/MVP ダッシュボード ===")
    print("合言葉: Facts in, balance out.")
    print("目的: ①右肩上がり × ②傾きの質 × ③時間を一体で評価")
    print()
    
    # 銘柄一覧
    tickers = manager.get_ticker_list()
    print(f"登録銘柄数: {len(tickers)}")
    
    # Horizon索引
    horizons = manager.get_horizon_index()
    print(f"Horizon分析数: {len(horizons)}")
    
    # 最新の分析結果
    print("\n=== 最新分析結果 ===")
    for ticker_info in tickers[:5]:  # 最初の5銘柄
        ticker = ticker_info['ticker']
        analysis = manager.get_ticker_analysis(ticker)
        
        if analysis['B']:
            stance = analysis['B'].get('stance', {})
            decision = stance.get('decision', 'N/A')
            size = stance.get('size', 'N/A')
            print(f"{ticker}: {decision} ({size})")
        else:
            print(f"{ticker}: 分析未実施")

def interactive_mode():
    """インタラクティブモード"""
    manager = AHFv01Manager()
    
    print("=== AHF v0.1/MVP インタラクティブモード ===")
    print("合言葉: Facts in, balance out.")
    print()
    print("コマンド:")
    print("  dashboard - ダッシュボード表示")
    print("  tickers - 銘柄一覧")
    print("  analyze <ticker> - 銘柄分析レポート表示")
    print("  fact <ticker> <date> <tag> <category> <verbatim> <impact> [source] - 事実追加")
    print("  scripts - PowerShellスクリプト一覧")
    print("  quit - 終了")
    print()
    
    while True:
        try:
            command = input("AHF> ").strip().split()
            
            if not command:
                continue
            
            cmd = command[0].lower()
            
            if cmd == 'quit':
                break
            elif cmd == 'dashboard':
                print_dashboard()
            elif cmd == 'tickers':
                tickers = manager.get_ticker_list()
                print("\n=== 銘柄一覧 ===")
                for ticker in tickers:
                    print(f"{ticker['ticker']}: {ticker['name']} ({ticker['sector']})")
            elif cmd == 'analyze' and len(command) > 1:
                ticker = command[1].upper()
                manager.print_analysis_report(ticker)
            elif cmd == 'fact' and len(command) > 6:
                ticker = command[1].upper()
                date = command[2]
                tag = command[3]
                category = command[4]
                verbatim = command[5]
                impact = command[6]
                source = command[7] if len(command) > 7 else ""
                manager.add_fact(ticker, date, tag, category, verbatim, impact, source)
                print(f"事実追加完了: {ticker}")
            elif cmd == 'scripts':
                print("\n=== PowerShellスクリプト ===")
                print("  New-AHFProject.ps1 - プロジェクト初期化")
                print("  Add-AHFTicker.ps1 - 銘柄追加")
                print("  Get-PolygonBars.ps1 - 価格データ取得")
                print("  New-AHFSnapshot.ps1 - スナップショット作成")
                print("\n使用例:")
                print("  pwsh .\\_scripts\\Add-AHFTicker.ps1 -Ticker WOLF")
                print("  pwsh .\\_scripts\\Get-PolygonBars.ps1 -Ticker WOLF -From 2024-01-01 -To 2025-09-13")
            else:
                print("無効なコマンドです。'help' でヘルプを表示。")
                
        except KeyboardInterrupt:
            print("\n終了します。")
            break
        except Exception as e:
            print(f"エラー: {e}")

def main():
    """メイン実行関数"""
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_mode()
    else:
        print_dashboard()

if __name__ == "__main__":
    main()