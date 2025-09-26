# AAOI T1一次情報検証モジュール実行結果

## A-1｜Q2'25実績＋Q3'25ガイダンス／800G可視性（EX-99.1, 8-K, Aug 7, 2025）

### 検証済みT1情報
- **「GAAP revenue was $103.0 million」** - Q2'25実績売上確認
- **「GAAP gross margin was 30.3%」** - Q2'25実績GM確認  
- **「Revenue in the range of $115 to $127 million」** - Q3'25ガイダンス確認
- **「meaningful shipments of 800G… second half of 2025」** - H2'25 800G出荷タイムライン確認
- **「capacity of over 100,000 units of 800G per month」** - 月産10万台800G生産能力確認

### インプリケーション
- Q3ガイダンス中点$121M → q/q +17.5%成長
- 800G H2'25「meaningful shipments」＋月産10万台可視性はプラス

## A-2｜Q2'25バランスシート（EX-99.1内のBS）

### 検証済みT1情報
- **「Cash, Cash Equivalents and Restricted Cash $87,195」** - 現金等$87.2M確認
- **「Convertible Senior Notes $133,936」** - 転換社債$133.9M確認

### インプリケーション
- キャッシュ/転債比率: 87.2M / 133.9M ≈ 0.65（健全）

## A-3｜運転資本／顧客濃度（10-Q, Jun 30, 2025）

### 検証済みT1情報
- **「accounts receivable was $211.5 million」** - AR残高確認
- **「top ten customers represented 98%…」** - 顧客集中度98%確認
- **「Unearned revenue… were both zero.」** - 前受収益ゼロ確認
- **「Total Revenue $102,952」** - Q2売上確認

### 計算結果
- **DSO（式：AR/Rev×91）＝約186.9日**（211.5/102.952×91）
- **DOH（式：Inv/COGS×91）＝約176.0日**（138.867/71.790×91）
- ※COGSは10-QのQ2数値（$71.790M）を使用

### インプリケーション
- AR/在庫の膨張は短期キャッシュ圧迫要因

## A-4｜Amazonウォラント（10-Q, Jun 30, 2025）

### 検証済みT1情報
- **「purchase up to… 7,945,399 shares」** - Amazon購入可能株式数確認
- **「vesting… based on purchases… up to $4 billion」** - 10年間$40億購入でベスティング確認

### インプリケーション
- Amazon需要連動（T1）で確実な顧客基盤確保

## A-5｜2030転換社債条件（8-K, Dec 23, 2024）

### 検証済みT1情報
- **「bear interest at 2.750%…」** - 年利2.75%確認
- **「will mature on January 15, 2030」** - 2030年1月15日満期確認

### インプリケーション
- 低利子負債で資金調達コスト管理

## A-6｜ATMプログラム拡張（424B5, Aug 27, 2025）

### 検証済みT1情報
- **「aggregate offering price of up to $150,000,000」** - ATMプログラム$1.5億確認

### インプリケーション
- 流動性手段を確保（希薄化とトレード）

## ①②③への即時インプリケーション（簡易スナップ）

### ①長期EV確度
- 現金等$87.2M／社債$133.9M、ATM$150Mで流動性手段を確保（希薄化とトレード）
- AR/在庫の膨張は短期キャッシュ圧迫

### ②長期EV勾配
- Q3売上$115–127M＆非GAAP GM 29.5–31.0%、800GH2'25「meaningful shipments」＋月産10万台可視性はプラス

### ③VRG（定量色判定は別工程）
- Amazon需要連動（T1）・ATM/CB条件は"認知"補助（色決定自体はEV/S×Ro40で後続評価）

## data_gap（UNCERTAINのまま保持）

### USリボルビング枠「three-year, $35M」
- 該当8-K本文の逐語未取得
- gap_reason：SEC本文URL特定未了
- TTL：7日

### 台湾大型リース明細＆旧拠点解約（2025/8/31）
- 9/4/2025 8-K本文の逐語未取得
- TTL：7日

### 台湾子会社の与信ライン（〜2030/7/29）
- 該当8-Kの逐語未取得
- TTL：7日

## 検証結果サマリー

- **dual_anchor_status**: CONFIRMED（本回答で使用＝SEC 8-K/10-Q/424B5 のみ）
- **auto_checks**: {anchor_lint_pass:true}
- **find_path**: 
  - site:sec.gov 1158114 8-K 2025 exhibit 99.1
  - site:sec.gov 1158114 10-Q 2025-06-30
  - site:sec.gov 1158114 424B5 2025-08-27
