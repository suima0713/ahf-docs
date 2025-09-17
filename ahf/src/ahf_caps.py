#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AHF minimal core (closed-form, no solver).
- 係数kは "参考列"用だが、この最小実装では計算のみ（表示分離の方針に沿う）。
- CEIL_CAP / SEASON_Q3GEQ_Q4 のフラグで一行式ロジックを切替。
- "最小H2"という語が紛らわしいため、本実装では "H2_at_caps" と明記。
"""

from dataclasses import dataclass
from typing import Tuple, Dict, List
import csv
import math
import sys
from pathlib import Path

# --------- Config / Flags ---------
@dataclass(frozen=True)
class Flags:
    CEIL_CAP: bool = True           # 歴史OPM上限を"固定値"として用いる（≒上限に張り付く）
    SEASON_Q3GEQ_Q4: bool = True    # 季節性：各セグメントで Q3 OPM >= Q4 OPM を課す

# --------- Core closed-form ----------
def h2_at_caps_ex_dsi(
    rev_h2_ex_dsi: float,
    elec_share: float,
    cap_elec: float,
    ugi_share: float,
    cap_ugi: float,
    q3_share: float,
    q4_share: float,
    flags: Flags
) -> float:
    """
    "上限に張り付く"前提のH2 Adj. EBITDA（ex-DSI）を閉形式で返す。
    ※ この仕様は利用者合意に基づく運用定義（純粋な最適化の"最小"ではない）。

    H2_at_caps_ex_dsi = Elec_H2_Rev * cap_elec + UGI_H2_Rev * cap_ugi
    （Q3:Q4比は結果に影響しないが、フラグ整合のため引数は受け取る）
    """
    if not (flags.CEIL_CAP and flags.SEASON_Q3GEQ_Q4):
        # 本ミニマム実装では、他フラグ組み合わせも "上限張り付き" 同一式に寄せる。
        # 余計な枝刈りを避け、常に同じ一行式で決まるよう固定。
        pass

    elec_h2_rev = rev_h2_ex_dsi * elec_share
    ugi_h2_rev  = rev_h2_ex_dsi * ugi_share
    return elec_h2_rev * cap_elec + ugi_h2_rev * cap_ugi


def full_year_adj_ebitda(
    h1_adj: float,
    h2_at_caps_ex_dsi: float,
    dsi_h2: float
) -> float:
    return h1_adj + h2_at_caps_ex_dsi + dsi_h2


def verdict_sat(
    full_year: float,
    guid_low: float,
    guid_high: float
) -> bool:
    return (full_year >= guid_low) and (full_year <= guid_high)


# --------- k（参考列用）の計算 -----------
def k_factor(
    adj_ebitda: float,
    operating_income: float
) -> float:
    """
    k = 全社Adj. EBITDA ÷ 全社Operating income
    """
    if operating_income == 0:
        return math.nan
    return adj_ebitda / operating_income


# --------- T1カタログ差分 ----------
def diff_t1(prev_csv: Path, curr_csv: Path) -> List[Dict[str, str]]:
    """
    idキーで差分（新規/削除/変更）を抽出。
    変更は excerpt40 / EDGAR_URL / unit などの文字列差異のみ簡易比較。
    """
    def read_map(p: Path) -> Dict[str, Dict[str, str]]:
        if not p.exists():
            return {}
        m = {}
        with p.open(newline='', encoding='utf-8') as f:
            r = csv.DictReader(f)
            for row in r:
                m[row.get('id','')] = row
        return m

    a = read_map(prev_csv)
    b = read_map(curr_csv)

    changes = []
    keys = set(a.keys()) | set(b.keys())
    for k in sorted(keys):
        if k not in a:
            changes.append({"id": k, "type": "ADD"})
        elif k not in b:
            changes.append({"id": k, "type": "DEL"})
        else:
            # 簡易比較（主要列のみ）
            cols = ["as_of","unit","excerpt40","EDGAR_URL","source_class"]
            changed = any((a[k].get(c,"") != b[k].get(c,"")) for c in cols)
            if changed:
                changes.append({"id": k, "type": "MOD"})
    return changes


# --------- demo run ----------
if __name__ == "__main__":
    # === 入力（必要最小限、Cursor上で直接編集して走らせる） ===
    # ガイダンス帯（Midは別途使わず、帯でSAT/UNSAT判定）
    GUID_LOW  = 2_760.0
    GUID_HIGH = 2_890.0

    # H1実績 Adj. EBITDA（USD M）
    H1_ADJ = 1_172.648

    # H2 ex-DSIの売上（USD M）
    REV_H2_EX_DSI = 14_194.0

    # セグメント構成（H2売上比）
    ELEC_SHARE = 0.675
    UGI_SHARE  = 0.325

    # Q3:Q4 季節比（ここではロジックに影響しないが引数整合のため保持）
    Q3_SHARE = 0.52
    Q4_SHARE = 0.48

    # 歴史OPM上限（FY24 10-Kより）
    CAP_ELEC = 0.111
    CAP_UGI  = 0.104

    # DSI H2（3点: low/mid/high）
    DSI_ARR = [45.0, 50.0, 55.0]  # USD M

    flags = Flags(CEIL_CAP=True, SEASON_Q3GEQ_Q4=True)

    h2_caps = h2_at_caps_ex_dsi(
        REV_H2_EX_DSI, ELEC_SHARE, CAP_ELEC, UGI_SHARE, CAP_UGI, Q3_SHARE, Q4_SHARE, flags
    )

    print("=== H2_at_caps (ex-DSI) ===")
    print(f"{h2_caps:,.1f} M")

    print("\n=== Full-year total & Verdict ===")
    for dsi in DSI_ARR:
        total = full_year_adj_ebitda(H1_ADJ, h2_caps, dsi)
        sat   = verdict_sat(total, GUID_LOW, GUID_HIGH)
        print(f"DSI {dsi:>5.1f} → {total:>8.1f} M  | Verdict: {'SAT' if sat else 'UNSAT'}")

    # T1差分の例（存在しない場合はスキップ）
    prev = Path(__file__).resolve().parents[1] / "data" / "t1_catalog_prev.csv"
    curr = Path(__file__).resolve().parents[1] / "data" / "t1_catalog.csv"
    changes = diff_t1(prev, curr)
    print("\n=== T1 Δ (prev vs curr) ===")
    if not changes:
        print("(no diff)")
    else:
        for ch in changes:
            print(f"{ch['type']}: {ch['id']}")
