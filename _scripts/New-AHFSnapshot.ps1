# New-AHFSnapshot.ps1 - スナップショット作成スクリプト（差分を残す）
param(
    [Parameter(Mandatory)][string]$Ticker,
    [string]$Root = ".\ahf"
)

Write-Host "=== AHFスナップショット作成: $Ticker ===" -ForegroundColor Green

$tickerRoot = Join-Path $Root "tickers\$Ticker"
$currentPath = Join-Path $tickerRoot "current"

# currentディレクトリの存在確認
if (-not (Test-Path $currentPath)) {
    Write-Error "currentディレクトリが見つかりません: $currentPath"
    Write-Host "先に Add-AHFTicker.ps1 を実行してください。" -ForegroundColor Yellow
    exit 1
}

# 今日の日付でスナップショット作成
$stamp = Get-Date -Format "yyyy-MM-dd"
$shotPath = Join-Path $tickerRoot "snapshots\$stamp"

# 既存のスナップショット確認
if (Test-Path $shotPath) {
    Write-Warning "今日のスナップショットは既に存在します: $shotPath"
    $overwrite = Read-Host "上書きしますか？ (y/N)"
    if ($overwrite -ne "y" -and $overwrite -ne "Y") {
        Write-Host "スナップショット作成をキャンセルしました。" -ForegroundColor Yellow
        exit 0
    }
    Remove-Item -Path $shotPath -Recurse -Force
}

# スナップショットディレクトリ作成
New-Item -ItemType Directory -Force -Path $shotPath | Out-Null
Write-Host "✓ スナップショットディレクトリ作成: $shotPath" -ForegroundColor Green

# currentからスナップショットにコピー
$files = Get-ChildItem -Path $currentPath -File
foreach ($file in $files) {
    $targetFile = Join-Path $shotPath $file.Name
    Copy-Item -Path $file.FullName -Destination $targetFile
    Write-Host "  ✓ $($file.Name)" -ForegroundColor Green
}

# メタデータ更新（日付を今日に更新）
$yamlFiles = @("A.yaml", "B.yaml", "C.yaml")
foreach ($yamlFile in $yamlFiles) {
    $filePath = Join-Path $shotPath $yamlFile
    if (Test-Path $filePath) {
        $content = Get-Content $filePath -Raw -Encoding UTF8
        # asof日付を更新
        $content = $content -replace "asof: \d{4}-\d{2}-\d{2}", "asof: $stamp"
        Set-Content -Path $filePath -Value $content -Encoding UTF8
        Write-Host "  ✓ $yamlFile メタデータ更新" -ForegroundColor Green
    }
}

# 差分確認（前回のスナップショットと比較）
$snapshotsDir = Join-Path $tickerRoot "snapshots"
$previousSnapshots = Get-ChildItem -Path $snapshotsDir -Directory | 
    Where-Object { $_.Name -ne $stamp } | 
    Sort-Object Name -Descending

if ($previousSnapshots.Count -gt 0) {
    $latestPrevious = $previousSnapshots[0]
    Write-Host "`n=== 差分確認: $($latestPrevious.Name) → $stamp ===" -ForegroundColor Cyan
    
    $diffFiles = @()
    foreach ($yamlFile in $yamlFiles) {
        $currentFile = Join-Path $shotPath $yamlFile
        $previousFile = Join-Path $latestPrevious.FullName $yamlFile
        
        if ((Test-Path $currentFile) -and (Test-Path $previousFile)) {
            $currentContent = Get-Content $currentFile -Raw
            $previousContent = Get-Content $previousFile -Raw
            
            if ($currentContent -ne $previousContent) {
                $diffFiles += $yamlFile
            }
        }
    }
    
    if ($diffFiles.Count -gt 0) {
        Write-Host "変更されたファイル:" -ForegroundColor Yellow
        $diffFiles | ForEach-Object { Write-Host "  • $_" -ForegroundColor White }
    } else {
        Write-Host "変更なし" -ForegroundColor Green
    }
}

# スナップショット完了
Write-Host "`n=== スナップショット作成完了 ===" -ForegroundColor Green
Write-Host "スナップショット: $shotPath" -ForegroundColor Cyan
Write-Host "次のステップ:" -ForegroundColor Yellow
Write-Host "  1. _catalog/horizon_index.csv に手動追記" -ForegroundColor White
Write-Host "  2. 必要に応じて current/ を最新で更新" -ForegroundColor White
Write-Host "  3. git add . && git commit -m 'Snapshot $Ticker $stamp'" -ForegroundColor White
