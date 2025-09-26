# New-AHFProject.ps1 - AHFプロジェクト初期化スクリプト（v0.3）
param([string]$Root = ".\ahf")

Write-Host "=== AHFプロジェクト初期化（v0.3 - 最小構成） ===" -ForegroundColor Green
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
meta:
  asof: YYYY-MM-DD

core:
  right_shoulder: []     # ①右肩上がり
  slope_quality: []      # ②傾きの質（ROIC−WACC/ROIIC/FCF）
  time_profile: []       # ③時間

time_annotation:         # ④カタリスト（一度だけ）
  delta_t_quarters: 
  delta_g_pct: 
  window_quarters: 
  note: 
"@ | Set-Content (Join-Path $tpl "A.yaml")

# B.yaml
@"
horizon:
  6M: {verdict: "", ΔIRRbp: }
  1Y: {verdict: "", ΔIRRbp: }
  3Y: {verdict: "", ΔIRRbp: }
  5Y: {verdict: "", ΔIRRbp: }

stance:
  decision: ""           # Go/保留/No-Go
  size: ""              # Low/Med/High
  reason: ""

kpi_watch: [2項目]
  - name: ""
    current: 
    target: 
  - name: ""
    current: 
    target: 
"@ | Set-Content (Join-Path $tpl "B.yaml")

# C.yaml
@"
tests:
  time_off: ""          # 〔Time〕無効化テスト
  delay_plus_0_5Q: ""   # t1+0.5Qテスト
  alignment_sales_pnl: "" # 売上↔GM/CF/在庫の整合
"@ | Set-Content (Join-Path $tpl "C.yaml")

# facts.md
@"
[YYYY-MM-DD][T1-F|T1-P|T1-C][Core①|Core②|Core③|Time] "逐語" (impact: KPI) <src>

タグ規約: 証拠=T1-F/T1-P/T1-C｜柱=Core①/②/③｜注釈=Time（④は一度だけ）
"@ | Set-Content (Join-Path $tpl "facts.md")

Write-Host "  ✓ A.yaml, B.yaml, C.yaml, facts.md" -ForegroundColor Green

# カタログファイル作成
$catalog = Join-Path $Root "_catalog"
Write-Host "カタログファイルを作成中..." -ForegroundColor Yellow

"ticker,name,sector,currency,fye_month,default_wacc" | Set-Content (Join-Path $catalog "tickers.csv")
"ticker,asof,6M,1Y,3Y,5Y,decision,delta_irr_bp" | Set-Content (Join-Path $catalog "horizon_index.csv")
"ticker,kpi1,kpi2" | Set-Content (Join-Path $catalog "kpi_watch.csv")

Write-Host "  ✓ tickers.csv, horizon_index.csv, kpi_watch.csv" -ForegroundColor Green

# 運用原則ファイル作成（既存ファイルをコピー）
$rules = Join-Path $Root "_rules"
if (Test-Path "_rules\operating_principles.md") {
    Copy-Item "_rules\operating_principles.md" (Join-Path $rules "operating_principles.md")
    Write-Host "  ✓ operating_principles.md（既存からコピー）" -ForegroundColor Green
} else {
    Write-Host "  ⚠ operating_principles.mdが見つかりません" -ForegroundColor Yellow
}

Write-Host "  ✓ operating_principles.md" -ForegroundColor Green

Write-Host "`n=== AHFプロジェクト初期化完了（v0.3 - 最小構成） ===" -ForegroundColor Green
Write-Host "次のステップ:" -ForegroundColor Cyan
Write-Host "  1. 環境変数設定:" -ForegroundColor White
Write-Host "     `$env:AHF_DATASOURCE = 'auto'" -ForegroundColor Gray
Write-Host "     `$env:AHF_INTERNAL_BASEURL = '<url>'" -ForegroundColor Gray
Write-Host "     `$env:AHF_INTERNAL_TOKEN = '<token>'" -ForegroundColor Gray
Write-Host "     `$env:POLYGON_API_KEY = '<key>'" -ForegroundColor Gray
Write-Host "  2. 銘柄追加: pwsh .\ahf\_scripts\Add-AHFTicker.ps1 -Ticker WOLF" -ForegroundColor White
Write-Host "  3. データ取得: Get-AHFPrices -Ticker WOLF -From 2024-01-01 -To 2024-12-31" -ForegroundColor White
