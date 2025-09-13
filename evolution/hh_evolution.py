"""
Harmonic Homeostasis (HH) 昇格判定システム
AHFからHHへの進化条件を監視・判定
"""

import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class EvolutionStatus(Enum):
    """進化ステータス"""
    AHF = "AHF"  # Analytic Homeostasis
    HH = "HH"    # Harmonic Homeostasis

@dataclass
class EvolutionMetrics:
    """進化指標"""
    time_annotation_ratio: float  # ④〔Time〕注釈の出番比率
    irr_consistency: float        # ΔIRRの一貫性（符号安定度）
    counter_evidence_strength: float  # 反証強度
    last_updated: datetime.datetime

@dataclass
class HHEvolutionCriteria:
    """HH昇格判定条件"""
    max_time_annotation_ratio: float = 0.20  # ≤20%
    min_irr_consistency: float = 0.80        # 80%以上の符号安定度
    min_counter_evidence_strength: float = 0.70  # 70%以上の反証強度

class HHEvolutionEngine:
    """HH進化エンジン"""
    
    def __init__(self):
        self.current_status = EvolutionStatus.AHF
        self.evolution_metrics: List[EvolutionMetrics] = []
        self.criteria = HHEvolutionCriteria()
        self.quarterly_irr_history: List[Dict] = []
        self.counter_evidence_tests: List[Dict] = []
    
    def evaluate_evolution_readiness(self, 
                                   time_annotations_count: int,
                                   total_updates: int,
                                   current_irr_data: List[float]) -> Dict:
        """
        HH進化準備度評価
        
        Args:
            time_annotations_count: ④〔Time〕注釈の総数
            total_updates: 全更新回数
            current_irr_data: 現在のIRRデータ
            
        Returns:
            進化評価結果
        """
        # 1. 手当てが減る：④〔Time〕注釈の出番が全更新の≤20%に自然低下
        time_annotation_ratio = time_annotations_count / total_updates if total_updates > 0 else 1.0
        
        # 2. 一貫性が増す：ΔIRRが四半期を跨いでも符号が安定
        irr_consistency = self._calculate_irr_consistency(current_irr_data)
        
        # 3. 反証に強い：C列（④無効化／t1+0.5Q）でも結論が維持されるケースが増える
        counter_evidence_strength = self._calculate_counter_evidence_strength()
        
        # 進化指標を記録
        metrics = EvolutionMetrics(
            time_annotation_ratio=time_annotation_ratio,
            irr_consistency=irr_consistency,
            counter_evidence_strength=counter_evidence_strength,
            last_updated=datetime.datetime.now()
        )
        self.evolution_metrics.append(metrics)
        
        # HH昇格判定
        ready_for_hh = self._is_ready_for_hh(metrics)
        
        return {
            'current_status': self.current_status.value,
            'evolution_metrics': {
                'time_annotation_ratio': time_annotation_ratio,
                'irr_consistency': irr_consistency,
                'counter_evidence_strength': counter_evidence_strength
            },
            'hh_criteria': {
                'max_time_annotation_ratio': self.criteria.max_time_annotation_ratio,
                'min_irr_consistency': self.criteria.min_irr_consistency,
                'min_counter_evidence_strength': self.criteria.min_counter_evidence_strength
            },
            'ready_for_hh': ready_for_hh,
            'evolution_signs': self._get_evolution_signs(metrics),
            'evaluated_at': datetime.datetime.now()
        }
    
    def _calculate_irr_consistency(self, irr_data: List[float]) -> float:
        """ΔIRRの一貫性計算（四半期を跨いでも符号が安定）"""
        if len(irr_data) < 2:
            return 0.0
        
        # 四半期ごとのΔIRRを計算
        quarterly_deltas = []
        for i in range(0, len(irr_data) - 3, 3):  # 3ヶ月ごと
            if i + 3 < len(irr_data):
                delta = irr_data[i + 3] - irr_data[i]
                quarterly_deltas.append(delta)
        
        if len(quarterly_deltas) < 2:
            return 0.0
        
        # 符号の安定度を計算
        positive_count = sum(1 for delta in quarterly_deltas if delta > 0)
        negative_count = sum(1 for delta in quarterly_deltas if delta < 0)
        total_count = len(quarterly_deltas)
        
        # より多く出現する符号の比率
        consistency = max(positive_count, negative_count) / total_count
        
        # 記録
        self.quarterly_irr_history.append({
            'quarterly_deltas': quarterly_deltas,
            'consistency': consistency,
            'timestamp': datetime.datetime.now()
        })
        
        return consistency
    
    def _calculate_counter_evidence_strength(self) -> float:
        """反証強度計算（C列無効化でも結論が維持されるケース）"""
        if not self.counter_evidence_tests:
            return 0.0
        
        # 反証テストの成功率を計算
        successful_tests = sum(1 for test in self.counter_evidence_tests 
                             if test.get('conclusion_maintained', False))
        total_tests = len(self.counter_evidence_tests)
        
        return successful_tests / total_tests if total_tests > 0 else 0.0
    
    def _is_ready_for_hh(self, metrics: EvolutionMetrics) -> bool:
        """HH昇格準備完了判定"""
        return (metrics.time_annotation_ratio <= self.criteria.max_time_annotation_ratio and
                metrics.irr_consistency >= self.criteria.min_irr_consistency and
                metrics.counter_evidence_strength >= self.criteria.min_counter_evidence_strength)
    
    def _get_evolution_signs(self, metrics: EvolutionMetrics) -> Dict:
        """進化サイン取得"""
        return {
            '手当てが減る': {
                'current': metrics.time_annotation_ratio,
                'target': self.criteria.max_time_annotation_ratio,
                'achieved': metrics.time_annotation_ratio <= self.criteria.max_time_annotation_ratio,
                'description': '④〔Time〕注釈の出番が全更新の≤20%に自然低下'
            },
            '一貫性が増す': {
                'current': metrics.irr_consistency,
                'target': self.criteria.min_irr_consistency,
                'achieved': metrics.irr_consistency >= self.criteria.min_irr_consistency,
                'description': 'ΔIRRが四半期を跨いでも符号が安定（±のブレが小さい）'
            },
            '反証に強い': {
                'current': metrics.counter_evidence_strength,
                'target': self.criteria.min_counter_evidence_strength,
                'achieved': metrics.counter_evidence_strength >= self.criteria.min_counter_evidence_strength,
                'description': 'C列（④無効化／t1+0.5Q）でも結論が維持されるケースが増える'
            }
        }
    
    def promote_to_hh(self) -> bool:
        """HH昇格実行"""
        if self.current_status == EvolutionStatus.AHF:
            latest_metrics = self.evolution_metrics[-1] if self.evolution_metrics else None
            if latest_metrics and self._is_ready_for_hh(latest_metrics):
                self.current_status = EvolutionStatus.HH
                return True
        return False
    
    def add_counter_evidence_test(self, test_name: str, conclusion_maintained: bool) -> None:
        """反証テスト追加"""
        test = {
            'test_name': test_name,
            'conclusion_maintained': conclusion_maintained,
            'timestamp': datetime.datetime.now()
        }
        self.counter_evidence_tests.append(test)
    
    def get_evolution_progress(self) -> Dict:
        """進化進捗取得"""
        if not self.evolution_metrics:
            return {'message': '進化指標がありません'}
        
        latest = self.evolution_metrics[-1]
        progress = {
            'current_status': self.current_status.value,
            'latest_metrics': latest,
            'total_evaluations': len(self.evolution_metrics),
            'hh_readiness': self._is_ready_for_hh(latest),
            'evolution_trend': self._calculate_evolution_trend()
        }
        
        return progress
    
    def _calculate_evolution_trend(self) -> Dict:
        """進化トレンド計算"""
        if len(self.evolution_metrics) < 2:
            return {'trend': 'insufficient_data'}
        
        recent = self.evolution_metrics[-3:]  # 最近3回
        older = self.evolution_metrics[-6:-3] if len(self.evolution_metrics) >= 6 else []
        
        if not older:
            return {'trend': 'insufficient_data'}
        
        # 各指標の改善傾向を計算
        time_annotation_trend = (sum(m.time_annotation_ratio for m in older) / len(older) - 
                                sum(m.time_annotation_ratio for m in recent) / len(recent))
        
        irr_consistency_trend = (sum(m.irr_consistency for m in recent) / len(recent) - 
                                sum(m.irr_consistency for m in older) / len(older))
        
        counter_evidence_trend = (sum(m.counter_evidence_strength for m in recent) / len(recent) - 
                                 sum(m.counter_evidence_strength for m in older) / len(older))
        
        return {
            'time_annotation_improvement': time_annotation_trend,
            'irr_consistency_improvement': irr_consistency_trend,
            'counter_evidence_improvement': counter_evidence_trend,
            'overall_trend': 'improving' if (time_annotation_trend > 0 and 
                                           irr_consistency_trend > 0 and 
                                           counter_evidence_trend > 0) else 'stable'
        }

# 使用例
if __name__ == "__main__":
    evolution_engine = HHEvolutionEngine()
    
    # 進化準備度評価
    evaluation = evolution_engine.evaluate_evolution_readiness(
        time_annotations_count=5,
        total_updates=30,
        current_irr_data=[0.05, 0.06, 0.04, 0.07, 0.05, 0.08, 0.06, 0.09]
    )
    
    print("HH進化評価結果:", evaluation)
    
    # 進化進捗確認
    progress = evolution_engine.get_evolution_progress()
    print("進化進捗:", progress)
