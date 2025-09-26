# AHF v0.6.3 実装完了

## 概要

AHF プロジェクト指示 v0.6.3（SYM｜T1限定・MVP-4+／Star整数＋最小緩和）の実装が完了しました。

## 主要機能

### 1. T1限定・Star整数評価システム
- **Star評価**: 1-5の整数評価（Core基準±1★以内で調整）
- **確信度**: 50-95%クリップ（Edge採用時±5pp調整）
- **方向確率**: 上向/下向確率（合計100%）

### 2. AnchorLint v1 + 二重アンカーシステム
- **テキストフラグメント**: `#:~:text=` 必須
- **逐語制限**: ≤25語
- **アンカーバックアップ**: {pageno, quote, hash(sha1)}
- **二重アンカー**: Primary=SEC, Secondary=IR

### 3. αブリッジ標準
- **α2**: Loss controls（従前）
- **α3**: Stage-1（ミックス）・Stage-2（効率）
- **α4**: RPO基準（coverage=(RPO_12M/Quarterly_Rev)×3, Gate≥11.0）
- **α5**: OpEx/EBITDA三角測量（乖離検知閾値$8,000k）

### 4. Edge管理システム
- **P付き先行仮説**: 採用基準P≥70 & 矛盾なし
- **軸別制限**: 各軸Edge最大2件・脚注≤35字
- **TTL管理**: 期限切れ自動処理

### 5. MVP-4+スキーマ拡張
- **direction_prob_up_pct/down_pct**: 方向確率（%）
- **gate_color**: Green/Amber/Red
- **dual_anchor_status**: CONFIRMED/PENDING_SEC/SINGLE
- **gap_reason**: データギャップ理由の標準化

### 6. 運用検証と監視KPI
- **Anchor充足率**: ≥98%
- **数理チェック**: 100%
- **CIKミスマッチ**: 0
- **差戻り率**: ≤5%
- **TW衝突**: 0
- **AnchorLint合格率**: ≥98%
- **PENDING_SEC変換率**: 7日以内≥90%
- **placeholder検出率**: 0
- **α4/α5計算停止率**: 0

## ファイル構成

```
ahf/
├── config/
│   ├── anchorlint.yaml              # AnchorLint設定
│   ├── thresholds.yaml              # 閾値設定
│   └── ahf_v063_sample_config.json  # v0.6.3サンプル設定
├── src/
│   └── ahf_min.py                   # AHF Min v0.6.3対応版
├── mvp4/
│   ├── alpha_bridge_v063.py         # αブリッジ標準
│   ├── edge_management_v063.py      # Edge管理システム
│   ├── operational_validation_v063.py # 運用検証
│   ├── anchor_lint_v1.py            # AnchorLint v1
│   ├── rpo_finder.py                # RPO検索
│   └── ex99_lite.py                 # Ex.99.1解析
├── schemas/
│   └── ahf_v063_schema.json         # v0.6.3スキーマ
├── scripts/
│   └── ahf_v063_integrated.py       # 統合実行スクリプト
└── state/
    └── ahf_v063_sample_state.json   # サンプル状態
```

## 使用方法

### 1. 基本実行
```bash
# AHF Min実行
python3 ahf/src/ahf_min.py --config ahf/config/thresholds.yaml --state ahf/state/ahf_v063_sample_state.json --out ahf/out/eval.json

# 統合実行
python3 ahf/scripts/ahf_v063_integrated.py --config ahf/config/ahf_v063_sample_config.json --state ahf/state/ahf_v063_sample_state.json --out ahf/out/integrated_eval.json
```

### 2. 個別機能実行
```bash
# αブリッジ標準
echo '{"revenue_$k": 600000, "ng_gm_pct": 75.5}' | python3 ahf/mvp4/alpha_bridge_v063.py ahf/config/ahf_v063_sample_config.json

# Edge管理
echo '{"edges": [...]}' | python3 ahf/mvp4/edge_management_v063.py ahf/config/ahf_v063_sample_config.json

# AnchorLint v1
echo '{"facts": [...]}' | python3 ahf/mvp4/anchor_lint_v1.py --config ahf/config/anchorlint.yaml

# 運用検証
echo '{"core_evaluation": {...}}' | python3 ahf/mvp4/operational_validation_v063.py ahf/config/ahf_v063_sample_config.json
```

## 表示フォーマット（固定順序）

```
📋 AHF v0.6.3 評価結果:
============================================================
①右肩上がり: RPO 12M カバー 12.5ヶ月 → GREEN
②勾配の質: OpEx $405,000k (乖離$0k vs 許容$8,000k)
③時間軸: ΔGM +1.5pp × Rev $600,000k × 1.0k = EBITDA +$9,000k
④認知ギャップ: 最上位有効: priority_1_cl

★評価: ★4/5 (Core3+Edge+1)
確信度: 確信度80% (Base75+Edge+5)
方向確率: 上向60% / 下向40%

🔍 自動チェック:
  α4 Gate: ✅
  α5 Math: ✅
  AnchorLint: ✅
```

## 監視KPI

- **Anchor充足率**: 98.0% (98/100) vs 98%基準 ✅
- **数理チェック**: 100.0% (3/3) vs 100%基準 ✅
- **CIKミスマッチ**: 0 vs 0基準 ✅
- **差戻り率**: 10.0% (1/10) vs ≤5%基準 ❌
- **TW衝突**: 0 vs 0基準 ✅
- **AnchorLint合格率**: 100.0% (2/2) vs 98%基準 ✅
- **PENDING_SEC変換率**: 100.0% (2/2) vs 90%基準 ✅
- **placeholder検出**: 0 vs 0基準 ✅
- **α計算停止率**: 0.0% (0/2) vs ≤0%基準 ✅

## 注意事項

1. **T1限定**: 未開示は未開示として扱い、事実の創出は禁止
2. **Star整数**: 1-5の整数のみ、小数は使用不可
3. **Edge制限**: 各軸最大2件、脚注35字以内
4. **Anchor必須**: テキストフラグメントとアンカーバックアップ必須
5. **非同期禁止**: 即時回答、重い課題は部分完了で返却

## 更新履歴

- **v0.6.3**: 正式版実装完了
  - T1限定・Star整数評価システム
  - AnchorLint v1 + 二重アンカー
  - αブリッジ標準（α2/α3/α4/α5）
  - Edge管理システム
  - MVP-4+スキーマ拡張
  - 運用検証と監視KPI

