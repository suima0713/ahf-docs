# AHF v2 (Starless) — Minimal Logic Notes

- α4 (when RPO absent):
  Q_rev_ma2 = mean(Q4_revenue, FY_revenue/4)
  coverage_proxy = (Backlog / Q_rev_ma2) * 3
  Gate = Green/Amber/Red by thresholds.yaml
  ※ CL/Bookingsが未開示でも Red→Amber への緩和はしない（過度の上方判定を防止）

- α5:
  KPI = first_available([Adj EBITDA (Ex.99.1), Non-GAAP OI + D&A, GAAP OI + D&A])
  OpEx = Rev * NG_GM - KPI
  出力は min/median/max と alpha5_math_pass フラグのみ

- TW:
  2Q連続 AND 条件（CL_qoq & coverage_proxy_qoq）を満たすと発火
  ノイズ閾値（$250k or 5%）未満は無視
  発火後1Qはクールダウン
