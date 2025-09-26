# S3-Box Rules PowerShellランチャー
# ①②③の軸ルールに完全準拠（過実装排除、守るべきことだけを固定）

param(
    [Parameter(Mandatory=$false)]
    [string]$Action = "help",
    
    [Parameter(Mandatory=$false)]
    [string]$Axis1Evidence = "",
    
    [Parameter(Mandatory=$false)]
    [int]$Axis1Score = 0,
    
    [Parameter(Mandatory=$false)]
    [double]$Axis1Confidence = 0.0,
    
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
    [double]$GFwd = 0,
    
    [Parameter(Mandatory=$false)]
    [double]$OPMFwd = 0
)

function Show-S3BoxRulesHelp {
    Write-Host @"
S3-Box Rules PowerShellランチャー
①②③の軸ルールに完全準拠（過実装排除、守るべきことだけを固定）

使用方法:
  .\Start-S3BoxRules.ps1 -Action <action> [parameters]

アクション:
  axis1     - ①長期EV確度（LEC）
  axis2     - ②長期EV勾配（NES）
  axis3     - ③バリュエーション＋認知ギャップ（体温計のみ）
  lint      - S3-Lint（強制チェック）
  data_gap  - data_gap表示（欠測はn/aで可視化）

例:
  .\Start-S3BoxRules.ps1 -Action axis1 -Axis1Evidence "completed the ATM… ~$98M #:~:text=completed%20the%20ATM" -Axis1Score 3 -Axis1Confidence 0.72
  .\Start-S3BoxRules.ps1 -Action axis2 -QQPct 17.48 -GuidanceRevisionPct 0 -OrderBacklogPct 0 -MarginChangeBps 0 -Ro40 45.0
  .\Start-S3BoxRules.ps1 -Action axis3 -EvSActual 5.0 -EvSPeerMedian 5.0 -GFwd 15.0 -OPMFwd 5.0
"@
}

function Start-S3BoxRules {
    param(
        [string]$Action,
        [string]$Axis1Evidence,
        [int]$Axis1Score,
        [double]$Axis1Confidence,
        [double]$QQPct,
        [double]$GuidanceRevisionPct,
        [double]$OrderBacklogPct,
        [double]$MarginChangeBps,
        [double]$Ro40,
        [double]$EvSActual,
        [double]$EvSPeerMedian,
        [double]$GFwd,
        [double]$OPMFwd
    )
    
    # Pythonスクリプト実行
    $pythonScript = "ahf/_scripts/s3_box_rules.py"
    
    if (-not (Test-Path $pythonScript)) {
        Write-Error "Pythonスクリプトが見つかりません: $pythonScript"
        return
    }
    
    # パラメータ構築
    $params = @{
        "action" = $Action
        "axis1_evidence" = $Axis1Evidence
        "axis1_score" = $Axis1Score
        "axis1_confidence" = $Axis1Confidence
        "q_q_pct" = $QQPct
        "guidance_revision_pct" = $GuidanceRevisionPct
        "order_backlog_pct" = $OrderBacklogPct
        "margin_change_bps" = $MarginChangeBps
        "ro40" = $Ro40
        "ev_s_actual" = $EvSActual
        "ev_s_peer_median" = $EvSPeerMedian
        "g_fwd" = $GFwd
        "opm_fwd" = $OPMFwd
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
    Show-S3BoxRulesHelp
} else {
    Start-S3BoxRules -Action $Action -Axis1Evidence $Axis1Evidence -Axis1Score $Axis1Score -Axis1Confidence $Axis1Confidence -QQPct $QQPct -GuidanceRevisionPct $GuidanceRevisionPct -OrderBacklogPct $OrderBacklogPct -MarginChangeBps $MarginChangeBps -Ro40 $Ro40 -EvSActual $EvSActual -EvSPeerMedian $EvSPeerMedian -GFwd $GFwd -OPMFwd $OPMFwd
}
