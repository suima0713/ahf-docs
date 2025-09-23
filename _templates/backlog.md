# E0-UL一元プール（T1最優先×内部ETL完結版）

## T1最優先原則
- **T1確定**: sec.gov（10-K/10-Q/8-K）≧ investors.jfrog.com（IR PR/資料）
- **T2候補**: 他AI/記事/トランスクリプト（EDGE、TTL=7日、意思決定には使わない）
- **95%は内部ETLで完結、他AIは"場所のヒント＋照合"の5%**

## 他AIの役割（限定）
- **用途**: 所在の手掛かり（例：10-K注記ページ、見出し名）と突合
- **扱い**: 必ずT2（EDGE/TTL=7日）。T1で再取得・再計算してからスコア/DIへ反映
- **禁止**: 他AIの数値や文言を直接引用・採用しない

| id | class | KPI/主張 | 現在の根拠≤40語 | ソース | T1化に足りないもの | 次アクション | 関連Impact | unavailability_reason | grace_until |
|----|-------|----------|-----------------|-------|-------------------|-------------|-------------|----------------------|-------------|
| L-G1 | Lead | FY26 mid $X | IR PRで数値提示 | <URL> | 10-Q/EX-99原本 | EX-99リンク確定 | guidance_fy26_mid | EDGAR_down | 2024-12-31 |
| L-C1 | Lead | Buyback $Y | 8-K見出し | <URL> | Item/金額逐語 | Item 8.01逐語抽出 | capital_allocation | rate_limited | 2024-12-31 |
| 001 | Lead | FY26_Floor | SEC 10-K本文の文言 | https://sec.gov/... | section/tableラベル | SEC再確認 | ①右肩上がり | not_found | 2024-12-31 |
| 002 | Lead | Fixed_fee_ratio | トランスクリプト発言 | https://ir.company.com/... | 逐語≤40語 | トランスクリプト精査 | ②傾きの質 | blocked_source | 2024-12-31 |

## 運用ルール
- class=Lead：新規発見の事実候補
- T1化に足りないもの：AUST（As-of/Unit/Section-or-Table/≤40語/直URL）の欠けている要素
- unavailability_reason：EDGAR_down／rate_limited／not_found／blocked_source
- grace_until：TTL期限（過ぎたら優先度繰上げ）
- 関連Impact：①量/②質/③時間/④ミスプライス

