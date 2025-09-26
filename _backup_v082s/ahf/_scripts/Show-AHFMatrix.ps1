# AHF Matrix Display - ミニ運用ルール対応
# T1実線 + U点線レンジのマトリクス表示

param(
    [Parameter(Mandatory=$true)]
    [string]$Ticker,
    
    [Parameter(Mandatory=$false)]
    [string]$Path = "ahf/tickers/$Ticker/current/"
)

function Show-AHFMatrix {
    param(
        [string]$TickerPath
    )
    
    Write-Host "=== AHF マトリクス表示（T1実線 + U点線レンジ） ===" -ForegroundColor Cyan
    Write-Host ""
    
    # credence_shadow.jsonを読み込み
    $shadowFile = Join-Path $TickerPath "credence_shadow.json"
    if (-not (Test-Path $shadowFile)) {
        Write-Host "credence_shadow.jsonが見つかりません。先にcredence calculatorを実行してください。" -ForegroundColor Red
        return
    }
    
    try {
        $shadowData = Get-Content $shadowFile -Raw | ConvertFrom-Json
        
        # 影表示があるKPIのみ表示
        $shadowValues = $shadowData.shadow_values
        $hasShadow = $false
        
        foreach ($kpi in $shadowValues.PSObject.Properties.Name) {
            $data = $shadowValues.$kpi
            if ($data.shadow_range) {
                $hasShadow = $true
                
                Write-Host "【$kpi】" -ForegroundColor Yellow
                Write-Host "  T1実線: $($data.t1_value) $($data.t1_unit) (asof: $($data.t1_asof))" -ForegroundColor Green
                
                $shadowLow = $data.shadow_range.low
                $shadowHigh = $data.shadow_range.high
                $contribution = $data.shadow_range.credence_contribution
                
                Write-Host "  U点線レンジ: $shadowLow ～ $shadowHigh $($data.t1_unit)" -ForegroundColor Magenta
                Write-Host "  影寄与: +$($contribution.ToString('F1')) $($data.t1_unit) (確度込み)" -ForegroundColor Cyan
                
                if ($data.credence_contributions) {
                    Write-Host "  寄与元:" -ForegroundColor Gray
                    foreach ($contrib in $data.credence_contributions) {
                        Write-Host "    - $($contrib.kpi): $($contrib.claim) (確度$($contrib.credence_pct)%)" -ForegroundColor Gray
                    }
                }
                Write-Host ""
            }
        }
        
        if (-not $hasShadow) {
            Write-Host "影表示対象のKPIが見つかりません。" -ForegroundColor Yellow
        }
        
        # credenceデータのサマリー
        if ($shadowData.credence_data) {
            Write-Host "=== Credenceデータサマリー ===" -ForegroundColor Cyan
            foreach ($kpi in $shadowData.credence_data.PSObject.Properties.Name) {
                $credence = $shadowData.credence_data.$kpi
                Write-Host "• ${kpi}: $($credence.claim) (確度$($credence.credence_pct)%)" -ForegroundColor White
            }
            Write-Host ""
        }
        
    } catch {
        Write-Host "エラー: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# メイン処理
$tickerPath = if ($Path -eq "ahf/tickers/$Ticker/current/") {
    "ahf/tickers/$Ticker/current/"
} else {
    $Path
}

if (-not (Test-Path $tickerPath)) {
    Write-Host "パスが見つかりません: $tickerPath" -ForegroundColor Red
    exit 1
}

Show-AHFMatrix -TickerPath $tickerPath
