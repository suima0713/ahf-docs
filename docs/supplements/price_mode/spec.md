# 仕様（簡潔）

- 指標：`EV/S(TTM) = Enterprise Value / TTM Sales`
- EV定義：`EV = Market Cap + Total Debt + Preferred + Minority - Cash & Equivalents`
- as_of：**ET終値の同日**。休場は直近営業日。
- 必須：同一ベンダ／同一TTM定義／同一通貨
- ③の式：`Disc% = (peer_median - actual) / peer_median` → 色/Vmult
