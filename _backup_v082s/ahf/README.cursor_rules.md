# AHF Cursor Rules - T1最優先×内部ETL完結 (v0.3.3)

## 基本原則（最優先）

### T1最優先×内部ETL完結
- **T1確定**: sec.gov（10-K/10-Q/8-K）≧ investors.jfrog.com（IR PR/資料）
- **T2候補**: 他AI/記事/トランスクリプト（EDGE、TTL=7日、意思決定には使わない）
- **95%は内部ETLで完結、他AIは"場所のヒント＋照合"の5%**

### ソース優先順位（固定）
1. **Primary**: SEC EDGAR（10-K/10-Q/8-K）
2. **Secondary**: Company IR（investors.jfrog.com等）
3. **T2候補**: 他AI/記事/トランスクリプト（EDGE、TTL=7日）

### 逐語とアンカー（AnchorLint）
- 逐語は25語以内＋#:~:text=必須
- PDFは anchor_backup{pageno,quote,hash} を併記
- 取れない＝**「T1未開示」**で確定（"未取得"と混同しない）

### 内部ETLワークフロー（E→T→L）
1. **Extract**: T1から所定の行を抽出
   - RPO総額/12M比率、NDR、$1M+顧客、Cloud/Enterprise+
   - GAAP/Non-GAAP OI、GMとhosting因果、SBC額、Cash/FCF
   - A/R・Deferred、Debt/Loans/Notes、Expected future amortization、CapEx
2. **Transform**: 標準式で派生KPIを算出
   - DSO(H1)＝(平均AR/6M売上)×181
   - DSO(Q)＝(期末AR/四半期売上)×91
   - EV＝時価総額 − 現金 ± 有利子負債
   - EV/S(Fwd)＝EV ÷ NTM売上（T1ガイド中点）
   - Ro40＝成長% + GAAP OPM%
   - DI＝(0.6·s2 + 0.4·s1)·Vmult
3. **Load**: facts/triageに格納
   - dual_anchor_status（CONFIRMED｜PENDING_SEC｜SINGLE）
   - auto_checks（anchor_lint/alpha4/alpha5）と TTL を明記

### 判定のヒステリシス（③VRG）
- 前回比 |ΔEV/S|<0.5× かつ |ΔRo40|<2pp は色据え置き（アップグレードのみ1.2×緩和）

### 他AIの役割（限定）
- **用途**: 所在の手掛かり（例：10-K注記ページ、見出し名）と突合
- **扱い**: 必ずT2（EDGE/TTL=7日）。T1で再取得・再計算してからスコア/DIへ反映
- **禁止**: 他AIの数値や文言を直接引用・採用しない

### "未開示"の確定
Marketplace寄与%、SKUアタッチ%、SBC"normalize"の目標%/時期、ガイダンス上方の条件文 など、現行T1に無ければ「T1未開示」確定。推定や二次は載せない。

### 例外処理
- HTMLで #:~:text= 不可→PDF anchor_backupへフォールバック
- SEC HTMLとPDFで表現差→SEC PDF優先、IRは補助

### ログと透明性
すべての更新で 差分（何を上書き/降格） と 根拠URL/backup を記録。EDGEは意思決定に影響させない（ウォッチ材料のみ）。

## 実装完了状況

### ✅ AHF EDGAR CLI Skeleton (MVP-4+) 完全実装済み

**場所**: `ahf/ahf_edgar_cli.py`

**機能**:
- EDGAR純正API＋軽量テキスト解析でα4/α5を自動判断
- AHFにそのまま流せるJSONを出力
- Dual-Anchorによる根拠保存
- Gap-Reasonによる取得失敗理由記録

### 主要機能

1. **自動判断**
   - α4のcoverage_months自動算出（12M%×RPO合計／Quarterly Rev）
   - α5のOpExとBand判定（Green/Amber/Red）
   - auto_checksでGate/Band通過や未計算理由を格納

2. **ダブルチェック**
   - Dual-Anchor（primary + 逐語ハッシュ）で根拠を再定位
   - Gap-Reason（NOT_DISCLOSED/PHRASE_NOT_FOUND等）で「取れない理由」を必ず記録

3. **完全なCLIインターフェース**
   - コマンドライン引数対応
   - 出力JSONフォーマット
   - エラーハンドリング完備

### 使用方法

```bash
# 基本使用
python ahf_edgar_cli.py --cik 1819994 \
  --user-agent "AHF/0.6.0 (ops@example.com)" \
  --alpha5-bands 83000 86500 \
  --out rklb_q2_2025.json
```

### 出力データ構造

```json
{
  "cik": 1819994,
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
  "anchors": {
    "alpha4": {"anchor_primary": "...", "anchor_backup": {...}},
    "alpha5": {"anchor_primary": "...", "anchor_backup": {...}}
  },
  "auto_checks": {
    "alpha5_math_pass": true,
    "alpha4_gate_pass": true,
    "messages": []
  }
}
```

### 主要計算式

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

### テスト状況

✅ 全テストケースがパス  
✅ 数値変換、SHA1ハッシュ、HTML解析  
✅ Ex.99.1解析、Dual-Anchor、Gap-Reason  
✅ α5 OpEx計算、Band判定、α4 Coverage Months計算  

### 拡張可能性

- 複数CIKのバッチ処理
- 結果の比較ダッシュボード化
- 定期的な自動実行と監視機能

### 関連ファイル

- `ahf/ahf_edgar_cli.py`: メインCLIスクリプト
- `ahf/tests/test_ahf_edgar_cli.py`: テストケース
- `ahf/mvp4/`: MVP-4モジュール群
- `ahf/README.cli.md`: 詳細ドキュメント
- `ahf/README.edgar.md`: EDGAR最適化ドキュメント

## 即座に利用可能

この実装により、EDGAR情報の検索・分析・比較が瞬時に可能。何か特定の企業や指標について質問があれば、すぐに回答可能。

## 注意事項

- レート制限: EDGAR APIは10 req/s以下で使用
- User-Agent: 必須（会社名/連絡先を設定）
- データ品質: 取得データの妥当性を必ず確認
- エラーハンドリング: ネットワークエラー時の適切な処理
