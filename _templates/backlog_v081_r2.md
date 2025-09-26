# AHF v0.8.1-r2 バックログテンプレート
# U/Leadのワンテーブル（固定4軸対応）

## 基本情報
- 銘柄: 
- 評価日: YYYY-MM-DD
- バージョン: v0.8.1-r2
- 目的: 投資判断に直結する固定4軸で評価
- MVP: ①②③④の名称と順序を絶対固定／T1 or T1*で確証（不足はn/a）／定型テーブル＋1行要約を即出力

## バックログテーブル

| id | class=U | KPI/主張 | 現在の根拠≤40語 | ソース | T1化に足りないもの | 次アクション | 関連Impact | unavailability_reason | grace_until |
|----|---------|----------|-----------------|--------|-------------------|--------------|------------|---------------------|-------------|
| U-001 | U | LEC計算 | 成長率15%だが希薄化影響不明 | ニュース記事 | SEC 10-Kの希薄化情報 | SEC 10-K確認 | LECスコア計算 | EDGAR_down | 2024-01-20 |
| U-002 | U | NES計算 | ガイダンス改定8%だが受注情報なし | IR発表 | 受注/Backlog詳細データ | IR詳細確認 | NESスコア計算 | rate_limited | 2024-01-18 |
| U-003 | U | Current_Val | EV/S 15.2xだがpeer比較不明 | 内部ETL | peer median計算 | peer分析実行 | バリュエーション判定 | data_unavailable | 2024-01-22 |
| U-004 | U | Future_Val | rDCF計算用のg_fwd不明 | アナリストレポート | T1/T1*のg_fwd | SEC確認 | 将来バリュ計算 | not_found | 2024-01-19 |

## 証拠階層別サマリー

### T1*候補
- **U-001**: SEC 10-K確認待ち（TTL: 7日）
- **U-002**: IR詳細確認待ち（TTL: 5日）

### T2候補
- **U-003**: peer分析実行待ち（TTL: 10日）
- **U-004**: SEC確認待ち（TTL: 8日）

## 優先度管理

### 高優先度（TTL ≤ 7日）
- U-002: NES計算に直結
- U-004: Future_Val計算に直結

### 中優先度（TTL 8-14日）
- U-001: LEC計算に直結
- U-003: Current_Val計算に直結

## 次アクション

### 即座実行
1. SEC 10-Kの希薄化情報確認
2. IR詳細データ取得
3. peer median計算実行
4. T1/T1*のg_fwd確認

### 定期確認
- TTL期限切れアイテムの再評価
- 優先度の再調整
- 関連Impactの更新

## データギャップ

### 不足データ
- LEC: 希薄化情報
- NES: 受注/Backlog情報
- Current_Val: peer median
- Future_Val: g_fwd

### ギャップ理由
- EDGAR_down: SEC EDGAR障害
- rate_limited: API制限
- data_unavailable: データ未提供
- not_found: 該当データなし

## 注意事項
- 全ての非T1データはここに記録
- TTL管理を厳格に実行
- 優先度は関連Impactで決定
- 次アクションは具体的に記録
