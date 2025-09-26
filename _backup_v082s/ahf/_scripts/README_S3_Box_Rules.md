# S3-Box Rules v1.0（最小・強制）

## 概要

**"箱（①②③）"に完全準拠**するための最小ルールだけを固定します。過実装は排除し、守るべきことだけを書きます。

## 共通（全軸）

### T1限定
- **SEC/IRのみ**：逐語≤25語＋#:~:text=必須（PDFは anchor_backup{pageno,quote,hash}）
- **欠測は n/a と明示**（埋めない）
- **定型テーブルの見出し名は厳守**：①長期EV確度／②長期EV勾配／③バリュエーション＋認知ギャップ

## ①長期EV確度（LEC）

### 使ってよい要素
- 流動性・負債・希薄化・CapEx・運転資本回転・大型契約の有無（すべてT1）
- **価格やマルチプル、Ro40は使わない**

### スコアリング
- スコアは★/5に丸め
- 根拠はT1逐語のみ

## ②長期EV勾配（NES）

### 唯一の式（固定）
```
NES = 0.5·q/q + 0.3·改定% + 0.2·受注% + Margin_term + Health_term
```

### 条件
- **Margin_term**：GM改善≥+50bps=+1／±50bps=0／悪化≤−50bps=−1
- **Health_term（Ro40）**：Ro40 = 成長% + GAAP OPM% をT1で算出し、
  - Ro40≥40→+1／30–40→0／<30→−1

### 制約
- **Ro40は②でのみ使用可**（①③へ持ち込まない）

### ★換算
- NES≥8→★5
- +5–8→★4
- +2–5→★3
- 0–2→★2
- <0→★1

## ③バリュエーション＋認知ギャップ（体温計のみ）

### 使ってよい要素は2つだけ（どちらも必須がベター／欠けたらn/a）

#### ピアEV/S（Peer Multiple, PM）
```
P = EV/S_actual ÷ EV/S_peer_median − 1
```

#### 逆DCFライト（rDCF）
```
R = EV/S_actual ÷ EV/S_fair − 1
```

### フェアEV/S計算（簡易3帯）
- **EV/S_fair = 10**×（g_fwd≥25% かつ OPM_fwd≥0%）
- **EV/S_fair = 8**×（いずれか中間：10–25% or −5〜0%）
- **EV/S_fair = 6**×（g_fwd<10% or OPM_fwd≤−5%）

### 制約
- **Ro40は使用禁止**（③では一切使わない）
- g_fwd, OPM_fwd はT1、EV/S_actual・ピア中央値はPrice-Mode可（日付・出典名を必ず併記）

### 色の決め方（機械）
- **Green**：|P|≤10% かつ |R|≤15%
- **Amber**：それ以外で、どちらかが±25%以内
- **Red**：P>+25% または R>+25%（割高）／P<−25% 且つ R<−25%（割安だが成長裏付け不足）

### DI倍率（変更不可）
- Green: 1.05
- Amber: 0.90
- Red: 0.75

## S3-Lint（強制チェック｜不足なら出力停止）

### チェック項目
- **L1**: 逐語≤25語
- **L2**: #:~:text=付き（PDFは anchor_backup）
- **L3**: ②の式に余計な項目が無い
- **L4**: Ro40は②のみ（①③内に出現したらFAIL）
- **L5**: ③はPMとrDCFのみ（他指標が混入したらFAIL）
- **L6**: Price-Mode使用時は日付＋出典名明記
- **L7**: 欠測はn/a表記

## 実行順（最小オペレーション）

1. **①②③のカード作成** → **S3-Lint**（FAILなら即修正。通ればRUN）
2. **②のNESを計算・★確定**（Ro40はここだけ）
3. **③のP/Rを計算し色決定・DI倍率適用**
4. **欠測はn/a＋data_gap**（TTL付与、埋めない）

## 禁止事項（違反＝出力停止）

- **③にRo40／GM／OPM／成長など体温計以外を入れること**
- **②以外でRo40を使うこと**
- **欠測を推測で埋めること**（n/a厳守）

## 使用方法

### PowerShell実行例

```powershell
# ①長期EV確度（LEC）
.\Start-S3BoxRules.ps1 -Action axis1 -Axis1Evidence "completed the ATM… ~$98M #:~:text=completed%20the%20ATM" -Axis1Score 3 -Axis1Confidence 0.72

# ②長期EV勾配（NES）
.\Start-S3BoxRules.ps1 -Action axis2 -QQPct 17.48 -GuidanceRevisionPct 0 -OrderBacklogPct 0 -MarginChangeBps 0 -Ro40 45.0

# ③バリュエーション＋認知ギャップ（体温計のみ）
.\Start-S3BoxRules.ps1 -Action axis3 -EvSActual 5.0 -EvSPeerMedian 5.0 -GFwd 15.0 -OPMFwd 5.0

# S3-Lint（強制チェック）
.\Start-S3BoxRules.ps1 -Action lint

# data_gap表示
.\Start-S3BoxRules.ps1 -Action data_gap
```

### Python直接実行

```python
from s3_box_rules import S3BoxRules

s3 = S3BoxRules()

# ①長期EV確度（LEC）
axis1_display = s3.get_axis1_display(
    "completed the ATM… ~$98M #:~:text=completed%20the%20ATM",
    3, 0.72
)
print(axis1_display)

# ②長期EV勾配（NES）
axis2_display = s3.get_axis2_display(17.48, 0, 0, 0, 45.0)
print(axis2_display)

# ③バリュエーション＋認知ギャップ（体温計のみ）
axis3_display = s3.get_axis3_display(5.0, 5.0, 15.0, 5.0)
print(axis3_display)
```

## ファイル構成

```
ahf/_scripts/
├── s3_box_rules.py        # S3-Box Rules v1.0実装
├── Start-S3BoxRules.ps1   # PowerShellランチャー
└── README_S3_Box_Rules.md # このファイル
```

## 注意事項

- 全ての説明は日本語で行う
- カーソルルールは常時遵守
- 変更時は必ずこのファイルを更新
- 新しいルール追加時はChair承認必須
- **"箱（①②③）"のルールに完全準拠**（過実装排除、守るべきことだけを固定）
