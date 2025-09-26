# -*- coding: utf-8 -*-
"""CLI: parse inputs into AHF JSON fragments for α4/α5.
Usage: python -m cli.ahf_extract <ex99_text_file> <note_text_file> <xbrl_json>
"""
import json, sys
from mvp4.ex99_lite import parse_ex99_lite
from mvp4.rpo_finder import find_rpo_12m
from mvp4.gap_logger import gap
from mvp4.anchor_utils import DualAnchor


def main():
    ex99 = open(sys.argv[1], "r", encoding="utf-8").read() if len(sys.argv) > 1 else ""
    note = open(sys.argv[2], "r", encoding="utf-8").read() if len(sys.argv) > 2 else ""
    xbrl = json.load(open(sys.argv[3], "r", encoding="utf-8")) if len(sys.argv) > 3 else {}

    ex = parse_ex99_lite(ex99)

    rpo = find_rpo_12m(xbrl, note)
    if "rpo_12m_pct" not in rpo or rpo.get("rpo_12m_pct") is None:
        rpo["gap_reason"] = gap("rpo_12m_pct", "NOT_DISCLOSED", 30)

    # Example anchor build (caller supplies url, quote, pageno)
    da = DualAnchor.build(
        url="https://example.com/file.pdf#:~:text=Remaining%20backlog%20totaled",
        quote="Remaining backlog totaled $995,410; 58% within 12 months.",
        pageno=12,
    )

    out = {
        "alpha5_inputs": ex,
        "alpha4_rpo": rpo,
        "anchor": da.as_dict(),
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
