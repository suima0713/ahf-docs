# 降格プロシージャ（T1*→T2）

トリガー：T1で**矛盾**が確認された場合

手順：
1. `status=contradiction:true` を付与
2. `evidence_tag: "T1*"` → **"T2"** へ降格
3. 関連★/FD%/Vmultを**再計**（必要ならUNCERTAINへ）
4. `triage.json` に差分ログ（旧→新）
5. 影響範囲（表・結論）を**Deltaカード**で提示
