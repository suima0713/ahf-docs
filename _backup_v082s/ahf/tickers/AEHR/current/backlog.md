# E0-UL一元プール（UNCERTAIN候補）

| id | class | KPI/主張 | 現在の根拠≤40語 | ソース | T1化に足りないもの | 次アクション | 関連Impact | grace_until |
|----|-------|----------|-----------------|-------|-------------------|-------------|-------------|-------------|
| GAP-001 | data_gap | RPO_total_$k | RPO非重要と明記 | SEC 10-Q | 数値開示なし | 代替指標探索 | ③時間軸 | 2025-10-19 |
| GAP-002 | data_gap | RPO_12m_pct | RPO非重要と明記 | SEC 10-Q | 12M比率未開示 | 代替指標探索 | ③時間軸 | 2025-10-19 |
| GAP-003 | resolved | Adj_EBITDA_$k | Non-GAAP営業利益$2,810kで代替 | SEC 8-K | 営業利益で代替済み | 完了 | ②勾配 | 2025-09-19 |
| GAP-004 | data_gap | segment_detail | セグメント詳細未開示 | SEC 10-Q | セグメント別詳細なし | 代替指標探索 | ②勾配 | 2025-10-19 |

## 運用ルール
- class=Lead：新規発見の事実候補
- T1化に足りないもの：AUST（As-of/Unit/Section-or-Table/≤40語/直URL）の欠けている要素
- grace_until：TTL期限（過ぎたら優先度繰上げ）
- 関連Impact：①量/②質/③時間/④ミスプライス
