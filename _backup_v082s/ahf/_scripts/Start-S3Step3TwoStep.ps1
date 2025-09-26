# S3-Step3-TwoStep PowerShellランチャー
# ③バリュエーション＋認知ギャップ｜Two-Step v1.0

param(
    [Parameter(Mandatory=$false)]
    [string]$Action = "help",
    
    [Parameter(Mandatory=$false)]
    [double]$EvSActual = 0,
    
    [Parameter(Mandatory=$false)]
    [double]$EvSPeerMedian = 0,
    
    [Parameter(Mandatory=$false)]
    [double]$GFwd = 0,
    
    [Parameter(Mandatory=$false)]
    [double]$OPMFwd = 0,
    
    [Parameter(Mandatory=$false)]
    [double]$GPeerMedian = 0,
    
    [Parameter(Mandatory=$false)]
    [string]$Evidence = "",
    
    [Parameter(Mandatory=$false)]
    [string]$ActualDate = "",
    
    [Parameter(Mandatory=$false)]
    [string]$ActualSource = ""
)

function Show-S3Step3TwoStepHelp {
    Write-Host @"
S3-Step3-TwoStep PowerShellランチャー
③バリュエーション＋認知ギャップ｜Two-Step v1.0

使用方法:
  .\Start-S3Step3TwoStep.ps1 -Action <action> [parameters]

アクション:
  step1     - Step-1｜フェアバリュー差（割安/割高の素点）
  step2     - Step-2｜適正性チェック（期待成長/認知ギャップで妥当性を判断）
  complete  - ③バリュエーション＋認知ギャップの完全評価
  lint      - S3-Lint ③（追加の最小チェック）

例:
  .\Start-S3Step3TwoStep.ps1 -Action complete -EvSActual 5.0 -EvSPeerMedian 5.0 -GFwd 15.0 -OPMFwd 5.0 -GPeerMedian 12.0 -Evidence "raises guidance, began volume shipments #:~:text=raises%20guidance" -ActualDate "2025-09-19" -ActualSource "Yahoo Finance"
"@
}

function Start-S3Step3TwoStep {
    param(
        [string]$Action,
        [double]$EvSActual,
        [double]$EvSPeerMedian,
        [double]$GFwd,
        [double]$OPMFwd,
        [double]$GPeerMedian,
        [string]$Evidence,
        [string]$ActualDate,
        [string]$ActualSource
    )
    
    # Pythonスクリプト実行
    $pythonScript = "ahf/_scripts/s3_step3_twostep.py"
    
    if (-not (Test-Path $pythonScript)) {
        Write-Error "Pythonスクリプトが見つかりません: $pythonScript"
        return
    }
    
    # パラメータ構築
    $params = @{
        "action" = $Action
        "ev_s_actual" = $EvSActual
        "ev_s_peer_median" = $EvSPeerMedian
        "g_fwd" = $GFwd
        "opm_fwd" = $OPMFwd
        "g_peer_median" = $GPeerMedian
        "evidence" = $Evidence
        "actual_date" = $ActualDate
        "actual_source" = $ActualSource
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
    Show-S3Step3TwoStepHelp
} else {
    Start-S3Step3TwoStep -Action $Action -EvSActual $EvSActual -EvSPeerMedian $EvSPeerMedian -GFwd $GFwd -OPMFwd $OPMFwd -GPeerMedian $GPeerMedian -Evidence $Evidence -ActualDate $ActualDate -ActualSource $ActualSource
}
