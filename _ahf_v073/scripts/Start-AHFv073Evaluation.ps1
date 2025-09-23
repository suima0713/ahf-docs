# AHF v0.7.3 統合評価実行スクリプト
# Purpose: 固定3軸評価システムの統合実行
# MVP: ①②③の名称と順序を毎回固定／T1で確証／定型テーブル＋1行要約で即時出力

param(
    [Parameter(Mandatory=$true)]
    [string]$Ticker,
    
    [Parameter(Mandatory=$false)]
    [string]$DataDir = "tickers",
    
    [Parameter(Mandatory=$false)]
    [switch]$Verbose
)

# スクリプト情報
$ScriptName = "Start-AHFv073Evaluation"
$Version = "0.7.3"
$Purpose = "投資判断に直結する固定3軸で評価する"
$MVP = "①②③の名称と順序を毎回固定／T1で確証／定型テーブル＋1行要約で即時出力"

Write-Host "=== $ScriptName v$Version ===" -ForegroundColor Cyan
Write-Host "Purpose: $Purpose" -ForegroundColor Yellow
Write-Host "MVP: $MVP" -ForegroundColor Yellow
Write-Host ""

# パラメータ検証
if (-not $Ticker) {
    Write-Error "Ticker parameter is required"
    exit 1
}

if (-not (Test-Path $DataDir)) {
    Write-Error "Data directory '$DataDir' does not exist"
    exit 1
}

$TickerPath = Join-Path $DataDir $Ticker
if (-not (Test-Path $TickerPath)) {
    Write-Error "Ticker directory '$TickerPath' does not exist"
    exit 1
}

$CurrentPath = Join-Path $TickerPath "current"
if (-not (Test-Path $CurrentPath)) {
    Write-Error "Current directory '$CurrentPath' does not exist"
    exit 1
}

# 必要なファイルの存在確認
$RequiredFiles = @(
    "facts.md",
    "triage.json"
)

$MissingFiles = @()
foreach ($File in $RequiredFiles) {
    $FilePath = Join-Path $CurrentPath $File
    if (-not (Test-Path $FilePath)) {
        $MissingFiles += $File
    }
}

if ($MissingFiles.Count -gt 0) {
    Write-Warning "Missing required files: $($MissingFiles -join ', ')"
    Write-Host "Creating placeholder files..."
    
    # facts.md作成
    if ("facts.md" -in $MissingFiles) {
        $FactsContent = @"
# T1確定事実（AUST満たすもののみ）

[YYYY-MM-DD][T1-F|T1-C][Core①|Core②|Core③|Time] "逐語≤40語" (impact: KPI) <URL>
"@
        $FactsPath = Join-Path $CurrentPath "facts.md"
        $FactsContent | Out-File -FilePath $FactsPath -Encoding UTF8
        Write-Host "Created: $FactsPath"
    }
    
    # triage.json作成
    if ("triage.json" -in $MissingFiles) {
        $TriageContent = @{
            "as_of" = (Get-Date).ToString("yyyy-MM-dd")
            "CONFIRMED" = @()
            "UNCERTAIN" = @()
            "HYPOTHESES" = @()
        } | ConvertTo-Json -Depth 3
        $TriagePath = Join-Path $CurrentPath "triage.json"
        $TriageContent | Out-File -FilePath $TriagePath -Encoding UTF8
        Write-Host "Created: $TriagePath"
    }
}

# Python実行環境確認
try {
    $PythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found"
    }
    Write-Host "Python環境: $PythonVersion" -ForegroundColor Green
} catch {
    Write-Error "Python not found or not in PATH"
    exit 1
}

# 必要なPythonモジュールの確認
$RequiredModules = @("yaml", "json", "datetime", "typing")
$MissingModules = @()

foreach ($Module in $RequiredModules) {
    try {
        python -c "import $Module" 2>$null
        if ($LASTEXITCODE -ne 0) {
            $MissingModules += $Module
        }
    } catch {
        $MissingModules += $Module
    }
}

if ($MissingModules.Count -gt 0) {
    Write-Warning "Missing Python modules: $($MissingModules -join ', ')"
    Write-Host "Installing required modules..."
    
    foreach ($Module in $MissingModules) {
        if ($Module -eq "yaml") {
            pip install PyYAML
        }
    }
}

# 統合評価実行
Write-Host "=== AHF v0.7.3 統合評価開始: $Ticker ===" -ForegroundColor Cyan
Write-Host ""

try {
    # Python統合スクリプト実行
    $PythonScript = Join-Path $PSScriptRoot "ahf_v073_integrated.py"
    $Arguments = @($Ticker, $DataDir)
    
    if ($Verbose) {
        Write-Host "実行コマンド: python `"$PythonScript`" $($Arguments -join ' ')" -ForegroundColor Gray
    }
    
    $Process = Start-Process -FilePath "python" -ArgumentList $PythonScript, $Arguments -Wait -PassThru -NoNewWindow
    
    if ($Process.ExitCode -eq 0) {
        Write-Host ""
        Write-Host "=== AHF v0.7.3 統合評価完了 ===" -ForegroundColor Green
        Write-Host "ティッカー: $Ticker" -ForegroundColor White
        Write-Host "結果ファイル: $CurrentPath\ahf_v073_output.json" -ForegroundColor White
        
        # 結果ファイルの存在確認
        $OutputFile = Join-Path $CurrentPath "ahf_v073_output.json"
        if (Test-Path $OutputFile) {
            $OutputContent = Get-Content $OutputFile -Raw | ConvertFrom-Json
            Write-Host "判定: $($OutputContent.decision.decision_type)" -ForegroundColor Yellow
            Write-Host "DI: $($OutputContent.decision.di_score)" -ForegroundColor Yellow
            Write-Host "サイズ: $($OutputContent.decision.size_pct)%" -ForegroundColor Yellow
        }
        
    } else {
        Write-Error "統合評価実行失敗 (Exit Code: $($Process.ExitCode))"
        exit $Process.ExitCode
    }
    
} catch {
    Write-Error "統合評価実行エラー: $($_.Exception.Message)"
    exit 1
}

# 後処理
Write-Host ""
Write-Host "=== 後処理 ===" -ForegroundColor Cyan

# 生成されたファイルの確認
$GeneratedFiles = @(
    "ahf_v073_output.json",
    "A.yaml",
    "B.yaml", 
    "C.yaml"
)

foreach ($File in $GeneratedFiles) {
    $FilePath = Join-Path $CurrentPath $File
    if (Test-Path $FilePath) {
        Write-Host "✓ $File" -ForegroundColor Green
    } else {
        Write-Host "✗ $File (未生成)" -ForegroundColor Red
    }
}

# スナップショット作成の提案
Write-Host ""
Write-Host "=== 次のステップ ===" -ForegroundColor Cyan
Write-Host "1. 結果を確認: Get-Content `"$CurrentPath\ahf_v073_output.json`" | ConvertFrom-Json"
Write-Host "2. スナップショット作成: New-AHFSnapshot -Ticker $Ticker"
Write-Host "3. レッドライン適用: python ahf_apply_redlines.py `"$CurrentPath\forensic.json`""

Write-Host ""
Write-Host "=== $ScriptName 完了 ===" -ForegroundColor Cyan
