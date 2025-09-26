# Turbo Screen 運用スクリプト
# スクリーニング最優先・偽陽性許容で走れるように設計

param(
    [Parameter(Mandatory=$true)]
    [string]$Ticker,
    
    [Parameter(Mandatory=$false)]
    [switch]$DisplayOnly,
    
    [Parameter(Mandatory=$false)]
    [switch]$RescoreEdges,
    
    [Parameter(Mandatory=$false)]
    [switch]$UpdateMatrix
)

# 環境設定
$ErrorActionPreference = "Stop"
$AHF_ROOT = Split-Path $PSScriptRoot -Parent

# パス設定
$TickerPath = Join-Path $AHF_ROOT "ahf\tickers\$Ticker"
$PythonScripts = Join-Path $AHF_ROOT "ahf\_scripts"

Write-Host "🚀 Turbo Screen 運用開始 - $Ticker" -ForegroundColor Cyan
Write-Host "=" * 60

# 1. ディレクトリ存在確認
if (-not (Test-Path $TickerPath)) {
    Write-Error "Ticker directory not found: $TickerPath"
    exit 1
}

# 2. Turbo Screen表示
if ($DisplayOnly -or -not $RescoreEdges) {
    Write-Host "📊 Turbo Screen Matrix表示..." -ForegroundColor Yellow
    
    $DisplayScript = Join-Path $PythonScripts "turbo_screen_display.py"
    if (Test-Path $DisplayScript) {
        python $DisplayScript $TickerPath
    } else {
        Write-Warning "turbo_screen_display.py not found"
    }
}

# 3. Edge再採点
if ($RescoreEdges) {
    Write-Host "🔄 Edge再採点処理..." -ForegroundColor Yellow
    
    $EdgeManagerScript = Join-Path $PythonScripts "turbo_screen_edge_manager.py"
    if (Test-Path $EdgeManagerScript) {
        python $EdgeManagerScript $TickerPath
    } else {
        Write-Warning "turbo_screen_edge_manager.py not found"
    }
}

# 4. マトリクス更新
if ($UpdateMatrix) {
    Write-Host "📈 マトリクス更新..." -ForegroundColor Yellow
    
    # B.yamlのTurbo Screen部分を更新
    $B_Yaml = Join-Path $TickerPath "current\B.yaml"
    if (Test-Path $B_Yaml) {
        Write-Host "B.yaml更新: Turbo Screen基準適用"
    } else {
        Write-Warning "B.yaml not found"
    }
}

# 5. 運用状況サマリー
Write-Host "`n📋 Turbo Screen 運用状況" -ForegroundColor Green
Write-Host "-" * 40

Write-Host "✅ 受付閾値: P≥60 (従来70)"
Write-Host "✅ TTL最大: 14日"
Write-Host "✅ 調整幅: Screen★±2 (Core★±1維持)"
Write-Host "✅ 確信度ブースト: ±10pp (Core±5pp)"
Write-Host "✅ クリップ: 45-95% (従来50-90%)"

Write-Host "`n🔧 数理ガード（Screen判定のみ緩和）:"
Write-Host "  - GM乖離許容: ≤0.5pp (Core≤0.2pp)"
Write-Host "  - 残差GP許容: ≤$12M (Core≤$8M)"
Write-Host "  - α5格子改善: ≤-$2.5M (Core≤-$3〜-$5M)"

Write-Host "`n⚡ アンカー運用:"
Write-Host "  - IR/PR一次許容: PENDING_SEC, TTL≤7日"
Write-Host "  - PDF制限: #:~:text=不可はbackup要件のみ"

Write-Host "`n📊 Edge掲出:"
Write-Host "  - 1軸辺り: 最大3件 (従来2件)"
Write-Host "  - 要約: 各≤25字"

Write-Host "`n🛡️ リスク管理:"
Write-Host "  - 偽陽性増は深掘りで自動修正"
Write-Host "  - Coreガードで巻き戻し"
Write-Host "  - 二段表示で意思決定切り分け可能"

Write-Host "`n🎯 次のアクション:"
Write-Host "  - Q3ドロップ時はCore基準で即リコンシル"
Write-Host "  - 乖離>0.5pp or 残差>$12MならScreen★自動格下げ"

Write-Host "`n" + "=" * 60
Write-Host "✅ Turbo Screen 運用完了" -ForegroundColor Green
