# -*- coding: utf-8 -*-
from __future__ import annotations
import hashlib
from dataclasses import dataclass
from typing import Optional, Dict

@dataclass
class DualAnchor:
    anchor_primary: str  # text-fragment or canonical URL
    pageno: Optional[int] = None
    quote: Optional[str] = None  # ≤25 words raw snippet
    hash: Optional[str] = None   # sha1 of normalized snippet

    @staticmethod
    def sha1_quote(quote: str) -> str:
        norm = " ".join(quote.split())[:200]
        return hashlib.sha1(norm.encode("utf-8")).hexdigest()

    @classmethod
    def build(cls, url: str, quote: str, pageno: Optional[int] = None) -> "DualAnchor":
        return cls(anchor_primary=url, pageno=pageno, quote=quote, hash=cls.sha1_quote(quote))

    def as_dict(self) -> Dict:
        return {
            "anchor_primary": self.anchor_primary,
            "anchor_backup": {
                "pageno": self.pageno,
                "quote": self.quote,
                "hash": self.hash,
            },
        }
