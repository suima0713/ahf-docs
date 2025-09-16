#!/usr/bin/env python3
import json, sys, pathlib
from typing import Dict, List, Any

def load_triage_files(ticker_path: str) -> Dict[str, List[Dict]]:
    """triageファイル群を読み込み"""
    triage_dir = pathlib.Path(ticker_path) / "current"
    
    files = {
        "CONFIRMED": triage_dir / "triage.json",
        "UNCERTAIN": triage_dir / "triage.json", 
        "PROVISIONAL": triage_dir / "triage_provisional.json"
    }
    
    data = {}
    for key, file_path in files.items():
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
                if isinstance(content, dict):
                    data[key] = content.get(key, [])
                else:
                    data[key] = content
        else:
            data[key] = []
    
    return data

def calculate_edge_confidence(t1_conf: float, p_confidence: float) -> float:
    """UI用統合表示の信頼度計算"""
    return max(t1_conf, p_confidence)

def validate_no_t1_overwrite(confirmed: List[Dict], provisional: List[Dict]) -> List[str]:
    """T1上書き禁止チェック"""
    errors = []
    
    confirmed_kpis = {rec.get("kpi") for rec in confirmed if rec.get("kpi")}
    provisional_kpis = {rec.get("kpi") for rec in provisional if rec.get("kpi")}
    
    # 同一KPI名の重複チェック
    overlapping = confirmed_kpis & provisional_kpis
    if overlapping:
        errors.append(f"T1 overwrite violation: KPI(s) {overlapping} exist in both CONFIRMED and PROVISIONAL")
    
    return errors

def generate_edge_overlay_report(ticker_path: str) -> Dict[str, Any]:
    """Edge Overlay統合レポート生成"""
    triage_data = load_triage_files(ticker_path)
    
    confirmed = triage_data.get("CONFIRMED", [])
    uncertain = triage_data.get("UNCERTAIN", [])
    provisional = triage_data.get("PROVISIONAL", [])
    
    # T1上書き禁止チェック
    overwrite_errors = validate_no_t1_overwrite(confirmed, provisional)
    
    # 統計情報
    stats = {
        "t1_count": len(confirmed),
        "uncertain_count": len(uncertain),
        "provisional_count": len(provisional),
        "total_kpis": len(confirmed) + len(uncertain) + len(provisional)
    }
    
    # P信頼度統計
    p_confidences = [rec.get("p_confidence", 0.0) for rec in provisional]
    if p_confidences:
        stats["p_confidence_avg"] = sum(p_confidences) / len(p_confidences)
        stats["p_confidence_max"] = max(p_confidences)
        stats["p_confidence_min"] = min(p_confidences)
    
    # ソース統計
    source_types = {}
    for rec in provisional:
        for source in rec.get("sources", []):
            source_type = source.get("type", "unknown")
            source_types[source_type] = source_types.get(source_type, 0) + 1
    stats["source_types"] = source_types
    
    report = {
        "ticker": pathlib.Path(ticker_path).name,
        "timestamp": pathlib.Path().cwd().stat().st_mtime,
        "stats": stats,
        "overwrite_errors": overwrite_errors,
        "data": {
            "CONFIRMED": confirmed,
            "UNCERTAIN": uncertain,
            "PROVISIONAL": provisional
        }
    }
    
    return report

def main():
    if len(sys.argv) != 2:
        print("Usage: ahf_v2_edge_overlay.py <ticker_path>"); sys.exit(2)
    
    ticker_path = sys.argv[1]
    
    try:
        report = generate_edge_overlay_report(ticker_path)
        
        # エラーチェック
        if report["overwrite_errors"]:
            print("AHF v2 Edge Overlay ERRORS:")
            for error in report["overwrite_errors"]:
                print(f"  {error}")
            sys.exit(1)
        
        # レポート出力
        print(json.dumps(report, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"Error generating edge overlay report: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
