# AHFデータ戦略（v0.2）

## 戦略転換

**Primary**: Internal ETL（価格・ファンダ・イベント・トランスクリプト等）
**Fallback**: Polygon（主に価格Bar／欠損補完）

## 選択ロジック

- `AHF_DATASOURCE=internal` - 内部ETLのみ使用
- `AHF_DATASOURCE=polygon` - Polygonのみ使用  
- `AHF_DATASOURCE=auto` - 内部ETL→失敗時にPolygon（デフォルト）

## 環境変数設定

```powershell
# データソース選択
$env:AHF_DATASOURCE = "auto"  # internal|polygon|auto

# 内部ETL設定
$env:AHF_INTERNAL_BASEURL = "https://<your-etl-host>/api"
$env:AHF_INTERNAL_TOKEN = "<bearer_token>"

# Polygon設定（フォールバック用）
$env:POLYGON_API_KEY = "<key>"
```

## 保存先構造

```
tickers/<TICKER>/attachments/providers/
├── internal/
│   ├── prices_2024-09-01_2025-09-13.json
│   ├── fundamentals_2025-Q3.json
│   ├── events_2025-09-13.json
│   └── transcripts_2025-Q3.json
└── polygon/
    ├── prices_2024-09-01_2025-09-13.json
    └── bars_2024-09-01_2025-09-13.csv
```

## PowerShellモジュール

`AHF.Data.psm1` - プロバイダ切替の薄いラッパ

### 主要関数

- `Get-AHFPrices` - 価格データ取得（自動プロバイダ選択）
- `Get-AHFPricesInternal` - 内部ETL価格データ取得
- `Get-AHFPricesPolygon` - Polygon価格データ取得
- `Save-AHFProviderPayload` - プロバイダ別データ保存

### 使用例

```powershell
Import-Module .\ahf\_scripts\AHF.Data.psm1

# 自動プロバイダ選択
Get-AHFPrices -Ticker WOLF -From 2024-09-01 -To 2025-09-13 -Timespan day

# 内部ETL強制
$env:AHF_DATASOURCE = "internal"
Get-AHFPrices -Ticker WOLF -From 2024-09-01 -To 2025-09-13 -Timespan day

# Polygon強制
$env:AHF_DATASOURCE = "polygon"
Get-AHFPrices -Ticker WOLF -From 2024-09-01 -To 2025-09-13 -Timespan day
```

## 内部ETLエンドポイント仕様

### 価格データ
```
GET /api/prices?symbol={ticker}&start={from}&end={to}&timespan={day|week|month}
Authorization: Bearer {token}
```

### ファンダメンタル
```
GET /api/fundamentals?symbol={ticker}&period={quarter|annual}
Authorization: Bearer {token}
```

### イベント
```
GET /api/events?symbol={ticker}&start={from}&end={to}
Authorization: Bearer {token}
```

### トランスクリプト
```
GET /api/transcripts?symbol={ticker}&period={quarter}
Authorization: Bearer {token}
```

## 実務フロー

1. **環境変数設定**
   ```powershell
   $env:AHF_DATASOURCE = "auto"
   $env:AHF_INTERNAL_BASEURL = "https://your-etl-host/api"
   $env:AHF_INTERNAL_TOKEN = "your-bearer-token"
   ```

2. **データ取得**
   ```powershell
   Import-Module .\ahf\_scripts\AHF.Data.psm1
   Get-AHFPrices -Ticker WOLF -From 2024-09-01 -To 2025-09-13
   ```

3. **A/B/C更新** - 従来通り
   - facts.md に1行追加
   - A.yaml の該当配列に1レコード追加
   - B.yaml のHorizonとC.yamlの3テスト更新

## 拡張性

このモジュールパターンで以下にも横展開可能：

- `Get-AHFFundamentals` - ファンダメンタルデータ
- `Get-AHFEvents` - イベントデータ
- `Get-AHFTranscripts` - トランスクリプト
- `Get-AHFNews` - ニュースデータ

## 利点

1. **内部ETLの強みを直で活かす** - 網羅性・正規化・低レイテンシ
2. **MVPでの交換可能性** - 薄いラッパで供給源を差し替えても上流は不変
3. **腐らない** - 取得元ごとに保存→監査や再現が容易
4. **使い勝手最大化** - 自動フォールバックで安定性確保
