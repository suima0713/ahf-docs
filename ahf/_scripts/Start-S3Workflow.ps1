# S3-Workflow PowerShellランチャー
# Stage-3即日運用フロー実行

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
    [bool]$TestResult = $false
)

function Show-S3Help {
    Write-Host @"
S3-Workflow PowerShellランチャー
Stage-3即日運用フロー実行

使用方法:
  .\Start-S3Workflow.ps1 -Action <action> [parameters]

アクション:
  create    - カード作成
  process   - カード処理（Lint→RUN登録）
  evaluate  - カード評価
  status    - ワークフロー状況
  summary   - カード要約
  export    - カードエクスポート
  import    - カードインポート

例:
  .\Start-S3Workflow.ps1 -Action create -CardId "TEST001" -Hypothesis "Q3売上成長率が17%を超える" -Evidence "ガイダンス中点`$121M、直前Q`$103Mだから→q/q%=17.48% #:~:text=Revenue" -TestFormula "q_q_pct >= 17" -TTLDays 30 -QQPct 17.48
"@
}

function Start-S3Workflow {
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
        [bool]$TestResult
    )
    
    # Pythonスクリプト実行
    $pythonScript = "ahf/_scripts/s3_workflow.py"
    
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
        "test_result" = $TestResult
    }
    
    # JSON形式でパラメータを渡す
    $jsonParams = $params | ConvertTo-Json -Compress
    $jsonParams = $jsonParams -replace '"', '\"'
    
    # Python実行
    $command = "python3 $pythonScript --params '$jsonParams'"
    Invoke-Expression $command
}

# メイン処理
if ($Action -eq "help") {
    Show-S3Help
} else {
    Start-S3Workflow -Action $Action -CardId $CardId -Hypothesis $Hypothesis -Evidence $Evidence -TestFormula $TestFormula -TTLDays $TTLDays -ImpactNotes $ImpactNotes -QQPct $QQPct -GuidanceRevisionPct $GuidanceRevisionPct -OrderBacklogPct $OrderBacklogPct -MarginChangeBps $MarginChangeBps -TestResult $TestResult
}
