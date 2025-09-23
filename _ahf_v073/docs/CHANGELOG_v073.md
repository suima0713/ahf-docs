# AHF v0.7.3 変更履歴

## v0.7.3 (2024-12-15)

### 🎯 主要機能追加
- **固定3軸評価システム実装**
  - ①長期EV確度（LEC）: `g_fwd + ΔOPM_fwd − Dilution − Capex_intensity`
  - ②長期EV勾配（NES）: `0.5·(次Q q/q%) + 0.3·(ガイド改定%) + 0.2·(受注/Backlog増勢%) + Margin_term`
  - ③バリュエーション＋認知ギャップ（VRG）: EV/S(Fwd) × Rule of 40

- **Turbo Screen機能追加**
  - 受付閾値: P≥60、TTL≤14日
  - ★調整: ±2★まで
  - 確信度ブースト: ±10pp
  - 数理ガード緩和適用

- **AnchorLint v1実装**
  - 逐語≤25語チェック
  - #:~:text=必須（SEC文書）
  - anchor_backup対応（PDF等）
  - デュアルアンカーステータス管理

- **MVP-4+出力スキーマ実装**
  - 定型テーブル出力
  - 方向確率計算
  - 自動チェック機能
  - 割り込み処理

### 🔧 技術的改善
- **統合実行スクリプト作成**
  - 全コンポーネント統合
  - A/B/C.yaml自動更新
  - facts.md/triage.json更新

- **PowerShellラッパー作成**
  - エラーハンドリング
  - ファイル存在確認
  - 詳細ログ出力

- **専用ディレクトリ構造整理**
  - `_ahf_v073/scripts/`: v0.7.3専用スクリプト
  - `_ahf_v073/templates/`: v0.7.3専用テンプレート
  - `_ahf_v073/docs/`: v0.7.3専用ドキュメント
  - `_ahf_v073/examples/`: 使用例

### 📋 テンプレート更新
- **A_v073.yaml**: 固定3軸材料テンプレート
- **B_v073.yaml**: 意思決定・評価結果テンプレート
- **C_v073.yaml**: 反証テストテンプレート
- **facts_v073.md**: T1事実テンプレート（逐語≤25語）
- **triage_v073.json**: 事実管理テンプレート（Edge事実対応）

### 🧪 テスト機能
- **test_ahf_v073.py**: 包括的テストスイート
  - 固定3軸評価エンジンテスト
  - Turbo Screen機能テスト
  - AnchorLint v1テスト
  - MVP-4+出力スキーマテスト
  - 統合実行テスト

### 📚 ドキュメント
- **README_v073.md**: v0.7.3専用ドキュメント
- **CHANGELOG_v073.md**: 変更履歴
- **使用例**: サンプル出力と実行例

### 🔄 意思決定ロジック
```
正規化：s1=①★/5、s2=②★/5
合成：DI = (0.6·s2 + 0.4·s1) · Vmult
アクション：GO ≥0.55｜WATCH 0.32–0.55｜NO-GO <0.32
位置サイズ目安：Size% ≈ 1.2% × DI
```

### 🎨 バリュエーション色分け
- **Green**: EV/S≤10× かつ Ro40≥40
- **Amber**: 10–14× または 35–40
- **Red**: >14× または <35

### 🚀 使用方法
```powershell
# 基本実行
.\_ahf_v073\scripts\Start-AHFv073Evaluation.ps1 -Ticker WOLF

# 詳細出力
.\_ahf_v073\scripts\Start-AHFv073Evaluation.ps1 -Ticker WOLF -Verbose

# テスト実行
python _ahf_v073\scripts\test_ahf_v073.py
```

### 📊 出力例
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

### 🔧 設定要件
- Python 3.7+
- PyYAML
- PowerShell 5.1+
- UTF-8エンコーディング

### 📁 生成ファイル
- `ahf_v073_output.json`: 完全な評価結果
- `A.yaml`: 材料（3軸のT1事実）
- `B.yaml`: 結論（意思決定・KPI×2）
- `C.yaml`: 反証（固定3テスト）
- `facts.md`: T1事実（逐語≤25語）
- `triage.json`: 事実管理（CONFIRMED/UNCERTAIN/EDGE_FACTS）

### 🎯 次のステップ
1. 結果を確認: `Get-Content "tickers\WOLF\current\ahf_v073_output.json" | ConvertFrom-Json`
2. スナップショット作成: `New-AHFSnapshot -Ticker WOLF`
3. レッドライン適用: `python ahf_apply_redlines.py "tickers\WOLF\current\forensic.json"`

---

## 前バージョンからの変更点

### v0.7.2 → v0.7.3
- 固定3軸に名称統一：①長期EV確度／②長期EV勾配／③バリュ＋認知ギャップ
- Purpose/MVPの2行ヘッダを必須化
- Turbo Screen を正式導入
- VRGの運用を明確化：色はEV/S×Ro40で機械決定
- 既存のT1厳格運用・AnchorLint・V-Overlayヒステリシスは継承

### 破壊的変更
- ディレクトリ構造の変更（`_ahf_v073/`専用ディレクトリ）
- テンプレートファイル名の変更（`_v073`サフィックス）
- スクリプトパスの変更（`_ahf_v073/scripts/`）

### 互換性
- 既存のAHFプロジェクトとの互換性は維持
- レガシー機能は`_scripts/`に残存
- 段階的移行をサポート
