# LUNR分析サマリー（2025-09-19）

## α4 Gate判定（最終）

**判定: Fail（coverage_months = data_gap）**

**理由**: 12M認識比率のT1明示が無い（IRは残高・減少のみ）

**T1根拠**:
- "Backlog $256,909 as of June 30, 2025" (IRリリース)
- "Backlog decreased by $71.4 million" (IRリリース)
- "12M recognition ratio not explicitly disclosed"

**coverage_months計算**: 不可能（RPO_12M%不明）

## α5 Gate判定（確定）

**判定: Green（OpEx規律確認済）**

**計算**: OpEx = Rev × NG-GM - Adj.EBITDA = $50,313k × (-23.5%) - (-$25,368k) = $13,525k

**帯域**: Green（≤$83,000k）

## 総合判定

**判定: 保留**

**理由**: α4 Gate不通過（coverage_months=data_gap）

**KPI状況**:
- coverage_ratio: data_gap（RPO 12M配分不明）
- contract_assets_roll: CA減少75.6%（先行弱）

## 次のステップ

1. **α4 Gate未達**: RPO 12M配分のT1明示が必要
2. **α5 Gate通過**: OpEx規律はGreen確認済
3. **保留継続**: α4 Gate不通過のため投資判定は保留
