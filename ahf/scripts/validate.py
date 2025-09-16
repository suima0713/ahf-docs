#!/usr/bin/env python3
import json, sys, re, urllib.parse, pathlib
from jsonschema import validate, Draft202012Validator

SCHEMA = json.load(open(pathlib.Path(__file__).parent.parent/"schemas"/"ahf_record.schema.json"))

ALLOWED_UNITS = {"USD","percent","count","text","date"}
T1CORE_DOMAIN = "www.sec.gov"

def word_count(s:str)->int:
    return 0 if not s else len(re.findall(r"\b\w+\b", s))

def is_sec(url:str)->bool:
    try:
        netloc = urllib.parse.urlparse(url).netloc.lower()
        return netloc.endswith("sec.gov") or netloc.endswith("secdatabase.com")
    except Exception:
        return False

def normalize(rec):
    # map legacy url -> source.url
    if "source" not in rec and "url" in rec:
        rec["source"] = {"url": rec["url"], "section": rec.get("section","")}
    return rec

def logical_checks(rec, idx, errors):
    # AUST: raw_verbatim <= 40 words when present
    rv = rec.get("raw_verbatim","")
    if rv and word_count(rv) > 40:
        errors.append((idx, "raw_verbatim exceeds 40 words"))

    # Units
    if "value" in rec and rec.get("unit") not in ALLOWED_UNITS:
        errors.append((idx, f"unit '{rec.get('unit')}' not in {sorted(ALLOWED_UNITS)}"))

    # T1-core must be sec.gov
    if rec.get("tag") == "T1-core":
        url = rec.get("source",{}).get("url","")
        if not is_sec(url):
            errors.append((idx, f"T1-core requires sec.gov URL, got: {url}"))

    # status/value exclusivity is enforced by schema, but double-check:
    if "status" in rec and "value" in rec:
        errors.append((idx, "record must not contain both 'value' and 'status'"))

    # basis/period hints
    if "revenue_concentration" in rec.get("kpi","") and not rec.get("basis"):
        errors.append((idx, "revenue_concentration* requires 'basis' (total_revenue|fees_net)"))

def main():
    if len(sys.argv) != 2:
        print("Usage: validate.py <json-file>"); sys.exit(2)
    data = json.load(open(sys.argv[1]))
    if isinstance(data, dict): data = [data]
    errors = []

    v = Draft202012Validator(SCHEMA)
    seen = set()
    for i, raw in enumerate(data):
        rec = normalize(raw)
        for e in sorted(v.iter_errors(rec), key=str):
            errors.append((i, e.message))
        logical_checks(rec, i, errors)

        # Duplicate key guard (kpi+asof+basis+customer)
        key = (rec.get("kpi"), rec.get("asof"), rec.get("basis"), rec.get("customer"))
        if key in seen:
            errors.append((i, f"duplicate key {key}"))
        else:
            seen.add(key)

    if errors:
        print("AHF validation FAILED:")
        for i,msg in errors:
            print(f"  [#{i}] {msg}")
        sys.exit(1)
    print("AHF validation OK ✔")

if __name__ == "__main__":
    main()
