#!/usr/bin/env python3
"""
AnchorLint v1 テストケース
主要ケース（PASS/FAIL/PENDING_SEC）をカバー
"""
import json
import sys
from pathlib import Path

# テスト対象モジュールのパスを追加
sys.path.insert(0, str(Path(__file__).parent.parent / "mvp4"))

from anchor_lint_v1 import lint_anchor, process_doc, DEFAULT_RULES

def test_pass_basic():
    """基本的なPASSケース"""
    fact = {
        "field": "rpo_total",
        "primary_anchor": "https://www.sec.gov/Archives/edgar/data/…/#:~:text=RPO%20was%20%241,162.3%20million",
        "verbatim_≤25w": "RPO was $1,162.3 million",
        "anchor_backup": {"pageno": 1, "quote": "RPO was $1,162.3 million", "hash": "abc123"},
        "find_path": "note"
    }
    out = lint_anchor(fact, DEFAULT_RULES)
    assert out["auto_checks"]["anchor_lint_pass"] is True
    assert out["dual_anchor_status"] in ("SINGLE", "CONFIRMED", "PENDING_SEC")
    print("✅ test_pass_basic: PASS")

def test_fail_placeholder_and_fragment():
    """プレースホルダとフラグメント不足のFAILケース"""
    fact = {
        "anchor": "https://investors.confluent.io/[41]",
        "verbatim_≤25w": "some words",
        "anchor_backup": {"pageno": 0, "quote": "some words", "hash": ""},
        "find_path": "note"
    }
    out = lint_anchor(fact, DEFAULT_RULES)
    assert out["auto_checks"]["anchor_lint_pass"] is False
    assert out["gap_reason"]["reason"] == "ANCHOR_INVALID"
    print("✅ test_fail_placeholder_and_fragment: PASS")

def test_pending_sec_dual():
    """IR primaryのPENDING_SECケース"""
    fact = {
        "primary_anchor": "https://investors.confluent.io/…#:~:text=Total%20revenue",
        "secondary_anchor": None,
        "verbatim_≤25w": "Total revenue $282,285",
        "anchor_backup": {"pageno": 1, "quote": "Total revenue $282,285", "hash": "def456"},
        "find_path": "statement"
    }
    out = lint_anchor(fact, DEFAULT_RULES)
    assert out["dual_anchor_status"] == "PENDING_SEC"
    print("✅ test_pending_sec_dual: PASS")

def test_confirmed_dual_anchor():
    """SEC + IR のCONFIRMEDケース"""
    fact = {
        "primary_anchor": "https://www.sec.gov/Archives/edgar/data/…/#:~:text=RPO%20total",
        "secondary_anchor": "https://investors.confluent.io/…#:~:text=RPO%20total",
        "verbatim_≤25w": "RPO total $1,200 million",
        "anchor_backup": {"pageno": 1, "quote": "RPO total $1,200 million", "hash": "ghi789"},
        "find_path": "note"
    }
    out = lint_anchor(fact, DEFAULT_RULES)
    assert out["dual_anchor_status"] == "CONFIRMED"
    print("✅ test_confirmed_dual_anchor: PASS")

def test_verbatim_too_long():
    """逐語が25語を超えるFAILケース"""
    fact = {
        "anchor": "https://www.sec.gov/…#:~:text=long%20sentence",
        "verbatim_≤25w": "This is a very long sentence that exceeds twenty five words and should fail the lint check because it is too verbose",
        "anchor_backup": {"pageno": 1, "quote": "long quote", "hash": "jkl012"},
        "find_path": "note"
    }
    out = lint_anchor(fact, DEFAULT_RULES)
    assert out["auto_checks"]["anchor_lint_pass"] is False
    assert any("too long" in msg for msg in out["auto_checks"]["messages"])
    print("✅ test_verbatim_too_long: PASS")

def test_missing_anchor_backup():
    """anchor_backup不完全のFAILケース"""
    fact = {
        "anchor": "https://www.sec.gov/…#:~:text=test",
        "verbatim_≤25w": "test quote",
        "anchor_backup": {"pageno": 1},  # quote, hash不足
        "find_path": "note"
    }
    out = lint_anchor(fact, DEFAULT_RULES)
    assert out["auto_checks"]["anchor_lint_pass"] is False
    assert any("incomplete" in msg for msg in out["auto_checks"]["messages"])
    print("✅ test_missing_anchor_backup: PASS")

def test_invalid_find_path():
    """find_pathが無効なFAILケース"""
    fact = {
        "anchor": "https://www.sec.gov/…#:~:text=test",
        "verbatim_≤25w": "test quote",
        "anchor_backup": {"pageno": 1, "quote": "test quote", "hash": "mno345"},
        "find_path": "invalid_path"
    }
    out = lint_anchor(fact, DEFAULT_RULES)
    assert out["auto_checks"]["anchor_lint_pass"] is False
    assert any("invalid or missing" in msg for msg in out["auto_checks"]["messages"])
    print("✅ test_invalid_find_path: PASS")

def test_process_doc_traversal():
    """process_docの文書走査テスト"""
    doc = {
        "facts": [
            {
                "field": "rpo_total",
                "anchor": "https://www.sec.gov/…#:~:text=RPO%20total",
                "verbatim_≤25w": "RPO total $1,200 million",
                "anchor_backup": {"pageno": 1, "quote": "RPO total $1,200 million", "hash": "pqr678"},
                "find_path": "note"
            }
        ],
        "metadata": {"version": "1.0"}
    }
    out = process_doc(doc, DEFAULT_RULES)
    assert out["facts"][0]["auto_checks"]["anchor_lint_pass"] is True
    print("✅ test_process_doc_traversal: PASS")

def run_all_tests():
    """全テスト実行"""
    print("🧪 AnchorLint v1 テスト実行開始")
    print("=" * 50)
    
    test_functions = [
        test_pass_basic,
        test_fail_placeholder_and_fragment,
        test_pending_sec_dual,
        test_confirmed_dual_anchor,
        test_verbatim_too_long,
        test_missing_anchor_backup,
        test_invalid_find_path,
        test_process_doc_traversal
    ]
    
    passed = 0
    failed = 0
    
    for test_func in test_functions:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"❌ {test_func.__name__}: FAIL - {e}")
            failed += 1
    
    print("=" * 50)
    print(f"📊 テスト結果: {passed} PASS, {failed} FAIL")
    
    if failed == 0:
        print("🎉 全テスト成功！")
        return True
    else:
        print("💥 テスト失敗あり")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
