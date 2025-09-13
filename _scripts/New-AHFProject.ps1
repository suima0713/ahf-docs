# New-AHFProject.ps1 - AHFプロジェクト初期化スクリプト
param([string]$Root = ".\ahf")

Write-Host "=== AHFプロジェクト初期化 ===" -ForegroundColor Green
Write-Host "合言葉: Facts in, balance out." -ForegroundColor Cyan

# ディレクトリ構造作成
$dirs = @("_catalog","_templates","_rules","_ingest","tickers","_scripts")
Write-Host "ディレクトリ構造を作成中..." -ForegroundColor Yellow
$dirs | ForEach-Object { 
    $path = Join-Path $Root $_
    New-Item -ItemType Directory -Force -Path $path | Out-Null
    Write-Host "  ✓ $path" -ForegroundColor Green
}

# テンプレートファイル作成
$tpl = Join-Path $Root "_templates"
Write-Host "テンプレートファイルを作成中..." -ForegroundColor Yellow

# A.yaml
@"
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
"@ | Set-Content (Join-Path $tpl "A.yaml")

# B.yaml
@"
meta: { ticker: XXX, asof: 2025-09-13 }
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
"@ | Set-Content (Join-Path $tpl "B.yaml")

# C.yaml
@"
meta: { ticker: XXX, asof: 2025-09-13 }
tests:
  time_off:            { result: "維持|後退", note: "④無効化時の影響" }
  delay_plus_0_5Q:     { result: "維持|後退", note: "t1/t2 を +0.5Q" }
  alignment_sales_pnl: { result: "整合|逆行", note: "売上↔GM/CF/在庫 の整合" }
"@ | Set-Content (Join-Path $tpl "C.yaml")

# facts.md
@"
# facts (最新が上)
- [YYYY-MM-DD][T1-F|T1-P|T1-C][Core①|Core②|Core③|Time] "逐語一行" (impact: KPI名) <元Docの場所>
"@ | Set-Content (Join-Path $tpl "facts.md")

Write-Host "  ✓ A.yaml, B.yaml, C.yaml, facts.md" -ForegroundColor Green

# カタログファイル作成
$catalog = Join-Path $Root "_catalog"
Write-Host "カタログファイルを作成中..." -ForegroundColor Yellow

"ticker,name,sector,currency,fye_month,default_wacc" | Set-Content (Join-Path $catalog "tickers.csv")
"ticker,asof,6M,1Y,3Y,5Y,decision,delta_irr_bp" | Set-Content (Join-Path $catalog "horizon_index.csv")
"ticker,kpi1,kpi2" | Set-Content (Join-Path $catalog "kpi_watch.csv")

Write-Host "  ✓ tickers.csv, horizon_index.csv, kpi_watch.csv" -ForegroundColor Green

# 運用原則ファイル作成
$rules = Join-Path $Root "_rules"
@"
# AHF運用原則（v0.1/MVP）

## 合言葉
**Facts in, balance out.**

## ブレ止め3か条
1. **①＞②＞③＞④**（④は注釈で"一度だけ"）
2. **出力は常に1ページ**（A/B/C＋Horizon＋KPI×2）
3. **反証を必ず通す**（④無効／t1+0.5Q／売上↔GM/CF/在庫）

## タグ規約
- **証拠**: [T1-F] 法定 / [T1-P] 会社PR / [T1-C] コール補助
- **柱**: [Core①] 右肩上がり / [Core②] 傾きの質 / [Core③] 時間
- **注釈**: [Time] ④（③の文中に一度だけ）

## 運用フロー
1. 素材投入（T1 / facts.md へ1行追加 → A.yaml へ写経）
2. B/C を更新（Horizon・KPI×2・反証3テスト）
3. current/ に反映 → スナップショット
4. 横串（_catalog）を手動追記
"@ | Set-Content (Join-Path $rules "operating_principles.md")

Write-Host "  ✓ operating_principles.md" -ForegroundColor Green

Write-Host "`n=== AHFプロジェクト初期化完了 ===" -ForegroundColor Green
Write-Host "次のステップ:" -ForegroundColor Cyan
Write-Host "  1. git init && git add . && git commit -m 'AHF init'" -ForegroundColor White
Write-Host "  2. pwsh .\ahf\_scripts\Add-AHFTicker.ps1 -Ticker WOLF" -ForegroundColor White
Write-Host "  3. 環境変数設定: `$env:POLYGON_API_KEY = '<YOUR_KEY>'" -ForegroundColor White
