# AHF（Analytic Homeostasis Framework）プロジェクト指示（v0.1 / MVP）

## 0) 目的と原則（北極星）

**目的**: 一次情報（T1）をA/B/Cマトリクスに流し、①右肩上がり × ②傾きの質 × ③時間を"一体で"評価。④（カタリスト）は③の文中に〔Time〕注釈で一度だけ。

**出力**: 銘柄ごとに1ページ（A=材料/B=結論/Horizon/KPI×2/C=反証）。

**優先度**: ①＞②＞③＞④。**複雑さは"枠内に圧縮"**して勝つ。

## 1) ツール前提

- **Cursor**: Git初期化・PRレビュー・タスク実行に使用
- **PowerShell 7+**: `$PSVersionTable.PSVersion` で確認
- **Polygon.io**: APIキー（環境変数 `POLYGON_API_KEY`）を取得・設定

例：`$env:POLYGON_API_KEY = "<YOUR_POLYGON_API_KEY>"`

## 2) ディレクトリ構造（Git ルート）

```
/ahf/
├── _catalog/            # 横串インデックス（全銘柄の要約CSV）
├── _templates/          # A/B/C ひな形と facts.md 雛形
├── _rules/              # 運用原則（①>②>③>④、タグ規約 など）
├── _ingest/             # 新規素材（PDF/8-K等）の仮置き
├── _scripts/            # PowerShell自動化スクリプト
└── tickers/
    └── <TICKER>/
        ├── attachments/     # 一次PDFやAPI生データ
        ├── snapshots/
        │   └── YYYY-MM-DD/
        │       ├── A.yaml
        │       ├── B.yaml
        │       ├── C.yaml
        │       └── facts.md
        └── current/         # 最新スナップショットのコピー
```

## 3) ファイル雛形（_templates/）

### A.yaml（A＝集める／T1のみ）

```yaml
meta: { ticker: XXX, asof: 2025-09-13 }
core:
  right_shoulder:   # ① 右肩上がり（逐語1行×最大3）
    - { date: YYYY-MM-DD, tag: T1-F|T1-P|T1-C, verbatim: "...", impact_kpi: ["Revenue"], note: "" }
  slope_quality:    # ② 傾きの質（ROIC−WACC/FCF/ROIIC）
    - { date: YYYY-MM-DD, tag: T1-F, verbatim: "...", impact_kpi: ["FCF","ROIC"] }
  time_profile:     # ③ t1/t2＋制約
    - { date: YYYY-MM-DD, tag: T1-P, verbatim: "...", impact_kpi: ["GM","Capacity"] }
time_annotation:    # ④〔Time〕＝"注釈"は一度だけ（外付け係数は使わない）
  delta_t_quarters: 0        # ±0.25〜0.5Q
  delta_g_pct: 0             # 必要時のみ ±5–10%
  window_quarters: 2
  note: "近接イベント（例：Q3ガイドなど）"
```

### B.yaml（B＝まとめる／Horizon＋結論＋KPI×2）

```yaml
horizon:
  six_months:   { verdict: "はい|△|いいえ", delta_irr_bp: 0, note: "" }
  one_year:     { verdict: "はい|△|いいえ", delta_irr_bp: 0, note: "" }
  three_years:  { verdict: "はい|△|いいえ", delta_irr_bp: 0, note: "" }
  five_years:   { verdict: "はい|△|いいえ", delta_irr_bp: 0, note: "" }
stance:
  decision: "Go|保留|No-Go"
  size: "S|M|L"             # ボラで配分
  reason: "主語＝①②。③は___で検証。"
kpi_watch:
  - "KPI①（質：GM/FCF 等）"
  - "KPI②（実行：在庫/未稼働/入金 等）"
```

### C.yaml（C＝反証／3テスト固定）

```yaml
tests:
  time_off:            { result: "維持|後退", note: "④無効化時の影響" }
  delay_plus_0_5Q:     { result: "維持|後退", note: "t1/t2 を +0.5Q" }
  alignment_sales_pnl: { result: "整合|逆行", note: "売上↔GM/CF/在庫 の整合" }
```

### facts.md（原子Fact・逆時系列）

```markdown
# facts (最新が上)
- [YYYY-MM-DD][T1-F|T1-P|T1-C][Core①|Core②|Core③|Time] "逐語一行" (impact: KPI名) <元Docの場所>
```

## 4) PowerShell スクリプト（/ahf/_scripts/ 推奨）

### 4.1 初期化：プロジェクト骨組み
`New-AHFProject.ps1`

### 4.2 銘柄の骨組み作成
`Add-AHFTicker.ps1`

### 4.3 ポリゴン：価格データ取得（例：日足）
`Get-PolygonBars.ps1`

### 4.4 スナップショット作成（差分を残す）
`New-AHFSnapshot.ps1`

## 5) 運用フロー（Cursor での実務手順）

### 初期化（初回だけ）
```powershell
pwsh .\ahf\_scripts\New-AHFProject.ps1
git init && git add . && git commit -m "AHF init"
```

### 銘柄追加
```powershell
pwsh .\ahf\_scripts\Add-AHFTicker.ps1 -Ticker WOLF
```

### 素材投入（T1 / facts.md へ1行追加 → A.yaml へ写経）
逐語1行・日付・タグ（T1-F/P/C）・影響KPI・[Core①/②/③ or Time] を記録。

### 価格データ取得（任意）
```powershell
pwsh .\ahf\_scripts\Get-PolygonBars.ps1 -Ticker WOLF -From 2024-09-01 -To 2025-09-13 -Timespan day
```

### B/C を更新（Horizon・KPI×2・反証3テスト）→ current/ に反映 → スナップショット
```powershell
pwsh .\ahf\_scripts\New-AHFSnapshot.ps1 -Ticker WOLF
```

### 横串（_catalog）を手動追記（MVP）
`horizon_index.csv` に `ticker,asof,6M,1Y,3Y,5Y,decision,delta_irr_bp` を1行追加。
（将来は YAML パースして自動更新に拡張）

## 6) タグ規約（最小）

- **証拠**: [T1-F] 法定 / [T1-P] 会社PR / [T1-C] コール補助
- **柱**: [Core①] 右肩上がり / [Core②] 傾きの質 / [Core③] 時間
- **注釈**: [Time] ④（③の文中に一度だけ）

## 7) 守ること（ブレ止め3か条）

1. **①＞②＞③＞④**（④は注釈で"一度だけ"）
2. **出力は常に1ページ**（A/B/C＋Horizon＋KPI×2）
3. **反証を必ず通す**（④無効／t1+0.5Q／売上↔GM/CF/在庫）
