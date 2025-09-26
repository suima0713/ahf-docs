# E0-UL一元プール（v0.8.0 - 固定3軸対応）

## T1最優先原則
- **T1確定**: sec.gov（10-K/10-Q/8-K）≧ investors.company.com（IR PR/資料）
- **T2候補**: 他AI/記事/トランスクリプト（EDGE、TTL=7日、意思決定には使わない）
- **95%は内部ETLで完結、他AIは"場所のヒント＋照合"の5%**

## 他AIの役割（限定）
- **用途**: 所在の手掛かり（例：10-K注記ページ、見出し名）と突合
- **扱い**: 必ずT2（EDGE/TTL=7日）。T1で再取得・再計算してからスコア/DIへ反映
- **禁止**: 他AIの数値や文言を直接引用・採用しない

## 固定3軸の分類
- **LEC**: ①長期EV確度（流動性・負債・希薄化・CapEx強度・運転資本回転・大型契約・コベナンツ等）
- **NES**: ②長期EV勾配（次Q q/q%・ガイド改定%・受注/Backlog増勢%・Margin_term・Health_term）
- **VRG**: ③バリュエーション＋認知ギャップ（EV/S_actual・EV/S_peer_median・EV/S_fair_rDCF・認知フラグ）

| id | class | axis | KPI/主張 | 現在の根拠≤25語 | ソース | T1化に足りないもの | 次アクション | 関連Impact | unavailability_reason | grace_until |
|----|-------|------|----------|-----------------|-------|-------------------|-------------|-------------|----------------------|-------------|
| L-G1 | Lead | LEC | FY26 mid $X | IR PRで数値提示 | <URL> | 10-Q/EX-99原本 | EX-99リンク確定 | guidance_fy26_mid | EDGAR_down | 2024-12-31 |
| L-C1 | Lead | NES | Buyback $Y | 8-K見出し | <URL> | Item/金額逐語 | Item 8.01逐語抽出 | capital_allocation | rate_limited | 2024-12-31 |
| 001 | Lead | LEC | FY26_Floor | SEC 10-K本文の文言 | https://sec.gov/... | section/tableラベル | SEC再確認 | ①長期EV確度 | not_found | 2024-12-31 |
| 002 | Lead | NES | Fixed_fee_ratio | トランスクリプト発言 | https://ir.company.com/... | 逐語≤25語 | トランスクリプト精査 | ②長期EV勾配 | blocked_source | 2024-12-31 |
| 003 | Lead | VRG | EV/S_peer_median | アナリストレポート | https://analyst.com/... | ピア定義・算出根拠 | ピアリスト確定 | ③バリュエーション | not_found | 2024-12-31 |

## 運用ルール
- class=Lead：新規発見の事実候補
- axis=LEC|NES|VRG：固定3軸の分類
- T1化に足りないもの：AUST（As-of/Unit/Section-or-Table/≤25語/直URL）の欠けている要素
- unavailability_reason：EDGAR_down／rate_limited／not_found／blocked_source
- grace_until：TTL期限（過ぎたら優先度繰上げ）
- 関連Impact：①LEC（長期EV確度）/②NES（長期EV勾配）/③VRG（バリュエーション＋認知ギャップ）

## Stage-3カード（半透明αの最大化）
| id | hypothesis | t1_verbatim | url_anchor | test_formula | threshold_result | reasoning | result | ttl_days | reflection | axis |
|----|------------|-------------|------------|--------------|------------------|-----------|--------|----------|------------|------|
| S3_001 | 違和感の仮説 | T1逐語≤25語 | URL#:~:text=... | 四則1行のテスト式 | 閾値/合否 | 推論1段 | PASS/FAIL/DEFER/REWRITE | 30 | 反映（★調整±1内/DI/α±0.08内） | LEC |

