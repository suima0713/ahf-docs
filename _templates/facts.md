# T1確定事実（AUST満たすもののみ）

[YYYY-MM-DD][T1-F|T1-C][Core①|Core②|Core③|Time] "逐語≤40語" (impact: KPI) <URL>

## 例

### ガイダンス発表（逐語≤40語）
[2024-12-15][T1-F][Time] "FY26 revenue guidance midpoint $2.5B (range $2.3B–$2.7B)." (impact: guidance_fy26_mid) <https://sec.gov/edgar/...>

### 進捗イベント（8-K/PR/契約）
[2024-12-15][T1-F][Core③] "Signed multi-year fixed-fee license with Microsoft." (impact: rpo_stepup_event) <https://sec.gov/edgar/.../Item 1.01>

### キャッシュ系（10-Q/10-K）
[2024-12-15][T1-F][Core②] "Free cash flow $150M for the quarter." (impact: fcf_q) <https://sec.gov/edgar/.../CF表>

[2024-12-15][T1-F][Core②] "Capital expenditures $25M." (impact: capex_q) <https://sec.gov/edgar/.../CF表>

### 従来例
[2024-12-15][T1-F][Core①] "FY26 revenue floor of $2.5B represents 15% growth" (impact: FY26_Floor) <https://sec.gov/edgar/...>

[2024-12-15][T1-C][Core②] "Fixed-fee contracts represent 75% of backlog" (impact: Fixed_fee_ratio) <https://ir.company.com/earnings/...>

## タグ規約
- **T1-F**: ファンダメンタル（SEC本文）
- **T1-C**: カタリスト（IR発表・トランスクリプト）
- **Core①**: 右肩上がり（量）
- **Core②**: 傾きの質（ROIC−WACC/ROIIC/FCF）
- **Core③**: 時間
- **Time**: カタリスト（一度だけ）

## 運用ルール
- **AUST必須**: As-of/Unit/Section-or-Table/≤40語/直URL
- **逐語のみ**: 本文から直接引用（見出し・目次不可）
- **UNCERTAIN混入禁止**: T1確定のみ記載
