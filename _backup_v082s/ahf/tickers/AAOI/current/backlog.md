# E0-UL一元プール（AAOI - Applied Optoelectronics）

## T1最優先原則
- **T1確定**: sec.gov（10-K/10-Q/8-K）≧ investors.aaoi.com（IR PR/資料）
- **T2候補**: 他AI/記事/トランスクリプト（EDGE、TTL=7日、意思決定には使わない）
- **95%は内部ETLで完結、他AIは"場所のヒント＋照合"の5%**

## 他AIの役割（限定）
- **用途**: 所在の手掛かり（例：10-K注記ページ、見出し名）と突合
- **扱い**: 必ずT2（EDGE/TTL=7日）。T1で再取得・再計算してからスコア/DIへ反映
- **禁止**: 他AIの数値や文言を直接引用・採用しない

| id | class | KPI/主張 | 現在の根拠≤40語 | ソース | T1化に足りないもの | 次アクション | 関連Impact | unavailability_reason | grace_until |
|----|-------|----------|-----------------|-------|-------------------|-------------|-------------|----------------------|-------------|
| L-G1 | Lead | GAAP OPM Q2'25 | PR内の損益明細で算出可能 | <URL> | 損益明細表のsection/table | 損益明細表逐語抽出 | ②傾きの質 | not_found | 2025-09-30 |
| L-C1 | Lead | 800G出荷実績 | H2に有意出荷示唆のみ | <URL> | 数量/顧客の具体情報 | Q4実績レポート待ち | ③時間 | not_found | 2025-10-07 |
| L-C2 | Lead | 主要顧客契約 | Microsoft/Amazon等の供給SOW | <URL> | 契約更新の最新逐語 | 8-K/IR更新確認 | ③時間 | blocked_source | 2025-10-07 |
| 001 | Lead | 転換社債残高 | PR内BSで$133.9M記載 | https://sec.gov/... | section/tableラベル | BS詳細確認 | ②傾きの質 | not_found | 2025-09-30 |
| 002 | Lead | 800G顧客承認状況 | 工場承認→出荷への移行 | https://sec.gov/... | 承認プロセス詳細 | 顧客承認進捗確認 | ③時間 | not_found | 2025-10-07 |
| 003 | U | H3 ATM実行状況 | "ATM sales to date"記載なし | 8-K/10-Q未検出 | ATM実行事実のT1 | Q3 10-Q/8-K監視 | ③時間 | not_found | 2025-10-07 |
| 004 | U | H5供給律速根拠 | LITE/COHRの800G言及なし | SEC EX-99.1未特定 | 同業の供給制約T1 | COHR/MRVL/AVGO再走査 | ②傾きの質 | not_found | 2025-09-30 |
| 005 | U | H1顧客受入慣行 | acceptance明示なし | 顧客慣行のT1不在 | 顧客受入プロセスのT1 | Q3 PR/10-Q監視 | ①量 | not_found | 2025-10-07 |
| 006 | U | 代替ソース認定 | "qualified a second source"等の逐語なし | 10-K/10-Q未検出 | 代替ソース認定のT1 | 10-K/10-Q再走査 | ②傾きの質 | not_found | 2025-09-30 |

## 運用ルール
- class=Lead：新規発見の事実候補
- T1化に足りないもの：AUST（As-of/Unit/Section-or-Table/≤40語/直URL）の欠けている要素
- unavailability_reason：EDGAR_down／rate_limited／not_found／blocked_source
- grace_until：TTL期限（過ぎたら優先度繰上げ）
- 関連Impact：①量/②質/③時間/④ミスプライス
