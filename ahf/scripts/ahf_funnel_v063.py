#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AHF v0.6.3 高速ファネル統合システム
Fast-Screen → Mini-Confirm → Deep-Dive
"""

import json
import sys
import subprocess
import argparse
import csv
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

class AHFV063Funnel:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.results = {}
        self.funnel_stats = {
            'total_screened': 0,
            'fast_screen_passed': 0,
            'mini_confirm_passed': 0,
            'deep_dive_candidates': 0,
            'processing_time': 0
        }
    
    def run_fast_screen(self, ticker: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Fast-Screen実行（8-12分）"""
        try:
            # Fast-Screen実行
            p = subprocess.run(
                [sys.executable, "ahf/mvp4/fast_screen_v063.py", "--config", self.config_path],
                input=json.dumps(data).encode("utf-8"),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            fast_screen_results = json.loads(p.stdout.decode("utf-8"))
            
            # 通過判定
            decision = fast_screen_results.get('pass_criteria', {}).get('decision', 'DROP')
            passed = decision in ['PASS', 'WATCH']
            
            return {
                'ticker': ticker,
                'stage': 'fast_screen',
                'decision': decision,
                'passed': passed,
                'results': fast_screen_results,
                'processing_time': '8-12min'
            }
        except Exception as e:
            return {
                'ticker': ticker,
                'stage': 'fast_screen',
                'decision': 'ERROR',
                'passed': False,
                'error': str(e),
                'processing_time': '8-12min'
            }
    
    def run_mini_confirm(self, ticker: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mini-Confirm実行（15-25分）"""
        try:
            # Mini-Confirm実行
            p = subprocess.run(
                [sys.executable, "ahf/mvp4/mini_confirm_v063.py", "--config", self.config_path],
                input=json.dumps(data).encode("utf-8"),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            mini_confirm_results = json.loads(p.stdout.decode("utf-8"))
            
            # 通過判定
            decision = mini_confirm_results.get('pass_criteria', {}).get('decision', 'DROP')
            passed = decision == 'GO'
            
            return {
                'ticker': ticker,
                'stage': 'mini_confirm',
                'decision': decision,
                'passed': passed,
                'results': mini_confirm_results,
                'processing_time': '15-25min'
            }
        except Exception as e:
            return {
                'ticker': ticker,
                'stage': 'mini_confirm',
                'decision': 'ERROR',
                'passed': False,
                'error': str(e),
                'processing_time': '15-25min'
            }
    
    def run_deep_dive(self, ticker: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Deep-Dive実行（既存v0.6.3）"""
        try:
            # Deep-Dive実行（既存の統合スクリプト使用）
            p = subprocess.run(
                [sys.executable, "ahf/scripts/ahf_v063_integrated.py", 
                 "--config", self.config_path,
                 "--state", "/dev/stdin",
                 "--out", "/dev/stdout"],
                input=json.dumps(data).encode("utf-8"),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            deep_dive_results = json.loads(p.stdout.decode("utf-8"))
            
            return {
                'ticker': ticker,
                'stage': 'deep_dive',
                'decision': 'COMPLETED',
                'passed': True,
                'results': deep_dive_results,
                'processing_time': '2-4h'
            }
        except Exception as e:
            return {
                'ticker': ticker,
                'stage': 'deep_dive',
                'decision': 'ERROR',
                'passed': False,
                'error': str(e),
                'processing_time': '2-4h'
            }
    
    def process_ticker(self, ticker: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """単一銘柄のファネル処理"""
        start_time = datetime.now()
        
        # Stage 1: Fast-Screen
        print(f"🔄 {ticker}: Fast-Screen実行中...", file=sys.stderr)
        fast_screen_result = self.run_fast_screen(ticker, data)
        
        if not fast_screen_result['passed']:
            return {
                'ticker': ticker,
                'final_decision': 'DROP',
                'reason': 'Fast-Screen failed',
                'stage_results': [fast_screen_result],
                'total_time': (datetime.now() - start_time).total_seconds() / 60
            }
        
        # Stage 2: Mini-Confirm
        print(f"🔄 {ticker}: Mini-Confirm実行中...", file=sys.stderr)
        mini_confirm_result = self.run_mini_confirm(ticker, data)
        
        if not mini_confirm_result['passed']:
            return {
                'ticker': ticker,
                'final_decision': 'WATCH',
                'reason': 'Mini-Confirm failed',
                'stage_results': [fast_screen_result, mini_confirm_result],
                'total_time': (datetime.now() - start_time).total_seconds() / 60
            }
        
        # Stage 3: Deep-Dive
        print(f"🔄 {ticker}: Deep-Dive実行中...", file=sys.stderr)
        deep_dive_result = self.run_deep_dive(ticker, data)
        
        return {
            'ticker': ticker,
            'final_decision': 'GO',
            'reason': 'All stages passed',
            'stage_results': [fast_screen_result, mini_confirm_result, deep_dive_result],
            'total_time': (datetime.now() - start_time).total_seconds() / 60
        }
    
    def process_watchlist(self, watchlist_path: str) -> Dict[str, Any]:
        """ウォッチリスト一括処理"""
        results = {
            'meta': {
                'processed_at': datetime.now().isoformat(),
                'watchlist_path': watchlist_path,
                'version': 'v0.6.3-funnel'
            },
            'tickers': [],
            'summary': {
                'total_processed': 0,
                'fast_screen_passed': 0,
                'mini_confirm_passed': 0,
                'deep_dive_candidates': 0,
                'total_time_minutes': 0
            }
        }
        
        # ウォッチリスト読み込み
        with open(watchlist_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            tickers = list(reader)
        
        print(f"📊 ウォッチリスト処理開始: {len(tickers)}銘柄", file=sys.stderr)
        
        for ticker_data in tickers:
            ticker = ticker_data['ticker']
            print(f"\n🏷️  処理中: {ticker}", file=sys.stderr)
            
            # 銘柄データ準備（CSVから辞書に変換）
            data = {
                'ticker': ticker,
                'as_of': ticker_data.get('as_of', datetime.now().strftime('%Y-%m-%d')),
                'revenue_$k': float(ticker_data.get('revenue_$k', 0)),
                'gaap_gm_pct': float(ticker_data.get('gaap_gm_pct', 0)),
                'adj_ebitda_$k': float(ticker_data.get('adj_ebitda_$k', 0)),
                'contract_assets_$k': float(ticker_data.get('contract_assets_$k', 0)),
                'contract_liabilities_$k': float(ticker_data.get('contract_liabilities_$k', 0)),
                'rpo_12m_pct': float(ticker_data.get('rpo_12m_pct', 0)),
                'backlog_12m_pct': float(ticker_data.get('backlog_12m_pct', 0)),
                'item1a_text': ticker_data.get('item1a_text', ''),
                'guidance_rev': {
                    'low': float(ticker_data.get('guidance_rev_low', 0)),
                    'mid': float(ticker_data.get('guidance_rev_mid', 0)),
                    'high': float(ticker_data.get('guidance_rev_high', 0))
                },
                'guidance_gm': {
                    'low': float(ticker_data.get('guidance_gm_low', 0)),
                    'mid': float(ticker_data.get('guidance_gm_mid', 0)),
                    'high': float(ticker_data.get('guidance_gm_high', 0))
                },
                'guidance_ebitda': {
                    'low': float(ticker_data.get('guidance_ebitda_low', 0)),
                    'high': float(ticker_data.get('guidance_ebitda_high', 0))
                }
            }
            
            # ファネル処理実行
            ticker_result = self.process_ticker(ticker, data)
            results['tickers'].append(ticker_result)
            
            # 統計更新
            results['summary']['total_processed'] += 1
            if ticker_result['final_decision'] != 'DROP':
                results['summary']['fast_screen_passed'] += 1
            if ticker_result['final_decision'] in ['GO', 'WATCH']:
                results['summary']['mini_confirm_passed'] += 1
            if ticker_result['final_decision'] == 'GO':
                results['summary']['deep_dive_candidates'] += 1
            
            results['summary']['total_time_minutes'] += ticker_result['total_time']
            
            # 進捗表示
            print(f"  ✅ 完了: {ticker_result['final_decision']} ({ticker_result['total_time']:.1f}分)", file=sys.stderr)
        
        return results
    
    def display_summary(self, results: Dict[str, Any]):
        """結果サマリー表示"""
        summary = results['summary']
        
        print(f"\n📊 ファネル処理完了", file=sys.stderr)
        print(f"=" * 50, file=sys.stderr)
        print(f"総処理銘柄数: {summary['total_processed']}", file=sys.stderr)
        print(f"Fast-Screen通過: {summary['fast_screen_passed']} ({summary['fast_screen_passed']/summary['total_processed']*100:.1f}%)", file=sys.stderr)
        print(f"Mini-Confirm通過: {summary['mini_confirm_passed']} ({summary['mini_confirm_passed']/summary['total_processed']*100:.1f}%)", file=sys.stderr)
        print(f"Deep-Dive候補: {summary['deep_dive_candidates']} ({summary['deep_dive_candidates']/summary['total_processed']*100:.1f}%)", file=sys.stderr)
        print(f"総処理時間: {summary['total_time_minutes']:.1f}分", file=sys.stderr)
        print(f"平均処理時間: {summary['total_time_minutes']/summary['total_processed']:.1f}分/銘柄", file=sys.stderr)
        
        # ROI計算
        original_time = summary['total_processed'] * 3  # 元々3時間/銘柄想定
        saved_time = original_time - summary['total_time_minutes']
        roi_improvement = saved_time / original_time * 100
        
        print(f"\n💰 ROI改善:", file=sys.stderr)
        print(f"元々の時間: {original_time:.1f}分", file=sys.stderr)
        print(f"実際の時間: {summary['total_time_minutes']:.1f}分", file=sys.stderr)
        print(f"時間削減: {saved_time:.1f}分 ({roi_improvement:.1f}%)", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description='AHF v0.6.3 高速ファネル')
    parser.add_argument('--config', required=True, help='設定ファイルパス')
    parser.add_argument('--watchlist', required=True, help='ウォッチリストCSVパス')
    parser.add_argument('--out', required=True, help='出力ファイルパス')
    
    args = parser.parse_args()
    
    try:
        # ファネル処理実行
        funnel = AHFV063Funnel(args.config)
        results = funnel.process_watchlist(args.watchlist)
        
        # 結果保存
        with open(args.out, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # サマリー表示
        funnel.display_summary(results)
        
        print(f"\n✅ ファネル処理完了")
        print(f"📊 結果保存: {args.out}")
        
    except Exception as e:
        print(f"❌ エラー: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()

