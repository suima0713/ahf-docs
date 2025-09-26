# S3-Step3-Essence PowerShellランチャー
# ③二段構え（最小・実戦用）の本質実装

param(
    [Parameter(Mandatory=$false)]
    [string]$Action = "help",
    
    [Parameter(Mandatory=$false)]
    [double]$PEActual = 0,
    
    [Parameter(Mandatory=$false)]
    [double]$PEPeerMedian = 0,
    
    [Parameter(Mandatory=$false)]
    [double]$GFwd = 0,
    
    [Parameter(Mandatory=$false)]
    [double]$OPMFwd = 0,
    
    [Parameter(Mandatory=$false)]
    [double]$GPeerMedian = 0,
    
    [Parameter(Mandatory=$false)]
    [string]$Evidence = "",
    
    [Parameter(Mandatory=$false)]
    [double]$PETarget = 25,
    
    [Parameter(Mandatory=$false)]
    [double]$Hurdle = 0.12
)

function Show-S3Step3EssenceHelp {
    Write-Host @"
S3-Step3-Essence PowerShellランチャー
③二段構え（最小・実戦用）の本質実装

使用方法:
  .\Start-S3Step3Essence.ps1 -Action <action> [parameters]

アクション:
  step1     - Step-1｜フェアバリュー差（素点）
  step2     - Step-2｜妥当性チェック（期待の正当性）
  essence   - ③二段構え（最小・実戦用）の完全評価
  high_per  - 高PER分析（逆DCFライト）
  evidence  - 証拠基準評価

例:
  .\Start-S3Step3Essence.ps1 -Action essence -PEActual 60.0 -PEPeerMedian 25.0 -GFwd 30.0 -OPMFwd 15.0 -GPeerMedian 20.0 -Evidence "ガイダンス上方, 実出荷, 前受, 契約負債↑, NRR/GRR, LTV/CAC>3, 10%超顧客分散 #:~:text=ガイダンス上方"
  .\Start-S3Step3Essence.ps1 -Action high_per -PEActual 100.0 -PETarget 25.0 -Hurdle 0.12
"@
}

function Start-S3Step3Essence {
    param(
        [string]$Action,
        [double]$PEActual,
        [double]$PEPeerMedian,
        [double]$GFwd,
        [double]$OPMFwd,
        [double]$GPeerMedian,
        [string]$Evidence,
        [double]$PETarget,
        [double]$Hurdle
    )
    
    # Pythonスクリプト実行
    $pythonScript = "ahf/_scripts/s3_step3_essence.py"
    
    if (-not (Test-Path $pythonScript)) {
        Write-Error "Pythonスクリプトが見つかりません: $pythonScript"
        return
    }
    
    # パラメータ構築
    $params = @{
        "action" = $Action
        "pe_actual" = $PEActual
        "pe_peer_median" = $PEPeerMedian
        "g_fwd" = $GFwd
        "opm_fwd" = $OPMFwd
        "g_peer_median" = $GPeerMedian
        "evidence" = $Evidence
        "pe_target" = $PETarget
        "hurdle" = $Hurdle
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
    Show-S3Step3EssenceHelp
} else {
    Start-S3Step3Essence -Action $Action -PEActual $PEActual -PEPeerMedian $PEPeerMedian -GFwd $GFwd -OPMFwd $OPMFwd -GPeerMedian $GPeerMedian -Evidence $Evidence -PETarget $PETarget -Hurdle $Hurdle
}
