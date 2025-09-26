# IDCC｜Gap Map（内部用・非公開）

**目的**: 工程C（反証）から抽出されたGap/矛盾を列挙し、T1-DEEP質問に紐づける

| ID | KPI/テーマ | 現状（T1/Lead） | 不足/違和感 | 目的（A/B/C接続） |
|---|---|---|---|---|
| G1 | FY26売上mid | FY25 mid=820m（T1） | FY26 mid不在 | KPI#1の正式Coverage分母 |
| G2 | RPOまたは同等 | 契約固定対価cash due ≈$2.0B（T1）/ defrev≤12M=178.3m（T1） | RPO_totalと≤12M％が未定義 | KPI#1の分子（≤12M） |
| G3 | 契約負債ロール | H1'25開示：opening→recognized=108.5m（T1） | 四半期ロールの表不足 | ブリッジ継続（質） |
| G4 | Buyback/Dividend | 未取得 | 枠・実行額・配当レート | KPI#2（還元の持続力） |
| G5 | OCF/FCF & 定義 | 未取得 | TTM or FY、定義逐語 | KPI#2（原資の質） |
| G6 | 顧客集中 | 未取得 | 10%超（売上/AR） | 収益の偏在リスク |
| G7 | Shares outstanding | 未取得 | "As of … there were … shares" | A/B/Cの分母安定 |
| G8 | HP/Samsungのランレート | Samsung ≈$131m/年（T1）/ HP不明 | HPの固定/動的別・認識タイミング | 収益ミックスの質 |

## T1-DEEP質問への紐づけ

### G1: FY26売上mid
**Mission**: FY26売上midをT1で確定し、KPI#1の正式Coverage分母としてB.yamlに効かせる
**Success**: AUST（as-of／unit／section or table／逐語≤40語／直URL）
**Fallback**: SEC→IRミラー/EX-99.*→Counterparty公式→blocked_source/not_found

### G2: RPOまたは同等
**Mission**: RPO_totalと≤12M％をT1で確定し、KPI#1の分子としてB.yamlに効かせる
**Success**: AUST（as-of／unit／section or table／逐語≤40語／直URL）
**Fallback**: SEC→IRミラー/EX-99.*→Counterparty公式→blocked_source/not_found

### G3: 契約負債ロール
**Mission**: 四半期ロールの表をT1で確定し、ブリッジ継続の質としてA.yamlに効かせる
**Success**: AUST（as-of／unit／section or table／逐語≤40語／直URL）
**Fallback**: SEC→IRミラー/EX-99.*→Counterparty公式→blocked_source/not_found

### G4: Buyback/Dividend
**Mission**: 枠・実行額・配当レートをT1で確定し、KPI#2（還元の持続力）としてB.yamlに効かせる
**Success**: AUST（as-of／unit／section or table／逐語≤40語／直URL）
**Fallback**: SEC→IRミラー/EX-99.*→Counterparty公式→blocked_source/not_found

### G5: OCF/FCF & 定義
**Mission**: TTM or FY、定義逐語をT1で確定し、KPI#2（原資の質）としてB.yamlに効かせる
**Success**: AUST（as-of／unit／section or table／逐語≤40語／直URL）
**Fallback**: SEC→IRミラー/EX-99.*→Counterparty公式→blocked_source/not_found

### G6: 顧客集中
**Mission**: 10%超（売上/AR）をT1で確定し、収益の偏在リスクとしてC.yamlに効かせる
**Success**: AUST（as-of／unit／section or table／逐語≤40語／直URL）
**Fallback**: SEC→IRミラー/EX-99.*→Counterparty公式→blocked_source/not_found

### G7: Shares outstanding
**Mission**: "As of … there were … shares"をT1で確定し、A/B/Cの分母安定として全ファイルに効かせる
**Success**: AUST（as-of／unit／section or table／逐語≤40語／直URL）
**Fallback**: SEC→IRミラー/EX-99.*→Counterparty公式→blocked_source/not_found

### G8: HP/Samsungのランレート
**Mission**: HPの固定/動的別・認識タイミングをT1で確定し、収益ミックスの質としてA.yamlに効かせる
**Success**: AUST（as-of／unit／section or table／逐語≤40語／直URL）
**Fallback**: SEC→IRミラー/EX-99.*→Counterparty公式→blocked_source/not_found
