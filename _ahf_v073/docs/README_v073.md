# AHF v0.7.3 固定3軸評価システム

## Purpose（本来の目的）
投資判断に直結する固定3軸で評価する。

## MVP（最優先）
①②③の名称と順序を毎回固定／T1で確証（不足はn/a。必要に応じ〔T2/T3〕タグで補助）／定型テーブル＋1行要約で即時出力。

## システム概要

### 固定3軸の定義
1. **①長期EV確度（LEC）**: どの環境でも生き残り、需要と利益を生み続ける確度
2. **②長期EV勾配（NES）**: 12–24ヶ月の伸び"傾き"（短期加速の手応え）
3. **③バリュエーション＋認知ギャップ（VRG）**: 価格×実力の評価

### 意思決定ロジック
```
正規化：s1=①★/5、s2=②★/5
合成：DI = (0.6·s2 + 0.4·s1) · Vmult
アクション：GO ≥0.55｜WATCH 0.32–0.55｜NO-GO <0.32
位置サイズ目安：Size% ≈ 1.2% × DI
```

### Turbo Screen（オーバーレイ）
- **受付閾値**: Edge採用 P≥60（Coreは従来P≥70）。TTL ≤14日
- **★調整幅**: Screen★は±2★まで（Coreは±1★維持）
- **確信度ブースト**: ±10ppを1回（Coreは±5pp）

## ファイル構成

```
_ahf_v073/
├── scripts/                    # v0.7.3専用スクリプト
│   ├── ahf_v073_evaluator.py      # 固定3軸評価エンジン
│   ├── ahf_turbo_screen.py        # Turbo Screen機能
│   ├── ahf_anchor_lint.py         # AnchorLint v1
│   ├── ahf_mvp4_output.py         # MVP-4+出力スキーマ
│   ├── ahf_v073_integrated.py     # 統合実行スクリプト
│   ├── test_ahf_v073.py           # テストスクリプト
│   └── Start-AHFv073Evaluation.ps1 # PowerShellラッパー
├── templates/                  # v0.7.3専用テンプレート
│   ├── A_v073.yaml               # 材料テンプレート
│   ├── B_v073.yaml               # 結論テンプレート
│   ├── C_v073.yaml               # 反証テンプレート
│   ├── facts_v073.md             # T1事実テンプレート
│   └── triage_v073.json          # 事実管理テンプレート
├── docs/                       # ドキュメント
│   └── README_v073.md            # このファイル
└── examples/                   # 使用例
    └── sample_output.json        # サンプル出力
```

## 使用方法

### 1. 基本実行
```powershell
# PowerShell経由（推奨）
.\_ahf_v073\scripts\Start-AHFv073Evaluation.ps1 -Ticker WOLF

# Python直接実行
python _ahf_v073\scripts\ahf_v073_integrated.py WOLF
```

### 2. 詳細オプション
```powershell
# 詳細出力付き
.\_ahf_v073\scripts\Start-AHFv073Evaluation.ps1 -Ticker WOLF -Verbose

# カスタムデータディレクトリ
.\_ahf_v073\scripts\Start-AHFv073Evaluation.ps1 -Ticker WOLF -DataDir "custom_tickers"
```

### 3. 個別コンポーネント実行
```python
# 固定3軸評価のみ
from _ahf_v073.scripts.ahf_v073_evaluator import AHFv073Evaluator
evaluator = AHFv073Evaluator()
evaluator.load_t1_data("facts.md", "triage.json")
lec_score = evaluator.evaluate_axis_lec()
nes_score = evaluator.evaluate_axis_nes()
vrg_score = evaluator.evaluate_axis_vrg()

# Turbo Screen適用
from _ahf_v073.scripts.ahf_turbo_screen import TurboScreenEngine
turbo_engine = TurboScreenEngine()
turbo_engine.load_edge_data("backlog.md", "triage.json")
eligible_facts = turbo_engine.filter_eligible_edge_facts()

# AnchorLint実行
from _ahf_v073.scripts.ahf_anchor_lint import AnchorLintEngine
lint_engine = AnchorLintEngine()
results = lint_engine.batch_lint_facts(t1_facts)
```

## 入力データ要件

### 必須ファイル
- `tickers/<TICKER>/current/facts.md`: T1事実
- `tickers/<TICKER>/current/triage.json`: 事実管理

### オプションファイル
- `tickers/<TICKER>/current/backlog.md`: Edge事実
- `tickers/<TICKER>/current/A.yaml`: 材料
- `tickers/<TICKER>/current/B.yaml`: 結論
- `tickers/<TICKER>/current/C.yaml`: 反証

## 出力形式

### MVP-4+出力スキーマ
```json
{
  "purpose": "投資判断に直結する固定3軸で評価する",
  "mvp": "①②③の名称と順序を毎回固定／T1で確証／定型テーブル＋1行要約で即時出力",
  "evaluation_date": "2024-12-15",
  "ticker": "WOLF",
  "axes": [
    {
      "axis_name": "①長期EV確度",
      "score": 4,
      "confidence": 80,
      "market_embedded": true,
      "alpha_opacity": 0.3,
      "direction_up_pct": 70.0,
      "direction_down_pct": 30.0,
      "representative_kpi": "guidance_fy26_mid",
      "t1_evidence": "FY26 revenue guidance midpoint $2.5B",
      "current_snapshot": "2500USD_millions"
    }
  ],
  "decision": {
    "decision_type": "WATCH",
    "size_pct": 0.5,
    "di_score": 0.45,
    "reason": "DI=0.45, LEC=4/5, NES=3/5, VRG=2/5"
  },
  "valuation_overlay": {
    "status": "Amber",
    "ev_sales_fwd": 12.5,
    "rule_of_40": 35.0,
    "di_multiplier": 0.90
  }
}
```

### 定型テーブル出力
```
=== AHF v0.7.3 固定3軸評価結果 ===
Purpose: 投資判断に直結する固定3軸で評価する
MVP: ①②③の名称と順序を毎回固定／T1で確証／定型テーブル＋1行要約で即時出力

【固定3軸評価】
| 軸 | 代表KPI/根拠(T1) | 現状スナップ | ★/5 | 確信度 | 市場織込み | Alpha不透明度 | 上向/下向(%) |
|---|---|---|---|---|---|---|---|
| ①長期EV確度 | guidance_fy26_mid | 2500USD_millions | 4 | 80% | ○ | 0.3 | 70/30 |
| ②長期EV勾配 | backlog_growth | 15% | 3 | 75% | ○ | 0.4 | 65/35 |
| ③バリュエーション＋認知ギャップ | ev_sales_fwd | 12.5x | 2 | 70% | ○ | 0.2 | 60/40 |

【意思決定】
判定: WATCH (DI=0.45)
サイズ: 0.5%
理由: DI=0.45, LEC=4/5, NES=3/5, VRG=2/5

【バリュエーション】
色: Amber
EV/S(Fwd): 12.5x
Rule of 40: 35
```

## 設定とカスタマイズ

### 環境変数
```powershell
# データソース設定
$env:AHF_DATASOURCE = "auto"  # internal | polygon | auto
$env:AHF_INTERNAL_BASEURL = "https://internal-api.example.com"
$env:AHF_INTERNAL_TOKEN = "your-token"
$env:POLYGON_API_KEY = "your-polygon-key"
```

### 設定ファイル
- `_rules/redlines.yaml`: レッドライン設定
- `_ahf_v073/templates/`: v0.7.3専用テンプレート
- `_catalog/`: カタログデータ

## トラブルシューティング

### よくある問題

1. **Python環境エラー**
   ```powershell
   # Python確認
   python --version
   
   # 必要モジュールインストール
   pip install PyYAML
   ```

2. **ファイル不足エラー**
   ```powershell
   # 必要なディレクトリ作成
   New-Item -ItemType Directory -Path "tickers\WOLF\current" -Force
   
   # プレースホルダーファイル作成
   New-Item -ItemType File -Path "tickers\WOLF\current\facts.md" -Force
   New-Item -ItemType File -Path "tickers\WOLF\current\triage.json" -Force
   ```

3. **AnchorLintエラー**
   - 逐語が25語を超過している
   - アンカー形式が不正（#:~:text=が必要）
   - SEC文書でアンカーバックアップを使用している

### ログとデバッグ
```powershell
# 詳細出力で実行
.\_ahf_v073\scripts\Start-AHFv073Evaluation.ps1 -Ticker WOLF -Verbose

# 出力ファイル確認
Get-Content "tickers\WOLF\current\ahf_v073_output.json" | ConvertFrom-Json
```

## 更新履歴

### v0.7.3 (2024-12-15)
- 固定3軸システム実装
- Turbo Screen機能追加
- AnchorLint v1実装
- MVP-4+出力スキーマ実装
- 統合実行スクリプト作成
- 専用ディレクトリ構造整理

### 主要機能
- ①長期EV確度（LEC）評価
- ②長期EV勾配（NES）評価  
- ③バリュエーション＋認知ギャップ（VRG）評価
- Decision-Wired意思決定ロジック
- Turbo Screenオーバーレイ
- AnchorLint v1厳密化
- 統合PowerShellラッパー

## ライセンス
AHF (Analytic Homeostasis Framework) - カーソルルール v0.3.2準拠
