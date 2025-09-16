#!/usr/bin/env python3
import json, sys, re, urllib.parse, pathlib
from jsonschema import validate, Draft202012Validator

SCHEMA = json.load(open(pathlib.Path(__file__).parent.parent/"schemas"/"ahf_v2_edge_overlay.schema.json"))

# 許容ソース定義
ALLOWED_SOURCES = {
    "rating_agency": ["KBRA", "S&P", "Moody's", "Fitch", "DBRS"],
    "issuer_pr": ["BusinessWire", "GlobeNewswire", "PR Newswire", "Marketwired"],
    "regulator": ["SEC", "FDIC", "OCC", "Federal Reserve", "CFPB"]
}

# 禁止ソース
FORBIDDEN_SOURCES = ["Twitter", "LinkedIn", "Facebook", "Reddit", "SeekingAlpha", "Yahoo Finance", "MarketWatch"]

# P対象トピック
P_TARGET_TOPICS = ["abs", "144a", "forward_flow", "partnership", "funding", "securitization"]

def calculate_p_confidence(sources):
    """P信頼度計算"""
    if not sources:
        return 0.0
    
    # 単一ソース = 0.4
    if len(sources) == 1:
        p_confidence_raw = 0.4
    # 独立2本以上かつ整合 = 0.7
    elif len(sources) >= 2:
        # 異なるタイプのソースがあるかチェック
        source_types = set(src.get("type") for src in sources)
        if len(source_types) > 1:
            p_confidence_raw = 0.7
        else:
            p_confidence_raw = 0.4
    else:
        p_confidence_raw = 0.0
    
    # p_confidence = 0.7 * p_confidence_raw（最大0.49にクリップ）
    p_confidence = min(0.7 * p_confidence_raw, 0.49)
    return round(p_confidence, 2)

def validate_source_legitimacy(source, idx, errors):
    """ソース正当性検証"""
    source_type = source.get("type")
    source_name = source.get("name", "")
    
    # 許容ソースチェック
    if source_type in ALLOWED_SOURCES:
        allowed_names = ALLOWED_SOURCES[source_type]
        if not any(name.lower() in source_name.lower() for name in allowed_names):
            errors.append((idx, f"Source name '{source_name}' not in allowed {source_type} sources: {allowed_names}"))
    
    # 禁止ソースチェック
    for forbidden in FORBIDDEN_SOURCES:
        if forbidden.lower() in source_name.lower():
            errors.append((idx, f"Forbidden source detected: '{source_name}' contains '{forbidden}'"))
    
    # URL検証
    url = source.get("url", "")
    if url and not url.startswith(("http://", "https://")):
        errors.append((idx, f"Invalid URL format: '{url}'"))

def validate_p_topic_relevance(kpi, idx, errors):
    """P対象トピック関連性チェック"""
    kpi_lower = kpi.lower()
    is_relevant = any(topic in kpi_lower for topic in P_TARGET_TOPICS)
    
    if not is_relevant:
        errors.append((idx, f"KPI '{kpi}' not in P target topics: {P_TARGET_TOPICS}. P should only be used for ABS/144A/Forward-Flow/Partnership/Funding topics."))

def validate_144a_regs_note(note, idx, errors):
    """144A/Reg S示唆のnote明記チェック"""
    if note and ("144a" in note.lower() or "reg s" in note.lower() or "regulation s" in note.lower()):
        if "edgar非開示" not in note.lower() and "non-disclosure" not in note.lower():
            errors.append((idx, "144A/Reg S topics should include note about EDGAR non-disclosure expectation"))

def validate_provisional_rules(rec, idx, errors):
    """PROVISIONAL専用ルール検証"""
    kpi = rec.get("kpi", "")
    note = rec.get("note", "")
    sources = rec.get("sources", [])
    
    # P対象トピック関連性
    validate_p_topic_relevance(kpi, idx, errors)
    
    # 144A/Reg S示唆のnote明記
    validate_144a_regs_note(note, idx, errors)
    
    # 必須note文言チェック
    if "provisional" not in note.lower() or "non-edgar" not in note.lower():
        errors.append((idx, "Note must contain 'Provisional (non-EDGAR)' to indicate P status"))
    
    if "do not overwrite t1" not in note.lower():
        errors.append((idx, "Note must contain 'Do not overwrite T1' warning"))
    
    # ソース検証
    for i, source in enumerate(sources):
        validate_source_legitimacy(source, f"{idx}.{i}", errors)
    
    # 信頼度計算と検証
    calculated_confidence = calculate_p_confidence(sources)
    stated_confidence = rec.get("p_confidence", 0.0)
    
    if abs(calculated_confidence - stated_confidence) > 0.01:
        errors.append((idx, f"p_confidence mismatch: stated {stated_confidence}, calculated {calculated_confidence}"))

def main():
    if len(sys.argv) != 2:
        print("Usage: ahf_v2_provisional_validator.py <json-file>"); sys.exit(2)
    
    data = json.load(open(sys.argv[1]))
    if isinstance(data, dict): data = [data]
    errors = []

    v = Draft202012Validator(SCHEMA)
    seen = set()
    
    for i, raw in enumerate(data):
        # スキーマ検証
        for e in sorted(v.iter_errors(raw), key=str):
            errors.append((i, e.message))
        
        # PROVISIONAL専用ルール検証
        validate_provisional_rules(raw, i, errors)

        # 重複キーガード
        key = (raw.get("kpi"), raw.get("asof"))
        if key in seen:
            errors.append((i, f"duplicate key {key}"))
        else:
            seen.add(key)

    if errors:
        print("AHF v2 PROVISIONAL validation FAILED:")
        for i,msg in errors:
            print(f"  [#{i}] {msg}")
        sys.exit(1)
    print("AHF v2 PROVISIONAL validation OK ✔")

if __name__ == "__main__":
    main()
