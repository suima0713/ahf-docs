"""
ハイリスクを枠内で取るための3原則
Primacy / Parsimony / Reversibility
"""

import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class Principle(Enum):
    """3原則"""
    PRIMACY = "Primacy"      # ①＞②＞③＞④
    PARSIMONY = "Parsimony"  # 出力は常に1ページ
    REVERSIBILITY = "Reversibility"  # 価格ではなくT1とKPIで即巻き戻し

@dataclass
class PrimacyRule:
    """Primacy原則：①＞②＞③＞④"""
    factor1_priority: float = 1.0
    factor2_priority: float = 0.8
    factor3_priority: float = 0.6
    factor4_priority: float = 0.4  # 時間の注釈に限る
    
    def get_weighted_score(self, factors: Dict[str, float]) -> float:
        """重み付きスコア計算"""
        return (factors.get('factor1', 0) * self.factor1_priority +
                factors.get('factor2', 0) * self.factor2_priority +
                factors.get('factor3', 0) * self.factor3_priority +
                factors.get('factor4', 0) * self.factor4_priority)

@dataclass
class ParsimonyRule:
    """Parsimony原則：出力は常に1ページ"""
    max_output_lines: int = 50
    required_elements: List[str] = None
    
    def __post_init__(self):
        if self.required_elements is None:
            self.required_elements = [
                "差分1行",
                "Horizon",
                "KPI×2"
            ]
    
    def validate_output(self, output: Dict) -> Tuple[bool, List[str]]:
        """出力検証"""
        errors = []
        
        # 必須要素チェック
        for element in self.required_elements:
            if element not in output:
                errors.append(f"必須要素 '{element}' が不足")
        
        # 行数チェック
        if len(str(output)) > self.max_output_lines * 80:  # 概算
            errors.append(f"出力が長すぎます（{self.max_output_lines}行以内）")
        
        return len(errors) == 0, errors

@dataclass
class ReversibilityRule:
    """Reversibility原則：価格ではなくT1とKPIで即巻き戻し"""
    reversal_triggers: List[str] = None
    kpi_thresholds: Dict[str, float] = None
    
    def __post_init__(self):
        if self.reversal_triggers is None:
            self.reversal_triggers = [
                "イベント未達",
                "遅延",
                "KPI逆行"
            ]
        
        if self.kpi_thresholds is None:
            self.kpi_thresholds = {
                "売上成長率": 0.05,  # 5%未満で巻き戻し
                "営業利益率": 0.10,  # 10%未満で巻き戻し
                "FCF": 0.0,         # マイナスで巻き戻し
                "在庫回転率": 0.5    # 0.5未満で巻き戻し
            }
    
    def check_reversal_conditions(self, current_kpis: Dict[str, float]) -> List[str]:
        """巻き戻し条件チェック"""
        triggered_conditions = []
        
        for kpi_name, threshold in self.kpi_thresholds.items():
            if kpi_name in current_kpis:
                if current_kpis[kpi_name] < threshold:
                    triggered_conditions.append(f"{kpi_name} < {threshold}")
        
        return triggered_conditions

class HighRiskPrinciplesEngine:
    """ハイリスク原則エンジン"""
    
    def __init__(self):
        self.primacy_rule = PrimacyRule()
        self.parsimony_rule = ParsimonyRule()
        self.reversibility_rule = ReversibilityRule()
        self.risk_taking_history: List[Dict] = []
    
    def apply_high_risk_principles(self, 
                                 factors: Dict[str, float],
                                 output: Dict,
                                 current_kpis: Dict[str, float]) -> Dict:
        """
        ハイリスク原則を適用
        
        Args:
            factors: ①②③④要因
            output: 出力内容
            current_kpis: 現在のKPI値
            
        Returns:
            原則適用結果
        """
        # 1. Primacy原則適用
        primacy_result = self._apply_primacy(factors)
        
        # 2. Parsimony原則適用
        parsimony_result = self._apply_parsimony(output)
        
        # 3. Reversibility原則適用
        reversibility_result = self._apply_reversibility(current_kpis)
        
        # 総合判定
        overall_decision = self._make_overall_decision(
            primacy_result, parsimony_result, reversibility_result
        )
        
        result = {
            'primacy': primacy_result,
            'parsimony': parsimony_result,
            'reversibility': reversibility_result,
            'overall_decision': overall_decision,
            'risk_level': self._assess_risk_level(overall_decision),
            'timestamp': datetime.datetime.now()
        }
        
        self.risk_taking_history.append(result)
        return result
    
    def _apply_primacy(self, factors: Dict[str, float]) -> Dict:
        """Primacy原則適用：①＞②＞③＞④"""
        weighted_score = self.primacy_rule.get_weighted_score(factors)
        
        # ④は時間の注釈に限る
        factor4_limited = factors.get('factor4', 0) <= 0.4
        
        return {
            'weighted_score': weighted_score,
            'factor4_limited': factor4_limited,
            'primacy_compliant': weighted_score > 0.7 and factor4_limited,
            'priority_order': ['factor1', 'factor2', 'factor3', 'factor4']
        }
    
    def _apply_parsimony(self, output: Dict) -> Dict:
        """Parsimony原則適用：出力は常に1ページ"""
        is_valid, errors = self.parsimony_rule.validate_output(output)
        
        # 複雑さは裏で圧縮
        complexity_compressed = self._check_complexity_compression(output)
        
        return {
            'is_valid': is_valid,
            'errors': errors,
            'complexity_compressed': complexity_compressed,
            'parsimony_compliant': is_valid and complexity_compressed
        }
    
    def _apply_reversibility(self, current_kpis: Dict[str, float]) -> Dict:
        """Reversibility原則適用：価格ではなくT1とKPIで即巻き戻し"""
        reversal_conditions = self.reversibility_rule.check_reversal_conditions(current_kpis)
        
        # 価格依存度チェック
        price_dependency = self._check_price_dependency(current_kpis)
        
        return {
            'reversal_conditions': reversal_conditions,
            'price_dependency': price_dependency,
            'reversibility_compliant': len(reversal_conditions) == 0 and price_dependency < 0.3
        }
    
    def _make_overall_decision(self, primacy_result: Dict, 
                             parsimony_result: Dict, 
                             reversibility_result: Dict) -> Dict:
        """総合判定"""
        all_compliant = (primacy_result['primacy_compliant'] and 
                        parsimony_result['parsimony_compliant'] and 
                        reversibility_result['reversibility_compliant'])
        
        if all_compliant:
            decision = "GO"
            risk_taking_level = "HIGH"
        elif (primacy_result['primacy_compliant'] and 
              parsimony_result['parsimony_compliant']):
            decision = "CAUTIOUS_GO"
            risk_taking_level = "MEDIUM"
        else:
            decision = "HOLD"
            risk_taking_level = "LOW"
        
        return {
            'decision': decision,
            'risk_taking_level': risk_taking_level,
            'all_principles_compliant': all_compliant
        }
    
    def _assess_risk_level(self, overall_decision: Dict) -> str:
        """リスクレベル評価"""
        return overall_decision['risk_taking_level']
    
    def _check_complexity_compression(self, output: Dict) -> bool:
        """複雑さ圧縮チェック"""
        # 簡易的な複雑さ圧縮チェック
        output_str = str(output)
        
        # 複雑さ指標
        complexity_indicators = ['nested', 'complex', 'detailed', 'verbose']
        compression_indicators = ['compressed', 'simplified', 'condensed', 'summary']
        
        complexity_count = sum(1 for indicator in complexity_indicators 
                             if indicator in output_str.lower())
        compression_count = sum(1 for indicator in compression_indicators 
                              if indicator in output_str.lower())
        
        return compression_count > complexity_count
    
    def _check_price_dependency(self, current_kpis: Dict[str, float]) -> float:
        """価格依存度チェック"""
        # 価格関連KPIの依存度を計算
        price_related_kpis = ['株価', '時価総額', 'PER', 'PBR']
        price_dependency = 0.0
        
        for kpi_name in price_related_kpis:
            if kpi_name in current_kpis:
                price_dependency += 0.25  # 各価格関連KPIで25%ずつ
        
        return min(price_dependency, 1.0)
    
    def get_risk_taking_summary(self) -> Dict:
        """リスクテイキングサマリー取得"""
        if not self.risk_taking_history:
            return {'message': 'リスクテイキング履歴がありません'}
        
        total_decisions = len(self.risk_taking_history)
        go_decisions = len([h for h in self.risk_taking_history 
                          if h['overall_decision']['decision'] == 'GO'])
        cautious_go = len([h for h in self.risk_taking_history 
                          if h['overall_decision']['decision'] == 'CAUTIOUS_GO'])
        hold_decisions = len([h for h in self.risk_taking_history 
                            if h['overall_decision']['decision'] == 'HOLD'])
        
        return {
            'total_decisions': total_decisions,
            'go_decisions': go_decisions,
            'cautious_go_decisions': cautious_go,
            'hold_decisions': hold_decisions,
            'risk_taking_ratio': go_decisions / total_decisions if total_decisions > 0 else 0,
            'latest_decision': self.risk_taking_history[-1] if self.risk_taking_history else None
        }
    
    def enforce_time_annotation_limit(self, time_annotations: List[str]) -> List[str]:
        """④〔Time〕注釈の制限を強制"""
        # ④は時間の注釈に限る（外付け係数は使わない）
        limited_annotations = []
        
        for annotation in time_annotations:
            if annotation.startswith('〔Time〕'):
                limited_annotations.append(annotation)
        
        # 最新の1つだけ残す
        return limited_annotations[-1:] if limited_annotations else []
    
    def create_one_page_output(self, 
                             diff_line: str,
                             horizon: Dict,
                             kpi_x2: Dict) -> Dict:
        """1ページ出力作成（差分1行＋Horizon＋KPI×2）"""
        output = {
            '差分1行': diff_line,
            'Horizon': horizon,
            'KPI×2': kpi_x2,
            'timestamp': datetime.datetime.now(),
            'output_type': 'one_page'
        }
        
        # Parsimony原則で検証
        is_valid, errors = self.parsimony_rule.validate_output(output)
        
        if not is_valid:
            output['validation_errors'] = errors
        
        return output

# 使用例
if __name__ == "__main__":
    engine = HighRiskPrinciplesEngine()
    
    # ハイリスク原則適用
    factors = {
        'factor1': 0.9,  # ①右肩上がり
        'factor2': 0.8,  # ②傾きの質
        'factor3': 0.7,  # ③時間
        'factor4': 0.3   # ④時間注釈（制限内）
    }
    
    output = {
        '差分1行': '四半期売上高15%増',
        'Horizon': {'6M': 'はい', '1Y': '△', '3Y': 'いいえ'},
        'KPI×2': {'売上成長率': 0.15, '営業利益率': 0.12}
    }
    
    current_kpis = {
        '売上成長率': 0.15,
        '営業利益率': 0.12,
        'FCF': 1000000,
        '在庫回転率': 0.8
    }
    
    result = engine.apply_high_risk_principles(factors, output, current_kpis)
    print("ハイリスク原則適用結果:", result)
    
    # リスクテイキングサマリー
    summary = engine.get_risk_taking_summary()
    print("リスクテイキングサマリー:", summary)
