# AAOI (Applied Optoelectronics) - 詳細分析結果

## A) ① 長期EV確度（強度）詳細

### 流動性・資本構成（逐語）
- 「Cash… $87,195」／「Convertible Senior Notes $133,936」
- キャッシュ/転債比率: 87.2M / 133.9M ≈ 0.65（健全）

### キャッシュ品質（QoQ推移）
- AR $211.5M・在庫 $138.9M → DSO≈187日（=AR/Rev×91）、DOH≈176日（=在庫/COGS×91）
- 上期でΔAR −$94.7M、Δ在庫 −$51.0Mの積み上げ（CF）
- 在庫積上げ＝受注→量産準備の解釈

### 顧客濃度（逐語）
- 「top ten customers represented 98%…」
- 集中度リスク：高（98% vs 94% YoY）

### 供給/能力（逐語）
- 「approval of our Taiwan factory for 800G…」
- 台湾工場の800G生産承認取得

### 降格/昇格トリガ（≤25語）
1. 「800G量産開始を開示」
2. 「追加顧客の800G承認」
3. 「契約負債の増加」
4. 「在庫圧縮の継続」

**LEC総評**: 成長基盤は強いが顧客集中と運転資本ストレッチが重い→★3（保守）

## B) ② 長期EV勾配（12–24M）

### ガイダンス改定率%
- 前回中点なし→n/a（0%）

### 受注/Backlog代理
- 上期でΔAR −$94.7M、Δ在庫 −$51.0Mの積み上げ（CF）

### 非GAAP→GAAPブリッジ
- Q2 Loss from operations −$16.0M（−15.5%）

### α3/α5（定義準拠）
- α3=1（因果明示＝800G資格/出荷時期）
- α5=2（OPM改善の素地）
- →S=3 ⇒ ★4

### 12–24Mシナリオ
- Base: ~$480M（Q3中点×4）
- High: ~$520M（800G量産+）
- Low: ~$400M（遅延・歩留悪化）

## C) ③ バリュエーション＋認知ギャップ（V-Overlay 2.0）

### TRI（0–2）
- T=2（工場承認＋H2出荷明示）
- R=1（IR/PR露出）
- →S_base=3→★加点で**★4**

### Ro40（GAAP）
- YoY +137.9%（$102.95M vs $43.27M）＋ OPM −15.5%＝~122

### EV/S(Fwd)【Price-Mode】
- EV $1.95B（Yahoo Key Statistics, 2025-09-23）
- NTM売上 $484M → 4.0×（Green）

### DI再計算
- V倍率=1.05（Green）

### 色替えトリガ（≤25語）
1. 「800G実出荷の逐語」
2. 「ガイダンス上方改定」
3. 「GAAP OPMの連続改善」

## data_gap（UNCERTAINは削除せず明示）

### gap_reason
- 前回ガイド中点（改定％起点）不在
- FY25通期ガイダンス未提示

### TTL
- 7日（追補T1探索の再試行期限）

### dual_anchor_status
- CONFIRMED（SEC 8-K EX-99.1 + 10-Q）

### auto_checks
- {anchor_lint_pass:true, alpha5_math_pass:true}

### find_path
- site:sec.gov AAOI 8-K 2025 exhibit 99.1 → EX-99.1開示
- site:sec.gov AAOI 10-Q 2025 → 2025-06-30 10-Q本文に到達

## ログ

### rss_score（次Q寄与）
- = +8.74（0.5×17.48%）

### alpha3_score
- 1

### alpha5_score
- 2

### tri3
- {T:2, R:1, V:Green, star:4, bonus_applied:false}

### valuation_overlay
- {status:Green, ev_sales_fwd:~4.0×, rule_of_40:~122, hysteresis:{evsales_delta:0.5, ro40_delta:2.0, upgrade_factor:1.2}}

### interrupts
- []

## 実行した"次アクション"

### T1再取得＆確証
- 8-K EX-99.1と10-Qから候補値（売上$103.0M、GM30.3%、Q3ガイド、800G H2）を逐語+#:~:textで確定

### 運転資本の健全性評価
- 10-QからAR/在庫/契約負債（0）を抽出→DSO/DOHを算出

### NES再計算
- q/q=+17.5%、改定%=0%、代理増勢=0、Margin term=0 → NES=+8.7（★5）

### VRG Price-Mode更新
- 2025-09-23時点のYahoo EVでEV/S≈4.0×、Ro40~122→Green

### トリガー明示
- 量産開始／ガイダンス上方／GAAP OPM連続改善を昇格条件として設定
