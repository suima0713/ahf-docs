# AHF v0.8.1-r2 ドキュメント

## 概要

AHF v0.8.1-r2は、投資判断に直結する固定4軸で評価するシステムです。

**Purpose**: 投資判断に直結する固定4軸で評価  
**MVP**: ①②③④の名称と順序を絶対固定／T1 or T1*で確証（不足はn/a）／定型テーブル＋1行要約を即出力

## 固定4軸

### ①長期EV確度（LEC: Long-term EV Certainty）
- **目的**: どの環境でも生き残り、需要と利益を生み続ける確度
- **主要入力（T1/T1*）**: 流動性・負債・希薄化・CapEx強度・運転資本回転・大型契約・コベナンツ等
- **計算式**: `LEC ≈ g_fwd + ΔOPM_fwd − Dilution − Capex_intensity`
- **星割当**: LEC ≥+20pp→★5／15–20→★4／8–15→★3／3–8→★2／<3→★1

### ②長期EV勾配（NES: Near-term EV Slope）
- **目的**: 12–24ヶ月の伸び"傾き"（短期加速の手応え）
- **計算式**: `NES = 0.5·(次Q q/q%) + 0.3·(ガイド改定%) + 0.2·(受注/Backlog増勢%) + Margin_term + Health_term`
- **星割当**: NES≥+8→★5／+5–8→★4／+2–5→★3／0–2→★2／<0→★1

### ③現バリュエーション（機械）（現在のみ／peer基準）
- **目的**: EV/S_actual_TTM と EV/S_peer_median_TTM（同日・同ソース）の乖離を機械判定
- **Two-Step**:
  - **Step-1**: Disc% = (peer_median − actual) / peer_median → 色/Vmult決定
  - **Step-2（注釈のみ）**: Δg = g_fwd − g_peer_median（T1/T1*がある時）＋認知フラグ± → Verdict
- **禁止**: rDCF混入不可／P/S代替不可（Ro40等は②のみ）

### ④将来EVバリュ（総合）（将来のみ）
- **目的**: 12–24Mの想定EVに照らした総合バリュ（①②③＋認知を直交統合）
- **指標**: FD% = (EVS_fair_12m − EVS_actual_today) / EVS_fair_12m
- **EVS_fair_12m**: rDCF帯（10/8/6×）× T1/T1*の g_fwd・OPM_fwd（中点）
- **星割当**: FD%≥+15%→★5／+5〜+15→★4／−5〜+5→★3／−15〜−5→★2／≤−15→★1

## 証拠階層（T1*導入）

### T1: 一次（SEC/IR）
- 唯一の一次確証
- 逐語≤25語＋#:~:text=必須
- PDFは anchor_backup{pageno,quote,hash}

### T1*: Corroborated二次（独立2源以上）
- 独立2源以上／異ドメイン／相互転載でない／T1と非矛盾
- 各源で逐語≤25語＋#:~:text=
- T1と同等に★／DIへ反映可
- 即時降格：のちにT1で矛盾が出れば即T2へ降格
- ttl_days=14でT1確認を追跡

### T2: 二次1源
- 逐語＋URL
- ★変更不可
- 確信度±10pp（1回）／市場織込み（−2/−7）／注釈のみ

## ワークフロー

### Intake → Stage-1 → Stage-2 → Stage-3 → Decision

1. **Intake**: 銘柄候補／T1/T1*可用性
2. **Stage-1｜Fast-Screen（Core）**: T1/T1*逐語≤25語＋#:~:text=
3. **Stage-2｜Mini-Confirm（α3/α5）**: T1/T1*のみでα3/α5確認
4. **Stage-3｜半透明αの最大化**: 固まったT1/T1*の地図から違和感→仮説を立て、T1/T1*で単一テスト
5. **Decision**: DI = (0.6·s2 + 0.4·s1) · Vmult(③)

## 意思決定

- **正規化**: s1=①★/5、s2=②★/5
- **合成**: DI = (0.6·s2 + 0.4·s1) · Vmult(③)
- **アクション**: GO ≥0.55｜WATCH 0.32–0.55｜NO-GO <0.32
- **サイズ**: Size% ≈ 1.2% × DI
- **SoftOverlay**: 合算±0.08（可逆）、T1*由来の加点は±0.03以内、④は表示専用（必要時±0.05のみ補助）

## スクリプト一覧

### コアスクリプト
- `ahf_v081_r2_integrated.py`: 統合評価システム
- `ahf_v081_r2_evaluator.py`: 4軸評価器
- `ahf_v081_r2_workflow.py`: ワークフロー実装
- `ahf_v081_r2_turbo_screen.py`: Turbo Screen実装

### バリデーションスクリプト
- `ahf_v081_r2_anchor_lint.py`: AnchorLint（逐語≤25語＋#:~:text=必須）
- `ahf_v081_r2_math_guard.py`: 数理ガード（GM乖離≤0.2pp、残差GP≤$8M等）
- `ahf_v081_r2_s3_lint.py`: S3-Lint（Stage-3のLint）

### テスト・実行スクリプト
- `test_ahf_v081_r2.py`: 全テストスイート
- `Start-AHFv081R2Evaluation.ps1`: PowerShell実行スクリプト

## テンプレート

### v0.8.1-r2対応テンプレート
- `A_v081_r2.yaml`: 材料（固定4軸対応）
- `B_v081_r2.yaml`: 総合判断（Horizon＋ΔIRR＋KPI×2）
- `C_v081_r2.yaml`: 反証（固定4テスト＋Stage-3）
- `facts_v081_r2.md`: T1/T1*確定事実（固定4軸タグ対応）
- `triage_v081_r2.json`: トリアージ（固定4軸対応）
- `backlog_v081_r2.md`: E0-UL一元プール（固定4軸対応）

## 使用方法

### 基本実行
```powershell
# 基本評価
.\Start-AHFv081R2Evaluation.ps1 -Ticker AAPL

# テスト実行
.\Start-AHFv081R2Evaluation.ps1 -Ticker AAPL -Test

# バリデーション実行
.\Start-AHFv081R2Evaluation.ps1 -Ticker AAPL -Validation

# Turbo Screen実行
.\Start-AHFv081R2Evaluation.ps1 -Ticker AAPL -TurboScreen
```

### Python直接実行
```bash
# 統合評価
python ahf_v081_r2_integrated.py AAPL

# 4軸評価器
python ahf_v081_r2_evaluator.py AAPL

# ワークフロー
python ahf_v081_r2_workflow.py AAPL

# Turbo Screen
python ahf_v081_r2_turbo_screen.py AAPL

# テスト
python test_ahf_v081_r2.py AAPL
```

### バリデーション
```bash
# AnchorLint
python ahf_v081_r2_anchor_lint.py input.json

# 数理ガード
python ahf_v081_r2_math_guard.py input.json core

# S3-Lint
python ahf_v081_r2_s3_lint.py input.json
```

## 出力形式

### 定型テーブル
| 軸 | 代表KPI/根拠(T1/T1*) | 現状スナップ | ★/5 | 確信度 | 市場織込み | Alpha不透明度 | 上向/下向（％） |
|----|----------------------|--------------|-----|--------|------------|----------------|-----------------|
| ①LEC | 長期EV確度 | LEC ≈ g_fwd + ΔOPM_fwd − Dilution − Capex_intensity | 3 | 高 | 織込み済み | 低 | +5% |
| ②NES | 長期EV勾配 | NES = 0.5·(次Q q/q%) + 0.3·(ガイド改定%) + 0.2·(受注/Backlog増勢%) + Margin_term + Health_term | 4 | 高 | 織込み済み | 低 | +3% |
| ③Current_Val | 現バリュエーション | Green | - | 中 | 未織込み | 高 | +8% |
| ④Future_Val | 将来EVバリュ | FD% = (EVS_fair_12m − EVS_actual_today) / EVS_fair_12m | 4 | 中 | 未織込み | 中 | +12% |

### 1行要約
`DI=0.45 → WATCH (Size≈0.5%)`

## 制約事項

### ChatOps制約（最優先）
- 非同期禁止・即時回答
- 未了は data_gap + gap_reason を必ず明記
- T1/T1*限定：SEC/IRのみ
- 逐語≤25語＋URLアンカー #:~:text= 必須
- 危険は明確拒否＋代替、往復最小
- 不確実は降格保存：triage=UNCERTAIN + TTL 付与で再試行

### 逸脱防止（強制オペ規律）
- 二鍵実行：Key-1=ユーザー明示コマンド、Key-2=S3-Lint PASS
- 粒度：1ターン=1カードRUN
- 二重アンカー待機：SEC×IRで二重化できる項目は PENDING_SECのまま反映禁止
- 価格系隔離：③は現在のみ（peer）、④は将来のみ（rDCF×T1/T1*）
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

## CHANGELOG（v0.8.1-c1 → v0.8.1-r2）

### T1*（Corroborated二次）を導入
- ★/DIに反映可、表示タグと即時降格規律を追加
- 独立性テスト、転載判定、TTL運用を実装

### ③＝現在のみ（peer）／④＝将来のみ（rDCF×T1/T1*）を再強化
- Price-Lint／AnchorLint-T1* を追加
- SoftOverlayにT1*上限（±0.03）を設定

### 価格系隔離（厳格）
- ③＝現在のみ：EV/S(TTM) を同日・同一ソースで issuer/peer を取得
- ④＝将来のみ：rDCF帯（10/8/6×）×T1/T1*の g_fwd・OPM_fwdで EVS_fair_12m→FD%
- Price-Mode：as_of=ET終値同日・同一定義（TTM売上）
- Price-Lint：{ev_used:true, ps_used:false, same_day:true, same_source:true} を自検
