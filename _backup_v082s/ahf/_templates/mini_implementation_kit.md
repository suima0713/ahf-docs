# AHFミニ実装キット - 実装損ゼロ・効くやつだけ

## 概要
単位/丸め/アンカー揺れを撲滅し、数式エラーを自動捕捉する最小構成の実装キットです。

## 導入の順序（10分で終わる最小手順）

### 1. 定数JSON（#2）をリポジトリに置く
```bash
# ガードレール定数は既に配置済み
ahf/_rules/guards.json
```

### 2. 既存出力をSOTスキーマ（#1）に合わせる
```bash
# SOTスキーマテンプレート
ahf/_templates/sot_schema.json
```

### 3. 監査マクロ（#3）を前処理に1回噛ませる
```bash
# 監査実行例
python ahf/_scripts/ahf_audit_macro.py payload.json ahf/_rules/guards.json
```

### 4. マトリクスに差分JSON（#5）を渡す
```bash
# マトリクス差分計算例
python ahf/_scripts/ahf_matrix_delta.py current_matrix.json prior_matrix.json
```

## 実装済みファイル

### スキーマ・テンプレート
- `ahf/_templates/sot_schema.json` - SOTスキーマ
- `ahf/_templates/matrix_delta.json` - マトリクス差分テンプレート
- `_templates/facts.md` - アンカー厳密化対応

### ガードレール・定数
- `ahf/_rules/guards.json` - ガードレール定数（共通定義）

### スクリプト
- `ahf/_scripts/ahf_audit_macro.py` - 監査マクロ
- `ahf/_scripts/ahf_matrix_delta.py` - マトリクス差分計算

## 効果

✅ **単位/係数ブレの再発ゼロ**
- ガードレール定数で統一
- 毎回の係数/閾値ブレ防止

✅ **アンカーの齟齬ゼロ（でも情報は削らない）**
- verbatim_≤25w + context_note の二段持ち
- 厳密化しても"最大情報"は温存

✅ **GM/GP/OpExの数式エラー自動捕捉**
- 監査マクロで事前チェック
- FAILなら赤札＋原因表示

✅ **マトリクスの差分説明が自動**
- 前回比の理由タグを機械的に付与
- 可視化ミス削減

## 運用ルール

### SOTスキーマ
- 金額=value_$k（千ドル整数）
- 率=pct（小数1位）
- 乖離=pp（小数2位）
- verbatim_≤25w は25語以内、削れない情報は context_note へ

### 監査マクロ
- GAAP→Non-GAAP GPブリッジ
- OT→GM（Stage-1）
- GAAP GM再計算
- アンカー検証（最小要件）

### アンカー厳密化
- verbatim_≤25w：法令順守用の短い逐語抜粋
- context_note：文脈・但し書き・表名など長文OK

## 注意事項
- 全ての説明は日本語で行う
- カーソルルールは常時遵守
- 変更時は必ずこのファイルを更新
