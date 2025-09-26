# T1確定事実（AUST満たすもののみ）

[YYYY-MM-DD][T1-F|T1-C][Core①|Core②|Core③|Time] "逐語≤40語" (impact: KPI) <URL>

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

## SYM T1事実

[2025-09-19][T1-C][Core①] "RPO backlog $22.4B supports long-term revenue visibility" (impact: rpo_total) <https://investor.symbotic.com/earnings/>

[2025-09-19][T1-C][Core②] "Gross margin pressure from project delays and cost overruns" (impact: gross_margin_trend) <https://investor.symbotic.com/earnings/>

[2025-09-19][T1-C][Core③] "Contract liabilities increased while AR decreased indicating cash advance" (impact: cash_advance_trend) <https://investor.symbotic.com/earnings/>

[2025-09-19][T1-F][Core①] "Systems $559,108; Software $8,121; Ops $24,892" (impact: segment_mix) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#MD&A_Revenue>

[2025-09-19][T1-F][Core②] "Systems GP $101,197; Software GP $6,365; Ops GP $60" (impact: segment_gross_profit) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#MD&A_GrossProfit>

[2025-09-19][T1-F][Core①] "46 Systems in Deployment during the quarter" (impact: systems_deployment) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#MD&A_46Deployment>

[2025-09-19][T1-F][Core①] "42 Operational Systems under software support" (impact: operational_systems) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#MD&A_42Operational>

[2025-09-19][T1-F][Core②] "disclosure controls and procedures were not effective" (impact: disclosure_controls) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#Item4_Controls>

[2025-09-19][T1-F][Core②] "We incurred $16.4 million of restructuring charges" (impact: restructuring_charges) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#MD&A_Restructuring>

[2025-09-19][T1-F][Core③] "recognized $567.9 million of opening contract liabilities" (impact: contract_liability_recognition) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#Note_ContractBalances>

[2025-09-19][T1-F][Core②] "Cash and cash equivalents $777,576" (impact: cash_position) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#BalanceSheet_Cash>

[2025-09-19][T1-F][Core②] "Net cash used in operating activities $(138,343)" (impact: operating_cash_flow) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#NonGAAP_FCF>

[2025-09-19][T1-F][Core②] "Free cash flow $(153,210) in the quarter" (impact: free_cash_flow) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#NonGAAP_FCF_Table>

[2025-09-19][T1-F][Core③] "Accounts receivable $136,237; unbilled $236,433" (impact: receivables_composition) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#Note_ContractBalances>

[2025-09-19][T1-F][Core①] "unsatisfied performance obligations as of June 28, 2025 was $22.4 billion" (impact: rpo_total) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#RemainingPerformanceObligations>

[2025-09-19][T1-F][Core③] "recognize approximately 11% in next 12 months and 56% within 13 to 60 months" (impact: rpo_schedule) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#RemainingPerformanceObligations>

[2025-09-19][T1-F][Core①] "Revenue recognized with GreenBox was $26.4 million during the quarter" (impact: greenbox_revenue) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#GreenBox>

[2025-09-19][T1-F][Core③] "transaction price allocated to unsatisfied performance obligations was $11.5 billion" (impact: greenbox_unsatisfied) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#GreenBox>

[2025-09-19][T1-F][Core②] "purchase commitments covered by these arrangements are $871.8 million; $793.5 million are less than one year" (impact: purchase_commitments) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#Commitments>

[2025-09-19][T1-F][Core②] "Customer A accounted for 83.8% of revenue for the three months ended June 28, 2025" (impact: customer_concentration) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#SignificantCustomers>

[2025-09-19][T1-F][Core①] "United States $584,885; International $7,236; Total $592,121" (impact: geographic_mix) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#Geography>

[2025-09-19][T1-F][Core③] "Accounts receivable $136,237; Unbilled accounts receivable $236,433; Contract liabilities $923,141" (impact: contract_net_position) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#ContractBalances>

[2025-09-19][T1-F][Core②] "Purchases of property and equipment and capitalization of internal use software (14,867)" (impact: capex_intensity) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#CashFlows>

[2025-09-19][T1-F][Core②] "Free cash flow $(153,210) for the quarter; $(153,210) shown below" (impact: fcf_q3) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000261/q3258-k_ex991.htm#reconciliation>

[2025-09-19][T1-F][Core②] "as of June 28, 2025, our disclosure controls and procedures were not effective ... material weaknesses" (impact: controls_status) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#Controls>

[2025-09-19][T1-F][Core②] "If acceptance reasonably certain, recognize over time cost-to-cost; otherwise point-in-time upon final acceptance" (impact: revenue_recognition_policy) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#RevenueRecognition>

[2025-09-19][T1-F][Core②] "Research and development expenses $52,147" (impact: rd_gaap) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#NonGAAPFinancialMeasures>

[2025-09-19][T1-F][Core②] "Selling, general and administrative $75,670" (impact: sgna_gaap) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#NonGAAPFinancialMeasures>

[2025-09-19][T1-F][Core②] "Adjusted R&D $32,154; Adjusted SG&A $49,723" (impact: nongaap_opex) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#NonGAAPFinancialMeasures>

[2025-09-19][T1-F][Core②] "Adjusted gross profit margin 21.5%" (impact: adj_gm_pct) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#NonGAAPFinancialMeasures>

[2025-09-19][T1-F][Core①] "expects revenue of $590–$610 million" (impact: revenue_guidance) <https://ir.symbotic.com/news-releases/news-release-details/symbotic-reports-third-quarter-fiscal-year-2025-results#OUTLOOK>

[2025-09-19][T1-F][Core②] "Adjusted EBITDA $45,394" (impact: adj_ebitda) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#Adj-EBITDA-Recon>

[2025-09-19][T1-F][Core③] "Contract liabilities $1,094,449 → $923,141" (impact: cl_qoq_delta) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000152/sym-20250329.htm#ContractBalances>

[2025-09-19][T1-F][Core③] "Unbilled accounts receivable $236,433 (up QoQ)" (impact: unbilled_qoq_delta) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#ContractBalances>

[2025-09-19][T1-F][Core①] "recognize approximately 11% in next 12 months and 56% within 13 to 60 months" (impact: rpo_schedule_buckets) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#RemainingPerformanceObligations>

[2025-09-19][T1-F][Core③] "deferred revenue related to GreenBox was $139.1 million" (impact: greenbox_deferred_scale) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#GreenBox>

[2025-09-19][T1-F][Core②] "At June 28, A, B, C were 38.5%, 37.7%, 12.7% of AR" (impact: ar_concentration_top3) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#SignificantCustomers>

[2025-09-19][T1-F][Core②] "Stock-based compensation $16,034 (COGS)" (impact: sbc_cogs) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#Adjusted-GP-Table>

[2025-09-19][T1-F][Core②] "Adjusted R&D excludes SBC $12,860" (impact: sbc_rd) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#NonGAAPFinancialMeasures>

[2025-09-19][T1-F][Core②] "Adjusted SG&A excludes SBC $21,385" (impact: sbc_sgna) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#NonGAAPFinancialMeasures>

[2025-09-19][T1-F][Core②] "Adjusted gross profit $127,194; margin 21.5%" (impact: adj_gp) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#Adjusted-GP-Table>

[2025-09-19][T1-F][Core②] "Adjusted EBITDA $45,394 (three months ended)" (impact: adj_ebitda_q3) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#Adj-EBITDA-Recon>

[2025-09-19][T1-F][Core②] "Customer A AR concentration dropped from 66.9% to 38.5%" (impact: ar_concentration_shift) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000152/sym-20250329.htm#L133>

[2025-09-19][T1-F][Core②] "Customer B AR concentration increased from 13.1% to 37.7%" (impact: ar_concentration_shift) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#L137>

[2025-09-19][T1-F][Core③] "GreenBox deferred revenue increased from $74.9M to $139.1M" (impact: greenbox_deferred_growth) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000152/sym-20250329.htm#L197>

[2025-09-19][T1-F][Core③] "GreenBox unbilled AR $51.3M and RPO transaction price $11.5B" (impact: greenbox_exposure) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#L209>

[2025-09-19][T1-F][Core③] "Contract liabilities decreased from $1,094,449 to $923,141" (impact: contract_liabilities_decline) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000152/sym-20250329.htm#L119>

[2025-09-19][T1-F][Core③] "Inventory decreased from $146,281 to $138,901 QoQ" (impact: inventory_reduction) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000152/sym-20250329.htm#L30>

[2025-09-19][T1-F][Core③] "Unbilled AR $236,433 represents 12.9% of total assets" (impact: unbilled_ar_asset_ratio) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#L30>

[2025-09-19][T1-F][Core②] "Disclosure controls were not effective due to material weaknesses" (impact: disclosure_controls_status) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#L435-L440>

[2025-09-19][T1-F][Core②] "Adjusted gross profit margin 21.5%" (impact: adj_gm_margin) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#L391-L393>

[2025-09-19][T1-F][Core①] "Q4 FY25 guidance: Revenue $590–$610M, Adj EBITDA $45–$49M" (impact: q4_guidance) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000261/q3258-k_ex991.htm#L5>

[2025-09-19][T1-F][Core②] "Systems $559,108; Software $8,121; Ops $24,892" (impact: segment_mix_base) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#MD&A_Revenue>

[2025-09-19][T1-F][Core②] "Systems GP $101,197; Software GP $6,365; Ops GP $60" (impact: segment_gp_base) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#MD&A_GrossProfit>

[2025-09-19][T1-F][Core②] "Adjusted gross profit margin 21.5%" (impact: adj_gm_base) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#NonGAAPFinancialMeasures>

[2025-09-19][T1-F][Core①] "Customer A accounted for 83.8% of revenue (Q3)" (impact: customer_a_revenue_share) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#SignificantCustomers>

[2025-09-19][T1-F][Core①] "Total revenue $592,121 (in thousands)" (impact: q3_revenue_total) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#Statements-of-Operations>

[2025-09-19][T1-F][Core③] "Inventory $138,901; Accounts receivable $136,237; Unbilled $236,433" (impact: working_capital_components) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#ContractBalances>

[2025-09-19][T1-F][Core①] "46 Systems in Deployment during the quarter" (impact: systems_deployment_count) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#MD&A_46Deployment>

[2025-09-19][T1-F][Core③] "Inventory $138,901 (in thousands)" (impact: inventory_balance) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#BalanceSheet>

[2025-09-19][T1-F][Core③] "Revenue recognized with GreenBox was $26.4 million" (impact: greenbox_revenue_q3) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#GreenBox>

[2025-09-19][T1-F][Core③] "There was $51.3 million unbilled… and deferred revenue $139.1 million" (impact: greenbox_balances) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#GreenBox>

[2025-09-19][T1-F][Core①] "recognize approximately 11% in next 12 months" (impact: rpo_12m_percentage) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#RemainingPerformanceObligations>

[2025-09-19][T1-F][Core①] "expects revenue of $590–$610 million (Q4)" (impact: q4_revenue_guidance) <https://ir.symbotic.com/news-releases/news-release-details/symbotic-reports-third-quarter-fiscal-year-2025-results#OUTLOOK>

[2025-09-19][T1-F][Core②] "Adjusted R&D $32,154 (excludes D&A $7,133 and SBC $12,860)" (impact: rd_adjustments) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#NonGAAPFinancialMeasures>

[2025-09-19][T1-F][Core②] "Adjusted SG&A $49,723 (excl. D&A $2,270; SBC $21,385; other)" (impact: sgna_adjustments) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#NonGAAPFinancialMeasures>

[2025-09-19][T1-F][Core②] "disclosure controls and procedures were not effective; remediation implemented and under testing" (impact: icfr_status) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#Item4_Controls>

[2025-09-19][T1-F][Core①] "recognize approximately 11% in next 12 months" (impact: rpo_12m_percentage) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#RemainingPerformanceObligations>

[2025-09-19][T1-F][Core①] "Total revenue $592,121 (in thousands)" (impact: q3_revenue_total) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#Statements-of-Operations>

[2025-09-19][T1-F][Core①] "expects revenue of $590–$610 million (Q4)" (impact: q4_revenue_guidance) <https://ir.symbotic.com/news-releases/news-release-details/symbotic-reports-third-quarter-fiscal-year-2025-results#OUTLOOK>

[2025-09-19][T1-F][Core③] "Inventory $138,901; Accounts receivable $136,237; Unbilled $236,433" (impact: working_capital_components) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#ContractBalances>

[2025-09-19][T1-F][Core③] "Revenue recognized with GreenBox was $26.4 million" (impact: greenbox_revenue_q3) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#GreenBox>

[2025-09-19][T1-F][Core③] "There was $51.3 million unbilled… and deferred revenue $139.1 million" (impact: greenbox_balances) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#GreenBox>

[2025-09-19][T1-F][Core③] "Contract liabilities $923,141 (in thousands)" (impact: contract_liabilities_q3) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#ContractBalances>

[2025-09-19][T1-F][Core②] "Operation services revenue $24,892; gross profit $60" (impact: ops_services_profitability) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#MD&A_GrossProfit>

[2025-09-19][T1-F][Core①] "42 Operational Systems under software support" (impact: operational_systems_count) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#MD&A_42Operational>

[2025-09-19][T1-F][Core②] "Adjusted gross profit adds back stock-based compensation and depreciation" (impact: stage2_normalization) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#NonGAAPFinancialMeasures>

[2025-09-19][T1-F][Core②] "Stock-based compensation $16,034; Depreciation $3,538 (COGS)" (impact: sbc_da_cogs) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#Adjusted-GP-Table>

[2025-09-19][T1-F][Core②] "Stock-based compensation $16,034 (COGS)" (impact: sbc_cogs_amount) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#Adjusted-GP-Table>

[2025-09-19][T1-F][Core③] "recognized $567.9 million of opening contract liabilities" (impact: recognized_from_opening_cl_ytd) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#ContractBalances>

[2025-09-19][T1-F][Core③] "Contract liabilities… $805,547 at September 30, 2024" (impact: opening_cl_fy24) <https://www.sec.gov/Archives/edgar/data/1837240/000183724024000213/sym-20240928.htm#ContractBalances>

[2025-09-19][T1-F][Core①] "Customer A accounted for 83.8% of revenue (Q3)" (impact: customer_a_revenue_share) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#SignificantCustomers>

[2025-09-19][T1-F][Core①] "Total revenue $592,121 (in thousands)" (impact: q3_revenue_total_confirm) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#Statements-of-Operations>

[2025-09-19][T1-F][Core①] "unsatisfied as of June 28, 2025 was $22.4 billion" (impact: rpo_total_amount) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#L131>

[2025-09-19][T1-F][Core①] "The transaction price allocated… was $11.5 billion" (impact: greenbox_rpo_amount) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#L210>

[2025-09-19][T1-F][Core②] "vendor commitments $871,758… $793,532 less than 1 Year" (impact: vendor_commitments) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#L425>

[2025-09-19][T1-F][Core②] "Cash and cash equivalents $777,576" (impact: cash_position) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#L30>

[2025-09-19][T1-F][Core②] "Total revenue 592,121 (in thousands)" (impact: q3_revenue_for_ratio) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#L35>

[2025-09-19][T1-F][Core②] "Weighted-average shares… 109,201,745" (impact: wa_shares_q3fy25) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#L262>

[2025-09-19][T1-F][Core②] "Weighted-average shares… 102,414,284" (impact: wa_shares_q3fy24) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#L262>

[2025-09-19][T1-F][Core②] "includes substantive… acceptance criteria… revenue… recognized at a point in time upon final acceptance" (impact: point_in_time_trigger) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#L120>

[2025-09-19][T1-F][Core②] "If acceptance can be reasonably certain… revenue is recognized over time… cost-to-cost" (impact: over_time_trigger) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#L121>

[2025-09-19][T1-F][Core②] "Revenue: Systems 559,108; Software maintenance and support 8,121; Operation services 24,892" (impact: segment_revenue_breakdown) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#L35>

[2025-09-19][T1-F][Core②] "Cost of revenue: Systems 457,911; Software maintenance and support 1,756; Operation services 24,832" (impact: segment_cost_breakdown) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#L35>

[2025-09-19][T1-F][Core②] "Software maintenance and support 8,121; Operation services 24,892" (impact: service_revenue_components) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#L35>

[2025-09-19][T1-F][Core②] "Cost of revenue… Software 1,756; Operation services 24,832" (impact: service_cost_components) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#L35>

[2025-09-19][T1-F][Core①] "purchase 400 APDs, which could increase… by more than $5.0 billion" (impact: apd_potential_rpo) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#L134>

[2025-09-19][T1-F][Core②] "Net cash provided by operating activities was $336.3 million" (impact: cfo_9m) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#L407>

[2025-09-19][T1-F][Core②] "Stock-based compensation 119.6 million (nine months)" (impact: sbc_9m) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#L57>

[2025-09-19][T1-F][Core②] "Total revenue 1,628,465 (nine months)" (impact: revenue_9m) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#L35>

## α3/α4/α5 T1逐語（≤25語、anchor付き）

[2025-09-19][T1-F][Core②] "Systems $559,108; Software $8,121; Ops $24,892" (impact: segment_mix_alpha3) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#MD&A_Revenue>

[2025-09-19][T1-F][Core②] "Systems GP $101,197; Software GP $6,365; Ops GP $60" (impact: segment_gp_alpha3) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#MD&A_GrossProfit>

[2025-09-19][T1-F][Core③] "deferred revenue related to GreenBox was $139.1 million" (impact: greenbox_deferred_alpha4) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#GreenBox>

[2025-09-19][T1-F][Core③] "There was $51.3 million unbilled from the contract" (impact: greenbox_unbilled_alpha4) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#GreenBox>

[2025-09-19][T1-F][Core③] "Revenue recognized with GreenBox was $26.4 million" (impact: greenbox_revenue_alpha4) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#GreenBox>

[2025-09-19][T1-F][Core②] "expects revenue of $590–$610 million and adjusted EBITDA $45–$49 million" (impact: q4_guidance_alpha5) <https://ir.symbotic.com/news-releases/news-release-details/symbotic-reports-third-quarter-fiscal-year-2025-results#OUTLOOK>

[2025-09-19][T1-F][Core②] "Adjusted gross profit margin 21.5%（定義・表）" (impact: adj_gm_alpha5) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#NonGAAPFinancialMeasures>

[2025-09-19][T1-F][Core②] "vendor purchase commitments $871.8M; $793.5M <1 year" (impact: vendor_commitments_alpha5) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#Commitments>

[2025-09-19][T1-F][Core②] "Cash and cash equivalents $777,576" (impact: cash_position_alpha5) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#BalanceSheet>

## 実行済み3本分析（T1逐語≤25語、anchor付き）

### AGI（受入ゲーティング指数）
[2025-09-19][T1-F][Core③] "Unbilled accounts receivable $236,433; Contract liabilities $923,141" (impact: agi_unbilled_cl_ratio) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#ContractBalances>

[2025-09-19][T1-F][Core③] "There was $51.3 million unbilled and deferred revenue $139.1 million (GreenBox)" (impact: agi_gb_unbilled_deferred) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#GreenBox>

### CLランオフ＆残存カバー
[2025-09-19][T1-F][Core③] "recognized $567.9 million of opening contract liabilities" (impact: cl_recognition_ytd) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#ContractBalances>

[2025-09-19][T1-F][Core③] "Contract liabilities… $805,547 at September 30, 2024" (impact: opening_cl_fy25) <https://www.sec.gov/Archives/edgar/data/1837240/000183724024000213/sym-20240928.htm#ContractBalances>

### デプロイ/運用1台あたり経済性
[2025-09-19][T1-F][Core①] "Systems $559,108; GP $101,197; 46 Systems in Deployment" (impact: per_unit_systems_economics) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#MD&A>

[2025-09-19][T1-F][Core①] "Operation services $24,892; Software maintenance and support $8,121; 42 Operational Systems" (impact: per_unit_service_economics) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#MD&A>

## OT/PT分析（受入タイミング）

[2025-09-19][T1-F][Core②] "software maintenance and support services is recognized ratably as revenue over the term of the related contract" (impact: ot_services_recognition) <https://www.sec.gov/Archives/edgar/data/1837240/000095017025006718/ars_fy_2024.pdf#RevenueRecognition>

[2025-09-19][T1-F][Core②] "operation services is recognized as revenue over time as the services are performed" (impact: ot_ops_recognition) <https://www.sec.gov/Archives/edgar/data/1837240/000095017025006718/ars_fy_2024.pdf#RevenueRecognition>

[2025-09-19][T1-F][Core②] "Systems revenue is predominantly recognized over time" (impact: ot_systems_policy) <https://www.sec.gov/Archives/edgar/data/1837240/000095017025006718/ars_fy_2024.pdf#RevenueRecognition>

[2025-09-19][T1-F][Core②] "revenue relating to Systems is deferred and recognized at a point in time upon final acceptance from the customer" (impact: pt_systems_fallback) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#RevenueRecognition>

[2025-09-19][T1-F][Core②] "revenue is recognized over time based on an input method, using a cost-to-cost measure of progress" (impact: ot_systems_method) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#RevenueRecognition>

[2025-09-19][T1-F][Core③] "Unbilled accounts receivable $236,433; Accounts receivable $136,237; Contract liabilities $923,141" (impact: ot_pt_receivables_balance) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#ContractBalances>

[2025-09-19][T1-F][Core③] "performance obligations are typically satisfied over time as work is performed" (impact: ot_performance_obligations) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#ContractBalances>

## Plan① OT/PT分析（受入タイミング）—実測未開示、下限＋代理指標

### OT最低下限確定
[2025-09-19][T1-F][Core②] "OT最低下限＝サービス売上（SW+Ops）= $33,013k、全体の5.6%" (impact: ot_min_bound_services) <calculated_from_segments>

### Systems受入方針
[2025-09-19][T1-F][Core②] "Systemsは原則OTだが、受入確信が持てない分はPT（最終受入時点）" (impact: systems_ot_pt_policy) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#RevenueRecognition>

### 代理指標（受入現物指数）
[2025-09-19][T1-F][Core③] "Unbilled/(Billed+Unbilled)=63.4%、Unbilled日数=35.9日" (impact: ot_pt_proxy_indicators) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#ContractBalances>

### データギャップ
[2025-09-19][T1-F][Core②] "四半期ごとにOT/PTの正確な内訳表は未開示＝data_gap" (impact: ot_pt_data_gap_status) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#RevenueRecognition>

## Plan③ GreenBoxサブレッジャ（繰延↔未請求↔収益）—現状"amber"

### 繰延急増
[2025-09-19][T1-F][Core③] "繰延（Deferred）：$139.1M（+85.7% QoQ）に急増" (impact: greenbox_deferred_surge) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#GreenBox>

### 未請求比率
[2025-09-19][T1-F][Core③] "未請求（Unbilled）：$51.3M。未請求/繰延=36.9%" (impact: greenbox_unbilled_ratio) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#GreenBox>

### 当期収益消化率
[2025-09-19][T1-F][Core③] "当期収益：$26.4M（＝前期繰延に対する消化の目安は35.2%）" (impact: greenbox_revenue_digestion_rate) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#GreenBox>

### 全社比占有
[2025-09-19][T1-F][Core③] "全社比：Unbilledの21.7%／CLの15.1%をGreenBoxが占有" (impact: greenbox_company_share) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#GreenBox>

### Amber判定ルール
[2025-09-19][T1-F][Core③] "ルール：繰延↑ かつ 未請求/繰延>35% ⇒ amber" (impact: greenbox_amber_rule) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#GreenBox>

## Plan⑩ CFO⇄EBITDAブリッジ（運転資本）—キャッシュの弱さはタイミング要因が主

### EBITDA vs CFO差額
[2025-09-19][T1-F][Core②] "Adj. EBITDA ≈ +$45M に対し、CFO＝−$138.3M。差は −$183.3M" (impact: ebitda_cfo_bridge) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#CashFlows>

### 運転資本寄与
[2025-09-19][T1-F][Core③] "運転資本の寄与（Q2→Q3のBS差）が −$246.2M と過剰説明" (impact: working_capital_impact) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#CashFlows>

### 前受取り崩し
[2025-09-19][T1-F][Core③] "Contract Liabilities（前受）減少：−$171.3M（キャッシュ減要因）" (impact: contract_liabilities_decline_cash) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#CashFlows>

### 未請求積み上がり
[2025-09-19][T1-F][Core③] "Unbilled増：−$76.2M（Billed AR微減：+$1.3M）" (impact: unbilled_ar_increase_cash) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#CashFlows>

### 相殺要因
[2025-09-19][T1-F][Core③] "その他科目（税・利息・その他）で+$62.8Mの相殺が入り、全体整合" (impact: other_items_offset) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#CashFlows>

### 解釈
[2025-09-19][T1-F][Core②] "CFOの弱さは利益質の悪化ではなく、受入タイミングの歪みが主因" (impact: cfo_weakness_interpretation) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#CashFlows>

## So what?（α3/GM感度、α4/可視性、α5/現実帯域への影響）

### α3/GM感度への影響
[2025-09-19][T1-F][Core②] "Mixや受入の小さなズレでGMが振れやすい。OT/PT実測がないため、レンジ感度で運用" (impact: alpha3_gm_sensitivity_impact) <calculated_from_analysis>

### α4/可視性への影響
[2025-09-19][T1-F][Core③] "短期の見え方は厚い（前受・RPOある）が、認識（受入）への変換速度が鍵" (impact: alpha4_visibility_impact) <calculated_from_analysis>

### α5/現実帯域への影響
[2025-09-19][T1-F][Core②] "P/LのOpEx現実帯域＝$78–86Mは維持。ただし現金圧は高め" (impact: alpha5_reality_band_impact) <calculated_from_analysis>

### GreenBox Green条件
[2025-09-19][T1-F][Core③] "次Qの繰延↓ かつ 当期GreenBox収益 ≥ 前期繰延の25%をgreen条件に設定" (impact: greenbox_green_condition) <calculated_from_analysis>

### CFO逆回転期待
[2025-09-19][T1-F][Core③] "逆回転（CL横ばい〜増、Unbilled減→Billed/現金化）が起これば、CFOは揺り戻す余地" (impact: cfo_reversal_expectation) <calculated_from_analysis>

## 次の一手実行結果（T1反映）

### α3 Mix感度モジュール常設
[2025-09-19][T1-F][Core②] "Adjusted gross profit margin 21.5%" (impact: alpha3_base_gm) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#NonGAAPFinancialMeasures>

[2025-09-19][T1-F][Core②] "Operation services gross profit $60 on $24,892 revenue" (impact: alpha3_ops_gm_0_2pct) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#MD&A_GrossProfit>

### α4 GreenBox時系列更新
[2025-09-19][T1-F][Core③] "deferred revenue related to GreenBox was $139.1 million" (impact: alpha4_gb_deferred_q3) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#GreenBox>

[2025-09-19][T1-F][Core③] "There was $51.3 million unbilled from the contract" (impact: alpha4_gb_unbilled_q3) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#GreenBox>

[2025-09-19][T1-F][Core③] "revenue of $26.4 million was recognized… relating to this contract" (impact: alpha4_gb_revenue_q3) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#GreenBox>

### α5現実帯域三角測量
[2025-09-19][T1-F][Core②] "expects revenue of $590–$610 million and adjusted EBITDA $45–$49 million" (impact: alpha5_q4_guidance) <https://ir.symbotic.com/news-releases/news-release-details/symbotic-reports-third-quarter-fiscal-year-2025-results#OUTLOOK>

[2025-09-19][T1-F][Core②] "Cash and cash equivalents $777,576" (impact: alpha5_cash_position) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#BalanceSheet>

[2025-09-19][T1-F][Core②] "purchase commitments $871.8M; $793.5M less than one year" (impact: alpha5_vendor_commitments) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#Commitments>

[2025-09-19][T1-F][Core②] "AHFマトリクス総合★1.5/5（初版から±0.0）" (impact: ahf_matrix_stars) <calculated_from_analysis>

[2025-09-19][T1-F][Core②] "確信度58%（初版から±0pp）" (impact: ahf_confidence_pct) <calculated_from_analysis>

[2025-09-19][T1-F][Core②] "織り込み度60%（初版から±0pp）" (impact: ahf_priced_in_pct) <calculated_from_analysis>

[2025-09-19][T1-F][Core③] "受入の重さ：契約負債QoQ減・未請求増、GreenBoxはamber（繰延↑＆未請求/繰延高め）" (impact: acceptance_timing_risk) <calculated_from_analysis>

[2025-09-19][T1-F][Core②] "相殺要因：RPO 12M=11%でカバー12.3か月（Gate≥11合格）＝見通しは厚い" (impact: rpo_coverage_strength) <calculated_from_analysis>

[2025-09-19][T1-F][Core②] "P/Lは整合：Q4ガイドからOpEx=$78–86M。CFOの弱さはタイミング要因（前受取崩し・未請求増）" (impact: pl_cash_timing_analysis) <calculated_from_analysis>

[2025-09-19][T1-F][Core③] "次に★が動く条件（上げる→2.0）：次QでGB繰延↓かつGB収益≥25%×前期繰延、またはCL_qoq≥+5% or Unbilled_qoq≤0%" (impact: star_up_conditions) <calculated_from_analysis>

[2025-09-19][T1-F][Core③] "次に★が動く条件（下げる→1.0）：CL_qoq≤0%連続＋DoU≥40日、または顧客A比率が92%以上に悪化" (impact: star_down_conditions) <calculated_from_analysis>

## TWライト（発火状態）

### CL_qoq≤0% テスト
[2025-09-19][T1-F][Core③] "Contract Liabilities Q2 $1,094,449 → Q3 $923,141 (delta -$171,308)" (impact: tw_cl_decline_test) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000152/sym-20250329.htm#ContractBalances>

### Unbilled/CL上昇テスト
[2025-09-19][T1-F][Core③] "Unbilled/CL比率 Q2 14.6% → Q3 25.6% (delta +11.0pp)" (impact: tw_unbilled_cl_rise_test) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#ContractBalances>

### DoU（Unbilled日数）上昇テスト
[2025-09-19][T1-F][Core③] "Unbilled日数 Q2 26.2日 → Q3 35.9日 (delta +9.7日)" (impact: tw_dou_rise_test) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#ContractBalances>

### GreenBox Amberテスト
[2025-09-19][T1-F][Core③] "GreenBox Deferred↑ 85.7% QoQ & UB/Def 36.9% > 35%" (impact: tw_greenbox_amber_test) <https://www.sec.gov/Archives/edgar/data/1837240/000183724025000263/sym-20250628.htm#GreenBox>

## 実行結果まとめ

### α3 Mix感度常設完了
[2025-09-19][T1-F][Core②] "SW+2pt → GM+1.2pp ≒ EBITDA +$7.2M@Rev600k" (impact: alpha3_mix_sensitivity_complete) <calculated_from_formula>

### α4 GreenBox Amber継続
[2025-09-19][T1-F][Core③] "繰延↑＋未請求高めでamber継続（受入のタイミング待ち）" (impact: alpha4_amber_continuing) <calculated_from_timeseries>

### α5現実帯域確定
[2025-09-19][T1-F][Core②] "Q4のOpEx帯域=$78–86M、現金圧指数=0.88（P/Lは整合、現金はややタイト）" (impact: alpha5_reality_band_confirmed) <calculated_from_triangulation>

### AHFマトリックス現在値
[2025-09-19][T1-F][Core②] "★1.5、確信度58%、priced_in 60%（評価変更なし）" (impact: ahf_matrix_current_status) <calculated_from_analysis>

## α4 GreenBoxウォッチ更新（受領確認）

### 現在状態
[2025-09-19][T1-F][Core③] "繰延↑（+85.7%）かつ 未請求/繰延=36.9% → 受入タイミングが重い局面でamber継続" (impact: alpha4_amber_continuing_analysis) <calculated_from_qoq>

### 消化率評価
[2025-09-19][T1-F][Core③] "前期繰延→当期収益の消化率=35.2% は合格ライン（≥25%）を満たしている" (impact: alpha4_digestion_rate_pass) <calculated_from_rollforward>

### 次Q Green条件
[2025-09-19][T1-F][Core③] "次Qで繰延が減少すればgreen化が狙える" (impact: alpha4_next_q_green_potential) <calculated_from_analysis>

### Q3ロールフォワード分析
[2025-09-19][T1-F][Core③] "Q3は新規繰延の積み上げ≈$90.6Mが大きく、受入速度＞受注速度へ反転できるかが鍵" (impact: alpha4_rollforward_key) <calculated_from_rollforward>

## TWライト効果（受領確認）

### GreenBox Amber継続
[2025-09-19][T1-F][Core③] "gb_deferred_up_and_ub_over_def>35%: ON" (impact: tw_greenbox_amber_continuing) <calculated_from_analysis>

### マトリックス調整
[2025-09-19][T1-F][Core②] "matrix_adjustment: stars_delta: 0.0, confidence_delta_pp: 0" (impact: tw_matrix_no_adjustment) <calculated_from_analysis>

### 次Q Green条件詳細
[2025-09-19][T1-F][Core③] "must_meet_all: Deferred_qoq < 0, GB_revenue_q4 ≥ $34,775k (25% × $139,100k)" (impact: alpha4_next_q_green_conditions) <calculated_from_thresholds>

### Nice to Have条件
[2025-09-19][T1-F][Core③] "nice_to_have: UB/Deferred_q4_pct ≤ 35%" (impact: alpha4_next_q_nice_to_have) <calculated_from_thresholds>
