#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AnchorLint v1 (MVP-4+)
 - Domain whitelist enforcement (sec.gov, investors.confluent.io)
 - Require #text-fragment (":~:text=")
 - Verbatim quote ≤ 25 words
 - anchor_backup {pageno, quote, hash(sha1)}
 - find_path ∈ {xbrl,note,md&a,fallback_text,manual}
 - Placeholder forbidding: \[[0-9]+\], PLACEHOLDER, not_found
 - Dual-anchor policy: primary=SEC (preferred), secondary=IR; fallback when SEC blocked

CLI:
  echo '{"facts":[...]}' | python ahf/mvp4/anchor_lint_v1.py --config ahf/config/anchorlint.yaml
"""
from __future__ import annotations
import sys, json, re, hashlib, argparse, urllib.parse
from typing import Dict, Any, List

DEFAULT_RULES = {
    "domain_whitelist": ["sec.gov", "investors.confluent.io"],
    "require_text_fragment": True,
    "verbatim_max_words": 25,
    "require_anchor_backup": True,
    "find_path_enum": ["xbrl", "note", "md&a", "fallback_text", "manual"],
    "placeholders_forbidden": [r"\[[0-9]+\]", r"(?i)not_found", r"(?i)PLACEHOLDER"],
    "dual_anchor_policy": {"primary": "SEC", "secondary": "IR", "fallback_when_sec_blocked": True}
}

def _host_ok(url: str, whitelist: List[str]) -> bool:
    try:
        host = urllib.parse.urlparse(url).netloc or ""
    except Exception:
        return False
    return any(host.endswith(d) for d in whitelist)

def _has_text_fragment(url: str) -> bool:
    return (":~:text=") in (url or "")

def _word_count(s: str) -> int:
    return len((s or "").strip().split())

def _sha1(s: str) -> str:
    return hashlib.sha1((s or "").encode("utf-8")).hexdigest()[:12]

def lint_anchor(f: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, Any]:
    """Lint a single T1 fact-like dict in-place and return it with auto_checks/gap_reason updates.
    Expected keys: 'anchor' or {'primary_anchor','secondary_anchor'}, 'verbatim_≤25w', 'anchor_backup', 'find_path'
    """
    out = dict(f)  # shallow copy
    auto = out.setdefault("auto_checks", {})
    msgs: List[str] = []
    pass_flags: List[bool] = []

    # Dual-anchor handling
    primary = out.get("primary_anchor") or out.get("anchor") or ""
    secondary = out.get("secondary_anchor")
    host_ok = _host_ok(primary, rules["domain_whitelist"]) if primary else False
    frag_ok = (not rules["require_text_fragment"]) or _has_text_fragment(primary)
    pass_flags += [host_ok, frag_ok]
    if not host_ok:
        msgs.append("primary host not whitelisted")
    if rules["require_text_fragment"] and not frag_ok:
        msgs.append("primary missing text-fragment")

    # Secondary when present
    if secondary:
        sec_host_ok = _host_ok(secondary, rules["domain_whitelist"])
        sec_frag_ok = (not rules["require_text_fragment"]) or _has_text_fragment(secondary)
        pass_flags += [sec_host_ok, sec_frag_ok]
        if not sec_host_ok:
            msgs.append("secondary host not whitelisted")
        if rules["require_text_fragment"] and not sec_frag_ok:
            msgs.append("secondary missing text-fragment")

    # Verbatim <= 25 words
    verb = out.get("verbatim_≤25w") or out.get("verbatim<=25w") or out.get("verbatim")
    if verb is None:
        pass_flags.append(False)
        msgs.append("missing verbatim_≤25w")
    else:
        wc = _word_count(verb)
        pass_flags.append(wc <= rules["verbatim_max_words"])
        if wc > rules["verbatim_max_words"]:
            msgs.append(f"verbatim too long ({wc} words)")

    # anchor_backup
    ab = out.get("anchor_backup")
    if rules["require_anchor_backup"]:
        ok = isinstance(ab, dict) and {"pageno", "quote", "hash"}.issubset(set(ab.keys()))
        pass_flags.append(ok)
        if not ok:
            # best-effort fill hash if quote exists
            if isinstance(ab, dict) and "quote" in ab and "hash" not in ab:
                ab["hash"] = _sha1(ab.get("quote", ""))
                out["anchor_backup"] = ab
            msgs.append("anchor_backup incomplete")

    # find_path enum
    fp = (out.get("find_path") or "").lower()
    fp_ok = fp in rules["find_path_enum"] if fp else False
    pass_flags.append(fp_ok)
    if not fp_ok:
        msgs.append("find_path invalid or missing")

    # Placeholder forbidding
    placeholders = rules["placeholders_forbidden"]
    ph_hit = False
    for pat in placeholders:
        try:
            if (re.search(pat, primary or "") or re.search(pat, (secondary or "")) or re.search(pat, (verb or ""))):
                ph_hit = True
                msgs.append(f"placeholder detected: {pat}")
                break
        except re.error:
            # Invalid regex pattern, skip
            continue
    pass_flags.append(not ph_hit)

    # Dual-anchor status
    dual_status = "SINGLE"
    if secondary:
        dual_status = "CONFIRMED" if ("sec.gov" in (primary or secondary)) else "PENDING_SEC"
    else:
        # primaryがIRならPENDING_SEC
        if primary and ("investors.confluent.io" in primary) and rules["dual_anchor_policy"]["fallback_when_sec_blocked"]:
            dual_status = "PENDING_SEC"
    out["dual_anchor_status"] = dual_status

    # Final pass/fail
    lint_pass = all(pass_flags)
    auto["anchor_lint_pass"] = lint_pass
    auto["messages"] = msgs
    out["auto_checks"] = auto
    if not lint_pass:
        out["gap_reason"] = {
            "field": out.get("field", "anchor"),
            "status": "data_gap",
            "reason": "ANCHOR_INVALID",
            "ttl_days": 7
        }
    return out

def process_doc(doc: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, Any]:
    # Traverse known containers: docs, quotes, rpo_timeline, etc.
    def _lint_in(obj: Any):
        if isinstance(obj, dict):
            keys = list(obj.keys())
            # Heuristic: if it has any anchor/verbatim fields, lint it
            if any(k in obj for k in ("anchor", "primary_anchor", "secondary_anchor", "verbatim_≤25w")):
                return lint_anchor(obj, rules)
            for k in keys:
                obj[k] = _lint_in(obj[k])
        elif isinstance(obj, list):
            return [ _lint_in(x) for x in obj ]
        return obj
    return _lint_in(doc)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="ahf/config/anchorlint.yaml")
    args = ap.parse_args()
    try:
        import yaml
        with open(args.config, "r", encoding="utf-8") as f:
            rules = yaml.safe_load(f) or {}
        # merge defaults
        for k,v in DEFAULT_RULES.items():
            rules.setdefault(k, v)
    except Exception:
        rules = DEFAULT_RULES
    doc = json.load(sys.stdin)
    out = process_doc(doc, rules)
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
