# AHF v0.8.1-r2 事実テンプレート
# T1/T1*確定事実（固定4軸対応）

## 基本情報
- 銘柄: 
- 評価日: YYYY-MM-DD
- バージョン: v0.8.1-r2
- 目的: 投資判断に直結する固定4軸で評価
- MVP: ①②③④の名称と順序を絶対固定／T1 or T1*で確証（不足はn/a）／定型テーブル＋1行要約を即出力

## 証拠階層
- **T1**: 一次（SEC/IR）
- **T1***: Corroborated二次（独立2源以上）
- **T2**: 二次1源

## 固定4軸事実

### ①長期EV確度（LEC）
```
[YYYY-MM-DD][T1-F|T1-P|T1-C][Core①] "逐語" (impact: LEC) <src>
```

### ②長期EV勾配（NES）
```
[YYYY-MM-DD][T1-F|T1-P|T1-C][Core②] "逐語" (impact: NES) <src>
```

### ③現バリュエーション（機械）
```
[YYYY-MM-DD][T1-F|T1-P|T1-C][Core③] "逐語" (impact: Current_Val) <src>
```

### ④将来EVバリュ（総合）
```
[YYYY-MM-DD][T1-F|T1-P|T1-C][Core④] "逐語" (impact: Future_Val) <src>
```

## 証拠タグ規約
- **T1-F**: T1-Financial（財務データ）
- **T1-P**: T1-Product（製品・サービス）
- **T1-C**: T1-Corporate（企業情報）
- **Core①**: 長期EV確度関連
- **Core②**: 長期EV勾配関連
- **Core③**: 現バリュエーション関連
- **Core④**: 将来EVバリュ関連

## 逐語要件
- 逐語は本文から取得
- ≤25語（見出し・目次不可）
- URLアンカー #:~:text= 必須
- PDFは anchor_backup{pageno,quote,hash}

## 証拠階層要件
- **T1**: SEC EDGAR または Company IR
- **T1***: 独立2源以上、異ドメイン、相互転載でない、T1と非矛盾
- **T2**: 二次1源（逐語＋URL）

## データギャップ
- データ不足時は `data_gap: true` を記録
- ギャップ理由を `gap_reason` に記録
- T1*証拠のTTL≤14日で追跡

## 注意事項
- 全ての事実はT1/T1*のみ記録
- 非T1は backlog.md に記録
- 矛盾フラグは triage.json に記録
- 二重アンカー待機は PENDING_SEC で記録
