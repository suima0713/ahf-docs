#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AHF EDGAR CLI Skeleton (MVP-4+)

Purpose:
  Deterministically fetch latest 10-Q/10-K/8-K(Ex.99.1) for a CIK,
  extract RPO 12M % from notes, parse Ex.99.1 for Rev/NG-GM/Adj.EBITDA,
  compute α4/α5 + auto-checks, and emit AHF-ready JSON.

Design:
  - EDGAR native APIs only (Submissions / Company Facts / Frames)
  - HTML note phrase windowing for 12M% (no external heavy parsers)
  - MVP-4 primitives: Dual-Anchor, Gap-Reason, Lite Ex.99.1 parser

Usage:
  python ahf_edgar_cli.py --cik 1819994 --user-agent "AHF/0.6.0 (ops@example.com)" \
    --alpha5-bands 83000 86500 --out out.json

Requirements:
  - Python 3.10+
  - requests (pip install requests)

Note:
  This is a skeleton meant for Cursor. Extend as needed.
"""

import argparse, time, json, re, hashlib, sys, random
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timezone
import requests

# ----------------------------- Config & Helpers -----------------------------

DEFAULT_HEADERS = {
    "User-Agent": "AHF/0.6.0 (contact: ops@example.com)"
}

THROTTLE_SEC = 0.2  # be polite to EDGAR

RETRY_STATUS = {429, 500, 502, 503, 504}

def log(level: str, event: str, **kw):
    rec = {"ts": datetime.now(timezone.utc).isoformat(), "lv": level, "ev": event}
    rec.update(kw)
    print(json.dumps(rec, ensure_ascii=False), file=sys.stderr)

PHRASES_12M = [
    "within 12 months", "within twelve months", "next 12 months", "next twelve months",
    "twelve-month period", "12-month period"
]

RE_TOTAL_REVENUES = re.compile(r"\bTotal\s+revenues?\b[^\d\-\(]*([\(\)\-\d,]+)", re.I)
RE_NG_GM_PCT = re.compile(r"\bNon\-GAAP\s+Gross\s+margin\b[^\d%]*([\-\d\.]+)\s*%", re.I)
RE_ADJ_EBITDA = re.compile(r"\bAdjusted\s+EBITDA\b[^\d\-\(]*([\(\)\-\d,]+)", re.I)


def _get_with_retries(url: str, headers: Dict[str, str], timeout=30, retries=3, backoff=0.5):
    for i in range(retries + 1):
        try:
            r = requests.get(url, headers=headers, timeout=timeout)
            ra = r.headers.get("Retry-After")
            if r.status_code in RETRY_STATUS:
                wait = float(ra) if ra else backoff * (2 ** i) + random.uniform(0, 0.2)
                log("warn", "http_retry", url=url, code=r.status_code, wait=round(wait,2), attempt=i)
                time.sleep(wait); continue
            r.raise_for_status()
            log("info", "http_ok", url=url, code=r.status_code)
            return r
        except requests.RequestException as e:
            if i == retries:
                log("error", "http_fail", url=url, err=str(e), attempt=i)
                raise
            wait = backoff * (2 ** i) + random.uniform(0, 0.2)
            log("warn", "http_retry_exc", url=url, err=str(e), wait=round(wait,2), attempt=i)
            time.sleep(wait)

def http_json(url: str, headers: Dict[str, str]) -> Any:
    r = _get_with_retries(url, headers)
    time.sleep(THROTTLE_SEC)
    return r.json()

def http_text(url: str, headers: Dict[str, str]) -> str:
    r = _get_with_retries(url, headers)
    r.encoding = r.apparent_encoding or "utf-8"
    time.sleep(THROTTLE_SEC)
    return r.text


def num_to_int_k(s: str) -> int:
    s2 = s.strip().replace(",", "")
    neg = s2.startswith("(") or s2.startswith("-")
    s2 = s2.strip("()-")
    if not s2:
        return 0
    val = float(s2)
    if neg:
        val = -val
    return int(round(val))


def sha1(text: str) -> str:
    return hashlib.sha1(" ".join(text.split()).encode("utf-8")).hexdigest()

# ----------------------------- EDGAR Fetchers -------------------------------

SEC_SUBMISSIONS = "https://data.sec.gov/submissions/CIK{cik:010d}.json"
SEC_FACTS = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"


def get_submissions(cik: int, headers: Dict[str, str]) -> Dict:
    return http_json(SEC_SUBMISSIONS.format(cik=cik), headers)


def get_company_facts(cik: int, headers: Dict[str, str]) -> Dict:
    return http_json(SEC_FACTS.format(cik=cik), headers)


# ----------------------------- Discovery Logic ------------------------------

def latest_docs(sub: Dict) -> Dict[str, Dict]:
    """Return dict with latest 10-Q, 10-K, and 8-K (Ex.99.1 url) if available."""
    docs = {"10-Q": None, "10-K": None, "8-K": None}
    filings = sub.get("filings", {}).get("recent", {})
    forms = filings.get("form", [])
    accns = filings.get("accessionNumber", [])
    prims = filings.get("primaryDocument", [])
    file_dates = filings.get("filingDate", [])

    for i in range(len(forms)):
        f = forms[i]
        if f not in docs:
            continue
        # pick the most recent occurrence per form
        candidate = {
            "accession": accns[i],
            "primary": prims[i],
            "filing_date": file_dates[i],
            "index_url": f"https://www.sec.gov/Archives/edgar/data/{sub['cik']}/{accns[i].replace('-', '')}/{prims[i]}"
        }
        # choose latest by date
        if (docs[f] is None) or (candidate["filing_date"] > docs[f]["filing_date"]):
            docs[f] = candidate

    # For 8-K, we need Exhibit 99.1 url (simple heuristic: same accession, file name contains 99.1)
    if docs["8-K"] is not None:
        base = docs["8-K"]["index_url"].rsplit("/", 1)[0]
        # fetch the folder listing (index.htm) and try to find ex99
        folder_idx = base + "/index.json"
        try:
            idx = http_json(folder_idx, DEFAULT_HEADERS)
            items = idx.get("directory", {}).get("item", [])
            ex = next((it for it in items if "99.1" in it.get("name", "").lower()), None)
            if ex:
                docs["8-K"]["ex99_url"] = f"https://www.sec.gov/Archives/{idx['directory']['name']}/{ex['name']}"
        except Exception:
            pass
    return docs

# ----------------------------- 12M Extraction -------------------------------

def strip_tags(html: str) -> str:
    return re.sub(r"<[^>]+>", " ", html)


def find_12m_pct_from_html(html: str) -> Optional[float]:
    t = strip_tags(html)
    low = t.lower()
    for phr in PHRASES_12M:
        i = low.find(phr)
        if i == -1:
            continue
        window = t[max(0, i-160): i]
        m = re.search(r"(\d{1,3}(?:\.\d+)?)\s*%", window)
        if m:
            return float(m.group(1))
    return None

# ----------------------------- Ex.99.1 Parser -------------------------------

def parse_ex99(text_or_html: str) -> Dict[str, Any]:
    t = strip_tags(text_or_html)
    out: Dict[str, Any] = {"status": "partial"}
    m1 = RE_TOTAL_REVENUES.search(t)
    if m1:
        out["rev_$k"] = num_to_int_k(m1.group(1))
    m2 = RE_NG_GM_PCT.search(t)
    if m2:
        out["ng_gm_pct"] = float(m2.group(1))
    m3 = RE_ADJ_EBITDA.search(t)
    if m3:
        out["adj_ebitda_$k"] = num_to_int_k(m3.group(1))
    if set(out.keys()) >= {"rev_$k", "ng_gm_pct", "adj_ebitda_$k"}:
        out["status"] = "ok"
    return out

# ----------------------------- Facts helpers --------------------------------

RPO_TOTAL_KEYS = [
    "us-gaap:RemainingPerformanceObligation",
    "us-gaap:RemainingPerformanceObligations",
]
CL_KEYS = [
    "us-gaap:ContractWithCustomerLiabilityCurrent",
    "us-gaap:ContractWithCustomerLiabilityNoncurrent",
]


def pick_latest_fact_val(facts: Dict, qname: str) -> Optional[int]:
    obj = facts.get("facts", {}).get(qname, {})
    units = obj.get("units", {})
    for unit, arr in units.items():
        if "USD" not in unit:
            continue
        latest = max(arr, key=lambda x: (x.get("end", ""), x.get("fy", 0), x.get("fp", "")))
        return int(round(latest.get("val", 0)))
    return None


def get_rpo_total_k(facts: Dict) -> Optional[int]:
    for k in RPO_TOTAL_KEYS:
        v = pick_latest_fact_val(facts, k)
        if v is not None:
            return v
    return None


def get_cl_latest_k(facts: Dict) -> Optional[int]:
    total = 0
    found = False
    for k in CL_KEYS:
        v = pick_latest_fact_val(facts, k)
        if v is not None:
            total += v
            found = True
    return total if found else None

# ----------------------------- Dual Anchor & Gap ----------------------------

def dual_anchor(url: str, quote: str, pageno: Optional[int] = None) -> Dict[str, Any]:
    return {
        "anchor_primary": url,
        "anchor_backup": {
            "pageno": pageno,
            "quote": quote[:200],
            "hash": sha1(quote[:200])
        }
    }


def gap(field: str, reason: str, ttl_days: int = 30) -> Dict[str, Any]:
    if reason not in {"NOT_DISCLOSED", "TAG_ABSENT", "PHRASE_NOT_FOUND", "DIFF_PERIOD"}:
        reason = "NOT_DISCLOSED"
    return {"field": field, "status": "data_gap", "reason": reason, "ttl_days": ttl_days}

# ----------------------------- Auto-Judge / Checks --------------------------

def alpha5_compute_opex_k(rev_k: int, ng_gm_pct: float, adj_ebitda_k: int) -> int:
    # OpEx = Rev × NG-GM − Adj. EBITDA
    return int(round(rev_k * (ng_gm_pct / 100.0) - adj_ebitda_k))


def alpha5_band(opex_k: int, green_le: int, amber_le: int) -> str:
    if opex_k <= green_le:
        return "Green"
    if opex_k <= amber_le:
        return "Amber"
    return "Red"


def alpha4_coverage_months(rpo_12m_k: Optional[int], q_rev_k: Optional[int]) -> Optional[float]:
    if not rpo_12m_k or not q_rev_k or q_rev_k == 0:
        return None
    return round((rpo_12m_k / q_rev_k) * 3.0, 1)

def validate_alpha5_inputs(ex: Dict[str, Any]) -> Tuple[Dict[str, Any], list]:
    warns = []
    out = dict(ex)
    if "rev_$k" in out and out["rev_$k"] < 0:
        warns.append("rev_negative"); out["rev_$k"] = abs(out["rev_$k"])
    if "ng_gm_pct" in out and not (-100.0 <= out["ng_gm_pct"] <= 100.0):
        warns.append("ng_gm_out_of_range"); out["ng_gm_pct"] = None
    if "adj_ebitda_$k" in out and abs(out["adj_ebitda_$k"]) > 10**9:
        warns.append("ebitda_absurd"); out["adj_ebitda_$k"] = None
    if out.get("status") == "ok" and (out.get("ng_gm_pct") is None or out.get("adj_ebitda_$k") is None):
        out["status"] = "partial"
    return out, warns

def validate_alpha4(rpo_total_k, rpo_12m_pct, q_rev_k) -> Tuple[Optional[int], Optional[float], list]:
    warns = []
    if rpo_total_k is not None and rpo_total_k < 0:
        warns.append("rpo_total_negative"); rpo_total_k = abs(rpo_total_k)
    if rpo_12m_pct is not None and not (0 <= rpo_12m_pct <= 100):
        warns.append("rpo_12m_pct_out_of_range"); rpo_12m_pct = None
    cov = alpha4_coverage_months(int(round(rpo_total_k * (rpo_12m_pct/100))) if (rpo_total_k is not None and rpo_12m_pct is not None) else None, q_rev_k)
    if cov is not None and cov > 36.0:
        warns.append("coverage_implausible_gt36"); cov = None
    return rpo_total_k, rpo_12m_pct, warns

# ----------------------------- Main CLI -------------------------------------

def run(cik: int, ua: str, green: int, amber: int, out_path: Optional[str]) -> Dict[str, Any]:
    headers = {"User-Agent": ua}

    try:
        sub = get_submissions(cik, headers)
        docs = latest_docs(sub)
    except Exception as e:
        log("error","disc_fail", err=str(e))
        return {
            "cik": cik, "docs": None,
            "alpha4_rpo": {"rpo_total_$k": None, "rpo_12m_pct": None, "coverage_months": None,
                           "find_path": "manual", "gap_reason": gap("rpo_12m_pct","NOT_DISCLOSED")},
            "alpha5_inputs": {"status":"partial"},
            "alpha5": {"opex_$k": None, "band": None, "bands": {"green_≤": green, "amber_≤": amber}},
            "facts": {}, "anchors": {}, "auto_checks": {"alpha5_math_pass": False, "alpha4_gate_pass": False, "messages": ["discovery_failed"]}
        }

    try:
        facts = get_company_facts(cik, headers)
        rpo_total_k = get_rpo_total_k(facts)
        cl_k = get_cl_latest_k(facts)
    except Exception as e:
        log("error","facts_fail", err=str(e))
        rpo_total_k = None
        cl_k = None

    # 10-Q primary HTML
    try:
        html_url = docs.get("10-Q", {}).get("index_url")
        html_text = http_text(html_url, headers) if html_url else ""
        rpo_12m_pct = find_12m_pct_from_html(html_text) if html_text else None
    except Exception as e:
        log("error","html_fail", err=str(e))
        html_text = ""
        rpo_12m_pct = None

    # Heuristic for RPO_12m absolute if pct + total present
    rpo_12m_k = None
    if rpo_total_k is not None and rpo_12m_pct is not None:
        rpo_12m_k = int(round(rpo_total_k * (rpo_12m_pct / 100.0)))

    # Ex.99.1
    try:
        ex_url = docs.get("8-K", {}).get("ex99_url")
        ex_text = http_text(ex_url, headers) if ex_url else ""
        ex = parse_ex99(ex_text) if ex_text else {"status": "partial"}
    except Exception as e:
        log("error","ex99_fail", err=str(e))
        ex = {"status": "partial"}

    # 妥当性チェック適用
    ex, w1 = validate_alpha5_inputs(ex);  [log("warn","alpha5_input_warn", code=m) for m in w1]
    rpo_total_k, rpo_12m_pct, w2 = validate_alpha4(rpo_total_k, rpo_12m_pct, ex.get("rev_$k"))
    [log("warn","alpha4_warn", code=m) for m in w2]

    # α5
    opex_k, band = None, None
    if set(ex.keys()) >= {"rev_$k", "ng_gm_pct", "adj_ebitda_$k"}:
        opex_k = alpha5_compute_opex_k(ex["rev_$k"], ex["ng_gm_pct"], ex["adj_ebitda_$k"])
        band = alpha5_band(opex_k, green, amber)

    # α4 coverage months (need Quarterly Rev; use ex99 rev as proxy if same quarter)
    cov_m = alpha4_coverage_months(rpo_12m_k, ex.get("rev_$k")) if rpo_12m_k else None

    # Anchors
    a4_anchor = None
    if html_url and rpo_12m_pct is not None:
        frag = "within%2012%20months"
        a4_anchor = dual_anchor(f"{html_url}#:~:text={frag}", "… within 12 months …", None)

    a5_anchor = None
    if ex_url:
        a5_anchor = dual_anchor(ex_url, "Total revenues … Non-GAAP Gross margin … Adjusted EBITDA …", None)

    # Gap reasons
    a4_gap = None
    if rpo_12m_pct is None:
        a4_gap = gap("rpo_12m_pct", "PHRASE_NOT_FOUND" if html_text else "NOT_DISCLOSED")

    out = {
        "cik": cik,
        "docs": docs,
        "alpha4_rpo": {
            "rpo_total_$k": rpo_total_k,
            "rpo_12m_pct": rpo_12m_pct,
            "rpo_12m_$k": rpo_12m_k,
            "coverage_months": cov_m,
            "find_path": "note" if rpo_12m_pct is not None else "manual",
            "gap_reason": a4_gap
        },
        "alpha5_inputs": ex,
        "alpha5": {
            "opex_$k": opex_k,
            "band": band,
            "bands": {"green_≤": green, "amber_≤": amber}
        },
        "facts": {"contract_liabilities_$k": cl_k},
        "anchors": {"alpha4": a4_anchor, "alpha5": a5_anchor},
        "auto_checks": {
            "alpha5_math_pass": bool(opex_k is not None),
            "alpha4_gate_pass": bool(cov_m is not None and cov_m >= 11.0),
            "messages": []
        }
    }

    # Simple sanity messages
    if out["alpha4_rpo"]["coverage_months"] is None:
        out["auto_checks"]["messages"].append("α4 coverage not computed: missing RPO_12M% or Quarterly Rev")
    if out["alpha5"]["band"] is None:
        out["auto_checks"]["messages"].append("α5 band not computed: missing ex99 metrics")

    # 要約ログ
    log("info","summary",
        cik=cik,
        a4_pass=bool(out["auto_checks"]["alpha4_gate_pass"]),
        a5_band=out["alpha5"]["band"],
        rpo_total_k=rpo_total_k,
        rpo_12m_pct=rpo_12m_pct,
        coverage_m=out["alpha4_rpo"]["coverage_months"])

    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
    return out


def main():
    ap = argparse.ArgumentParser(description="AHF EDGAR CLI Skeleton (MVP-4+)")
    ap.add_argument("--cik", type=int, required=True, help="Company CIK (int)")
    ap.add_argument("--user-agent", type=str, default=DEFAULT_HEADERS["User-Agent"], help="HTTP User-Agent")
    ap.add_argument("--alpha5-bands", type=int, nargs=2, default=[83000, 86500], metavar=("GREEN_LE", "AMBER_LE"))
    ap.add_argument("--out", type=str, default=None, help="Output JSON path")
    args = ap.parse_args()

    DEFAULT_HEADERS["User-Agent"] = args.user_agent
    out = run(args.cik, args.user_agent, args.alpha5_bands[0], args.alpha5_bands[1], args.out)
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        sys.stderr.write(f"[ERROR] {e}\n")
        sys.exit(1)
