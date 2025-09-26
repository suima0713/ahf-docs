#!/usr/bin/env python3
"""
AHF Credence Calculator - ミニ運用ルール対応
T1厳守のまま仮置き（U）をcredence_pctで重み付けしてマトリクス表示に反映

Usage:
    python3 ahf/_scripts/ahf_credence_calculator.py ahf/tickers/<TICKER>/current/
"""

import json
import sys
import os
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

def load_triage_data(ticker_path: str) -> Dict[str, Any]:
    """triage.jsonを読み込み"""
    triage_file = os.path.join(ticker_path, "triage.json")
    if not os.path.exists(triage_file):
        raise FileNotFoundError(f"triage.json not found: {triage_file}")
    
    try:
        with open(triage_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON parse error in {triage_file}: {e}")
    except Exception as e:
        raise ValueError(f"Error reading {triage_file}: {e}")

def load_impact_cards(ticker_path: str) -> List[Dict[str, Any]]:
    """impact_cards.jsonを読み込み"""
    cards_file = os.path.join(ticker_path, "impact_cards.json")
    if not os.path.exists(cards_file):
        return []
    
    with open(cards_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # オブジェクト構造の場合はcards配列を返す
    if isinstance(data, dict) and "cards" in data:
        return data["cards"]
    # 配列構造の場合はそのまま返す
    elif isinstance(data, list):
        return data
    else:
        return []

def extract_credence_data(triage_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """UNCERTAINからcredence_pct付きエントリを抽出"""
    credence_data = {}
    
    for item in triage_data.get("UNCERTAIN", []):
        if "credence_pct" in item:
            kpi = item["kpi"]
            credence_data[kpi] = {
                "claim": item.get("claim", ""),
                "credence_pct": item["credence_pct"],
                "status": item.get("status", "Lead"),
                "url_index": item.get("url_index", ""),
                "aust_gaps": item.get("aust_gaps", []),
                "ttl_days": item.get("ttl_days", 30),
                "note": item.get("note", "")
            }
    
    return credence_data

def calculate_shadow_values(confirmed_data: List[Dict[str, Any]], 
                          credence_data: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """T1実線 + U点線レンジの影表示計算"""
    shadow_values = {}
    
    # T1確定値をベースラインとして設定
    for item in confirmed_data:
        kpi = item["kpi"]
        
        # valueフィールドがない場合はスキップ
        if "value" not in item:
            continue
            
        shadow_values[kpi] = {
            "t1_value": item["value"],
            "t1_unit": item.get("unit", "unknown"),
            "t1_asof": item.get("asof", "unknown"),
            "t1_tag": item.get("tag", item.get("tier", "unknown")),
            "shadow_range": None,
            "credence_contributions": []
        }
    
    # U（仮置き）の重み付け寄与を計算
    for kpi, credence_info in credence_data.items():
        credence_pct = credence_info["credence_pct"]
        claim = credence_info["claim"]
        
        # 数値抽出（簡易版）
        numeric_value = extract_numeric_value(claim)
        if numeric_value is not None:
            weighted_contribution = numeric_value * (credence_pct / 100)
            
            # 関連するT1 KPIに寄与を追加
            related_kpis = find_related_kpis(kpi, shadow_values.keys())
            for related_kpi in related_kpis:
                if related_kpi in shadow_values:
                    shadow_values[related_kpi]["credence_contributions"].append({
                        "kpi": kpi,
                        "claim": claim,
                        "credence_pct": credence_pct,
                        "weighted_value": weighted_contribution
                    })
    
    # 影レンジを計算
    for kpi, data in shadow_values.items():
        if data["credence_contributions"]:
            total_contribution = sum(c["weighted_value"] for c in data["credence_contributions"])
            t1_value = data["t1_value"]
            
            # 数値型チェック
            if isinstance(t1_value, (int, float)):
                shadow_values[kpi]["shadow_range"] = {
                    "low": t1_value,
                    "high": t1_value + total_contribution,
                    "credence_contribution": total_contribution
                }
    
    return shadow_values

def extract_numeric_value(claim: str) -> Optional[float]:
    """クレーム文字列から数値を抽出（簡易版）"""
    import re
    
    # $131m/yr, 15-20%, 131000000等のパターンを抽出
    patterns = [
        r'\$(\d+(?:\.\d+)?)m',  # $131m
        r'(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)%',  # 15-20%
        r'(\d+(?:\.\d+)?)%',  # 15%
        r'(\d+(?:\.\d+)?)',  # 131000000
    ]
    
    for pattern in patterns:
        match = re.search(pattern, claim)
        if match:
            if '-' in pattern:  # レンジの場合
                return (float(match.group(1)) + float(match.group(2))) / 2
            else:
                return float(match.group(1))
    
    return None

def find_related_kpis(credence_kpi: str, t1_kpis: List[str]) -> List[str]:
    """credence KPIに関連するT1 KPIを特定"""
    related = []
    
    # キーワードベースの関連性判定
    keywords = {
        "fy26": ["fy26", "guidance", "revenue"],
        "samsung": ["samsung", "recurring", "rpo"],
        "arr": ["arr", "revenue", "guidance"],
        "floor": ["rpo", "contracted", "revenue"]
    }
    
    for keyword, related_terms in keywords.items():
        if keyword in credence_kpi.lower():
            for t1_kpi in t1_kpis:
                if any(term in t1_kpi.lower() for term in related_terms):
                    related.append(t1_kpi)
    
    return related

def generate_matrix_display(shadow_values: Dict[str, Dict[str, Any]]) -> str:
    """マトリクス表示用の出力を生成"""
    output = []
    output.append("=== AHF マトリクス表示（T1実線 + U点線レンジ） ===\n")
    
    for kpi, data in shadow_values.items():
        if data["shadow_range"]:
            t1_value = data["t1_value"]
            shadow_low = data["shadow_range"]["low"]
            shadow_high = data["shadow_range"]["high"]
            contribution = data["shadow_range"]["credence_contribution"]
            
            output.append(f"【{kpi}】")
            output.append(f"  T1実線: {t1_value} {data['t1_unit']} (asof: {data['t1_asof']})")
            output.append(f"  U点線レンジ: {shadow_low} ～ {shadow_high} {data['t1_unit']}")
            output.append(f"  影寄与: +{contribution:.1f} {data['t1_unit']} (確度込み)")
            
            if data["credence_contributions"]:
                output.append("  寄与元:")
                for contrib in data["credence_contributions"]:
                    output.append(f"    - {contrib['kpi']}: {contrib['claim']} (確度{contrib['credence_pct']}%)")
            
            output.append("")
    
    return "\n".join(output)

def update_impact_cards_with_shadow(impact_cards: List[Dict[str, Any]], 
                                  shadow_values: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """impact_cards.jsonを影表示対応で更新"""
    updated_cards = []
    
    for card in impact_cards:
        updated_card = card.copy()
        
        # 入力KPIに影表示があるかチェック
        shadow_inputs = []
        for input_kpi in card.get("inputs", []):
            if input_kpi in shadow_values and shadow_values[input_kpi]["shadow_range"]:
                shadow_inputs.append(input_kpi)
        
        if shadow_inputs:
            # 影表示用の計算式を追加
            original_expr = card.get("expr", "")
            updated_card["shadow_expr"] = f"{original_expr} + shadow_contributions"
            updated_card["shadow_inputs"] = shadow_inputs
            updated_card["shadow_note"] = "T1+U重み付け計算対応"
        
        updated_cards.append(updated_card)
    
    return updated_cards

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 ahf_credence_calculator.py <ticker_path>")
        sys.exit(1)
    
    ticker_path = sys.argv[1]
    
    try:
        print(f"Processing ticker path: {ticker_path}")
        
        # データ読み込み
        print("Loading triage data...")
        triage_data = load_triage_data(ticker_path)
        print(f"Triage data loaded: {len(triage_data.get('CONFIRMED', []))} CONFIRMED items")
        
        print("Loading impact cards...")
        impact_cards = load_impact_cards(ticker_path)
        print(f"Impact cards loaded: {len(impact_cards)} cards")
        
        # credenceデータ抽出
        print("Extracting credence data...")
        credence_data = extract_credence_data(triage_data)
        print(f"Credence data extracted: {len(credence_data)} items")
        
        if not credence_data:
            print("credence_pct付きのUNCERTAINエントリが見つかりません。")
            return
        
        # 影表示計算
        print("Calculating shadow values...")
        confirmed_data = triage_data.get("CONFIRMED", [])
        confirmed_add_data = triage_data.get("CONFIRMED_add", [])
        all_confirmed_data = confirmed_data + confirmed_add_data
        shadow_values = calculate_shadow_values(all_confirmed_data, credence_data)
        print(f"Shadow values calculated: {len(shadow_values)} items")
        
        # マトリクス表示生成
        print("Generating matrix display...")
        matrix_output = generate_matrix_display(shadow_values)
        print(matrix_output)
        
        # impact_cards更新
        print("Updating impact cards...")
        updated_cards = update_impact_cards_with_shadow(impact_cards, shadow_values)
        
        # 結果をファイルに保存
        output_file = os.path.join(ticker_path, "credence_shadow.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "as_of": triage_data.get("as_of", ""),
                "credence_data": credence_data,
                "shadow_values": shadow_values,
                "updated_impact_cards": updated_cards
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n結果を {output_file} に保存しました。")
        
    except Exception as e:
        import traceback
        print(f"エラー: {e}")
        print("詳細なエラー情報:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
