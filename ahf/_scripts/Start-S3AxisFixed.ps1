# S3-Axis-Fixed PowerShellランチャー
# ①②③の軸ルールに完全準拠（Ro40は②のみ、③は体温計：ピア×逆DCFのみ）

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

function Show-S3AxisFixedHelp {
    Write-Host @"
S3-Axis-Fixed PowerShellランチャー
①②③の軸ルールに完全準拠（Ro40は②のみ、③は体温計：ピア×逆DCFのみ）

使用方法:
  .\Start-S3AxisFixed.ps1 -Action <action> [parameters]

アクション:
  create    - カード作成（軸ルール準拠）
  process   - カード処理（Lint→RUN登録）
  evaluate  - カード評価
  status    - ワークフロー状況
  summary   - カード要約
  axis2     - ②長期EV勾配（NES計算、Ro40はここにのみ影響）
  axis3     - ③バリュエーション＋認知ギャップ（体温計：ピア×逆DCFのみ）
  data_gap  - data_gap表示（不足はn/aで可視化）

例:
  .\Start-S3AxisFixed.ps1 -Action axis2 -QQPct 17.48 -GuidanceRevisionPct 0 -OrderBacklogPct 0 -MarginChangeBps 0 -Ro40 45.0
  .\Start-S3AxisFixed.ps1 -Action axis3 -EvSActual 5.0 -EvSPeerMedian 5.0 -EvSFair 5.0
"@
}

function Start-S3AxisFixed {
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
    $pythonScript = "ahf/_scripts/s3_axis_fixed.py"
    
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
    Show-S3AxisFixedHelp
} else {
    Start-S3AxisFixed -Action $Action -CardId $CardId -Hypothesis $Hypothesis -Evidence $Evidence -TestFormula $TestFormula -TTLDays $TTLDays -ImpactNotes $ImpactNotes -QQPct $QQPct -GuidanceRevisionPct $GuidanceRevisionPct -OrderBacklogPct $OrderBacklogPct -MarginChangeBps $MarginChangeBps -Ro40 $Ro40 -EvSActual $EvSActual -EvSPeerMedian $EvSPeerMedian -EvSFair $EvSFair -TestResult $TestResult
}
