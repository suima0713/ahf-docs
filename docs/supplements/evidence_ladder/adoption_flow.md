# 採用フロー（T1 / T1* / T2）

1) 候補取得 → AnchorLint（≤25語＋`#:~:text=`）  
2) 分類：T1（SEC/IR）／T1*（独立2源一致）／T2（単独二次）  
3) タグ付け：`evidence_tag`／`dual_anchor_status`  
4) 反映：
   - T1/T1*：★/DIに反映可（③Vmult／④FD%含む）
   - T2：★不可。**確信度±10pp（1回）**・織込み・注釈のみ
5) 追跡：
   - T1*：**ttl_days=14**でT1確認をスケジュール
6) ログ：`auto_checks.anchor_lint_t1star_pass` 等を記録
