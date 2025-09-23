# AHF v0.7.2β Fail-safe統合版 - 最終システム

## 概要

AHF v0.7.2β Fail-safe統合版は、Stage-1での誤判定を防ぐ運用ルールを導入した最終システムです。

### 核心思想

**"結論に直結する最重要3点"で初期スクリーニングでもブレない＝誤判定しない運用**

- ①確かさ（LEC反証優先）
- ②勾配（短期傾きのみ）  
- ③評価＋認知（V-Overlay VRG）

## 主要機能

### 1. Fail-safe運用ルール

**欠落時はWATCH固定・GOは出さない**

- 欠落キーが1つでもあれば、Decisionは自動的にWATCH
- GO判定は全軸データ充足時のみ
- 誤判定リスクを最小化

### 2. ①長期EV成長の確かさ（LEC反証優先）

**反証：減点のみ・上振れ不可**

#### 3つの反証ゲート
1. **生存性**（流動性・コベナンツ・利益）
   - 現金残高 < $100M → 減点
   - 運転資本 ≤ 0 → 減点
   - EBITDA ≤ 0 → 減点
   - RCF利用可能額 < $50M → 軽微減点

2. **優位性**（価格転嫁力/構造）
   - ASP下落 → 減点
   - 価格圧力言及 → 減点
   - 競合脅威言及 → 減点

3. **ニーズ粘着性**（政策/顧客遅延）
   - 政策リスク言及 → 減点
   - 案件遅延言及 → 減点
   - 規制不確実性言及 → 減点

#### 最終★計算
```
最終★ = min{機械式ベース, 3ゲート判定}
```
**上振れ不可**の保守的判定

### 3. ②勾配（短期傾きのみ）

**プロキシ不足は★2（中立寄り）**

#### 評価項目
- **ガイダンスq/q**：次四半期の成長率
- **B/B**：受注残比率
- **マージン漂移**：利益率の変化

#### 判定ルール
- プロキシ充足度：最低2つ以上のデータが必要
- プロキシ不足時：自動的に★2
- データ充足時：スコアに基づく★1-5

### 4. ③評価＋認知（V-Overlay VRG）

**EV/S×Ro40のみ・未投入は未判定**

#### 評価項目
- **EV/S**：企業価値/売上比率
- **Ro40**：Rule of 40指標

#### 判定ルール
- データ充足度：EV/S×Ro40の両方が必要
- 未投入時：カテゴリ=UNDETERMINED、★=0
- 投入時：Green/Amber/Red判定

## ファイル構成

### コアエンジン
- `ahf_failsafe_engine_v072.py` - Fail-safe運用ルール
- `ahf_lec_analysis_failsafe_v072.py` - ①LEC反証優先分析
- `ahf_alpha_scoring_failsafe_v072.py` - ②勾配短期傾き分析
- `ahf_v_overlay_failsafe_v072.py` - ③V-Overlay VRG分析

### 統合システム
- `ahf_v072_failsafe_integrated.py` - Fail-safe統合版

## 使用方法

### 基本的な実行
```bash
python ahf_v072_failsafe_integrated.py <triage.jsonのパス> <facts.mdのパス>
```

### 出力例
```
=== AHF v0.7.2β Fail-safe統合評価結果 ===
銘柄: ARRY
As of: 2025-09-22

【①長期EV成長の確かさ（LEC反証優先）】
  ★: 2
  生存性: PASS
  優位性: FAIL
  ニーズ: WARN
  説明: 生存性:PASS 優位性:FAIL ニーズ:WARN →★2

【②勾配（短期傾きのみ）】
  ★: 2
  ガイダンスq/q: N/A
  B/B: 1.0x
  プロキシ充足度: False
  説明: プロキシ不足→★2

【③評価＋認知（V-Overlay VRG）】
  ★: 0
  EV/S: N/A
  Ro40: N/A
  カテゴリ: UNDETERMINED
  データ充足度: False
  説明: EV/S×Ro40データ不足→未判定

【Fail-safe判定】
  Decision: WATCH
  Fail-safe適用: True
  欠落キー: ②次Q q/q, ②マージン漂移, ③EV/S(Fwd), ③Ro40
  ①★2 × ②★2 × ③★0
```

## 判定ロジック

### Decision判定
1. **Fail-safeチェック**
   - 欠落キーあり → WATCH（強制）
   
2. **通常判定**
   - ②★3以上 × ③★2以上 → GO
   - ②★2以上 × ③★1以上 → WATCH
   - その他 → NO-GO

### 欠落キー定義
- **②勾配**：次Q q/q、B/B、マージン漂移
- **③V-Overlay**：EV/S(Fwd)、Ro40
- **①LEC**：生存性データ、優位性データ、需要データ

## 設定ファイル

### thresholds.yaml（オプション）
```yaml
lec_failsafe:
  survival_thresholds:
    cash_min: 100000000
    rcf_min: 50000000
  moat_penalties:
    asp_decline: -1.0
    price_pressure: -0.5
    competitive_threat: -0.5
  demand_penalties:
    policy_risk: -1.0
    project_delay: -0.5
    regulatory_uncertainty: -0.5

alpha_failsafe:
  thresholds:
    guidance_qoq_strong: 12.0
    guidance_qoq_positive: 0.0
    book_to_bill_strong: 1.1
    book_to_bill_adequate: 1.0
    margin_trend_positive: 0.0
  weights:
    guidance: 0.5
    book_to_bill: 0.3
    margin_trend: 0.2

v_overlay_failsafe:
  thresholds:
    ev_sales:
      green_max: 8.0
      amber_max: 15.0
    rule_of_40:
      green_min: 40.0
      amber_min: 20.0
```

## 運用上の特徴

### 1. 保守的安全性
- データ不足時は自動的に保守的判定
- 上振れリスクを排除
- 誤判定による損失を最小化

### 2. 透明性
- 欠落キーを明確に表示
- 各軸の判定根拠を詳細に説明
- Fail-safe適用理由を明示

### 3. 実用性
- Stage-1スクリーニングでの誤判定防止
- 投資判断の最重要3点に集中
- 運用負荷を最小化

## バージョン履歴

### v0.7.2β Fail-safe統合版
- Fail-safe運用ルール導入
- ①LEC反証優先・減点のみ
- ②勾配短期傾きのみ・プロキシ不足は★2
- ③V-Overlay EV/S×Ro40のみ・未投入は未判定
- 欠落時はWATCH固定・GOは出さない

## 注意事項

1. **設定ファイル**：thresholds.yamlが存在しない場合はデフォルト値を使用
2. **エラーハンドリング**：設定値の欠落時は安全なデフォルト値にフォールバック
3. **ファイル形式**：入力ファイルはUTF-8エンコーディング必須
4. **パフォーマンス**：大量データ処理時はメモリ使用量に注意

## ライセンス

AHF v0.7.2β Fail-safe統合版
Copyright (c) 2025 AHF Project



