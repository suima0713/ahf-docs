# Promote-AHFMarketData.ps1 - AHFデータ昇格スクリプト（v0.3）
# パリティ検証合格後のPolygonデータをcurrent/に昇格
param(
    [Parameter(Mandatory)][string]$Ticker,
    [Parameter(Mandatory)][string]$From,   # "2024-01-01"
    [Parameter(Mandatory)][string]$To,     # "2025-09-13"
    [switch]$Force,                        # 強制昇格（パリティチェックスキップ）
    [switch]$Backup,                       # 既存データのバックアップ作成
    [string]$Root = ".\ahf"
)

Write-Host "=== AHFデータ昇格: $Ticker ===" -ForegroundColor Green
Write-Host "期間: $From ～ $To" -ForegroundColor Yellow
Write-Host "強制昇格: $Force" -ForegroundColor Yellow
Write-Host "バックアップ: $Backup" -ForegroundColor Yellow

# パリティ検証（Force指定時はスキップ）
if (-not $Force) {
    Write-Host "`n=== 事前パリティ検証 ===" -ForegroundColor Cyan
    try {
        $parityScript = Join-Path $PSScriptRoot "Test-AHFParity.ps1"
        if (-not (Test-Path $parityScript)) {
            Write-Error "パリティ検証スクリプトが見つかりません: $parityScript"
            exit 1
        }
        
        & $parityScript -Ticker $Ticker -From $From -To $To -Root $Root
        if ($LASTEXITCODE -ne 0) {
            Write-Error "パリティ検証に失敗しました。--Force を使用して強制昇格するか、データを修正してください。"
            exit 1
        }
        Write-Host "✓ パリティ検証合格" -ForegroundColor Green
    } catch {
        Write-Error "パリティ検証エラー: $($_.Exception.Message)"
        exit 1
    }
} else {
    Write-Host "⚠ パリティ検証をスキップ（強制昇格）" -ForegroundColor Yellow
}

# ソースファイル確認
$polygonSourcePath = Join-Path $Root "tickers\$Ticker\attachments\providers\polygon\prices_${From}_${To}.csv"
if (-not (Test-Path $polygonSourcePath)) {
    Write-Error "昇格元ファイルが見つかりません: $polygonSourcePath"
    exit 1
}

# ターゲットディレクトリ作成
$targetDir = Join-Path $Root "tickers\$Ticker\current\market"
New-Item -ItemType Directory -Force -Path $targetDir | Out-Null

$targetPath = Join-Path $targetDir "prices_${From}_${To}.csv"

# 既存ファイルのバックアップ
if ($Backup -and (Test-Path $targetPath)) {
    $backupDir = Join-Path $Root "tickers\$Ticker\snapshots\$(Get-Date -Format 'yyyy-MM-dd-HHmm')"
    New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
    
    $backupPath = Join-Path $backupDir "prices_${From}_${To}.csv"
    Copy-Item $targetPath $backupPath
    Write-Host "✓ 既存データをバックアップ: $backupPath" -ForegroundColor Green
}

# データ昇格実行
Write-Host "`n=== データ昇格実行 ===" -ForegroundColor Cyan
try {
    Copy-Item $polygonSourcePath $targetPath -Force
    Write-Host "✓ データ昇格完了: $targetPath" -ForegroundColor Green
    
    # メタデータ作成
    $metadataPath = Join-Path $targetDir "prices_${From}_${To}.metadata.json"
    $metadata = [pscustomobject]@{
        ticker = $Ticker
        from_date = $From
        to_date = $To
        promoted_date = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        source_provider = "polygon"
        parity_verified = -not $Force
        original_file = $polygonSourcePath
        promoted_by = $env:USERNAME
        notes = if ($Force) { "強制昇格（パリティチェックスキップ）" } else { "パリティ検証合格後昇格" }
    }
    
    $metadata | ConvertTo-Json -Depth 3 | Set-Content $metadataPath -Encoding UTF8
    Write-Host "✓ メタデータ作成: $metadataPath" -ForegroundColor Green
    
    # データ統計表示
    $data = Import-Csv $targetPath
    $firstDate = $data[0].date
    $lastDate = $data[-1].date
    $priceRange = "$(($data | Measure-Object -Property low -Minimum).Minimum) - $(($data | Measure-Object -Property high -Maximum).Maximum)"
    $avgVolume = [math]::Round(($data | Measure-Object -Property volume -Average).Average, 0)
    
    Write-Host "`n=== 昇格データ統計 ===" -ForegroundColor Cyan
    Write-Host "期間: $firstDate ～ $lastDate" -ForegroundColor White
    Write-Host "データ数: $($data.Count) 件" -ForegroundColor White
    Write-Host "価格レンジ: $priceRange" -ForegroundColor White
    Write-Host "平均出来高: $avgVolume" -ForegroundColor White
    
    Write-Host "`n=== 昇格完了 ===" -ForegroundColor Green
    Write-Host "→ データは現在の分析で使用可能です" -ForegroundColor Green
    Write-Host "→ A/B/Cファイルは未更新のまま（方針通り）" -ForegroundColor Yellow
    
} catch {
    Write-Error "データ昇格エラー: $($_.Exception.Message)"
    exit 1
}

# 後処理：昇格成功後のクリーンアップ（オプション）
if ($Force) {
    Write-Host "`n⚠ 強制昇格のため、手動でのデータ検証を推奨します" -ForegroundColor Yellow
}

Write-Host "`n=== 次のステップ ===" -ForegroundColor Cyan
Write-Host "1. データの可視化確認" -ForegroundColor White
Write-Host "2. ΔIRR計算での使用" -ForegroundColor White
Write-Host "3. 必要に応じてA/B/Cファイルの更新検討" -ForegroundColor White
