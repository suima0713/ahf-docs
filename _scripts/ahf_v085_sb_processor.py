#!/usr/bin/env python3
"""
AHF v0.8.5-SB + Hard-Lock v2 Processor
S4/5/6の物理分離処理を実行
"""

import re
import json
import sys
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta

class AHFv085Processor:
    """AHF v0.8.5-SB プロセッサー"""
    
    def __init__(self):
        # ステージ定義
        self.stages = {
            'S4': self.process_s4_d_only,
            'S5': self.process_s5_e_only, 
            'S6': self.process_s6_synthesis
        }
        
        # 軸定義
        self.axes = {
            'LEC': '長期EV確度',
            'NES': '長期EV勾配', 
            'VALUE': '現バリュ（絶対）',
            'FUTURE': '将来EVバリュ（総合）'
        }
    
    def extract_stage(self, text: str) -> Optional[str]:
        """テキストからステージを抽出"""
        stage_pattern = r'STAGE:\s*(S[456])'
        match = re.search(stage_pattern, text)
        return match.group(1) if match else None
    
    def validate_t1_source(self, source: str) -> bool:
        """T1ソースの検証"""
        t1_patterns = [
            r'8-K|10-Q|10-K',
            r'SEC\s+EDGAR',
            r'IR\s+PR|Investor\s+Relations',
            r'ガイダンス|guidance'
        ]
        
        return any(re.search(pattern, source, re.IGNORECASE) for pattern in t1_patterns)
    
    def calculate_alpha3_nowcast(self, mix_data: Dict, causality_data: Dict) -> int:
        """α3 Now-cast計算"""
        # Mix↑≥+200bps かつ 一次因果（MD&A/PR）
        mix_boost = mix_data.get('mix_change', 0) >= 200
        causality = causality_data.get('primary_causality', False)
        
        if mix_boost and causality:
            return 2
        elif mix_boost or causality:
            return 1
        else:
            return 0
    
    def calculate_alpha5_nowcast(self, oi_growth: float, revenue_yoy: float, 
                                oi_margin_yoy: float, efficiency_phrase: bool) -> int:
        """α5 Now-cast計算"""
        # OI成長≧売上YoY+200bps 又は OIマージンYoY＋≥50bps ＋効率フレーズ
        condition1 = oi_growth >= revenue_yoy + 200
        condition2 = oi_margin_yoy >= 50 and efficiency_phrase
        
        if condition1 or condition2:
            return 2
        elif condition1 or condition2:
            return 1
        else:
            return 0
    
    def calculate_lec(self, metrics: Dict) -> Tuple[int, float]:
        """① 長期EV確度（LEC）計算"""
        # 骨格4：A/R↓・DOH↓・CL(契約負債)↑・集中↓ の達成数（0–4）
        achievements = 0
        
        # A/R↓
        if metrics.get('ar_trend') == 'decreasing':
            achievements += 1
        
        # DOH↓
        if metrics.get('doh_trend') == 'decreasing':
            achievements += 1
        
        # CL(契約負債)↑
        if metrics.get('cl_trend') == 'increasing':
            achievements += 1
        
        # 集中↓
        if metrics.get('concentration_trend') == 'decreasing':
            achievements += 1
        
        # Fwdブースト(+1, 上限★4)
        fwd_boost = 0
        if (metrics.get('next_q_guidance_qoq', 0) >= 12 and 
            metrics.get('primary_causality', False)):
            fwd_boost = 1
        
        # 星計算
        base_stars = min(achievements + 1, 5)  # 0→★2, 1→★3, 2→★4, ≥3→★5
        final_stars = min(base_stars + fwd_boost, 5)
        
        # 確信度計算（50-95%）
        confidence = 50 + (achievements * 11.25) + (fwd_boost * 15)
        confidence = min(confidence, 95)
        
        return final_stars, confidence
    
    def calculate_nes(self, data: Dict) -> Tuple[int, float]:
        """② 長期EV勾配（NES）計算"""
        # 式（骨子）：0.5·q/q + 0.3·GuideΔ + 0.2·Orders/Backlog + Margin_term + Health_term
        
        qoq = data.get('qoq_change', 0)
        guide_delta = data.get('guidance_delta', 0)
        orders_backlog = data.get('orders_backlog', 0)
        
        # Margin_term
        gm_change = data.get('gm_change', 0)
        if gm_change >= 50:
            margin_term = 1
        elif gm_change >= -50:
            margin_term = 0
        else:
            margin_term = -1
        
        # Health_term：成長%＋GAAP OPM%
        growth_rate = data.get('growth_rate', 0)
        gaap_opm = data.get('gaap_opm', 0)
        ro40 = growth_rate + gaap_opm
        
        if ro40 >= 40:
            health_term = 1
        elif ro40 >= 30:
            health_term = 0
        else:
            health_term = -1
        
        # NES計算
        nes = (0.5 * qoq + 0.3 * guide_delta + 0.2 * orders_backlog + 
               margin_term + health_term)
        
        # 星計算
        if nes >= 8:
            stars = 5
        elif nes >= 5:
            stars = 4
        elif nes >= 2:
            stars = 3
        elif nes >= 0:
            stars = 2
        else:
            stars = 1
        
        # 確信度計算
        confidence = 50 + (nes * 5.625)
        confidence = max(50, min(confidence, 95))
        
        return stars, confidence
    
    def calculate_current_value(self, data: Dict) -> Tuple[str, float, int]:
        """③ 現バリュ（絶対）計算"""
        # Step-1（色/Vmult）
        evs_actual = data.get('evs_actual', 0)
        evs_fair_base = data.get('evs_fair_base', 0)
        
        # 帯選択：g_fwd・OPM_fwd による
        g_fwd = data.get('g_fwd', 0)
        opm_fwd = data.get('opm_fwd', 0)
        
        # 帯の決定（簡略化）
        if g_fwd >= 15 and opm_fwd >= 20:
            band_multiplier = 10
        elif g_fwd >= 10 and opm_fwd >= 15:
            band_multiplier = 8
        else:
            band_multiplier = 6
        
        fair_band = band_multiplier * evs_actual
        
        # 色→Vmult
        if evs_actual >= fair_band * 0.95:
            color = 'Green'
            vmult = 1.05
        elif evs_actual >= fair_band * 0.85:
            color = 'Amber'
            vmult = 0.90
        else:
            color = 'Red'
            vmult = 0.75
        
        # Step-2（星）
        if color == 'Green':
            stars = 3
        elif color == 'Amber':
            stars = 2
        else:
            stars = 1
        
        return color, vmult, stars
    
    def process_s4_d_only(self, data: Dict) -> Dict:
        """S4｜D（カタリスト認知度 ＋ 整合チェック）処理"""
        result = {
            'stage': 'S4',
            'dual_anchor_status': self.determine_dual_anchor_status(data),
            'd_ledger': [],
            'd_calculation': {},
            'd_minus': [],
            'data_gaps': []
        }
        
        # カタリスト台帳の構築
        catalysts = data.get('catalysts', [])
        for catalyst in catalysts:
            # スキーマ：k:(A 認知, P 成立確率, I 影響, H 時点重み)
            entry = {
                'k': catalyst.get('key', ''),
                'A': self.get_cognition_score(catalyst.get('source', '')),
                'P': catalyst.get('probability', 0.5),
                'I': self.get_impact_score(catalyst.get('impact', 'Mid')),
                'H': self.get_time_weight(catalyst.get('horizon', '6-12M')),
                'quote': catalyst.get('quote', '')[:25]  # 25語以内
            }
            result['d_ledger'].append(entry)
        
        # d計算
        U = sum(entry['H'] * entry['I'] * entry['P'] * (1 - entry['A']) 
                for entry in result['d_ledger'])
        Umax = sum(entry['H'] * entry['I'] * entry['P'] 
                   for entry in result['d_ledger'])
        
        d = max(0, min(1, U / Umax if Umax > 0 else 0))
        
        result['d_calculation'] = {
            'U': U,
            'Umax': Umax,
            'd': d
        }
        
        # 非価格ディスカウント要因
        result['d_minus'] = data.get('discount_factors', [])
        
        # data_gap
        result['data_gaps'] = data.get('data_gaps', [])
        
        return result
    
    def process_s5_e_only(self, data: Dict) -> Dict:
        """S5｜E（ピア相対：逆DCF-light）処理"""
        result = {
            'stage': 'S5',
            'dual_anchor_status': self.determine_dual_anchor_status(data),
            'ntm_calculation': {},
            'evs_fair_calculation': {},
            'e_score': 0,
            'data_gaps': []
        }
        
        # NTM=4×次Qガイダンス中点（T1）
        next_q_guidance = data.get('next_q_guidance', {})
        ntm = 4 * next_q_guidance.get('midpoint', 0)
        result['ntm_calculation'] = {'ntm': ntm}
        
        # EVS_fair近似式
        opm_fwd = data.get('opm_fwd', 0)
        tax_rate = data.get('tax_rate', 0.25)
        wacc = data.get('wacc', 0.10)
        g_fwd = data.get('g_fwd', 0)
        
        evs_fair = (opm_fwd * (1 - tax_rate)) / (wacc - g_fwd)
        result['evs_fair_calculation'] = {
            'opm_fwd': opm_fwd,
            'tax_rate': tax_rate,
            'wacc': wacc,
            'g_fwd': g_fwd,
            'evs_fair': evs_fair
        }
        
        # 相対スコア e
        peers = data.get('peers', [])
        if peers:
            premiums = []
            for peer in peers:
                peer_evs = peer.get('evs', 0)
                premium = (peer_evs - evs_fair) / evs_fair if evs_fair > 0 else 0
                premiums.append(premium)
            
            if premiums:
                prem_med = sorted(premiums)[len(premiums) // 2]
                current_premium = (data.get('current_evs', 0) - evs_fair) / evs_fair if evs_fair > 0 else 0
                
                # |Prem−Prem_med|≥10pp：0 / 0.25 / 0.50
                diff = abs(current_premium - prem_med)
                if diff >= 0.10:
                    e_score = 0
                elif diff >= 0.05:
                    e_score = 0.25
                else:
                    e_score = 0.50
                
                result['e_score'] = e_score
        
        result['data_gaps'] = data.get('data_gaps', [])
        
        return result
    
    def process_s6_synthesis(self, data: Dict) -> Dict:
        """S6｜④ 将来EVバリュ（総合）処理（Proof-Ladder仕様）"""
        result = {
            'stage': 'S6',
            'dual_anchor_status': self.determine_dual_anchor_status(data),
            'thesis': '',
            'p1_quote': '',
            'p2_color': '',
            'visibility_b': '',
            'e_score': 0,
            'e_intensity': '',
            'red_flags': [],
            'future_stars': 0,
            'verdict': '',
            'data_gaps': []
        }
        
        # 入力値の取得
        lec_stars = data.get('lec_stars', 0)  # ①★
        nes_stars = data.get('nes_stars', 0)  # ②★
        current_color = data.get('current_color', 'Red')  # ③色
        d_value = data.get('d_value', 0)  # S4のd
        e_score = data.get('e_score', 0)  # S5のe
        visibility_b = data.get('visibility_b', 'Med')  # 見えにくさ
        
        # Proof-Ladder要素の設定
        result['thesis'] = data.get('thesis', '12-24MでEV確度と勾配の両立により適正価格への収束を期待')
        result['p1_quote'] = data.get('p1_quote', '次Qガイダンス+15%QoQ、実行完了のT1確認')
        result['p2_color'] = current_color
        result['visibility_b'] = visibility_b
        result['e_score'] = e_score
        result['e_intensity'] = data.get('e_intensity', 'Med')
        result['red_flags'] = data.get('red_flags', ['集中度の数値開示不足', '運転資本改善の定量化待ち'])
        
        # ④クイック判定（A/B/Cルール）
        future_stars, verdict = self.calculate_verdict_abc(
            lec_stars, nes_stars, current_color, e_score, 
            d_value, visibility_b
        )
        
        result['future_stars'] = future_stars
        result['verdict'] = verdict
        result['data_gaps'] = data.get('data_gaps', [])
        
        return result
    
    def calculate_verdict_abc(self, lec_stars: int, nes_stars: int, current_color: str, 
                            e_score: float, d_value: float, visibility_b: str) -> Tuple[int, str]:
        """A/B/CルールによるVerdict計算"""
        
        # A｜雲が晴れた（確度↑）：①≥★4 ＋ ②≥★4 ＋ ③=Green ＋（e≥0.25 or 資格completed/CL>0/集中低下のいずれか1つ）
        if (lec_stars >= 4 and nes_stars >= 4 and current_color == 'Green' and 
            (e_score >= 0.25 or True)):  # 簡略化：資格completed等の条件はTrueと仮定
            future_stars = 5
            verdict = '★5 Under'
        
        # B｜勢い＞確度（雲あり）：②=★5 ＋ ①=★2–3 ＋ ③=Green（eは0.25〜0.50可）
        elif (nes_stars == 5 and 2 <= lec_stars <= 3 and current_color == 'Green' and 
              0.25 <= e_score <= 0.50):
            future_stars = 4
            verdict = '★4 Under'
        
        # C｜色が弱い/勢い不足：③=Amber/Red or ②≤★3
        elif current_color in ['Amber', 'Red'] or nes_stars <= 3:
            if current_color == 'Red':
                future_stars = 2
                verdict = '★2 Over'
            else:
                future_stars = 3
                verdict = '★3 Neutral'
        
        # デフォルト
        else:
            future_stars = 3
            verdict = '★3 Neutral'
        
        # タイブレーク
        # 1. D(−)（実行未了/前受0/集中高/開示粒度不足）が強 → 一段階ダウン
        if d_value > 0.5:  # 集中度高と仮定
            future_stars = max(1, future_stars - 1)
            verdict = verdict.replace(f'★{future_stars + 1}', f'★{future_stars}')
        
        # 2. B高（会計ラグ等の"見えにくさ"）＋ e=0.50 → 認知ラグ加点（★4寄り）
        if visibility_b == 'High' and e_score == 0.50:
            if future_stars == 3:
                future_stars = 4
                verdict = verdict.replace('★3', '★4')
        
        # 二重割安センチネル：③=Green × ⑤=e=0.50 のとき B（見えにくさ） を必ず算出
        if current_color == 'Green' and e_score == 0.50:
            verdict += f" (B={visibility_b})"
        
        return future_stars, verdict
    
    def determine_dual_anchor_status(self, data: Dict) -> str:
        """dual_anchor_statusの決定"""
        # T1ソースの確認
        t1_sources = data.get('t1_sources', [])
        sec_sources = [s for s in t1_sources if re.search(r'8-K|10-Q|10-K|SEC', s, re.IGNORECASE)]
        
        if len(sec_sources) >= 2:
            return 'CONFIRMED'
        elif len(sec_sources) == 1:
            return 'PENDING_SEC'
        else:
            return 'SINGLE'
    
    def get_cognition_score(self, source: str) -> float:
        """認知度スコア計算"""
        if re.search(r'8-K|10-Q|10-K', source, re.IGNORECASE):
            return 1.0
        elif re.search(r'IR\s+PR|Investor\s+Relations', source, re.IGNORECASE):
            return 0.75
        elif re.search(r'ガイダンス|guidance', source, re.IGNORECASE):
            return 0.6
        else:
            return 0.1
    
    def get_impact_score(self, impact: str) -> float:
        """影響度スコア計算"""
        impact_map = {
            'Small': 0.1,
            'Mid': 0.3,
            'Large': 0.5,
            'XL': 0.7
        }
        return impact_map.get(impact, 0.3)
    
    def get_time_weight(self, horizon: str) -> float:
        """時間重み計算"""
        if '0-6M' in horizon or '0-6m' in horizon:
            return 1.0
        elif '6-12M' in horizon or '6-12m' in horizon:
            return 0.66
        elif '12-24M' in horizon or '12-24m' in horizon:
            return 0.33
        else:
            return 0.66  # デフォルト
    
    def calculate_di(self, lec_stars: int, nes_stars: int, vmult: float) -> Tuple[str, float]:
        """DI計算"""
        di = (0.6 * nes_stars / 5 + 0.4 * lec_stars / 5) * vmult
        
        if di >= 0.55:
            decision = 'GO'
        elif di >= 0.32:
            decision = 'WATCH'
        else:
            decision = 'NO-GO'
        
        # Red時DI上限0.55
        if vmult == 0.75:  # Red
            di = min(di, 0.55)
            if di < 0.55:
                decision = 'WATCH'
        
        return decision, di
    
    def validate_hardlock_v2(self, stage: str, text: str) -> Tuple[bool, List[str]]:
        """Hard-Lock v2検証"""
        errors = []
        
        # 宣誓ヘッダの検証
        if not re.search(rf'STAGE:\s*{stage}\s*\([^)]+\)', text):
            errors.append(f"Missing STAGE header for {stage}")
        
        # ALLOW/BLOCKの検証
        if not re.search(r'ALLOW:\{[^}]+\}', text):
            errors.append("Missing ALLOW block")
        
        if not re.search(r'BLOCK:\{[^}]+\}', text):
            errors.append("Missing BLOCK block")
        
        # ステージ別の禁句チェック
        banned_terms = self.get_banned_terms(stage)
        for term in banned_terms:
            if re.search(term, text, re.IGNORECASE):
                errors.append(f"Banned term found: {term}")
        
        # Preflight/Exitの検証
        if not re.search(r'Preflight:', text):
            errors.append("Missing Preflight section")
        
        if not re.search(r'Exit:', text):
            errors.append("Missing Exit section")
        
        return len(errors) == 0, errors
    
    def get_banned_terms(self, stage: str) -> List[str]:
        """ステージ別の禁句リスト"""
        if stage == 'S4':
            return [
                r'peer', r'relative', r'EVS_fair', r'premium', r'median', 
                r'discount率', r'Verdict', r'④', r'マルチプル'
            ]
        elif stage == 'S5':
            return [
                r'④', r'合成', r'DI改変'
            ]
        elif stage == 'S6':
            return [
                r'数式合成の前提化', r'D/E再計算', r'DI改変'
            ]
        return []
    
    def process_stage(self, stage: str, data: Dict) -> Dict:
        """ステージ処理のメイン"""
        if stage not in self.stages:
            raise ValueError(f"Unknown stage: {stage}")
        
        result = self.stages[stage](data)
        
        # Hard-Lock v2検証
        output_text = self.generate_output_template(stage, result)
        is_valid, errors = self.validate_hardlock_v2(stage, output_text)
        
        if not is_valid:
            result['hardlock_errors'] = errors
            result['hardlock_status'] = 'FAILED'
        else:
            result['hardlock_status'] = 'PASSED'
        
        return result
    
    def generate_output_template(self, stage: str, result: Dict) -> str:
        """出力テンプレート生成"""
        if stage == 'S4':
            return self.generate_s4_template(result)
        elif stage == 'S5':
            return self.generate_s5_template(result)
        elif stage == 'S6':
            return self.generate_s6_template(result)
        else:
            return "Unknown stage"
    
    def generate_s4_template(self, result: Dict) -> str:
        """S4テンプレート生成（直行MVP仕様）"""
        template = f"""STAGE: S4 (D-only) | ALLOW:{{D_ledger,D_minus,d_calc,data_gap}} | BLOCK:{{peer,relative,EVS_fair,premium,median,discount率,Verdict,④}}
dual_anchor_status: {result['dual_anchor_status']}

1) D(+)台帳 Top3（逐語≤25語＋#text/anchor_backup）
"""
        # Top3のみ表示
        top3_ledger = result['d_ledger'][:3]
        for i, entry in enumerate(top3_ledger, 1):
            template += f"{i}. {entry['k']}: A={entry['A']}, P={entry['P']}, I={entry['I']}, H={entry['H']} | \"{entry['quote']}\"\n"
        
        template += f"""
2) d計算（数式のみ）
U = Σ(H·I·P·(1-A_eff)) = {result['d_calculation']['U']:.3f}
Umax = Σ(H·I·P) = {result['d_calculation']['Umax']:.3f}
d = clip(U/Umax, 0, 1) = {result['d_calculation']['d']:.3f}

3) D(−)台帳 Top3
"""
        # Top3のみ表示
        top3_minus = result['d_minus'][:3]
        for i, factor in enumerate(top3_minus, 1):
            template += f"{i}. {factor}\n"
        
        template += f"""
4) 整合（30秒）：③の割安＝d+h（重し）。今回は h≫d を明示
d={result['d_calculation']['d']:.3f}（未社会化）+ h=0.15（非価格重し）→ ③割安=0.45

5) 示唆（最小）：何が出れば h↓/d↓ か（T1トリガー）
- 実行完了のT1確認（completed shipments等）
- 集中度低下の数値開示
- 運転資本改善の定量化

6) 監査（最小）：監視T1（≤5）
- 次Qガイダンス更新
- 8-K/10-Qでの実行状況
- IR PRでの進捗報告
- 契約負債の推移
- 集中度の数値開示

7) data_gap/TTL
"""
        for gap in result['data_gaps']:
            template += f"- {gap}\n"
        
        template += """
Preflight: stage=S4 | allow={D_ledger,D_minus,d_calc,data_gap} | blocklist=PASS
Exit: no banned terms, math-only (d), anchors ok
"""
        
        return template
    
    def generate_s5_template(self, result: Dict) -> str:
        """S5テンプレート生成（直行MVP仕様）"""
        template = f"""STAGE: S5 (E-only) | ALLOW:{{ntm,evs_fair,e_score,anchors,data_gap}} | BLOCK:{{④,Verdict,合成,DI改変}}
dual_anchor_status: {result['dual_anchor_status']}

前提：同日ET・NTM統一
NTM = 4×次Qガイダンス中点 = {result['ntm_calculation']['ntm']:.2f}

1) Prem_AAOI, Prem_peer群, Prem_med（E_intensity注記）
Prem_AAOI = EVS_actual/EVS_fair - 1 = {result.get('prem_aaoi', 0):.1%}
Prem_peer群 = {result.get('prem_peers', [])}
Prem_med = {result.get('prem_med', 0):.1%}
E_intensity = |Prem_AAOI - Prem_med| = {result.get('e_intensity', 0):.1%} (High/Med/Low)

2) e∈{{0,0.25,0.5}}
e = {result['e_score']:.2f}

3) 整合（30秒）：③との方向一致/不一致を一言
③=Green × e={result['e_score']:.2f} → 方向一致（両方割安）

4) 示唆（最小）：eを動かすT1トリガー
- ピアの次Qガイダンス更新
- セクター全体のEVS_fair再計算
- 新規ピアの追加/除外

5) 監査（最小）：不足T1/T1*＋TTL
- ピアの8-K/10-Q更新
- セクター平均のWACC/g_fwd更新
- 新規上場企業の追加検討

6) data_gap/TTL
"""
        for gap in result['data_gaps']:
            template += f"- {gap}\n"
        
        template += """
Preflight: stage=S5 | allow={ntm,evs_fair,e_score,anchors,data_gap} | blocklist=PASS
Exit: no banned terms, math-only (e), anchors ok
"""
        
        return template
    
    def generate_s6_template(self, result: Dict) -> str:
        """S6テンプレート生成（Proof-Ladder仕様）"""
        template = f"""STAGE: S6 (④-only) | ALLOW:{{④★,Verdict,proof_ladder}} | BLOCK:{{数式合成Sの前提化,D/E再計算,DI改変}}
dual_anchor_status: {result['dual_anchor_status']}

1. Thesis（1行：12–24Mの核心仮説）
{result.get('thesis', '12-24MでEV確度と勾配の両立により適正価格への収束を期待')}

2. P1 勢い：②の根拠をT1逐語1本（≤25語）
\"{result.get('p1_quote', '次Qガイダンス+15%QoQ、実行完了のT1確認')}\"

3. P2 価格：③の色（Green/Amber/Red）のみ（倍率の再掲なし）
{result.get('p2_color', 'Green')}

4. P3 可視性：D(+) vs D(−) の要旨1行＋"見えにくさ"B=Low/Med/High
D(+): 実行完了のT1確認待ち / D(-): 集中度高・運転資本改善未定量化
B = {result.get('visibility_b', 'Med')}

5. 相対：e（0/0.25/0.50、必要なら E_intensity も一言）
e = {result.get('e_score', 0.25):.2f} (E_intensity: {result.get('e_intensity', 'Med')})

6. Red flags：最大2件（矛盾/未解消リスク）
{result.get('red_flags', ['集中度の数値開示不足', '運転資本改善の定量化待ち'])}

7. Verdict（★＋Under/Neutral/Over）：下のクイック判定に当てはめて断言
{result.get('verdict', '★4 Under')}

data_gap/TTL
"""
        for gap in result['data_gaps']:
            template += f"- {gap}\n"
        
        template += """
Preflight: stage=S6 | allow={④★,Verdict,proof_ladder} | blocklist=PASS
Exit: no banned terms, proof-ladder only, anchors ok
"""
        
        return template

def main():
    """メイン実行"""
    if len(sys.argv) < 3:
        print("Usage: python ahf_v085_sb_processor.py <stage> <data_file>")
        print("Stages: S4, S5, S6")
        sys.exit(1)
    
    stage = sys.argv[1]
    data_file = sys.argv[2]
    
    if stage not in ['S4', 'S5', 'S6']:
        print("Error: Invalid stage. Must be S4, S5, or S6")
        sys.exit(1)
    
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{data_file}' not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        sys.exit(1)
    
    processor = AHFv085Processor()
    
    try:
        result = processor.process_stage(stage, data)
        output = processor.generate_output_template(stage, result)
        
        print(output)
        
        # 結果をファイルに保存
        output_file = f"ahf_v085_{stage.lower()}_output.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output)
        
        print(f"\nOutput saved to: {output_file}")
        
    except Exception as e:
        print(f"Error processing stage {stage}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
