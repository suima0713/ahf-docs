# PDFS Stage-2 Deep-first with interrupts 出力

## 現在地（人向け）

### **Action**: NO-GO

### **要点**: 
- **α3**: モデルと−4.9pp乖離（閾値0.2pp超過）→ **FAIL**（ただしMD&A説明でPASS_EXPLAINEDタグ）
- **α5**: 改善の素地なし（median−actual=−$1.41M、閾値-$3M未達）→ **FAIL**

### **次のトリガー**: 
- 原価沈静化（CoR非GAAPの鈍化）確認
- CL↑・CA↓の反転確認
- Item1A No change維持

### **Interrupt**: BALANCE_WEAK（CL↓ & CA↑）

## 詳細分析結果

### α3分析（Mix→GM予測）
- **ドリフト**: -4.9pp（閾値0.2pp超過）
- **残差GP**: $2.53M（閾値$8M以内）
- **MD&A説明**: Q2 10-Q本文で原因カテゴリを明文で取得完了
- **ステータス**: **FAIL**（PASS_EXPLAINEDタグ）

### α5分析（OpEx改善）
- **実績OpEx**: $35.725M
- **グリッド中央値**: $34.313M
- **改善余地**: -$1.41M（閾値-$3M未達）
- **ステータス**: **FAIL**

### WATCH条件
- **Item1A**: No change（PASS）
- **CL**: 27.131 → 23.363（↓13.9%）
- **CA**: 6.928 → 8.167（↑17.9%）
- **判定**: CL↓/CA↑で補助条件未成立

### 中断コード
- **A3_UNEXPLAINED**: なし（MD&A説明取得済み）
- **BALANCE_WEAK**: あり（CL↓ & CA↑）
- **ITEM1A_CHANGE**: なし
- **ANCHOR_FAIL**: なし

## 運用トーン

**NO-GO**: α3とα5の両方で機械ゲート不合格。売上Mixは良化したが、非Mixコスト増がGMを押し下げ、OpEx面の余地も不足。

**現時点は"見送り"**が妥当。
