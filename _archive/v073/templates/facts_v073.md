# T1確定事実（AUST満たすもののみ）- v0.7.3

## 固定3軸評価用T1事実

### ①長期EV確度（LEC）
[YYYY-MM-DD][T1-F|T1-C][LEC] "逐語≤25語" (impact: KPI) <URL>

### ②長期EV勾配（NES）
[YYYY-MM-DD][T1-F|T1-C][NES] "逐語≤25語" (impact: KPI) <URL>

### ③バリュエーション＋認知ギャップ（VRG）
[YYYY-MM-DD][T1-F|T1-C][VRG] "逐語≤25語" (impact: KPI) <URL>

## アンカー厳密化（情報削減ゼロ運用）

### verbatim_≤25w（法令順守用の短い逐語抜粋）
- 25語以内の厳密な逐語抜粋
- 見出し・目次は不可
- 本文から直接引用のみ

### context_note（文脈・但し書き・表名など長文OK）
- 文脈・但し書き・表名など長文OK
- 厳密化しても"最大情報"は温存
- 情報削減ゼロ運用

## 例

### ガイダンス発表（逐語≤25語）
[2024-12-15][T1-F][LEC] "FY26 revenue guidance midpoint $2.5B (range $2.3B–$2.7B)." (impact: guidance_fy26_mid) <https://sec.gov/edgar/...>

### 進捗イベント（8-K/PR/契約）
[2024-12-15][T1-F][NES] "Signed multi-year fixed-fee license with Microsoft." (impact: rpo_stepup_event) <https://sec.gov/edgar/.../Item 1.01>

### キャッシュ系（10-Q/10-K）
[2024-12-15][T1-F][LEC] "Free cash flow $150M for the quarter." (impact: fcf_q) <https://sec.gov/edgar/.../CF表>

[2024-12-15][T1-F][LEC] "Capital expenditures $25M." (impact: capex_q) <https://sec.gov/edgar/.../CF表>

### バリュエーション
[2024-12-15][T1-F][VRG] "EV/Sales forward multiple 12.5x based on FY26 guidance." (impact: ev_sales_fwd) <https://sec.gov/edgar/...>

## タグ規約
- **T1-F**: ファンダメンタル（SEC本文）
- **T1-C**: カタリスト（IR発表・トランスクリプト）
- **LEC**: 長期EV確度（①）
- **NES**: 長期EV勾配（②）
- **VRG**: バリュエーション＋認知ギャップ（③）

## 運用ルール
- **AUST必須**: As-of/Unit/Section-or-Table/≤25語/直URL
- **逐語のみ**: 本文から直接引用（見出し・目次不可）
- **UNCERTAIN混入禁止**: T1確定のみ記載
- **固定3軸**: ①LEC/②NES/③VRGの順序固定
