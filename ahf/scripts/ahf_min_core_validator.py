#!/usr/bin/env python3
import json, sys, re, urllib.parse, pathlib
from jsonschema import validate, Draft202012Validator

SCHEMA = json.load(open(pathlib.Path(__file__).parent.parent/"schemas"/"ahf_min_core.schema.json"))

# 独立ソース正規化辞書（重複加点防止）
SOURCE_NORMALIZATION = {
    "abs15g_ex99": ["abs15g_ex-99.1", "ex99-1", "exhibit 99.1"],
    "trustee_report": ["trustee-report", "trustee_filing"],
    "8k_ex99": ["8-k_ex-99.1", "8k_exhibit_99.1"],
    "10q_note2": ["10-q_note_2", "10q_note2"],
    "10q_note4": ["10-q_note_4", "10q_note4"]
}

def detect_basis(quote, section_title=""):
    """分母判定ロジック"""
    text = (quote + " " + section_title).lower()
    
    if re.search(r"fees,?\s*net|platform\s+and\s+referral\s+fees", text):
        return "fees_net"
    elif re.search(r"total\s+revenue", text):
        return "total"
    else:
        return None

def detect_entity_type(quote):
    """顧客の意味付け判定"""
    if re.search(r"bank\s+partner", quote.lower()):
        return "bank_partner"
    elif re.search(r"significant\s+customers|customer", quote.lower()):
        return "customer"
    else:
        return None

def detect_144a_regs(quote):
    """144A/Reg S示唆検出"""
    return bool(re.search(r"rule\s+144a|regulation\s+s", quote.lower()))

def detect_no_above_10pct(quote):
    """No >10%表現検出"""
    return bool(re.search(r"no\s+customer.*accounted\s+for\s+more\s+than\s+10%", quote.lower()))

def normalize_source(source_key):
    """独立ソース正規化"""
    for canonical, aliases in SOURCE_NORMALIZATION.items():
        if source_key.lower() in [alias.lower() for alias in aliases]:
            return canonical
    return source_key

def validate_kpi_naming(rec, idx, errors):
    """KPI命名と分母の整合性チェック"""
    kpi = rec.get("kpi", "")
    basis = rec.get("basis")
    quote = rec.get("quote", "")
    
    # 分母判定
    detected_basis = detect_basis(quote)
    
    # KPI命名チェック
    if "_total_" in kpi and detected_basis == "fees_net":
        errors.append((idx, f"KPI '{kpi}' uses _total_ but quote contains 'fees, net'"))
    elif "_fees_net_" in kpi and detected_basis == "total":
        errors.append((idx, f"KPI '{kpi}' uses _fees_net_ but quote contains 'total revenue'"))
    
    # basis設定の推奨
    if detected_basis and not basis:
        errors.append((idx, f"Detected basis '{detected_basis}' but not set in record"))

def validate_144a_handling(rec, idx, errors):
    """144A/Reg S取り扱いチェック"""
    quote = rec.get("quote", "")
    kpi = rec.get("kpi", "")
    
    if detect_144a_regs(quote):
        # ABS数値系は not_expected_on_edgar_if_144a に統一
        if any(abs_kpi in kpi for abs_kpi in ["abs_transaction_size", "abs_class_a_size", "abs_closing_date"]):
            if rec.get("status") != "not_expected_on_edgar_if_144a":
                errors.append((idx, f"ABS KPI '{kpi}' should have status 'not_expected_on_edgar_if_144a' for 144A/Reg S"))

def validate_no_above_10pct(rec, idx, errors):
    """No >10%表現の取り扱いチェック"""
    quote = rec.get("quote", "")
    value = rec.get("value")
    
    if detect_no_above_10pct(quote):
        if value is not None and value != 0:
            errors.append((idx, f"'No >10%' quote should have value=null, not {value}"))
        if not rec.get("note") or "none_above_10pct" not in rec.get("note", ""):
            errors.append((idx, f"'No >10%' quote should have note='none_above_10pct'"))

def validate_aust_metadata(rec, idx, errors):
    """AUSTメタの軽量バリデーション"""
    # facts.md 行チェック
    if "quote" in rec:
        quote = rec["quote"]
        if len(quote) > 200:
            errors.append((idx, "quote exceeds 200 characters"))
        
        # 必須フィールドチェック
        required_fields = ["asof", "unit", "section", "url"]
        for field in required_fields:
            if not rec.get(field):
                errors.append((idx, f"Missing required field '{field}' for facts.md line"))
    
    # triage.CONFIRMED チェック
    if rec.get("tag") in ["T1-core", "T1-adj"]:
        required_fields = ["kpi", "unit", "asof", "tag", "url"]
        for field in required_fields:
            if not rec.get(field):
                errors.append((idx, f"Missing required field '{field}' for CONFIRMED record"))
        # value は null も許可
        if "value" not in rec:
            errors.append((idx, f"Missing 'value' field for CONFIRMED record (null is allowed)"))
    
    # triage.UNCERTAIN チェック
    if rec.get("status"):
        required_fields = ["kpi", "status", "url_index", "ttl_days"]
        for field in required_fields:
            if not rec.get(field):
                errors.append((idx, f"Missing required field '{field}' for UNCERTAIN record"))

def main():
    if len(sys.argv) != 2:
        print("Usage: ahf_min_core_validator.py <json-file>"); sys.exit(2)
    
    data = json.load(open(sys.argv[1]))
    if isinstance(data, dict): data = [data]
    errors = []

    v = Draft202012Validator(SCHEMA)
    seen = set()
    
    for i, raw in enumerate(data):
        # スキーマ検証
        for e in sorted(v.iter_errors(raw), key=str):
            errors.append((i, e.message))
        
        # カスタム検証
        validate_kpi_naming(raw, i, errors)
        validate_144a_handling(raw, i, errors)
        validate_no_above_10pct(raw, i, errors)
        validate_aust_metadata(raw, i, errors)

        # 重複キーガード
        key = (raw.get("kpi"), raw.get("asof"))
        if key in seen:
            errors.append((i, f"duplicate key {key}"))
        else:
            seen.add(key)

    if errors:
        print("AHF-Min Core validation FAILED:")
        for i,msg in errors:
            print(f"  [#{i}] {msg}")
        sys.exit(1)
    print("AHF-Min Core validation OK ✔")

if __name__ == "__main__":
    main()
