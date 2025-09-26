#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
S3-Step3-Essence - ③二段構え（最小・実戦用）
Step-1｜フェアバリュー差（素点）
Step-2｜妥当性チェック（期待の正当性）
「高PERは何を要請しているか？」を一撃で見る式（逆DCFライト）
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

class S3Step3Essence:
    """③二段構え（最小・実戦用）の本質実装"""
    
    def __init__(self):
        # Vmult（変更不可）
        self.vmult = {
            "Green": 1.05,
            "Amber": 0.90,
            "Red": 0.75
        }
        
        # 認知フラグ（＋）
        self.positive_flags = [
            "ガイダンス上方", "実出荷", "前受", "契約負債↑", "ATM未実行",
            "raises guidance", "began", "volume shipments", "contract liabilities↑", 
            "ATM sales to date=0", "10%顧客分散"
        ]
        
        # 認知フラグ（−）
        self.negative_flags = [
            "acceptance要件", "在庫滞留", "集中悪化", "希薄化",
            "acceptance required", "Raw/WIP滞留", "ATM実行", "集中度悪化"
        ]
        
        # 証拠基準（T1だけ）
        self.evidence_criteria = {
            "継続性": ["NRR/GRR", "RPO/契約負債の伸び＞売上伸び", "リテンション/コホート曲線"],
            "単位経済": ["LTV/CAC>3", "粗利↑＆販管費率↓でOPM+50bps×連続"],
            "集中/希薄化": ["10%超顧客分散", "ATM未実行/希薄化<2%/年"],
            "規制/為替/在庫": ["acceptanceなし", "在庫回転/DSO改善"]
        }
    
    def calculate_peer_multiple(self, pe_actual: float, pe_peer_median: float) -> float:
        """ピアEV/S（またはPE）中央値と比較（Peer Multiple）"""
        if pe_peer_median == 0:
            return 0.0
        return (pe_actual / pe_peer_median) - 1
    
    def calculate_fair_ev_s_rdcf(self, g_fwd: float, opm_fwd: float) -> float:
        """逆DCFライトで"フェア"を置く（T1の g_fwd・OPM_fwd だけ）"""
        if g_fwd >= 25 and opm_fwd >= 0:
            return 10.0  # g_fwd≥25% かつ OPM_fwd≥0%
        elif (g_fwd >= 10 and g_fwd < 25) or (opm_fwd >= -5 and opm_fwd < 0):
            return 8.0   # いずれか中間（10–25% or −5〜0%）
        else:
            return 6.0   # g_fwd<10% or OPM_fwd≤−5%
    
    def calculate_discount_rate(self, pe_peer_median: float, pe_rdcf: float, pe_actual: float) -> float:
        """上の大きい方を基準値にして**割引率 Disc%**を出す"""
        # 基準値 = max(ピア中央値, rDCF)
        pe_base = max(pe_peer_median, pe_rdcf)
        
        if pe_base == 0:
            return 0.0
        
        return (pe_base - pe_actual) / pe_base
    
    def determine_color_step1(self, disc_pct: float) -> str:
        """Disc%で色/Vmultを機械決定（Green/Amber/Red）"""
        abs_disc = abs(disc_pct)
        
        if abs_disc <= 0.10:
            return "Green"    # |Disc%| ≤ 10%
        elif abs_disc <= 0.25:
            return "Amber"    # 10% < |Disc%| ≤ 25%
        else:
            return "Red"      # |Disc%| > 25%
    
    def calculate_growth_delta(self, g_fwd: float, g_peer_median: float) -> float:
        """期待成長の相対差：Δg = g_fwd − g_peer_median"""
        return g_fwd - g_peer_median
    
    def count_cognitive_flags(self, evidence: str) -> Tuple[int, int]:
        """認知フラグ（＋：ガイダンス上方・実出荷・前受/契約負債↑・ATM未実行／−：acceptance要件・在庫滞留・集中悪化・希薄化）"""
        evidence_lower = evidence.lower()
        
        positive_count = sum(1 for flag in self.positive_flags if flag in evidence_lower)
        negative_count = sum(1 for flag in self.negative_flags if flag in evidence_lower)
        
        return positive_count, negative_count
    
    def determine_verdict_step2(self, disc_pct: float, delta_g: float, 
                              positive_flags: int, negative_flags: int) -> str:
        """判定：Under/Over （適正 or 不適正）のラベルだけ付ける。色は変えない。"""
        if disc_pct > 0.10:  # 割安
            if delta_g >= 10 or positive_flags >= 2:
                return "Underpriced / 不適正（割安すぎ）"
            elif abs(delta_g) < 10 and abs(positive_flags - negative_flags) <= 1:
                return "Underpriced / ほぼ適正"
            else:
                return "Underpriced / ほぼ適正"
        
        elif disc_pct < -0.10:  # 割高
            if delta_g <= -10 or negative_flags >= 2:
                return "Overpriced / 不適正（割高すぎ）"
            elif abs(delta_g) < 10 and abs(positive_flags - negative_flags) <= 1:
                return "Overpriced / ほぼ適正"
            else:
                return "Overpriced / ほぼ適正"
        
        else:  # 中立
            return "中立"
    
    def calculate_eps_cagr_required(self, pe_now: float, pe_target: float = 25, hurdle: float = 0.12) -> float:
        """「高PERは何を要請しているか？」を一撃で見る式（逆DCFライト）
        
        5年で"市場並みPER"に収斂すると仮定した時に必要なEPS成長：
        EPS_CAGR_req = ((PE_now / PE_target) · (1 + hurdle)^5)^(1/5) − 1
        """
        # 係数 = (PE_now / PE_target) × (1 + hurdle)^5
        coefficient = (pe_now / pe_target) * ((1 + hurdle) ** 5)
        
        # EPS_CAGR_req = 係数^(1/5) - 1
        eps_cagr_req = (coefficient ** (1/5)) - 1
        
        return eps_cagr_req
    
    def evaluate_evidence_criteria(self, evidence: str) -> Dict:
        """何を"証拠"にするか（T1だけ）の評価"""
        evidence_lower = evidence.lower()
        
        results = {}
        for category, criteria in self.evidence_criteria.items():
            count = 0
            for criterion in criteria:
                if criterion.lower() in evidence_lower:
                    count += 1
            results[category] = count
        
        # 総合評価
        total_evidence = sum(results.values())
        if total_evidence >= 3:
            evidence_verdict = "先取り期待は妥当＝高PERでも買える"
        elif total_evidence >= 1:
            evidence_verdict = "部分的証拠＝要監視"
        else:
            evidence_verdict = "期待倒れ＝売り/回避"
        
        return {
            "results": results,
            "total_evidence": total_evidence,
            "verdict": evidence_verdict
        }
    
    def evaluate_step1_essence(self, pe_actual: float, pe_peer_median: float, 
                              g_fwd: float, opm_fwd: float) -> Dict:
        """Step-1｜フェアバリュー差（素点）の狙い：市場が"今"つけているプレミアムがどれだけ大きいか/小さいか"""
        # ピアEV/S（またはPE）中央値と比較
        peer_multiple = self.calculate_peer_multiple(pe_actual, pe_peer_median)
        
        # 逆DCFライトで"フェア"を置く
        pe_rdcf = self.calculate_fair_ev_s_rdcf(g_fwd, opm_fwd)
        
        # 上の大きい方を基準値にして**割引率 Disc%**を出す
        disc_pct = self.calculate_discount_rate(pe_peer_median, pe_rdcf, pe_actual)
        
        # 色判定
        color = self.determine_color_step1(disc_pct)
        vmult = self.vmult.get(color, 0.90)
        
        return {
            "pe_actual": pe_actual,
            "pe_peer_median": pe_peer_median,
            "pe_rdcf": pe_rdcf,
            "peer_multiple": peer_multiple,
            "disc_pct": disc_pct,
            "color": color,
            "vmult": vmult
        }
    
    def evaluate_step2_essence(self, step1_result: Dict, g_fwd: float, g_peer_median: float, 
                              evidence: str) -> Dict:
        """Step-2｜妥当性チェック（期待の正当性）の狙い：その割安/割高が**将来の実力（認知ギャップ/耐性）**で正当化できるか"""
        # 期待成長の相対差
        delta_g = self.calculate_growth_delta(g_fwd, g_peer_median)
        
        # 認知フラグ
        positive_flags, negative_flags = self.count_cognitive_flags(evidence)
        
        # 判定
        verdict = self.determine_verdict_step2(
            step1_result["disc_pct"], delta_g, positive_flags, negative_flags
        )
        
        # 証拠基準評価
        evidence_eval = self.evaluate_evidence_criteria(evidence)
        
        return {
            "delta_g": delta_g,
            "positive_flags": positive_flags,
            "negative_flags": negative_flags,
            "verdict": verdict,
            "evidence_evaluation": evidence_eval
        }
    
    def get_high_per_analysis(self, pe_now: float, pe_target: float = 25, hurdle: float = 0.12) -> str:
        """高PER分析の表示"""
        eps_cagr_req = self.calculate_eps_cagr_required(pe_now, pe_target, hurdle)
        
        return f"""
高PER分析（逆DCFライト）:
PE_now = {pe_now:.1f}×, PE_target = {pe_target:.1f}×, hurdle = {hurdle:.1%}

係数 = (PE_now / PE_target) × (1 + hurdle)^5 = ({pe_now:.1f}/{pe_target:.1f}) × {1+hurdle:.3f}^5 = {pe_now/pe_target:.2f} × {(1+hurdle)**5:.2f} = {(pe_now/pe_target)*((1+hurdle)**5):.2f}

EPS_CAGR_req = 係数^(1/5) - 1 = {(pe_now/pe_target)*((1+hurdle)**5):.2f}^(1/5) - 1 = {eps_cagr_req:.1%}

⇒ 5年でEPS年率{eps_cagr_req:.1%}を持続できる"証拠"がT1にどれだけあるか、が勝負
"""
    
    def get_step3_essence_display(self, pe_actual: float, pe_peer_median: float, 
                                 g_fwd: float, opm_fwd: float, g_peer_median: float, 
                                 evidence: str) -> str:
        """③二段構え（最小・実戦用）の表示"""
        # Step-1
        step1_result = self.evaluate_step1_essence(pe_actual, pe_peer_median, g_fwd, opm_fwd)
        
        # Step-2
        step2_result = self.evaluate_step2_essence(step1_result, g_fwd, g_peer_median, evidence)
        
        # 高PER分析
        high_per_analysis = self.get_high_per_analysis(pe_actual)
        
        return f"""
③二段構え（最小・実戦用）:

[Step-1] フェアバリュー差（素点）:
PE_actual = {step1_result['pe_actual']:.1f}×
PE_peer_median = {step1_result['pe_peer_median']:.1f}×, PE_rDCF = {step1_result['pe_rdcf']:.1f}×
Peer Multiple = {step1_result['peer_multiple']:.1%}
Disc% = {step1_result['disc_pct']:.1%}
色 = {step1_result['color']}（Vmult={step1_result['vmult']:.2f}）

[Step-2] 妥当性チェック（期待の正当性）:
期待成長Δg = {step2_result['delta_g']:.1f}pp
認知フラグ [+{step2_result['positive_flags']} / −{step2_result['negative_flags']}]
Verdict = {step2_result['verdict']}

証拠基準評価:
{step2_result['evidence_evaluation']['verdict']}
継続性: {step2_result['evidence_evaluation']['results']['継続性']}/3
単位経済: {step2_result['evidence_evaluation']['results']['単位経済']}/2
集中/希薄化: {step2_result['evidence_evaluation']['results']['集中/希薄化']}/2
規制/為替/在庫: {step2_result['evidence_evaluation']['results']['規制/為替/在庫']}/2

{high_per_analysis}
"""

def main():
    """テスト実行"""
    s3 = S3Step3Essence()
    
    # ③二段構え（最小・実戦用）のテスト
    print("=== ③二段構え（最小・実戦用）のテスト ===")
    essence_display = s3.get_step3_essence_display(
        pe_actual=60.0,  # 高PER例
        pe_peer_median=25.0,
        g_fwd=30.0,
        opm_fwd=15.0,
        g_peer_median=20.0,
        evidence="ガイダンス上方, 実出荷, 前受, 契約負債↑, NRR/GRR, LTV/CAC>3, 10%超顧客分散 #:~:text=ガイダンス上方"
    )
    print(essence_display)
    
    # 高PER分析のテスト
    print("=== 高PER分析のテスト ===")
    high_per_analysis = s3.get_high_per_analysis(100.0)  # 超高PER例
    print(high_per_analysis)

if __name__ == "__main__":
    main()
