"""
Complexity Packing - 枠内で複雑さを活かす5手順
AHFの枠に詰め込んで、リスク最大化しつつフレームアウト最小化
"""

import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class T1Source(Enum):
    """T1出典の強度"""
    BOTH_PARTIES = "両当事者"  # 最強
    COMPANY = "自社"
    CALL = "コール"

class T1Type(Enum):
    """T1タイプ"""
    CORE = "Core"  # 恒常値
    TIME = "Time"  # 時間注釈

@dataclass
class AtomicFact:
    """原子化された事実（1行）"""
    verbatim: str           # 逐語
    date: datetime.date     # 日付
    source: T1Source        # 出典（T1-F/P/C）
    impact_kpi: str         # 影響KPI（売上, GM, FCF, 在庫 等）
    t1_type: T1Type         # [Core] or [Time]
    strength: float         # 強度（0.0-1.0）
    timestamp: datetime.datetime

@dataclass
class NormalizedT1:
    """正規化されたT1（重複排除済み）"""
    atomic_facts: List[AtomicFact]
    latest_fact: AtomicFact
    combined_strength: float
    contradiction_flag: bool = False

@dataclass
class MatrixMapping:
    """マトリクス配置"""
    factor1_trend: float        # ①右肩上がり
    factor2_quality: float      # ②傾きの質（ROIC−WACC・ROIIC・FCF/NI）
    factor3_time: float         # ③時間
    time_annotation: str        # ④〔Time〕注釈（③の文中に一度だけ）

@dataclass
class CompressionMetrics:
    """圧縮指標"""
    horizon_6m: Dict[str, float]  # Δg, Δt, ΔIRR
    horizon_1y: Dict[str, float]
    horizon_3y: Dict[str, float]
    horizon_5y: Dict[str, float]
    roiic_wacc_core: float        # ②の質の一本芯

@dataclass
class DecisionResult:
    """決断結果"""
    go_decision: bool
    size_adjustment: float        # σで調整
    risk_level: str
    reversal_trigger: List[str]   # 巻き戻しトリガー

class ComplexityPackingEngine:
    """複雑さ圧縮エンジン"""
    
    def __init__(self):
        self.atomic_facts: List[AtomicFact] = []
        self.normalized_t1s: List[NormalizedT1] = []
        self.matrix_mapping: Optional[MatrixMapping] = None
        self.compression_metrics: Optional[CompressionMetrics] = None
        self.decision_history: List[DecisionResult] = []
    
    def process_complexity_packing(self, 
                                 verbatim: str,
                                 impact_kpi: str,
                                 timing: str) -> Dict:
        """
        複雑さ圧縮の5手順を一気に実行
        
        Args:
            verbatim: 逐語1行（T1）
            impact_kpi: どこに効く？（KPI名）
            timing: いつ？（四半期レンジ）
            
        Returns:
            圧縮結果
        """
        # 1. 原子化：事実を"1行"で取り込む
        atomic_fact = self._atomicize(verbatim, impact_kpi, timing)
        
        # 2. 正規化＆重複排除
        normalized_t1 = self._normalize_and_deduplicate(atomic_fact)
        
        # 3. マッピング
        matrix_mapping = self._mapping(normalized_t1)
        
        # 4. 圧縮指標へ落とす
        compression_metrics = self._compress_to_metrics(matrix_mapping)
        
        # 5. 決断（対角スイープ A→B→C）
        decision_result = self._make_decision(compression_metrics)
        
        return {
            'atomic_fact': atomic_fact,
            'normalized_t1': normalized_t1,
            'matrix_mapping': matrix_mapping,
            'compression_metrics': compression_metrics,
            'decision_result': decision_result,
            'processing_timestamp': datetime.datetime.now()
        }
    
    def _atomicize(self, verbatim: str, impact_kpi: str, timing: str) -> AtomicFact:
        """1. 原子化：事実を"1行"で取り込む"""
        # 出典の強度を推定（簡易版）
        source = self._estimate_source_strength(verbatim)
        
        # T1タイプを判定
        t1_type = self._determine_t1_type(verbatim, timing)
        
        # 強度を計算
        strength = self._calculate_strength(verbatim, source, t1_type)
        
        atomic_fact = AtomicFact(
            verbatim=verbatim,
            date=datetime.date.today(),
            source=source,
            impact_kpi=impact_kpi,
            t1_type=t1_type,
            strength=strength,
            timestamp=datetime.datetime.now()
        )
        
        self.atomic_facts.append(atomic_fact)
        return atomic_fact
    
    def _normalize_and_deduplicate(self, new_fact: AtomicFact) -> NormalizedT1:
        """2. 正規化＆重複排除"""
        # 同趣旨のT1を検索
        similar_facts = self._find_similar_facts(new_fact)
        
        if similar_facts:
            # 最新×強いT1だけ残す
            latest_strongest = max(similar_facts, key=lambda f: f.strength)
            
            # 矛盾チェック
            contradiction = self._check_contradiction(new_fact, latest_strongest)
            
            if contradiction:
                # Gateで停止し再検証
                return NormalizedT1(
                    atomic_facts=[new_fact],
                    latest_fact=new_fact,
                    combined_strength=new_fact.strength,
                    contradiction_flag=True
                )
            
            # 統合
            all_facts = similar_facts + [new_fact]
            combined_strength = max(f.strength for f in all_facts)
            
            normalized_t1 = NormalizedT1(
                atomic_facts=all_facts,
                latest_fact=new_fact,
                combined_strength=combined_strength
            )
        else:
            # 新規T1
            normalized_t1 = NormalizedT1(
                atomic_facts=[new_fact],
                latest_fact=new_fact,
                combined_strength=new_fact.strength
            )
        
        self.normalized_t1s.append(normalized_t1)
        return normalized_t1
    
    def _mapping(self, normalized_t1: NormalizedT1) -> MatrixMapping:
        """3. マッピング"""
        # ①右肩上がり
        factor1_trend = self._calculate_trend(normalized_t1)
        
        # ②傾きの質（ROIC−WACC・ROIIC・FCF/NI）
        factor2_quality = self._calculate_quality(normalized_t1)
        
        # ③時間
        factor3_time = self._calculate_time_factor(normalized_t1)
        
        # ④〔Time〕注釈（③の文中に一度だけ）
        time_annotation = self._generate_time_annotation(normalized_t1)
        
        matrix_mapping = MatrixMapping(
            factor1_trend=factor1_trend,
            factor2_quality=factor2_quality,
            factor3_time=factor3_time,
            time_annotation=time_annotation
        )
        
        self.matrix_mapping = matrix_mapping
        return matrix_mapping
    
    def _compress_to_metrics(self, matrix_mapping: MatrixMapping) -> CompressionMetrics:
        """4. 圧縮指標へ落とす"""
        # 各Horizonで Δg（勾配差）／Δt（前倒し/遅延）／ΔIRR を記入
        horizon_6m = self._calculate_horizon_metrics(matrix_mapping, "6M")
        horizon_1y = self._calculate_horizon_metrics(matrix_mapping, "1Y")
        horizon_3y = self._calculate_horizon_metrics(matrix_mapping, "3Y")
        horizon_5y = self._calculate_horizon_metrics(matrix_mapping, "5Y")
        
        # ②の"質"は ROIIC−WACC を一本芯に
        roiic_wacc_core = matrix_mapping.factor2_quality
        
        compression_metrics = CompressionMetrics(
            horizon_6m=horizon_6m,
            horizon_1y=horizon_1y,
            horizon_3y=horizon_3y,
            horizon_5y=horizon_5y,
            roiic_wacc_core=roiic_wacc_core
        )
        
        self.compression_metrics = compression_metrics
        return compression_metrics
    
    def _make_decision(self, compression_metrics: CompressionMetrics) -> DecisionResult:
        """5. 決断（対角スイープ A→B→C）"""
        # ①②が○で ΔIRR ≥ +300〜500bp → Go
        factor1_ok = compression_metrics.horizon_1y.get('ΔIRR', 0) >= 0.03  # 300bp
        factor2_ok = compression_metrics.roiic_wacc_core > 0
        
        go_decision = factor1_ok and factor2_ok
        
        # サイズはσで調整
        size_adjustment = self._calculate_size_adjustment(compression_metrics)
        
        # リスクレベル
        risk_level = self._assess_risk_level(compression_metrics)
        
        # 巻き戻しトリガー
        reversal_trigger = self._identify_reversal_triggers(compression_metrics)
        
        decision_result = DecisionResult(
            go_decision=go_decision,
            size_adjustment=size_adjustment,
            risk_level=risk_level,
            reversal_trigger=reversal_trigger
        )
        
        self.decision_history.append(decision_result)
        return decision_result
    
    def _estimate_source_strength(self, verbatim: str) -> T1Source:
        """出典の強度を推定"""
        # 簡易的な推定ロジック
        if "両社" in verbatim or "合意" in verbatim:
            return T1Source.BOTH_PARTIES
        elif "当社" in verbatim or "弊社" in verbatim:
            return T1Source.COMPANY
        else:
            return T1Source.CALL
    
    def _determine_t1_type(self, verbatim: str, timing: str) -> T1Type:
        """T1タイプを判定"""
        # 時間関連キーワードで判定
        time_keywords = ["来期", "四半期", "年度", "月次", "週次"]
        if any(keyword in timing for keyword in time_keywords):
            return T1Type.TIME
        else:
            return T1Type.CORE
    
    def _calculate_strength(self, verbatim: str, source: T1Source, t1_type: T1Type) -> float:
        """強度を計算"""
        base_strength = {
            T1Source.BOTH_PARTIES: 1.0,
            T1Source.COMPANY: 0.7,
            T1Source.CALL: 0.5
        }[source]
        
        type_multiplier = {
            T1Type.CORE: 1.0,
            T1Type.TIME: 0.8
        }[t1_type]
        
        return base_strength * type_multiplier
    
    def _find_similar_facts(self, new_fact: AtomicFact) -> List[AtomicFact]:
        """同趣旨のT1を検索"""
        similar = []
        for fact in self.atomic_facts:
            if (fact.impact_kpi == new_fact.impact_kpi and 
                fact.t1_type == new_fact.t1_type):
                similar.append(fact)
        return similar
    
    def _check_contradiction(self, fact1: AtomicFact, fact2: AtomicFact) -> bool:
        """矛盾チェック"""
        # 簡易的な矛盾検出
        contradiction_keywords = ["増加", "減少", "上昇", "下落", "改善", "悪化"]
        for keyword in contradiction_keywords:
            if keyword in fact1.verbatim and keyword in fact2.verbatim:
                return True
        return False
    
    def _calculate_trend(self, normalized_t1: NormalizedT1) -> float:
        """①右肩上がり計算"""
        # 簡易的なトレンド計算
        return normalized_t1.combined_strength * 0.8
    
    def _calculate_quality(self, normalized_t1: NormalizedT1) -> float:
        """②傾きの質計算（ROIC−WACC・ROIIC・FCF/NI）"""
        # 簡易的な品質計算
        return normalized_t1.combined_strength * 0.9
    
    def _calculate_time_factor(self, normalized_t1: NormalizedT1) -> float:
        """③時間計算"""
        # 簡易的な時間要因計算
        return normalized_t1.combined_strength * 0.7
    
    def _generate_time_annotation(self, normalized_t1: NormalizedT1) -> str:
        """④〔Time〕注釈生成（③の文中に一度だけ）"""
        if normalized_t1.latest_fact.t1_type == T1Type.TIME:
            return f"〔Time〕{normalized_t1.latest_fact.verbatim}"
        return ""
    
    def _calculate_horizon_metrics(self, matrix_mapping: MatrixMapping, horizon: str) -> Dict[str, float]:
        """Horizon指標計算"""
        # 簡易的なHorizon指標計算
        base_value = matrix_mapping.factor1_trend * matrix_mapping.factor2_quality
        
        return {
            'Δg': base_value * 0.1,  # 勾配差
            'Δt': base_value * 0.05,  # 前倒し/遅延
            'ΔIRR': base_value * 0.02  # IRR差
        }
    
    def _calculate_size_adjustment(self, compression_metrics: CompressionMetrics) -> float:
        """サイズ調整（σで調整）"""
        # 簡易的なサイズ調整計算
        return compression_metrics.roiic_wacc_core * 0.1
    
    def _assess_risk_level(self, compression_metrics: CompressionMetrics) -> str:
        """リスクレベル評価"""
        if compression_metrics.roiic_wacc_core > 0.8:
            return "HIGH"
        elif compression_metrics.roiic_wacc_core > 0.5:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _identify_reversal_triggers(self, compression_metrics: CompressionMetrics) -> List[str]:
        """巻き戻しトリガー特定"""
        triggers = []
        
        if compression_metrics.horizon_6m.get('ΔIRR', 0) < 0:
            triggers.append("6M ΔIRR逆行")
        
        if compression_metrics.horizon_1y.get('ΔIRR', 0) < 0:
            triggers.append("1Y ΔIRR逆行")
        
        if compression_metrics.roiic_wacc_core < 0:
            triggers.append("ROIIC-WACC逆行")
        
        return triggers
    
    def get_compression_summary(self) -> Dict:
        """圧縮サマリー取得"""
        return {
            'total_atomic_facts': len(self.atomic_facts),
            'normalized_t1s': len(self.normalized_t1s),
            'contradictions': len([t1 for t1 in self.normalized_t1s if t1.contradiction_flag]),
            'latest_decision': self.decision_history[-1] if self.decision_history else None,
            'compression_ratio': len(self.normalized_t1s) / len(self.atomic_facts) if self.atomic_facts else 0
        }

# 使用例
if __name__ == "__main__":
    engine = ComplexityPackingEngine()
    
    # 複雑さ圧縮実行
    result = engine.process_complexity_packing(
        verbatim="四半期売上高が前年同期比15%増加",
        impact_kpi="売上高",
        timing="来四半期"
    )
    
    print("複雑さ圧縮結果:", result)
    
    # 圧縮サマリー
    summary = engine.get_compression_summary()
    print("圧縮サマリー:", summary)
