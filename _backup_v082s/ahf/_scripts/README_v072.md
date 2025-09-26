# AHF v0.7.2 - T1限定・MVP-4+／Star整数＋高コントラスト

## 概要

v0.7.1からの主変更：①の星決定をRSSで高コントラスト化／②をNow-cast点数化（α3・α5）／③のV-Overlayを2.0に刷新（AND＋<＋アップグレード厳格化）。時間軸は引き続き撤廃。

## 主要変更点

### 1. ①長期右肩（高コントラストRSS）

```
RSS = +2·I(DR_qoq ≥ +8%  or  Bookings_qoq ≥ +10%)
    +1·I(DR_qoq ∈ [0,+8%))
    +1·I(Paid↑ or ARPU↑)
    +1·I(CL↑ and CA↓)
    −1·I(DR_qoq < 0 or (Paid↓ and ARPU↓))
```

**星割当**: RSS≥4→★5／=3→★4／=2→★3／=1→★2／≤0→★1

**自動降格**: DR 2Q連続減 で ★≤2 に即降格

### 2. ②右肩の勾配（Now-cast点数化）

#### α3_score（0/1/2）
- **2点**: |GM_drift| ≤ 0.2pp かつ Residual_GP ≤ $8M
- **1点**: |GM_drift| ≤ 0.8pp かつ Residual_GP ≤ $8M かつ MD&Aの一次説明逐語
- **0点**: 上記以外

#### α5_score（0/1/2）
- **2点**: median(OpEx_grid) − OpEx_actual ≤ −$3M
- **1点**: −$3M < 差 ≤ −$1M かつ 効率フレーズ逐語
- **0点**: 上記以外

**星割当**: 合計S=α3+α5：S=4→★5、3→★4、2→★3、1→★2、0→★1

### 3. ③認知ギャップ＝TRI-3＋V-Overlay 2.0

**入力（3点）**:
- T：T1因果の明瞭度（0–2）
- R：T1シグナルの社会化度（0–2）
- V：バリュエーション織込み度

**V-Overlay 2.0**:
- Green：EV/Sales(Fwd) ≤ 10× かつ Rule-of-40 ≥ 40
- Amber：10×＜EV/Sales(Fwd) ≤ 14× または Ro40 ∈[35,40)
- Red：EV/Sales(Fwd) > 14× または Ro40 < 35

**ヒステリシス**: AND＋厳密不等号、アップグレード1.2倍

**星反映**: Green=据置／Amber=★−1（下限★1）／Red=★−1 & ★上限=3

## 使用方法

### 統合実行

```bash
python3 ahf/_scripts/ahf_v072_integrated.py DUOL
```

### 個別実行

```bash
# ①RSS算定（高コントラスト）
python3 ahf/_scripts/ahf_rss_calculator.py tickers/DUOL/current/triage.json

# ②αスコア算定（Now-cast点数化）
python3 ahf/_scripts/ahf_alpha_scoring.py tickers/DUOL/current/triage.json tickers/DUOL/current/facts.md

# ③TRI-3+V-Overlay 2.0算定
python3 ahf/_scripts/ahf_tri3_v_overlay.py tickers/DUOL/current/triage.json tickers/DUOL/current/alpha_scoring.json

# ④AnchorLint v1実行
python3 ahf/_scripts/ahf_anchor_lint.py tickers/DUOL/current/triage.json

# ⑤自動チェック実行
python3 ahf/_scripts/ahf_auto_checks.py tickers/DUOL/current/triage.json

# ⑥アクションガイド生成
python3 ahf/_scripts/ahf_action_guide.py DUOL
```

## MVP-4+スキーマ拡張

### 新規フィールド

- `rss_score`: RSSスコア
- `alpha3_score`: α3スコア（0-2）
- `alpha5_score`: α5スコア（0-2）
- `direction_prob_up_pct`: 上向き確率
- `direction_prob_down_pct`: 下向き確率
- `gate_color`: ゲート色（Green/Amber/Red）
- `anchor_backup`: アンカーバックアップ情報
- `find_path`: 検索パス
- `gap_reason`: ギャップ理由
- `dual_anchor_status`: 二重アンカーステータス
- `auto_checks`: 自動チェック結果
- `tri3`: TRI-3結果
- `valuation_overlay`: バリュエーションオーバーレイ
- `interrupts`: 割り込みリスト

### スキーマファイル

- `ahf/schemas/mvp4_plus_schema.json`: MVP-4+スキーマ定義

## 数値検算ガードレール

### 必須検証

1. **GM乖離≤0.2pp**
2. **残差GP≤$8,000k**
3. **OT∈[46.8,61.0]**
4. **α4ゲート≥11.0**
5. **α5数理検証**: OpEx = Rev × NG-GM − KPI

### アンカー要件

- **#:~:text= 必須**
- **逐語≤25語**
- **アンカーバックアップ必須**
- **二重アンカーステータス管理**

## 出力例

### 統合評価結果

```
=== AHF v0.7.2 Integrated Evaluation Results ===
Ticker: DUOL
Version: v0.7.2
Pipeline: T1限定・MVP-4+／Star整数＋高コントラスト

実行ステップ:
  ✓ RSS: success
  ✓ Alpha: success
  ✓ TRI3_V: success
  ✓ AnchorLint: success
  ✓ AutoChecks: success
  ✓ Action: success

v0.7.2評価サマリー:
  ①RSS: 3 → ★4
  ②α3/α5: α3=1, α5=2 → ★3
  ③TRI-3+V: 基礎★3 → 最終★3 (Amber)
  自動チェック: α4=True, α5=True, アンカー=True
  推奨アクション: BUY Small
  理由: 高品質だが価格リスク高（③Red）
```

## 重要なポイント

1. **T1限定**: 追加の期待値や主観は一切入れない
2. **Star整数**: ★1〜★5の整数判定
3. **高コントラスト**: メリハリのある判定
4. **Now-cast**: 次決算待ちを強制しない
5. **自動チェック**: 数値検算ガードレール必須
6. **アンカー管理**: #:~:text= 必須、二重アンカー対応

## ファイル構成

- `ahf_rss_calculator.py`: ①RSS算定
- `ahf_alpha_scoring.py`: ②α3/α5算定
- `ahf_tri3_v_overlay.py`: ③TRI-3+V-Overlay算定
- `ahf_anchor_lint.py`: AnchorLint v1実行
- `ahf_auto_checks.py`: 自動チェック実行
- `ahf_action_guide.py`: アクションガイド生成
- `ahf_v072_integrated.py`: 統合実行
- `mvp4_plus_schema.json`: MVP-4+スキーマ

## 注意事項

- 全ての説明は日本語で行う
- カーソルルールは常時遵守
- 変更時は必ずこのファイルを更新
- 新しいルール追加時はChair承認必須
