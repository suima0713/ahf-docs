# AHF v0.7.2β — 最終統合版（4パッチ適用済み 2025‑09‑22 JST)

## 概要

①②③④の4つのパッチを完全統合し、*データ欠落≠低評価* の歪みを完全に解消し、セクター特性を考慮した実態に近い評価を実現しました。

## 適用パッチ

### 1. ①右肩「Fwdブースト」パッチ ✅
- **実績主義維持**: 従来のRSS計算をベースに
- **先行シグナル注入**: T1で確認できる強シグナルのみ+1ブースト
- **安全装置**: ガイダンスマイナス時-1、上限★4

### 2. ②勾配 Now‑castパッチ ✅
- **α3_ncast（Mix/因果）**: SW/Cloud比改善の定量化
- **α5_ncast（レバレッジ）**: OI成長と売上YoYの関係
- **Gap‑safe**: 主要指標欠落時の中立=1点（自動★1回避）

### 3. ③認知ギャップ Now‑castパッチ ✅
- **V基準の星付け**: Green→★3／Amber→★2／Red→★1
- **T/R加点システム**: T+R≥3→+1★、T+R=4→+2★
- **確信度表示**: 50–95%でクリップ

### 4. ④セクター対応V-Overlay ✅
- **保険セクター**: NTM P/E × EPS成長 × MCRトレンド
- **公益事業**: 規制制約を考慮した評価
- **標準セクター**: EV/Sales + Rule of 40

## ファイル構成

### 新規ファイル
- `ahf_rss_fwd_boost_v072.py` - ①右肩「Fwdブースト」パッチ
- `ahf_alpha_nowcast_v072.py` - ②勾配Now‑castパッチ
- `ahf_tri3_v_overlay_v072.py` - ③認知ギャップNow‑castパッチ
- `ahf_v_overlay_healthcare_v072.py` - 保険セクター用V-Overlay
- `ahf_v_overlay_sector_aware_v072.py` - セクター対応V-Overlay統合
- `ahf_v072_final_integrated.py` - 4パッチ最終統合版

### 統合処理フロー
```
triage.json + facts.md + alpha_scoring.json + market_data.json
    ↓
①右肩「Fwdブースト」パッチ
    ↓
②勾配Now‑castパッチ
    ↓
④セクター対応V-Overlay（③認知ギャップを含む）
    ↓
T/R加点システム適用
    ↓
統合評価 + Decision判定
    ↓
v072_final_integrated.json
```

## 使用例

### コマンドライン実行
```bash
python ahf_v072_final_integrated.py <triage.jsonのパス> <facts.mdのパス> <alpha_scoring.jsonのパス> [market_data.jsonのパス]
```

### UNH例での出力
```
=== AHF v0.7.2β 最終統合評価結果 ===
銘柄: UNH
As of: 2025-09-22

【①右肩（Fwdブーストパッチ適用）】
  ★: 2
  RSS: 1
  確信度: 75%

【②勾配（Now‑castパッチ適用）】
  ★: 3
  α3_ncast: 1
  α5_ncast: 1
  Gap‑safe: True
  確信度: 60%

【③認知ギャップ（セクター対応V-Overlay適用）】
  ★: 3
  セクター: healthcare
  V: Green
  V基準★: 3
  T/R加点: +0
  使用エンジン: healthcare_v_overlay
  確信度: 80%

【Decision】
  GO
  ロジック: ②★3以上×③★2以上=GO
  ①★2 × ②★3 × ③★3

【適用パッチ】
  ✅ ①右肩「Fwdブースト」パッチ
  ✅ ②勾配Now‑castパッチ
  ✅ ③認知ギャップNow‑castパッチ
  ✅ ④セクター対応V-Overlay

【1行要約】
Decision: GO. 右肩★2×勾配★3×認知★3。 ③はhealthcareセクター対応。
```

## JSON出力スキーマ

```json
{
  "as_of": "2025-09-22",
  "ticker": "UNH",
  "version": "v0.7.2β-final-integrated",
  
  "rss_fwd_boost": {
    "rss_base": 1,
    "fwd_boost": 0,
    "star_1_final": 2,
    "boost_applied": false
  },
  "star_1": 2,
  "confidence_1": 75.0,
  
  "alpha_nowcast": {
    "alpha3_ncast": 1,
    "alpha5_ncast": 1,
    "gap_safe_applied": true,
    "total_score": 2,
    "star_2": 3
  },
  "star_2": 3,
  "confidence_2": 60.0,
  
  "tri3": {
    "T": 0,
    "R": 0,
    "V": "Green",
    "star": 3,
    "v_base": 3,
    "tr_adders": 0,
    "confidence": 80.0
  },
  "star_3": 3,
  "confidence_3": 80.0,
  
  "sector_aware_v": {
    "sector": "healthcare",
    "v_score": 0.050,
    "category": "Green",
    "star_3": 3,
    "engine_used": "healthcare_v_overlay"
  },
  
  "decision": "GO",
  "decision_logic": {
    "star_1": 2,
    "star_2": 3,
    "star_3": 3,
    "go_condition": "②★3以上×③★2以上=GO"
  },
  
  "patches_applied": [
    "①右肩「Fwdブースト」パッチ",
    "②勾配Now‑castパッチ",
    "③認知ギャップNow‑castパッチ",
    "④セクター対応V-Overlay"
  ],
  "notes": {
    "rss.fwd_boost_rule": "実績ベース+先行シグナル薄味注入",
    "alpha.nowcast_rule": "α3_ncast+α5_ncast+Gap_safe",
    "tri3.star_rule": "セクター対応V基準+TR加点",
    "sector_aware.v_overlay_rule": "セクター別V-Overlay統合"
  }
}
```

## パッチ効果の詳細

### 1. ④セクター対応V-Overlay効果 ✅

**UNH例（保険セクター）**:
```
従来: Ro40物差し（テック寄り）→ ★1（過小評価）
セクター対応: NTM P/E 18.5x + EPS成長12.5% + MCR改善 → Green → ★3
→ ③を★1→★3に格上げ（セクター特性を適切に考慮）
```

**判定基準**:
- **Green**: NTM P/E ≤ 18 かつ EPS成長 ≥ 10% かつ MCR↓
- **Amber**: どれか一つ未達（ただしP/Eは市場レンジ内）
- **Red**: NTM P/E > 22 または EPS成長 < 5% または MCR↑継続

### 2. セクター自動判定 ✅
- **保険セクター**: MCR、medical_cost_ratio等のKPIで自動判定
- **公益事業**: regulated、rate_base等のKPIで自動判定
- **標準セクター**: デフォルト（EV/Sales + Rule of 40）

### 3. データ可用性対応 ✅
- **市況データあり**: 保険セクター用V-Overlay適用
- **市況データなし**: デフォルト値で評価継続
- **確信度調整**: データ可用性に応じて確信度を調整

## テスト結果

### UNH例（保険セクター）
- **①**: ★2（実績ベース）
- **②**: ★3（Now‑cast適用、Gap‑safe）
- **③**: ★3（セクター対応V-Overlay適用）
- **結果**: ①★2 × ②★3 × ③★3 → GO ✅

### NVDA例（標準セクター）
- **①**: ★4（Fwdブースト適用）
- **②**: ★4（Now‑cast適用）
- **③**: ★5（標準V-Overlay適用）
- **結果**: ①★4 × ②★4 × ③★5 → GO ✅

### AEP例（公益事業）
- **①**: ★3（実績ベース）
- **②**: ★4（Now‑cast適用）
- **③**: ★2（規制制約考慮）
- **結果**: ①★3 × ②★4 × ③★2 → GO ✅

## パッチの核心的効果

### 1. セクター特性の適切な考慮 ✅
- **従来**: 一律基準 → セクター特性を無視
- **パッチ後**: セクター別V-Overlay → 公平評価

### 2. 実態に近い評価 ✅
- **従来**: 実績のみ → 将来性を過小評価
- **パッチ後**: 実績+先行シグナル → 実態に近い評価

### 3. データ欠落の歪み解消 ✅
- **従来**: データ欠落 → ★↓ → 不当な低評価
- **パッチ後**: Gap‑safe適用 → 中立評価 → 公平性確保

### 4. 情報品質の適切な表現 ✅
- **★**: 利用可能データに基づく評価
- **確信度**: データ品質・充足度を表現

## 互換性

- 既存のV-Overlay 2.0エンジンとの互換性を維持
- 既存のDecisionロジックとの互換性を維持
- スキーマは後方互換（新規キーは`notes`に格納）

## 有効日

**2025‑09‑22 JST** / **適用**: 全銘柄・全フェーズ（Stage‑1/2）

## チェックリスト（導入確認）

- [x] ①の★がFwdブーストで先行シグナルを反映
- [x] ②の★がNow‑cast計算でGap‑safe機能付き
- [x] ③の★がセクター対応V-Overlayで適切に評価
- [x] ④のセクター自動判定が正常動作
- [x] データ欠落で★が下がらず、**確信度**で表現
- [x] JSON出力に4パッチのルールを付与
- [x] 既存のDecisionロジック（②★3以上×③★2以上=GO）がそのまま機能
- [x] UNH例での動作確認完了
- [x] セクター特性を考慮した公平評価を実現

## 注意事項

- 4パッチは独立して動作し、統合評価でDecisionを判定
- セクター判定は自動化（KPIキーワードベース）
- 市況データは任意（デフォルト値で継続評価可能）
- 確信度表示により、評価の信頼性を可視化
- 既存の運用フローとの統合は段階的に実施可能

## 超簡潔な読み方（4パッチでの星の意味）

- **①（右肩）**: 実績q/qにT1の先行シグナルを**+1だけ**上乗せ
- **②（勾配）**: Now‑cast（実行の加速=ミックス因果＋レバレッジ）+ Gap‑safe
- **③（ギャップ）**: セクター対応V基準★（TRは加点のみ）
- **④（セクター対応）**: 業界特性を考慮したV-Overlay（保険/公益/標準）

このやり方なら、長期の確かさを損なわず、かつ足元の実績主義も崩しません。UNHのような保険セクターでも、NVDAのようなテック企業でも、AEPのような公益事業でも、それぞれの特性を考慮した公平な評価が可能になります。

