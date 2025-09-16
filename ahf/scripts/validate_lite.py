#!/usr/bin/env python3
import json, sys, re, urllib.parse, pathlib
from jsonschema import validate, Draft202012Validator

SCHEMA = json.load(open(pathlib.Path(__file__).parent.parent/"schemas"/"ahf_lite.schema.json"))

ALLOWED_UNITS = {"USD","percent","count","text","date"}
ALLOWED_STATUS = {"C","P","W"}

def word_count(s:str)->int:
    return 0 if not s else len(re.findall(r"\b\w+\b", s))

def is_sec(url:str)->bool:
    try:
        netloc = urllib.parse.urlparse(url).netloc.lower()
        return netloc.endswith("sec.gov") or netloc.endswith("secdatabase.com")
    except Exception:
        return False

def logical_checks(rec, idx, errors):
    # AHF-Lite: claim <= 200 chars (simplified from 40 words)
    claim = rec.get("claim","")
    if claim and len(claim) > 200:
        errors.append((idx, "claim exceeds 200 characters"))

    # Status validation
    status = rec.get("status")
    if status not in ALLOWED_STATUS:
        errors.append((idx, f"status '{status}' not in {sorted(ALLOWED_STATUS)}"))

    # C status must have value and unit
    if status == "C":
        if "value" not in rec:
            errors.append((idx, "C status requires 'value' field"))
        if "unit" not in rec:
            errors.append((idx, "C status requires 'unit' field"))
        if rec.get("unit") not in ALLOWED_UNITS:
            errors.append((idx, f"unit '{rec.get('unit')}' not in {sorted(ALLOWED_UNITS)}"))

    # P/W status must have ttl_days and trigger_if_false
    if status in ["P", "W"]:
        if "ttl_days" not in rec:
            errors.append((idx, f"{status} status requires 'ttl_days' field"))
        if "trigger_if_false" not in rec:
            errors.append((idx, f"{status} status requires 'trigger_if_false' field"))
        if rec.get("ttl_days", 0) <= 0 or rec.get("ttl_days", 0) > 365:
            errors.append((idx, "ttl_days must be between 1 and 365"))

    # C status should prefer sec.gov URLs
    if status == "C" and "url" in rec:
        url = rec["url"]
        if not is_sec(url) and not url.startswith("<"):
            errors.append((idx, f"C status should use sec.gov URLs, got: {url}"))

def main():
    if len(sys.argv) != 2:
        print("Usage: validate_lite.py <json-file>"); sys.exit(2)
    data = json.load(open(sys.argv[1]))
    if isinstance(data, dict): data = [data]
    errors = []

    v = Draft202012Validator(SCHEMA)
    seen = set()
    for i, raw in enumerate(data):
        for e in sorted(v.iter_errors(raw), key=str):
            errors.append((i, e.message))
        logical_checks(raw, i, errors)

        # Duplicate key guard (kpi+asof)
        key = (raw.get("kpi"), raw.get("asof"))
        if key in seen:
            errors.append((i, f"duplicate key {key}"))
        else:
            seen.add(key)

    if errors:
        print("AHF-Lite validation FAILED:")
        for i,msg in errors:
            print(f"  [#{i}] {msg}")
        sys.exit(1)
    print("AHF-Lite validation OK ✔")

if __name__ == "__main__":
    main()
