# AHF v0.7.2β — ③認知ギャップ Now‑castパッチ（適用済み 2025‑09‑22 JST)

## 概要

③「認知ギャップ（TRI‑3＋V‑Overlay 2.0）」の星付けをナウキャスト化し、*データ欠落≠低評価* の歪みを解消しました。

## 主な変更点

### 1. V基準の星付け
- **基準★はVのみ**：Green→★3／Amber→★2／Red→★1（ヒステリシス据置）
- 従来のT/Rベースの星付けから変更

### 2. T/R加点システム
- **T/Rは加点のみ**：T+R≥3 → +1★、T+R=4 → さらに +1★（上限★5）
- データ欠落で★が下がらない設計

### 3. 確信度システム
- **確信度**で情報充足度を表現（T/Rの弱さ・未整合＝確信度↓）
- 計算式：`Base60% + Bridge整合+10pp + (CL↑&CA↓)+5pp + ガイダンス明瞭+5pp − 新四半期未着地−10pp`
- 50–95%でクリップ

### 4. 既存機能維持
- **ボーナス★**（α3=2 かつ α5=2 → +1★、上限★5）維持
- **Decisionロジック**（②★3以上×③★2以上=GO）は変更なし

## ファイル構成

### 新規ファイル
- `ahf_tri3_v_overlay_v072.py` - メイン実装
- `test_decision_logic_v072.py` - テストスクリプト
- `test_*_sample.json` - テストデータ

### JSON出力スキーマ
```json
{
  "tri3": {
    "T": 0|1|2,
    "R": 0|1|2,
    "V": "Green|Amber|Red",
    "star": 1..5,
    "bonus_applied": true|false
  },
  "valuation_overlay": {
    "status": "Green|Amber|Red",
    "v_score": float,
    "ev_sales": float,
    "rule_of_40": float,
    "hysteresis_applied": bool
  },
  "confidence": 50.0..95.0,
  "star_calculation": {
    "v_base": 1|2|3,
    "tr_adders": 0|1|2,
    "alpha_bonus": 0|1,
    "final": 1..5
  },
  "notes": {
    "tri3.star_rule": "V_base_plus_TR_adders"
  }
}
```

## 使用例

### コマンドライン実行
```bash
python ahf_tri3_v_overlay_v072.py <triage.jsonのパス> <alpha_scoring.jsonのパス>
```

### テスト実行
```bash
python test_decision_logic_v072.py
```

## テスト結果

### テストケース1: 完全なデータ（V=Green、T+R=4）
- **結果**: ★5 (V基準3+TR加点2+αボーナス1)
- **確信度**: 70%
- **Decision**: GO ✅

### テストケース2: ARRY例（V=Green、T+R=2）
- **結果**: ★4 (V基準3+TR加点0+αボーナス1)
- **確信度**: 60%
- **Decision**: GO ✅

### テストケース3: Amber例（V=Amber、T+R=3）
- **結果**: ★4 (V基準2+TR加点1+αボーナス1)
- **確信度**: 60%
- **Decision**: GO ✅

### テストケース4: Red例（V=Red、T+R=1）
- **結果**: ★2 (V基準1+TR加点0+αボーナス1)
- **確信度**: 50%
- **Decision**: GO ✅（境界値）

## 互換性

- 既存のV-Overlay 2.0エンジンとの互換性を維持
- 既存のDecisionロジックとの互換性を維持
- スキーマは後方互換（新規キーは`notes`に格納）

## 有効日

**2025‑09‑22 JST** / **適用**: 全銘柄・全フェーズ（Stage‑1/2）

## チェックリスト（導入確認）

- [x] ③の★がV基準になっている
- [x] T/R欠落で★が下がらず、**確信度**で表現されている
- [x] JSON出力に `notes.tri3.star_rule`（任意）を付与
- [x] 既存のDecisionロジック（②★3以上×③★2以上=GO）がそのまま機能

## 注意事項

- このパッチは③認知ギャップの評価ロジックのみを変更
- ②傾きの質の評価ロジックは変更なし
- 既存の運用フローとの統合は別途実装が必要

