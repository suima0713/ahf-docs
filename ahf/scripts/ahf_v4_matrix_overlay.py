#!/usr/bin/env python3
import json, sys, pathlib
from typing import Dict, List

def generate_matrix_edge_annotations(axis_edges: Dict[str, List]) -> Dict[str, str]:
    """AHFマトリクスEdge表示生成：各軸末尾に〔Edge: P/TTL/要旨〕を最大2件"""
    
    annotations = {}
    
    for axis, edges in axis_edges.items():
        if not edges:
            continue
        
        # 最大2件まで
        display_edges = edges[:2]
        
        edge_lines = []
        for edge in display_edges:
            p_score = edge.get("p", 0)
            ttl_days = edge.get("ttl_days", 0)
            source_summary = edge.get("source_summary", "")
            
            # 要旨≤25字にクリップ
            summary_short = source_summary[:25] if len(source_summary) > 25 else source_summary
            
            edge_line = f"〔Edge: P={p_score}, TTL={ttl_days}d, {summary_short}〕"
            edge_lines.append(edge_line)
        
        # 軸別注釈
        if edge_lines:
            annotations[axis] = "\n".join(edge_lines)
    
    return annotations

def calculate_star_adjustment(adopted_edges: List[Dict]) -> int:
    """星評価調整：Core基準に対し Edgeで ±1★ のみ調整可"""
    total_adjustment = 0
    
    for edge in adopted_edges:
        edge_impact = edge.get("edge_impact", {})
        star_adj = edge_impact.get("star_adjustment", 0)
        total_adjustment += star_adj
    
    # 上限5★、下限1★
    return max(-1, min(1, total_adjustment))

def calculate_confidence_adjustment(adopted_edges: List[Dict]) -> int:
    """確信度調整：Edge採用時に +5pp（強気）/−5pp（弱気） を一度だけ付与"""
    total_adjustment = 0
    
    for edge in adopted_edges:
        edge_impact = edge.get("edge_impact", {})
        conf_adj = edge_impact.get("confidence_adjustment", 0)
        total_adjustment += conf_adj
    
    # 50–95%にクリップ
    return max(-5, min(5, total_adjustment))

def generate_abc_yaml_overlay(axis_edges: Dict[str, List]) -> Dict[str, str]:
    """A/B/C.yaml用Edge表示生成"""
    
    yaml_overlays = {}
    
    # A.yaml（材料）用
    a_overlay = []
    if "revenue" in axis_edges:
        for edge in axis_edges["revenue"][:2]:
            p_score = edge.get("p", 0)
            summary = edge.get("source_summary", "")[:25]
            a_overlay.append(f"〔Edge: P={p_score}, {summary}〕")
    
    if a_overlay:
        yaml_overlays["A.yaml"] = "\n".join(a_overlay)
    
    # B.yaml（結論&Horizon&KPI×2）用
    b_overlay = []
    if "credit" in axis_edges:
        for edge in axis_edges["credit"][:2]:
            p_score = edge.get("p", 0)
            summary = edge.get("source_summary", "")[:25]
            b_overlay.append(f"〔Edge: P={p_score}, {summary}〕")
    
    if b_overlay:
        yaml_overlays["B.yaml"] = "\n".join(b_overlay)
    
    # C.yaml（反証）用
    c_overlay = []
    if "funding" in axis_edges:
        for edge in axis_edges["funding"][:2]:
            p_score = edge.get("p", 0)
            summary = edge.get("source_summary", "")[:25]
            c_overlay.append(f"〔Edge: P={p_score}, {summary}〕")
    
    if c_overlay:
        yaml_overlays["C.yaml"] = "\n".join(c_overlay)
    
    return yaml_overlays

def main():
    if len(sys.argv) != 2:
        print("Usage: ahf_v4_matrix_overlay.py <edge_evaluation_file>"); sys.exit(2)
    
    edge_eval_file = sys.argv[1]
    
    try:
        with open(edge_eval_file, 'r', encoding='utf-8') as f:
            edge_data = json.load(f)
        
        adopted_edges = edge_data.get("adopted_edges", [])
        matrix_overlay = edge_data.get("matrix_overlay", {})
        
        # マトリクス注釈生成
        matrix_annotations = generate_matrix_edge_annotations(matrix_overlay)
        
        # 評価調整計算
        star_adjustment = calculate_star_adjustment(adopted_edges)
        confidence_adjustment = calculate_confidence_adjustment(adopted_edges)
        
        # A/B/C.yaml用表示生成
        yaml_overlays = generate_abc_yaml_overlay(matrix_overlay)
        
        # 結果出力
        result = {
            "matrix_annotations": matrix_annotations,
            "evaluation_adjustments": {
                "star_adjustment": star_adjustment,
                "confidence_adjustment": confidence_adjustment
            },
            "yaml_overlays": yaml_overlays,
            "adopted_edges_summary": {
                "count": len(adopted_edges),
                "by_axis": {axis: len(edges) for axis, edges in matrix_overlay.items()}
            }
        }
        
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"Error generating matrix overlay: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
