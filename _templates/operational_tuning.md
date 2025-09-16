# 運用チューニング（最小・即適用）

## 役割固定

### 本文（A/B/C）＝T1だけ（羅針盤）
- **A｜材料**: T1逐語≤40語のみ（直URL・節名・as-of・ユニット）
- **B｜総合判断**: Horizon別に結論（Buy/Hold/Sell）を同時に出す
- **C｜反証**: Time off／+0.5Q／売上↔GM/CF整合の3テストのみ

### Decision Overlay＝構造①×傾き②×バリュV×時間③
- **構造①**: TAM/非代替
- **傾き②**: 収益質
- **バリュV**: ΔIRR
- **時間③**: Horizon

### 交差禁止
**Overlayは本文に混ぜない**

## T1カバレッジ目標（目安）
- **6M**: ≥70%
- **1Y**: ≥80%  
- **3Y+**: ≥90%

※"件数"ではなくKPIを閉じ切る割合

## IDCCの"いまの欠け"＝ギャップ源

### Coverage分子
**RPO"同等"の総量**（NTM％はNTM償却178.3mで部分充足）

### Coverage分母  
**FY26 mid**（EX-99.1/Outlook）

→ この2つが埋まれば、OverlayのΔIRRが定量で閉じ、認知ギャップに最大レバ

## いま即やること（T1を"7→9割"へ）

### 1. RPO"同等"の総量（10-Q/10-K/Note/MD&A）
- **ゴール**: contracted_revenue_total or minimum_guarantees_total の単一数値（as-of/単位/節名/直URL）
- **成否ルール**: 見つからなければ T1: not_found を逐語で確定（"未開示という事実"をT1化）

### 2. FY26 mid（EX-99.1「Financial Outlook」）
- **ゴール**: guidance_fy26_revenue_mid（USD、mid抽出）
- **成否ルール**: FY25のみの逐語をT1化し、FY26はnot_foundを確定（分母の空白を明示）

### 3. Note3ロールの継続監査（開示更新ごとに式一致：opening＋additions−recognized＝ending）
- **ゴール**: contract_liabilities_roll_check=match を維持（質②の担保）

## マトリクス上の置き場（ぶれ防止）

### A｜材料
上の3テーマの逐語≤40語のみ（直URL・節名・as-of・ユニット）

### B｜総合判断
Horizon別に結論（Buy/Hold/Sell）を同時に出す
- 例）6M＝Hold、1Y＝Buy（〔Time〕窓=2Q）、3Y＝Buy/Hold、5Y＝Trim

**KPI×2固定**:
1. **Coverage**（RPO≤12M / FY26 mid）
2. **Contract liabilitiesロール"match"**

### C｜反証
Time off／+0.5Q／売上↔GM/CF整合の3テストのみ

## 期待ギャップの捉え方（T1を厚くする効用）

### T1を5割→9割に厚く
- **外れやすい前提**（噂・感触）が消え、Overlay（S×Q×V）の自由度が上がる（=大胆な仮説でも"根本から否定されにくい"）
- **未開示の穴**をT1: not_foundで"事実として固定"でき、市場の思い込みと差が可視化される

### だから
あなたの長期仮説（TAM成長×非代替×需要粘着）はOverlayで主役、T1は"基準線を9割まで塗る"ことでレバ比を最大化します
