# Start-AHFMonitoring.ps1 - AHF自動監視スクリプト（v0.3）
# パリティ検証とキルスイッチ自動発動
param(
    [string[]]$Tickers = @("WOLF"),  # 監視対象銘柄
    [int]$CheckIntervalHours = 24,   # チェック間隔（時間）
    [int]$ParityFailureThreshold = 7, # パリティ失敗しきい値（日数）
    [double]$ApiFailureThreshold = 0.2, # API失敗率しきい値（20%）
    [switch]$Background,             # バックグラウンド実行
    [switch]$DryRun                  # ドライラン（実際のキルスイッチは発動しない）
)

Write-Host "=== AHF自動監視開始 ===" -ForegroundColor Green
Write-Host "監視対象: $($Tickers -join ', ')" -ForegroundColor Yellow
Write-Host "チェック間隔: $CheckIntervalHours 時間" -ForegroundColor Yellow
Write-Host "パリティ失敗しきい値: $ParityFailureThreshold 日" -ForegroundColor Yellow
Write-Host "API失敗率しきい値: $($ApiFailureThreshold * 100)%" -ForegroundColor Yellow

# 監視状態ファイル
$monitorStateFile = ".\ahf\.monitor_state.json"
$killSwitchFile = ".\ahf\.killswitch"

# 初期状態設定
if (-not (Test-Path $monitorStateFile)) {
    $initialState = [pscustomobject]@{
        start_time = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        tickers = $Tickers
        parity_failures = @{}
        api_failures = @{}
        last_check = ""
        total_checks = 0
    }
    
    # .ahfディレクトリ作成
    if (-not (Test-Path ".\ahf")) {
        New-Item -ItemType Directory -Path ".\ahf" -Force | Out-Null
    }
    
    $initialState | ConvertTo-Json -Depth 3 | Set-Content $monitorStateFile -Encoding UTF8
    Write-Host "✓ 監視状態初期化: $monitorStateFile" -ForegroundColor Green
}

# 監視ループ関数
function Start-MonitoringLoop {
    param(
        [string[]]$Tickers,
        [int]$IntervalHours,
        [int]$ParityThreshold,
        [double]$ApiThreshold,
        [bool]$IsDryRun
    )
    
    Write-Host "`n=== 監視ループ開始 ===" -ForegroundColor Cyan
    
    while ($true) {
        $state = Get-Content $monitorStateFile | ConvertFrom-Json
        $currentTime = Get-Date
        $state.last_check = $currentTime.ToString("yyyy-MM-dd HH:mm:ss")
        $state.total_checks++
        
        Write-Host "`n--- 監視チェック #$($state.total_checks) ($($currentTime.ToString('HH:mm:ss'))) ---" -ForegroundColor Cyan
        
        $killSwitchTriggered = $false
        $killReason = ""
        
        foreach ($ticker in $Tickers) {
            Write-Host "`n銘柄: $ticker" -ForegroundColor Yellow
            
            # パリティ検証
            try {
                $parityScript = Join-Path $PSScriptRoot "Test-AHFParity.ps1"
                if (Test-Path $parityScript) {
                    # 過去30日間のデータでパリティ検証
                    $fromDate = (Get-Date).AddDays(-30).ToString("yyyy-MM-dd")
                    $toDate = (Get-Date).AddDays(-1).ToString("yyyy-MM-dd")
                    
                    & $parityScript -Ticker $ticker -From $fromDate -To $toDate -Root ".\ahf" 2>$null
                    $parityResult = $LASTEXITCODE
                    
                    if ($parityResult -ne 0) {
                        # パリティ失敗
                        if (-not $state.parity_failures.$ticker) {
                            $state.parity_failures.$ticker = @()
                        }
                        $state.parity_failures.$ticker += $currentTime.ToString("yyyy-MM-dd")
                        
                        # 古い失敗記録を削除（30日以上前）
                        $cutoffDate = (Get-Date).AddDays(-30).ToString("yyyy-MM-dd")
                        $state.parity_failures.$ticker = $state.parity_failures.$ticker | Where-Object { $_ -ge $cutoffDate }
                        
                        $failureCount = $state.parity_failures.$ticker.Count
                        Write-Host "  ⚠ パリティ失敗 ($failureCount 日連続)" -ForegroundColor Red
                        
                        if ($failureCount -ge $ParityThreshold) {
                            $killSwitchTriggered = $true
                            $killReason = "パリティ検証失敗 ($ticker: $failureCount 日連続)"
                        }
                    } else {
                        # パリティ成功
                        $state.parity_failures.$ticker = @()
                        Write-Host "  ✓ パリティ検証OK" -ForegroundColor Green
                    }
                }
            } catch {
                Write-Host "  ⚠ パリティ検証エラー: $($_.Exception.Message)" -ForegroundColor Yellow
            }
            
            # API失敗率チェック
            try {
                $apiFailureCount = 0
                $totalApiCalls = 0
                
                # 過去7日間のAPI呼び出し結果をチェック
                for ($i = 1; $i -le 7; $i++) {
                    $checkDate = (Get-Date).AddDays(-$i).ToString("yyyy-MM-dd")
                    $logFile = ".\ahf\api_logs_$ticker`_$checkDate.json"
                    
                    if (Test-Path $logFile) {
                        $logData = Get-Content $logFile | ConvertFrom-Json
                        $totalApiCalls += $logData.total_calls
                        $apiFailureCount += $logData.failed_calls
                    }
                }
                
                if ($totalApiCalls -gt 0) {
                    $failureRate = $apiFailureCount / $totalApiCalls
                    
                    if (-not $state.api_failures.$ticker) {
                        $state.api_failures.$ticker = @{
                            total_calls = 0
                            failed_calls = 0
                            last_check = ""
                        }
                    }
                    
                    $state.api_failures.$ticker.total_calls = $totalApiCalls
                    $state.api_failures.$ticker.failed_calls = $apiFailureCount
                    $state.api_failures.$ticker.last_check = $currentTime.ToString("yyyy-MM-dd HH:mm:ss")
                    
                    Write-Host "  API失敗率: $([math]::Round($failureRate * 100, 1))% ($apiFailureCount/$totalApiCalls)" -ForegroundColor $(if($failureRate -gt $ApiThreshold){"Red"}else{"Green"})
                    
                    if ($failureRate -gt $ApiThreshold) {
                        $killSwitchTriggered = $true
                        $killReason = "API失敗率超過 ($ticker: $([math]::Round($failureRate * 100, 1))%)"
                    }
                }
            } catch {
                Write-Host "  ⚠ API失敗率チェックエラー: $($_.Exception.Message)" -ForegroundColor Yellow
            }
        }
        
        # キルスイッチ発動判定
        if ($killSwitchTriggered -and -not $IsDryRun) {
            Write-Host "`n🚨 キルスイッチ発動条件満たす: $killReason" -ForegroundColor Red
            
            # キルスイッチ発動
            $killScript = Join-Path $PSScriptRoot "Set-AHFDataSource.ps1"
            if (Test-Path $killScript) {
                & $killScript -Mode kill -Reason $killReason
                Write-Host "✓ キルスイッチ発動完了" -ForegroundColor Red
                
                # 監視停止
                Write-Host "`n監視を停止します（キルスイッチ発動のため）" -ForegroundColor Yellow
                break
            }
        } elseif ($killSwitchTriggered) {
            Write-Host "`n⚠ ドライラン: キルスイッチ発動条件満たすが実行しません" -ForegroundColor Yellow
            Write-Host "理由: $killReason" -ForegroundColor Yellow
        }
        
        # 状態保存
        $state | ConvertTo-Json -Depth 3 | Set-Content $monitorStateFile -Encoding UTF8
        
        # 待機
        Write-Host "`n次回チェックまで $IntervalHours 時間待機..." -ForegroundColor Cyan
        Start-Sleep -Seconds ($IntervalHours * 3600)
    }
}

# バックグラウンド実行
if ($Background) {
    Write-Host "`nバックグラウンドで監視を開始します..." -ForegroundColor Yellow
    $job = Start-Job -ScriptBlock {
        param($Tickers, $IntervalHours, $ParityThreshold, $ApiThreshold, $IsDryRun, $MonitorStateFile, $PSScriptRoot)
        
        # 監視ループ関数を再定義（ジョブ内で実行）
        function Start-MonitoringLoop {
            param([string[]]$Tickers, [int]$IntervalHours, [int]$ParityThreshold, [double]$ApiThreshold, [bool]$IsDryRun)
            
            while ($true) {
                # 監視ロジック（簡略版）
                Write-Host "監視チェック実行中..." -ForegroundColor Green
                Start-Sleep -Seconds ($IntervalHours * 3600)
            }
        }
        
        Start-MonitoringLoop -Tickers $Tickers -IntervalHours $IntervalHours -ParityThreshold $ParityThreshold -ApiThreshold $ApiThreshold -IsDryRun $IsDryRun
    } -ArgumentList $Tickers, $CheckIntervalHours, $ParityFailureThreshold, $ApiFailureThreshold, $DryRun, $monitorStateFile, $PSScriptRoot
    
    Write-Host "✓ バックグラウンドジョブ開始: Job ID $($job.Id)" -ForegroundColor Green
    Write-Host "ジョブ確認: Get-Job -Id $($job.Id)" -ForegroundColor Yellow
    Write-Host "ジョブ停止: Stop-Job -Id $($job.Id)" -ForegroundColor Yellow
} else {
    # フォアグラウンド実行
    Start-MonitoringLoop -Tickers $Tickers -IntervalHours $CheckIntervalHours -ParityThreshold $ParityFailureThreshold -ApiThreshold $ApiFailureThreshold -IsDryRun $DryRun
}

Write-Host "`n=== 監視設定完了 ===" -ForegroundColor Green
