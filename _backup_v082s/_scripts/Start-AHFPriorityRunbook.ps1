# AHF Priority Runbook v0.3.2a
# 優先順位チェックリストのPowerShellスクリプト

param(
    [Parameter(Mandatory=$true)]
    [string]$Ticker,
    
    [Parameter(Mandatory=$false)]
    [string]$Action = "check"
)

function Start-AHFPriorityRunbook {
    param(
        [string]$Ticker,
        [string]$Action
    )
    
    $tickerPath = "ahf/tickers/$Ticker/current"
    
    if (-not (Test-Path $tickerPath)) {
        Write-Error "ティッカーディレクトリが見つかりません: $tickerPath"
        return
    }
    
    $triageFile = Join-Path $tickerPath "triage.json"
    $backlogFile = Join-Path $tickerPath "backlog.md"
    $factsFile = Join-Path $tickerPath "facts.md"
    $impactCardsFile = Join-Path $tickerPath "impact_cards.json"
    
    switch ($Action) {
        "check" {
            Show-PriorityChecklist -TickerPath $tickerPath
        }
        "ingest" {
            Start-DataIngestion -TickerPath $tickerPath
        }
        "t1-promote" {
            Start-T1Promotion -TickerPath $tickerPath
        }
        "matrix" {
            Start-MatrixCalculation -TickerPath $tickerPath
        }
        "ttl-check" {
            Start-TTLCheck -TickerPath $tickerPath
        }
        "guidance-track" {
            Start-GuidanceTracking -TickerPath $tickerPath
        }
        default {
            Write-Host "利用可能なアクション: check, ingest, t1-promote, matrix, ttl-check, guidance-track"
        }
    }
}

function Show-PriorityChecklist {
    param([string]$TickerPath)
    
    Write-Host "=== AHF Priority Runbook v0.3.2a ===" -ForegroundColor Green
    Write-Host "ティッカー: $(Split-Path $TickerPath -Leaf)" -ForegroundColor Yellow
    Write-Host ""
    
    # Step A: 取り込みチェック
    Write-Host "Step A | 取り込み（毎回すぐ）" -ForegroundColor Cyan
    $backlogFile = Join-Path $TickerPath "backlog.md"
    if (Test-Path $backlogFile) {
        $backlogContent = Get-Content $backlogFile -Raw
        $leadCount = ($backlogContent | Select-String "class=Lead" -AllMatches).Matches.Count
        Write-Host "  ✓ backlog.md: $leadCount 件のLead候補" -ForegroundColor Green
    } else {
        Write-Host "  ✗ backlog.md が見つかりません" -ForegroundColor Red
    }
    
    $triageFile = Join-Path $TickerPath "triage.json"
    if (Test-Path $triageFile) {
        $triageData = Get-Content $triageFile | ConvertFrom-Json
        $uncertainCount = $triageData.UNCERTAIN.Count
        Write-Host "  ✓ triage.json: $uncertainCount 件のUNCERTAIN" -ForegroundColor Green
    } else {
        Write-Host "  ✗ triage.json が見つかりません" -ForegroundColor Red
    }
    
    Write-Host ""
    
    # Step B: T1照合チェック
    Write-Host "Step B | T1照合（AUST満たすまで遅延容認）" -ForegroundColor Cyan
    if (Test-Path $triageFile) {
        $triageData = Get-Content $triageFile | ConvertFrom-Json
        $confirmedCount = $triageData.CONFIRMED.Count
        Write-Host "  ✓ CONFIRMED: $confirmedCount 件のT1確定" -ForegroundColor Green
        
        $austGaps = $triageData.UNCERTAIN | Where-Object { $_.aust_gaps.Count -le 1 }
        if ($austGaps) {
            Write-Host "  → T1昇格候補: $($austGaps.Count) 件" -ForegroundColor Yellow
        }
    }
    
    $factsFile = Join-Path $TickerPath "facts.md"
    if (Test-Path $factsFile) {
        $factsContent = Get-Content $factsFile -Raw
        $t1Count = ($factsContent | Select-String "\[T1-" -AllMatches).Matches.Count
        Write-Host "  ✓ facts.md: $t1Count 件のT1逐語" -ForegroundColor Green
    }
    
    Write-Host ""
    
    # Step C: マトリクス反映チェック
    Write-Host "Step C | マトリクス反映（影レンジ）" -ForegroundColor Cyan
    $matrixFile = Join-Path $TickerPath "matrix_results.json"
    if (Test-Path $matrixFile) {
        Write-Host "  ✓ matrix_results.json: 影レンジ算定済み" -ForegroundColor Green
    } else {
        Write-Host "  → マトリクス算定が必要" -ForegroundColor Yellow
    }
    
    Write-Host ""
    
    # Step D: TTL消化チェック
    Write-Host "Step D | TTL消化" -ForegroundColor Cyan
    if (Test-Path $triageFile) {
        $triageData = Get-Content $triageFile | ConvertFrom-Json
        $expiredCount = ($triageData.UNCERTAIN | Where-Object { $_.status -eq "expired" }).Count
        if ($expiredCount -gt 0) {
            Write-Host "  → TTL期限切れ: $expiredCount 件" -ForegroundColor Red
        } else {
            Write-Host "  ✓ TTL期限内" -ForegroundColor Green
        }
    }
    
    Write-Host ""
    
    # 優先順位表示
    Write-Host "優先順位（何を先にT1ロックするか）" -ForegroundColor Magenta
    Write-Host "1. KPI直撃：①量（Floor/RPO行）、②質（固定比率）" -ForegroundColor White
    Write-Host "2. 定義脚注：包含/除外の脚注・但し書き" -ForegroundColor White
    Write-Host "3. 反証に直結：Subsequent Events／8-K更新" -ForegroundColor White
    Write-Host "4. 評価直撃：EVの構成（現金/負債の最新化）" -ForegroundColor White
}

function Start-DataIngestion {
    param([string]$TickerPath)
    
    Write-Host "=== データ取り込み開始 ===" -ForegroundColor Green
    
    # backlog.mdに新規Lead追加の例
    $backlogFile = Join-Path $TickerPath "backlog.md"
    if (-not (Test-Path $backlogFile)) {
        Write-Host "backlog.mdを作成中..." -ForegroundColor Yellow
        Copy-Item "_templates/backlog.md" $backlogFile
    }
    
    Write-Host "backlog.mdに新規事実候補を1行追記してください" -ForegroundColor Yellow
    Write-Host "同期でtriage.json/UNCERTAINへ転記：credence_pctとttl_days付与" -ForegroundColor Yellow
}

function Start-T1Promotion {
    param([string]$TickerPath)
    
    Write-Host "=== T1昇格処理 ===" -ForegroundColor Green
    
    $triageFile = Join-Path $TickerPath "triage.json"
    if (Test-Path $triageFile) {
        Write-Host "credence計算とTTL管理を実行中..." -ForegroundColor Yellow
        python3 "_scripts/ahf_credence_manager.py" $triageFile
    }
}

function Start-MatrixCalculation {
    param([string]$TickerPath)
    
    Write-Host "=== マトリクス算定 ===" -ForegroundColor Green
    
    $triageFile = Join-Path $TickerPath "triage.json"
    $impactCardsFile = Join-Path $TickerPath "impact_cards.json"
    
    if ((Test-Path $triageFile) -and (Test-Path $impactCardsFile)) {
        Write-Host "影レンジ算定を実行中..." -ForegroundColor Yellow
        python3 "_scripts/ahf_matrix_calculator.py" $triageFile $impactCardsFile
    } else {
        Write-Host "必要なファイルが見つかりません" -ForegroundColor Red
    }
}

function Start-TTLCheck {
    param([string]$TickerPath)
    
    Write-Host "=== TTL消化チェック ===" -ForegroundColor Green
    
    $triageFile = Join-Path $TickerPath "triage.json"
    if (Test-Path $triageFile) {
        python3 "_scripts/ahf_credence_manager.py" $triageFile
    }
}

function Start-GuidanceTracking {
    param([string]$TickerPath)
    
    Write-Host "=== ガイダンス追跡 ===" -ForegroundColor Green
    
    $triageFile = Join-Path $TickerPath "triage.json"
    $impactCardsFile = Join-Path $TickerPath "impact_cards.json"
    
    if ((Test-Path $triageFile) -and (Test-Path $impactCardsFile)) {
        Write-Host "ガイダンス → 実績 → 資金配分の追跡を実行中..." -ForegroundColor Yellow
        python3 "_scripts/ahf_guidance_tracker.py" $TickerPath
    } else {
        Write-Host "必要なファイルが見つかりません" -ForegroundColor Red
    }
}

# メイン実行
Start-AHFPriorityRunbook -Ticker $Ticker -Action $Action

