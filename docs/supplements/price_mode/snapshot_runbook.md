# ③ スナップ手順（同日・同ソース）

1) ベンダを選定（例：Yahoo）  
2) **同日ET**で issuer/peer の **EV/S(TTM)** を取得  
3) peer_median を算出（偶数は平均）  
4) `Disc%` → 色/Vmult 決定  
5) `valuation_overlay` に記録（date/source/peer_set/price_lint）
