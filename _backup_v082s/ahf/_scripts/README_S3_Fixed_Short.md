# S3-Fixed-Short - 運用"固定"ショート版（これだけで回します）

## 概要

**運用"固定"ショート版（これだけで回します）**の最終実装です。いま決めた枠組みと基準だけで、細かい条件を足さずに柔軟・一貫して評価できます。

## 運用"固定"ショート版（これだけで回します）

### T1限定（SEC/IR、逐語≤25語＋#:~:text=、欠測は n/a）

### ①長期EV確度
- 流動性・負債・希薄化・運転資本などのみ（価格/マルチ不使用）

### ②長期EV勾配
```
NES = 0.5·q/q + 0.3·改定% + 0.2·受注% + Margin_term + Health_term(Ro40)
```
- ★判定を機械化（Ro40は②のみ）

### ③バリュエーション＋認知ギャップ（体温計）＝二段構え
- **Step-1**：Disc%＝EV/S_actual vs max(ピアEV/S中央値, rDCF帯) → 色/Vmult決定
- **Step-2**：Δg と 認知フラグ(+/−)で Verdict（色は変えない）

### Lint強制
- ③にRo40が出たらFAIL
- ③はPM+rDCF以外NG
- Price-Modeは日付＋出典必須

### 判断
- 上記だけでマトリクス→DI→Decision
- 恣意は入れない、過実装もしない
- 必要なのはこの箱の中で数字を埋めることだけ

## 使用方法

### PowerShell実行例

```powershell
# ①長期EV確度
.\Start-S3FixedShort.ps1 -Action axis1 -Axis1Evidence "completed the ATM… ~$98M #:~:text=completed%20the%20ATM" -Axis1Score 3 -Axis1Confidence 0.72

# ②長期EV勾配（NES式と★判定を機械化）
.\Start-S3FixedShort.ps1 -Action axis2 -QQPct 17.48 -GuidanceRevisionPct 0 -OrderBacklogPct 0 -MarginChangeBps 0 -Ro40 45.0

# ③バリュエーション＋認知ギャップ（体温計）＝二段構え
.\Start-S3FixedShort.ps1 -Action axis3 -EvSActual 5.0 -EvSPeerMedian 5.0 -GFwd 15.0 -OPMFwd 5.0 -GPeerMedian 12.0 -Axis3Evidence "ガイダンス上方, 実出荷, 前受, 契約負債↑ #:~:text=ガイダンス上方"

# マトリクス表示
.\Start-S3FixedShort.ps1 -Action matrix

# Lint強制チェック
.\Start-S3FixedShort.ps1 -Action lint

# 運用固定ショート版の要約
.\Start-S3FixedShort.ps1 -Action summary
```

### Python直接実行

```python
from s3_fixed_short import S3FixedShort

s3 = S3FixedShort()

# ①長期EV確度
axis1_data = s3.evaluate_axis1(
    "completed the ATM… ~$98M #:~:text=completed%20the%20ATM",
    3, 0.72
)

# ②長期EV勾配
axis2_data = s3.evaluate_axis2(17.48, 0, 0, 0, 45.0)

# ③バリュエーション＋認知ギャップ
axis3_data = s3.evaluate_axis3(5.0, 5.0, 15.0, 5.0, 12.0, 
                              "ガイダンス上方, 実出荷, 前受, 契約負債↑ #:~:text=ガイダンス上方")

# マトリクス表示
matrix_display = s3.get_matrix_display(axis1_data, axis2_data, axis3_data)
print(matrix_display)
```

## ファイル構成

```
ahf/_scripts/
├── s3_fixed_short.py        # S3-Fixed-Short実装
├── Start-S3FixedShort.ps1   # PowerShellランチャー
└── README_S3_Fixed_Short.md # このファイル
```

## 適用例

### AAOI（Q3 T1入り次第更新）
- ①長期EV確度：流動性・負債・希薄化・運転資本
- ②長期EV勾配：NES計算（Ro40は②のみ）
- ③バリュエーション＋認知ギャップ：二段構え

### 他銘柄（PLTR/DUOL/APPなど）
- 同じ手順で評価
- T1の数値を拾うだけでOK

## 注意事項

- 全ての説明は日本語で行う
- カーソルルールは常時遵守
- 変更時は必ずこのファイルを更新
- 新しいルール追加時はChair承認必須
- **運用"固定"ショート版（これだけで回します）に完全準拠**
- **以後、この型から逸脱しません**
- **すぐ適用できます**
