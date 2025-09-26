#!/usr/bin/env python3
import json, sys, re, pathlib
from typing import Dict, List, Tuple, Optional

# Edge取り込み基準
EDGE_ADOPTION_THRESHOLD = 70
EDGE_BACKLOG_THRESHOLD = 50
MAX_EDGE_PER_AXIS = 2

# P採点の簡易ガイド：出自(40%)×一致性/整合(40%)×鮮度(20%)
P_SCORING_WEIGHTS = {
    "source_credibility": 0.4,
    "consistency": 0.4,
    "freshness": 0.2
}

# 許容ソース（例）
ALLOWED_EDGE_SOURCES = {
    "rating_agency": ["KBRA", "S&P", "Moody's", "Fitch", "DBRS"],
    "issuer_ir": ["Company IR", "Investor Relations", "Earnings Call"],
    "regulator": ["SEC", "FDIC", "OCC", "Federal Reserve", "CFPB"],
    "major_news": ["Reuters", "Bloomberg", "WSJ", "FT"],
    "primary_doc": ["Official Document", "Filing", "Press Release"]
}

def calculate_p_score(source_type: str, consistency_score: float, freshness_score: float) -> int:
    """P採点計算：出自(40%)×一致性/整合(40%)×鮮度(20%)"""
    
    # 出自スコア（40%）
    source_credibility = 0.0
    for category, sources in ALLOWED_EDGE_SOURCES.items():
        if source_type.lower() in [s.lower() for s in sources]:
            if category == "rating_agency":
                source_credibility = 0.9
            elif category == "issuer_ir":
                source_credibility = 0.8
            elif category == "regulator":
                source_credibility = 0.85
            elif category == "major_news":
                source_credibility = 0.7
            elif category == "primary_doc":
                source_credibility = 0.75
            break
    
    # 総合Pスコア計算
    p_score = (
        source_credibility * P_SCORING_WEIGHTS["source_credibility"] +
        consistency_score * P_SCORING_WEIGHTS["consistency"] +
        freshness_score * P_SCORING_WEIGHTS["freshness"]
    ) * 100
    
    return min(int(p_score), 100)

def evaluate_edge_adoption(p_score: int, contradiction: bool) -> str:
    """Edge取り込み基準評価"""
    if contradiction:
        return "reject"
    elif p_score >= EDGE_ADOPTION_THRESHOLD:
        return "adopt"
    elif p_score >= EDGE_BACKLOG_THRESHOLD:
        return "backlog"
    else:
        return "reject"

def calculate_edge_impact(p_score: int, kpi_type: str, contradiction: bool) -> Dict:
    """Edge表示と評価への影響計算"""
    if contradiction or p_score < EDGE_ADOPTION_THRESHOLD:
        return {}
    
    impact = {}
    
    # 星評価：Core基準に対し Edgeで ±1★ のみ調整可
    if p_score >= 70:
        if "risk" in kpi_type.lower() or "loss" in kpi_type.lower():
            impact["star_adjustment"] = -1  # リスク系は−1★も可
        else:
            impact["star_adjustment"] = 1   # 通常は+1★
    
    # 確信度(%)：Edge採用時に +5pp（強気）/−5pp（弱気） を一度だけ付与
    if "risk" in kpi_type.lower() or "loss" in kpi_type.lower():
        impact["confidence_adjustment"] = -5  # 弱気
    else:
        impact["confidence_adjustment"] = 5   # 強気
    
    # 注釈（要旨≤25字）
    impact["annotation"] = f"Edge: P={p_score}, TTL=7d"
    
    return impact

def validate_edge_source(source_summary: str) -> Tuple[bool, str]:
    """Edgeソース検証"""
    if len(source_summary) > 35:
        return False, f"Source summary exceeds 35 characters: {len(source_summary)}"
    
    # 許容ソースチェック
    source_lower = source_summary.lower()
    is_allowed = any(
        any(source.lower() in source_lower for source in sources)
        for sources in ALLOWED_EDGE_SOURCES.values()
    )
    
    if not is_allowed:
        return False, f"Source not in allowed categories: {source_summary}"
    
    return True, ""

def process_edge_records(records: List[Dict]) -> Dict[str, List]:
    """Edge記録の処理と分類"""
    results = {
        "adopt": [],
        "backlog": [],
        "reject": []
    }
    
    for record in records:
        if record.get("class") not in ["EDGE", "LEAD"]:
            continue
        
        p_score = record.get("p", 0)
        contradiction = record.get("contradiction", False)
        source_summary = record.get("source_summary", "")
        
        # ソース検証
        is_valid_source, source_error = validate_edge_source(source_summary)
        if not is_valid_source:
            record["validation_error"] = source_error
            results["reject"].append(record)
            continue
        
        # 採用基準評価
        adoption_decision = evaluate_edge_adoption(p_score, contradiction)
        
        # Edge影響計算
        kpi = record.get("kpi", "")
        edge_impact = calculate_edge_impact(p_score, kpi, contradiction)
        if edge_impact:
            record["edge_impact"] = edge_impact
        
        results[adoption_decision].append(record)
    
    return results

def generate_matrix_overlay(adopted_edges: List[Dict]) -> Dict[str, List]:
    """AHFマトリクスEdge表示生成"""
    # 軸別にEdgeを分類（最大2件/軸）
    axis_edges = {}
    
    for edge in adopted_edges:
        kpi = edge.get("kpi", "")
        
        # 軸判定（簡易）
        if "revenue" in kpi.lower() or "concentration" in kpi.lower():
            axis = "revenue"
        elif "credit" in kpi.lower() or "loss" in kpi.lower():
            axis = "credit"
        elif "funding" in kpi.lower() or "liquidity" in kpi.lower():
            axis = "funding"
        else:
            axis = "other"
        
        if axis not in axis_edges:
            axis_edges[axis] = []
        
        if len(axis_edges[axis]) < MAX_EDGE_PER_AXIS:
            axis_edges[axis].append(edge)
    
    return axis_edges

def main():
    if len(sys.argv) != 2:
        print("Usage: ahf_v4_edge_evaluator.py <triage_file>"); sys.exit(2)
    
    triage_file = sys.argv[1]
    
    try:
        with open(triage_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # UNCERTAINからEdge記録を抽出
        uncertain_records = data.get("UNCERTAIN", [])
        edge_records = [r for r in uncertain_records if r.get("class") in ["EDGE", "LEAD"]]
        
        # Edge処理
        edge_results = process_edge_records(edge_records)
        
        # マトリクス表示生成
        matrix_overlay = generate_matrix_overlay(edge_results["adopt"])
        
        # 結果出力
        report = {
            "edge_evaluation": {
                "adopt_count": len(edge_results["adopt"]),
                "backlog_count": len(edge_results["backlog"]),
                "reject_count": len(edge_results["reject"])
            },
            "adopted_edges": edge_results["adopt"],
            "backlog_edges": edge_results["backlog"],
            "rejected_edges": edge_results["reject"],
            "matrix_overlay": matrix_overlay
        }
        
        print(json.dumps(report, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"Error processing edge records: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
