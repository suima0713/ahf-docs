# AHF v0.8.0 ドキュメント

## 概要

AHF v0.8.0は、投資判断に直結する固定3軸で評価するシステムです。

**Purpose**: 投資判断に直結する固定3軸で評価する  
**MVP**: ①②③の名称と順序を固定／T1で確証（不足は n/a）／定型テーブル＋1行要約を即時出力

## 固定3軸

### ①長期EV確度（LEC: Long-term EV Certainty）
- **目的**: どの環境でも生き残り、需要と利益を生み続ける確度
- **主要入力（T1）**: 流動性・負債・希薄化・CapEx強度・運転資本回転・大型契約・コベナンツ等
- **計算式**: `LEC ≈ g_fwd + ΔOPM_fwd − Dilution − Capex_intensity`
- **星割当**: LEC ≥+20pp→★5／15–20→★4／8–15→★3／3–8→★2／<3→★1

### ②長期EV勾配（NES: Near-term EV Slope）
- **目的**: 12–24ヶ月の伸び"傾き"（短期加速の手応え）
- **計算式**: `NES = 0.5·(次Q q/q%) + 0.3·(ガイド改定%) + 0.2·(受注/Backlog増勢%) + Margin_term + Health_term`
- **星割当**: NES≥+8→★5／+5–8→★4／+2–5→★3／0–2→★2／<0→★1

### ③バリュエーション＋認知ギャップ（VRG: Valuation + Recognition Gap）
- **目的**: 価格（EV/S_actual）に対する"フェア"との差を測り、その差が将来期待や認知で妥当かを注釈
- **Two-Step**:
  - **Step-1**: フェアバリュー差（素点）→ 色/Vmult決定
  - **Step-2**: 適正性チェック（注釈のみ／色は変えない）

## ワークフロー

### Intake → Stage-1 → Stage-2 → Stage-3 → Decision

1. **Intake**: 銘柄候補／T1可用性
2. **Stage-1｜Fast-Screen（Core）**: T1逐語≤25語＋#:~:text=
3. **Stage-2｜Mini-Confirm（α3/α5）**: T1のみでα3/α5確認
4. **Stage-3｜半透明αの最大化**: 固まったT1の地図から違和感→仮説を立て、T1で単一テスト
5. **Decision**: DI = (0.6·s2 + 0.4·s1) · Vmult

## 意思決定

- **正規化**: s1=①★/5、s2=②★/5
- **合成**: DI = (0.6·s2 + 0.4·s1) · Vmult
- **アクション**: GO ≥0.55｜WATCH 0.32–0.55｜NO-GO <0.32
- **サイズ**: Size% ≈ 1.2% × DI

## スクリプト一覧

### コアスクリプト
- `ahf_v080_workflow.py`: ワークフロー実装
- `ahf_v080_evaluator.py`: 評価器実装
- `ahf_v080_turbo_screen.py`: Turbo Screen実装
- `ahf_v080_integrated.py`: 統合評価システム

### バリデーションスクリプト
- `ahf_v080_anchor_lint.py`: AnchorLint v1（逐語≤25語＋#:~:text=必須）
- `ahf_v080_math_guard.py`: 数理ガード（GM乖離≤0.2pp、残差GP≤$8M等）
- `ahf_v080_s3_lint.py`: S3-Lint（Stage-3のLint）

### テスト・実行スクリプト
- `test_ahf_v080.py`: 全テストスイート
- `Start-AHFv080Evaluation.ps1`: PowerShell実行スクリプト

## テンプレート

### v0.8.0対応テンプレート
- `A_v080.yaml`: 材料（固定3軸対応）
- `B_v080.yaml`: 総合判断（Horizon＋ΔIRR＋KPI×2）
- `C_v080.yaml`: 反証（固定3テスト＋Stage-3）
- `facts_v080.md`: T1確定事実（固定3軸タグ対応）
- `triage_v080.json`: トリアージ（固定3軸対応）
- `backlog_v080.md`: E0-UL一元プール（固定3軸対応）

## 使用方法

### 基本実行
```powershell
# 基本評価
.\Start-AHFv080Evaluation.ps1 -Ticker AAPL

# テスト実行
.\Start-AHFv080Evaluation.ps1 -Ticker AAPL -Test

# バリデーション実行
.\Start-AHFv080Evaluation.ps1 -Ticker AAPL -Validation

# Turbo Screen実行
.\Start-AHFv080Evaluation.ps1 -Ticker AAPL -TurboScreen
```

### Python直接実行
```bash
# ワークフロー
python ahf_v080_workflow.py AAPL

# 評価器
python ahf_v080_evaluator.py AAPL

# Turbo Screen
python ahf_v080_turbo_screen.py AAPL

# 統合評価
python ahf_v080_integrated.py AAPL

# テスト
python test_ahf_v080.py
```

### バリデーション
```bash
# AnchorLint
python ahf_v080_anchor_lint.py input.json

# 数理ガード
python ahf_v080_math_guard.py input.json core

# S3-Lint
python ahf_v080_s3_lint.py input.json
```

## 出力形式

### 定型テーブル
| 軸 | 代表KPI/根拠(T1) | 現状スナップ | ★/5 | 確信度 | 市場織込み | Alpha不透明度 | 上向/下向（％） |
|----|------------------|--------------|-----|--------|------------|----------------|-----------------|
| ①LEC | 長期EV確度 | LEC ≈ g_fwd + ΔOPM_fwd − Dilution − Capex_intensity | 3 | 高 | 織込み済み | 低 | +5% |
| ②NES | 長期EV勾配 | NES = 0.5·(次Q q/q%) + 0.3·(ガイド改定%) + 0.2·(受注/Backlog増勢%) + Margin_term + Health_term | 4 | 高 | 織込み済み | 低 | +3% |
| ③VRG | バリュエーション | Green | - | 中 | 未織込み | 高 | +8% |

### 1行要約
`DI=0.45 → WATCH (Size≈0.5%)`

## 制約事項

### ChatOps制約（最優先）
- 非同期禁止・即時回答
- 未了は data_gap + gap_reason を必ず明記
- T1限定：SEC/IRのみ
- 逐語≤25語＋URLアンカー #:~:text= 必須
- 危険は明確拒否＋代替、往復最小
- 不確実は降格保存：triage=UNCERTAIN + TTL 付与で再試行

### 逸脱防止（強制オペ規律）
- 二鍵実行：Key-1=ユーザー明示コマンド、Key-2=S3-Lint PASS
- 粒度：1ターン=1カードRUN
- 二重アンカー待機：SEC×IRで二重化できる項目は PENDING_SECのまま反映禁止
- 価格系隔離：③は PM+rDCFのみ
- 曖昧命令の拒否：例「元通り」「続行」「任せる」→不実行

## 品質管理

### 3分ルール
- 3分経過で代替案提案またはClaudeに相談
- 実用的な「動けばOK」ソリューション重視
- 進捗報告フォーマット：`3分経過：...`

### テスト要件
- 全スクリプトのテスト必須
- バリデーション機能のテスト必須
- テンプレート整合性チェック必須

## 注意事項

- 全ての説明は日本語で行う
- カーソルルールは常時遵守
- 変更時は必ずドキュメントを更新
- 新しいルール追加時はChair承認必須

