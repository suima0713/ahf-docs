"""
圧縮分析テンプレート
複雑さは量ではなく"圧縮の質"で勝つ
AHFの枠に詰め込んで、リスク最大化しつつフレームアウト最小化
"""

import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from core.complexity_packing import ComplexityPackingEngine, AtomicFact
from core.high_risk_principles import HighRiskPrinciplesEngine

@dataclass
class CompressedAnalysis:
    """圧縮分析結果（1ページ）"""
    stock_code: str
    stock_name: str
    analysis_date: datetime.datetime
    
    # 原子化結果
    atomic_fact: AtomicFact
    
    # 圧縮指標
    compression_metrics: Dict
    
    # 決断結果
    decision_result: Dict
    
    # ハイリスク原則適用結果
    risk_principles: Dict
    
    # 1ページ出力
    one_page_output: Dict
    
    # サマリー
    summary: str

class CompressedAnalysisEngine:
    """圧縮分析エンジン"""
    
    def __init__(self):
        self.complexity_engine = ComplexityPackingEngine()
        self.risk_engine = HighRiskPrinciplesEngine()
    
    def analyze_with_compression(self, 
                               stock_code: str,
                               stock_name: str,
                               verbatim: str,
                               impact_kpi: str,
                               timing: str,
                               market_context: Dict = None) -> CompressedAnalysis:
        """
        圧縮分析実行
        
        Args:
            stock_code: 銘柄コード
            stock_name: 銘柄名
            verbatim: 逐語1行（T1）
            impact_kpi: どこに効く？（KPI名）
            timing: いつ？（四半期レンジ）
            market_context: 市場コンテキスト
            
        Returns:
            圧縮分析結果
        """
        # 1. 複雑さ圧縮（5手順）
        compression_result = self.complexity_engine.process_complexity_packing(
            verbatim, impact_kpi, timing
        )
        
        # 2. ハイリスク原則適用
        factors = {
            'factor1': compression_result['matrix_mapping'].factor1_trend,
            'factor2': compression_result['matrix_mapping'].factor2_quality,
            'factor3': compression_result['matrix_mapping'].factor3_time,
            'factor4': 0.3  # 時間注釈は制限内
        }
        
        # 1ページ出力作成
        one_page_output = self._create_one_page_output(compression_result)
        
        # 現在のKPI値（簡易版）
        current_kpis = self._extract_current_kpis(compression_result, market_context)
        
        # ハイリスク原則適用
        risk_principles = self.risk_engine.apply_high_risk_principles(
            factors, one_page_output, current_kpis
        )
        
        # 圧縮分析結果構築
        analysis = CompressedAnalysis(
            stock_code=stock_code,
            stock_name=stock_name,
            analysis_date=datetime.datetime.now(),
            atomic_fact=compression_result['atomic_fact'],
            compression_metrics=compression_result['compression_metrics'],
            decision_result=compression_result['decision_result'],
            risk_principles=risk_principles,
            one_page_output=one_page_output,
            summary=self._generate_compressed_summary(compression_result, risk_principles)
        )
        
        return analysis
    
    def _create_one_page_output(self, compression_result: Dict) -> Dict:
        """1ページ出力作成（差分1行＋Horizon＋KPI×2）"""
        # 差分1行
        diff_line = f"{compression_result['atomic_fact'].verbatim} → {compression_result['atomic_fact'].impact_kpi}"
        
        # Horizon（6M/1Y/3Y/5Y：はい/△/いいえ）
        horizon = {}
        compression_metrics = compression_result['compression_metrics']
        for horizon_key in ['horizon_6m', 'horizon_1y', 'horizon_3y', 'horizon_5y']:
            if hasattr(compression_metrics, horizon_key):
                metrics = getattr(compression_metrics, horizon_key)
                delta_irr = metrics.get('ΔIRR', 0)
                if delta_irr > 0.03:  # 300bp
                    horizon[horizon_key.replace('horizon_', '')] = 'はい'
                elif delta_irr > 0.01:  # 100bp
                    horizon[horizon_key.replace('horizon_', '')] = '△'
                else:
                    horizon[horizon_key.replace('horizon_', '')] = 'いいえ'
        
        # KPI×2
        kpi_x2 = {
            'ROIIC-WACC': compression_metrics.roiic_wacc_core,
            'ΔIRR_1Y': compression_metrics.horizon_1y.get('ΔIRR', 0)
        }
        
        return {
            '差分1行': diff_line,
            'Horizon': horizon,
            'KPI×2': kpi_x2,
            'timestamp': datetime.datetime.now()
        }
    
    def _extract_current_kpis(self, compression_result: Dict, market_context: Dict = None) -> Dict:
        """現在のKPI値抽出"""
        if market_context is None:
            market_context = {}
        
        # 圧縮結果からKPI値を抽出
        compression_metrics = compression_result['compression_metrics']
        current_kpis = {
            '売上成長率': compression_metrics.horizon_1y.get('Δg', 0) * 100,
            '営業利益率': compression_metrics.roiic_wacc_core * 100,
            'FCF': compression_metrics.horizon_1y.get('ΔIRR', 0) * 1000000,
            '在庫回転率': compression_metrics.horizon_6m.get('Δt', 0) + 0.5
        }
        
        # 市場コンテキストから追加
        if market_context:
            current_kpis.update(market_context.get('kpis', {}))
        
        return current_kpis
    
    def _generate_compressed_summary(self, compression_result: Dict, risk_principles: Dict) -> str:
        """圧縮サマリー生成"""
        decision = compression_result['decision_result']
        risk_level = risk_principles['risk_level']
        
        summary_parts = [
            f"決断: {decision.go_decision}",
            f"リスク: {risk_level}",
            f"ROIIC-WACC: {compression_result['compression_metrics'].roiic_wacc_core:.3f}",
            f"ΔIRR_1Y: {compression_result['compression_metrics'].horizon_1y.get('ΔIRR', 0):.3f}"
        ]
        
        if decision.reversal_trigger:
            summary_parts.append(f"巻き戻し: {', '.join(decision.reversal_trigger)}")
        
        return " | ".join(summary_parts)
    
    def format_compressed_report(self, analysis: CompressedAnalysis) -> str:
        """圧縮レポートを1ページ形式でフォーマット"""
        report = f"""
=== AHF圧縮分析レポート ===
銘柄: {analysis.stock_name} ({analysis.stock_code})
分析日時: {analysis.analysis_date.strftime('%Y-%m-%d %H:%M')}

【原子化事実（1行）】
逐語: {analysis.atomic_fact.verbatim}
出典: {analysis.atomic_fact.source.value}
影響KPI: {analysis.atomic_fact.impact_kpi}
タイプ: {analysis.atomic_fact.t1_type.value}
強度: {analysis.atomic_fact.strength:.3f}

【圧縮指標】
ROIIC-WACC: {analysis.compression_metrics.roiic_wacc_core:.3f}

Horizon指標:
6M: Δg={analysis.compression_metrics.horizon_6m.get('Δg', 0):.3f}, Δt={analysis.compression_metrics.horizon_6m.get('Δt', 0):.3f}, ΔIRR={analysis.compression_metrics.horizon_6m.get('ΔIRR', 0):.3f}
1Y: Δg={analysis.compression_metrics.horizon_1y.get('Δg', 0):.3f}, Δt={analysis.compression_metrics.horizon_1y.get('Δt', 0):.3f}, ΔIRR={analysis.compression_metrics.horizon_1y.get('ΔIRR', 0):.3f}
3Y: Δg={analysis.compression_metrics.horizon_3y.get('Δg', 0):.3f}, Δt={analysis.compression_metrics.horizon_3y.get('Δt', 0):.3f}, ΔIRR={analysis.compression_metrics.horizon_3y.get('ΔIRR', 0):.3f}
5Y: Δg={analysis.compression_metrics.horizon_5y.get('Δg', 0):.3f}, Δt={analysis.compression_metrics.horizon_5y.get('Δt', 0):.3f}, ΔIRR={analysis.compression_metrics.horizon_5y.get('ΔIRR', 0):.3f}

【決断結果】
Go判定: {analysis.decision_result.go_decision}
サイズ調整: {analysis.decision_result.size_adjustment:.3f}
リスクレベル: {analysis.decision_result.risk_level}
巻き戻しトリガー: {', '.join(analysis.decision_result.reversal_trigger) if analysis.decision_result.reversal_trigger else 'なし'}

【ハイリスク原則】
Primacy: {analysis.risk_principles['primacy']['primacy_compliant']}
Parsimony: {analysis.risk_principles['parsimony']['parsimony_compliant']}
Reversibility: {analysis.risk_principles['reversibility']['reversibility_compliant']}
総合判定: {analysis.risk_principles['overall_decision']['decision']}

【1ページ出力】
{analysis.one_page_output['差分1行']}

Horizon: {analysis.one_page_output['Horizon']}
KPI×2: {analysis.one_page_output['KPI×2']}

【サマリー】
{analysis.summary}

合言葉: Facts in, balance out.
複雑さは量ではなく"圧縮の質"で勝つ。
"""
        return report

# 使用例
if __name__ == "__main__":
    engine = CompressedAnalysisEngine()
    
    # 圧縮分析実行
    analysis = engine.analyze_with_compression(
        stock_code="7203",
        stock_name="トヨタ自動車",
        verbatim="四半期売上高が前年同期比15%増加、EV事業の収益性改善",
        impact_kpi="売上高",
        timing="来四半期",
        market_context={
            'kpis': {
                '売上成長率': 0.15,
                '営業利益率': 0.12
            }
        }
    )
    
    # 圧縮レポート出力
    report = engine.format_compressed_report(analysis)
    print(report)
