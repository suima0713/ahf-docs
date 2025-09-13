# PRISM/VOICE → AHF 移管プレイブック（最小3ステップ）

## 概要
PRISM/VOICEからAHFへの移管は"枠（A/B/C＋facts）に詰め替えるだけ"。最小で速い実務プレイブック。

---

## 移管プレイブック（最小3ステップ）

### 1) レガシーの"原子"を出す（CSV/JSON）

PRISM/VOICEから1行＝1事実のCSVを出してください（手元のフォーマットでOK）。

**理想列:**
```csv
facts_legacy.csv
date,source_type,pillar,verbatim,impact_kpi,url,asof
# source_type: T1-F|T1-P|T1-C
# pillar: Core1|Core2|Core3|Time ← "Time"はカタリスト/イベント
```

**任意で結論系:**
```csv
horizon_legacy.csv
asof,sixM_verdict,oneY_verdict,threeY_verdict,fiveY_verdict,decision,delta_irr_bp,reason

kpi_legacy.csv
asof,kpi1,kpi2
```

### 2) AHF骨組みを用意
```powershell
pwsh .\ahf\_scripts\New-AHFProject.ps1
pwsh .\ahf\_scripts\Add-AHFTicker.ps1 -Ticker <TICKER>
```

### 3) "詰め替え"実行
```powershell
pwsh .\ahf\_scripts\Convert-LegacyToAHF.ps1 -Ticker <TICKER>
```

**変換内容:**
- `facts_legacy.csv` → `facts.md`（逆時系列で1行ずつ）
- `A.yaml`: pillarごとに配列へ格納、Timeは `time_annotation` に一度だけ
- `B.yaml`/`C.yaml`: 既存の結論・KPI・反証を写経（なければ空でOK）
- `snapshots/`: asofごとに過去スナップショットを再構築（任意）
- `attachments/`: PDFや元ファイルは `attachments/providers/internal/` へそのまま移動（URLだけでも可）

---

## ファイル配置

```
tickers/<TICKER>/attachments/legacy/
├── facts_legacy.csv      # 必須
├── horizon_legacy.csv    # 任意
└── kpi_legacy.csv        # 任意
```

---

## 品質チェック（5つだけ）

1. **タグ整合**: T1-F/P/C × Core①/②/③/Time 以外が混ざっていない
2. **Time注釈は1回**: `time_annotation` が最新1件だけを反映
3. **重複排除**: 同趣旨の逐語は最新×強T1のみ
4. **facts.mdは逆時系列**: 検索性を確保
5. **A/B/Cは1ページで読める**: 出力過多にしない（PRISM禁止事項順守）

---

## スナップショット再構築（任意）

過去の `asof` 単位で履歴を再現する場合：

1. `facts_legacy.csv` の `asof` 列でユニーク日付を取得
2. 各日付ごとにその日までの行で A/B/C/facts を再生成
3. `/snapshots/YYYY-MM-DD/` に保存 → `current/` は最新で上書き

（スクリプトを関数化して、`-AsOf` に日付を渡してループすればOK。）

---

## 注記

- **MVPではJSONで保存**（すぐ読めるため）
- **運用上YAMLが良ければ、後段で変換**
- **Time要素は最新1件だけを `time_annotation` に採用**（"一度だけ"原則）
- **PRISM禁止事項順守**: 頼んでいない提案や実装は厳禁
