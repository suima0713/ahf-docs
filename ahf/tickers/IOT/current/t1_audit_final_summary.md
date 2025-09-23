# IOT T1監査完了・最終確定版

## 1) Anchor Backup確定（SHA1付与）

**✅ 全アンカーバックアップハッシュ確定済み:**
- `cik_line`: 7904aa594e8147911730045f09b30bafdcfcc2ac
- `non_gaap_gm`: 6d205501a49f645ac121c59faab22a6f7dd93eab
- `total_revenue`: 3379c7cddf84edd8801c35f225987882ed98e4f3
- `nongaap_oi`: 13b2f51b8e9b7f36b2640e4c0894c9d763926af6
- `da_line`: 665174987f938094e377e947e5df9d181cceed66
- `rpo_12m`: 54712600a6cb63dba31f8fa74237b0439fae8c8e
- `rpo_total`: 22a3bc5988e61c50519c40c76f5344833e60676f
- `deferred_rev_end`: cfa0f7d7936a2a63749607adcc3c1a71978219e9

## 2) facts.md（T1のみ／逐語≤25語＋#fragment）

**✅ 全T1逐語記録更新完了:**
- Total revenue $391.5 million — Ex.99.1 (hash: 3379c7cd...)
- Non-GAAP gross margin 78% — Ex.99.1 (hash: 6d205501...)
- Non-GAAP operating income $59,698 — Ex.99.1 (hash: 13b2f51b...)
- Depreciation and amortization 5,399 — Ex.99.1 (hash: 66517498...)
- RPO was $3,165.5 million — 10-Q (hash: 22a3bc59...)
- approximately $1,401.8 million over the next 12 months — 10-Q (hash: 54712600...)
- Deferred revenue, end of period $740,512 — 10-Q (hash: cfa0f7d7...)
- CIK lock: Samsara Inc. (Filer) CIK : 0001642896 (hash: 7904aa59...)

## 3) triage.json（CONFIRMED/T1 と UNCERTAIN/Edge）

**✅ CONFIRMED T1データ:**
- revenue_q=391480k
- ng_gm_pct_q=78.0
- nongaap_oi_q=59698k
- da_q=5399k
- rpo_total=3165500k
- rpo_12m=1401800k
- cl_end=740512k
- coverage_months=10.7

**✅ UNCERTAINギャップ:**
- adjusted_ebitda: NOT_DISCLOSED (30日)
- contract_assets: TAG_ABSENT (30日)
- alpha3_segments: NOT_DISCLOSED (60日)

## 4) α5バンド設定（運用パラメータロック）

**✅ ALPHA5運用パラメータ確定:**
- 計算OpEx: $240,595k
- Green ≤ $246,600k（+2.5%）
- Amber ≤ $258,600k（+7.5%）
- Red > $258,600k
- alpha5_math_pass: true

## 5) AHFマトリクス（現行版固定）

**✅ 最終確定版AHFマトリクス:**
- ①右肩: ★3（売上$391,480k・YoY+30%/ARR $1.640B）
- ②勾配: ★3（非GAAP粗利率78%、OpEx≈$240,595k）
- ③時間軸: ★2（RPO 12M=$1,401,800k→coverage10.7m（Gate<11））
- ④認知ギャップ: ★2（CL q/q +4.9%（+5%TW未達））

## 6) TW監視自動実行設定

**✅ 週次監視設定完了:**
- 頻度: 毎週金曜 09:00 JST
- 対象: IOT (CIK 0001642896)
- 監視項目: CL_qoq, coverage_months
- トリガー: CL≥+5% OR coverage≥11
- 通知: TWヒット時自動通知

## 結論ワンライナー

**IOTはα5=OpEx約$240,595kで効率は維持、α4はcoverage10.7ヶ月でGate未達。主リスク=CL伸び鈍化、上振れ=ARR拡大と粗利維持。**

## ファイル更新完了

- ✅ facts.md: T1逐語 + anchor backup hashes
- ✅ triage.json: CONFIRMED T1 + UNCERTAIN gaps
- ✅ impact_cards.json: ALPHA5 bands + operational parameters
- ✅ ahf_matrix_t1_confirmed.json: 最終確定版マトリクス
- ✅ tw_monitoring_config.json: 週次監視設定
- ✅ 全ファイル整合性確認済み

**T1監査ステータス: ✅ 完了・運用開始準備完了**
