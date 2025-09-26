# Add-AHFTicker.ps1 - 銘柄の骨組み作成スクリプト（v0.3）
param(
    [Parameter(Mandatory)][string]$Ticker,
    [string]$Root = ".\ahf"
)

Write-Host "=== AHF銘柄追加（v0.3 - 最小構成）: $Ticker ===" -ForegroundColor Green

# 銘柄ディレクトリ構造作成
$tickerRoot = Join-Path $Root "tickers\$Ticker"
$paths = @("attachments","snapshots","current")
Write-Host "ディレクトリ構造を作成中..." -ForegroundColor Yellow

$paths | ForEach-Object { 
    $path = Join-Path $tickerRoot $_
    New-Item -ItemType Directory -Force -Path $path | Out-Null
    Write-Host "  ✓ $path" -ForegroundColor Green
}

# providersディレクトリ構造作成（v0.2対応）
$providerPaths = @("attachments\providers\internal", "attachments\providers\polygon")
Write-Host "プロバイダディレクトリ構造を作成中..." -ForegroundColor Yellow

$providerPaths | ForEach-Object { 
    $path = Join-Path $tickerRoot $_
    New-Item -ItemType Directory -Force -Path $path | Out-Null
    Write-Host "  ✓ $path" -ForegroundColor Green
}

# 今日の日付でスナップショット作成
$stamp = Get-Date -Format "yyyy-MM-dd"
$shot = Join-Path $tickerRoot "snapshots\$stamp"
New-Item -ItemType Directory -Force -Path $shot | Out-Null
Write-Host "  ✓ $shot" -ForegroundColor Green

# テンプレートからファイルをコピー（v0.3最小構成）
$templates = @("A.yaml", "B.yaml", "C.yaml", "facts.md")
$templatePath = Join-Path $Root "_templates"

foreach ($template in $templates) {
    $sourceFile = Join-Path $templatePath $template
    $targetFile = Join-Path $shot $template
    
    if (Test-Path $sourceFile) {
        $content = Get-Content $sourceFile -Raw -Encoding UTF8
        # 日付を更新
        $content = $content -replace "YYYY-MM-DD", $stamp
        
        Set-Content -Path $targetFile -Value $content -Encoding UTF8
        Write-Host "  ✓ $template (date: $stamp)" -ForegroundColor Green
    }
}

# currentディレクトリにコピー
$currentPath = Join-Path $tickerRoot "current"
if (Test-Path $currentPath) {
    Remove-Item -Path $currentPath -Recurse -Force
}
Copy-Item -Recurse -Force $shot $currentPath
Write-Host "  ✓ current/ にコピー完了" -ForegroundColor Green

# カタログに銘柄を追加（手動確認用）
Write-Host "`n=== カタログ更新が必要 ===" -ForegroundColor Yellow
Write-Host "以下の行を _catalog/tickers.csv に手動追加してください:" -ForegroundColor Cyan
Write-Host "$Ticker,<name>,<sector>,USD,12,0.12" -ForegroundColor White

Write-Host "`n=== 銘柄 $Ticker 追加完了（v0.3 - 最小構成） ===" -ForegroundColor Green
Write-Host "次のステップ:" -ForegroundColor Cyan
Write-Host "  1. データ取得: Get-AHFPrices -Ticker $Ticker -From 2024-01-01 -To 2024-12-31" -ForegroundColor White
Write-Host "  2. 運用ループ（A/B/C）:" -ForegroundColor White
Write-Host "     A) facts.md にT1逐語を1行 → A.yaml の該当配列へ写経" -ForegroundColor Gray
Write-Host "     B) B.yaml のHorizon更新／Go/保留/No-Go／KPI×2" -ForegroundColor Gray
Write-Host "     C) C.yaml の反証3テスト" -ForegroundColor Gray
Write-Host "  3. スナップショット: New-AHFSnapshot -Ticker $Ticker" -ForegroundColor White
