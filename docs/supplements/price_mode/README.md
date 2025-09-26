# Price-Mode（③＝現在のみ）
- 判定：**EV/S(TTM)** の **issuer vs peer_median(TTM)**（**同日・同ソース**）。
- 禁止：rDCF混入・P/S代替。④（将来EV）は別箱。
- Lint：ev_used=true / same_day=true / same_source=true。