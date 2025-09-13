# Test-AHFParity.ps1 - AHFデータパリティ検証スクリプト（v0.3）
# Internal vs Polygon データ整合性チェック
param(
    [Parameter(Mandatory)][string]$Ticker,
    [Parameter(Mandatory)][string]$From,   # "2024-01-01"
    [Parameter(Mandatory)][string]$To,     # "2025-09-13"
    [double]$CloseTolerance = 0.005,       # 0.50%
    [double]$CumulativeTolerance = 0.015,  # 1.50%
    [int]$BusinessDays = 5,                # 5営業日の累積差
    [string]$Root = ".\ahf"
)

Write-Host "=== AHFパリティ検証: $Ticker ===" -ForegroundColor Green
Write-Host "期間: $From ～ $To" -ForegroundColor Yellow
Write-Host "終値許容差: $($CloseTolerance * 100)%" -ForegroundColor Yellow
Write-Host "累積許容差: $($CumulativeTolerance * 100)% ($BusinessDays営業日)" -ForegroundColor Yellow

# ファイルパス構築
$internalPath = Join-Path $Root "tickers\$Ticker\attachments\providers\internal\prices_${From}_${To}.csv"
$polygonPath = Join-Path $Root "tickers\$Ticker\attachments\providers\polygon\prices_${From}_${To}.csv"

# ファイル存在確認
if (-not (Test-Path $internalPath)) {
    Write-Error "Internalデータファイルが見つかりません: $internalPath"
    exit 1
}

if (-not (Test-Path $polygonPath)) {
    Write-Error "Polygonデータファイルが見つかりません: $polygonPath"
    exit 1
}

Write-Host "`n=== データロード ===" -ForegroundColor Cyan
Write-Host "Internal: $internalPath" -ForegroundColor Gray
Write-Host "Polygon: $polygonPath" -ForegroundColor Gray

try {
    # データロード
    $internal = Import-Csv $internalPath
    $polygon = Import-Csv $polygonPath
    
    Write-Host "✓ Internal: $($internal.Count) 件" -ForegroundColor Green
    Write-Host "✓ Polygon: $($polygon.Count) 件" -ForegroundColor Green
    
    # 日付正規化（複数形式に対応）
    $internal | ForEach-Object {
        if ($_.date) {
            $_.ts = $_.date
        } elseif ($_.timestamp) {
            $_.ts = $_.timestamp.Split(' ')[0]  # 日付部分のみ抽出
        }
        # 数値型変換
        $_.close = [double]$_.close
        $_.volume = [double]$_.volume
    }
    
    $polygon | ForEach-Object {
        if ($_.date) {
            $_.ts = $_.date
        } elseif ($_.timestamp) {
            $_.ts = $_.timestamp.Split(' ')[0]  # 日付部分のみ抽出
        }
        # 数値型変換
        $_.close = [double]$_.close
        $_.volume = [double]$_.volume
    }
    
    # マージ処理
    Write-Host "`n=== データマージ ===" -ForegroundColor Cyan
    $merged = $internal | ForEach-Object {
        $intRow = $_
        $polyRow = $polygon | Where-Object { $_.ts -eq $intRow.ts }
        
        if ($polyRow) {
            [pscustomobject]@{
                ts = $intRow.ts
                close_int = $intRow.close
                close_pol = $polyRow.close
                volume_int = $intRow.volume
                volume_pol = $polyRow.volume
                price_diff_pct = if ($intRow.close -ne 0) { [math]::Abs(($intRow.close - $polyRow.close) / $intRow.close) } else { 0 }
            }
        }
    }
    
    if ($merged.Count -eq 0) {
        Write-Error "マッチするデータが見つかりません。日付形式を確認してください。"
        exit 1
    }
    
    Write-Host "✓ マッチデータ: $($merged.Count) 件" -ForegroundColor Green
    
    # パリティ検証
    Write-Host "`n=== パリティ検証 ===" -ForegroundColor Cyan
    
    # 1. 終値差チェック
    $closeViolations = $merged | Where-Object { $_.price_diff_pct -gt $CloseTolerance }
    $closeViolationCount = $closeViolations.Count
    $closeViolationPct = [math]::Round(($closeViolationCount / $merged.Count) * 100, 2)
    
    Write-Host "終値差違反: $closeViolationCount / $($merged.Count) 件 ($closeViolationPct%)" -ForegroundColor $(if($closeViolationCount -eq 0){"Green"}else{"Red"})
    
    # 2. 累積差チェック（連続5営業日）
    $cumulativeViolations = @()
    for ($i = 0; $i -le ($merged.Count - $BusinessDays); $i++) {
        $window = $merged[$i..($i + $BusinessDays - 1)]
        $cumulativeDiff = ($window | Measure-Object -Property price_diff_pct -Sum).Sum
        if ($cumulativeDiff -gt $CumulativeTolerance) {
            $cumulativeViolations += [pscustomobject]@{
                start_date = $window[0].ts
                end_date = $window[-1].ts
                cumulative_diff = [math]::Round($cumulativeDiff * 100, 2)
            }
        }
    }
    
    Write-Host "累積差違反: $($cumulativeViolations.Count) 期間" -ForegroundColor $(if($cumulativeViolations.Count -eq 0){"Green"}else{"Red"})
    
    # 3. ゼロ出来高チェック
    $zeroVolumeIssues = $merged | Where-Object { $_.volume_int -eq 0 -or $_.volume_pol -eq 0 }
    $zeroVolumeCount = $zeroVolumeIssues.Count
    Write-Host "ゼロ出来高: $zeroVolumeCount 件" -ForegroundColor $(if($zeroVolumeCount -eq 0){"Green"}else{"Yellow"})
    
    # 4. 非単調チェック（価格の異常な変動）
    $monotonicIssues = @()
    for ($i = 1; $i -lt $merged.Count; $i++) {
        $prev = $merged[$i-1]
        $curr = $merged[$i]
        
        # 価格の異常なジャンプ（50%以上）
        if ($prev.close_int -ne 0 -and $curr.close_int -ne 0) {
            $jump = [math]::Abs(($curr.close_int - $prev.close_int) / $prev.close_int)
            if ($jump -gt 0.5) {
                $monotonicIssues += [pscustomobject]@{
                    date = $curr.ts
                    prev_close = $prev.close_int
                    curr_close = $curr.close_int
                    jump_pct = [math]::Round($jump * 100, 2)
                }
            }
        }
    }
    
    Write-Host "非単調変動: $($monotonicIssues.Count) 件" -ForegroundColor $(if($monotonicIssues.Count -eq 0){"Green"}else{"Yellow"})
    
    # 総合判定
    Write-Host "`n=== 総合判定 ===" -ForegroundColor Cyan
    $isParityOk = ($closeViolationCount -eq 0) -and ($cumulativeViolations.Count -eq 0)
    
    if ($isParityOk) {
        Write-Host "✓ パリティ検証: OK" -ForegroundColor Green
        Write-Host "→ Polygonデータは昇格可能です" -ForegroundColor Green
        
        # 統計サマリー
        $avgDiff = [math]::Round(($merged | Measure-Object -Property price_diff_pct -Average).Average * 100, 3)
        $maxDiff = [math]::Round(($merged | Measure-Object -Property price_diff_pct -Maximum).Maximum * 100, 3)
        
        Write-Host "`n=== 統計サマリー ===" -ForegroundColor Cyan
        Write-Host "平均価格差: $avgDiff%" -ForegroundColor White
        Write-Host "最大価格差: $maxDiff%" -ForegroundColor White
        Write-Host "検証期間: $($merged[0].ts) ～ $($merged[-1].ts)" -ForegroundColor White
        
        exit 0
    } else {
        Write-Host "✗ パリティ検証: NG" -ForegroundColor Red
        Write-Host "→ Polygonデータは昇格不可です" -ForegroundColor Red
        
        # 詳細エラー表示
        if ($closeViolationCount -gt 0) {
            Write-Host "`n終値差違反詳細 (最初の5件):" -ForegroundColor Red
            $closeViolations | Select-Object -First 5 | ForEach-Object {
                Write-Host "  $($_.ts): Internal=$($_.close_int) Polygon=$($_.close_pol) 差=$([math]::Round($_.price_diff_pct * 100, 2))%" -ForegroundColor Red
            }
        }
        
        if ($cumulativeViolations.Count -gt 0) {
            Write-Host "`n累積差違反詳細:" -ForegroundColor Red
            $cumulativeViolations | ForEach-Object {
                Write-Host "  $($_.start_date) ～ $($_.end_date): 累積差=$($_.cumulative_diff)%" -ForegroundColor Red
            }
        }
        
        exit 1
    }
    
} catch {
    Write-Error "パリティ検証エラー: $($_.Exception.Message)"
    Write-Error "スタックトレース: $($_.Exception.StackTrace)"
    exit 1
}
