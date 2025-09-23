#!/usr/bin/env python3
"""
AHFマトリクス差分計算 - 前回比の理由タグを機械的に付与、可視化ミス削減
最小構成で実装損を出さずに効くやつだけ
"""

import json
import sys
from pathlib import Path

def calculate_matrix_delta(current_matrix, prior_matrix):
    """
    マトリクス差分計算 - 前回比の理由タグを機械的に付与
    
    Args:
        current_matrix: 現在のマトリクスデータ
        prior_matrix: 前回のマトリクスデータ
    
    Returns:
        dict: 差分データ（星とΔ矢印用）
    """
    try:
        axes = current_matrix.get("axes", [])
        current_stars = current_matrix.get("current_stars", [])
        prior_stars = prior_matrix.get("prior_stars", [])
        
        # 差分計算
        delta = [current - prior for current, prior in zip(current_stars, prior_stars)]
        
        # 理由タグ生成（簡易版）
        reasons = []
        for i, (axis, d) in enumerate(zip(axes, delta)):
            if d > 0.2:
                reasons.append(f"{axis}↑")
            elif d < -0.2:
                reasons.append(f"{axis}↓")
            else:
                reasons.append(f"{axis}→")
        
        return {
            "matrix": {
                "as_of": current_matrix.get("as_of", ""),
                "axes": axes,
                "current_stars": current_stars,
                "prior_stars": prior_stars,
                "delta": delta,
                "reasons": reasons
            }
        }
        
    except Exception as e:
        return {"error": f"Matrix delta calculation failed: {str(e)}"}

def main():
    """メイン処理"""
    if len(sys.argv) != 3:
        print("Usage: python ahf_matrix_delta.py <current_matrix.json> <prior_matrix.json>")
        sys.exit(1)
    
    current_file = sys.argv[1]
    prior_file = sys.argv[2]
    
    try:
        # 現在のマトリクス読み込み
        with open(current_file, 'r', encoding='utf-8') as f:
            current_matrix = json.load(f)
        
        # 前回のマトリクス読み込み
        with open(prior_file, 'r', encoding='utf-8') as f:
            prior_matrix = json.load(f)
        
        # 差分計算実行
        result = calculate_matrix_delta(current_matrix, prior_matrix)
        
        # 結果出力
        if "error" in result:
            print(f"❌ エラー: {result['error']}")
        else:
            print("✅ マトリクス差分計算完了")
            matrix = result["matrix"]
            for i, (axis, delta) in enumerate(zip(matrix["axes"], matrix["delta"])):
                print(f"  {axis}: {matrix['prior_stars'][i]} → {matrix['current_stars'][i]} (Δ{delta:+.1f})")
        
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
