# Axis-4 Relative Overlay（④ 市場相対ギャップ＝統合）

目的：①質・②傾き・③絶対・歪み(TR) を束ねた"相対"の読み解き。

## スコア（R）
- Disc_rel = (peer_median_TTM − EVS_today) / peer_median_TTM
- Δg = g_fwd − g_peer_median（T1/T1*、pp）
- s1 = ①★/5, s2 = ②★/5
- TR_adj ∈ { +0.15, +0.05, 0, −0.05, −0.15 }（上限±0.20）
- 正規化：z_rel, z_dg ∈ [−1,+1]（±25%→±1、クリップ）
- 合成：R = 0.40·z_rel + 0.20·z_dg + 0.20·s1 + 0.20·s2 + TR_adj
- 相対★：R% ≥+15→★5／+5〜+15→★4／−5〜+5→★3／−15〜−5→★2／≤−15→★1

## 補助指標
PII = peer_median_TTM / fair_band（>1＝業界相対が公正帯より高止まり）

## ポリシー
- ④は**説明専用**（DIに不使用、必要時 SoftOverlay ±0.05）
- ③のVmultだけが DI に入る（安定性担保）
