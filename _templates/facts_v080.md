# T1確定事実（v0.8.0 - 固定3軸対応）

## T1最優先原則
- **T1確定**: sec.gov（10-K/10-Q/8-K）≧ investors.company.com（IR PR/資料）
- **T2候補**: 他AI/記事/トランスクリプト（EDGE、TTL=7日、意思決定には使わない）
- **95%は内部ETLで完結、他AIは"場所のヒント＋照合"の5%**

## 逐語とアンカー（AnchorLint v1）
- 逐語は25語以内＋#:~:text=必須
- PDFは anchor_backup{pageno,quote,hash} を併記
- 取れない＝**「T1未開示」**で確定（"未取得"と混同しない）

## 固定3軸のタグ規約

### ①長期EV確度（LEC）
[YYYY-MM-DD][T1-F|T1-C][LEC] "逐語≤25語" (impact: KPI) <URL#:~:text=...>

### ②長期EV勾配（NES）
[YYYY-MM-DD][T1-F|T1-C][NES] "逐語≤25語" (impact: KPI) <URL#:~:text=...>

### ③バリュエーション＋認知ギャップ（VRG）
[YYYY-MM-DD][T1-F|T1-C][VRG] "逐語≤25語" (impact: KPI) <URL#:~:text=...>

## 例

### ①長期EV確度（LEC）
[2024-12-15][T1-F][LEC] "Free cash flow $150M for the quarter." (impact: fcf_q) <https://sec.gov/edgar/...#:~:text=Free%20cash%20flow>

[2024-12-15][T1-F][LEC] "Capital expenditures $25M." (impact: capex_q) <https://sec.gov/edgar/...#:~:text=Capital%20expenditures>

[2024-12-15][T1-F][LEC] "Working capital decreased $30M." (impact: wc_change) <https://sec.gov/edgar/...#:~:text=Working%20capital>

### ②長期EV勾配（NES）
[2024-12-15][T1-F][NES] "Q4 revenue guidance $2.5B (15% YoY growth)." (impact: guidance_q4) <https://sec.gov/edgar/...#:~:text=revenue%20guidance>

[2024-12-15][T1-F][NES] "Gross margin improved 200bps to 75%." (impact: gm_improvement) <https://sec.gov/edgar/...#:~:text=Gross%20margin>

[2024-12-15][T1-F][NES] "Backlog increased 25% to $8.5B." (impact: backlog_growth) <https://sec.gov/edgar/...#:~:text=Backlog%20increased>

### ③バリュエーション＋認知ギャップ（VRG）
[2024-12-15][T1-F][VRG] "EV/S multiple 8.5x based on current market cap." (impact: evs_actual) <https://sec.gov/edgar/...#:~:text=EV/S%20multiple>

[2024-12-15][T1-F][VRG] "Peer median EV/S 12.3x." (impact: evs_peer_median) <https://sec.gov/edgar/...#:~:text=Peer%20median>

[2024-12-15][T1-F][VRG] "Fair value EV/S 10.2x based on DCF." (impact: evs_fair_rdcf) <https://sec.gov/edgar/...#:~:text=Fair%20value>

## 運用ルール
- **AUST必須**: As-of/Unit/Section-or-Table/≤25語/直URL
- **逐語のみ**: 本文から直接引用（見出し・目次不可）
- **UNCERTAIN混入禁止**: T1確定のみ記載
- **固定3軸**: ①LEC（長期EV確度）②NES（長期EV勾配）③VRG（バリュエーション＋認知ギャップ）
- **価格系隔離**: ③はPM+rDCFのみ（Ro40/GM/OPM/成長は②に限定）

