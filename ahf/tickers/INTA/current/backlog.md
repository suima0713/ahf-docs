# 非T1（将来T1に昇格し得る情報＆手掛かり）のワンテーブル管理

**class**: U=T0-U, A=T1-adj(open pair), L=E0(Lead), X=棄却

## INTA｜U（不確定）ワンテーブル

| id | class | KPI / 主張 | 現在の根拠 | ソース（直 or Accession） | T1化に足りないもの | 次アクション（コピペ可） | 関連Impact | unavailability_reason | grace_until |
|---|---|---|---|---|---|---|---|---|---|
| BL-001 | **U** | RPO_total & ≤12M% | 候補: **$719.7M** / **61%**（FY25） | 10-K Accession **0001193125-25-184080** | 10-K本文の逐語、該当Note直URL、単位 | FY25 10-K Note 2のRPO段落を逐語＋as-of＋直URL＋単位で返して。 | **coverage_ratio** | **EDGAR_down** | **2025-09-21** |
| BL-002 | **U** | Contract liabilities（opening→recognized） | 候補: recognized from opening **$211.4M**（FY25） | 10-K Accession **0001193125-25-184080** | 10-K本文の逐語、該当表直URL | FY25 10-K Note 2のContract liabilitiesから「Revenue recognized … included in the opening contract liability …」の本文逐語＋金額＋直URLを返して。 | **contract_liabilities_roll** | — | — |
| BL-003 | **U** | Shares outstanding（Cover） | 候補: **82,120,030** shares（as of 2025-08-13） | 10-K Accession **0001193125-25-184080** | Cover本文の逐語、直URL | FY25 10-K Cover pageから当該一文の本文逐語＋直URLを返して。 | — | — | — |
| BL-004 | **U** | Disaggregation of revenue（FY25金額） | 候補: Subs/License/PS 金額の表有無が未確定 | 10-K Accession **0001193125-25-184080** | 表の有無確認、あれば金額（$ in thousands）＋表名＋直URL | FY25 10-KのNote 2に"Disaggregation of revenue"表があれば、Subscription/License/Professional servicesのFY25金額（$ in thousands）を表名付きで提示。無ければ「表なし」。 | — | — | — |
| BL-005 | **U** | Concentrations（A/R または Revenue） | 候補: A/R集中 **17%/16%**（FY25/FY24）主張あり | 10-K Accession **0001193125-25-184080** | EDGARのConcentrations注記逐語、直URL | FY25 10-KのConcentrations注記から、A/RまたはRevenueの集中％があれば逐語＋直URL。無ければ「記載なし」。 | — | — | — |
| BL-006 | **U** | Deferred revenue（10-K B/S最終値） | 候補: current **$253,812k**, noncurrent **$4,120k** vs IR **$256,994k/2,002k** | 10-K Accession **0001193125-25-184080** | 10-K B/Sの該当行逐語（$ in thousands）、直URL、as-of | FY25 10-KのConsolidated Balance Sheetsから「Deferred revenue, current / noncurrent」を逐語（$ in thousands）＋as-of＋直URLで返して。 | — | — | — |
| BL-007 | **X** | guidance_fy26_nonGAAP_op_margin | status=not_found（EX-99.1に率なし） | EX-99.1 Outlook | — | — | — | **not_found** | — |
| BL-008 | **X** | arr_disclaimer | status=not_found（今回EX-99.1に独立性の但書見当たらず） | EX-99.1 Non-GAAP Measures | — | — | — | **not_found** | — |
| BL-009 | **X** | buyback_authorization | T1-core/CONFIRMED（8-K Item 7.01で$150M承認確定） | 8-K Item 7.01 / EX-99.1 | — | — | **buyback_execution** | **T1-core** | — |

## 相手面探索（片面→両面化）

**【相手面の対向ソース探索】**この"片面一次"に対応するもう一方の一次情報を提示。
一致する本文逐語（≤40語）＋URL。見つからなければ「未発表」。

```
片面側: "<逐語≤40語>" (URL: <一次URL>)
出力：counterparty verbatim≤40 | as-of | source | URL | 判定(T1-core/T1-adj/U)
```

## 使い方（超シンプル）

**確定（T1）以外はぜんぶここに載せる。**従来の uncertain.md / leads.json は不要。

### 昇格/降格のルール：

1. **逐語＋直URLが揃い矛盾なし** → T1-core（facts/forensicへ移し、この表から削除）
2. **片面→相手面も揃い一致** → T1-core、食い違い → U のまま
3. **誤報確定** → class=X にして1行だけ残す（履歴）

### 優先度は Impact カード列で判断（coverage_ratio / contract_liabilities_roll など）。

この表から**昇格（T1）／継続（U）／棄却（X）**の更新だけを行い、他ファイル（facts/forensic/impact）は後段で反映してください。