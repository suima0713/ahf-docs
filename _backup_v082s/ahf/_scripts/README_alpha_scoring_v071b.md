# AHF Alpha Scoring v0.7.1b - ②勾配ルーブリック Now-cast対応

## 概要

②勾配ルーブリックを「いま見えるT1だけで即決できる形」に微修正。次決算待ちを強制しないNow-castルールを実装。

## 主要変更点

### 1. 機械判定の二段階→点数化

#### α3_score（0/1/2）
- **2点**: |GM_drift| ≤ 0.2pp かつ Residual ≤ $8M（機械PASS）
- **1点**: |GM_drift| ≤ 0.8pp かつ Residual ≤ $8M かつ T1逐語で一次説明あり
- **0点**: 上記以外

#### α5_score（0/1/2）
- **2点**: median(OpEx_grid) − OpEx_actual ≤ −$3M（改善の素地あり）
- **1点**: −$3M < 差 ≤ −$1M かつ T1に運用効率フレーズ
- **0点**: 上記以外

### 2. ★2決定（機械）

| α3_score | α5_score | ★2判定 |
|----------|----------|--------|
| 2        | 2        | 4★     |
| 2        | 1        | 3★     |
| 1        | 2        | 3★     |
| 2        | 0        | 2★     |
| 1        | 1        | 2★     |
| 1        | 0        | 1★     |
| 0        | 1        | 1★     |
| 0        | 0        | 1★据え置き |

### 3. Now-cast再計算

- 8-K/Ex.99.1検出時は②だけ再計算（①③は従来ロジック）
- T1の範囲に8-K/Ex.99.1（ガイダンス更新）を含める
- 過度な期待値や主観は一切入れない

## 使用方法

### 1. αスコア算定

```bash
python3 ahf/_scripts/ahf_alpha_scoring.py tickers/DUOL/current/triage.json tickers/DUOL/current/facts.md
```

### 2. Now-cast再計算

```bash
python3 ahf/_scripts/ahf_nowcast_recalc.py DUOL
```

### 3. 設定ファイル

`ahf/config/thresholds.yaml`に以下が追加済み：

```yaml
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
      "efficiency improvements",
      "operational efficiency"
    ]
```

## 出力例

### αスコア算定結果

```
=== AHF Alpha Scoring Results (v0.7.1b) ===
As of: 2024-01-15

α3_score: 1 (GM drift: 0.72pp, Residual: $2.1M)
α5_score: 2 (OpEx diff: $-3.6M)
★2判定: 3 (α3=1, α5=2 → ★3)
```

### Now-cast再計算結果

```
=== AHF Now-cast Recalculation Results (v0.7.1b) ===
Ticker: DUOL
As of: 2024-01-15
Updates detected: 2

α3_score: 1
α5_score: 2
★2判定: 3
B.yaml updated: true

検出された更新:
  - 2024-01-14: 8-K
  - 2024-01-15: Ex.99.1
```

## 重要なポイント

1. **T1逐語のみ使用**: 見出し・目次は不可、≤40語
2. **機械判定**: 追加の期待値や主観は一切入れない
3. **即時決定**: 次決算待ちを強制しない
4. **Interrupt発火**: A3_UNEXPLAINED等は従来どおり

## ファイル構成

- `ahf_alpha_scoring.py`: α3_score/α5_score算定
- `ahf_nowcast_recalc.py`: Now-cast再計算
- `thresholds.yaml`: 閾値設定
- `alpha_scoring.json`: 算定結果
- `nowcast_recalc.json`: 再計算結果

## 注意事項

- 全ての説明は日本語で行う
- カーソルルールは常時遵守
- 変更時は必ずこのファイルを更新
