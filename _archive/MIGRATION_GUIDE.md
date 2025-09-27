# AHF Migration Guide - v0.8.2-SBへの移行

## 移行概要

### 対象バージョン
- **v0.7.3** → v0.8.2-SB
- **v0.8.0** → v0.8.2-SB
- **v0.8.1-R2** → v0.8.2-SB

### 主要変更点
1. **レンジ予測特化**: 投資判定からレンジ予測への転換
2. **Fact Maximization**: T1/T1*データの厳格化
3. **demote_not_delete**: 未確証データの保全
4. **時間窓固定**: 12-24M期間の強制

## データ移行

### 1. triage.json
**旧形式**:
```json
{
  "confirmed": [...],
  "pending": [...],
  "rejected": [...]
}
```

**新形式**:
```json
{
  "as_of": "YYYY-MM-DD",
  "CONFIRMED": [
    {
      "kpi": "...",
      "value": ...,
      "unit": "...",
      "asof": "...",
      "tag": "T1-core|T1-adj",
      "url": "..."
    }
  ],
  "UNCERTAIN": [
    {
      "kpi": "...",
      "status": "absent_on_T1",
      "ttl_days": 14,
      "find_path": "Next 10-Q/8-K: <section>"
    }
  ]
}
```

### 2. facts.md
**旧形式**:
```
[日付][ソース] 事実内容
```

**新形式**:
```
[YYYY-MM-DD][T1-F|T1-P|T1-C][Core①|Core②|Core③|Time] "逐語≤25語" (impact: KPI) <src>
```

### 3. A.yaml (材料)
**旧形式**: 複雑なマトリックス構造

**新形式**:
```yaml
meta:
  asof: YYYY-MM-DD
core:
  right_shoulder: []     # ①右肩上がり
  slope_quality: []      # ②傾きの質（NES式）
  time_profile: []       # ③時間
time_annotation:         # ④カタリスト（一度だけ）
  delta_t_quarters: 
  delta_g_pct: 
  window_quarters: 
  note: 
```

### 4. B.yaml (結論)
**旧形式**: 複数の判定軸

**新形式**:
```yaml
horizon:
  6M: {verdict: "", ΔIRRbp: }
  1Y: {verdict: "", ΔIRRbp: }
  3Y: {verdict: "", ΔIRRbp: }
  5Y: {verdict: "", ΔIRRbp: }
stance:
  decision: ""           # Go/保留/No-Go
  size: ""              # Low/Med/High
  reason: ""
kpi_watch: [2項目]
  - name: ""
    current: 
    target: 
```

## スクリプト移行

### 1. 評価エンジン
**旧**: `ahf_v081_r2_evaluator.py`
**新**: AHF Core v0.8.2-SBフレームワークに統合

**主要変更**:
- マトリックス計算の簡素化
- NES式の導入
- Vmult計算の標準化

### 2. ワークフロー管理
**旧**: `ahf_v081_r2_workflow.py`
**新**: Simple Control Promptに統合

**主要変更**:
- A/B二段階ワークフロー
- 判定確定の明確化
- レンジ予測の標準化

### 3. データ検証
**旧**: `ahf_v081_r2_anchor_lint.py`
**新**: AUST規律に統合

**主要変更**:
- T1/T1*の厳格化
- 逐語≤25語の制限
- anchor_backupの導入

## 計算式変更

### 1. NES式（②長期EV勾配）
**新規導入**:
```
NES = 0.5·(次Q q/q%) + 0.3·(改定%) + 0.2·(受注%) + Margin_term + Health_term
```

**Margin計算**:
- GM+50bps = +1
- ±50bps = 0
- GM-50bps = -1

**Health計算** (Ro40 = 成長% + GAAP OPM%):
- ≥40 = +1
- 30-40 = 0
- <30 = -1

### 2. 判定式（DI）
**旧**: 複雑なマトリックス計算

**新**:
```
DI = (0.6·②★/5 + 0.4·①★/5) · Vmult(③)
```

### 3. Vmult計算
**新規標準化**:
- Green: 1.05
- Amber: 0.90
- Red: 0.75

## 移行手順

### ステップ1: バックアップ
```powershell
Copy-Item -Path "tickers\*" -Destination "_backup_migration\" -Recurse
```

### ステップ2: 新テンプレート適用
```powershell
# 新しいA.yamlテンプレートをコピー
Copy-Item -Path "_templates\A.yaml" -Destination "tickers\<TICKER>\current\"
```

### ステップ3: データ変換
```powershell
# 自動変換スクリプト実行
.\Convert-LegacyToAHF.ps1 -Ticker <TICKER> -FromVersion v081_r2
```

### ステップ4: 検証
```powershell
# パリティ検証
.\Test-AHFParity.ps1 -Ticker <TICKER>
```

### ステップ5: 新フレームワーク実行
```
# AHF Core v0.8.2-SB Simple Control Promptを使用
```

## 互換性マトリックス

| 機能 | v0.7.3 | v0.8.0 | v0.8.1-R2 | v0.8.2-SB |
|------|--------|--------|-----------|-----------|
| triage.json | ❌ | ⚠️ | ✅ | ✅ |
| facts.md | ❌ | ❌ | ⚠️ | ✅ |
| A/B/C.yaml | ❌ | ❌ | ❌ | ✅ |
| PowerShell Scripts | ✅ | ✅ | ✅ | ✅ |
| Python Scripts | ❌ | ⚠️ | ⚠️ | ✅ |

**凡例**:
- ✅ 完全互換
- ⚠️ 部分互換（変換必要）
- ❌ 非互換（再作成必要）

## トラブルシューティング

### よくある問題

#### 1. triage.json形式エラー
**エラー**: `KeyError: 'CONFIRMED'`
**解決**: 新形式に変換
```json
{
  "CONFIRMED": [],
  "UNCERTAIN": []
}
```

#### 2. NES計算エラー
**エラー**: `ValueError: NES calculation failed`
**解決**: 必要なKPIを確認
- 次Q q/q%
- 改定%
- 受注%
- GM
- 成長%
- GAAP OPM%

#### 3. T1/T1*検証エラー
**エラー**: `ValidationError: Not T1 source`
**解決**: 出典を確認
- SEC EDGAR
- Company IR
- 独立二次×2のみ

### サポート

#### 技術サポート
- **自動変換**: `Convert-LegacyToAHF.ps1`使用
- **手動変換**: 新テンプレートに従って再構築
- **検証**: `Test-AHFParity.ps1`で確認

#### データ復旧
- **バックアップ**: `_backup_migration\`から復元
- **部分復旧**: 個別ファイルの手動修正
- **完全再構築**: 新フレームワークで再作成

---

**最終更新**: 2024-12-19  
**移行責任者**: AHF Core Team  
**ステータス**: 移行ガイド完成
