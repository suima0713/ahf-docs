# S3-Enhanced 拡張システム

## 概要

Stage-3投資判断直結システムの拡張版です。NES+Health_term（Ro40）と③バリュエーション＋認知ギャップの機械判定を統合したシステムです。

## 拡張機能

### 1. NES+Health_term（Ro40）

**拡張式**
```
NES = 0.5·(次Q q/q%) + 0.3·(ガイド改定%) + 0.2·(受注/Backlog増勢%) + Margin_term + Health_term
```

**Health_term条件（Ro40）**
- Ro40≥40→+1
- 30–40→0
- <30→−1

**Margin_term条件**
- 改善≥+50bps=+1
- ±50bps=0
- 悪化≤−50bps=−1

### 2. ③バリュエーション＋認知ギャップ

**色判定（機械）**
- **Green**: |P|≤10% かつ |R|≤15%
- **Amber**: それ以外でどちらかが±25%以内
- **Red**: P>+25% または R>+25%（割高）、もしくは P<−25% & R<−25%（割安だが成長裏付け不足）

**DI倍率**
- Green: 1.05
- Amber: 0.90
- Red: 0.75

**認知ギャップ**
- Δ = P − R（符号だけ記録：＋＝市場割安、−＝割高）

## 使用方法

### PowerShell実行例

```powershell
# 拡張カード作成
.\Start-S3Enhanced.ps1 -Action create -CardId "TEST001" -Hypothesis "Q3売上成長率が17%を超える" -Evidence "ガイダンス中点$121M、直前Q$103Mだから→q/q%=17.48% #:~:text=Revenue" -TestFormula "q_q_pct >= 17" -TTLDays 30 -QQPct 17.48 -Ro40 45.0 -EvSActual 5.0 -EvSPeerMedian 5.0 -EvSFair 5.0

# カード処理
.\Start-S3Enhanced.ps1 -Action process -CardId "TEST001"

# NES計算表示（Health_term含む）
.\Start-S3Enhanced.ps1 -Action nes -QQPct 17.48 -GuidanceRevisionPct 0 -OrderBacklogPct 0 -MarginChangeBps 0 -Ro40 45.0

# バリュエーション計算表示
.\Start-S3Enhanced.ps1 -Action valuation -EvSActual 5.0 -EvSPeerMedian 5.0 -EvSFair 5.0

# ワークフロー状況
.\Start-S3Enhanced.ps1 -Action status
```

### Python直接実行

```python
from s3_enhanced import S3Enhanced

s3 = S3Enhanced()

# 拡張カード作成
card = s3.create_card(
    card_id="TEST001",
    hypothesis="Q3売上成長率が17%を超える",
    evidence="ガイダンス中点$121M、直前Q$103Mだから→q/q%=17.48% #:~:text=Revenue",
    test_formula="q_q_pct >= 17",
    ttl_days=30,
    q_q_pct=17.48,
    ro40=45.0,  # Ro40≥40→+1
    ev_s_actual=5.0,
    ev_s_peer_median=5.0,
    ev_s_fair=5.0
)

# カード処理
result = s3.process_card_workflow(card)
print(f"結果: {result['status']}")

# 拡張表示
enhanced_display = s3.get_enhanced_display(result)
print(enhanced_display)
```

## ファイル構成

```
ahf/_scripts/
├── nes_auto.py              # NES自動欄（Health_term拡張）
├── valuation_system.py      # ③バリュエーション＋認知ギャップ
├── s3_enhanced.py          # S3拡張システム
├── Start-S3Enhanced.ps1    # PowerShellランチャー
└── README_S3_Enhanced.md   # このファイル
```

## 運用メモ

### 拡張NES計算

1. **Health_term追加**: Ro40による補正
2. **②長期EV勾配**: NES（Ro40はここにのみ影響）
3. **レバレッジが効く素地**: Ro40≥40→+1, 30–40→0, <30→−1

### バリュエーション判定

1. **PM（Peer Multiple）**: P = EV/S_actual ÷ EV/S_peer_median − 1
2. **rDCF（逆DCFライト）**: R = EV/S_actual ÷ EV/S_fair − 1
3. **色判定**: 機械的判定（Green/Amber/Red）
4. **DI倍率**: 色別適用（1.05/0.90/0.75）

### 認知ギャップ

- **Δ = P − R**: 符号だけ記録
- **＋**: 市場割安
- **−**: 割高

## 注意事項

- 全ての説明は日本語で行う
- カーソルルールは常時遵守
- 変更時は必ずこのファイルを更新
- 新しいルール追加時はChair承認必須
