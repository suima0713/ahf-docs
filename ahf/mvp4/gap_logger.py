# -*- coding: utf-8 -*-
from typing import Dict

VALID = {"NOT_DISCLOSED", "DIFF_PERIOD", "TAG_ABSENT", "PHRASE_NOT_FOUND"}


def gap(field: str, reason: str, ttl_days: int = 30) -> Dict:
    if reason not in VALID:
        reason = "NOT_DISCLOSED"
    return {
        "field": field,
        "status": "data_gap",
        "reason": reason,
        "ttl_days": int(ttl_days),
    }
