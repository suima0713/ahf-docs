# AHF運用原則（v0.3 - 最小構成）

## 基本方針
**一次情報（T1）を A/B/C マトリクスに流し、①右肩上がり × ②傾きの質 × ③時間を"一体"で評価。④（カタリスト）は③の文中に〔Time〕注釈で一度だけ**反映。

### 出力
銘柄ごと 1ページ（A=材料／B=結論＆Horizon＆KPI×2／C=反証）

### 優先度
①＞②＞③＞④（④は注釈／外付け係数禁止）

---

## データ方針（Provider Policy）

### Primary
**Internal ETL**（価格・イベント・ファンダのSSoT）

### Fallback
**Polygon**（価格系の欠損補完・スプリット/配当・長期バックフィルのみ）

### モード
```
AHF_DATASOURCE=internal | polygon | auto（推奨：auto＝内部→失敗時にPolygon）
```

### パリティ検証（Internal vs Polygon）
- 日次終値の絶対％差 ≤ 0.50%
- 直近5営業日の累積差 ≤ 1.5%
- スプリット/配当日付一致（±1営業日許容）
- 失格時は昇格しない（保存のみ）

### キルスイッチ
```
7日連続パリティNG または API失敗率>20% → Polygon停止（AHF_DATASOURCE=internal）
```

---

## テンプレート規約

### A.yaml（材料）
```yaml
meta:
  asof: YYYY-MM-DD

core:
  right_shoulder: []     # ①右肩上がり
  slope_quality: []      # ②傾きの質（ROIC−WACC/ROIIC/FCF）
  time_profile: []       # ③時間

time_annotation:         # ④カタリスト（一度だけ）
  delta_t_quarters: 
  delta_g_pct: 
  window_quarters: 
  note: 
```

### B.yaml（結論）
```yaml
horizon:
  6M: {verdict: "", ΔIRRbp: }
  1Y: {verdict: "", ΔIRRbp: }
  3Y: {verdict: "", ΔIRRbp: }
  5Y: {verdict: "", ΔIRRbp: }

stance:
  decision: ""           # Go/保留/No-Go
  size: ""              # Low/Med/High
  reason: ""

kpi_watch: [2項目]
  - name: ""
    current: 
    target: 
  - name: ""
    current: 
    target: 
```

### C.yaml（反証）
```yaml
tests:
  time_off: ""          # 〔Time〕無効化テスト
  delay_plus_0_5Q: ""   # t1+0.5Qテスト
  alignment_sales_pnl: "" # 売上↔GM/CF/在庫の整合
```

### facts.md（逆時系列・原子1行）
```
[YYYY-MM-DD][T1-F|T1-P|T1-C][Core①|Core②|Core③|Time] "逐語" (impact: KPI) <src>
```

**タグ規約**: 証拠=T1-F/T1-P/T1-C｜柱=Core①/②/③｜注釈=Time（④は一度だけ）

---

## 運用ループ（MVP：3ステップ）

### A｜集める
T1逐語を facts.md に1行 → A.yaml の該当配列（①/②/③）へ写経。④があれば time_annotation に一度だけ。

### B｜まとめる
Horizon（6M/1Y/3Y/5Y）を更新／Go/保留/No-Go／KPI×2（質＋実行）。

### C｜反証
〔Time〕無効／t1+0.5Q／売上↔GM/CF/在庫の整合。

→ current/ を上書き → New-AHFSnapshot 実行 → _catalog CSVを手動1行更新（MVP）。

---

## ガードレール（ブレ止め）

### 外付け係数禁止
④は③の文中の注釈（delta_t_quarters/小さなdelta_g_pct）で"一回だけ"。

### 判断の最小出力
常に1ページ（差分1行＋Horizon＋KPI×2）。

### 入る基準
①②が○ かつ ΔIRR ≥ +300〜500bp（逆DCF比）。ΔIRRがΔt頼みだけは回避。

### サイズ
σ（Low/Med/High）で配分のみ調整（見立ては変えない）。

---

## 決定木

### データソース選択
```
Internalが揃う → それだけで運用（Polygonは監査用に裏で回す）
Internalに欠損/遅延 → Polygonでバックフィル → 検証OKなら可視化に使用
パリティNG/不安定 → その銘柄はInternalのみで進行（Polygon保留）
```

### エスカレーション
```
パリティ違反 → データ品質チームに報告
API障害 → キルスイッチ発動、Internal専用運用
```

---

## 成功指標

- **データ品質**: パリティ検証合格率 > 95%
- **システム安定性**: Internal依存度 100%維持
- **開発効率**: チャート・可視化の見栄え向上
- **運用コスト**: Polygon APIコスト < 月額$100