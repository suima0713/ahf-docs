# S3-Contract v1.0（過実装なし）

## 概要

**運用"契約" v1.0（過実装なし）**の最終実装です。軸名固定・T1厳守・②の式固定・③の二段・Lintで止めるを完全準拠します。

## 了解した原理（要点3つ）

### ②（勾配）：Ro40＝"健全性/レバレッジが利く素地"
- NES式のHealth項としてだけ反映
- ②でのみ使用可（①③へ持ち込まない）

### ③（体温計）：二段構えのみ
- **Step-1**：フェアバリュー差＝EV/S_actual と ピアEV/S中央値・逆DCFフェアEV/Sの比較→**Disc%**で色決定（Vmult）
- **Step-2**：その割安/割高は妥当か？＝期待成長Δgと認知フラグ（T1逐語）でVerdictを付ける

### ほかは入れない
- ③にRo40/GM/OPMなどは持ち込まない（②のみ）

## 運用"契約" v1.0（過実装なし）

### 軸名固定
- ①長期EV確度
- ②長期EV勾配
- ③バリュエーション＋認知ギャップ

### T1厳守
- 逐語≤25語＋#:~:text=
- 欠測はn/a（推測で埋めない）

### ②の式（変更不可）
```
NES = 0.5·q/q + 0.3·改定% + 0.2·受注% + Margin_term + Health_term(Ro40)
```

### ③の二段
- **Step-1**：EV/S_fair_base = max(ピア中央値, rDCF帯) → Disc% → 色/Vmult決定
- **Step-2**：Δg と 認知フラグ(+/−) で Verdict（色は変えない）

### Lintで止める
- ③にRo40が出たらFAIL
- Step-1/2以外の項目が混入してもFAIL

## 使用方法

### PowerShell実行例

```powershell
# ①長期EV確度
.\Start-S3ContractV1.ps1 -Action axis1 -Axis1Evidence "completed the ATM… ~$98M #:~:text=completed%20the%20ATM" -Axis1Score 3 -Axis1Confidence 0.72

# ②長期EV勾配（NES）
.\Start-S3ContractV1.ps1 -Action axis2 -QQPct 17.48 -GuidanceRevisionPct 0 -OrderBacklogPct 0 -MarginChangeBps 0 -Ro40 45.0

# ③バリュエーション＋認知ギャップ（Two-Step）
.\Start-S3ContractV1.ps1 -Action axis3 -EvSActual 5.0 -EvSPeerMedian 5.0 -GFwd 15.0 -OPMFwd 5.0 -GPeerMedian 12.0 -Axis3Evidence "raises guidance, began volume shipments #:~:text=raises%20guidance"

# Lintで止める
.\Start-S3ContractV1.ps1 -Action lint

# 運用契約 v1.0の要約
.\Start-S3ContractV1.ps1 -Action summary
```

### Python直接実行

```python
from s3_contract_v1 import S3ContractV1

s3 = S3ContractV1()

# ①長期EV確度
axis1_display = s3.get_axis1_display(
    "completed the ATM… ~$98M #:~:text=completed%20the%20ATM",
    3, 0.72
)
print(axis1_display)

# ②長期EV勾配（NES）
axis2_display = s3.get_axis2_display(17.48, 0, 0, 0, 45.0)
print(axis2_display)

# ③バリュエーション＋認知ギャップ（Two-Step）
axis3_display = s3.get_axis3_display(5.0, 5.0, 15.0, 5.0, 12.0, 
                                    "raises guidance, began volume shipments #:~:text=raises%20guidance")
print(axis3_display)
```

## ファイル構成

```
ahf/_scripts/
├── s3_contract_v1.py        # S3-Contract v1.0実装
├── Start-S3ContractV1.ps1   # PowerShellランチャー
└── README_S3_Contract_V1.md # このファイル
```

## 注意事項

- 全ての説明は日本語で行う
- カーソルルールは常時遵守
- 変更時は必ずこのファイルを更新
- 新しいルール追加時はChair承認必須
- **運用"契約" v1.0（過実装なし）に完全準拠**
- **次回の出力は、この契約どおりの超シンプル版マトリクスで更新**
