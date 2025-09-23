#!/usr/bin/env python3
"""
AHF監査マクロ - エラーを事前に赤札（数式/単位/アンカー/丸め）
最小構成で実装損を出さずに効くやつだけ
"""

import json
import sys
from pathlib import Path

def audit(payload, guards):
    """
    監査マクロ - 数式/単位/アンカー/丸めのエラーを事前捕捉
    
    Args:
        payload: 監査対象のデータ
        guards: ガードレール定数
    
    Returns:
        dict: {"pass": bool, "issues": list}
    """
    issues = []

    try:
        # A. GAAP→Non-GAAP GPブリッジ
        if "q2_baseline" in payload and "q2_cogs_adjustments" in payload:
            gp = payload["q2_baseline"].get("gaap_gross_profit_$k", 0)
            adj = payload["q2_cogs_adjustments"]
            ngp = payload["q2_baseline"].get("nongaap_gross_profit_$k", 0)
            
            if adj and isinstance(adj, list):
                adj_sum = sum(i.get("amount_$k", 0) for i in adj)
                bridge_diff = abs((gp + adj_sum) - ngp)
                if bridge_diff > guards["gp_bridge_tolerance_$k"]:
                    issues.append(f"GP bridge mismatch: {bridge_diff} > {guards['gp_bridge_tolerance_$k']}")

        # B. OT→GM（Stage-1）
        if "mix" in payload:
            mix = payload["mix"]
            ot_q2 = mix.get("ot_pct_q2", 0)
            ot_q3 = mix.get("ot_pct_q3", 0)
            ss_q2 = mix.get("ss_pct_q2", 0)
            ss_q3 = mix.get("ss_pct_q3", 0)
            
            stage1_pp = (ot_q3 - ot_q2) * (guards["ot_to_gm_pp_per_5pp"] / 5.0) \
                      + (ss_q3 - ss_q2) * guards["seg_mix_pp_per_1pp"]

        # C. GAAP GM再計算
        if "gm" in payload and "q3" in payload:
            gm = payload["gm"]
            q3 = payload["q3"]
            
            gm_q2 = gm.get("gaap_gm_q2_pct", 0)
            gm_target = gm.get("gaap_gm_target_pct", 0)
            residual_pp = gm_target - (gm_q2 + stage1_pp)
            residual_$k = round(q3.get("rev_mid_$k", 0) * residual_pp / 100)
            
            if abs((gm_q2 + stage1_pp + residual_pp) - gm_target) > guards["gm_bridge_tolerance_pp"]:
                issues.append("GM reconciliation tolerance exceeded")
            if residual_$k > guards["efficiency_residual_cap_$k"]:
                issues.append(f"Efficiency residual cap exceeded: {residual_$k} > {guards['efficiency_residual_cap_$k']}")

        # D. アンカー検証（最小要件）
        for m in payload.get("anchors", []):
            if not m.get("verbatim") or len(m["verbatim"].split()) > 25 or "anchor" not in m:
                issues.append(f"Anchor/quote invalid: {m.get('field','?')}")

    except Exception as e:
        issues.append(f"Audit error: {str(e)}")

    return {"pass": len(issues) == 0, "issues": issues}

def main():
    """メイン処理"""
    if len(sys.argv) != 3:
        print("Usage: python ahf_audit_macro.py <payload.json> <guards.json>")
        sys.exit(1)
    
    payload_file = sys.argv[1]
    guards_file = sys.argv[2]
    
    try:
        # ペイロード読み込み
        with open(payload_file, 'r', encoding='utf-8') as f:
            payload = json.load(f)
        
        # ガードレール読み込み
        with open(guards_file, 'r', encoding='utf-8') as f:
            guards_data = json.load(f)
            guards = guards_data["guards"]
        
        # 監査実行
        result = audit(payload, guards)
        
        # 結果出力
        if result["pass"]:
            print("✅ 監査パス: 問題なし")
        else:
            print("❌ 監査NG:")
            for issue in result["issues"]:
                print(f"  - {issue}")
        
        # JSON出力（他スクリプト連携用）
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except FileNotFoundError as e:
        print(f"ファイルが見つかりません: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"JSON解析エラー: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
