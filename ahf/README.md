# AHF Minimal (Caps/Season Flags, T1 Catalog)

## 更新手順（最小）
1. `data/t1_catalog.csv` を追記/更新（EDGAR URLが空の行は source_class=T1-B とする）
2. `data/t1_catalog_prev.csv` は前回版を保持（差分可視化用）
3. `src/ahf_caps.py` の"入力定数"だけ編集（H1_ADJ、REV_H2_EX_DSI など）
4. `python3 src/ahf_caps.py` 実行 → H2_at_caps、通期SAT/UNSAT、T1Δを出力

## ルール
- CEIL_CAP & SEASON_Q3GEQ_Q4 は固定ON（閉形式一行式で安定）
- "not_found" はコード値で固定（例: `segment_margin_numeric_guidance=not_found`）
- T1-B（水印対象）：EDGAR URL空の行が主要レバーに含まれる場合、画面ラベル「Provisional」を付す（表示層で実装）

## 備考
- k係数（AdjEBITDA/OperatingIncome）は当面"参考列"のみ。必要なときに `k_factor()` 呼び出しで算出。
- Q3:Q4の分割は H2_at_caps 一行式では数値に影響しない（仕様）
