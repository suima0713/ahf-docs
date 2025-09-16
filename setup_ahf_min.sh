#!/usr/bin/env bash
set -euo pipefail

# ======== Config (minimal) ========
ROOT="ahf"
DATE=$(date +"%Y-%m-%d")
TICKER=""
MAKE_SNAPSHOT="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    -t|--ticker) TICKER="$2"; shift 2;;
    --snap|--snapshot) MAKE_SNAPSHOT="true"; shift 1;;
    *) echo "Unknown arg: $1"; exit 1;;
  esac
done

# ======== Helpers ========
mk() { mkdir -p "$1"; echo " + dir: $1"; }
write() { # write <path> <content>
  local p="$1"; shift
  printf "%s" "$*" > "$p"
  echo " + file: $p"
}

yaml_escape() { sed "s/'/''/g"; }

# ======== 1) Project skeleton ========
init_project() {
  echo "Initializing AHF v0.3.3 minimal skeleton..."
  mk "$ROOT/_catalog"
  mk "$ROOT/_templates"
  mk "$ROOT/_rules"
  mk "$ROOT/_ingest"
  mk "$ROOT/_scripts"

  # operating_principles.md (v0.3.3 - ChatOps統合版)
  write "$ROOT/_rules/operating_principles.md" "$(cat <<'MD'
# AHF運用原則（v0.3.3 - ChatOps統合版）

## ChatOps制約（最優先）

**非同期禁止／即時回答**：将来実行の約束や所要時間提示は一切しない。重い課題は部分完了でも即返す。

**不要な確認・往復最小化**：曖昧でも安全範囲ならベストエフォートで出力。危険なら明確に拒否＋代替案。

**AUST厳守**：As-of／Unit／Source（節・表ラベル）／逐語≤40語／直URLが揃わなければT1に載せない。

**用語とルールの自動保持**：本指示に沿ったフォーマット・用語を自動継続（ユーザーが毎回指示しなくても維持）。

**出力はMVP**：頼まれていない提案・実装・冗長化をしない（Chair指示時のみポリッシュ）。

## 基本方針
**一次情報（T1）を A/B/C マトリクスに流し、①右肩上がり × ②傾きの質 × ③時間を"一体"で評価。④（カタリスト）は③の文中に〔Time〕注釈で一度だけ**反映。

### 出力
銘柄ごと 1ページ（A=材料／B=結論＆Horizon＆KPI×2／C=反証）

### 優先度
①＞②＞③＞④（④は注釈／外付け係数禁止）

---

## データ方針（Provider Policy）

### Primary
**Internal ETL**（価格・イベント・ファンダのSSoT）

### Fallback
**Polygon**（価格系の欠損補完・スプリット/配当・長期バックフィルのみ）

### モード
```
AHF_DATASOURCE=internal | polygon | auto（推奨：auto＝内部→失敗時にPolygon）
```

### パリティ検証（Internal vs Polygon）
- 日次終値の絶対％差 ≤ 0.50%
- 直近5営業日の累積差 ≤ 1.5%
- スプリット/配当日付一致（±1営業日許容）
- 失格時は昇格しない（保存のみ）

### データソース管理
```
パリティNG または API障害時は内部ETLにフォールバック（情報収集は継続）
```

---

## テンプレート規約

### A.yaml（材料）
```yaml
meta:
  asof: YYYY-MM-DD

core:
  right_shoulder: []     # ①右肩上がり
  slope_quality: []      # ②傾きの質（ROIC−WACC/ROIIC/FCF）
  time_profile: []       # ③時間

time_annotation:         # ④カタリスト（一度だけ）
  delta_t_quarters: 
  delta_g_pct: 
  window_quarters: 
  note: 
```

### B.yaml（結論）
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
  - name: ""
    current: 
    target: 
```

### C.yaml（反証）
```yaml
tests:
  time_off: ""          # 〔Time〕無効化テスト
  delay_plus_0_5Q: ""   # t1+0.5Qテスト
  alignment_sales_pnl: "" # 売上↔GM/CF/在庫の整合
```

### facts.md（逆時系列・原子1行）
```
[YYYY-MM-DD][T1-F|T1-P|T1-C][Core①|Core②|Core③|Time] "逐語" (impact: KPI) <src>
```

**タグ規約**: 証拠=T1-F/T1-P/T1-C｜柱=Core①/②/③｜注釈=Time（④は一度だけ）

### backlog.md（Lead/Uのワンテーブル）
```
| id | class=Lead/U | KPI/主張 | 現在の根拠≤40語 | ソース | T1化に足りないもの | 次アクション | 関連Impact | unavailability_reason | grace_until |
```

### triage.json（HYPOTHESES追加）
```json
{
  "HYPOTHESES": [
    {
      "id": "H1_fy26_floor_reset",
      "status": "pending|confirmed|falsified",
      "what_to_watch": ["Note2_FY26_row_delta_kUSD", "Samsung_include_sentence"],
      "trigger": "FY26_row_qoq_delta_kUSD >= 100000",
      "falsifier": "FY26_row_qoq_delta_kUSD < 50000 AND call_notes='deferred recognition later'",
      "kpi_links": ["fy26_contracted_revenue", "samsung_inclusion_in_rpo"]
    }
  ]
}
```

### impact_cards.json（新カード追加）
```json
[
  {
    "id": "ev_over_floor",
    "inputs": ["ev_usd","floor_low_kUSD","floor_high_kUSD"],
    "expr": "ev_usd/(1000*avg(floor_low_kUSD,floor_high_kUSD))",
    "gates": { "up": "<=10.0", "down": ">=20.0" }
  },
  {
    "id": "disagg_fixed_ratio_2Q",
    "inputs": ["fixed_ratio_q1_pct","fixed_ratio_q2_pct"],
    "expr": "min(fixed_ratio_q1_pct,fixed_ratio_q2_pct)",
    "gates": { "up": ">=90", "down": "<85" }
  }
]
```

---

## 運用ループ（MVP：3ステップ＋レッドライン）

### A｜入口（E0-UL）
Leadを広く収集→backlog.md／triage.json(UNCERTAIN)。T1は並走可。

### B｜まとめる
Horizon（6M/1Y/3Y/5Y）／Go・保留・No-Go／KPI×2（質＋実行）。

### C｜反証
〔Time〕無効／t1+0.5Q／売上↔GM/CF/在庫整合。

### D｜レッドライン
forensic.json→スクリプト実行→B.yaml と facts.md に反映。

→ current/ を上書き → New-AHFSnapshot 実行 → _catalog CSVを手動1行更新（MVP）。

---

## ガードレール（ブレ止め）

### 情報の幅を最大化
④は③の文中の注釈（delta_t_quarters/小さなdelta_g_pct）で適宜記録。

### 判断の出力
Horizon＋KPI×2を含む包括的な出力。

### 入る基準
①②が○ かつ ΔIRR ≥ +300〜500bp（逆DCF比）。情報の幅を重視。

### サイズ
σ（Low/Med/High）で配分のみ調整（見立ては変えない）。

---

## 決定木

### データソース選択
```
Internalが揃う → それだけで運用（Polygonは監査用に裏で回す）
Internalに欠損/遅延 → Polygonでバックフィル → 検証OKなら可視化に使用
パリティNG/不安定 → その銘柄はInternalのみで進行（Polygon保留）
```

### データ品質管理
```
パリティ違反 → データ品質チームに報告
API障害 → フォールバック運用、情報収集継続
```

---

## デュアルAI運用規律（内部）

**Vetting→Persist** の二段構え（内部のみ）

**Vetting**：一次文書の位置特定・抜粋候補（E0-UL含む）
**Persist**：AUST検証→facts.md/triage.jsonへ確定保存

**貼り付けは最小**：ユーザー可視のプロンプト羅列を避け、確定したT1のみ提示。

**衝突時**は AUST不備側をUNCERTAINへ退避し、contradictionタグで管理。

## 成功指標

- **データ品質**: パリティ検証合格率 > 95%
- **システム安定性**: Internal依存度 100%維持
- **開発効率**: チャート・可視化の見栄え向上
- **運用コスト**: Polygon APIコスト < 月額$100
- **ChatOps効率**: 即時回答率 100%、往復回数最小化
MD
)"

  # redlines
  write "$ROOT/_rules/redlines.yaml" "$(cat <<'YAML'
# STOP/HOLD/FLAG minimal rules (v0.3.3)
STOP:
  - key: item_4_02
    desc: "Non-reliance on previously issued financial statements (Item 4.02)"
  - key: item_4_01
    desc: "Change in certifying accountant with disagreements (Item 4.01)"
HOLD:
  - key: item_3_01
    desc: "Nasdaq/NYSE listing deficiency (Item 3.01) or Going Concern"
FLAG:
  - key: arr_bridge_missing
    desc: "ARR disclosed without GAAP/IFRS bridge"
  - key: reverse_split_approved_only
    desc: "Reverse split approved but not effective"
  - key: cap_table_inconsistent
    desc: "Capital activity but basic shares unclear"
YAML
)"

  # scripts (minimal stubs)
  write "$ROOT/_scripts/ahf_apply_redlines.py" "$(cat <<'PY'
#!/usr/bin/env python3
import json, sys, pathlib

def main():
  if len(sys.argv) < 2:
    print("usage: ahf_apply_redlines.py <path/to/forensic.json>")
    sys.exit(0)

  f = pathlib.Path(sys.argv[1])
  if not f.exists():
    print("forensic.json not found; nothing to apply.")
    sys.exit(0)

  data = json.loads(f.read_text())
  # Minimal stub: just echo what would be applied
  print("[redlines] OK - parsed forensic.json")
  for k,v in data.items():
    print(f"  - {k}: {v}")
  print("No destructive edits performed (minimal mode).")

if __name__ == "__main__":
  main()
PY
)"
  chmod +x "$ROOT/_scripts/ahf_apply_redlines.py"

  write "$ROOT/_scripts/New-AHFProject.ps1" "$(cat <<'PS1'
param()
Write-Host "AHF v0.3.3 skeleton is created by bash script in this minimal setup." -ForegroundColor Green
PS1
)"

  write "$ROOT/_scripts/Add-AHFTicker.ps1" "$(cat <<'PS1'
param([Parameter(Mandatory=$true)][string]$Ticker)
Write-Host "Use bash setup_ahf_min.sh -t $Ticker in this minimal setup." -ForegroundColor Yellow
PS1
)"

  write "$ROOT/_scripts/New-AHFSnapshot.ps1" "$(cat <<'PS1'
param([Parameter(Mandatory=$true)][string]$Ticker)
Write-Host "Use bash setup_ahf_min.sh -t $Ticker --snap in this minimal setup." -ForegroundColor Yellow
PS1
)"

  echo "Project skeleton ready."
}

# ======== 2) Ticker scaffold ========
init_ticker() {
  local T="$1"
  echo "Scaffolding ticker: $T"
  local BASE="$ROOT/tickers/$T"
  mk "$BASE/snapshots"
  mk "$BASE/current"
  mk "$BASE/attachments/providers/internal"
  mk "$BASE/attachments/providers/polygon"

  # A.yaml
  write "$BASE/current/A.yaml" "$(cat <<YAML
meta:
  asof: '$DATE'
core:
  right_shoulder: null
  slope_quality: null
  time_profile: null
time_annotation:
  delta_t_quarters: null
  delta_g_pct: null
  window_quarters: null
  note: null
YAML
)"

  # B.yaml
  write "$BASE/current/B.yaml" "$(cat <<YAML
horizon:
  6M: { verdict: null }
  1Y: { verdict: null }
  3Y: { verdict: null }
  5Y: { verdict: null }
delta_irr_bp: null
stance:
  decision: null  # Go | Hold | No-Go
  size: null
  reason: null
kpi_watch:
  - null
  - null
YAML
)"

  # C.yaml
  write "$BASE/current/C.yaml" "$(cat <<YAML
tests:
  time_off: null
  delay_plus_0_5Q: null
  alignment_sales_pnl: null
YAML
)"

  # facts.md（T1のみ）
  write "$BASE/current/facts.md" ""

  # backlog.md（Lead/Uの一元プール）
  write "$BASE/current/backlog.md" "$(cat <<'MD'
| id | class | KPI/主張 | 現在の根拠≤40語 | ソース | T1化に足りないもの | 次アクション | 関連Impact | unavailability_reason | grace_until |
|----|-------|-----------|------------------|--------|----------------------|--------------|-------------|-----------------------|-------------|
MD
)"

  # triage.json（CONFIRMED/UNCERTAIN/HYPOTHESES）
  write "$BASE/current/triage.json" "$(cat <<JSON
{
  "as_of": "$DATE",
  "CONFIRMED": [],
  "UNCERTAIN": [],
  "HYPOTHESES": [
    {
      "id": "H1_fy26_floor_reset",
      "status": "pending",
      "what_to_watch": ["Note2_FY26_row_delta_kUSD", "Samsung_include_sentence"],
      "trigger": "FY26_row_qoq_delta_kUSD >= 100000",
      "falsifier": "FY26_row_qoq_delta_kUSD < 50000 AND call_notes='deferred recognition later'",
      "kpi_links": ["fy26_contracted_revenue", "samsung_inclusion_in_rpo"]
    },
    {
      "id": "H2_fixed_dominance",
      "status": "pending",
      "what_to_watch": ["Note3_fixed_ratio_pct"],
      "trigger": "fixed_ratio_pct >= 90 for 2 consecutive quarters",
      "falsifier": "fixed_ratio_pct < 85 for 2 consecutive quarters",
      "kpi_links": ["rev_fixed_q"]
    },
    {
      "id": "H3_renewals_stepup",
      "status": "pending",
      "what_to_watch": ["each_renewal_line_items"],
      "trigger": ">=2 renewals at flat_to_+10pct",
      "falsifier": ">=2 key renewals down or lapse",
      "kpi_links": ["renewal_map"]
    },
    {
      "id": "H4_ev_over_floor_gap",
      "status": "pending",
      "what_to_watch": ["ev_usd","floor_range_kUSD","ntm_deferred_recognition_kUSD"],
      "trigger": "ev_over_floor_low <= peer_p25",
      "falsifier": "ev_over_floor_high >= peer_p75",
      "kpi_links": ["ev_over_floor"]
    },
    {
      "id": "H5_seasonality_shrinks",
      "status": "pending",
      "what_to_watch": ["call_quote_33m","guidance_mape"],
      "trigger": "33m cadence repeated 2Q & MAPE↓",
      "falsifier": "cadence missing 2Q or MAPE↑",
      "kpi_links": ["samsung_qtr_33m"]
    }
  ]
}
JSON
)"

  # impact_cards.json（v0.3.3拡張）
  write "$BASE/current/impact_cards.json" "$(cat <<'JSON'
[
  {
    "id": "coverage_ratio",
    "inputs": ["RPO_total","RPO_le12m_pct","Guidance_FY26_total_revenue_mid"],
    "expr": "(RPO_total*(RPO_le12m_pct/100))/Guidance_FY26_total_revenue_mid",
    "gates": { "up": ">=0.90", "down": "<0.60" }
  },
  {
    "id": "ev_over_floor",
    "inputs": ["ev_usd","floor_low_kUSD","floor_high_kUSD"],
    "expr": "ev_usd/(1000*avg(floor_low_kUSD,floor_high_kUSD))",
    "gates": { "up": "<=10.0", "down": ">=20.0" }
  },
  {
    "id": "disagg_fixed_ratio_2Q",
    "inputs": ["fixed_ratio_q1_pct","fixed_ratio_q2_pct"],
    "expr": "min(fixed_ratio_q1_pct,fixed_ratio_q2_pct)",
    "gates": { "up": ">=90", "down": "<85" }
  }
]
JSON
)"

  # forensic.json（レッドライン判定の入力入れ物）
  write "$BASE/current/forensic.json" "$(cat <<'JSON'
{
  "items": []
}
JSON
)"
}

# ======== 3) Snapshot ========
make_snapshot() {
  local T="$1"
  local BASE="$ROOT/tickers/$T"
  local SNAP="$BASE/snapshots/$DATE"
  if [[ ! -d "$BASE/current" ]]; then
    echo "No current/ for $T. Run: bash setup_ahf_min.sh -t $T"
    exit 1
  fi
  mk "$SNAP"
  cp "$BASE/current/"* "$SNAP/"
  echo "Snapshot created: $SNAP"
}

# ======== Run ========
init_project
if [[ -n "$TICKER" ]]; then
  init_ticker "$TICKER"
  [[ "$MAKE_SNAPSHOT" == "true" ]] && make_snapshot "$TICKER"
fi

echo "Done."
