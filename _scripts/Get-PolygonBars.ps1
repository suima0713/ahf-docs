# Get-PolygonBars.ps1 - Polygon.io価格データ取得スクリプト
param(
    [Parameter(Mandatory)][string]$Ticker,
    [Parameter(Mandatory)][string]$From,   # "2024-01-01"
    [Parameter(Mandatory)][string]$To,     # "2025-09-13"
    [int]$Multiplier = 1,
    [ValidateSet("minute","hour","day","week","month")][string]$Timespan = "day",
    [string]$Root = ".\ahf"
)

Write-Host "=== Polygon.io価格データ取得: $Ticker ===" -ForegroundColor Green

# APIキー確認
if (-not $env:POLYGON_API_KEY) { 
    Write-Error "POLYGON_API_KEY が未設定です。`$env:POLYGON_API_KEY = '<YOUR_POLYGON_API_KEY>' を設定してください。"
    exit 1
}

Write-Host "APIキー: $($env:POLYGON_API_KEY.Substring(0,8))..." -ForegroundColor Yellow

# APIエンドポイント構築
$base = "https://api.polygon.io/v2/aggs/ticker/$Ticker/range/$Multiplier/$Timespan/$From/$To"
$uri = "$base?adjusted=true&sort=asc&limit=50000&apiKey=$($env:POLYGON_API_KEY)"

Write-Host "リクエストURL: $base" -ForegroundColor Yellow
Write-Host "期間: $From から $To" -ForegroundColor Yellow
Write-Host "間隔: $Timespan" -ForegroundColor Yellow

try {
    # API呼び出し
    Write-Host "API呼び出し中..." -ForegroundColor Yellow
    $data = Invoke-RestMethod -Method GET -Uri $uri
    
    if (-not $data.results) {
        Write-Warning "データが取得できませんでした。銘柄コードや期間を確認してください。"
        exit 1
    }
    
    Write-Host "✓ データ取得成功: $($data.results.Count) 件" -ForegroundColor Green
    
    # 保存ディレクトリ作成
    $saveDir = Join-Path $Root "tickers\$Ticker\attachments\polygon"
    New-Item -ItemType Directory -Force -Path $saveDir | Out-Null
    
    # JSON保存
    $jsonFile = Join-Path $saveDir "bars_$From`_$To.json"
    $data | ConvertTo-Json -Depth 6 | Set-Content $jsonFile -Encoding UTF8
    Write-Host "✓ JSON保存: $jsonFile" -ForegroundColor Green
    
    # CSV変換
    $csv = $data.results | Select-Object @{
        n="date"
        e={[DateTimeOffset]::FromUnixTimeMilliseconds($_.t).ToString("yyyy-MM-dd")}
    }, @{
        n="timestamp"
        e={[DateTimeOffset]::FromUnixTimeMilliseconds($_.t).ToString("yyyy-MM-dd HH:mm:ss")}
    }, @{
        n="open"
        e={[math]::Round($_.o, 2)}
    }, @{
        n="high"
        e={[math]::Round($_.h, 2)}
    }, @{
        n="low"
        e={[math]::Round($_.l, 2)}
    }, @{
        n="close"
        e={[math]::Round($_.c, 2)}
    }, @{
        n="volume"
        e={$_.v}
    }, @{
        n="vwap"
        e={[math]::Round($_.vw, 2)}
    }, @{
        n="transactions"
        e={$_.n}
    }
    
    $csvFile = Join-Path $saveDir "bars_$From`_$To.csv"
    $csv | Export-Csv -NoTypeInformation -Path $csvFile -Encoding UTF8
    Write-Host "✓ CSV保存: $csvFile" -ForegroundColor Green
    
    # サマリー表示
    $firstDate = $csv[0].date
    $lastDate = $csv[-1].date
    $priceRange = "$($csv | Measure-Object -Property low -Minimum).Minimum - $($csv | Measure-Object -Property high -Maximum).Maximum"
    $avgVolume = [math]::Round(($csv | Measure-Object -Property volume -Average).Average, 0)
    
    Write-Host "`n=== データサマリー ===" -ForegroundColor Cyan
    Write-Host "期間: $firstDate ～ $lastDate" -ForegroundColor White
    Write-Host "データ数: $($csv.Count) 件" -ForegroundColor White
    Write-Host "価格レンジ: $priceRange" -ForegroundColor White
    Write-Host "平均出来高: $avgVolume" -ForegroundColor White
    
    Write-Host "`n=== 価格データ取得完了 ===" -ForegroundColor Green
    
} catch {
    Write-Error "API呼び出しエラー: $($_.Exception.Message)"
    if ($_.Exception.Response) {
        $statusCode = $_.Exception.Response.StatusCode
        Write-Error "HTTPステータス: $statusCode"
    }
    exit 1
}
