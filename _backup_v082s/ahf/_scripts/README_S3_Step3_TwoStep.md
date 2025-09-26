# S3-Step3-TwoStep v1.0（最小・強制）

## 概要

**③バリュエーション＋認知ギャップ｜Two-Step v1.0**の実装です。温度（Step-1）→妥当性（Step-2）の二段で固定し、複雑化せず・恣意なく・再現可能で運用できます。

## Step-1｜フェアバリュー差（割安/割高の素点）

### 使うもの（これだけ）
- **EV/S_actual**（Price-Mode：市場データ。日付・出典名を併記）
- **EV/S_peer_median**（ピア群のEV/S中央値。Price-Mode）
- **EV/S_fair_rDCF**（逆DCFライトの"帯"で決めるフェアEV/S。T1の成長・OPMだけ）

### 計算（四則のみ）

#### rDCFライトの帯
- **EV/S_fair_rDCF = 10×** … g_fwd≥25% かつ OPM_fwd≥0%
- **EV/S_fair_rDCF = 8×** … いずれか中間（10–25% or −5〜0%）
- **EV/S_fair_rDCF = 6×** … g_fwd<10% or OPM_fwd≤−5%

※ g_fwd はT1ガイダンス年率換算、OPM_fwd はT1（なければ直近GAAP OPM）

#### フェアの基準
```
EV/S_fair_base = max(EV/S_peer_median, EV/S_fair_rDCF)（保守）
```

#### 割引率
```
Disc% = (EV/S_fair_base − EV/S_actual) / EV/S_fair_base
```

### 色（DI倍率）はStep-1だけで機械決定
- **Green**：|Disc%| ≤ 10%
- **Amber**：10% < |Disc%| ≤ 25%
- **Red**：|Disc%| > 25%

→ **Vmult**：Green 1.05 / Amber 0.90 / Red 0.75（変更不可）

**ここまでが体温計の温度。Ro40は使用禁止（②でのみ使用）。**

## Step-2｜適正性チェック（期待成長/認知ギャップで"割安/割高の妥当性"を判断）

### 使うもの（T1だけ）
- **期待成長の相対差**：Δg = g_fwd − g_peer_median（ピアのT1ガイダンス）
- **認知フラグ（±）**：T1逐語の有無

#### 認知フラグ（＋）
- raises guidance、began/volume shipments、contract liabilities↑、ATM sales to date=0、10%顧客分散

#### 認知フラグ（−）
- acceptance required、Raw/WIP滞留、ATM実行、集中度悪化

### 判定（ラベルだけ／色は変えない）
- **Underpriced / 不適正（割安すぎ）**：Disc%>10% かつ Δg ≥ +10pp or ＋フラグ≥2
- **Underpriced / ほぼ適正**：Disc%>10% かつ |Δg|<10pp かつ フラグ拮抗
- **Overpriced / 不適正（割高すぎ）**：Disc%<−10% かつ Δg ≤ −10pp or −フラグ≥2
- **Overpriced / ほぼ適正**：Disc%<−10% かつ |Δg|<10pp かつ フラグ拮抗
- **中立**：|Disc%| ≤ 10%（Green圏内）

**Step-2は注釈のみ（DI倍率はStep-1で固定）。**
**必要ならSoftOverlay ±0.02以内で微調整可（任意・可逆）。**

## 出力フォーマット（③の固定欄｜欠測は n/a）

```
[Step-1] EV/S_actual(日付/出典) = x.x×
        EV/S_peer_median = y.y×, EV/S_fair_rDCF = z.z× → EV/S_fair_base = …
        Disc% = …
        色 = Green/Amber/Red（Vmult=…）

[Step-2] 期待成長Δg = …pp, 認知フラグ [+n / −m]
        Verdict = Underpriced/Overpriced/Neutral（適正/不適正）
```

## S3-Lint ③（追加の最小チェック）

### チェック項目
- **L5-a**：③にRo40が出現したらFAIL
- **L5-b**：③はEV/S_actual・ピア中央値・rDCF帯のみ（他指標混入でFAIL）
- **L6**：Price-Modeは日付＋出典名必須
- **L7**：欠測はn/a

## 使い方（AAOIにそのまま当て込む）

1. **まずEV/S_actual（日付・出典）とピアEV/S中央値を取得**
2. **T1でg_fwd, OPM_fwdを入れてrDCF帯→Step-1を確定**
3. **顧客/同業のT1でΔgと認知フラグを集め、Step-2のVerdictを付ける**
4. **色とVmultはStep-1だけで決まる（Ro40は②にのみ反映）**

## 使用方法

### PowerShell実行例

```powershell
# ③バリュエーション＋認知ギャップの完全評価
.\Start-S3Step3TwoStep.ps1 -Action complete -EvSActual 5.0 -EvSPeerMedian 5.0 -GFwd 15.0 -OPMFwd 5.0 -GPeerMedian 12.0 -Evidence "raises guidance, began volume shipments #:~:text=raises%20guidance" -ActualDate "2025-09-19" -ActualSource "Yahoo Finance"

# Step-1のみ
.\Start-S3Step3TwoStep.ps1 -Action step1 -EvSActual 5.0 -EvSPeerMedian 5.0 -GFwd 15.0 -OPMFwd 5.0

# Step-2のみ
.\Start-S3Step3TwoStep.ps1 -Action step2 -GFwd 15.0 -GPeerMedian 12.0 -Evidence "raises guidance, began volume shipments #:~:text=raises%20guidance"

# S3-Lint ③チェック
.\Start-S3Step3TwoStep.ps1 -Action lint -EvSActual 5.0 -EvSPeerMedian 5.0 -GFwd 15.0 -OPMFwd 5.0 -Evidence "ro40=45, margin改善 #:~:text=ro40"
```

### Python直接実行

```python
from s3_step3_twostep import S3Step3TwoStep

s3_step3 = S3Step3TwoStep()

# ③バリュエーション＋認知ギャップの完全評価
result = s3_step3.evaluate_complete_step3(
    ev_s_actual=5.0,
    ev_s_peer_median=5.0,
    g_fwd=15.0,
    opm_fwd=5.0,
    g_peer_median=12.0,
    evidence="raises guidance, began volume shipments #:~:text=raises%20guidance",
    actual_date="2025-09-19",
    actual_source="Yahoo Finance"
)

print(result["output_format"])
print(f"Lint結果: {'PASS' if result['lint_pass'] else 'FAIL'}")
```

## ファイル構成

```
ahf/_scripts/
├── s3_step3_twostep.py        # S3-Step3-TwoStep v1.0実装
├── Start-S3Step3TwoStep.ps1   # PowerShellランチャー
└── README_S3_Step3_TwoStep.md # このファイル
```

## 注意事項

- 全ての説明は日本語で行う
- カーソルルールは常時遵守
- 変更時は必ずこのファイルを更新
- 新しいルール追加時はChair承認必須
- **③は"温度（Step-1）→妥当性（Step-2）"の二段に固定**
- **複雑化せず・恣意なく・再現可能で運用**
