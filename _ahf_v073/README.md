# AHF v0.7.3 固定3軸評価システム

## Purpose（本来の目的）
投資判断に直結する固定3軸で評価する。

## MVP（最優先）
①②③の名称と順序を毎回固定／T1で確証（不足はn/a。必要に応じ〔T2/T3〕タグで補助）／定型テーブル＋1行要約で即時出力。

## ディレクトリ構造

```
_ahf_v073/
├── scripts/                    # v0.7.3専用スクリプト
│   ├── ahf_v073_evaluator.py      # 固定3軸評価エンジン
│   ├── ahf_turbo_screen.py        # Turbo Screen機能
│   ├── ahf_anchor_lint.py         # AnchorLint v1
│   ├── ahf_mvp4_output.py         # MVP-4+出力スキーマ
│   ├── ahf_v073_integrated.py     # 統合実行スクリプト
│   ├── test_ahf_v073.py           # テストスクリプト
│   ├── Start-AHFv073Evaluation.ps1 # PowerShellラッパー
│   └── README_v073_scripts.md     # スクリプト説明
├── templates/                  # v0.7.3専用テンプレート
│   ├── A_v073.yaml               # 材料テンプレート
│   ├── B_v073.yaml               # 結論テンプレート
│   ├── C_v073.yaml               # 反証テンプレート
│   ├── facts_v073.md             # T1事実テンプレート
│   └── triage_v073.json          # 事実管理テンプレート
├── docs/                       # ドキュメント
│   ├── README_v073.md            # 詳細ドキュメント
│   └── CHANGELOG_v073.md         # 変更履歴
├── examples/                   # 使用例
│   └── sample_output.json        # サンプル出力
└── README.md                   # このファイル
```

## クイックスタート

### 1. 基本実行
```powershell
# PowerShell経由（推奨）
.\_ahf_v073\scripts\Start-AHFv073Evaluation.ps1 -Ticker WOLF

# Python直接実行
python _ahf_v073\scripts\ahf_v073_integrated.py WOLF
```

### 2. テスト実行
```python
python _ahf_v073\scripts\test_ahf_v073.py
```

### 3. 詳細オプション
```powershell
# 詳細出力付き
.\_ahf_v073\scripts\Start-AHFv073Evaluation.ps1 -Ticker WOLF -Verbose

# カスタムデータディレクトリ
.\_ahf_v073\scripts\Start-AHFv073Evaluation.ps1 -Ticker WOLF -DataDir "custom_tickers"
```

## 固定3軸の定義

### ①長期EV確度（LEC）
どの環境でも生き残り、需要と利益を生み続ける確度
- 成長の土台：通期/中期の売上成長ガイダンス
- 収益性の方向：通期OPM/EBITDAレンジ
- 資本強度：希薄化率（SO増）／CapEx強度
- 実行裏付け：政府/大型契約、実績ケイデンス

### ②長期EV勾配（NES）
12–24ヶ月の伸び"傾き"（短期加速の手応え）
- 次Q q/q％
- 通期ガイド改定率％
- Orders/Backlogの増勢
- マージンドリフト

### ③バリュエーション＋認知ギャップ（VRG）
価格×実力の評価
- EV/S(Fwd) と Rule-of-40
- 色分け：Green/Amber/Red
- 認知ギャップの定量化

## 意思決定ロジック

```
正規化：s1=①★/5、s2=②★/5
合成：DI = (0.6·s2 + 0.4·s1) · Vmult
アクション：GO ≥0.55｜WATCH 0.32–0.55｜NO-GO <0.32
位置サイズ目安：Size% ≈ 1.2% × DI
```

## 出力例

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
```

## 詳細情報

- **詳細ドキュメント**: `docs/README_v073.md`
- **変更履歴**: `docs/CHANGELOG_v073.md`
- **スクリプト説明**: `scripts/README_v073_scripts.md`
- **サンプル出力**: `examples/sample_output.json`

## ライセンス
AHF (Analytic Homeostasis Framework) - カーソルルール v0.3.2準拠
