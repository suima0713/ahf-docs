# UPST E0-UL一元プール（UNCERTAIN候補）

| id | class | KPI/主張 | 現在の根拠≤40語 | ソース | T1化に足りないもの | 次アクション | 関連Impact | grace_until |
|----|-------|----------|-----------------|-------|-------------------|-------------|-------------|-------------|
| L1 | Lead | Q3 guidance $280M | IR PRで数値提示 | <URL> | 10-Q/EX-99原本 | EX-99リンク確定 | guidance_q3_2024 | 2024-12-31 |
| L2 | Lead | 0%CB $690M | 8-K見出し | <URL> | Item/金額逐語 | Item 8.01逐語抽出 | convertible_bond | 2024-12-31 |
| L3 | Lead | 倉庫 $475M/$100M/$50M | トランスクリプト発言 | <URL> | 逐語≤40語 | トランスクリプト精査 | warehouse_facility | 2024-12-31 |
| L4 | Lead | H1'25 OCF ▲$133.6M | プレスリリース | <URL> | SEC本文確認 | 10-K/10-Q本文 | operating_cash_flow | 2024-12-31 |
| L5 | Lead | CapEx $0.115M | 財務諸表 | <URL> | CF表確認 | キャッシュフロー表 | capex_q3 | 2024-12-31 |
| L6 | Lead | 最大損失 $660.2M | リスク開示 | <URL> | 脚注確認 | リスク要因 | max_loss | 2024-12-31 |
| LP3 | Lead | Forward-flow covenants | 契約書 | <URL> | 定量逐語 | 契約条項抽出 | forward_flow_covenants | 2024-12-31 |
| LP4 | Lead | 倉庫コベナンツ | 契約書 | <URL> | 定量逐語 | 契約条項抽出 | warehouse_covenants | 2024-12-31 |
| LP5 | Lead | 手数料収益58%集中 | セグメント情報 | <URL> | セグメント表 | セグメント分析 | fee_revenue_concentration | 2024-12-31 |
| LP7 | Lead | 資金調達能力 | 流動性分析 | <URL> | 流動性表 | 流動性分析 | funding_capacity | 2024-12-31 |
| L8 | Lead | Forward-flow $1.2B（Fortress） | IR/BusinessWireで言及（SEC一次未確認） | <URL> | EDGAR 8-K/EX-10.x原本 | EDGARで8-K/EX-10.x探索 | forward_flow_commitment | 2025-09-23 |
| L9 | Lead | Q3 CFO弱さ＝タイミング要因 | 運転資本分析完了 | <URL> | 次Q反転条件 | CL_qoq≥+5%かつUnbilled_qoq≤0% | cfo_timing_recovery | 2025-12-31 |
| L10 | Lead | TWライト据え置き条件 | 運転資本分析完了 | <URL> | CL_qoq≤0、Unbilled増はON | 次Qモニタリング | working_capital_trend | 2025-12-31 |

## 運用ルール
- class=Lead：新規発見の事実候補
- T1化に足りないもの：AUST（As-of/Unit/Section-or-Table/≤40語/直URL）の欠けている要素
- grace_until：TTL期限（過ぎたら優先度繰上げ）
- 関連Impact：①量/②質/③時間/④ミスプライス
