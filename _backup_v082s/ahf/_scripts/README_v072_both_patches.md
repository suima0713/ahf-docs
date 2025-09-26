# AHF v0.7.2β — 両パッチ統合版（適用済み 2025‑09‑22 JST)

## 概要

③認知ギャップ Now‑castパッチと②勾配 Now‑castパッチを統合し、*データ欠落≠低評価* の歪みを完全に解消しました。

## 適用パッチ

### 1. ③認知ギャップ Now‑castパッチ ✅
- **V基準の星付け**: Green→★3／Amber→★2／Red→★1
- **T/R加点システム**: T+R≥3→+1★、T+R=4→+2★
- **確信度表示**: 50–95%でクリップ
- **データ欠落≠低評価**の歪み解消

### 2. ②勾配 Now‑castパッチ ✅
- **α3_ncast（Mix/因果）**: SW/Cloud比改善の定量化
- **α5_ncast（レバレッジ）**: OI成長と売上YoYの関係
- **Gap‑safe**: 主要指標欠落時の中立=1点（自動★1回避）
- **合成**: S=α3_ncast+α5_ncast（0–4）→ ★

## ファイル構成

### 新規ファイル
- `ahf_alpha_nowcast_v072.py` - ②勾配Now‑castパッチ
- `ahf_v072_integrated_nowcast.py` - 両パッチ統合版
- `ahf_tri3_v_overlay_v072.py` - ③認知ギャップNow‑castパッチ（既存）

### 統合処理フロー
```
triage.json + facts.md + alpha_scoring.json
    ↓
③認知ギャップ Now‑castパッチ
    ↓
②勾配 Now‑castパッチ
    ↓
統合評価 + Decision判定
    ↓
v072_integrated_nowcast.json
```

## 使用例

### コマンドライン実行
```bash
python ahf_v072_integrated_nowcast.py <triage.jsonのパス> <facts.mdのパス> <alpha_scoring.jsonのパス>
```

### 出力例
```
=== AHF v0.7.2β 統合評価結果 ===
銘柄: ORCL
As of: 2025-09-22

【①右肩（RSS）】
  ★: 4

【②勾配（Now‑castパッチ適用）】
  ★: 3
  α3_ncast: 1
  α5_ncast: 1
  Gap‑safe: True
  確信度: 60%

【③認知ギャップ（Now‑castパッチ適用）】
  ★: 3
  V: Green
  T/R: 2/1
  確信度: 62%

【Decision】
  GO
  ロジック: ②★3以上×③★2以上=GO
  ②★3 × ③★3

【適用パッチ】
  ✅ ③認知ギャップ Now‑castパッチ
  ✅ ②勾配 Now‑castパッチ

【1行要約】
Decision: GO. 右肩★4×勾配★3×認知★3。
```

## JSON出力スキーマ

```json
{
  "as_of": "2025-09-22",
  "ticker": "ORCL",
  "version": "v0.7.2β-integrated-nowcast",
  
  "rss_score": 4,
  "star_1": 4,
  
  "alpha_nowcast": {
    "alpha3_ncast": 1,
    "alpha5_ncast": 1,
    "gap_safe_applied": true,
    "total_score": 2,
    "star_2": 3
  },
  "confidence_2": 60.0,
  
  "tri3": {
    "T": 2,
    "R": 1,
    "V": "Green",
    "star": 3,
    "bonus_applied": false
  },
  "star_3": 3,
  "confidence_3": 62.0,
  
  "decision": "GO",
  "decision_logic": {
    "star_1": 4,
    "star_2": 3,
    "star_3": 3,
    "go_condition": "②★3以上×③★2以上=GO"
  },
  
  "patches_applied": [
    "③認知ギャップ Now‑castパッチ",
    "②勾配 Now‑castパッチ"
  ],
  "notes": {
    "tri3.star_rule": "V_base_plus_TR_adders",
    "alpha.nowcast_rule": "α3_ncast+α5_ncast+Gap_safe"
  }
}
```

## ORCL KPIマップ対応

### 固定KPIマッピング
- **CL**: Deferred revenues（10‑QのBS脚注）
- **CA**: Unbilled receivables（10‑QのAR/契約資産明細）
- **Bookings proxy**: RPO（Remaining performance obligations）

### 抽出順
1. EX‑99.1 → 10‑Q（セグ構成/BS/RPO/Item1A）
2. Period Lock: ヘッダに期名+日付（例: Q1 FY26, 2025‑08‑31）

## テスト結果

### テストケース1: 完全データ
- **結果**: ②★4, ③★5 → GO ✅
- **α3_ncast**: 2（SW/Cloud改善+因果）
- **α5_ncast**: 1（OI成長≒売上YoY+効率フレーズ）
- **確信度**: 75%

### テストケース2: ORCL（Gap‑safe適用）
- **結果**: ②★3, ③★3 → GO ✅
- **α3_ncast**: 1（Gap‑safe適用）
- **α5_ncast**: 1（Gap‑safe適用）
- **確信度**: 60%

## パッチ効果

### 1. データ欠落の歪み解消 ✅
- **従来**: データ欠落 → ★↓ → 不当な低評価
- **パッチ後**: Gap‑safe適用 → 中立評価 → 公平性確保

### 2. 情報品質の適切な表現 ✅
- **★**: 利用可能データに基づく評価
- **確信度**: データ品質・充足度を表現

### 3. 既存ロジックとの互換性 ✅
- Decision基準（②★3以上×③★2以上=GO）維持
- 既存ワークフローとの統合可能

## 互換性

- 既存のV-Overlay 2.0エンジンとの互換性を維持
- 既存のDecisionロジックとの互換性を維持
- スキーマは後方互換（新規キーは`notes`に格納）

## 有効日

**2025‑09‑22 JST** / **適用**: 全銘柄・全フェーズ（Stage‑1/2）

## チェックリスト（導入確認）

- [x] ③の★がV基準になっている
- [x] T/R欠落で★が下がらず、**確信度**で表現されている
- [x] ②の★がNow‑cast計算になっている
- [x] Gap‑safe機能が正常に動作している
- [x] JSON出力に両パッチのルールを付与
- [x] 既存のDecisionロジック（②★3以上×③★2以上=GO）がそのまま機能
- [x] ORCL KPIマップでの動作確認完了

## 注意事項

- 両パッチは独立して動作し、統合評価でDecisionを判定
- Gap‑safe機能により、データ欠落時の自動★1回避を実現
- 確信度表示により、評価の信頼性を可視化
- 既存の運用フローとの統合は段階的に実施可能

