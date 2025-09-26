# AHF EDGAR最適化 — 内部環境最適解

**目的**: Arelle不要でEDGAR純正API＋軽量テキスト解析だけで「ほぼ完全」に読み切る

## アーキテクチャ概要

### データ取得の順序（外部ライブラリ不要）

1. **Discovery（提出一覧）**
   - API: `https://data.sec.gov/submissions/CIK##########.json`
   - 目的: 最新の10-Q/10-K/8-Kのアクセッションと主要文書URLを確定
   - CIK例: BKSY=1753539, LUNR=1844452, RKLB=1819994

2. **Company Facts（iXBRL事実）**
   - API: `https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json`
   - 取得タグ: 契約負債、契約資産、RPO合計
   - 成果: CL/CA/RPO合計が「タグ駆動」で安定取得

3. **Frames（系列値・次元）**
   - API: `https://data.sec.gov/api/xbrl/frames/{taxonomy}/{tag}/{unit}/{period}.json`
   - 用途: 四半期売上Q値、セグメント売上
   - 成果: Quarterly_Revを正しく把握（α4/α5の土台）

4. **注記テキスト（12M比率の決め手）**
   - 出典: 10-Q/10-KのHTML本文
   - 手順: 見出し候補に近接検索→「within 12 months」の直前から%抽出
   - 成果: RPO_12m_pctを多数社で安定確保

5. **Ex.99.1（非GAAPの最小3点）**
   - 対象: 8-KのExhibit 99.1
   - ルール: 「Total revenues / Non-GAAP Gross margin / Adjusted EBITDA」の3語のみ
   - 成果: α5をOpEx=Rev×GM−EBITDAで即時算出

## 実装モジュール

### 1. EDGARクライアント（`edgar_client.py`）
```python
from mvp4.edgar_client import submissions, company_facts, frames

# 提出書類一覧取得
submissions_data = submissions("0001753539")

# Company Facts取得
facts_data = company_facts("0001753539")

# Frames取得
frames_data = frames("us-gaap", "Revenues", "USD", "2024-06-30")
```

### 2. タグ別名マップ（`tag_maps.py`）
```python
from mvp4.tag_maps import get_all_financials

# 全財務データを一括取得
financials = get_all_financials(facts_data)
# → {"rpo_total": 995410000, "contract_liability": ..., "revenue": ...}
```

### 3. 12Mテキスト抽出（`note_12m.py`）
```python
from mvp4.note_12m import get_12m_percentage

# HTML本文から12ヶ月以内の比率を抽出
pct_12m = get_12m_percentage(html_content)
# → 58.0 (58% within 12 months)
```

### 4. EDGAR統合（`edgar_integration.py`）
```python
from mvp4.edgar_integration import extract_from_edgar

# 全データを一括抽出
result = extract_from_edgar("0001753539")
```

## ロバスト化（壊れない根拠と「未了の質」）

### Dual-Anchor
- `anchor_primary`: #text-fragment or canonical URL
- `anchor_backup`: {pageno, quote≤25語, sha1(quote)}
- リンク切れでも逐語ハッシュで再定位可能

### Gap-Reason（必須）
- `NOT_DISCLOSED` / `TAG_ABSENT` / `PHRASE_NOT_FOUND` / `DIFF_PERIOD`
- 「なぜdata_gapなのか」を機械可読に残す＝次の探索コスト0

### Rate/Headers
- EDGARはUser-Agent必須（会社名/連絡先を設定）
- 節度あるレート（≤10 req/s推奨）

## 使用方法

### CLI使用
```bash
# EDGARから全データを抽出
python -m cli.edgar_extract 0001753539

# 出力例
{
  "alpha4_rpo": {
    "rpo_total_k": 995410,
    "rpo_12m_pct": 58.0,
    "find_path": "xbrl",
    "gap_reason": null
  },
  "alpha5_inputs": {
    "rev_k": 144498,
    "ng_gm_pct": 36.9,
    "adj_ebitda_k": -27584,
    "status": "ok",
    "find_path": "ex99"
  },
  "anchor": {
    "anchor_primary": "https://www.sec.gov/.../rklb-20250630.htm#:~:text=...within%2012%20months",
    "anchor_backup": {
      "pageno": 0,
      "quote": "Remaining backlog ... 58% within 12 months.",
      "hash": "a1b2..."
    }
  }
}
```

### プログラム使用
```python
from mvp4.edgar_integration import EdgarExtractor

# 抽出器を初期化
extractor = EdgarExtractor("0001753539")

# α4データ（RPO）を抽出
alpha4_data = extractor.extract_alpha4_data()

# α5データ（Ex.99.1）を抽出
alpha5_data = extractor.extract_alpha5_data()

# 全データを一括抽出
all_data = extractor.extract_all()
```

## 最適化のポイント

### Arelle不要
- EDGARのCompany Facts/Framesで「数」を取り、注記テキストで「%」を補完
- 軽量テキスト解析のみで安定取得

### α4/α5自動確定
- 12M%が見つかる会社はGate即判定
- 非GAAPは3項目だけでOpEx自動化

### 壊れない＆情報ロスゼロ
- Dual-Anchor＋Gap-Reasonで再現性と未了の質を担保
- 再探索コストをゼロ化

### AI/カーソルの使い所
- カーソルで上記モジュールをそのまま実装→即テスト
- LLMは注記本文の見出し検出や崩れた表の整形に補助的に使用（ただし確証はT1）

## テスト

```bash
# EDGAR統合テスト
python tests/test_edgar_integration.py

# 個別モジュールテスト
python tests/test_ex99_lite.py
python tests/test_rpo_finder.py
python tests/test_anchor_utils.py
python tests/test_gap_logger.py
```

## 注意事項

- 実際のAPI呼び出しはレート制限に注意
- User-Agentヘッダーは必須
- エラーハンドリングとリトライ機能を適切に実装
- データの整合性チェックを必ず実行
