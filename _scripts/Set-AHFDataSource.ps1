# Set-AHFDataSource.ps1 - AHFデータソース管理スクリプト（v0.3）
# キルスイッチ機能とプロバイダ状態管理
param(
    [ValidateSet("auto","internal","polygon","kill")][string]$Mode = "auto",
    [string]$Reason = "",
    [switch]$Force,
    [switch]$ShowStatus
)

Write-Host "=== AHFデータソース管理 ===" -ForegroundColor Green

# 現在の状態表示
if ($ShowStatus) {
    Write-Host "`n=== 現在の状態 ===" -ForegroundColor Cyan
    $currentMode = $env:AHF_DATASOURCE
    if (-not $currentMode) { $currentMode = "auto" }
    
    Write-Host "データソース: $currentMode" -ForegroundColor White
    Write-Host "Internal API: $(if($env:AHF_INTERNAL_BASEURL){'設定済み'}else{'未設定'})" -ForegroundColor White
    Write-Host "Polygon API: $(if($env:POLYGON_API_KEY){'設定済み'}else{'未設定'})" -ForegroundColor White
    
    # キルスイッチ状態確認
    $killSwitchFile = ".\ahf\.killswitch"
    if (Test-Path $killSwitchFile) {
        $killInfo = Get-Content $killSwitchFile | ConvertFrom-Json
        Write-Host "キルスイッチ: 発動中 ($($killInfo.reason))" -ForegroundColor Red
        Write-Host "発動時刻: $($killInfo.timestamp)" -ForegroundColor Red
        Write-Host "発動者: $($killInfo.triggered_by)" -ForegroundColor Red
    } else {
        Write-Host "キルスイッチ: 正常" -ForegroundColor Green
    }
    
    return
}

# キルスイッチ状態確認
$killSwitchFile = ".\ahf\.killswitch"
$isKillSwitchActive = Test-Path $killSwitchFile

if ($isKillSwitchActive -and $Mode -ne "kill") {
    $killInfo = Get-Content $killSwitchFile | ConvertFrom-Json
    Write-Host "⚠ キルスイッチが発動中です" -ForegroundColor Red
    Write-Host "理由: $($killInfo.reason)" -ForegroundColor Red
    Write-Host "発動時刻: $($killInfo.timestamp)" -ForegroundColor Red
    
    if (-not $Force) {
        Write-Host "`nキルスイッチを解除するには:" -ForegroundColor Yellow
        Write-Host "Set-AHFDataSource -Mode auto -Force" -ForegroundColor Yellow
        return
    } else {
        Write-Host "`n⚠ 強制モードでキルスイッチを無視します" -ForegroundColor Yellow
        Remove-Item $killSwitchFile -Force
        Write-Host "✓ キルスイッチ解除" -ForegroundColor Green
    }
}

# モード設定
switch ($Mode) {
    "auto" {
        $env:AHF_DATASOURCE = "auto"
        Write-Host "✓ データソース: auto (Internal優先、Polygonフォールバック)" -ForegroundColor Green
    }
    "internal" {
        $env:AHF_DATASOURCE = "internal"
        Write-Host "✓ データソース: internal (Internal ETL専用)" -ForegroundColor Green
    }
    "polygon" {
        $env:AHF_DATASOURCE = "polygon"
        Write-Host "✓ データソース: polygon (Polygon専用)" -ForegroundColor Green
    }
    "kill" {
        # キルスイッチ発動
        $killInfo = [pscustomobject]@{
            timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
            reason = if ($Reason) { $Reason } else { "手動発動" }
            triggered_by = $env:USERNAME
            previous_mode = $env:AHF_DATASOURCE
        }
        
        # .ahfディレクトリ作成（存在しない場合）
        if (-not (Test-Path ".\ahf")) {
            New-Item -ItemType Directory -Path ".\ahf" -Force | Out-Null
        }
        
        $killInfo | ConvertTo-Json | Set-Content $killSwitchFile -Encoding UTF8
        
        $env:AHF_DATASOURCE = "internal"
        Write-Host "🚨 キルスイッチ発動！" -ForegroundColor Red
        Write-Host "理由: $($killInfo.reason)" -ForegroundColor Red
        Write-Host "データソース: internal に強制変更" -ForegroundColor Red
        Write-Host "Polygonデータ取得は停止されます" -ForegroundColor Red
        
        # ログ記録
        $logFile = ".\ahf\killswitch.log"
        $logEntry = [pscustomobject]@{
            timestamp = $killInfo.timestamp
            reason = $killInfo.reason
            triggered_by = $killInfo.triggered_by
            previous_mode = $killInfo.previous_mode
        }
        
        $logEntry | ConvertTo-Json | Add-Content $logFile -Encoding UTF8
        Write-Host "✓ ログ記録: $logFile" -ForegroundColor Green
    }
}

# 環境変数の永続化（ユーザープロファイル）
$profilePath = $PROFILE
if (-not (Test-Path $profilePath)) {
    New-Item -ItemType File -Path $profilePath -Force | Out-Null
}

# 既存のAHF_DATASOURCE設定を削除
$profileContent = Get-Content $profilePath -ErrorAction SilentlyContinue
$newProfileContent = $profileContent | Where-Object { $_ -notmatch "AHF_DATASOURCE" }

# 新しい設定を追加
$newProfileContent += "`n# AHF Data Source Configuration"
$newProfileContent += "`$env:AHF_DATASOURCE = '$Mode'"

$newProfileContent | Set-Content $profilePath -Encoding UTF8
Write-Host "✓ 環境変数永続化: $profilePath" -ForegroundColor Green

# 状態確認
Write-Host "`n=== 設定完了 ===" -ForegroundColor Cyan
Write-Host "現在のデータソース: $env:AHF_DATASOURCE" -ForegroundColor White

if ($Mode -eq "kill") {
    Write-Host "`n=== キルスイッチ後の運用 ===" -ForegroundColor Cyan
    Write-Host "1. Internal ETLのみで運用継続" -ForegroundColor White
    Write-Host "2. Polygonデータ取得は自動停止" -ForegroundColor White
    Write-Host "3. 既存の昇格済みデータは使用可能" -ForegroundColor White
    Write-Host "4. キルスイッチ解除: Set-AHFDataSource -Mode auto -Force" -ForegroundColor White
}
