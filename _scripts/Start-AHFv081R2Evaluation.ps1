# AHF v0.8.1-r2 評価実行スクリプト
# 固定4軸（①長期EV確度、②長期EV勾配、③現バリュエーション、④将来EVバリュ）の統合評価

param(
    [Parameter(Mandatory=$true)]
    [string]$Ticker,
    
    [Parameter(Mandatory=$false)]
    [string]$ConfigFile = $null,
    
    [Parameter(Mandatory=$false)]
    [switch]$Test,
    
    [Parameter(Mandatory=$false)]
    [switch]$Validation,
    
    [Parameter(Mandatory=$false)]
    [switch]$TurboScreen,
    
    [Parameter(Mandatory=$false)]
    [switch]$Verbose
)

# スクリプト情報
$ScriptName = "Start-AHFv081R2Evaluation"
$Version = "v0.8.1-r2"
$Purpose = "投資判断に直結する固定4軸で評価"
$MVP = "①②③④の名称と順序を絶対固定／T1 or T1*で確証（不足はn/a）／定型テーブル＋1行要約を即出力"

# ログ関数
function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp][$Level] $Message"
    
    if ($Verbose) {
        Write-Host $logMessage
    }
    
    # ログファイルに出力
    $logFile = "ahf/tickers/$Ticker/current/ahf_v081_r2_evaluation.log"
    Add-Content -Path $logFile -Value $logMessage -Encoding UTF8
}

# エラーハンドリング
function Handle-Error {
    param(
        [string]$ErrorMessage,
        [string]$ErrorCode = "UNKNOWN"
    )
    
    Write-Log "エラー発生: $ErrorMessage" "ERROR"
    Write-Log "エラーコード: $ErrorCode" "ERROR"
    
    # データギャップ記録
    $gapFile = "ahf/tickers/$Ticker/current/data_gap.json"
    $gapData = @{
        "timestamp" = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        "error_code" = $ErrorCode
        "error_message" = $ErrorMessage
        "ticker" = $Ticker
    }
    
    $gapData | ConvertTo-Json | Out-File -FilePath $gapFile -Encoding UTF8
    
    throw $ErrorMessage
}

# 環境変数チェック
function Test-EnvironmentVariables {
    Write-Log "環境変数チェック開始"
    
    $requiredVars = @(
        "AHF_DATASOURCE",
        "AHF_INTERNAL_BASEURL",
        "AHF_INTERNAL_TOKEN"
    )
    
    foreach ($var in $requiredVars) {
        if (-not (Get-Item "env:$var" -ErrorAction SilentlyContinue)) {
            Handle-Error "環境変数 $var が設定されていません" "ENV_VAR_MISSING"
        }
    }
    
    Write-Log "環境変数チェック完了"
}

# 設定読み込み
function Get-Configuration {
    param(
        [string]$ConfigFile
    )
    
    if ($ConfigFile -and (Test-Path $ConfigFile)) {
        Write-Log "設定ファイル読み込み: $ConfigFile"
        $config = Get-Content $ConfigFile | ConvertFrom-Json
    } else {
        Write-Log "デフォルト設定を使用"
        $config = @{
            "purpose" = $Purpose
            "mvp" = $MVP
            "axes" = @{
                "LEC" = "①長期EV確度"
                "NES" = "②長期EV勾配"
                "CURRENT_VAL" = "③現バリュエーション（機械）"
                "FUTURE_VAL" = "④将来EVバリュ（総合）"
            }
            "evidence_ladder" = @{
                "T1" = "一次（SEC/IR）"
                "T1_STAR" = "Corroborated二次（独立2源以上）"
                "T2" = "二次1源"
            }
            "workflow" = @{
                "intake" = $true
                "stage1_fast_screen" = $true
                "stage2_mini_confirm" = $true
                "stage3_alpha_maximization" = $true
                "decision" = $true
            }
            "validation" = @{
                "anchor_lint" = $true
                "anchor_lint_t1star" = $true
                "price_lint" = $true
                "math_guard" = $true
                "s3_lint" = $true
            }
            "output" = @{
                "format" = "json"
                "include_reports" = $true
                "save_files" = $true
            }
        }
    }
    
    return $config
}

# 統合評価実行
function Start-IntegratedEvaluation {
    param(
        [string]$Ticker,
        [hashtable]$Config
    )
    
    Write-Log "統合評価開始: $Ticker"
    
    try {
        # Pythonスクリプト実行
        $pythonScript = "ahf_v081_r2_integrated.py"
        $pythonPath = "python"
        
        # 引数構築
        $arguments = @($pythonScript, $Ticker)
        
        if ($ConfigFile) {
            $arguments += $ConfigFile
        }
        
        # 実行
        $result = & $pythonPath $arguments 2>&1
        
        if ($LASTEXITCODE -ne 0) {
            Handle-Error "Pythonスクリプト実行失敗: $result" "PYTHON_EXECUTION_FAILED"
        }
        
        Write-Log "統合評価完了"
        return $result
        
    } catch {
        Handle-Error "統合評価実行エラー: $($_.Exception.Message)" "INTEGRATED_EVALUATION_FAILED"
    }
}

# テスト実行
function Start-TestEvaluation {
    param(
        [string]$Ticker
    )
    
    Write-Log "テスト評価開始: $Ticker"
    
    try {
        # テストスクリプト実行
        $testScript = "test_ahf_v081_r2.py"
        $pythonPath = "python"
        
        $result = & $pythonPath $testScript $Ticker 2>&1
        
        if ($LASTEXITCODE -ne 0) {
            Handle-Error "テスト実行失敗: $result" "TEST_EXECUTION_FAILED"
        }
        
        Write-Log "テスト評価完了"
        return $result
        
    } catch {
        Handle-Error "テスト評価実行エラー: $($_.Exception.Message)" "TEST_EVALUATION_FAILED"
    }
}

# バリデーション実行
function Start-ValidationEvaluation {
    param(
        [string]$Ticker
    )
    
    Write-Log "バリデーション評価開始: $Ticker"
    
    try {
        # バリデーションスクリプト実行
        $validationScripts = @(
            "ahf_v081_r2_anchor_lint.py",
            "ahf_v081_r2_math_guard.py",
            "ahf_v081_r2_s3_lint.py"
        )
        
        $results = @()
        
        foreach ($script in $validationScripts) {
            Write-Log "バリデーション実行: $script"
            
            $result = & python $script "ahf/tickers/$Ticker/current/input.json" 2>&1
            
            if ($LASTEXITCODE -ne 0) {
                Write-Log "バリデーション失敗: $script - $result" "WARNING"
            } else {
                Write-Log "バリデーション成功: $script"
            }
            
            $results += $result
        }
        
        Write-Log "バリデーション評価完了"
        return $results
        
    } catch {
        Handle-Error "バリデーション評価実行エラー: $($_.Exception.Message)" "VALIDATION_EVALUATION_FAILED"
    }
}

# Turbo Screen実行
function Start-TurboScreenEvaluation {
    param(
        [string]$Ticker
    )
    
    Write-Log "Turbo Screen評価開始: $Ticker"
    
    try {
        # Turbo Screenスクリプト実行
        $turboScript = "ahf_v081_r2_turbo_screen.py"
        $pythonPath = "python"
        
        $result = & $pythonPath $turboScript $Ticker 2>&1
        
        if ($LASTEXITCODE -ne 0) {
            Handle-Error "Turbo Screen実行失敗: $result" "TURBO_SCREEN_EXECUTION_FAILED"
        }
        
        Write-Log "Turbo Screen評価完了"
        return $result
        
    } catch {
        Handle-Error "Turbo Screen評価実行エラー: $($_.Exception.Message)" "TURBO_SCREEN_EVALUATION_FAILED"
    }
}

# メイン実行
function Main {
    Write-Log "AHF v0.8.1-r2 評価開始"
    Write-Log "銘柄: $Ticker"
    Write-Log "目的: $Purpose"
    Write-Log "MVP: $MVP"
    
    try {
        # 環境変数チェック
        Test-EnvironmentVariables
        
        # 設定読み込み
        $config = Get-Configuration -ConfigFile $ConfigFile
        
        # 出力ディレクトリ作成
        $outputDir = "ahf/tickers/$Ticker/current"
        if (-not (Test-Path $outputDir)) {
            New-Item -ItemType Directory -Path $outputDir -Force
            Write-Log "出力ディレクトリ作成: $outputDir"
        }
        
        # 実行モード判定
        if ($Test) {
            $result = Start-TestEvaluation -Ticker $Ticker
        } elseif ($Validation) {
            $result = Start-ValidationEvaluation -Ticker $Ticker
        } elseif ($TurboScreen) {
            $result = Start-TurboScreenEvaluation -Ticker $Ticker
        } else {
            $result = Start-IntegratedEvaluation -Ticker $Ticker -Config $config
        }
        
        # 結果出力
        if ($result) {
            Write-Log "評価結果:"
            Write-Host $result
            
            # 結果ファイル保存
            $resultFile = "$outputDir/ahf_v081_r2_result.json"
            $result | Out-File -FilePath $resultFile -Encoding UTF8
            Write-Log "結果ファイル保存: $resultFile"
        }
        
        Write-Log "AHF v0.8.1-r2 評価完了"
        
    } catch {
        Write-Log "評価実行エラー: $($_.Exception.Message)" "ERROR"
        exit 1
    }
}

# スクリプト実行
Main
