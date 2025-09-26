# AHF MVP-4 (Minimal Implementation) — Operator Notes

**Scope**: Drop-in utilities for AHF v0.6.0 to improve *recall without losing information* while keeping T1-only rigor.

## Modules Overview

### 1) Dual-Anchor + Snippet Hash (robust citations)
- **Purpose**: Always store `anchor_backup` (pageno, ≤25w quote, sha1)
- **Usage**: `DualAnchor.build(url, quote, pageno)` → `as_dict()`
- **Integration**: Attach to any T1 discovery for robust citation

### 2) 12M Finder (XBRL→text fallback) for α4
- **Purpose**: Find RPO total and 12M% using XBRL first, fallback to text phrases
- **Usage**: `find_rpo_12m(xbrl_dict, note_text)` → sets `find_path` to one of `xbrl|fallback_text|manual`
- **Integration**: α4 compute coverage months only when `rpo_total_$k` and `rpo_12m_pct` are present

### 3) Ex.99.1 Lite Parser (Rev, NG-GM%, Adj. EBITDA) for α5
- **Purpose**: Works on raw plain text extracted from Ex.99.1/IR releases
- **Usage**: `parse_ex99_lite(text)` → returns `rev_$k`, `ng_gm_pct`, `adj_ebitda_$k`
- **Integration**: α5 compute `OpEx = Rev × NG-GM − Adj. EBITDA` immediately once inputs are present

### 4) Gap-Reason Logger (standardized data_gap reasons)
- **Purpose**: Attach to any `data_gap` field
- **Usage**: `gap(field, reason, ttl_days)` → standardized gap reason object
- **Integration**: Attach to fields that cannot be found or parsed

## Pipeline Integration

### α4 (RPO Coverage Analysis)
```python
rpo = find_rpo_12m(xbrl_dict, note_text)
if "rpo_12m_pct" not in rpo or rpo.get("rpo_12m_pct") is None:
    rpo["gap_reason"] = gap("rpo_12m_pct", "NOT_DISCLOSED", 30)
```

### α5 (Operating Expense Analysis)
```python
ex = parse_ex99_lite(ex99_text)
# Compute OpEx = Rev × NG-GM − Adj. EBITDA when all inputs present
```

### Dual-Anchor Integration
```python
da = DualAnchor.build(url, quote, pageno)
anchor_data = da.as_dict()
# Attach to T1 discoveries for robust citation
```

## File Structure

```
ahf/
├─ mvp4/
│  ├─ anchor_utils.py      # DualAnchor class
│  ├─ rpo_finder.py        # 12M RPO detection
│  ├─ ex99_lite.py         # Ex.99.1 parser
│  ├─ gap_logger.py        # Gap reason logger
│  ├─ patterns.py          # Centralized regex patterns
│  └─ __init__.py
├─ cli/
│  └─ ahf_extract.py       # Orchestration demo
├─ schemas/
│  ├─ outputs.schema.json  # MVP-4 field extensions
│  └─ reasons.schema.json  # Gap reason schema
└─ tests/
    ├─ test_ex99_lite.py
    ├─ test_rpo_finder.py
    ├─ test_anchor_utils.py
    └─ test_gap_logger.py
```

## Usage Examples

### CLI Orchestration
```bash
python -m ahf.cli.ahf_extract ex99_text.txt note_text.txt xbrl_data.json
```

### Programmatic Usage
```python
from ahf.mvp4 import parse_ex99_lite, find_rpo_12m, DualAnchor, gap

# Parse Ex.99.1 document
ex99_data = parse_ex99_lite(ex99_text)

# Find RPO data
rpo_data = find_rpo_12m(xbrl_dict, note_text)

# Create robust anchor
anchor = DualAnchor.build(url, quote, pageno)

# Log data gaps
gap_info = gap("field_name", "NOT_DISCLOSED", 30)
```

## Non-Goals

- Full XBRL parser, PDF OCR, or vendor-specific scrapers
- Network calls or external dependencies
- Complex document structure parsing
- Full SEC EDGAR integration

These can be added later behind the same interfaces.

## Testing

Run unit tests:
```bash
cd ahf
python -m pytest tests/ -v
```

Or run individual test files:
```bash
python tests/test_ex99_lite.py
python tests/test_rpo_finder.py
python tests/test_anchor_utils.py
python tests/test_gap_logger.py
```

## Integration Notes

- **No breaking changes**: All extensions are additive
- **T1 rigor maintained**: Only processes explicitly provided text/data
- **Fallback strategy**: XBRL → text → manual for RPO detection
- **Robust citations**: Dual-anchor system with hash verification
- **Standardized gaps**: Consistent data_gap reasons across pipeline
