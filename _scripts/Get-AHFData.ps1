# Get-AHFData.ps1 - AHFデータ取得スクリプト（v0.2）
# 内部ETL主軸、Polygonフォールバック

param(
    [Parameter(Mandatory)][string]$Ticker,
    [Parameter(Mandatory)][string]$From,   # "2024-01-01"
    [Parameter(Mandatory)][string]$To,     # "2025-09-13"
    [ValidateSet("day","week","month")][string]$Timespan = "day",
    [ValidateSet("prices","fundamentals","events","transcripts")][string]$DataType = "prices",
    [string]$Period = "",  # ファンダメンタルやトランスクリプト用
    [string]$Root = ".\ahf"
)

Write-Host "=== AHFデータ取得: $Ticker ===" -ForegroundColor Green
Write-Host "データタイプ: $DataType" -ForegroundColor Yellow
Write-Host "期間: $From ～ $To" -ForegroundColor Yellow

# AHF.Dataモジュールをインポート
$modulePath = Join-Path $Root "_scripts\AHF.Data.psm1"
if (-not (Test-Path $modulePath)) {
    Write-Error "AHF.Data.psm1モジュールが見つかりません: $modulePath"
    exit 1
}

Import-Module $modulePath -Force

try {
    switch ($DataType) {
        "prices" {
            Write-Host "価格データ取得中..." -ForegroundColor Cyan
            $result = Get-AHFPrices -Ticker $Ticker -From $From -To $To -Timespan $Timespan
            
            # サマリー表示
            if ($result.results) {
                $count = $result.results.Count
                $firstDate = [DateTimeOffset]::FromUnixTimeMilliseconds($result.results[0].t).ToString("yyyy-MM-dd")
                $lastDate = [DateTimeOffset]::FromUnixTimeMilliseconds($result.results[-1].t).ToString("yyyy-MM-dd")
                Write-Host "✓ 価格データ取得成功: $count 件 ($firstDate ～ $lastDate)" -ForegroundColor Green
            }
        }
        "fundamentals" {
            if (-not $Period) {
                $Period = "quarter"
            }
            Write-Host "ファンダメンタルデータ取得中... ($Period)" -ForegroundColor Cyan
            $result = Get-AHFFundamentals -Ticker $Ticker -Period $Period
            Write-Host "✓ ファンダメンタルデータ取得成功" -ForegroundColor Green
        }
        "events" {
            Write-Host "イベントデータ取得中..." -ForegroundColor Cyan
            $result = Get-AHFEvents -Ticker $Ticker -From $From -To $To
            Write-Host "✓ イベントデータ取得成功" -ForegroundColor Green
        }
        "transcripts" {
            if (-not $Period) {
                $Period = "2025-Q3"  # デフォルト
            }
            Write-Host "トランスクリプト取得中... ($Period)" -ForegroundColor Cyan
            $result = Get-AHFTranscripts -Ticker $Ticker -Period $Period
            Write-Host "✓ トランスクリプト取得成功" -ForegroundColor Green
        }
    }
    
    Write-Host "`n=== データ取得完了 ===" -ForegroundColor Green
    Write-Host "保存先: tickers\$Ticker\attachments\providers\" -ForegroundColor Cyan
    
} catch {
    Write-Error "データ取得エラー: $($_.Exception.Message)"
    exit 1
} finally {
    # モジュールをアンロード
    Remove-Module AHF.Data -ErrorAction SilentlyContinue
}

Write-Host "`n次のステップ:" -ForegroundColor Yellow
Write-Host "  1. facts.md にT1事実を追加" -ForegroundColor White
Write-Host "  2. A.yaml の該当配列に1レコード追加" -ForegroundColor White
Write-Host "  3. B.yaml のHorizonとC.yamlの3テストを更新" -ForegroundColor White
