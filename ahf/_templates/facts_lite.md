# AHF-Lite Facts (UPST)

## C (Confirmed / T1) - EDGAR逐語のみ

[AS-OF 2025-06-30][C][Credit] "Realized losses on loans sold... $7.2 million."
Unit: USD / Section: Note 4 / URL: <EDGAR直URL>

[AS-OF 2025-06-30][C][Funding] "The revolving credit facility has a total capacity of $500.0 million..."
Unit: USD / Section: Note 8 / URL: <EDGAR直URL>

[AS-OF 2025-06-30][C][Origination] "Loan purchases totaled $288.4 million..."
Unit: USD / Section: 8-K EX-99.1 / URL: <EDGAR直URL>

[AS-OF 2025-06-30][C][Portfolio] "Loans held for sale at fair value... $1.020 billion"
Unit: USD / Section: Note 4 / URL: <EDGAR直URL>

[AS-OF 2025-06-30][C][Credit] "Nonaccrual loans... 2.3% of total loans"
Unit: percent / Section: Note 4 / URL: <EDGAR直URL>

## W (Watch) - 仮説・未確証

[AS-OF 2025-09-02][W][ABS] "ABS-15G filed with Ex.99.1 (AUP)."
Unit: text / Section: Item 2.01 / URL: <EDGAR直URL> / ttl:14 / trigger:10-D/8-K/424B出現

[AS-OF 2025-09-02][W][Funding] "Forward-flow agreement with Fortress (unconfirmed)."
Unit: text / Section: Note / URL: <source_note> / ttl:7 / trigger:8-K/Ex-10.xx未出

## 運用ルール

### C (Confirmed) - 100%反映
- EDGAR原文の逐語のみ（≤40語）
- as-of/Unit/Section/直URL必須
- 数値はCに限って記録

### P (Probable) - 25%相当の先行
- 一次未確定だが有力（2独立ソース/整合/反証なし）
- ttl切れ or 反証で即ゼロ

### W (Watch) - 0%（監視のみ）
- 仮説・未確証
- 数行の根拠メモ＋監視トリガのみ

### 昇格/降格ルール
- P→C: EDGARに同一または同等逐語登場
- P→W: ttl失効 or 反証
- W→P: 二次だが独立×2の整合を得たら
