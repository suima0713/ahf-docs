# -*- coding: utf-8 -*-
"""Extract Rev / Non-GAAP GM% / Adjusted EBITDA from Ex.99.1-like text.
Robust to parentheses negatives and sparse formatting.
"""
from typing import Optional, Dict
from .patterns import RE_TOTAL_REVENUES, RE_NG_GM_PCT, RE_ADJ_EBITDA, parse_num_to_int_k

class Ex99LiteResult(Dict):
    pass

def parse_ex99_lite(text: str) -> Ex99LiteResult:
    out: Ex99LiteResult = Ex99LiteResult()

    m_rev = RE_TOTAL_REVENUES.search(text)
    if m_rev:
        out["rev_k"] = parse_num_to_int_k(m_rev.group(1))
    
    m_gm = RE_NG_GM_PCT.search(text)
    if m_gm:
        out["ng_gm_pct"] = float(m_gm.group(1))

    m_ebitda = RE_ADJ_EBITDA.search(text)
    if m_ebitda:
        out["adj_ebitda_k"] = parse_num_to_int_k(m_ebitda.group(1))

    out["status"] = "ok" if set(out.keys()) >= {"rev_k", "ng_gm_pct", "adj_ebitda_k"} else "partial"
    return out
