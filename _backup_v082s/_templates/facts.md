# T1確定事実（T1最優先×内部ETL完結版）

## T1最優先原則
- **T1確定**: sec.gov（10-K/10-Q/8-K）≧ investors.jfrog.com（IR PR/資料）
- **T2候補**: 他AI/記事/トランスクリプト（EDGE、TTL=7日、意思決定には使わない）
- **95%は内部ETLで完結、他AIは"場所のヒント＋照合"の5%**

## 逐語とアンカー（AnchorLint）
- 逐語は25語以内＋#:~:text=必須
- PDFは anchor_backup{pageno,quote,hash} を併記
- 取れない＝**「T1未開示」**で確定（"未取得"と混同しない）

[YYYY-MM-DD][T1-F|T1-C][Core①|Core②|Core③|Time] "逐語≤25語" (impact: KPI) <URL#:~:text=...>

## アンカー厳密化（情報削減ゼロ運用）

### verbatim_≤25w（法令順守用の短い逐語抜粋）
- 25語以内の厳密な逐語抜粋
- 見出し・目次は不可
- 本文から直接引用のみ
- #:~:text=必須

### context_note（文脈・但し書き・表名など長文OK）
- 文脈・但し書き・表名など長文OK
- 厳密化しても"最大情報"は温存
- 情報削減ゼロ運用

## 例

### ガイダンス発表（逐語≤25語）
[2024-12-15][T1-F][Time] "FY26 revenue guidance midpoint $2.5B (range $2.3B–$2.7B)." (impact: guidance_fy26_mid) <https://sec.gov/edgar/...#:~:text=revenue%20guidance%20midpoint>

### 進捗イベント（8-K/PR/契約）
[2024-12-15][T1-F][Core③] "Signed multi-year fixed-fee license with Microsoft." (impact: rpo_stepup_event) <https://sec.gov/edgar/...#:~:text=multi-year%20fixed-fee>

### キャッシュ系（10-Q/10-K）
[2024-12-15][T1-F][Core②] "Free cash flow $150M for the quarter." (impact: fcf_q) <https://sec.gov/edgar/...#:~:text=Free%20cash%20flow>

[2024-12-15][T1-F][Core②] "Capital expenditures $25M." (impact: capex_q) <https://sec.gov/edgar/...#:~:text=Capital%20expenditures>

### 従来例
[2024-12-15][T1-F][Core①] "FY26 revenue floor of $2.5B represents 15% growth" (impact: FY26_Floor) <https://sec.gov/edgar/...#:~:text=revenue%20floor>

[2024-12-15][T1-C][Core②] "Fixed-fee contracts represent 75% of backlog" (impact: Fixed_fee_ratio) <https://ir.company.com/earnings/...#:~:text=Fixed-fee%20contracts>

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
