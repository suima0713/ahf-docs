# S3-Axis-Fixed 軸ルール準拠システム

## 概要

**①②③の軸ルールに完全準拠**したS3システムです。Ro40は②のみ、③は"ピア×逆DCFの体温計だけ"に統一し、マトリクスの"箱"を厳守します。

## 軸ルール（完全準拠）

### ①長期EV確度
- **代表KPI**: 流動性○（ATM完了）／前受0継続／運転資本は重い
- **現状スナップ**: 流動性○（ATM完了）／前受0継続／運転資本は重い
- **★/5**: 3
- **確信度**: 0.72
- **市場織込み**: 部分織込み
- **Alpha不透明度**: 中
- **上向/下向**: 60 / 40

### ②長期EV勾配
- **代表KPI**: NES計算（Ro40はここにのみ影響）
- **現状スナップ**: NES計算：q/q=17.48%、改定%/受注%=0、Margin=0、Health（Ro40≥40）=+1 ⇒ NES=9.74→★5
- **★/5**: 5
- **確信度**: 0.80
- **市場織込み**: 一部未織込み
- **Alpha不透明度**: 中
- **上向/下向**: 70 / 30

### ③バリュエーション＋認知ギャップ
- **代表KPI**: 体温計（ピア×逆DCFのみ）
- **現状スナップ**: P（PM）＝n/a（ピアEV/S中央値 未確定）／R（rDCF）＝n/a（g_fwd・OPM_fwd・FCF率 未確定）／色= n/a
- **★/5**: n/a
- **確信度**: 0.55
- **市場織込み**: 過少評価の可能性
- **Alpha不透明度**: 中
- **上向/下向**: 65 / 35

## 軸ルール（完全準拠）

### ②長期EV勾配（Ro40はここにのみ影響）

**NES式（常設）**
```
NES = 0.5·q/q + 0.3·改定% + 0.2·受注% + Margin_term + Health_term(Ro40)
```

**Margin_term条件**
- 改善≥+50bps=+1
- ±50bps=0
- 悪化≤−50bps=−1

**Health_term条件（Ro40）**
- Ro40≥40→+1
- 30–40→0
- <30→−1

### ③バリュエーション＋認知ギャップ（体温計：ピア×逆DCFのみ）

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
# ②長期EV勾配（NES計算、Ro40はここにのみ影響）
.\Start-S3AxisFixed.ps1 -Action axis2 -QQPct 17.48 -GuidanceRevisionPct 0 -OrderBacklogPct 0 -MarginChangeBps 0 -Ro40 45.0

# ③バリュエーション＋認知ギャップ（体温計：ピア×逆DCFのみ）
.\Start-S3AxisFixed.ps1 -Action axis3 -EvSActual 5.0 -EvSPeerMedian 5.0 -EvSFair 5.0

# data_gap表示（不足はn/aで可視化）
.\Start-S3AxisFixed.ps1 -Action data_gap

# 軸統合要約
.\Start-S3AxisFixed.ps1 -Action summary
```

### Python直接実行

```python
from s3_axis_fixed import S3AxisFixed

s3 = S3AxisFixed()

# ②長期EV勾配の計算
axis2_display = s3.get_axis2_display(17.48, 0, 0, 0, 45.0)
print(axis2_display)

# ③バリュエーション＋認知ギャップの計算
axis3_display = s3.get_axis3_display(5.0, 5.0, 5.0)
print(axis3_display)

# data_gap表示
data_gap_display = s3.get_data_gap_display("n/a", "n/a", "n/a")
print(data_gap_display)
```

## ファイル構成

```
ahf/_scripts/
├── s3_axis_fixed.py        # ①②③軸ルール準拠システム
├── Start-S3AxisFixed.ps1   # PowerShellランチャー
└── README_S3_Axis_Fixed.md # このファイル
```

## 運用メモ

### 軸ルール（完全準拠）

1. **Ro40は②のみ**: 健全性／レバレッジの素地＝Health_term
2. **③は体温計**: ピアEV/Sと逆DCFフェアEV/Sだけで色を機械決定（PとRの2温度計）
3. **不足はn/aで可視化**: data_gapに残す（恣意で埋めない）

### data_gap（最小）

- **ピアEV/S中央値（光学/トランシーバ）**: n/a（TTL 7d）
- **逆DCFライト入力（g_fwd, OPM_fwd, FCF率）**: n/a（TTL 7d）
- **Price-Mode出典の定点化**: EV/株価の最新日付更新（次回更新時に併記）

### 是正ポイント（約束）

- **Ro40は②のみ**（③には一切持ち込まない）
- **③は体温計**：ピアEV/Sと逆DCFフェアEV/Sだけで色を機械決定（PとRの2温度計）
- **不足はn/aで可視化**し、data_gapに残す（恣意で埋めない）

## 注意事項

- 全ての説明は日本語で行う
- カーソルルールは常時遵守
- 変更時は必ずこのファイルを更新
- 新しいルール追加時はChair承認必須
- **マトリクスの"箱"を厳守**して評価を更新
