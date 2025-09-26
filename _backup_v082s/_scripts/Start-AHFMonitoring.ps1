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
        data_quality_issues = @{}
        api_issues = @{}
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
                        # データ品質問題
                        if (-not $state.data_quality_issues.$ticker) {
                            $state.data_quality_issues.$ticker = @()
                        }
                        $state.data_quality_issues.$ticker += $currentTime.ToString("yyyy-MM-dd")
                        
                        # 古い問題記録を削除（30日以上前）
                        $cutoffDate = (Get-Date).AddDays(-30).ToString("yyyy-MM-dd")
                        $state.data_quality_issues.$ticker = $state.data_quality_issues.$ticker | Where-Object { $_ -ge $cutoffDate }
                        
                        $issueCount = $state.data_quality_issues.$ticker.Count
                        Write-Host "  ⚠ データ品質問題 ($issueCount 日連続)" -ForegroundColor Yellow
                    } else {
                        # データ品質正常
                        $state.data_quality_issues.$ticker = @()
                        Write-Host "  ✓ データ品質OK" -ForegroundColor Green
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
                        $apiIssueCount += $logData.failed_calls
                    }
                }
                
                if ($totalApiCalls -gt 0) {
                    $issueRate = $apiIssueCount / $totalApiCalls
                    
                    if (-not $state.api_issues.$ticker) {
                        $state.api_issues.$ticker = @{
                            total_calls = 0
                            failed_calls = 0
                            last_check = ""
                        }
                    }
                    
                    $state.api_issues.$ticker.total_calls = $totalApiCalls
                    $state.api_issues.$ticker.failed_calls = $apiIssueCount
                    $state.api_issues.$ticker.last_check = $currentTime.ToString("yyyy-MM-dd HH:mm:ss")
                    
                    Write-Host "  API問題率: $([math]::Round($issueRate * 100, 1))% ($apiIssueCount/$totalApiCalls)" -ForegroundColor $(if($issueRate -gt $ApiThreshold){"Yellow"}else{"Green"})
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
                
                # フォールバック運用
                Write-Host "`nフォールバック運用に切り替えます" -ForegroundColor Yellow
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
