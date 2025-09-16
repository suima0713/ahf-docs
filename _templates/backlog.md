# E0-UL一元プール（UNCERTAIN候補）

| id | class | KPI/主張 | 現在の根拠≤40語 | ソース | T1化に足りないもの | 次アクション | 関連Impact | grace_until |
|----|-------|----------|-----------------|-------|-------------------|-------------|-------------|-------------|
| L-G1 | Lead | FY26 mid $X | IR PRで数値提示 | <URL> | 10-Q/EX-99原本 | EX-99リンク確定 | guidance_fy26_mid | 2024-12-31 |
| L-C1 | Lead | Buyback $Y | 8-K見出し | <URL> | Item/金額逐語 | Item 8.01逐語抽出 | capital_allocation | 2024-12-31 |
| 001 | Lead | FY26_Floor | SEC 10-K本文の文言 | https://sec.gov/... | section/tableラベル | SEC再確認 | ①右肩上がり | 2024-12-31 |
| 002 | Lead | Fixed_fee_ratio | トランスクリプト発言 | https://ir.company.com/... | 逐語≤40語 | トランスクリプト精査 | ②傾きの質 | 2024-12-31 |

## 運用ルール
- class=Lead：新規発見の事実候補
- T1化に足りないもの：AUST（As-of/Unit/Section-or-Table/≤40語/直URL）の欠けている要素
- grace_until：TTL期限（過ぎたら優先度繰上げ）
- 関連Impact：①量/②質/③時間/④ミスプライス

