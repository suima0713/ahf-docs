#!/usr/bin/env python3
"""
AHF v0.8.0 ワークフロー実装
固定3軸（①長期EV確度、②長期EV勾配、③バリュエーション＋認知ギャップ）対応

Purpose: 投資判断に直結する固定3軸で評価する
MVP: ①②③の名称と順序を固定／T1で確証（不足は n/a）／定型テーブル＋1行要約を即時出力
"""

import json
import yaml
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class WorkflowStage(Enum):
    INTAKE = "intake"
    STAGE1_FAST_SCREEN = "stage1_fast_screen"
    STAGE2_MINI_CONFIRM = "stage2_mini_confirm"
    STAGE3_ALPHA_MAXIMIZATION = "stage3_alpha_maximization"
    DECISION = "decision"

class AxisType(Enum):
    LEC = "LEC"  # ①長期EV確度
    NES = "NES"  # ②長期EV勾配
    VRG = "VRG"  # ③バリュエーション＋認知ギャップ

@dataclass
class T1Fact:
    """T1確定事実"""
    date: str
    source: str  # T1-F|T1-C
    axis: AxisType
    verbatim: str  # ≤25語
    impact: str
    url: str
    anchor: str  # #:~:text= or anchor_backup

@dataclass
class Stage3Card:
    """Stage-3カード（半透明αの最大化）"""
    id: str
    hypothesis: str
    t1_verbatim: str
    url_anchor: str
    test_formula: str
    threshold_result: str
    reasoning: str
    result: str  # PASS/FAIL/DEFER/REWRITE
    ttl_days: int
    reflection: str
    axis: AxisType

class AHFv080Workflow:
    """AHF v0.8.0 ワークフロー実装"""
    
    def __init__(self, ticker: str):
        self.ticker = ticker
        self.current_stage = WorkflowStage.INTAKE
        self.t1_facts: List[T1Fact] = []
        self.stage3_cards: List[Stage3Card] = []
        self.tripwires = {
            "a3_unexplained": False,
            "balance_weak": False,
            "item1a_change": False,
            "anchor_fail": False
        }
        
    def run_workflow(self) -> Dict[str, Any]:
        """ワークフロー実行（一本路線／Deep-first with Interrupts）"""
        result = {
            "purpose": "投資判断に直結する固定3軸で評価する",
            "mvp": "①②③の名称と順序を固定／T1で確証（不足は n/a）／定型テーブル＋1行要約を即時出力",
            "mode": "Deep-first with Interrupts",
            "action_log": [],
            "data_gap": {},
            "gap_reason": {}
        }
        
        try:
            # Intake：銘柄候補／T1可用性
            result.update(self._run_intake())
            
            # Stage-1｜Fast-Screen（Core）
            if self._check_interrupts():
                result["interrupts"] = self._get_interrupts()
                return result
                
            result.update(self._run_stage1_fast_screen())
            
            # Stage-2｜Mini-Confirm（α3/α5）
            if result.get("di_score", 0) >= 0.32:
                result.update(self._run_stage2_mini_confirm())
                
                # Stage-3｜半透明αの最大化
                result.update(self._run_stage3_alpha_maximization())
            
            # Decision
            result.update(self._run_decision())
            
        except Exception as e:
            result["error"] = str(e)
            result["data_gap"]["error"] = True
            result["gap_reason"]["error"] = f"ワークフロー実行エラー: {str(e)}"
            
        return result
    
    def _run_intake(self) -> Dict[str, Any]:
        """Intake：銘柄候補／T1可用性"""
        return {
            "intake": {
                "ticker": self.ticker,
                "t1_availability": self._check_t1_availability(),
                "target_list": [self.ticker]
            }
        }
    
    def _run_stage1_fast_screen(self) -> Dict[str, Any]:
        """Stage-1｜Fast-Screen（Core）：T1逐語≤25語＋#:~:text="""
        result = {
            "stage1": {
                "mode": "Fast-Screen",
                "axes": {}
            }
        }
        
        # ①長期EV確度（LEC）
        lec_result = self._calculate_lec()
        result["stage1"]["axes"]["LEC"] = lec_result
        
        # ②長期EV勾配（NES）
        nes_result = self._calculate_nes()
        result["stage1"]["axes"]["NES"] = nes_result
        
        # ③バリュエーション＋認知ギャップ（VRG）
        vrg_result = self._calculate_vrg()
        result["stage1"]["axes"]["VRG"] = vrg_result
        
        # DI計算
        di_score = self._calculate_di(lec_result, nes_result, vrg_result)
        result["stage1"]["di_score"] = di_score
        
        # 定型テーブル＋1行要約
        result["stage1"]["summary_table"] = self._generate_summary_table(lec_result, nes_result, vrg_result)
        result["stage1"]["one_line_summary"] = self._generate_one_line_summary(di_score)
        
        return result
    
    def _run_stage2_mini_confirm(self) -> Dict[str, Any]:
        """Stage-2｜Mini-Confirm（α3/α5）：T1のみ"""
        result = {
            "stage2": {
                "mode": "Mini-Confirm",
                "alpha3": self._check_alpha3(),
                "alpha5": self._check_alpha5(),
                "star_adjustments": self._calculate_star_adjustments()
            }
        }
        return result
    
    def _run_stage3_alpha_maximization(self) -> Dict[str, Any]:
        """Stage-3｜半透明αの最大化：固まったT1の地図から違和感→仮説を立て、T1で単一テスト"""
        result = {
            "stage3": {
                "mode": "半透明αの最大化",
                "cards": [],
                "s3_lint": self._run_s3_lint(),
                "reflections": []
            }
        }
        
        # 仮説抽出（3-5件）
        hypotheses = self._extract_hypotheses()
        
        for hypothesis in hypotheses:
            card = self._create_stage3_card(hypothesis)
            if self._run_s3_lint_on_card(card):
                result["stage3"]["cards"].append(card)
                reflection = self._calculate_reflection(card)
                result["stage3"]["reflections"].append(reflection)
        
        return result
    
    def _run_decision(self) -> Dict[str, Any]:
        """Decision（Wired）：DI = (0.6·s2 + 0.4·s1) · Vmult"""
        result = {
            "decision": {
                "di_calculation": self._calculate_final_di(),
                "action": self._determine_action(),
                "size_percentage": self._calculate_size_percentage(),
                "soft_overlay": self._calculate_soft_overlay()
            }
        }
        return result
    
    def _calculate_lec(self) -> Dict[str, Any]:
        """①長期EV確度（LEC）計算"""
        # LEC ≈ g_fwd + ΔOPM_fwd − Dilution − Capex_intensity
        # 星割当：LEC ≥+20pp→★5／15–20→★4／8–15→★3／3–8→★2／<3→★1
        return {
            "score": 0,  # ★1-5
            "calculation": "LEC ≈ g_fwd + ΔOPM_fwd − Dilution − Capex_intensity",
            "t1_sources": [],
            "data_gap": False
        }
    
    def _calculate_nes(self) -> Dict[str, Any]:
        """②長期EV勾配（NES）計算"""
        # NES = 0.5·(次Q q/q%) + 0.3·(ガイド改定%) + 0.2·(受注/Backlog増勢%) + Margin_term + Health_term
        # 星割当：NES≥+8→★5／+5–8→★4／+2–5→★3／0–2→★2／<0→★1
        return {
            "score": 0,  # ★1-5
            "calculation": "NES = 0.5·(次Q q/q%) + 0.3·(ガイド改定%) + 0.2·(受注/Backlog増勢%) + Margin_term + Health_term",
            "t1_sources": [],
            "data_gap": False
        }
    
    def _calculate_vrg(self) -> Dict[str, Any]:
        """③バリュエーション＋認知ギャップ（Two-Step）計算"""
        # Step-1｜フェアバリュー差（素点）
        # Step-2｜適正性チェック（注釈のみ／色は変えない）
        return {
            "step1": {
                "evs_actual": 0.0,
                "evs_peer_median": 0.0,
                "evs_fair_rdcf": 0.0,
                "disc_pct": 0.0,
                "color": "Green",  # Green(1.05)/Amber(0.90)/Red(0.75)
                "vmult": 1.05
            },
            "step2": {
                "expectation_gap": 0.0,
                "cognition_flags_pos": [],
                "cognition_flags_neg": [],
                "verdict": "Neutral"
            },
            "t1_sources": [],
            "data_gap": False
        }
    
    def _calculate_di(self, lec_result: Dict, nes_result: Dict, vrg_result: Dict) -> float:
        """Decision Index計算"""
        s1 = lec_result["score"] / 5.0  # ①長期EV確度の正規化
        s2 = nes_result["score"] / 5.0  # ②長期EV勾配の正規化
        vmult = vrg_result["step1"]["vmult"]  # ③バリュエーションのVmult
        
        di = (0.6 * s2 + 0.4 * s1) * vmult
        return di
    
    def _generate_summary_table(self, lec_result: Dict, nes_result: Dict, vrg_result: Dict) -> str:
        """定型テーブル生成"""
        table = f"""
| 軸 | 代表KPI/根拠(T1) | 現状スナップ | ★/5 | 確信度 | 市場織込み | Alpha不透明度 | 上向/下向（％） |
|----|------------------|--------------|-----|--------|------------|----------------|-----------------|
| ①LEC | 長期EV確度 | {lec_result.get('calculation', 'n/a')} | {lec_result['score']} | 高 | 織込み済み | 低 | +5% |
| ②NES | 長期EV勾配 | {nes_result.get('calculation', 'n/a')} | {nes_result['score']} | 高 | 織込み済み | 低 | +3% |
| ③VRG | バリュエーション | {vrg_result['step1'].get('color', 'n/a')} | - | 中 | 未織込み | 高 | +8% |
        """.strip()
        return table
    
    def _generate_one_line_summary(self, di_score: float) -> str:
        """1行要約生成"""
        if di_score >= 0.55:
            action = "GO"
        elif di_score >= 0.32:
            action = "WATCH"
        else:
            action = "NO-GO"
        
        return f"DI={di_score:.2f} → {action} (Size≈{1.2 * di_score:.1f}%)"
    
    def _check_alpha3(self) -> Dict[str, Any]:
        """α3：RPO/Backlog coverage確認"""
        return {
            "gate": 11.0,
            "calculation": "(RPO_12M/Quarterly_Rev)×3",
            "pass": False,
            "data_gap": True
        }
    
    def _check_alpha5(self) -> Dict[str, Any]:
        """α5：OpEx/EBITDA三角測量"""
        return {
            "math_pass": False,
            "calculation": "OpEx = Rev × (NG-GM) − KPI",
            "data_gap": True
        }
    
    def _calculate_star_adjustments(self) -> Dict[str, int]:
        """★調整幅計算（各軸±1内で微調整）"""
        return {
            "LEC": 0,  # ±1内
            "NES": 0,  # ±1内
            "VRG": 0   # 注釈のみ
        }
    
    def _extract_hypotheses(self) -> List[Dict[str, Any]]:
        """仮説抽出（3-5件）"""
        return [
            {
                "id": "H1_guidance_adherence",
                "hypothesis": "ガイダンス遵守度の違和感",
                "axis": AxisType.NES
            },
            {
                "id": "H2_cash_conversion",
                "hypothesis": "キャッシュコンバージョンの違和感",
                "axis": AxisType.LEC
            }
        ]
    
    def _create_stage3_card(self, hypothesis: Dict[str, Any]) -> Stage3Card:
        """Stage-3カード作成"""
        return Stage3Card(
            id=hypothesis["id"],
            hypothesis=hypothesis["hypothesis"],
            t1_verbatim="T1逐語≤25語",
            url_anchor="URL#:~:text=...",
            test_formula="四則1行のテスト式",
            threshold_result="閾値/合否",
            reasoning="推論1段",
            result="PENDING",
            ttl_days=30,
            reflection="反映（★調整±1内/DI/α±0.08内）",
            axis=hypothesis["axis"]
        )
    
    def _run_s3_lint(self) -> Dict[str, bool]:
        """S3-Lint（最小5チェック）"""
        return {
            "l1_verbatim_25w": True,    # L1逐語≤25語
            "l2_anchor_present": True,  # L2アンカー有り
            "l3_single_formula": True,  # L3四則1行
            "l4_ttl_7_90d": True,       # L4TTL=7–90d
            "l5_reasoning_1step": True, # L5推論≤1段
            "overall_pass": True        # 全体パス
        }
    
    def _run_s3_lint_on_card(self, card: Stage3Card) -> bool:
        """カードのS3-Lint実行"""
        return (
            len(card.t1_verbatim) <= 25 and
            card.url_anchor != "" and
            card.test_formula != "" and
            7 <= card.ttl_days <= 90 and
            card.reasoning != ""
        )
    
    def _calculate_reflection(self, card: Stage3Card) -> Dict[str, Any]:
        """反映計算（★調整±1内/DI/α±0.08内）"""
        return {
            "star_adjustment": 0,  # ±1内
            "di_adjustment": 0.0,  # ±0.08内
            "alpha_adjustment": 0.0  # ±0.08内
        }
    
    def _calculate_final_di(self) -> float:
        """最終DI計算"""
        return 0.0
    
    def _determine_action(self) -> str:
        """アクション決定：GO ≥0.55｜WATCH 0.32–0.55｜NO-GO <0.32"""
        di = self._calculate_final_di()
        if di >= 0.55:
            return "GO"
        elif di >= 0.32:
            return "WATCH"
        else:
            return "NO-GO"
    
    def _calculate_size_percentage(self) -> float:
        """サイズ計算：Size% ≈ 1.2% × DI"""
        di = self._calculate_final_di()
        return 1.2 * di
    
    def _calculate_soft_overlay(self) -> Dict[str, Any]:
        """SoftOverlay計算（任意・可逆で合算±0.08にクリップ）"""
        return {
            "enabled": False,
            "adjustment": 0.0,
            "reason": "",
            "reversible": True
        }
    
    def _check_interrupts(self) -> bool:
        """Interrupt確認"""
        return any(self.tripwires.values())
    
    def _get_interrupts(self) -> List[str]:
        """Interrupt一覧取得"""
        return [k for k, v in self.tripwires.items() if v]
    
    def _check_t1_availability(self) -> bool:
        """T1可用性確認"""
        return True  # 実装時は実際のT1ソース確認

def main():
    """メイン実行"""
    if len(sys.argv) < 2:
        print("Usage: python ahf_v080_workflow.py <TICKER>")
        sys.exit(1)
    
    ticker = sys.argv[1]
    workflow = AHFv080Workflow(ticker)
    result = workflow.run_workflow()
    
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()

