# T1確定事実（AUST満たすもののみ）

[2025-09-19][T1-F][Core①] "Revenue $50,313" (impact: revenue_q) <https://www.sec.gov/Archives/edgar/data/1844452/000184445225000051/lunr-20250630xexx991.htm#:~:text=Revenue%20%2450%2C313>

[2025-09-19][T1-F][Core②] "Adjusted EBITDA $(25,368)" (impact: adj_ebitda_q) <https://www.sec.gov/Archives/edgar/data/1844452/000184445225000051/lunr-20250630xexx991.htm#:~:text=Adjusted%20EBITDA%24(25%2C368)>

[2025-09-19][T1-F][Core②] "Cost of revenue (excluding depreciation) 56,047" (impact: nongaap_cogs) <https://www.sec.gov/Archives/edgar/data/1844452/000184445225000051/lunr-20250630xexx991.htm#:~:text=Cost%20of%20revenue%20(excluding%20depreciation)56%2C047>

[2025-09-19][T1-F][Core②] "Cost of revenue ... affiliated companies 6,109" (impact: nongaap_cogs2) <https://www.sec.gov/Archives/edgar/data/1844452/000184445225000051/lunr-20250630xexx991.htm#:~:text=affiliated%20companies%206%2C109>

[2025-09-19][T1-F][Core③] "Contract assets 8,438" (impact: contract_assets) <https://www.sec.gov/Archives/edgar/data/1844452/000184445225000051/lunr-20250630xexx991.htm#:~:text=Contract%20assets%208%2C438>

[2025-09-19][T1-F][Core③] "Contract liabilities, current 68,426; non-current 3,215" (impact: contract_liabilities) <https://www.sec.gov/Archives/edgar/data/1844452/000184445225000051/lunr-20250630xexx991.htm#:~:text=Contract%20liabilities%2C%20current>

[2025-09-19][T1-F][Core③] "Backlog $256,909 as of June 30, 2025" (impact: backlog_total_ir) <https://investors.intuitivemachines.com/news-releases/news-release-details/intuitive-machines-reports-second-quarter-2025-financial-results>

[2025-09-19][T1-F][Core③] "Backlog decreased by $71.4 million" (impact: backlog_decline) <https://investors.intuitivemachines.com/news-releases/news-release-details/intuitive-machines-reports-second-quarter-2025-financial-results>

[2025-09-19][T1-F][Core③] "12M recognition ratio not explicitly disclosed" (impact: coverage_months_data_gap) <https://investors.intuitivemachines.com/news-releases/news-release-details/intuitive-machines-reports-second-quarter-2025-financial-results>

[2025-09-19][T1-F][Core②] "Revenue $50,313; Cost of revenue (ex dep) $56,047" (impact: segment_data_gap) <https://www.sec.gov/Archives/edgar/data/1844452/000184445225000051/lunr-20250630xexx991.htm#:~:text=Revenue%20%2450%2C313>

[2025-09-19][T1-F][Core②] "Cost of revenue (ex dep) – affiliated companies $6,109" (impact: affiliated_cogs) <https://www.sec.gov/Archives/edgar/data/1844452/000184445225000051/lunr-20250630xexx991.htm#:~:text=affiliated%20companies%206%2C109>

[2025-09-19][T1-F][Core①] "Revenue $62,524" (impact: q1_revenue_total) <https://investors.intuitivemachines.com/news-releases/news-release-details/intuitive-machines-reports-first-quarter-2025-financial-results>

[2025-09-19][T1-F][Core②] "Revenue disaggregation data_gap" (impact: category_mix_data_gap) <https://www.sec.gov/Archives/edgar/data/1844452/000184445225000051/lunr-20250630xexx991.htm>

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
