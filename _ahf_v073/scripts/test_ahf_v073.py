#!/usr/bin/env python3
"""
AHF v0.7.3 テストスクリプト
Purpose: 固定3軸評価システムの動作確認
"""

import os
import sys
import json
import tempfile
from datetime import datetime

# テスト用のサンプルデータ
SAMPLE_FACTS_MD = """# T1確定事実（AUST満たすもののみ）

[2024-12-15][T1-F][Core①] "FY26 revenue guidance midpoint $2.5B (range $2.3B–$2.7B)." (impact: guidance_fy26_mid) <https://sec.gov/edgar/...>
[2024-12-15][T1-F][Core②] "Operating margin improved 2.5pp to 15.2%." (impact: opm_drift) <https://sec.gov/edgar/...>
[2024-12-15][T1-F][Core③] "Backlog grew 15% quarter-over-quarter to $1.2B." (impact: backlog_growth) <https://sec.gov/edgar/...>
[2024-12-15][T1-C][Time] "Multi-year contract with Microsoft signed." (impact: contract_event) <https://ir.company.com/earnings/...>
"""

SAMPLE_TRIAGE_JSON = {
    "as_of": "2024-12-15",
    "CONFIRMED": [
        {
            "kpi": "guidance_fy26_mid",
            "value": 2500,
            "unit": "USD_millions",
            "asof": "2024-12-15",
            "tag": "T1-core",
            "url": "https://sec.gov/edgar/..."
        },
        {
            "kpi": "opm_drift",
            "value": 2.5,
            "unit": "pp",
            "asof": "2024-12-15",
            "tag": "T1-core",
            "url": "https://sec.gov/edgar/..."
        },
        {
            "kpi": "backlog_growth",
            "value": 15,
            "unit": "%",
            "asof": "2024-12-15",
            "tag": "T1-core",
            "url": "https://sec.gov/edgar/..."
        }
    ],
    "UNCERTAIN": [],
    "HYPOTHESES": []
}

SAMPLE_BACKLOG_MD = """| id | class=EDGE | KPI/主張 | 現在の根拠≤40語 | ソース | T1化に足りないもの | 次アクション | 関連Impact | unavailability_reason | grace_until |
| H1 | class=EDGE | market_sentiment_positive | Analyst upgrades and price target increases | IR | SEC filing pending | Monitor | sentiment_boost | rate_limited | 2024-12-22 |
| H2 | class=EDGE | competitive_advantage | Patent portfolio expansion | PR | Legal confirmation needed | Verify | moat_strength | not_found | 2024-12-20 |
"""

def create_test_environment():
    """テスト環境を作成"""
    # 一時ディレクトリ作成
    test_dir = tempfile.mkdtemp(prefix="ahf_v073_test_")
    ticker_dir = os.path.join(test_dir, "tickers", "TEST")
    current_dir = os.path.join(ticker_dir, "current")
    
    os.makedirs(current_dir, exist_ok=True)
    
    # テストファイル作成
    facts_file = os.path.join(current_dir, "facts.md")
    with open(facts_file, "w", encoding="utf-8") as f:
        f.write(SAMPLE_FACTS_MD)
    
    triage_file = os.path.join(current_dir, "triage.json")
    with open(triage_file, "w", encoding="utf-8") as f:
        json.dump(SAMPLE_TRIAGE_JSON, f, ensure_ascii=False, indent=2)
    
    backlog_file = os.path.join(current_dir, "backlog.md")
    with open(backlog_file, "w", encoding="utf-8") as f:
        f.write(SAMPLE_BACKLOG_MD)
    
    return test_dir, ticker_dir, current_dir

def test_ahf_v073_evaluator():
    """固定3軸評価エンジンのテスト"""
    print("=== テスト1: AHF v0.7.3 固定3軸評価エンジン ===")
    
    try:
        from ahf_v073_evaluator import AHFv073Evaluator
        
        test_dir, ticker_dir, current_dir = create_test_environment()
        
        evaluator = AHFv073Evaluator()
        evaluator.load_t1_data(
            os.path.join(current_dir, "facts.md"),
            os.path.join(current_dir, "triage.json")
        )
        
        print(f"✓ T1事実読み込み: {len(evaluator.t1_facts)}件")
        
        # 3軸評価
        lec_score = evaluator.evaluate_axis_lec()
        nes_score = evaluator.evaluate_axis_nes()
        vrg_score = evaluator.evaluate_axis_vrg()
        
        print(f"✓ LEC評価: ★{lec_score.score}/5 (確信度{lec_score.confidence}%)")
        print(f"✓ NES評価: ★{nes_score.score}/5 (確信度{nes_score.confidence}%)")
        print(f"✓ VRG評価: ★{vrg_score.score}/5 (確信度{lec_score.confidence}%)")
        
        # 意思決定計算
        axis_scores = [lec_score, nes_score, vrg_score]
        decision = evaluator.calculate_decision(axis_scores)
        
        print(f"✓ 意思決定: {decision.decision.value} (DI={decision.di_score:.2f})")
        print(f"✓ サイズ: {decision.size_pct:.1f}%")
        
        # 出力生成
        output = evaluator.generate_output(axis_scores, decision)
        print(f"✓ 出力生成: {len(output['axes'])}軸")
        
        return True
        
    except Exception as e:
        print(f"✗ エラー: {e}")
        return False

def test_turbo_screen():
    """Turbo Screen機能のテスト"""
    print("\n=== テスト2: Turbo Screen機能 ===")
    
    try:
        from ahf_turbo_screen import TurboScreenEngine
        
        test_dir, ticker_dir, current_dir = create_test_environment()
        
        turbo_engine = TurboScreenEngine()
        turbo_engine.load_edge_data(
            os.path.join(current_dir, "backlog.md"),
            os.path.join(current_dir, "triage.json")
        )
        
        print(f"✓ Edge事実読み込み: {len(turbo_engine.edge_facts)}件")
        
        # 受付閾値フィルタリング
        eligible_facts = turbo_engine.filter_eligible_edge_facts()
        print(f"✓ 受付Edge事実: {len(eligible_facts)}件")
        
        # Edge事実サマリー
        summary = turbo_engine.generate_edge_summary(eligible_facts)
        print(f"✓ Edge事実サマリー: {summary['total_edge_facts']}件")
        
        return True
        
    except Exception as e:
        print(f"✗ エラー: {e}")
        return False

def test_anchor_lint():
    """AnchorLint v1のテスト"""
    print("\n=== テスト3: AnchorLint v1 ===")
    
    try:
        from ahf_anchor_lint import AnchorLintEngine
        
        lint_engine = AnchorLintEngine()
        
        # サンプル事実データ
        sample_facts = [
            {
                "kpi": "guidance_fy26_mid",
                "verbatim": "FY26 revenue guidance midpoint $2.5B",
                "anchor": "https://sec.gov/edgar/...#:~:text=FY26%20revenue%20guidance",
                "url": "https://sec.gov/edgar/..."
            },
            {
                "kpi": "backlog_growth",
                "verbatim": "This is a very long verbatim that exceeds the 25 word limit and should be flagged by the lint engine",
                "anchor": "anchor_backup{quote: 'backlog growth', hash: 'abc123'}",
                "url": "https://ir.company.com/earnings/"
            },
            {
                "kpi": "opm_drift",
                "verbatim": "Operating margin improved",
                "anchor": "",
                "url": "https://sec.gov/edgar/..."
            }
        ]
        
        # AnchorLint実行
        results = lint_engine.batch_lint_facts(sample_facts)
        print(f"✓ AnchorLint実行: {len(results)}件")
        
        # レポート生成
        report = lint_engine.generate_lint_report(results)
        print(f"✓ 有効率: {report['summary']['validity_rate']:.1f}%")
        
        # 問題のある事実
        problematic = [r for r in results if r.status.value != "VALID"]
        print(f"✓ 問題事実: {len(problematic)}件")
        
        return True
        
    except Exception as e:
        print(f"✗ エラー: {e}")
        return False

def test_mvp4_output():
    """MVP-4+出力スキーマのテスト"""
    print("\n=== テスト4: MVP-4+出力スキーマ ===")
    
    try:
        from ahf_mvp4_output import MVP4OutputGenerator
        
        generator = MVP4OutputGenerator()
        
        # サンプルデータ
        sample_t1_facts = [
            {"kpi": "guidance_fy26_mid", "value": 2500, "unit": "USD_millions", "verbatim": "FY26 revenue guidance midpoint $2.5B"},
            {"kpi": "opm_drift", "value": 2.5, "unit": "pp", "verbatim": "Operating margin improved 2.5pp"},
            {"kpi": "backlog_growth", "value": 15, "unit": "%", "verbatim": "Backlog grew 15% quarter-over-quarter"}
        ]
        
        # 軸結果生成
        axis_results = [
            generator.generate_axis_result("①長期EV確度", 4, 80, sample_t1_facts),
            generator.generate_axis_result("②長期EV勾配", 3, 75, sample_t1_facts),
            generator.generate_axis_result("③バリュエーション＋認知ギャップ", 2, 70, sample_t1_facts)
        ]
        
        print(f"✓ 軸結果生成: {len(axis_results)}軸")
        
        # 意思決定生成
        decision = generator.generate_decision_result(0.45, [4, 3, 2])
        print(f"✓ 意思決定: {decision.decision_type} (DI={decision.di_score:.2f})")
        
        # バリュエーション生成
        valuation = generator.generate_valuation_overlay(12.5, 35)
        print(f"✓ バリュエーション: {valuation.status} (EV/S={valuation.ev_sales_fwd:.1f}x)")
        
        # 完全出力生成
        output = generator.generate_complete_output("TEST", axis_results, decision, valuation, sample_t1_facts)
        print(f"✓ 完全出力: {len(output)}項目")
        
        # テーブル形式出力
        table = generator.format_output_table(output)
        print(f"✓ テーブル出力: {len(table.split(chr(10)))}行")
        
        return True
        
    except Exception as e:
        print(f"✗ エラー: {e}")
        return False

def test_integrated():
    """統合実行のテスト"""
    print("\n=== テスト5: 統合実行 ===")
    
    try:
        from ahf_v073_integrated import AHFv073Integrated
        
        test_dir, ticker_dir, current_dir = create_test_environment()
        
        # 統合実行
        integrated = AHFv073Integrated("TEST", os.path.join(test_dir, "tickers"))
        result = integrated.run_evaluation()
        
        if "error" in result:
            print(f"✗ 統合実行エラー: {result['error']}")
            return False
        
        print(f"✓ 統合実行成功: {result['decision']['decision_type']}")
        print(f"✓ DI: {result['decision']['di_score']:.2f}")
        print(f"✓ サイズ: {result['decision']['size_pct']:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"✗ エラー: {e}")
        return False

def main():
    """メインテスト実行"""
    print("=== AHF v0.7.3 テストスイート ===")
    print(f"実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("固定3軸評価エンジン", test_ahf_v073_evaluator),
        ("Turbo Screen機能", test_turbo_screen),
        ("AnchorLint v1", test_anchor_lint),
        ("MVP-4+出力スキーマ", test_mvp4_output),
        ("統合実行", test_integrated)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name}: テスト実行エラー - {e}")
            results.append((test_name, False))
    
    # 結果サマリー
    print("\n=== テスト結果サマリー ===")
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n総合結果: {passed}/{total} テスト通過")
    
    if passed == total:
        print("🎉 全テスト通過！AHF v0.7.3は正常に動作します。")
        return 0
    else:
        print("⚠️  一部テストが失敗しました。ログを確認してください。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
