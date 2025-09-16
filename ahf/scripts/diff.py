#!/usr/bin/env python3
import json, sys

def key(rec):
    return (rec.get("kpi"), rec.get("asof"), rec.get("basis",""), rec.get("customer",""))

def to_map(lst):
    return { key(r): r for r in lst }

def main():
    if len(sys.argv) != 3:
        print("Usage: diff.py <previous.json> <latest.json>"); sys.exit(2)
    prev = json.load(open(sys.argv[1])); latest = json.load(open(sys.argv[2]))
    if isinstance(prev, dict): prev = [prev]
    if isinstance(latest, dict): latest = [latest]

    mp, ml = to_map(prev), to_map(latest)
    added   = [ml[k] for k in ml.keys() - mp.keys()]
    removed = [mp[k] for k in mp.keys() - ml.keys()]
    changed = []
    for k in ml.keys() & mp.keys():
        a,b = mp[k], ml[k]
        # compare meaningful fields
        fields = ["value","status","unit","tag","source","raw_verbatim"]
        if any(a.get(f)!=b.get(f) for f in fields):
            changed.append({"before": a, "after": b})

    print(json.dumps({"added": added, "changed": changed, "removed": removed}, indent=2))

if __name__ == "__main__":
    main()
