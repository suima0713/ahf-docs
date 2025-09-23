# AHF EDGAR CLI Skeleton (MVP-4+) — 完全版

**目的**: EDGAR純正API＋軽量テキスト解析でα4/α5を自動判断し、AHFにそのまま流せるJSONを出力

## 🚀 主要機能

### 自動判断
- **α4のcoverage_months自動算出**: 12M%×RPO合計／Quarterly Rev
- **α5のOpExとBand判定**: Green/Amber/Redを即判定
- **auto_checks**: Gate/Band通過や未計算理由を格納

### ダブルチェック
- **Dual-Anchor**: primary + 逐語ハッシュで根拠を再定位
- **Gap-Reason**: NOT_DISCLOSED/PHRASE_NOT_FOUND等で「取れない理由」を必ず記録

## 📋 使用方法

### 基本使用
```bash
python ahf_edgar_cli.py --cik 1819994 \
  --user-agent "AHF/0.6.0 (ops@example.com)" \
  --alpha5-bands 83000 86500 \
  --out rklb_q2_2025.json
```

### 引数説明
- `--cik`: 企業のCIK（必須）
- `--user-agent`: HTTP User-Agent（EDGAR必須）
- `--alpha5-bands`: α5のBand閾値（Green≤, Amber≤）
- `--out`: 出力JSONファイルパス（任意）

### 出力例
```json
{
  "cik": 1819994,
  "docs": {
    "10-Q": {
      "accession": "0001819994-24-000123",
      "primary": "rklb-20250630.htm",
      "filing_date": "2025-07-15",
      "index_url": "https://www.sec.gov/Archives/edgar/data/1819994/000181999424000123/rklb-20250630.htm"
    },
    "8-K": {
      "accession": "0001819994-24-000124",
      "primary": "rklb-20250715.htm",
      "filing_date": "2025-07-15",
      "index_url": "https://www.sec.gov/Archives/edgar/data/1819994/000181999424000124/rklb-20250715.htm",
      "ex99_url": "https://www.sec.gov/Archives/edgar/data/1819994/000181999424000124/ex99-1.htm"
    }
  },
  "alpha4_rpo": {
    "rpo_total_$k": 995410,
    "rpo_12m_pct": 58.0,
    "rpo_12m_$k": 577338,
    "coverage_months": 12.0,
    "find_path": "note",
    "gap_reason": null
  },
  "alpha5_inputs": {
    "rev_$k": 144498,
    "ng_gm_pct": 36.9,
    "adj_ebitda_$k": -27584,
    "status": "ok"
  },
  "alpha5": {
    "opex_$k": 80800,
    "band": "Amber",
    "bands": {"green_≤": 83000, "amber_≤": 86500}
  },
  "facts": {
    "contract_liabilities_$k": 125000
  },
  "anchors": {
    "alpha4": {
      "anchor_primary": "https://www.sec.gov/Archives/edgar/data/1819994/000181999424000123/rklb-20250630.htm#:~:text=within%2012%20months",
      "anchor_backup": {
        "pageno": null,
        "quote": "… within 12 months …",
        "hash": "a1b2c3d4e5f6..."
      }
    },
    "alpha5": {
      "anchor_primary": "https://www.sec.gov/Archives/edgar/data/1819994/000181999424000124/ex99-1.htm",
      "anchor_backup": {
        "pageno": null,
        "quote": "Total revenues … Non-GAAP Gross margin … Adjusted EBITDA …",
        "hash": "f6e5d4c3b2a1..."
      }
    }
  },
  "auto_checks": {
    "alpha5_math_pass": true,
    "alpha4_gate_pass": true,
    "messages": []
  }
}
```

## 🔧 実装詳細

### データ取得フロー
1. **Discovery**: 最新10-Q/10-K/8-Kのアクセッション確定
2. **Company Facts**: RPO/CLをXBRLタグから取得
3. **HTML解析**: 10-Q本文から12M%を抽出
4. **Ex.99.1解析**: 8-KからRev/NG-GM/Adj.EBITDAを抽出
5. **自動計算**: α4 coverage_months、α5 OpEx/Band判定
6. **アンカー作成**: Dual-Anchorで根拠を保存
7. **ギャップログ**: 取得失敗理由を記録

### 計算式
```python
# α4 Coverage Months
coverage_months = (rpo_12m_$k / quarterly_rev_$k) * 3.0

# α5 OpEx
opex_$k = rev_$k * (ng_gm_pct / 100.0) - adj_ebitda_$k

# α5 Band判定
if opex_$k <= green_threshold: "Green"
elif opex_$k <= amber_threshold: "Amber"  
else: "Red"
```

### エラーハンドリング
- **レート制限**: 0.2秒間隔でEDGAR API呼び出し
- **タイムアウト**: 30秒でHTTPリクエスト制限
- **データ検証**: 異常値の自動検出とギャップログ
- **フォールバック**: 複数タグでのXBRLデータ取得

## 🧪 テスト

```bash
# 全テスト実行
python tests/test_ahf_edgar_cli.py

# 個別テスト
python -c "from tests.test_ahf_edgar_cli import test_alpha5_compute_opex; test_alpha5_compute_opex()"
```

## 📊 出力データ構造

### 主要フィールド
- `alpha4_rpo`: RPO関連データ（合計、12M%、coverage_months）
- `alpha5_inputs`: Ex.99.1から抽出した3項目
- `alpha5`: 計算されたOpExとBand判定
- `anchors`: Dual-Anchorによる根拠保存
- `auto_checks`: 自動判定結果とメッセージ

### ギャップログ
- `NOT_DISCLOSED`: データが開示されていない
- `TAG_ABSENT`: XBRLタグが存在しない
- `PHRASE_NOT_FOUND`: 注記テキストに該当フレーズなし
- `DIFF_PERIOD`: 期間が異なる

## 🚀 拡張可能性

### バッチ処理
```bash
# 複数CIKの一括処理
for cik in 1819994 1753539 1844452; do
  python ahf_edgar_cli.py --cik $cik --out ${cik}_q2_2025.json
done
```

### ダッシュボード化
- 複数結果の比較分析
- 時系列でのBand変化追跡
- ギャップログの集計と傾向分析

### 監視機能
- 定期的な自動実行
- 異常値のアラート
- データ品質の継続監視

## ⚠️ 注意事項

- **レート制限**: EDGAR APIは10 req/s以下で使用
- **User-Agent**: 必須（会社名/連絡先を設定）
- **データ品質**: 取得データの妥当性を必ず確認
- **エラーハンドリング**: ネットワークエラー時の適切な処理

## 🔗 関連ファイル

- `ahf_edgar_cli.py`: メインCLIスクリプト
- `tests/test_ahf_edgar_cli.py`: テストケース
- `mvp4/`: MVP-4モジュール群
- `README.edgar.md`: EDGAR最適化ドキュメント
