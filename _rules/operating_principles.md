# AHF運用原則（v0.3.3 - T1最優先×内部ETL完結版）

## T1最優先×内部ETL完結（最優先原則）

### ソース優先順位（固定）
1. **T1確定**: sec.gov（10-K/10-Q/8-K）≧ investors.jfrog.com（IR PR/資料）
2. **T2候補**: 他AI/記事/トランスクリプト（EDGE、TTL=7日、意思決定には使わない）
3. **95%は内部ETLで完結、他AIは"場所のヒント＋照合"の5%**

### 逐語とアンカー（AnchorLint）
- 逐語は25語以内＋#:~:text=必須
- PDFは anchor_backup{pageno,quote,hash} を併記
- 取れない＝**「T1未開示」**で確定（"未取得"と混同しない）

### 内部ETLワークフロー（E→T→L）
1. **Extract**: T1から所定の行を抽出
2. **Transform**: 標準式で派生KPIを算出
3. **Load**: facts/triageに格納

### 他AIの役割（限定）
- **用途**: 所在の手掛かり（例：10-K注記ページ、見出し名）と突合
- **扱い**: 必ずT2（EDGE/TTL=7日）。T1で再取得・再計算してからスコア/DIへ反映
- **禁止**: 他AIの数値や文言を直接引用・採用しない

## AHF 評価ルール更新（全体適用）

**深掘りでT1（低認知ソース）を新規発見 → Confidence ↑**

**同時に、市場の織り込みは必要時のみ ↓（−2/−5/−7）**

**目安：脚注/注記=−2、Exhibit/ABS-15G=−5、144A/RegS等で実弾示唆=−7**

**★スコアは"ファンダ変化時のみ"更新（ルール適用で★は動かさない）**

**評価は必ず★5段階で表記（★★★★★、★★★☆☆等）**

この運用で、深掘りの成果が確実に評価面へ反映されつつ、過剰に★を動かさないバランスを維持します。

---

## ChatOps制約（最優先）

**非同期禁止／即時回答**：将来実行の約束や所要時間提示は一切しない。重い課題は部分完了でも即返す。

**不要な確認・往復最小化**：曖昧でも安全範囲ならベストエフォートで出力。危険なら明確に拒否＋代替案。

**AUST厳守**：As-of／Unit／Source（節・表ラベル）／逐語≤40語／直URLが揃わなければT1に載せない。

**用語とルールの自動保持**：本指示に沿ったフォーマット・用語を自動継続（ユーザーが毎回指示しなくても維持）。

**出力はMVP**：頼まれていない提案・実装・冗長化をしない（Chair指示時のみポリッシュ）。

## 基本方針
**一次情報（T1）を A/B/C マトリクスに流し、①右肩上がり × ②傾きの質 × ③時間軸 × ④認知ギャップを"一体"で評価。**

### ③時間軸（Timeline）＝「近端〜12Mの可視性」
- **定義**: 受注・契約・ガイダンスがいつ売上・粗利へ落ちるかの解像度
- **指標**: RPO 12M coverage、CL coverage、ガイダンス明瞭度
- **★評価**: coverage≥11m=★5、9-11m=★4、6-9m=★3、<6m=★2、撤回等=★1
- **Fast-Screen**: 原則n/a（RPO_12M/CL_currentでcoverage算出可能時のみ採点）

### ④認知ギャップ（Cognition）＝「市場との現在の乖離」
- **定義**: 市場合意に対しT1で確認できる定量の上振れ・下振れの芽
- **運用**: デフォルト★3、二段トリガー（A×B同時成立）で+1、ネガT1で-1
- **方向性**: ポジなら★↑、ネガなら★↓
- **Fast-Screen**: 原則n/a（T1強トリガーのみ採点）

### 出力
銘柄ごと 1ページ（A=材料／B=結論＆Horizon＆KPI×2／C=反証）

### 優先度
①＞②＞③＞④（③時間軸と④認知ギャップは独立評価）

### 詳細ルール
時間軸・認知ギャップの詳細な評価ルールは `ahf/_rules/time_cognition_framework_v063a.yaml` を参照。

### Fast-Screen専用ルール
短時間での精度ある採点は困難なため、③・④は原則n/a（未採点）とする。
詳細は `ahf/_rules/fast_screen_time_cognition_v063a.yaml` を参照。

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

### データソース管理
```
パリティNG または API障害時は内部ETLにフォールバック（情報収集は継続）
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

### backlog.md（Lead/Uのワンテーブル）
```
| id | class=Lead/U | KPI/主張 | 現在の根拠≤40語 | ソース | T1化に足りないもの | 次アクション | 関連Impact | unavailability_reason | grace_until |
```

### triage.json（HYPOTHESES追加）
```json
{
  "HYPOTHESES": [
    {
      "id": "H1_fy26_floor_reset",
      "status": "pending|confirmed|falsified",
      "what_to_watch": ["Note2_FY26_row_delta_kUSD", "Samsung_include_sentence"],
      "trigger": "FY26_row_qoq_delta_kUSD >= 100000",
      "falsifier": "FY26_row_qoq_delta_kUSD < 50000 AND call_notes='deferred recognition later'",
      "kpi_links": ["fy26_contracted_revenue", "samsung_inclusion_in_rpo"]
    }
  ]
}
```

### impact_cards.json（新カード追加）
```json
[
  {
    "id": "ev_over_floor",
    "inputs": ["ev_usd","floor_low_kUSD","floor_high_kUSD"],
    "expr": "ev_usd/(1000*avg(floor_low_kUSD,floor_high_kUSD))",
    "gates": { "up": "<=10.0", "down": ">=20.0" }
  },
  {
    "id": "disagg_fixed_ratio_2Q",
    "inputs": ["fixed_ratio_q1_pct","fixed_ratio_q2_pct"],
    "expr": "min(fixed_ratio_q1_pct,fixed_ratio_q2_pct)",
    "gates": { "up": ">=90", "down": "<85" }
  }
]
```

---

## 運用ループ（MVP：3ステップ＋レッドライン）

### A｜入口（E0-UL）
Leadを広く収集→backlog.md／triage.json(UNCERTAIN)。T1は並走可。

### B｜まとめる
Horizon（6M/1Y/3Y/5Y）／Go・保留・No-Go／KPI×2（質＋実行）。

### C｜反証
〔Time〕無効／t1+0.5Q／売上↔GM/CF/在庫整合。

### D｜レッドライン
forensic.json→スクリプト実行→B.yaml と facts.md に反映。

→ current/ を上書き → New-AHFSnapshot 実行 → _catalog CSVを手動1行更新（MVP）。

---

## ガードレール（ブレ止め）

### 情報の幅を最大化
④は③の文中の注釈（delta_t_quarters/小さなdelta_g_pct）で適宜記録。

### 判断の出力
Horizon＋KPI×2を含む包括的な出力。

### 入る基準
①②が○ かつ ΔIRR ≥ +300〜500bp（逆DCF比）。情報の幅を重視。

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

### データ品質管理
```
パリティ違反 → データ品質チームに報告
API障害 → フォールバック運用、情報収集継続
```

---

## デュアルAI運用規律（内部）

**Vetting→Persist** の二段構え（内部のみ）

**Vetting**：一次文書の位置特定・抜粋候補（E0-UL含む）
**Persist**：AUST検証→facts.md/triage.jsonへ確定保存

**貼り付けは最小**：ユーザー可視のプロンプト羅列を避け、確定したT1のみ提示。

**衝突時**は AUST不備側をUNCERTAINへ退避し、contradictionタグで管理。

## 成功指標

- **データ品質**: パリティ検証合格率 > 95%
- **システム安定性**: Internal依存度 100%維持
- **開発効率**: チャート・可視化の見栄え向上
- **運用コスト**: Polygon APIコスト < 月額$100
- **ChatOps効率**: 即時回答率 100%、往復回数最小化