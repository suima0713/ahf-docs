# S3-Enhanced PowerShellランチャー
# Stage-3拡張システム実行（NES+Health_term + ③バリュエーション＋認知ギャップ）

param(
    [Parameter(Mandatory=$false)]
    [string]$Action = "help",
    
    [Parameter(Mandatory=$false)]
    [string]$CardId = "",
    
    [Parameter(Mandatory=$false)]
    [string]$Hypothesis = "",
    
    [Parameter(Mandatory=$false)]
    [string]$Evidence = "",
    
    [Parameter(Mandatory=$false)]
    [string]$TestFormula = "",
    
    [Parameter(Mandatory=$false)]
    [int]$TTLDays = 30,
    
    [Parameter(Mandatory=$false)]
    [string]$ImpactNotes = "",
    
    [Parameter(Mandatory=$false)]
    [double]$QQPct = 0,
    
    [Parameter(Mandatory=$false)]
    [double]$GuidanceRevisionPct = 0,
    
    [Parameter(Mandatory=$false)]
    [double]$OrderBacklogPct = 0,
    
    [Parameter(Mandatory=$false)]
    [double]$MarginChangeBps = 0,
    
    [Parameter(Mandatory=$false)]
    [double]$Ro40 = 0,
    
    [Parameter(Mandatory=$false)]
    [double]$EvSActual = 0,
    
    [Parameter(Mandatory=$false)]
    [double]$EvSPeerMedian = 0,
    
    [Parameter(Mandatory=$false)]
    [double]$EvSFair = 0,
    
    [Parameter(Mandatory=$false)]
    [bool]$TestResult = $false
)

function Show-S3EnhancedHelp {
    Write-Host @"
S3-Enhanced PowerShellランチャー
Stage-3拡張システム実行（NES+Health_term + ③バリュエーション＋認知ギャップ）

使用方法:
  .\Start-S3Enhanced.ps1 -Action <action> [parameters]

アクション:
  create    - カード作成（拡張版）
  process   - カード処理（Lint→RUN登録）
  evaluate  - カード評価
  status    - ワークフロー状況
  summary   - カード要約
  nes       - NES計算表示（Health_term含む）
  valuation - バリュエーション計算表示

例:
  .\Start-S3Enhanced.ps1 -Action create -CardId "TEST001" -Hypothesis "Q3売上成長率が17%を超える" -Evidence "ガイダンス中点`$121M、直前Q`$103Mだから→q/q%=17.48% #:~:text=Revenue" -TestFormula "q_q_pct >= 17" -TTLDays 30 -QQPct 17.48 -Ro40 45.0 -EvSActual 5.0 -EvSPeerMedian 5.0 -EvSFair 5.0
"@
}

function Start-S3Enhanced {
    param(
        [string]$Action,
        [string]$CardId,
        [string]$Hypothesis,
        [string]$Evidence,
        [string]$TestFormula,
        [int]$TTLDays,
        [string]$ImpactNotes,
        [double]$QQPct,
        [double]$GuidanceRevisionPct,
        [double]$OrderBacklogPct,
        [double]$MarginChangeBps,
        [double]$Ro40,
        [double]$EvSActual,
        [double]$EvSPeerMedian,
        [double]$EvSFair,
        [bool]$TestResult
    )
    
    # Pythonスクリプト実行
    $pythonScript = "ahf/_scripts/s3_enhanced.py"
    
    if (-not (Test-Path $pythonScript)) {
        Write-Error "Pythonスクリプトが見つかりません: $pythonScript"
        return
    }
    
    # パラメータ構築
    $params = @{
        "action" = $Action
        "card_id" = $CardId
        "hypothesis" = $Hypothesis
        "evidence" = $Evidence
        "test_formula" = $TestFormula
        "ttl_days" = $TTLDays
        "impact_notes" = $ImpactNotes
        "q_q_pct" = $QQPct
        "guidance_revision_pct" = $GuidanceRevisionPct
        "order_backlog_pct" = $OrderBacklogPct
        "margin_change_bps" = $MarginChangeBps
        "ro40" = $Ro40
        "ev_s_actual" = $EvSActual
        "ev_s_peer_median" = $EvSPeerMedian
        "ev_s_fair" = $EvSFair
        "test_result" = $TestResult
    }
    
    # JSON形式でパラメータを渡す
    $jsonParams = $params | ConvertTo-Json -Compress
    $jsonParams = $jsonParams -replace '"', '\"'
    
    # Python実行
    $command = "python $pythonScript --params '$jsonParams'"
    Invoke-Expression $command
}

# メイン処理
if ($Action -eq "help") {
    Show-S3EnhancedHelp
} else {
    Start-S3Enhanced -Action $Action -CardId $CardId -Hypothesis $Hypothesis -Evidence $Evidence -TestFormula $TestFormula -TTLDays $TTLDays -ImpactNotes $ImpactNotes -QQPct $QQPct -GuidanceRevisionPct $GuidanceRevisionPct -OrderBacklogPct $OrderBacklogPct -MarginChangeBps $MarginChangeBps -Ro40 $Ro40 -EvSActual $EvSActual -EvSPeerMedian $EvSPeerMedian -EvSFair $EvSFair -TestResult $TestResult
}
