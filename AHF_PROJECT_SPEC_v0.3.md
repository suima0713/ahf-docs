# AHF（Analytic Homeostasis Framework）プロジェクト指示｜v0.3（最小構成）

※本質がぼやけないよう"必要最小・運用直結"のみ。

---

## −1) PRISM｜ChatGPT 禁止事項（必ず遵守／本指示全体に優先）

- **頼んでいない提案や実装は厳禁**（勝手な追加・拡張をしない）
- **最小MVPからChair主導で段階的にポリッシュアップ**
- **各工程で可読性の高い説明・根拠を明示**（出典・式・前提を最小で添える）
- **Chairが依頼・決定するまでは冗長なコードを書かない**
- **内容を都度、自動記憶し、ルール徹底と文脈保持に努める**

---

## 0) 目的 & 原則（北極星）

**目的**: 一次情報（T1）を A/B/C マトリクスに流し、①右肩上がり × ②傾きの質 × ③時間を"一体"で評価。④（カタリスト）は③の文中に〔Time〕注釈で一度だけ**反映。

**出力**: 銘柄ごと 1ページ（A=材料／B=結論＆Horizon＆KPI×2／C=反証）。

**優先度**: ①＞②＞③＞④（④は注釈／外付け係数禁止）。

---

## 1) データ方針（Provider Policy）

**Primary**: Internal ETL（価格・イベント・ファンダのSSoT）

**Fallback**: Polygon（価格の欠損補完・スプリット/配当・長期バックフィルのみ）

**モード**: `AHF_DATASOURCE=internal | polygon | auto`（推奨：auto）

**パリティ検証**: 日次終値の絶対％差 ≤ 0.50%、直近5営業日の累積差 ≤ 1.5%／コーポレートアクション日付一致（±1営業日）。失格は昇格不可。

**キルスイッチ**: 7日連続パリティNG または API失敗率>20% → Polygon停止（`AHF_DATASOURCE=internal`）

**環境変数**: `AHF_DATASOURCE`／`AHF_INTERNAL_BASEURL`／`AHF_INTERNAL_TOKEN`／（任意）`POLYGON_API_KEY`

---

## 2) レポ構成（最小ディレクトリ）
```
/ahf/
  _catalog/  _templates/  _rules/  _ingest/  _scripts/
  tickers/<TICKER>/attachments/providers/{internal|polygon}/
  tickers/<TICKER>/snapshots/YYYY-MM-DD/{A.yaml,B.yaml,C.yaml,facts.md}
  tickers/<TICKER>/current/
```

---

## 3) テンプレ（要素だけ）※_templates/

**A.yaml**: `meta.asof`／`core.{right_shoulder, slope_quality, time_profile}`／`time_annotation{delta_t_quarters, delta_g_pct, window_quarters, note}`

**B.yaml**: `horizon.{6M,1Y,3Y,5Y}.verdict/ΔIRRbp`／`stance.decision/size/reason`／`kpi_watch[2]`

**C.yaml**: `tests.{time_off, delay_plus_0_5Q, alignment_sales_pnl}`

**facts.md**: `[YYYY-MM-DD][T1-F|T1-P|T1-C][Core①|Core②|Core③|Time] "逐語" (impact: KPI) <src>`

**タグ規約**: T1-F/P/C｜Core①/②/③｜Time（④は一度だけ）

---

## 4) スクリプト（名前と役割のみ）

**New-AHFProject.ps1**: 骨組み初期化

**Add-AHFTicker.ps1 -Ticker <T>**: 銘柄作成＋初回スナップショット

**AHF.Data.psm1（Get-AHFPrices）**: Internal優先→Polygon補完ラッパ（保存は attachments/providers/...）

**Test-AHFParity.ps1**: Internal vs Polygon 検証

**New-AHFSnapshot.ps1 -Ticker <T>**: current/ を日時保存・更新

---

## 5) 運用ループ（MVP：3ステップ）

**A｜集める**: T1逐語を facts.md に1行 → A.yaml（①/②/③）へ写経。④は time_annotation に一度だけ。

**B｜まとめる**: Horizon（6M/1Y/3Y/5Y）／Go/保留/No-Go／KPI×2（質＋実行）。

**C｜反証**: 〔Time〕無効／t1+0.5Q／売上↔GM/CF/在庫の整合。

→ current/ 上書き → New-AHFSnapshot → _catalog を手動1行更新（MVP）。

---

## 6) ガードレール

- **外付け係数禁止**（④は③の注釈で一回だけ）
- **出力は常に1ページ**（差分1行＋Horizon＋KPI×2）
- **入る基準**: ①②が○ かつ ΔIRR ≥ +300–500bp（逆DCF比）／Δt依存のみは回避
- **サイズはσで調整**（見立ては変えない）

---

## 7) 即コマンド（初回）
```powershell
pwsh .\ahf\_scripts\New-AHFProject.ps1
$env:AHF_DATASOURCE="auto"; $env:AHF_INTERNAL_BASEURL="<url>"; $env:AHF_INTERNAL_TOKEN="<token>"
pwsh .\ahf\_scripts\Add-AHFTicker.ps1 -Ticker WOLF
```

---

**以上、最小構成＋PRISM禁止事項の最新版です。**
