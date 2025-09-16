# AHF（Analytic Homeostasis Framework）v0.3.1

**合言葉: Facts in, balance out.**

## 概要

AHFを「腐らないディレクトリ」として設計した構成。PRISMガイドライン準拠、レッドライン運用対応。情報の最大化を阻害しない構造で、過去データは腐らず、鮮度・精度・量・深さをA→B→Cに減衰なく流せる構造。

**v0.3.1の特徴**: 内部ETL主軸、Polygonフォールバックのデータ戦略、レッドライン自動適用システム。

## ディレクトリ構造

```
/ahf/
├── _catalog/            # 横串の索引（全銘柄の要約）
│   ├── tickers.csv
│   ├── horizon_index.csv
│   └── kpi_watch.csv
├── _templates/          # A/B/CとFactの雛形だけ
│   ├── A.yaml
│   ├── B.yaml
│   ├── C.yaml
│   └── facts.md
├── _rules/              # 運用原則（1枚）
│   └── operating_principles.md
├── _ingest/             # 新規素材の置き場（PDF, 8-K等）
├── _scripts/            # PowerShell自動化スクリプト
│   ├── AHF.Data.psm1    # データ取得モジュール（v0.2）
│   ├── Get-AHFData.ps1  # データ取得スクリプト
│   ├── Add-AHFTicker.ps1
│   └── New-AHFSnapshot.ps1
├── tickers/
│   └── WOLF/
│       ├── attachments/
│       │   └── providers/    # プロバイダ別データ保存（v0.2）
│       │       ├── internal/ # 内部ETLデータ
│       │       └── polygon/  # Polygonデータ
│       ├── snapshots/
│       │   └── 2025-09-13/    # "その日の真実"を丸ごと保存
│       │       ├── A.yaml
│       │       ├── B.yaml
│       │       ├── C.yaml
│       │       └── facts.md
│       └── current/         # 最新スナップショットをコピー
└── main.py
```

## 使用方法

### 環境変数設定（v0.2）

```powershell
# データソース選択
$env:AHF_DATASOURCE = "auto"  # internal|polygon|auto

# 内部ETL設定
$env:AHF_INTERNAL_BASEURL = "https://your-etl-host/api"
$env:AHF_INTERNAL_TOKEN = "your-bearer-token"

# Polygon設定（フォールバック用）
$env:POLYGON_API_KEY = "your-polygon-key"
```

### 基本実行

```bash
# ダッシュボード表示
python main.py

# インタラクティブモード
python main.py --interactive
```

### データ取得（v0.2）

```powershell
# 価格データ取得（自動プロバイダ選択）
pwsh .\_scripts\Get-AHFData.ps1 -Ticker WOLF -From 2024-01-01 -To 2025-09-13

# ファンダメンタルデータ取得
pwsh .\_scripts\Get-AHFData.ps1 -Ticker WOLF -DataType fundamentals -Period quarter

# イベントデータ取得
pwsh .\_scripts\Get-AHFData.ps1 -Ticker WOLF -DataType events -From 2024-01-01 -To 2025-09-13

# トランスクリプト取得
pwsh .\_scripts\Get-AHFData.ps1 -Ticker WOLF -DataType transcripts -Period 2025-Q3
```

### インタラクティブコマンド

```
dashboard          # ダッシュボード表示
tickers           # 銘柄一覧
analyze WOLF      # 銘柄分析表示
fact WOLF 2025-09-13 T1-P Core① "Revenue up 15%" Revenue  # 事実追加
scripts           # PowerShellスクリプト一覧
quit              # 終了
```

## 3クリック運用

### 新規断片処理
1. `tickers/XXX/snapshots/日付/` を複製
2. `facts.md` に1行追記
3. `A.yaml` の該当配列に1レコード追加（Core①/②/③ or Time）

### B/C更新
- `B.yaml` のHorizonと`C.yaml`の3テストを更新
- 横串反映：`_catalog/horizon_index.csv` に追加

### 時間注釈ルール
- ④は`A.yaml`の`time_annotation`に"1回だけ"記録
- ①②を上書きしない

## ファイル形式

### A.yaml（集める）
```yaml
meta:
  ticker: WOLF
  asof: 2025-09-13
core:
  right_shoulder:   # ① 右肩上がり
  slope_quality:    # ② 傾きの質
  time_profile:     # ③ t1/t2＋制約
time_annotation:    # ④ 〔Time〕注釈
```

### B.yaml（まとめる）
```yaml
horizon:
  six_months: { verdict: "はい", delta_irr_bp: 350 }
stance:
  decision: "Go"
  size: "M"
kpi_watch: ["KPI1", "KPI2"]
```

### C.yaml（反証）
```yaml
tests:
  time_off: { result: "維持/後退" }
  delay_plus_0_5Q: { result: "維持/後退" }
  alignment_sales_pnl: { result: "整合/逆行" }
```

### facts.md（原子Fact）
```markdown
# facts (T1 only; 最新が上)
- [2025-07-29][T1-P][Core①] "..." (impact: Revenue) <url>
```

## 検索性

- 全ファイルに `asof: YYYY-MM-DD` を入れる
- `facts.md` を逆時系列、タグは `[T1-F/P/C] × [Core①/②/③ or Time]` の二段
- 期間検索はフォルダ名（YYYY-MM-DD）で一撃
- 内容検索はタグで一撃

## ローテーション運用

- `current/` を常に最新で上書き（ダッシュボード用途）
- 過去判断の再検証は `snapshots/` を対で比較
- 差分は人間が1行メモ

## 運用原則

詳細は `_rules/operating_principles.md` を参照。

- **3分ルール**: 3分経過で代替案を提案
- **MVP原則**: 軽く・速く・戻せる
- **時間注釈ルール**: ④は1回だけ記録
- **検索性ルール**: タグと日付で一撃検索

## 特徴

1. **腐らない**: スナップショットで過去データ保存
2. **軽い**: 効率的なファイル構成
3. **速い**: 迅速な運用
4. **戻せる**: 差分＋KPI×2で即巻き戻し
5. **検索最強**: タグと日付で一撃検索
6. **データ戦略v0.2**: 内部ETL主軸、Polygonフォールバック
7. **使い勝手最大化**: 自動プロバイダ選択で安定性確保
8. **拡張性**: ファンダメンタル、イベント、トランスクリプト対応