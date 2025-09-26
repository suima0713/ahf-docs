# AHF v0.8.0 評価開始スクリプト
# 固定3軸（①長期EV確度、②長期EV勾配、③バリュエーション＋認知ギャップ）の評価実行

param(
    [Parameter(Mandatory=$true)]
    [string]$Ticker,
    
    [Parameter(Mandatory=$false)]
    [string]$ConfigFile = "",
    
    [Parameter(Mandatory=$false)]
    [switch]$Test = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$TurboScreen = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$Validation = $false
)

# スクリプトディレクトリ取得
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonScripts = Join-Path $ScriptDir "ahf_v080_*.py"

Write-Host "AHF v0.8.0 評価開始" -ForegroundColor Green
Write-Host "銘柄: $Ticker" -ForegroundColor Yellow
Write-Host "設定ファイル: $ConfigFile" -ForegroundColor Yellow
Write-Host "=" * 50

try {
    # テスト実行
    if ($Test) {
        Write-Host "テスト実行中..." -ForegroundColor Cyan
        python "$ScriptDir\test_ahf_v080.py"
        if ($LASTEXITCODE -ne 0) {
            throw "テスト実行失敗"
        }
        Write-Host "✅ テスト完了" -ForegroundColor Green
    }
    
    # バリデーション実行
    if ($Validation) {
        Write-Host "バリデーション実行中..." -ForegroundColor Cyan
        
        # AnchorLint
        Write-Host "  - AnchorLint実行中..." -ForegroundColor Gray
        $anchorLintData = @"
[
    {
        "id": "T1-001",
        "verbatim": "Free cash flow $150M for the quarter.",
        "url": "https://sec.gov/edgar/...",
        "anchor": "#:~:text=Free%20cash%20flow"
    }
]
"@
        $anchorLintData | Out-File -FilePath "$env:TEMP\anchor_lint_test.json" -Encoding UTF8
        python "$ScriptDir\ahf_v080_anchor_lint.py" "$env:TEMP\anchor_lint_test.json"
        
        # 数理ガード
        Write-Host "  - 数理ガード実行中..." -ForegroundColor Gray
        $mathGuardData = @"
[
    {
        "id": "MATH-001",
        "gm_actual": 0.75,
        "gm_expected": 0.73,
        "gp": 150000,
        "revenue": 200000,
        "gm": 0.75,
        "opex": 50000,
        "ot": 50.0
    }
]
"@
        $mathGuardData | Out-File -FilePath "$env:TEMP\math_guard_test.json" -Encoding UTF8
        python "$ScriptDir\ahf_v080_math_guard.py" "$env:TEMP\math_guard_test.json" "core"
        
        # S3-Lint
        Write-Host "  - S3-Lint実行中..." -ForegroundColor Gray
        $s3LintData = @"
[
    {
        "id": "S3-001",
        "t1_verbatim": "Guidance raised to $2.5B",
        "url_anchor": "https://sec.gov/...#:~:text=Guidance%20raised",
        "test_formula": "guidance_fy26_mid >= 2500",
        "ttl_days": 30,
        "reasoning": "ガイダンス上方修正は成長加速を示唆"
    }
]
"@
        $s3LintData | Out-File -FilePath "$env:TEMP\s3_lint_test.json" -Encoding UTF8
        python "$ScriptDir\ahf_v080_s3_lint.py" "$env:TEMP\s3_lint_test.json"
        
        Write-Host "✅ バリデーション完了" -ForegroundColor Green
    }
    
    # Turbo Screen実行
    if ($TurboScreen) {
        Write-Host "Turbo Screen実行中..." -ForegroundColor Cyan
        python "$ScriptDir\ahf_v080_turbo_screen.py" $Ticker
        if ($LASTEXITCODE -ne 0) {
            throw "Turbo Screen実行失敗"
        }
        Write-Host "✅ Turbo Screen完了" -ForegroundColor Green
    }
    
    # 統合評価実行
    Write-Host "統合評価実行中..." -ForegroundColor Cyan
    
    $configArgs = @()
    if ($ConfigFile -and (Test-Path $ConfigFile)) {
        $configArgs += $ConfigFile
    }
    
    python "$ScriptDir\ahf_v080_integrated.py" $Ticker @configArgs
    if ($LASTEXITCODE -ne 0) {
        throw "統合評価実行失敗"
    }
    
    Write-Host "✅ 統合評価完了" -ForegroundColor Green
    
    # 結果表示
    $outputDir = "ahf\tickers\$Ticker\current"
    if (Test-Path $outputDir) {
        Write-Host "`n出力ファイル:" -ForegroundColor Yellow
        Get-ChildItem $outputDir -Filter "*v080*" | ForEach-Object {
            Write-Host "  - $($_.Name)" -ForegroundColor Gray
        }
    }
    
    Write-Host "`n🎉 AHF v0.8.0 評価完了" -ForegroundColor Green
    
} catch {
    Write-Host "❌ エラー: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
} finally {
    # 一時ファイル削除
    if (Test-Path "$env:TEMP\anchor_lint_test.json") {
        Remove-Item "$env:TEMP\anchor_lint_test.json" -Force
    }
    if (Test-Path "$env:TEMP\math_guard_test.json") {
        Remove-Item "$env:TEMP\math_guard_test.json" -Force
    }
    if (Test-Path "$env:TEMP\s3_lint_test.json") {
        Remove-Item "$env:TEMP\s3_lint_test.json" -Force
    }
}

Write-Host "`n使用方法:" -ForegroundColor Cyan
Write-Host "  .\Start-AHFv080Evaluation.ps1 -Ticker AAPL" -ForegroundColor Gray
Write-Host "  .\Start-AHFv080Evaluation.ps1 -Ticker AAPL -Test" -ForegroundColor Gray
Write-Host "  .\Start-AHFv080Evaluation.ps1 -Ticker AAPL -Validation" -ForegroundColor Gray
Write-Host "  .\Start-AHFv080Evaluation.ps1 -Ticker AAPL -TurboScreen" -ForegroundColor Gray
Write-Host "  .\Start-AHFv080Evaluation.ps1 -Ticker AAPL -ConfigFile config.json" -ForegroundColor Gray

