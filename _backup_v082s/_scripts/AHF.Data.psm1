# AHF.Data.psm1 - AHFデータ取得モジュール（v0.2）
# 内部ETL主軸、Polygonフォールバック

function Get-AHFPrices {
    <#
    .SYNOPSIS
    AHF価格データ取得（自動プロバイダ選択）
    
    .DESCRIPTION
    環境変数AHF_DATASOURCEに基づいて内部ETLまたはPolygonから価格データを取得します。
    autoの場合は内部ETL→失敗時にPolygonにフォールバックします。
    キルスイッチが発動中の場合はInternal ETL専用で動作します。
    
    .PARAMETER Ticker
    銘柄コード（例：WOLF, AAPL）
    
    .PARAMETER From
    開始日（YYYY-MM-DD形式）
    
    .PARAMETER To
    終了日（YYYY-MM-DD形式）
    
    .PARAMETER Timespan
    時間間隔（day, week, month）
    
    .EXAMPLE
    Get-AHFPrices -Ticker WOLF -From 2024-09-01 -To 2025-09-13 -Timespan day
    #>
    param(
        [Parameter(Mandatory)][string]$Ticker,
        [Parameter(Mandatory)][string]$From, 
        [Parameter(Mandatory)][string]$To,
        [ValidateSet("day","week","month")][string]$Timespan="day"
    )
    
    # キルスイッチ状態確認
    $killSwitchFile = ".\ahf\.killswitch"
    if (Test-Path $killSwitchFile) {
        $killInfo = Get-Content $killSwitchFile | ConvertFrom-Json
        Write-Host "🚨 キルスイッチ発動中: $($killInfo.reason)" -ForegroundColor Red
        Write-Host "→ Internal ETL専用で動作します" -ForegroundColor Yellow
        $provider = "internal"
    } else {
        $provider = $env:AHF_DATASOURCE
        if (-not $provider) { $provider = "auto" }
    }
    
    Write-Host "=== AHF価格データ取得: $Ticker ===" -ForegroundColor Green
    Write-Host "プロバイダ: $provider" -ForegroundColor Yellow
    Write-Host "期間: $From ～ $To ($Timespan)" -ForegroundColor Yellow
    
    try {
        if ($provider -in @("internal","auto")) {
            Write-Host "内部ETLから取得中..." -ForegroundColor Cyan
            return Get-AHFPricesInternal -Ticker $Ticker -From $From -To $To -Timespan $Timespan
        }
    } catch { 
        if ($provider -ne "auto") { 
            Write-Error "内部ETL取得失敗: $($_.Exception.Message)"
            throw 
        }
        Write-Warning "内部ETL取得失敗、Polygonにフォールバック: $($_.Exception.Message)"
    }
    
    # キルスイッチ発動中はPolygonを使用しない
    if (Test-Path $killSwitchFile) {
        Write-Error "キルスイッチ発動中のため、Polygonデータは取得できません。"
        throw "キルスイッチ発動中: Polygonアクセス禁止"
    }
    
    Write-Host "Polygonから取得中..." -ForegroundColor Cyan
    return Get-AHFPricesPolygon -Ticker $Ticker -From $From -To $To -Timespan $Timespan
}

function Get-AHFPricesInternal {
    <#
    .SYNOPSIS
    内部ETLから価格データを取得
    
    .PARAMETER Ticker
    銘柄コード
    
    .PARAMETER From
    開始日
    
    .PARAMETER To
    終了日
    
    .PARAMETER Timespan
    時間間隔
    #>
    param(
        [string]$Ticker,
        [string]$From,
        [string]$To,
        [string]$Timespan
    )
    
    if (-not $env:AHF_INTERNAL_BASEURL -or -not $env:AHF_INTERNAL_TOKEN) {
        throw "AHF_INTERNAL_BASEURL または AHF_INTERNAL_TOKEN が未設定です。"
    }
    
    $uri = "$($env:AHF_INTERNAL_BASEURL)/prices?symbol=$Ticker&start=$From&end=$To&timespan=$Timespan"
    $headers = @{ 
        Authorization = "Bearer $($env:AHF_INTERNAL_TOKEN)"
        "Content-Type" = "application/json"
    }
    
    Write-Host "内部ETL URL: $uri" -ForegroundColor Gray
    
    try {
        $response = Invoke-RestMethod -Method GET -Uri $uri -Headers $headers -TimeoutSec 120
        
        if (-not $response) {
            throw "内部ETLからデータが取得できませんでした。"
        }
        
        Write-Host "✓ 内部ETL取得成功" -ForegroundColor Green
        Save-AHFProviderPayload -Ticker $Ticker -Payload $response -Provider "internal" -Stem "prices_${From}_$To"
        
        return $response
        
    } catch {
        Write-Error "内部ETL API呼び出しエラー: $($_.Exception.Message)"
        throw
    }
}

function Get-AHFPricesPolygon {
    <#
    .SYNOPSIS
    Polygon.ioから価格データを取得
    
    .PARAMETER Ticker
    銘柄コード
    
    .PARAMETER From
    開始日
    
    .PARAMETER To
    終了日
    
    .PARAMETER Timespan
    時間間隔
    #>
    param(
        [string]$Ticker,
        [string]$From,
        [string]$To,
        [string]$Timespan
    )
    
    if (-not $env:POLYGON_API_KEY) { 
        throw "POLYGON_API_KEY が未設定です。" 
    }
    
    $uri = "https://api.polygon.io/v2/aggs/ticker/$Ticker/range/1/$Timespan/$From/$To?adjusted=true&sort=asc&limit=50000&apiKey=$($env:POLYGON_API_KEY)"
    
    Write-Host "Polygon URL: $($uri -replace $env:POLYGON_API_KEY, '***')" -ForegroundColor Gray
    
    try {
        $response = Invoke-RestMethod -Method GET -Uri $uri -TimeoutSec 120
        
        if (-not $response.results) {
            throw "Polygonからデータが取得できませんでした。"
        }
        
        Write-Host "✓ Polygon取得成功: $($response.results.Count) 件" -ForegroundColor Green
        Save-AHFProviderPayload -Ticker $Ticker -Payload $response -Provider "polygon" -Stem "prices_${From}_$To"
        
        # CSV変換も保存
        $csv = $response.results | Select-Object @{
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
        
        Save-AHFProviderPayload -Ticker $Ticker -Payload $csv -Provider "polygon" -Stem "prices_${From}_$To" -Format "csv"
        
        return $response
        
    } catch {
        Write-Error "Polygon API呼び出しエラー: $($_.Exception.Message)"
        throw
    }
}

function Save-AHFProviderPayload {
    <#
    .SYNOPSIS
    プロバイダ別データ保存
    
    .PARAMETER Ticker
    銘柄コード
    
    .PARAMETER Payload
    保存するデータ
    
    .PARAMETER Provider
    プロバイダ名（internal, polygon）
    
    .PARAMETER Stem
    ファイル名の基本部分
    
    .PARAMETER Format
    保存形式（json, csv）
    #>
    param(
        [string]$Ticker,
        [Parameter(Mandatory)]$Payload,
        [string]$Provider,
        [string]$Stem,
        [ValidateSet("json","csv")][string]$Format = "json"
    )
    
    $dir = ".\ahf\tickers\$Ticker\attachments\providers\$Provider"
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
    
    $filePath = Join-Path $dir "$Stem.$Format"
    
    if ($Format -eq "json") {
        $content = $Payload | ConvertTo-Json -Depth 8
        $content | Set-Content $filePath -Encoding UTF8
    } elseif ($Format -eq "csv") {
        $Payload | Export-Csv -NoTypeInformation -Path $filePath -Encoding UTF8
    }
    
    Write-Host "✓ データ保存: $filePath" -ForegroundColor Green
}

function Get-AHFFundamentals {
    <#
    .SYNOPSIS
    ファンダメンタルデータ取得（内部ETL）
    
    .PARAMETER Ticker
    銘柄コード
    
    .PARAMETER Period
    期間（quarter, annual）
    #>
    param(
        [Parameter(Mandatory)][string]$Ticker,
        [ValidateSet("quarter","annual")][string]$Period = "quarter"
    )
    
    if (-not $env:AHF_INTERNAL_BASEURL -or -not $env:AHF_INTERNAL_TOKEN) {
        throw "AHF_INTERNAL_BASEURL または AHF_INTERNAL_TOKEN が未設定です。"
    }
    
    $uri = "$($env:AHF_INTERNAL_BASEURL)/fundamentals?symbol=$Ticker&period=$Period"
    $headers = @{ 
        Authorization = "Bearer $($env:AHF_INTERNAL_TOKEN)"
        "Content-Type" = "application/json"
    }
    
    Write-Host "=== ファンダメンタルデータ取得: $Ticker ($Period) ===" -ForegroundColor Green
    
    try {
        $response = Invoke-RestMethod -Method GET -Uri $uri -Headers $headers -TimeoutSec 120
        Save-AHFProviderPayload -Ticker $Ticker -Payload $response -Provider "internal" -Stem "fundamentals_$Period"
        return $response
    } catch {
        Write-Error "ファンダメンタルデータ取得エラー: $($_.Exception.Message)"
        throw
    }
}

function Get-AHFEvents {
    <#
    .SYNOPSIS
    イベントデータ取得（内部ETL）
    
    .PARAMETER Ticker
    銘柄コード
    
    .PARAMETER From
    開始日
    
    .PARAMETER To
    終了日
    #>
    param(
        [Parameter(Mandatory)][string]$Ticker,
        [Parameter(Mandatory)][string]$From,
        [Parameter(Mandatory)][string]$To
    )
    
    if (-not $env:AHF_INTERNAL_BASEURL -or -not $env:AHF_INTERNAL_TOKEN) {
        throw "AHF_INTERNAL_BASEURL または AHF_INTERNAL_TOKEN が未設定です。"
    }
    
    $uri = "$($env:AHF_INTERNAL_BASEURL)/events?symbol=$Ticker&start=$From&end=$To"
    $headers = @{ 
        Authorization = "Bearer $($env:AHF_INTERNAL_TOKEN)"
        "Content-Type" = "application/json"
    }
    
    Write-Host "=== イベントデータ取得: $Ticker ===" -ForegroundColor Green
    Write-Host "期間: $From ～ $To" -ForegroundColor Yellow
    
    try {
        $response = Invoke-RestMethod -Method GET -Uri $uri -Headers $headers -TimeoutSec 120
        Save-AHFProviderPayload -Ticker $Ticker -Payload $response -Provider "internal" -Stem "events_${From}_$To"
        return $response
    } catch {
        Write-Error "イベントデータ取得エラー: $($_.Exception.Message)"
        throw
    }
}

function Get-AHFTranscripts {
    <#
    .SYNOPSIS
    トランスクリプトデータ取得（内部ETL）
    
    .PARAMETER Ticker
    銘柄コード
    
    .PARAMETER Period
    四半期（例：2025-Q3）
    #>
    param(
        [Parameter(Mandatory)][string]$Ticker,
        [Parameter(Mandatory)][string]$Period
    )
    
    if (-not $env:AHF_INTERNAL_BASEURL -or -not $env:AHF_INTERNAL_TOKEN) {
        throw "AHF_INTERNAL_BASEURL または AHF_INTERNAL_TOKEN が未設定です。"
    }
    
    $uri = "$($env:AHF_INTERNAL_BASEURL)/transcripts?symbol=$Ticker&period=$Period"
    $headers = @{ 
        Authorization = "Bearer $($env:AHF_INTERNAL_TOKEN)"
        "Content-Type" = "application/json"
    }
    
    Write-Host "=== トランスクリプト取得: $Ticker ($Period) ===" -ForegroundColor Green
    
    try {
        $response = Invoke-RestMethod -Method GET -Uri $uri -Headers $headers -TimeoutSec 120
        Save-AHFProviderPayload -Ticker $Ticker -Payload $response -Provider "internal" -Stem "transcripts_$Period"
        return $response
    } catch {
        Write-Error "トランスクリプト取得エラー: $($_.Exception.Message)"
        throw
    }
}

# モジュールメンバーをエクスポート
Export-ModuleMember -Function Get-AHFPrices, Get-AHFPricesInternal, Get-AHFPricesPolygon, Save-AHFProviderPayload, Get-AHFFundamentals, Get-AHFEvents, Get-AHFTranscripts
