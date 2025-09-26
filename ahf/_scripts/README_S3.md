# S3 (Stage-3) 投資判断直結システム

## 概要

Stage-3を投資判断に直結させるための最小実装システムです。T1逐語ベースの仮説検証とNES自動計算により、短く作る→確かに叩く→星/DIにブレなく反映を実現します。

## コンポーネント

### 1. S3-MinSpec v1.0（固定ルール）

**RUN条件（全部満たす）**
- T1逐語 ≤25語 + #:~:text=（PDFは anchor_backup{pageno,quote,hash} 可）
- テスト1本（Pass/Failを四則で判定できる式を1行で明記）
- 推論1段以内（事実→含意×1）
- 差戻し（DEFER/REWRITE）

**カード書式（固定）**
```
ID｜仮説≤60字｜根拠逐語(≤25語+anchor)｜テスト式(=…)| TTL｜評価: VALID/MIXED/WEAK/CONTRA
付記: ①②③への影響(±1★内), α_base(−0.15〜+0.15)
```

**反映規律**
- 星調整：各軸±1★内／DI反映は合否確定後
- 半透明α（SoftOverlay）：RUNのみ、合算**±0.08上限**（可逆）

### 2. S3-Lint（軽量版）

**最小5チェック**
- L1: 逐語が≤25語か
- L2: URLが#:~:text=付きか（PDFは anchor_backup 併記）
- L3: テスト式が1行で四則のみか（+ - × ÷ % ≤ ≥ =）
- L4: TTLが入っているか（7–90d）
- L5: 推論段数≤1（"だから→"が一回まで）

**エラー表示例**
```
Lint FAIL: L2(anchor missing #:) / L3(test formula absent)
PASS時は Lint PASS をカード末尾に記載
```

### 3. NES自動欄（常設）

**式（毎回表示）**
```
NES = 0.5·(次Q q/q%) + 0.3·(ガイド改定%) + 0.2·(受注/Backlog増勢%) + Margin_term
Margin_term: 改善≥+50bps=+1／±50bps=0／悪化≤−50bps=−1
```

**★換算（固定）**
- NES ≥ +8 → ★5
- +5–8 → ★4
- +2–5 → ★3
- 0–2 → ★2
- <0 → ★1

## 使用方法

### 基本フロー

1. **カード作成** → **S3-Lint**（PASSならRUN登録、CONTRAのみ差戻し）
2. **NES欄は常に表示**（式・入力・結果・★）
3. **DI反映**：テスト合否が出たカードのみ（半透明αは±0.08上限で暫定、Failで即反転）

### PowerShell実行例

```powershell
# カード作成
.\Start-S3Integrated.ps1 -Action create -CardId "TEST001" -Hypothesis "Q3売上成長率が17%を超える" -Evidence "ガイダンス中点$121M、直前Q$103Mだから→q/q%=17.48% #:~:text=Revenue" -TestFormula "q_q_pct >= 17" -TTLDays 30 -QQPct 17.48

# カード処理
.\Start-S3Integrated.ps1 -Action process -CardId "TEST001"

# NES計算表示
.\Start-S3Integrated.ps1 -Action nes -QQPct 17.48 -GuidanceRevisionPct 0 -OrderBacklogPct 0 -MarginChangeBps 0

# ワークフロー状況
.\Start-S3Integrated.ps1 -Action status
```

### Python直接実行

```python
from s3_integrated import S3Integrated

s3 = S3Integrated()

# カード作成
card = s3.create_card(
    card_id="TEST001",
    hypothesis="Q3売上成長率が17%を超える",
    evidence="ガイダンス中点$121M、直前Q$103Mだから→q/q%=17.48% #:~:text=Revenue",
    test_formula="q_q_pct >= 17",
    ttl_days=30,
    q_q_pct=17.48
)

# カード処理
result = s3.process_card_workflow(card)
print(f"結果: {result['status']}")

# NES表示
nes_display = s3.get_nes_display(17.48, 0, 0, 0)
print(nes_display)
```

## ファイル構成

```
ahf/_scripts/
├── s3_minspec.py          # S3-MinSpec v1.0実装
├── s3_lint.py             # S3-Lint軽量版実装
├── nes_auto.py            # NES自動欄実装
├── s3_workflow.py         # S3-Workflow実装
├── s3_integrated.py       # S3統合システム
├── Start-S3Integrated.ps1 # PowerShellランチャー
└── README_S3.md          # このファイル
```

## 運用メモ

### 正規化プロセス

1. **T1逐語ベース**：25語以内の証拠文
2. **アンカー必須**：#:~:text=またはanchor_backup
3. **四則演算のみ**：テスト式は1行で四則演算のみ
4. **推論1段以内**：「だから→」が一回まで
5. **TTL管理**：7-90日の有効期限

### 品質管理

- **Lint必須**：全カードはS3-Lint通過必須
- **CONTRA判定**：T1同士の明白な矛盾のみ差戻し
- **NES常設**：式・入力・結果・★を常に表示
- **SoftOverlay**：±0.08上限で可逆調整

### 投資判定への反映

- **星調整**：各軸±1★内
- **DI反映**：テスト合否確定後
- **半透明α**：RUNのみ、合算±0.08上限

## 注意事項

- 全ての説明は日本語で行う
- カーソルルールは常時遵守
- 変更時は必ずこのファイルを更新
- 新しいルール追加時はChair承認必須
