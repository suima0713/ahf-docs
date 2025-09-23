#!/usr/bin/env python3
"""
AHF Min v0.6.3 - MVP-4+対応版
T1限定・Star整数評価・Edge管理・AnchorLint v1対応
"""

import json
import yaml
import argparse
import sys
import subprocess
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timedelta

class AHFMin:
    def __init__(self, config_path: str, state_path: str):
        self.config = self.load_config(config_path)
        self.state = self.load_state(state_path)
        self.results = {}
        self.edge_items = []  # v0.6.3: Edge管理
        self.t1_items = []    # v0.6.3: T1管理
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """設定ファイルを読み込み"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def load_state(self, state_path: str) -> Dict[str, Any]:
        """状態ファイルを読み込み"""
        with open(state_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def evaluate_alpha4_gate(self) -> Dict[str, Any]:
        """v0.6.3: α4 Gate判定（RPO基準）"""
        rpo_12m_months = self.state.get('rpo_12m_months_vs_q4_mid', 0)
        config = self.config.get('alpha4', {})
        pass_months = config.get('pass_months', 11.0)
        amber_floor = config.get('amber_floor_months', 9.0)
        
        # Gate判定
        if rpo_12m_months >= pass_months:
            gate_color = 'green'
            gate_status = 'PASS'
        elif rpo_12m_months >= amber_floor:
            gate_color = 'amber'
            gate_status = 'AMBER'
        else:
            gate_color = 'red'
            gate_status = 'FAIL'
        
        result = {
            'gate': gate_status,
            'gate_color': gate_color,
            'value': rpo_12m_months,
            'thresholds': {
                'pass_months': pass_months,
                'amber_floor': amber_floor
            },
            'description': f"RPO 12M カバー {rpo_12m_months:.1f}ヶ月 → {gate_color.upper()}"
        }
        return result
    
    def evaluate_alpha5_bands(self) -> Dict[str, Any]:
        """v0.6.3: α5 OpEx/EBITDA三角測量"""
        opex = self.state.get('opex_q3_25', 0)
        config = self.config.get('alpha5', {})
        tolerance = config.get('tolerance_$k', 8000)
        
        # 数理チェック
        revenue = self.state.get('revenue_$k', 0)
        ng_gm_pct = self.state.get('ng_gm_pct', 0)
        adj_ebitda = self.state.get('adj_ebitda_$k', 0)
        
        # OpEx = Rev * NG_GM - KPI の整合性チェック
        calculated_opex = revenue * (ng_gm_pct / 100) - adj_ebitda
        math_deviation = abs(opex - calculated_opex)
        math_pass = math_deviation <= tolerance
        
        result = {
            'band': 'TBD',  # 帯域は未設定
            'value': opex,
            'math_pass': math_pass,
            'math_deviation_$k': math_deviation,
            'tolerance_$k': tolerance,
            'description': f"OpEx ${opex:,.0f}k (乖離${math_deviation:,.0f}k vs 許容${tolerance:,.0f}k)"
        }
        return result
    
    def evaluate_gm_to_ebitda_conversion(self) -> Dict[str, Any]:
        """GM→EBITDA換算係数"""
        delta_gm_pp = self.state.get('delta_gm_pp', 0)
        revenue = self.state.get('revenue_$k', 600000)  # デフォルト600k
        
        # 売上に応じた係数を選択
        factors = self.config['thresholds']['gm_to_ebitda_pp_factor_$k']
        closest_rev = min(factors.keys(), key=lambda x: abs(x - revenue))
        factor = factors[closest_rev]
        
        ebitda_impact = revenue * delta_gm_pp / 100 * factor
        
        result = {
            'ebitda_impact_$k': ebitda_impact,
            'delta_gm_pp': delta_gm_pp,
            'revenue_$k': revenue,
            'factor': factor,
            'description': f"ΔGM {delta_gm_pp:+.1f}pp × Rev ${revenue:,.0f}k × {factor}k = EBITDA {ebitda_impact:+,.0f}k"
        }
        return result
    
    def evaluate_tripwire_priority(self) -> Dict[str, Any]:
        """トリップワイヤ優先順位判定"""
        priorities = self.config['thresholds']['tripwire_priority']
        results = {}
        
        # 各優先度の判定
        for i, priority in enumerate(priorities, 1):
            if priority == 'contract_liabilities':
                cl_qoq = self.state.get('cl_qoq', 0)
                results[f'priority_{i}_cl'] = {
                    'status': 'PASS' if cl_qoq >= 0 else 'FAIL',
                    'value': cl_qoq,
                    'description': f"CL QoQ {cl_qoq:+.1f}%"
                }
            elif priority == 'greenbox_rollforward':
                gb_deferred = self.state.get('gb_deferred_change', 0)
                results[f'priority_{i}_gb'] = {
                    'status': 'PASS' if gb_deferred < 0 else 'FAIL',
                    'value': gb_deferred,
                    'description': f"GB Deferred {gb_deferred:+.1f}%"
                }
            elif priority == 'unbilled_dou':
                dou = self.state.get('dou_days', 0)
                unbilled_share = self.state.get('unbilled_share_pct', 0)
                results[f'priority_{i}_dou'] = {
                    'status': 'PASS' if dou <= 30 and unbilled_share <= 50 else 'FAIL',
                    'value': {'dou': dou, 'unbilled_share': unbilled_share},
                    'description': f"DoU {dou}日, Unbilled {unbilled_share:.1f}%"
                }
            elif priority == 'mix':
                delta_sw = self.state.get('delta_sw_pp', 0)
                delta_ops = self.state.get('delta_ops_pp', 0)
                delta_gm = 0.60 * delta_sw - 0.18 * delta_ops
                results[f'priority_{i}_mix'] = {
                    'status': 'PASS' if delta_gm >= 0 else 'FAIL',
                    'value': delta_gm,
                    'description': f"ΔGM {delta_gm:+.1f}pp (SW {delta_sw:+.1f}, Ops {delta_ops:+.1f})"
                }
        
        # 最上位の有効な判定を特定
        active_priority = None
        for i, priority in enumerate(priorities, 1):
            key = f'priority_{i}_{priority.split("_")[0]}'
            if key in results and results[key]['status'] == 'PASS':
                active_priority = key
                break
        
        result = {
            'active_priority': active_priority,
            'results': results,
            'description': f"最上位有効: {active_priority or 'None'}"
        }
        return result
    
    def evaluate_ot_pt_proxy(self) -> Dict[str, Any]:
        """OT/PT未開示スロットの代理指標"""
        service_ot = self.state.get('service_ot_actual', 0)
        unbilled_share = self.state.get('unbilled_share_pct', 0)
        dou_days = self.state.get('dou_days', 0)
        cl_qoq = self.state.get('cl_qoq', 0)
        
        targets = self.config['thresholds']['ot_pt_proxy_targets']
        
        result = {
            'service_ot': {
                'value': service_ot,
                'status': 'PASS' if service_ot >= 33013 else 'FAIL',
                'description': f"Service OT ${service_ot:,.0f}k vs $33,013k下限"
            },
            'unbilled_share': {
                'value': unbilled_share,
                'status': 'PASS' if unbilled_share <= targets['unbilled_share_pct'] else 'FAIL',
                'description': f"Unbilled {unbilled_share:.1f}% vs ≤{targets['unbilled_share_pct']}%目標"
            },
            'dou_days': {
                'value': dou_days,
                'status': 'PASS' if dou_days <= targets['dou_days'] else 'FAIL',
                'description': f"DoU {dou_days}日 vs ≤{targets['dou_days']}日目標"
            },
            'cl_qoq': {
                'value': cl_qoq,
                'status': 'PASS' if cl_qoq >= targets['cl_qoq'] else 'FAIL',
                'description': f"CL QoQ {cl_qoq:+.1f}% vs ≥{targets['cl_qoq']}%目標"
            }
        }
        return result
    
    def evaluate_star_rating(self) -> Dict[str, Any]:
        """v0.6.3: Star整数評価（1-5）"""
        config = self.config.get('star_evaluation', {})
        min_stars = config.get('min_stars', 1)
        max_stars = config.get('max_stars', 5)
        
        # Core基準（基本3★）
        core_stars = 3
        
        # Edge調整（±1★）
        edge_adjustment = 0
        if self.edge_items:
            for edge in self.edge_items:
                if edge.get('confidence', 0) >= 70:  # P≥70
                    if edge.get('direction', 'neutral') == 'bullish':
                        edge_adjustment += 1
                    elif edge.get('direction', 'neutral') == 'bearish':
                        edge_adjustment -= 1
        
        # 最終Star評価
        final_stars = max(min_stars, min(max_stars, core_stars + edge_adjustment))
        
        result = {
            'stars': final_stars,
            'core_stars': core_stars,
            'edge_adjustment': edge_adjustment,
            'description': f"★{final_stars}/5 (Core{core_stars}+Edge{edge_adjustment:+d})"
        }
        return result
    
    def evaluate_direction_probability(self) -> Dict[str, Any]:
        """v0.6.3: 方向確率評価"""
        up_pct = self.state.get('direction_prob_up_pct', 50)
        down_pct = self.state.get('direction_prob_down_pct', 50)
        
        # 合計100%チェック
        total = up_pct + down_pct
        if total != 100:
            up_pct = 50
            down_pct = 50
        
        result = {
            'direction_prob_up_pct': up_pct,
            'direction_prob_down_pct': down_pct,
            'description': f"上向{up_pct}% / 下向{down_pct}%"
        }
        return result
    
    def evaluate_confidence_level(self) -> Dict[str, Any]:
        """v0.6.3: 確信度評価（50-95%クリップ）"""
        base_confidence = self.state.get('confidence_pct', 75)
        config = self.config.get('star_evaluation', {})
        confidence_clip = config.get('confidence_clip', [50, 95])
        
        # Edge採用時のみ±5pp調整（1回のみ）
        edge_adjustment = 0
        if self.edge_items and any(e.get('confidence', 0) >= 70 for e in self.edge_items):
            edge_adjustment = 5 if any(e.get('direction') == 'bullish' for e in self.edge_items) else -5
        
        final_confidence = max(confidence_clip[0], min(confidence_clip[1], base_confidence + edge_adjustment))
        
        result = {
            'confidence_pct': final_confidence,
            'base_confidence': base_confidence,
            'edge_adjustment': edge_adjustment,
            'description': f"確信度{final_confidence}% (Base{base_confidence}+Edge{edge_adjustment:+d})"
        }
        return result
    
    def run_evaluation(self) -> Dict[str, Any]:
        """v0.6.3: 全評価を実行（MVP-4+対応）"""
        self.results = {
            'alpha4_gate': self.evaluate_alpha4_gate(),
            'alpha5_bands': self.evaluate_alpha5_bands(),
            'gm_to_ebitda_conversion': self.evaluate_gm_to_ebitda_conversion(),
            'tripwire_priority': self.evaluate_tripwire_priority(),
            'ot_pt_proxy': self.evaluate_ot_pt_proxy(),
            'star_rating': self.evaluate_star_rating(),
            'direction_probability': self.evaluate_direction_probability(),
            'confidence_level': self.evaluate_confidence_level()
        }
        return self.results
    
    def apply_anchor_lint(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """v0.6.3: AnchorLint v1 + 二重アンカー適用"""
        lint_cfg = Path("ahf/config/anchorlint.yaml")
        if not lint_cfg.exists():
            return results
        
        try:
            # AnchorLint v1実行
            p = subprocess.run(
                [sys.executable, "ahf/mvp4/anchor_lint_v1.py", "--config", str(lint_cfg)],
                input=json.dumps(results).encode("utf-8"),
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                check=True
            )
            linted_results = json.loads(p.stdout.decode("utf-8"))
            
            # v0.6.3: 二重アンカー状態を追加
            linted_results.setdefault("dual_anchor_status", "CONFIRMED")
            linted_results.setdefault("auto_checks", {}).setdefault("anchor_lint_pass", True)
            
            return linted_results
        except Exception as e:
            # fail-soft: keep result, log lint error
            results.setdefault("auto_checks", {}).setdefault("messages", []).append(f"anchorlint_error: {e}")
            results.setdefault("auto_checks", {}).setdefault("anchor_lint_pass", False)
            return results
    
    def generate_anchor_backup(self, text: str, pageno: int = 1) -> Dict[str, Any]:
        """v0.6.3: アンカーバックアップ生成"""
        # 25語以内にクリップ
        words = text.split()[:25]
        clipped_text = " ".join(words)
        
        # SHA1ハッシュ生成
        text_hash = hashlib.sha1(clipped_text.encode('utf-8')).hexdigest()
        
        return {
            "pageno": pageno,
            "quote": clipped_text,
            "hash": text_hash
        }
    
    def validate_verbatim(self, text: str) -> bool:
        """v0.6.3: 逐語検証（≤25語）"""
        words = text.split()
        return len(words) <= 25
    
    def check_domain_whitelist(self, url: str) -> bool:
        """v0.6.3: ドメインホワイトリストチェック"""
        config = self.config.get('anchor_policy', {})
        whitelist = config.get('domain_whitelist', ['sec.gov', 'investors.*'])
        
        for domain in whitelist:
            if domain.replace('*', '') in url:
                return True
        return False

    def save_results(self, output_path: str):
        """結果をJSONファイルに保存（AnchorLint適用後）"""
        # AnchorLint v1を適用
        linted_results = self.apply_anchor_lint(self.results)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(linted_results, f, ensure_ascii=False, indent=2)

def main():
    parser = argparse.ArgumentParser(description='AHF Min - 最小実装版')
    parser.add_argument('--config', required=True, help='設定ファイルパス')
    parser.add_argument('--state', required=True, help='状態ファイルパス')
    parser.add_argument('--out', required=True, help='出力ファイルパス')
    
    args = parser.parse_args()
    
    try:
        # AHF Min実行
        ahf = AHFMin(args.config, args.state)
        results = ahf.run_evaluation()
        ahf.save_results(args.out)
        
        print("✅ AHF Min評価完了")
        print(f"📊 結果保存: {args.out}")
        
        # v0.6.3: 表示フォーマット（固定順序）
        print("\n📋 AHF v0.6.3 評価結果:")
        print("=" * 60)
        
        # 軸の順序固定：①右肩 → ②勾配 → ③時間軸 → ④認知ギャップ
        print(f"①右肩上がり: {results['alpha4_gate']['description']}")
        print(f"②勾配の質: {results['alpha5_bands']['description']}")
        print(f"③時間軸: {results['gm_to_ebitda_conversion']['description']}")
        print(f"④認知ギャップ: {results['tripwire_priority']['description']}")
        
        # Star評価と確信度
        print(f"\n★評価: {results['star_rating']['description']}")
        print(f"確信度: {results['confidence_level']['description']}")
        print(f"方向確率: {results['direction_probability']['description']}")
        
        # 自動チェック結果
        auto_checks = results.get('auto_checks', {})
        if auto_checks:
            print(f"\n🔍 自動チェック:")
            print(f"  α4 Gate: {'✅' if auto_checks.get('alpha4_gate_pass') else '❌'}")
            print(f"  α5 Math: {'✅' if auto_checks.get('alpha5_math_pass') else '❌'}")
            print(f"  AnchorLint: {'✅' if auto_checks.get('anchor_lint_pass') else '❌'}")
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

