# IDCC 運用ノート v0.3.2-UL

## 内部優先度変数（固定化）
**EXP_COST > MISINFO_COST** で固定
- 収集優先度：Lead拡張 → 矛盾タグ → TTL
- T1直行は抑制

## Pilot Buy ルール（運用ノート明記）
**Gate**: S≥70・Q≥50・ΔIRR≥+700bp、レッドライン無
**サイズ**: 標準の1/4開始。T1トリガー毎に段階増（2トリガーで標準）
**減額**: Note3ロール鈍化／Royalty比率低下／集中悪化／Item 3.01等

## Horizon重み（B.yaml埋め込み）
- 6M: T1:構造比 = 8:2
- 1Y: T1:構造比 = 7:3  
- 3Y: T1:構造比 = 5:5
- 5Y: T1:構造比 = 3:7

## Coverage暫定運用
**分母未了（FY26 mid）・分子未了（RPO同等）のとき**:
- 暫定Coverageを表示せず
- 判断はS×Q×Vへ委譲
- レポ側は"未計算"を明記

## 矛盾解消フロー
triage.json.contradiction_setで管理:
- status: resolved/pending
- winner_url: 確定ソース
- note: 解消経緯

## S×Q×Vカード運用
impact_cards.jsonに常設:
- structure_card: TAM×非代替性
- quality_card: 収益質×CF安定性  
- valuation_card: ΔIRR bp
- pilot_buy_rule: 総合判定
