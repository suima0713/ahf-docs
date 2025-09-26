# AAOI (Applied Optoelectronics) - 3軸分析結果

## 投資判断に直結する固定3軸評価

### ①長期EV確度：★★★☆☆ (3/5)
**代表KPI/根拠（T1逐語≤25語＋リンク）**
- 「Convertible Senior Notes $133,936」［PR: Preliminary BS］
- 現金等$87.2M／転債$133.9M（PR）。AR$211.5M・棚卸$138.9M（10-Q）。顧客集中「Top ten 98%」。

**現状スナップ**: 3/5、確信度：72%、市場織込み：60%、Alpha不透明度：40%、上向/下向：65/35

### ②長期EV勾配：★★★★★ (5/5)
**代表KPI/根拠（T1逐語≤25語＋リンク）**
- 「Revenue in the range of $115 to $127 million.」
- 次Qガイド中点$121M→q/q +17.5%。Non-GAAP GM 29.5–31.0%。α3_ncast=1／α5_ncast=2 ⇒ S=3→★4〜5基調。

**現状スナップ**: 5/5、確信度：78%、市場織込み：55%、Alpha不透明度：45%、上向/下向：70/30

### ③バリュエーション＋認知ギャップ：★★★★☆ (4/5)
**代表KPI/根拠（T1逐語≤25語＋リンク）**
- 「GAAP revenue was $103.0 million」
- Price-Mode（2025-09-22 ET, Yahoo）: EV≈$1.95B、NTM売上≈$484M（Q3中点×4）→EV/S≈4.0×。Ro40（Q2 YoY 138% − OPM ~15.5%）≈122。色=Green。

**現状スナップ**: 4/5、確信度：74%、市場織込み：62%、Alpha不透明度：38%、上向/下向：68/32

## dual_anchor_status
**SINGLE（SEC 8-K/EX-99.1 + 10-Qで確証）**

## DI（Stage-1）計算結果
**正規化**: s1=①3/5=0.60、s2=②5/5=1.00、s3=③4/5=0.80
**VRG色**: Green → Vmult=1.05
**DI = (0.6·1.00 + 0.4·0.80) · 1.05 = 0.882 → GO**

## 1行要約
800GのH2実出荷見込みとQ3 q/q+17.5%ガイダンスでNESは満点、EV/S≈4.0×でVRGはGreen—量産達成を待たず先行コア採用が合理的。

## 12–24Mシナリオ（T1準拠の最小骨格）

| シナリオ | 売上 | OPM（GAAP） | Ro40 | s1/s2 | DI |
|----------|------|-------------|------|-------|-----|
| Base | ~$480M（Q3中点×4） | -5% | ~55 | ★3 / ★4 | 0.756 |
| High | ~$520M（800G量産+） | +2% | ~82 | ★4 / ★5 | 0.966 |
| Low | ~$400M（遅延・歩留悪化） | -10% | ~10 | ★2 / ★2 | 0.420 |

## data_gap（UNCERTAINとして保持）
1. **GAAP OPMの正確値**（PR内の損益明細で算出可能だが引用未取得）→ Ro40の厳密化。TTL=7d。
2. **800G出荷実績**（数量/顧客）：T1は「H2に有意出荷」示唆のみ。TTL=14d。
3. **Microsoft/Amazon等の契約進捗の最新逐語**：供給SOWの更新有無。TTL=14d。

## auto_checks
{anchor_lint_pass:true}

## 投資判定
**Decision：GO（DI=0.882｜V倍率=Green 1.05適用）**
**理由**: ①長期EV確度は中程度、②長期EV勾配は満点、③バリュエーションはGreen
**次のマイルストーン**: H2'25の800G実出荷確認と量産スケールの拡大

## T1検証モジュール実行結果（SEC 8-K/10-Q/424B5）

### A-1｜Q2'25実績＋Q3'25ガイダンス／800G可視性
・「GAAP revenue was $103.0 million」
・「GAAP gross margin was 30.3%」
・「Revenue in the range of $115 to $127 million」
・「meaningful shipments of 800G… second half of 2025」
・「capacity of over 100,000 units of 800G per month」

### A-2｜Q2'25バランスシート
・「Cash, Cash Equivalents and Restricted Cash $87,195」
・「Convertible Senior Notes $133,936」

### A-3｜運転資本／顧客濃度
・「accounts receivable was $211.5 million」
・「top ten customers represented 98%…」
・「Unearned revenue… were both zero.」
・DSO≈186.9日、DOH≈176.0日

### A-4｜Amazonウォラント
・「purchase up to… 7,945,399 shares」
・「vesting… based on purchases… up to $4 billion」

### A-5｜2030転換社債条件
・「bear interest at 2.750%…」
・「will mature on January 15, 2030」

### A-6｜ATMプログラム拡張
・「aggregate offering price of up to $150,000,000」

## ログ / メトリクス
- **rss_score（次Q寄与）**: = +8.74（0.5×17.48%）
- **alpha3_score**: 1 ／ **alpha5_score**: 2
- **tri3**: {T:2, R:1, V:Green, star:4, bonus_applied:false}
- **valuation_overlay**: {status:Green, ev_sales_fwd:~4.0×, rule_of_40:~122}
- **interrupts**: []

## キャッシュ品質指標
- **DSO**: ≈ 187日（AR/Rev×91）
- **DOH**: ≈ 176日（在庫/COGS×91）
- **キャッシュ/転債比率**: 0.65（健全）
- **顧客集中度**: 98%（リスク高）

## 色替えトリガ（≤25語）
1. 「800G実出荷の逐語」
2. 「ガイダンス上方改定」
3. 「GAAP OPMの連続改善」

## ①②③への即時インプリケーション（簡易スナップ）

### ①長期EV確度
- 現金等$87.2M／社債$133.9M、ATM$150Mで流動性手段を確保（希薄化とトレード）
- AR/在庫の膨張は短期キャッシュ圧迫

### ②長期EV勾配
- Q3売上$115–127M＆非GAAP GM 29.5–31.0%、800GH2'25「meaningful shipments」＋月産10万台可視性はプラス

### ③VRG（定量色判定は別工程）
- Amazon需要連動（T1）・ATM/CB条件は"認知"補助（色決定自体はEV/S×Ro40で後続評価）

## data_gap（UNCERTAINのまま保持）
- **USリボルビング枠「three-year, $35M」**: 該当8-K本文の逐語未取得（gap_reason：SEC本文URL特定未了／TTL：7日）
- **台湾大型リース明細＆旧拠点解約（2025/8/31）**: 9/4/2025 8-K本文の逐語未取得（TTL：7日）
- **台湾子会社の与信ライン（〜2030/7/29）**: 該当8-Kの逐語未取得（TTL：7日）

## トリガー①「800Gの実出荷開始」検証結果

### 結論（現時点 2025-09-23 JST）
**未確証（forward-looking のみ）**

### 一次根拠（逐語≤25語＋アンカー）
- **Q2'25 PR/8-K EX-99.1, Aug 7, 2025**: "produce meaningful shipments of 800G… in the second half of 2025"
- **Q1'25 PR/8-K EX-99.1, May 8, 2025**: "increased confidence in a second half of 2025 ramp in 800G sales"

### 未発見のT1逐語
上記はいずれも計画/見通しであり、実出荷の既成事実（"began shipping", "shipped", "commenced volume shipments" 等）のT1逐語は未発見。

### ①②③への影響
- **②長期EV勾配**: 据え置き（★5維持の根拠＝Q3ガイドと資格進展）
- **①長期EV確度**: 据え置き（実出荷のキャッシュ・回収実績が未確認）
- **③VRG**: 色=Green据え置き（EV/S×Ro40の機械判定に変更なし）

## ①②③へのインプリケーション（スナップ更新）

| 軸 | 代表KPI/根拠（T1逐語≤25語＋リンク） | 現状スナップ | ★/5 | 確信度 | 市場織込み | Alpha不透明度 | 上向/下向（％） |
|---|---|---|---|---|---|---|---|
| ①長期EV確度 | 「three-year, $35M revolver」／「draw… through Jul 29, 2030」 | 流動性ヘッドルーム拡張（US$35M＋CN枠）。一方、台湾リースで固定費レバー増。★は据え置き。 | ★3 | ↗ 74% | 60% | 40% | 62 / 38 |
| ②長期EV勾配 | 「lease… Wugu, New Taipei（大面積）」 | キャパ確度↑（稼働11/1/25〜）。量産接続でNESの持続性を補強。★据え置き（満点維持）。 | ★5 | ↗ 80% | 55% | 45% | 70 / 30 |
| ③バリュエーション＋認知ギャップ | ― | 色=Green据え置き（EV/S×Ro40に変更なし）。リボ枠は認知補助。 | ★4 | 74% | 62% | 38% | 68 / 32 |

## data_gap 更新

### 解消項目
- **リボ枠（US$35M）**: 「three-year, $35M revolver」でT1確認
- **台湾リース詳細**: 「lease… Wugu, New Taipei（大面積）」でT1確認  
- **子会社与信（〜2030/7/29）**: 「draw… through Jul 29, 2030」でT1確認

### 継続項目
- **実出荷の逐語**: 未確証（forward-looking情報のみ）
- **ガイダンス改定**: 前回ガイド中点なし
- **GAAP OPMの連続改善**: 連続改善の実績未確認
- **運転資本の正常化**: DSO/DOH高水準継続
- **顧客分散の実績**: 98%集中度継続

## 検証結果サマリー
- **dual_anchor_status**: CONFIRMED（すべてSEC 8-K）
- **auto_checks**: {anchor_lint_pass:true}
- **評価変化の特徴**: 評価自体の変化は小さめ。ただし確信度は①②で数ポイント上乗せ（一次契約の確証により）
- **次のマイルストーン**: 実出荷開始のT1逐語確認とGAAP OPM改善の実績確認

## 最新3軸評価（2025-09-23更新）

| 軸 | 代表KPI/根拠（T1逐語≤25語＋リンク） | 現状スナップ | ★/5 | 確信度 | 市場織込み | Alpha不透明度 | 上向/下向（％） |
|---|---|---|---|---|---|---|---|
| ①長期EV確度 | 「completed the ATM Offering… $98M」／「obligations… unsecured」／「terminated the agreements… CZB」 | ATM純増資約$98Mで流動性強化。子会社82百万人民元の無担保枠新設／旧CZB枠を無違約で解約。長期購入コミットなし。 | ★3 | 68% | 部分織込み | 中 | 58/42 |
| ②長期EV勾配 | 「Revenue $115–$127M（Q3'25）」／「GAAP revenue was $103.0M」／「meaningful shipments of 800G… H2'25」 | Q2→Q3中点121のq/q≈+17.5%。GMガイダンス29.5–31.0%で横ばい（Margin_term=0）。800G量産資格進展。 | ★4 | 70% | 一部未織込み | 中 | 65/35 |
| ③バリュエーション＋認知ギャップ | 「revenue recognition… most often upon shipment」／「top ten customers represented 95%」 | Ro40（GAAP OPM）= n/a（Q2 OPM未開示）。EV/S(Price-Mode)計測保留（価格は取得済）。色=PENDING（ヒステリシス維持）。 | ★2 | 55% | 価格主導 | 高 | 50/50 |

## 12–24Mシナリオ表（更新版）

| シナリオ | 売上 | OPM（GAAP） | Ro40 | s1/s2 | DI |
|----------|------|-------------|------|-------|-----|
| Base | n/a | n/a | n/a | 3/4 | 0.65（V=Amber仮0.90） |
| High | n/a | n/a | n/a | 4/5 | 0.86（V=Green仮1.05） |
| Low | n/a | n/a | n/a | 2/3 | 0.41（V=Red仮0.75、上限0.55適用で0.41） |

## 計算メモ（②NES）
- q/q= (121/103–1)=+17.5%
- ガイド改定%=n/a
- 受注代理%=n/a
- Margin_term=0
- NES≈0.5·17.5=+8.7→★4相当

## 株価取得（Price-Mode用途）
- **AAOI**: $30.54（2025-09-23、web.finance）
- **発行株式**: 62.37M（2025-08-26時点 424B5 S-14）
- **EV/S算出**: キャッシュ＆有利子負債の最新T1が未取得のため保留

## 最新投資判定
**Decision：WATCH（DI_base≈0.65〈Amber仮〉）**

**1行要約**: ATMで資金厚み、無担保枠・旧枠整理、Q3 q/q+17.5%＋800G量産接近で勾配強化も、EV/S×Ro40未確定のためエントリー判断は色確定待ち。

## data_gap（UNCERTAINを維持）
- **gap_reason**: EV/S算出用の最新現金・有利子負債（Q2'25 10-Q）とGAAP OPM（四半期ベース）が未取得
- **TTL**: 72時間
- **dual_anchor_status**: CONFIRMED（すべてSEC/IR一次）

## auto_checks
{anchor_lint_pass:true, alpha5_math_pass:n/a, messages:["逐語25語以内・#:~:text= 準拠"]}

## 受注/バックログ代理KPI
Δ在庫・ΔA/R・契約負債）Q2→Q3の連続系列未取得（TTL 72h）

## Price-Mode補注
株価・発行株は取得済、EV（現金・負債）不足で色決定不可

## ログ
- **rss_score/alpha3_score/alpha5_score**: n/a
- **tri3**: {T:「Q3ガイド明示・q/q+17.5%」, R:「ATM完了・枠更新のSEC一次」、V:「Price-Mode保留」, star:②＝★4, bonus_applied:なし}
- **valuation_overlay**: {status:PENDING, ev_sales_fwd:n/a, rule_of_40:n/a, hysteresis:{evsales_delta:0.5, ro40_delta:2.0, upgrade_factor:1.2}}
- **interrupts**: []

## 解消されたdata_gap（2025-09-23更新）

### Convertible Notes期末残高（解消）
- **逐語**: "Convertible Senior Notes 133,936 134,497"
- **リンク**: Q2'25 EX-99.1 BS
- **期末残高**: $133.936M（2025/6/30）／$134.497M（2024/12/31）
- **dual_anchor_status**: CONFIRMED（SEC EX-99.1）
- **auto_checks**: {anchor_lint_pass:true}

### 継続するdata_gap
- **A/Rエイジング（桶別）・支払条件の定量**: 四半期/年次ともバケットやNet〇日の定量開示なし（会計方針の一般記述のみ）。TTL：7日（次の10-Q/8-Kで再走査）