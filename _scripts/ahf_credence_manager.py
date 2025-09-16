#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AHF Credence Manager v0.3.2a
credence計算とTTL管理の最小実装
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any

def calculate_credence(source_type: str, aust_gaps: List[str]) -> int:
    """
    確度（credence）ルーブリック（最小）
    90：SEC本文 or 公式一次資料に準ずる明示（AUSTの1要素欠け）
    75：複数一次派生（複数トランスクリプト一致・一次と整合）
    50：一次と整合するがソースが二次のみに依存
    30：未検証の単発ソース／要反証待ち
    """
    base_credence = {
        "SEC": 90,
        "IR_official": 75,
        "transcript": 75,
        "counterparty": 50,
        "secondary": 30
    }
    
    credence = base_credence.get(source_type, 30)
    
    # AUST欠け要素による減点
    gap_penalty = len(aust_gaps) * 10
    credence = max(30, credence - gap_penalty)
    
    return credence

def check_ttl_expiry(triage_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    TTL消化チェック
    ttl_days超過のUNCERTAINは自動失効→status: expiredに更新
    """
    today = datetime.now().date()
    
    for item in triage_data.get("UNCERTAIN", []):
        if item.get("status") == "Lead":
            as_of = datetime.strptime(triage_data["as_of"], "%Y-%m-%d").date()
            ttl_days = item.get("ttl_days", 30)
            expiry_date = as_of + timedelta(days=ttl_days)
            
            if today > expiry_date:
                item["status"] = "expired"
                print(f"[INFO] TTL期限切れ: {item['kpi']} (期限: {expiry_date})")
    
    return triage_data

def promote_to_t1(triage_data: Dict[str, Any], kpi: str) -> Dict[str, Any]:
    """
    AUST満たすUNCERTAINをT1昇格
    """
    uncertain_items = triage_data.get("UNCERTAIN", [])
    confirmed_items = triage_data.get("CONFIRMED", [])
    
    # 該当するUNCERTAINアイテムを検索
    for i, item in enumerate(uncertain_items):
        if item["kpi"] == kpi and item.get("status") == "Lead":
            # AUSTチェック（aust_gapsが空または最小限）
            aust_gaps = item.get("aust_gaps", [])
            if len(aust_gaps) <= 1:  # 1要素まで欠けていれば昇格可能
                # CONFIRMEDに移動
                confirmed_item = {
                    "kpi": item["kpi"],
                    "value": item.get("value", 0),
                    "unit": item.get("unit", ""),
                    "asof": triage_data["as_of"],
                    "tag": "T1-core",
                    "url": item.get("url_index", "")
                }
                confirmed_items.append(confirmed_item)
                
                # UNCERTAINから削除
                uncertain_items.pop(i)
                
                print(f"[INFO] T1昇格: {kpi}")
                break
    
    triage_data["CONFIRMED"] = confirmed_items
    triage_data["UNCERTAIN"] = uncertain_items
    return triage_data

def process_triage_file(file_path: str) -> None:
    """
    triage.jsonファイルの処理
    """
    if not os.path.exists(file_path):
        print(f"[ERROR] ファイルが見つかりません: {file_path}")
        return
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            triage_data = json.load(f)
        
        # TTL消化チェック
        triage_data = check_ttl_expiry(triage_data)
        
        # UNCERTAINアイテムのcredence再計算
        for item in triage_data.get("UNCERTAIN", []):
            if item.get("status") == "Lead":
                source_type = item.get("source_type", "secondary")
                aust_gaps = item.get("aust_gaps", [])
                item["credence_pct"] = calculate_credence(source_type, aust_gaps)
        
        # ファイル保存
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(triage_data, f, ensure_ascii=False, indent=2)
        
        print(f"[INFO] 処理完了: {file_path}")
        
    except Exception as e:
        print(f"[ERROR] 処理エラー: {e}")

def main():
    if len(sys.argv) != 2:
        print("使用方法: python ahf_credence_manager.py <triage.jsonのパス>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    process_triage_file(file_path)

if __name__ == "__main__":
    main()

