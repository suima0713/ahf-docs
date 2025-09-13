"""
AHF銘柄分析テンプレート
1ページに落とす分析結果の標準フォーマット
"""

import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from core.ahf_engine import T1Analysis, AHFAnalysisEngine
from evolution.hh_evolution import HHEvolutionEngine

@dataclass
class StockAnalysis:
    """銘柄分析結果（1ページ形式）"""
    stock_code: str
    stock_name: str
    analysis_date: datetime.datetime
    t1_analysis: T1Analysis
    matrix_foundation: float
    horizon_status: Dict
    kpi_status: Dict
    time_annotations: List[str]
    evolution_status: Dict
    summary: str

class AHFStockAnalyzer:
    """AHF銘柄分析器（1ページ出力）"""
    
    def __init__(self):
        self.ahf_engine = AHFAnalysisEngine()
        self.evolution_engine = HHEvolutionEngine()
    
    def analyze_stock(self, stock_code: str, stock_name: str, 
                     market_data: Dict, fundamental_data: Dict) -> StockAnalysis:
        """
        銘柄分析実行（AHFループで1ページに落とす）
        
        Args:
            stock_code: 銘柄コード
            stock_name: 銘柄名
            market_data: 市場データ
            fundamental_data: ファンダメンタルデータ
            
        Returns:
            1ページ分析結果
        """
        # T1分析生成
        t1 = self._generate_t1_analysis(market_data, fundamental_data)
        
        # 30秒ループ実行
        loop_result = self.ahf_engine.run_30_second_loop(t1)
        
        # 時間注釈追加
        time_annotations = self._generate_time_annotations(market_data)
        for annotation in time_annotations:
            self.ahf_engine.add_time_annotation(annotation)
        
        # HH進化評価
        evolution_result = self.evolution_engine.evaluate_evolution_readiness(
            time_annotations_count=len(time_annotations),
            total_updates=len(self.ahf_engine.analysis_history),
            current_irr_data=self._extract_irr_data(market_data)
        )
        
        # 1ページ分析結果構築
        analysis = StockAnalysis(
            stock_code=stock_code,
            stock_name=stock_name,
            analysis_date=datetime.datetime.now(),
            t1_analysis=t1,
            matrix_foundation=loop_result['matrix_update']['foundation_value'],
            horizon_status=loop_result['horizon_update'],
            kpi_status=loop_result['kpi_monitoring'],
            time_annotations=time_annotations,
            evolution_status=evolution_result,
            summary=self._generate_summary(loop_result, evolution_result)
        )
        
        return analysis
    
    def _generate_t1_analysis(self, market_data: Dict, fundamental_data: Dict) -> T1Analysis:
        """T1分析生成（どこに効く？いつ？も一言）"""
        # 市場データから影響範囲を特定
        impact_scope = self._determine_impact_scope(market_data)
        
        # タイミングを特定
        timing = self._determine_timing(market_data)
        
        # 簡潔な結論
        conclusion = self._generate_conclusion(market_data, fundamental_data)
        
        return T1Analysis(
            impact_scope=impact_scope,
            timing=timing,
            conclusion=conclusion
        )
    
    def _determine_impact_scope(self, market_data: Dict) -> str:
        """影響範囲特定（どこに効く？）"""
        # 簡易的な影響範囲判定ロジック
        volatility = market_data.get('volatility', 0)
        volume = market_data.get('volume', 0)
        
        if volatility > 0.3:
            return "市場全体の流動性"
        elif volume > 1000000:
            return "セクター全体"
        else:
            return "個別銘柄"
    
    def _determine_timing(self, market_data: Dict) -> str:
        """タイミング特定（いつ？）"""
        # 簡易的なタイミング判定ロジック
        trend = market_data.get('trend', 0)
        
        if trend > 0.1:
            return "来四半期"
        elif trend > 0.05:
            return "来半期"
        else:
            return "来年"
    
    def _generate_conclusion(self, market_data: Dict, fundamental_data: Dict) -> str:
        """簡潔な結論生成（も一言）"""
        # 簡易的な結論生成ロジック
        pe_ratio = fundamental_data.get('pe_ratio', 0)
        growth_rate = fundamental_data.get('growth_rate', 0)
        
        if pe_ratio < 15 and growth_rate > 0.1:
            return "買いシグナル"
        elif pe_ratio > 25 or growth_rate < 0:
            return "売りシグナル"
        else:
            return "慎重観察が必要"
    
    def _generate_time_annotations(self, market_data: Dict) -> List[str]:
        """時間注釈生成"""
        annotations = []
        
        # 市場状況に基づく時間注釈
        if market_data.get('market_stress', False):
            annotations.append("市場ストレス期間中の特別監視")
        
        if market_data.get('earnings_season', False):
            annotations.append("決算シーズン中の変動性増加")
        
        if market_data.get('fed_meeting', False):
            annotations.append("FOMC会合前後の政策金利変動リスク")
        
        return annotations
    
    def _extract_irr_data(self, market_data: Dict) -> List[float]:
        """IRRデータ抽出"""
        # 簡易的なIRRデータ生成
        return market_data.get('historical_returns', [0.05, 0.06, 0.04, 0.07, 0.05, 0.08])
    
    def _generate_summary(self, loop_result: Dict, evolution_result: Dict) -> str:
        """分析サマリー生成"""
        foundation = loop_result['matrix_update']['foundation_value']
        rebalance = loop_result['rebalance_needed']
        hh_ready = evolution_result['ready_for_hh']
        
        summary_parts = [
            f"土台値: {foundation:.3f}",
            f"リバランス: {'必要' if rebalance else '不要'}",
            f"HH準備度: {'準備完了' if hh_ready else '継続監視'}"
        ]
        
        return " | ".join(summary_parts)
    
    def format_analysis_report(self, analysis: StockAnalysis) -> str:
        """分析レポートを1ページ形式でフォーマット"""
        report = f"""
=== AHF銘柄分析レポート ===
銘柄: {analysis.stock_name} ({analysis.stock_code})
分析日時: {analysis.analysis_date.strftime('%Y-%m-%d %H:%M')}

【T1分析（1行）】
どこに効く？: {analysis.t1_analysis.impact_scope}
いつ？: {analysis.t1_analysis.timing}
も一言: {analysis.t1_analysis.conclusion}

【①②③マトリクス（土台・恒常値）】
土台値: {analysis.matrix_foundation:.3f}

【Horizon追跡】
6M: {analysis.horizon_status['horizon_6m']}
1Y: {analysis.horizon_status['horizon_1y']}
3Y: {analysis.horizon_status['horizon_3y']}
5Y: {analysis.horizon_status['horizon_5y']}

【KPI監視（×2）】
{analysis.kpi_status['kpi1']['name']}: {analysis.kpi_status['kpi1']['value']:.3f} ({analysis.kpi_status['kpi1']['status']})
{analysis.kpi_status['kpi2']['name']}: {analysis.kpi_status['kpi2']['value']:.3f} ({analysis.kpi_status['kpi2']['status']})

【④時間の注釈】
{chr(10).join(f"- {annotation}" for annotation in analysis.time_annotations) if analysis.time_annotations else "なし"}

【HH進化状況】
現在ステータス: {analysis.evolution_status['current_status']}
HH準備完了: {'はい' if analysis.evolution_status['ready_for_hh'] else 'いいえ'}

進化サイン:
- 手当てが減る: {analysis.evolution_status['evolution_signs']['手当てが減る']['achieved']} ({analysis.evolution_status['evolution_signs']['手当てが減る']['current']:.1%})
- 一貫性が増す: {analysis.evolution_status['evolution_signs']['一貫性が増す']['achieved']} ({analysis.evolution_status['evolution_signs']['一貫性が増す']['current']:.1%})
- 反証に強い: {analysis.evolution_status['evolution_signs']['反証に強い']['achieved']} ({analysis.evolution_status['evolution_signs']['反証に強い']['current']:.1%})

【サマリー】
{analysis.summary}

合言葉: Facts in, balance out.
"""
        return report

# 使用例
if __name__ == "__main__":
    analyzer = AHFStockAnalyzer()
    
    # サンプルデータ
    market_data = {
        'volatility': 0.25,
        'volume': 500000,
        'trend': 0.08,
        'market_stress': False,
        'earnings_season': True,
        'fed_meeting': False,
        'historical_returns': [0.05, 0.06, 0.04, 0.07, 0.05, 0.08, 0.06, 0.09]
    }
    
    fundamental_data = {
        'pe_ratio': 18.5,
        'growth_rate': 0.12
    }
    
    # 銘柄分析実行
    analysis = analyzer.analyze_stock("7203", "トヨタ自動車", market_data, fundamental_data)
    
    # 1ページレポート出力
    report = analyzer.format_analysis_report(analysis)
    print(report)
