# Price-Mode Quick Ref（③ 現バリュ＝絶対・機械）

目的：同日・同ソースの EV/S(TTM) で「帯×EVS_today」の乖離を機械判定。

## 手順（90秒）
1) 帯＝10/8/6×（T1/T1*：g_fwd・OPM_fwd、中点）
2) EVS_today＝EV/S_actual_TTM（同日・同ソース）
3) Disc_abs = (fair_band − EVS_today) / fair_band
4) 色/Vmult：Green 1.05｜Amber 0.90｜Red 0.75
5) Price-Lint：{ ev_used:true, ps_used:false, same_day:true, same_source:true }

## EV 定義
EV = Market Cap + Total Debt + Preferred + Minority − Cash & Equivalents

## 禁止
- Fwd/NTM EV/S を分母に使わない
- peer（相対）や将来仮定を③に混入しない（相対は④へ）
