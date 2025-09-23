# AHF High Contrast Evaluation v0.7.1c
## ハイコントラスト版星判定システム

### 概要

「メリハリ不足」を解消しつつ、T1だけで即決できるハイコントラスト版星判定システム。①RSS、②α3/α5点数化、③TRI-3+V-Overlay 2.0の組み合わせで即時判定を可能にする。

### 主要特徴

1. **即時判定**: 次決算待ちを強制しないNow-castルール
2. **ハイコントラスト**: ★1〜★5の使い切りでメリハリ確保
3. **T1ベース**: 追加の期待値や主観は一切入れない
4. **実務適用**: 星の組合せで即アクション決定

## システム構成

### ①長期右肩（★1–5）— Right-Shoulder Score（RSS）

```
RSS = 2·I(DR_qoq ≥ +8% or Bookings_qoq ≥ +10%)
    + 1·I(DR_qoq ∈ [0,+8%))
    + 1·I(Paid↑ or ARPU↑)
    + 1·I(CL↑ and CA↓)
    − 1·I(DR_qoq < 0 or (Paid↓ and ARPU↓))
```

**星割当**: RSS≥4→★5／=3→★4／=2→★3／=1→★2／≤0→★1

**ガード**: DR 2Q連続減 で★≤2に即降格

### ②勾配（★1–5）— α3/α5の点数化

#### α3_score（0/1/2）
- **2点**: |GM_drift| ≤ 0.2pp かつ Residual ≤ $8M
- **1点**: |GM_drift| ≤ 0.8pp かつ Residual ≤ $8M かつ MD&A逐語で一次説明
- **0点**: 上記以外

#### α5_score（0/1/2）
- **2点**: median(OpEx_grid) − OpEx_actual ≤ −$3M
- **1点**: −$3M < 差 ≤ −$1M かつ 効率フレーズ逐語
- **0点**: 上記以外

**星割当（ハイコントラスト）**: 合計S=α3+α5：4→★5、3→★4、2→★3、1→★2、0→★1

### ③認知ギャップ（★1–5）— TRI-3＋V-Overlay 2.0

**T/R基礎★**: 0→1★、1–2→2★、3→3★、4→4★

**V-Overlay 2.0調整**:
- Amber → ★−1
- Red → ★−1 & ★上限=3

**ボーナス**: α3=2 かつ α5=2 の時のみ +1★（上限★5）

## 使用方法

### 統合実行

```bash
python3 ahf/_scripts/ahf_high_contrast_evaluation.py DUOL
```

### 個別実行

```bash
# ①RSS算定
python3 ahf/_scripts/ahf_rss_calculator.py tickers/DUOL/current/triage.json

# ②αスコア算定
python3 ahf/_scripts/ahf_alpha_scoring.py tickers/DUOL/current/triage.json tickers/DUOL/current/facts.md

# ③TRI-3+V-Overlay算定
python3 ahf/_scripts/ahf_tri3_v_overlay.py tickers/DUOL/current/triage.json tickers/DUOL/current/alpha_scoring.json

# ④アクションガイド生成
python3 ahf/_scripts/ahf_action_guide.py DUOL
```

## 実務ガイド（星の組合せで即アクション）

### 推奨アクション

| ①RSS | ②α3/α5 | ③TRI-3+V | 推奨 | サイズ | 理由 |
|------|---------|-----------|------|--------|------|
| ★4-5 | ★4-5 | ★2+ | BUY | Medium | 高品質+適正価格 |
| ★4-5 | ★4-5 | ★1 | HOLD | None | 高品質+高価格 |
| ★4-5 | ★4-5 | ★2+ (Red) | BUY | Small | 高品質+価格リスク高 |
| ★1-2 | - | - | AVOID | None | 品質不足 |
| - | ★1 | - | AVOID | None | 収益性不足 |

### リスク管理

- **③Red**: 最大★=3で上限管理（プレミアム剥落リスク高）
- **①★1-2 or ②★1**: 見送り/縮小（TWがなくても）
- **高品質+適正価格**: 小さくIN→証拠で追撃

## 設定ファイル

### thresholds.yaml

```yaml
stage1:
  rs_dr_high: 8.0                    # DR_qoq ≥ +8% で高成長
  rs_bookings_high: 10.0             # Bookings_qoq ≥ +10% で高成長
  dr_guard_threshold: 2               # DR 2Q連続減で★≤2に即降格

stage2:
  alpha3:
    alpha3_near_pp: 0.8               # ≤0.8pp で「説明付き近接」評価
  alpha5:
    alpha5_weak_band: [-3000000, -1000000]  # -$3M < 差 ≤ -$1M で「弱い改善」
    efficiency_phrases: [
      "operating leverage",
      "operating discipline", 
      "hiring pacing",
      "cost discipline",
      "cost control",
      "efficiency improvements",
      "operational efficiency"
    ]
```

## 出力例

### 統合評価結果

```
=== AHF High Contrast Evaluation Results (v0.7.1c) ===
Ticker: DUOL
Pipeline: high_contrast_v071c

実行ステップ:
  ✓ RSS: success
  ✓ Alpha: success
  ✓ TRI3_V: success
  ✓ Action: success

評価サマリー:
  ①RSS: 3 → ★4
  ②α3/α5: α3=1, α5=2 → ★3
  ③TRI-3+V: 基礎★3 → 最終★3 (Amber)
  推奨アクション: BUY Small
  理由: 高品質だが価格リスク高（③Red）
```

### アクションガイド結果

```
=== AHF Action Guide Results (v0.7.1c) ===
Ticker: DUOL
As of: 2024-01-15

星判定:
  ①RSS: ★4
  ②α3/α5: ★3
  ③TRI-3+V: ★3
  V区分: Amber

アクション:
  推奨: BUY
  サイズ: Small
  理由: 高品質だが価格リスク高（③Red）
  リスク: High

次のステップ:
  - 小さくIN
  - 価格監視強化
  - 上限管理（★3以下）

リスク評価:
  レベル: High
  リスク数: 1
  リスク:
    - プレミアム剥落リスク高（V-Overlay Red）
  対策:
    - 上限管理（★3以下）

サマリー: DUOL: BUY Small (高品質だが価格リスク高（③Red）)
```

## 重要なポイント

1. **T1逐語のみ使用**: 見出し・目次は不可、≤40語
2. **機械判定**: 追加の期待値や主観は一切入れない
3. **即時決定**: 次決算待ちを強制しない
4. **ハイコントラスト**: ★1〜★5の使い切りでメリハリ確保
5. **実務適用**: 星の組合せで即アクション決定

## ファイル構成

- `ahf_rss_calculator.py`: ①RSS算定
- `ahf_alpha_scoring.py`: ②α3/α5算定
- `ahf_tri3_v_overlay.py`: ③TRI-3+V-Overlay算定
- `ahf_action_guide.py`: アクションガイド生成
- `ahf_high_contrast_evaluation.py`: 統合実行
- `thresholds.yaml`: 閾値設定

## 注意事項

- 全ての説明は日本語で行う
- カーソルルールは常時遵守
- 変更時は必ずこのファイルを更新
- 新しいルール追加時はChair承認必須
