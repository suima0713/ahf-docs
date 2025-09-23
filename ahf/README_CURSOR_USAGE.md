# AHF Min - カーソルでの使い方（最小手順）

## 基本セットアップ

### 1. フォルダを開く
```
ahf/ をCursorで開く
```

### 2. そのまま一度走らせる
```bash
python src/ahf_min.py --config config/thresholds.yaml --state state/example_state.json --out out/eval.json
```

## 数値を差し替えるだけで再評価

### 例1: RPO 12M カバー月数の変更
```json
// state/example_state.json を編集
{
  "rpo_12m_months_vs_q4_mid": 10.5,  // ← この値を変更
  // ...
}
```
保存 → 再実行

### 例2: Mix入力の変更
```json
// state/example_state.json を編集
{
  "delta_sw_pp": 2.0,    // ← SW変化
  "delta_ops_pp": 0.0,   // ← Ops変化
  "revenue_$k": 600000,  // ← 売上
  // ...
}
```
保存 → 再実行 → ΔGM=+1.2pp、rev_$k=600000なら EBITDA +$7,200k へ反映

## 実装した"優先4つ"の中身（最小）

### ① Gate/Band早見表
- **alpha4_gate_months**: 11.0（RPO 12M カバー基準）
- **alpha5_bands**: {green≤83,000, amber≤86,500}（$k）

### ② GM→EBITDA換算係数
- **gm_to_ebitda_pp_factor_$k**: {590000:5900, 600000:6000, 610000:6100}

### ③ TW優先度（衝突解決）
- **tripwire_priority**: ["contract_liabilities","greenbox_rollforward","unbilled_dou","mix"]

### ④ OT/PT未開示スロット（代理KPI）
- **目標**: unbilled_share_pct≤50% / dou_days≤30 / cl_qoq≥0

## 自動化機能

### RPOカバー月数→Gate判定（11ヶ月基準）
- 10.5ヶ月 → FAIL
- 11.5ヶ月 → PASS

### Q4ガイド→OpEx帯域（Green/Amber/Red）
- $83,000k以下 → GREEN
- $83,000k〜$86,500k → AMBER
- $86,500k超 → RED

### Mix入力→EBITDA変化（Rev別係数で即時換算）
- 売上$600k、ΔGM+1.2pp → EBITDA +$7,200k
- 売上$590k、ΔGM+1.2pp → EBITDA +$7,080k

### TW衝突時の一意決定（最上位のみで★/確信度を動かす前段）
1. Contract Liabilities（CL）方向
2. GreenBoxロールフォワード（Deferred/UB/消化）
3. DoU / Unbilled 指数
4. Mix（ΔSW/ΔOps）

## 出力例

```json
{
  "alpha4_gate": {
    "gate": "PASS",
    "value": 11.5,
    "threshold": 11.0,
    "description": "RPO 12M カバー 11.5ヶ月 vs 11.0ヶ月基準"
  },
  "alpha5_bands": {
    "band": "AMBER",
    "value": 85000,
    "thresholds": {"green": 83000, "amber": 86500},
    "description": "OpEx $85,000k → AMBER帯域"
  },
  "gm_to_ebitda_conversion": {
    "ebitda_impact_$k": 7200.0,
    "delta_gm_pp": 1.2,
    "revenue_$k": 600000,
    "factor": 6000,
    "description": "ΔGM +1.2pp × Rev $600,000k × 6000k = EBITDA +7,200k"
  }
}
```

## 次の10-Q/Ex.99.1が出た瞬間に

1. **Gate/Band判定** → ★/確信度を機械的に更新
2. **Mix入力** → EBITDAを即換算
3. **OT/PT未開示でも代理指標で方針判断が可能**

実装損ほぼゼロで意思決定の速さに直結する構造が完成。

