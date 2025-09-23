# PDFS Backlog (U/Leadのワンテーブル)

| id | class=U | KPI/主張 | 現在の根拠≤40語 | ソース | T1化に足りないもの | 次アクション | 関連Impact | unavailability_reason | grace_until |
|----|---------|----------|-----------------|--------|-------------------|--------------|------------|---------------------|-------------|
| U001 | U | Adj EBITDA (full D&A) | 現時点は部分D&Aで保守推定。完全D&AのT1確認が必要 | Ex.99.2 | 10-Qの完全なD&A分解表 | 10-Q Item 1A確認 | Alpha5改善判定 | partial_da_only | 2025-09-28 |
| U002 | U | 10-Q Item 1A (No change?) | リスク要因の変更確認が必要 | Q10 | Item 1Aの具体的な変更内容 | 10-Q抽出・比較 | WATCH→GO判定 | not_found | 2025-09-28 |
| U003 | U | Contract Liabilities QoQ | Contract Liabilitiesの四半期変化確認が必要 | Q10 | Balance SheetのCL項目 | 10-Q Balance Sheet確認 | WATCH→GO判定 | not_found | 2025-09-28 |
| U004 | U | Contract Assets QoQ | Contract Assetsの四半期変化確認が必要 | Q10 | Balance SheetのCA項目 | 10-Q Balance Sheet確認 | WATCH→GO判定 | not_found | 2025-09-28 |
| U005 | U | 完全なD&A分解 | 取得無形償却と取得技術償却の詳細分解 | Ex.99.2 | 10-QのD&A詳細表 | 10-Q D&A分解確認 | Alpha5 EBITDA計算 | partial_da_only | 2025-09-28 |
| U006 | U | 営業キャッシュフロー | 営業CFの四半期変化とD&A影響 | Q10 | Cash Flow Statement | 10-Q CFS確認 | Alpha5改善判定 | not_found | 2025-09-28 |
| U007 | U | 在庫・仕掛品 | 在庫の四半期変化と原価影響 | Q10 | Balance Sheet Inventory | 10-Q Balance Sheet確認 | Cost Decomposition | not_found | 2025-09-28 |
| U008 | U | 価格・ボリューム分解 | 価格上昇とボリューム増加の分解 | Ex.99.1 | 価格・ボリューム分析 | 管理レポート確認 | Mix Analysis | not_found | 2025-09-28 |
| U009 | U | GM低下要因説明 | Q2のGM低下要因の一次テキスト説明が未確認（数表中心） | Ex.99.1/99.2 | テキスト説明 | Ex.99テキスト分析 | Alpha3 Explanation | not_found | 2025-09-28 |
| U010 | U | コスト構造変化 | 非GAAP売上原価+$1.70M増加の具体要因説明が必要 | Ex.99.2 | 管理層説明 | 管理ディスカッション確認 | Cost Decomposition | not_found | 2025-09-28 |
| U011 | U | Q2 10-Q GM説明 | Q2 10-Q本文でGM悪化の一次説明を特定（α3＝Explained昇格可否） | Q2 10-Q | MD&A段落 | 10-Q本文確認 | Alpha3 Explanation | blocked_source | 2025-09-28 |
| U012 | U | Contract Assets Q2 | CA（契約資産）のQ2値を確定（WATCH救済の可否） | Q2 10-Q | Contract Balances | 10-Q Note 2確認 | WATCH→GO判定 | not_found | 2025-09-28 |
| U013 | U | Q2 Item 1A | Item 1A（Risk Factors）更新の有無を一次で確定 | Q2 10-Q | Item 1A | 10-Q本文確認 | WATCH→GO判定 | blocked_source | 2025-09-28 |

# AHFマトリックス評価トリガー条件（次Q確認項目）
| TRIGGER-001 | U | 原価項目の沈静化 | 下請/クラウド/設備IT/ハードの表現が「横ばい/減少」へ変化 | 次Q 10-Q | 同段落の表現変化 | 次Q MD&Aの同段落で増加表現→横ばい/減少への変化を確認 | cost_silencing_trigger | not_found | 2025-12-15 |
| TRIGGER-002 | U | CL↑×CA↓への反転 | Contract balancesの矢印反転（CL↑ & CA↓） | 次Q 10-Q | Contract balances表 | 次Q Contract balances表でCL↑ & CA↓の反転を確認 | cl_ca_reversal_trigger | not_found | 2025-12-15 |

## 深掘り結果に基づく新規探索項目

| DEEP-001 | U | 原価増の一時性判定 | 下請・クラウド・設備IT・ハードの増加が一時的か構造的かの判定 | 次Q 10-Q | MD&A段落の表現変化 | 次Q MD&Aで「増加」→「横ばい/減少」への変化を確認 | cost_temporality_assessment | not_found | 2025-12-15 |
| DEEP-002 | U | 買収統合コストの影響 | SecureWise買収の統合コストがCOGSに与える影響の定量化 | 次Q 10-Q | 買収関連コストの開示 | 買収統合コストのCOGS寄与度を確認 | acquisition_cost_impact | not_found | 2025-12-15 |
| DEEP-003 | U | ハード提供比率の変化 | ハード提供比率の上振れが構造的か一時的かの判定 | 次Q 10-Q | 製品構成の開示 | ハード提供比率の四半期変化を確認 | hardware_ratio_assessment | not_found | 2025-12-15 |
| DEEP-004 | U | クラウド使用量スパイク | クラウド使用量の一時的スパイクが原価に与える影響 | 次Q 10-Q | クラウド関連コストの開示 | クラウド使用量の正規化を確認 | cloud_usage_normalization | not_found | 2025-12-15 |
| DEEP-005 | U | 設備・IT投資の影響 | 設備・IT投資の減価償却が原価に与える影響の定量化 | 次Q 10-Q | 設備投資の開示 | 設備・IT投資の減価償却影響を確認 | capex_depreciation_impact | not_found | 2025-12-15 |