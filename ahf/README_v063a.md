# AHF v0.6.3a 実装完了

## 概要

認知ギャップ★の再定義により、「今は未確証だが、殺さない」をデータ構造として担保する仕組みを実装完了。

## 主要機能

### 1. 認知ギャップ★の再定義
- **デフォルト★=3維持**: 基本評価は変更なし
- **オプション種±1★**: T1で確認できる"オプション種"がある銘柄は±1★調整
- **キルスイッチ限定**: 3つの致命的要因のみで-1★即時

### 2. オプション種（Option Seeds）
- **最大3件**: T1逐語×最大3で芽の根拠を列挙
- **4つのタイプ**:
  - ① 非常に大きい新規契約/許認可/供給能力の数値開示
  - ② coverage≥9か月（α4でGreen/Amber）
  - ③ ガイダンスの段差上げ
  - ④ セグメント再編で高粗利の顕在化

### 3. Validation Hooks
- **後段検証の一点**: 次に何を確かめれば芽が花になるかを一行で
- **タイムライン**: 1-4四半期の検証スケジュール
- **キーメトリクス**: 検証すべき具体的指標

### 4. priced_in（市場織込み）とalpha不透明度
- **オプション種が強いほど**: 織込み=低、不透明度=高
- **可能性を残す**: "上に振れる余地"を即時に残す

### 5. 方向確率の可変幅拡大
- **通常±5pp → ±10ppまで**: オプション種の強さに応じて拡大
- **上向き確率の調整**: オプション種が強いほど上向き確率を上昇

### 6. キルスイッチの明文化（3つ限定）
- **① 収益認識の後ろ向き会計イベントの定量**
- **② 開示統制"not effective"が収益認識に直結**
- **③ coverageが連続悪化**

## ファイル構成

```
ahf/
├── mvp4/
│   ├── cognitive_gap_v063a.py       # 認知ギャップ分析
│   ├── fast_screen_v063.py         # Fast-Screen
│   ├── mini_confirm_v063.py        # Mini-Confirm
│   └── alpha_bridge_v063.py        # αブリッジ標準
├── scripts/
│   └── ahf_v063a_integrated.py     # v0.6.3a統合実行
├── config/
│   └── ahf_v063a_config.json       # v0.6.3a設定
└── state/
    └── ahf_v063a_sample_state.json # サンプル状態
```

## 使用方法

### 1. 基本実行
```bash
# v0.6.3a統合実行
python3 ahf/scripts/ahf_v063a_integrated.py \
  --config ahf/config/ahf_v063a_config.json \
  --state ahf/state/ahf_v063a_sample_state.json \
  --out ahf/out/v063a_results.json

# 認知ギャップ分析のみ
echo '{"ticker": "SYM", "large_contracts": [...]}' | python3 ahf/mvp4/cognitive_gap_v063a.py --config ahf/config/ahf_v063a_config.json
```

### 2. オプション種の設定例
```json
{
  "large_contracts": [
    {
      "value_$k": 150000,
      "verbatim": "New enterprise contract worth $150M",
      "anchor": "https://sec.gov/edgar/data/1234567/000123456724000001/0001234567-24-000001-index.htm#:~:text=New%20enterprise%20contract",
      "strength": "high"
    }
  ],
  "guidance_upgrade": {
    "upgraded": true,
    "description": "Revenue guidance raised by 15%",
    "verbatim": "Revenue guidance increased from $580M to $600M",
    "anchor": "https://investors.sym.com/earnings#:~:text=Revenue%20guidance%20increased",
    "magnitude": 15
  },
  "coverage_months": 12.5,
  "segment_restructure": {
    "restructured": true,
    "description": "High-margin segment expansion",
    "verbatim": "Expanded high-margin cloud segment",
    "anchor": "https://sec.gov/edgar/data/1234567/000123456724000001/0001234567-24-000001-index.htm#:~:text=Expanded%20high-margin",
    "margin_improvement": 8
  }
}
```

## 表示フォーマット

### 認知ギャップ分析結果
```
🧠 認知ギャップ分析結果:
  銘柄: SYM
  ★評価: 認知ギャップ★4 (Base3+Option+1.0+Kill+0.0)
  オプション種: 3件
  織込み/不透明度: 織込み=low, 不透明度=high
  方向確率: 方向確率: 70%/30% (調整幅±10.0pp)
```

### オプション種詳細
```
📊 オプション種:
  1. Large Contract: $150,000k (High strength)
  2. Coverage Strength: 12.5 months (High strength)  
  3. Guidance Upgrade: Revenue guidance raised by 15% (High strength)

🔍 Validation Hooks:
  1. Large Contract → Next quarter revenue recognition and cash flow impact (1-2 quarters)
  2. Coverage Strength → RPO conversion to revenue and margin expansion (2-3 quarters)
  3. Guidance Upgrade → Guidance execution and underlying drivers (1 quarter)
```

### ファネル統合結果
```
📊 AHF v0.6.3a 統合評価結果
================================================================================
📅 評価日時: 2024-12-19
🏷️  銘柄: SYM
🔧 バージョン: v0.6.3a

🧠 認知ギャップ分析:
  ★評価: 認知ギャップ★4 (Base3+Option+1.0+Kill+0.0)
  オプション種: 3件
  織込み/不透明度: 織込み=low, 不透明度=high
  方向確率: 方向確率: 70%/30% (調整幅±10.0pp)

🚀 Fast-Screen:
  判定: PASS
  理由: Hard pass: Both axis1 and axis2 >= 3 stars
  ★評価: 4/3/3/4

🔍 Mini-Confirm:
  判定: GO
  理由: Both α3 and α5 passed
  α3: PASS
  α5: PASS

🔬 Deep-Dive:
  実行: 完了
  ★評価: ★4/5 (Core3+Edge+1)
  確信度: 確信度80% (Base75+Edge+5)

🎯 ファネル判定:
  最終判定: GO
  理由: All stages passed
  段階: deep_dive
```

## 効果イメージ

### ALAB例
```
Option Seeds:
- Q3売上ガイド上振れ
- 営業CF大
- AIラック量産

結果:
- 認知ギャップ★3→4
- priced_in=中→低
- 上向き確率+5pp
```

### FROG例
```
Option Seeds:
- クラウド+45%
- 12M RPO≈7.5か月

結果:
- ★3維持
- 方向確率56/44→60/40に拡げ
- 可能性を残す
```

## キルスイッチの明文化

### 使用可能な3つ
1. **収益認識の後ろ向き会計イベントの定量**
2. **開示統制"not effective"が収益認識に直結**
3. **coverageが連続悪化**

### 使用不可
- その他の弱材料は確率・織込みで表現
- ★では殺さない

## 運用開始手順

### 1. 環境準備
```bash
# 設定ファイル準備
cp ahf/config/ahf_v063a_config.json ahf/config/production_config.json

# 状態ファイル準備
cp ahf/state/ahf_v063a_sample_state.json ahf/state/production_state.json
```

### 2. 初回実行
```bash
# v0.6.3a統合実行
python3 ahf/scripts/ahf_v063a_integrated.py \
  --config ahf/config/production_config.json \
  --state ahf/state/production_state.json \
  --out ahf/out/v063a_results.json
```

### 3. 結果確認
```bash
# 結果表示
cat ahf/out/v063a_results.json | jq '.cognitive_gap_analysis'

# オプション種確認
cat ahf/out/v063a_results.json | jq '.cognitive_gap_analysis.option_seeds'

# Validation Hooks確認
cat ahf/out/v063a_results.json | jq '.cognitive_gap_analysis.validation_hooks'
```

## 注意事項

1. **v0.6.3の維持**: 既存の品質基準を崩さない
2. **オプション種制限**: 最大3件まで
3. **キルスイッチ限定**: 3つの致命的要因のみ
4. **T1限定**: 未開示は未開示として扱う
5. **Anchor必須**: テキストフラグメントの必須化

## まとめ

v0.6.3aにより、「今は未確証だが、殺さない」をデータ構造として担保。オプション種の特定とValidation Hooksにより、可能性を残しながら適切なリスク管理を実現。

**「星は静かに、確率と織込みで可能性を開く」に寄せた運用が可能になりました。**



