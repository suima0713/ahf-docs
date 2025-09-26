# AHF Priority Runbook v0.3.2a 運用カード

## "貼るだけ"運用カード（新ティッカー時）

### Mission
KPI（①量/②質）に直結する一次文言をT1確定し、A/B/Cへ流す。

### Success
AUST（as-of, unit, section/table, ≤40語, 直URL）を満たす逐語。

### Fallback
SEC→IRミラー→相手方公式（同一事実はT1-adj）／不足はUNCERTAINで運用。

## 確度（credence）ルーブリック（最小）

| 確度 | 条件 | 例 |
|------|------|-----|
| 90 | SEC本文 or 公式一次資料に準ずる明示（AUSTの1要素欠け） | SEC 10-K本文 |
| 75 | 複数一次派生（複数トランスクリプト一致・一次と整合） | 複数トランスクリプト |
| 50 | 一次と整合するがソースが二次のみに依存 | アナリストレポート |
| 30 | 未検証の単発ソース／要反証待ち | 単発ニュース |

## マトリクス算定ルール（影レンジの出し方）

### ①右肩上がり（量）のKPI = FYxx "Floor"
- Floor_T1 = sum(T1項目)
- Floor_shadow = Floor_T1 + Σ(UNCERTAIN_i.value × credence_i)
- 表示：実線 = Floor_T1、影帯 = [Floor_T1, Floor_shadow]

### ②傾き（質）= Fixed-fee比率
- 実線：T1比率
- 影：T1比率 ±（UNCERTAIN寄与の方向×credence）

### ④ミスプライス = EV / Floor
- 実線：EV / Floor_T1
- 影：EV / Floor_shadow（帯で表示）

## 優先順位（何を先にT1ロックするか）

1. **KPI直撃**：①量（Floor/RPO行）、②質（固定比率）
2. **定義脚注**：包含/除外の脚注・但し書き
3. **反証に直結**：Subsequent Events／8-K更新
4. **評価直撃**：EVの構成（現金/負債の最新化）

## 受け入れ基準（Doneの定義）

- [ ] triage.json/UNCERTAINにcredence付で当日反映されている
- [ ] A/B/CはT1のみで整合（UNCERTAIN混入なし）
- [ ] マトリクスには影レンジが描出可能（T1とUNCERTAINが分離管理）

## 反証・矛盾の扱い（最小ガード）

- 矛盾はUNCERTAINにcontradiction: trueで両説並列、credenceで重み分け
- T1に矛盾が出たら新T1で上書き＋旧T1はfacts.md末尾に[RETIRED YYYY-MM-DD]注記

