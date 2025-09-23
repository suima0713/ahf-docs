# CFLT Backlog（Lead/U/EDGEのワンテーブル）

| id | class=Lead/U/EDGE | KPI/主張 | 現在の根拠≤40語 | ソース | T1化に足りないもの | 次アクション | 関連Impact | unavailability_reason | grace_until |
|----|-------------------|----------|------------------|--------|---------------------|--------------|------------|---------------------|-------------|
| L-001 | Lead | Cloud消費最適化の逆転 | 21% growth in subscription; 28% growth in Confluent Cloud | SeekingAlpha transcript | 具体的なYoY成長率数値 | 10-Q/10-KでCloud revenue成長率を特定 | cloud_consumption_growth | not_found | 2025-01-15 |
| L-002 | Lead | Flink商用化の$1M顧客数 | Three customers are now contributing over $1 million each in Flink ARR | Moomoo earnings summary | 公式IR文書での確認 | 次回IRでFlink顧客数の正式開示確認 | flink_arr_coverage | blocked_source | 2025-01-30 |
| L-003 | Lead | Streaming Agents商用導入 | agentic AI directly into stream processing pipelines | PR release | 具体的な商用導入件数・顧客名 | 次回IRでStreaming Agents商用進捗開示 | ai_streaming_integration | not_found | 2025-02-15 |
| L-004 | Lead | パートナー投資回収率 | $200 million investment over the next three years | Blog post | パートナー経由売上比率の四半期開示 | 10-Qでパートナー売上比率の継続開示確認 | partner_ecosystem_leverage | not_found | 2025-01-15 |
| L-005 | Lead | CTO交代のAI実装影響 | appointment of Stephen Deasy as Chief Technology Officer | Investing.com | 具体的なロードマップ変更・実装速度指標 | 次回IRでAI関連ロードマップの更新確認 | ai_implementation_speed | blocked_source | 2025-01-30 |
| L-006 | U | 最適化逆風の持続性 | consumption growth notably below ... due to optimization | SeekingAlpha transcript | 最適化の具体的な影響度・期間 | 10-Qで最適化影響の定量化確認 | cloud_consumption_growth | not_found | 2025-01-15 |
| L-007 | U | Flink単価維持能力 | serverless architecture charges you only for the five minutes | Docs page | 商用利用での実際の単価・収益性 | 次回IRでFlink収益性指標の開示 | flink_monetization | not_found | 2025-02-15 |
| L-008 | U | DSP市場のAI需要 | 89% see DSPs easing AI adoption | Press release | 具体的な市場規模・成長率 | 第三者リサーチでの市場規模確認 | ai_streaming_integration | blocked_source | 2025-02-28 |
| EDGE-001 | EDGE | BYOC顧客数 | BYOC customer count ≥500 | T2推測 | IR文書での正式開示 | 次回IRでBYOC顧客数の開示確認 | byoc_adoption | not_found | 2025-03-15 |
| EDGE-002 | EDGE | AI workload revenue比率 | AI workload revenue ≥20% | T2推測 | IR文書での正式開示 | 次回IRでAI workload revenue比率の開示確認 | ai_revenue_ratio | not_found | 2025-03-15 |
| EDGE-F2-FLINK-1 | EDGE | Flink ARR > $1M顧客が3社（増減トラッキング） | Three customers are now contributing over $1 million each in Flink ARR | Moomoo earnings summary | 次回開示で件数更新を確認 | 次回IRでFlink $1M顧客数の更新確認 | F2 | blocked_source | 2025-02-14 |
| EDGE-F1-NRR-1 | EDGE | NRR ≈ 114%（四半期指標の定期観測） | Net Revenue Retention (NRR) 114% | AlphaSpread | IR/10-Qで数値開示があれば昇格 | 次回IRでNRR数値の正式開示確認 | F1 | blocked_source | 2025-02-14 |
| EDGE-F2-BYOC-1 | EDGE | WarpStream買収＝BYOC拡張のTAM加速仮説 | advance next-gen BYOC data streaming | Press release | 定量TAMは未開示→定性のまま維持 | 次回IRでBYOC TAM定量化確認 | F2 | not_found | 2025-06-14 |
| EDGE-F2-BYOC-PRICE-1 | EDGE | WarpStream買収額 ≈ $220M（非公式数値） | acquired WarpStream for $220M after just 13 months | LinkedIn | 会社公表額なし。矛盾出たら即撤回 | 次回IRで買収額の正式開示確認 | F2 | blocked_source | 2025-06-14 |
| EDGE-F5-CTO-1 | EDGE | CTO交代（Stephen Deasy）→AI実装速度への影響 | Confluent ... appointment of Stephen Deasy as CTO | Investing.com | IR一次ソース確認でき次第T1昇格 | 次回IRでCTO交代の正式発表確認 | F5 | blocked_source | 2025-03-14 |
| EDGE-F1-HDW-1 | EDGE | AIネイティブ顧客の使用減少が成長鈍化要因 | consumption growth notably below ... due to optimization | SeekingAlpha transcript | マネジメント言及の一次発言で裏取り継続 | 10-Qで最適化影響の定量化確認 | F1 | not_found | 2025-02-14 |
| EDGE-F3-SA-1 | EDGE | Streaming Agentsの市場反応（投稿量/反響） | With Streaming Agents ... orchestrate event-driven agents | Twitter | ソーシャル指標はノイズ大→短TTLで再評価 | 次回IRでStreaming Agents商用進捗開示 | F3 | blocked_source | 2025-01-30 |
| EDGE-F3-SHIFTLEFT-1 | EDGE | Shift-leftでコスト削減（81%が効果と回答） | 81% of IT leaders reduced costs and risks | PR release | 自社調査のため第三者調査で補強必要 | 第三者調査での補強確認 | F3 | not_found | 2025-04-14 |
| EDGE-F4-PARTNER-REV-1 | EDGE | パートナー経由売上比率↑（$200M投資の成果） | $200 million investment over the next three years | Blog post | 定量比率の開示待ち（未開示） | 10-Qでパートナー売上比率の継続開示確認 | F4 | not_found | 2025-04-14 |
| EDGE-F1-DOWNGRADE-1 | EDGE | 7/31株価急落・アナリスト格下げの連鎖 | Stifel downgraded ... price target to $21 | Investing.com | 価格要因は一次資料で裏取り困難→参考 | アナリストレポートの一次確認 | F1 | blocked_source | 2025-01-14 |
| EDGE-F1-PIPELINE-1 | EDGE | Confluent Platformのパイプライン可視性改善 | Platform pipeline visibility improves | not_found | 出自不明→2週間で未確認なら棚卸し | 出自確認・2週間で棚卸し | F1 | not_found | 2025-01-01 |
| TW-CLAUDE-CL_QOQ-7 | EDGE | Cloud_revenue_qoq ≥ +7%（YoY引用からの派生KPI） | Cloud revenue $151m, up 28% YoY | https://investors.confluent.io/financials/quarterly-results | q/qはPL/BS併用で要算出（直接開示なし） | 次回IRでq/q成長率の直接開示確認 | CL_qoq | not_found | 2025-02-14 |
| TW-CLAUDE-FLINK-CFUx2 | EDGE | Flink_consumption_CFU_hours ≥ 2x_prior_Q | serverless ... charged only while queries execute | https://docs.confluent.io/cloud/current/flink/concepts/flink-billing.html | CFUは課金指標。実績は未開示→補助KPI | 次回IRでFlink CFU実績開示確認 | flink_consumption | not_found | 2025-02-14 |
| TW-CLAUDE-NRR-115 | EDGE | NRR < 115% を下げTWに使用 | Net Revenue Retention 114% | https://www.alphaspread.com/security/nasdaq/cflt/investor-relations | NRRの一次T1が恒常開示でないためEDGE | 次回IRでNRRの継続開示確認 | NRR | blocked_source | 2025-02-14 |
| TW-CLAUDE-BYOC-CANNIBAL | EDGE | BYOCがCloud移行をカニバる仮説 | WarpStream ... next-gen BYOC | https://www.confluent.io/blog/confluent-acquires-warpstream/ | 実測は未開示。顧客事例で補強要 | 次回IRでBYOC vs Cloud移行率開示 | byoc_cannibalization | not_found | 2025-06-14 |
| TW-GROK-AI-PARTNERS-2 | EDGE | AI Partnerships 新規 ≥2（イベント発生型） | discussing AI momentum and consumption headwinds | https://seekingalpha.com/article/4820687-confluent-inc-cflt-presents-at-goldman-sachs-communicopia-technology-conference-2025 | イベント情報は断片的→IR一次で検証要 | 次回IRでAIパートナーシップ新規件数確認 | ai_partnerships | blocked_source | 2025-02-01 |
| TW-GROK-NRR-110 | EDGE | NRR ≤110% を下げTW補助に使用 | NRR for the quarter was 114% | https://seekingalpha.com/article/4806526-confluent-inc-cflt-q2-2025-earnings-call-transcript | 一次IRログ未固定のためEDGE | 次回IRでNRRの継続開示確認 | NRR | blocked_source | 2025-02-14 |
| TW-GEMINI-SEC-CIK-MISMATCH | RESOLVED | SECリンクのCIK不一致（1716121）→要差替 | foreign CIK, mismatch vs 1699838 | https://www.sec.gov/Archives/edgar/data/1716121/000171612125000031/cflt-20250630.htm | 正はCIK=1699838。実際のファイルでは修正済み | 確認済み：正しいCIK=1699838で統一済み | CIK_correction | resolved | 2025-01-01 |
| TW-PPLX-ANCHOR-PLACEHOLDER | EDGE | placeholderアンカー（[41]/[43]）の再取得 | anchor placeholders require resolution | not_found | 解決までEDGEに留置。T1出たら昇格 | アンカー解決まで留置 | anchor_resolution | not_found | 2025-01-01 |
| TW-CLAUDE-FLINK-REV<5% | EDGE | Flink revenue <5% of total（反証条件） | Flink ARR ... annualizing actual consumption | https://investors.confluent.io/financials/quarterly-results | 分離開示なし→直接観測不可。補助仮説として保持 | 次回IRでFlink revenue比率開示確認 | flink_revenue_ratio | not_found | 2025-02-14 |
| ALPHA5-BANDS-CONFIG | EDGE | α5バンドしきい値（green/amber）未設定 | bands設定待ちのため data_gap | not_found | --alpha5-bands設定待ち | プロジェクト設定で--alpha5-bandsを設定 | alpha5_bands | data_gap | 2025-01-08 |
| EDGE-FLINK-ARR-10M | EDGE | Flink ARR ≈ $10M（H1で~3倍） | Flink ARR approximately $10 million | Yahoo Finance/Investing.com | T1未掲の金額表現 | 将来IR資料でT1昇格を待つ | flink_arr_absolute | blocked_source | 2025-02-15 |
| EDGE-RPO-GROWTH-31Q | EDGE | RPO growth 31%（四半期） | RPO growth of 31% year over year | Yahoo Finance/SeekingAlpha | 10-Qは割合59%のみ | T1出典出れば昇格 | rpo_growth_rate | blocked_source | 2025-02-15 |
| ALPHA4-RPO-Q1-2025 | RESOLVED | Q1'25 RPO/12Mデータ | Q1'25 RPO $1,016.1M、~61%が12M、当期売上$271.1M→coverage=6.9ヶ月 | https://investors.confluent.io/static-files/5936d963-05cd-47cf-b6fb-c703e70910f7 | T1確証完了（IR補足PDF） | 確認済み：Q1'25 IR補足PDFからT1昇格 | rpo_q1_2025_coverage | resolved | 2025-01-01 |
| ALPHA4-RPO-Q3-2024 | RESOLVED | Q3'24 RPO/12Mデータ | Q3'24 RPO $883.0M、~65%が12M、当期売上$250,199k→coverage=6.9ヶ月 | https://www.sec.gov/Archives/edgar/data/1699838/000095017024119042/cflt-20240930.htm#:~:text=RPO%20was%20%24883.0%20million%2C%20approximately%2065%25 | T1確証完了 | 確認済み：Q3'24 10-Q本文からT1昇格 | rpo_q3_2024_coverage | resolved | 2025-01-01 |
| TW-EDGE-ALPHA5-DEV | EDGE | alpha5_residual_gp_$k > 8000 をbear補助に使用 | alpha5乖離TWはMVP外の補助TW | Ex.99.1 非GAAP表（URL#fragment・逐語） | 承認後にB.yamlで is_enabled:true に昇格 | 承認後にB.yamlで有効化 | alpha5_deviation_tw | not_found | 2025-04-15 |

# 中優先度追跡項目（B群）- 検証チェックリスト反映
| B-001 | U | SecureWise連結のコスト波及 | 売上側寄与（Analytics）とSG&A/金利の注記を突合し、COGSカテゴリとの整合を確認 | Ex.99.1 + 10-Q MD&A | COGSへの波及"あり得る"が本文と整合 | 次回IRでSecureWise連結影響の定量化確認 | securewise_cost_spillover | not_found | 2025-02-15 |
| B-002 | U | Mix→GMの再現性 | Q1/Q2のAnalytics比とNon-GAAP GMを並べ、モデル期待Δ vs 実測Δを追記 | Ex.99.1の表（2期） | 乖離の方向がMD&A要因と一致 | 次回IRでMix→GMモデルの継続検証 | mix_gm_reproducibility | not_found | 2025-02-15 |
