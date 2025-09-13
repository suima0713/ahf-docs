# Add-AHFTicker.ps1 - 銘柄の骨組み作成スクリプト
param(
    [Parameter(Mandatory)][string]$Ticker,
    [string]$Root = ".\ahf"
)

Write-Host "=== AHF銘柄追加: $Ticker ===" -ForegroundColor Green

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

# テンプレートからファイルをコピーして銘柄名を更新
$templates = @("A.yaml", "B.yaml", "C.yaml", "facts.md")
$templatePath = Join-Path $Root "_templates"

foreach ($template in $templates) {
    $sourceFile = Join-Path $templatePath $template
    $targetFile = Join-Path $shot $template
    
    if (Test-Path $sourceFile) {
        $content = Get-Content $sourceFile -Raw -Encoding UTF8
        # テンプレートのXXXを実際の銘柄名に置換
        $content = $content -replace "XXX", $Ticker
        $content = $content -replace "2025-09-13", $stamp
        
        Set-Content -Path $targetFile -Value $content -Encoding UTF8
        Write-Host "  ✓ $template (ticker: $Ticker, date: $stamp)" -ForegroundColor Green
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

Write-Host "`n=== 銘柄 $Ticker 追加完了 ===" -ForegroundColor Green
Write-Host "次のステップ:" -ForegroundColor Cyan
Write-Host "  1. 環境変数設定:" -ForegroundColor White
Write-Host "     `$env:AHF_DATASOURCE = 'auto'" -ForegroundColor Gray
Write-Host "     `$env:AHF_INTERNAL_BASEURL = 'https://your-etl-host/api'" -ForegroundColor Gray
Write-Host "     `$env:AHF_INTERNAL_TOKEN = 'your-bearer-token'" -ForegroundColor Gray
Write-Host "  2. データ取得:" -ForegroundColor White
Write-Host "     pwsh .\ahf\_scripts\Get-AHFData.ps1 -Ticker $Ticker -From 2024-01-01 -To 2025-09-13" -ForegroundColor Gray
Write-Host "  3. facts.md にT1事実を追加" -ForegroundColor White
Write-Host "  4. A.yaml の該当配列に1レコード追加" -ForegroundColor White
Write-Host "  5. B.yaml のHorizonとC.yamlの3テストを更新" -ForegroundColor White
Write-Host "  6. pwsh .\ahf\_scripts\New-AHFSnapshot.ps1 -Ticker $Ticker" -ForegroundColor White
