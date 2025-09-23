# AHF v0.7.3 スクリプト一覧

## 主要スクリプト

### 1. ahf_v073_evaluator.py
**固定3軸評価エンジン**
- ①長期EV確度（LEC）評価
- ②長期EV勾配（NES）評価
- ③バリュエーション＋認知ギャップ（VRG）評価
- Decision-Wired意思決定ロジック

### 2. ahf_turbo_screen.py
**Turbo Screen機能**
- Edge事実の受付閾値管理（P≥60、TTL≤14日）
- ★調整（±2★まで）
- 確信度ブースト（±10pp）
- 数理ガード緩和適用

### 3. ahf_anchor_lint.py
**AnchorLint v1**
- 逐語≤25語チェック
- #:~:text=必須（SEC文書）
- anchor_backup対応（PDF等）
- デュアルアンカーステータス管理

### 4. ahf_mvp4_output.py
**MVP-4+出力スキーマ**
- 定型テーブル出力
- 方向確率計算
- 自動チェック機能
- 割り込み処理

### 5. ahf_v073_integrated.py
**統合実行スクリプト**
- 全コンポーネント統合
- A/B/C.yaml自動更新
- facts.md/triage.json更新
- エラーハンドリング

### 6. Start-AHFv073Evaluation.ps1
**PowerShellラッパー**
- エラーハンドリング
- ファイル存在確認
- 詳細ログ出力
- 環境設定

### 7. test_ahf_v073.py
**テストスクリプト**
- 包括的テストスイート
- 各コンポーネントの動作確認
- 統合テスト
- エラー検出

## 使用方法

### 基本実行
```powershell
# PowerShell経由（推奨）
.\_ahf_v073\scripts\Start-AHFv073Evaluation.ps1 -Ticker WOLF

# Python直接実行
python _ahf_v073\scripts\ahf_v073_integrated.py WOLF
```

### テスト実行
```python
python _ahf_v073\scripts\test_ahf_v073.py
```

### 個別コンポーネント実行
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

## 依存関係

### Python パッケージ
- `json`: 標準ライブラリ
- `yaml`: PyYAML（`pip install PyYAML`）
- `datetime`: 標準ライブラリ
- `typing`: 標準ライブラリ
- `dataclasses`: 標準ライブラリ
- `enum`: 標準ライブラリ
- `re`: 標準ライブラリ
- `urllib.parse`: 標準ライブラリ
- `hashlib`: 標準ライブラリ

### PowerShell 要件
- PowerShell 5.1+
- .NET Framework 4.5+

## エラーハンドリング

### よくあるエラー
1. **Python環境エラー**: Python 3.7+が必要
2. **モジュール不足**: `pip install PyYAML`
3. **ファイル不足**: 必要なディレクトリ・ファイルの作成
4. **権限エラー**: 実行権限の確認

### デバッグ方法
```powershell
# 詳細出力で実行
.\_ahf_v073\scripts\Start-AHFv073Evaluation.ps1 -Ticker WOLF -Verbose

# 出力ファイル確認
Get-Content "tickers\WOLF\current\ahf_v073_output.json" | ConvertFrom-Json
```

## 設定

### 環境変数
```powershell
$env:AHF_DATASOURCE = "auto"
$env:AHF_INTERNAL_BASEURL = "https://internal-api.example.com"
$env:AHF_INTERNAL_TOKEN = "your-token"
$env:POLYGON_API_KEY = "your-polygon-key"
```

### 設定ファイル
- `_ahf_v073/templates/`: v0.7.3専用テンプレート
- `_rules/redlines.yaml`: レッドライン設定
- `_catalog/`: カタログデータ

## 出力ファイル

### 生成されるファイル
- `ahf_v073_output.json`: 完全な評価結果
- `A.yaml`: 材料（3軸のT1事実）
- `B.yaml`: 結論（意思決定・KPI×2）
- `C.yaml`: 反証（固定3テスト）
- `facts.md`: T1事実（逐語≤25語）
- `triage.json`: 事実管理（CONFIRMED/UNCERTAIN/EDGE_FACTS）

### ログファイル
- コンソール出力: リアルタイムログ
- エラーログ: エラー発生時の詳細情報
- デバッグログ: 詳細出力モード時の追加情報
