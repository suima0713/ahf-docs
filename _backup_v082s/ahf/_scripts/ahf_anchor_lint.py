#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AHF AnchorLint v1 + 二重アンカー
#:~:text= 必須、PDF等で不可→anchor_backupでPENDING_SEC
"""

import json
import os
import sys
import re
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import urlparse, parse_qs

def validate_anchor_format(anchor: str) -> Tuple[bool, str]:
    """
    #:~:text= アンカーフォーマットの検証
    """
    if not anchor:
        return False, "アンカーが空です"
    
    # #:~:text= パターンの検証
    if not anchor.startswith("#:~:text="):
        return False, "#:~:text= で始まっていません"
    
    # テキスト部分の抽出
    text_part = anchor[9:]  # "#:~:text=" を除去
    
    if not text_part:
        return False, "テキスト部分が空です"
    
    # テキスト長の検証（25語以内）
    words = text_part.split()
    if len(words) > 25:
        return False, f"テキストが25語を超えています: {len(words)}語"
    
    return True, "OK"

def extract_anchor_backup_info(url: str, anchor: str, content: str) -> Dict[str, Any]:
    """
    anchor_backup情報の抽出
    """
    backup_info = {
        "pageno": None,
        "quote": None,
        "hash": None
    }
    
    # ページ番号の抽出（URLから）
    if "page=" in url:
        page_match = re.search(r'page=(\d+)', url)
        if page_match:
            backup_info["pageno"] = int(page_match.group(1))
    
    # 引用文の抽出（アンカーから）
    if anchor.startswith("#:~:text="):
        quote = anchor[9:]
        backup_info["quote"] = quote
    
    # ハッシュの生成
    if content:
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        backup_info["hash"] = content_hash
    
    return backup_info

def determine_find_path(url: str, content: str) -> str:
    """
    find_pathの決定
    """
    if "sec.gov" in url:
        if "xbrl" in content.lower():
            return "xbrl"
        elif "note" in content.lower():
            return "note"
        elif "md&a" in content.lower() or "mda" in content.lower():
            return "md&a"
        else:
            return "fallback_text"
    else:
        return "manual"

def check_dual_anchor_status(primary_url: str, secondary_url: str, 
                           primary_anchor: str, secondary_anchor: str) -> str:
    """
    二重アンカーステータスの決定
    """
    # SEC一次、IR二次の優先順位
    if primary_url and "sec.gov" in primary_url and primary_anchor:
        return "CONFIRMED"
    elif secondary_url and "sec.gov" not in secondary_url and secondary_anchor:
        return "PENDING_SEC"
    elif primary_anchor or secondary_anchor:
        return "SINGLE"
    else:
        return "CONFIRMED"  # デフォルト

def validate_anchor_lint(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    AnchorLint v1の実行
    """
    result = {
        "anchor_lint_pass": False,
        "anchor_backup": {},
        "find_path": "",
        "gap_reason": "",
        "dual_anchor_status": "CONFIRMED",
        "messages": []
    }
    
    url = item.get("url", "")
    anchor = item.get("anchor", "")
    content = item.get("content", "")
    
    # アンカーフォーマットの検証
    anchor_valid, anchor_msg = validate_anchor_format(anchor)
    if not anchor_valid:
        result["gap_reason"] = "ANCHOR_INVALID"
        result["messages"].append(anchor_msg)
        return result
    
    # anchor_backup情報の抽出
    result["anchor_backup"] = extract_anchor_backup_info(url, anchor, content)
    
    # find_pathの決定
    result["find_path"] = determine_find_path(url, content)
    
    # 二重アンカーステータスの決定
    primary_url = item.get("primary_url", url)
    secondary_url = item.get("secondary_url", "")
    primary_anchor = item.get("primary_anchor", anchor)
    secondary_anchor = item.get("secondary_anchor", "")
    
    result["dual_anchor_status"] = check_dual_anchor_status(
        primary_url, secondary_url, primary_anchor, secondary_anchor
    )
    
    # 最終判定
    if anchor_valid and result["anchor_backup"]["quote"]:
        result["anchor_lint_pass"] = True
        result["messages"].append("AnchorLint合格")
    else:
        result["gap_reason"] = "ANCHOR_INVALID"
        result["messages"].append("AnchorLint不合格")
    
    return result

def process_anchor_lint(triage_file: str) -> Dict[str, Any]:
    """
    triage.jsonの全項目にAnchorLint v1を適用
    """
    with open(triage_file, 'r', encoding='utf-8') as f:
        triage_data = json.load(f)
    
    confirmed_items = triage_data.get("CONFIRMED", [])
    uncertain_items = triage_data.get("UNCERTAIN", [])
    
    # CONFIRMED項目のAnchorLint実行
    for item in confirmed_items:
        lint_result = validate_anchor_lint(item)
        
        # 結果を項目に追加
        item.update(lint_result)
    
    # UNCERTAIN項目のAnchorLint実行
    for item in uncertain_items:
        lint_result = validate_anchor_lint(item)
        item.update(lint_result)
    
    # 統計情報の生成
    total_items = len(confirmed_items) + len(uncertain_items)
    passed_items = sum(1 for item in confirmed_items + uncertain_items 
                      if item.get("anchor_lint_pass", False))
    
    stats = {
        "total_items": total_items,
        "passed_items": passed_items,
        "pass_rate": (passed_items / total_items * 100) if total_items > 0 else 0,
        "anchor_lint_pass": passed_items >= total_items * 0.98  # 98%以上で合格
    }
    
    return {
        "as_of": triage_data["as_of"],
        "anchor_lint_results": {
            "CONFIRMED": confirmed_items,
            "UNCERTAIN": uncertain_items
        },
        "stats": stats
    }

def main():
    if len(sys.argv) != 2:
        print("使用方法: python ahf_anchor_lint.py <triage.jsonのパス>")
        sys.exit(1)
    
    triage_file = sys.argv[1]
    
    if not os.path.exists(triage_file):
        print(f"[ERROR] triage.jsonが見つかりません: {triage_file}")
        sys.exit(1)
    
    try:
        results = process_anchor_lint(triage_file)
        
        # 結果出力
        print("=== AHF AnchorLint v1 Results ===")
        print(f"As of: {results['as_of']}")
        print()
        print(f"総項目数: {results['stats']['total_items']}")
        print(f"合格項目数: {results['stats']['passed_items']}")
        print(f"合格率: {results['stats']['pass_rate']:.1f}%")
        print(f"AnchorLint合格: {results['stats']['anchor_lint_pass']}")
        print()
        
        # 不合格項目の表示
        failed_items = []
        for item in results['anchor_lint_results']['CONFIRMED'] + results['anchor_lint_results']['UNCERTAIN']:
            if not item.get("anchor_lint_pass", False):
                failed_items.append({
                    "kpi": item.get("kpi", "Unknown"),
                    "gap_reason": item.get("gap_reason", "Unknown"),
                    "messages": item.get("messages", [])
                })
        
        if failed_items:
            print("不合格項目:")
            for item in failed_items:
                print(f"  - {item['kpi']}: {item['gap_reason']}")
                for msg in item['messages']:
                    print(f"    {msg}")
        
        # 結果をJSONファイルに保存
        output_file = triage_file.replace("triage.json", "anchor_lint.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"[INFO] 結果を保存しました: {output_file}")
        
    except Exception as e:
        print(f"[ERROR] 処理エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
