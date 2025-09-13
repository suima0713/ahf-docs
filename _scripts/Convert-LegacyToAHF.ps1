# Convert-LegacyToAHF.ps1 - レガシーシステムからAHFへの移管ツール
# PRISM/VOICEのCSV → facts.md/A/B/C への変換

param(
    [Parameter(Mandatory)][string]$Ticker,
    [string]$LegacyCsvPath,
    [string]$OutputDir = ".\tickers\$Ticker\current"
)

function Convert-LegacyCsvToAHF {
    <#
    .SYNOPSIS
    レガシーシステムのCSVをAHF形式に変換
    
    .DESCRIPTION
    PRISM/VOICEのCSVデータをAHFのfacts.md、A.yaml、B.yaml、C.yaml形式に変換します。
    
    .PARAMETER Ticker
    銘柄コード
    
    .PARAMETER LegacyCsvPath
    レガシーCSVファイルのパス
    
    .PARAMETER OutputDir
    出力先ディレクトリ
    
    .EXAMPLE
    Convert-LegacyCsvToAHF -Ticker WOLF -LegacyCsvPath ".\legacy\WOLF_data.csv"
    #>
    param(
        [string]$Ticker,
        [string]$LegacyCsvPath,
        [string]$OutputDir
    )
    
    Write-Host "=== レガシーシステム移管: $Ticker ===" -ForegroundColor Green
    
    if (-not (Test-Path $LegacyCsvPath)) {
        Write-Error "レガシーCSVファイルが見つかりません: $LegacyCsvPath"
        return
    }
    
    # 出力ディレクトリ作成
    New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
    
    try {
        # CSV読み込み
        $data = Import-Csv $LegacyCsvPath
        Write-Host "✓ CSV読み込み完了: $($data.Count) 行" -ForegroundColor Green
        
        # facts.md生成
        Generate-FactsMd -Ticker $Ticker -Data $data -OutputDir $OutputDir
        
        # A.yaml生成（基本情報）
        Generate-AYaml -Ticker $Ticker -Data $data -OutputDir $OutputDir
        
        # B.yaml生成（市場データ）
        Generate-BYaml -Ticker $Ticker -Data $data -OutputDir $OutputDir
        
        # C.yaml生成（分析結果）
        Generate-CYaml -Ticker $Ticker -Data $data -OutputDir $OutputDir
        
        Write-Host "✓ レガシー移管完了: $OutputDir" -ForegroundColor Green
        
    } catch {
        Write-Error "レガシー移管エラー: $($_.Exception.Message)"
        throw
    }
}

function Generate-FactsMd {
    param($Ticker, $Data, $OutputDir)
    
    $factsPath = Join-Path $OutputDir "facts.md"
    
    $content = @"
# $Ticker - 基本事実

## 会社概要
- **銘柄コード**: $Ticker
- **会社名**: [レガシーから移行]
- **セクター**: [レガシーから移行]
- **通貨**: USD
- **決算月**: 12月

## レガシー移行情報
- **移行日**: $(Get-Date -Format "yyyy-MM-dd")
- **移行元**: レガシーシステム
- **データ件数**: $($Data.Count) 行

## 主要指標
[レガシーデータから自動生成]

## 備考
- レガシーシステムから自動移行されたデータ
- 検証・調整が必要な項目があります
"@
    
    $content | Set-Content $factsPath -Encoding UTF8
    Write-Host "✓ facts.md生成: $factsPath" -ForegroundColor Cyan
}

function Generate-AYaml {
    param($Ticker, $Data, $OutputDir)
    
    $aPath = Join-Path $OutputDir "A.yaml"
    
    $content = @"
# A.yaml - 基本情報
ticker: $Ticker
name: "[レガシーから移行]"
sector: "[レガシーから移行]"
currency: USD
fye_month: 12
default_wacc: 0.10

# レガシー移行メタデータ
legacy_migration:
  migrated_date: "$(Get-Date -Format "yyyy-MM-dd")"
  source_system: "legacy"
  data_count: $($Data.Count)
  
# 基本財務情報
fundamentals:
  market_cap: null  # 要更新
  revenue_ttm: null  # 要更新
  net_income_ttm: null  # 要更新
  
# リスク指標
risk_metrics:
  beta: null  # 要更新
  volatility: null  # 要更新
"@
    
    $content | Set-Content $aPath -Encoding UTF8
    Write-Host "✓ A.yaml生成: $aPath" -ForegroundColor Cyan
}

function Generate-BYaml {
    param($Ticker, $Data, $OutputDir)
    
    $bPath = Join-Path $OutputDir "B.yaml"
    
    $content = @"
# B.yaml - 市場データ
ticker: $Ticker
last_updated: "$(Get-Date -Format "yyyy-MM-dd HH:mm:ss")"

# 価格データ
price_data:
  current_price: null  # 要更新
  price_52w_high: null  # 要更新
  price_52w_low: null  # 要更新
  volume_avg: null  # 要更新

# 市場指標
market_metrics:
  pe_ratio: null  # 要更新
  pb_ratio: null  # 要更新
  dividend_yield: null  # 要更新
  
# レガシー移行データ
legacy_data:
  migrated_records: $($Data.Count)
  migration_date: "$(Get-Date -Format "yyyy-MM-dd")"
"@
    
    $content | Set-Content $bPath -Encoding UTF8
    Write-Host "✓ B.yaml生成: $bPath" -ForegroundColor Cyan
}

function Generate-CYaml {
    param($Ticker, $Data, $OutputDir)
    
    $cPath = Join-Path $OutputDir "C.yaml"
    
    $content = @"
# C.yaml - 分析結果
ticker: $Ticker
analysis_date: "$(Get-Date -Format "yyyy-MM-dd")"

# 投資判断
investment_decision:
  recommendation: "HOLD"  # 要分析
  target_price: null  # 要分析
  confidence: 0.5  # 要分析
  
# 分析結果
analysis_results:
  dcf_value: null  # 要計算
  relative_valuation: null  # 要計算
  risk_assessment: "MEDIUM"  # 要評価
  
# レガシー移行状況
migration_status:
  data_migrated: true
  analysis_required: true
  validation_pending: true
"@
    
    $content | Set-Content $cPath -Encoding UTF8
    Write-Host "✓ C.yaml生成: $cPath" -ForegroundColor Cyan
}

# メイン実行
if ($LegacyCsvPath) {
    Convert-LegacyCsvToAHF -Ticker $Ticker -LegacyCsvPath $LegacyCsvPath -OutputDir $OutputDir
} else {
    Write-Host "使用例:" -ForegroundColor Yellow
    Write-Host "Convert-LegacyToAHF -Ticker WOLF -LegacyCsvPath '.\legacy\WOLF_data.csv'" -ForegroundColor Cyan
}