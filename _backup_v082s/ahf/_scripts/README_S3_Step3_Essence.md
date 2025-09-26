# S3-Step3-Essence - ③二段構え（最小・実戦用）

## 概要

**③二段構え（最小・実戦用）**の本質実装です。超高PERは「先取りされた成長力と継続性」が妥当かどうかでしか正当化できません。

## ③二段構え（最小・実戦用）

### Step-1｜フェアバリュー差（素点）

**狙い**：市場が"今"つけているプレミアムがどれだけ大きいか/小さいか。

**やること**：
1. ピアEV/S（またはPE）中央値と比較（Peer Multiple）
2. 逆DCFライトで"フェア"を置く（T1の g_fwd・OPM_fwd だけ）
3. 上の大きい方を基準値にして**割引率 Disc%**を出す

**結論の使い方**：Disc%で色/Vmultを機械決定（Green/Amber/Red）。ここは感情を入れない。

### Step-2｜妥当性チェック（期待の正当性）

**狙い**：その割安/割高が**将来の実力（認知ギャップ/耐性）**で正当化できるか。

**やること（T1だけ）**：
1. 期待成長の相対差：Δg = g_fwd − g_peer_median
2. 認知フラグ（＋：ガイダンス上方・実出荷・前受/契約負債↑・ATM未実行／−：acceptance要件・在庫滞留・集中悪化・希薄化）
3. 判定：Under/Over （適正 or 不適正）のラベルだけ付ける。色は変えない。

→ どう"売買"するかはStep-1の色×Step-2のラベルで決める。

## 「高PERは何を要請しているか？」を一撃で見る式（逆DCFライト）

5年で"市場並みPER"に収斂すると仮定した時に必要なEPS成長：

```
EPS_CAGR_req = ((PE_now / PE_target) · (1 + hurdle)^5)^(1/5) − 1
```

**例**：
- PE_now=60, PE_target=25, hurdle=12%
- 係数 = (60/25)×1.12^5 ≈ 2.4×1.762 ≈ 4.23
- EPS_CAGR_req ≈ 33%
- ⇒ 5年でEPS年率33%を持続できる"証拠"がT1にどれだけあるか、が勝負

同様に PE_now=100 なら… 必要CAGRは≳40% と一気にハードルが跳ね上がる。

## 何を"証拠"にするか（T1だけ）

### 継続性
- NRR/GRR、RPO/契約負債の伸び＞売上伸び、リテンション/コホート曲線

### 単位経済
- LTV/CAC>3、粗利↑＆販管費率↓でOPM+50bps×連続

### 集中/希薄化
- 10%超顧客分散、ATM未実行/希薄化<2%/年

### 規制/為替/在庫
- acceptanceなし、在庫回転/DSO改善

**ここが揃えば**「先取り期待は妥当」＝高PERでも買える。**揃わなければ**期待倒れ＝売り/回避。

## 使用方法

### PowerShell実行例

```powershell
# ③二段構え（最小・実戦用）の完全評価
.\Start-S3Step3Essence.ps1 -Action essence -PEActual 60.0 -PEPeerMedian 25.0 -GFwd 30.0 -OPMFwd 15.0 -GPeerMedian 20.0 -Evidence "ガイダンス上方, 実出荷, 前受, 契約負債↑, NRR/GRR, LTV/CAC>3, 10%超顧客分散 #:~:text=ガイダンス上方"

# 高PER分析（逆DCFライト）
.\Start-S3Step3Essence.ps1 -Action high_per -PEActual 100.0 -PETarget 25.0 -Hurdle 0.12

# Step-1のみ
.\Start-S3Step3Essence.ps1 -Action step1 -PEActual 60.0 -PEPeerMedian 25.0 -GFwd 30.0 -OPMFwd 15.0

# Step-2のみ
.\Start-S3Step3Essence.ps1 -Action step2 -GFwd 30.0 -GPeerMedian 20.0 -Evidence "ガイダンス上方, 実出荷, 前受, 契約負債↑ #:~:text=ガイダンス上方"

# 証拠基準評価
.\Start-S3Step3Essence.ps1 -Action evidence -Evidence "NRR/GRR, LTV/CAC>3, 10%超顧客分散, acceptanceなし #:~:text=NRR"
```

### Python直接実行

```python
from s3_step3_essence import S3Step3Essence

s3 = S3Step3Essence()

# ③二段構え（最小・実戦用）の完全評価
essence_display = s3.get_step3_essence_display(
    pe_actual=60.0,  # 高PER例
    pe_peer_median=25.0,
    g_fwd=30.0,
    opm_fwd=15.0,
    g_peer_median=20.0,
    evidence="ガイダンス上方, 実出荷, 前受, 契約負債↑, NRR/GRR, LTV/CAC>3, 10%超顧客分散 #:~:text=ガイダンス上方"
)
print(essence_display)

# 高PER分析
high_per_analysis = s3.get_high_per_analysis(100.0)  # 超高PER例
print(high_per_analysis)
```

## ファイル構成

```
ahf/_scripts/
├── s3_step3_essence.py        # S3-Step3-Essence実装
├── Start-S3Step3Essence.ps1   # PowerShellランチャー
└── README_S3_Step3_Essence.md # このファイル
```

## まとめ

**あなたの主張＝完全に正しい。**

Step-1で温度（割安/割高）を機械算出 → Step-2で妥当性（証拠）をT1で判定。

これでPLTR/DUOL/APPの"高PERが稼げるか"を短く・一貫して決められます。
やろうと思えば、この枠で今すぐ3社にも当て込めます（T1の数値を拾うだけでOK）。

## 注意事項

- 全ての説明は日本語で行う
- カーソルルールは常時遵守
- 変更時は必ずこのファイルを更新
- 新しいルール追加時はChair承認必須
- **③二段構え（最小・実戦用）の本質を完全実装**
