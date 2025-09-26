# DUAL-ANCHOR Backfill パッチ

## 概要
SEC∧IRの二重アンカー化のためのBackfillタスク（削除せず保持）

## Backlog追加エントリ

| id | class=LEAD | KPI/主張 | 現在の根拠≤40語 | ソース | T1化に足りないもの | 次アクション | 関連Impact | unavailability_reason | grace_until |
|---|---|---|---|---|---|---|---|---|---|
| DUAL-ANCHOR-BACKFILL-RPO | LEAD | RPO/12MのSEC二重化（IR確証済のSEC化） | IRでRPO総額確認済、SEC同等記載を特定 | investors.confluent.io | SEC EDGAR内のRPO記載箇所の特定 | SEC 10-Q/10-KのRPO note検索 | RPO coverage ratio | blocked_source | 7日 |
| DUAL-ANCHOR-BACKFILL-UNBILLED | LEAD | Unbilled/NotesのSEC二重化 | IRでUnbilled金額確認済、SEC記載箇所特定要 | investors.confluent.io | SEC内のunbilled記載箇所の特定 | SEC financial statements検索 | unbilled_share_pct | blocked_source | 7日 |
| DUAL-ANCHOR-BACKFILL-DR | LEAD | Deferred(B/S)のSEC二重化 | IRでDeferred revenue確認済、SEC記載箇所特定要 | investors.confluent.io | SEC内のdeferred revenue記載箇所の特定 | SEC balance sheet検索 | deferred_revenue_ratio | blocked_source | 7日 |

## 適用方法
1. 既存のbacklog.mdに上記テーブルを追記
2. triage.jsonにUNCERTAINステータスで追加
3. 7日後に優先度繰上げ（grace_until経過後）

## 注意事項
- これらのタスクは削除せず保持（情報エッジを削らない）
- SEC復旧時に自動でCONFIRMED昇格
- PENDING_SEC状態でもIRアンカーは継続利用可能
