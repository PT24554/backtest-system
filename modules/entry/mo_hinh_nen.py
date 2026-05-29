"""
modules/entry/mo_hinh_nen.py
─────────────────────────────
Entry Module: Mô hình nến

Nhận dạng các mô hình nến Nhật phổ biến để xác định tín hiệu đảo chiều.

Mô hình hỗ trợ:
  "hammer"          → BUY  (Búa)
  "shooting_star"   → SELL (Sao băng)
  "bull_engulfing"  → BUY  (Nhấn chìm tăng)
  "bear_engulfing"  → SELL (Nhấn chìm giảm)
  "doji_reversal"   → BUY/SELL (Doji đảo chiều — cần ngữ cảnh 3 nến trước)

Tham số:
- patterns (list[str] | None): danh sách mô hình kích hoạt (mặc định: tất cả).
- min_body_ratio (float, mặc định 0.1): thân nến tối thiểu (tránh false positive).
"""

from __future__ import annotations

import pandas as pd

from modules.base import IEntryModule, Signal


_ALL = ["hammer", "shooting_star", "bull_engulfing", "bear_engulfing", "doji_reversal"]


class MoHinhNenEntry(IEntryModule):
    MODULE_NAME = "Mô hình nến"

    def __init__(
        self,
        patterns:       list[str] | None = None,
        min_body_ratio: float            = 0.1,
    ):
        self.patterns       = patterns if patterns is not None else list(_ALL)
        self.min_body_ratio = min_body_ratio

    @property
    def name(self) -> str:
        return self.MODULE_NAME

    # ── Pattern helpers ────────────────────────────────────────────────────────

    @staticmethod
    def _body(r)        -> float: return abs(r.close - r.open)
    @staticmethod
    def _full(r)        -> float: return r.high - r.low
    @staticmethod
    def _upper_wick(r)  -> float: return r.high - max(r.open, r.close)
    @staticmethod
    def _lower_wick(r)  -> float: return min(r.open, r.close) - r.low

    def _hammer(self, r) -> bool:
        body, full = self._body(r), self._full(r)
        if full == 0: return False
        return (self._lower_wick(r) >= 2 * body
                and self._upper_wick(r) <= 0.4 * body
                and body / full >= self.min_body_ratio)

    def _shooting_star(self, r) -> bool:
        body, full = self._body(r), self._full(r)
        if full == 0: return False
        return (self._upper_wick(r) >= 2 * body
                and self._lower_wick(r) <= 0.4 * body
                and body / full >= self.min_body_ratio)

    @staticmethod
    def _bull_engulfing(prev, curr) -> bool:
        return (prev.close < prev.open           # prev giảm
                and curr.close > curr.open       # curr tăng
                and curr.open  <= prev.close     # mở thấp hơn đáy prev
                and curr.close >= prev.open)     # đóng cao hơn đỉnh prev

    @staticmethod
    def _bear_engulfing(prev, curr) -> bool:
        return (prev.close > prev.open           # prev tăng
                and curr.close < curr.open       # curr giảm
                and curr.open  >= prev.close     # mở cao hơn đỉnh prev
                and curr.close <= prev.open)     # đóng thấp hơn đáy prev

    def _is_doji(self, r) -> bool:
        full = self._full(r)
        return full > 0 and self._body(r) / full < 0.1

    # ── Main check ────────────────────────────────────────────────────────────

    def check(self, df: pd.DataFrame, idx: int) -> Signal:
        row  = df.iloc[idx]
        prev = df.iloc[idx - 1] if idx > 0 else None

        if "hammer" in self.patterns and self._hammer(row):
            return Signal.BUY

        if "shooting_star" in self.patterns and self._shooting_star(row):
            return Signal.SELL

        if prev is not None:
            if "bull_engulfing" in self.patterns and self._bull_engulfing(prev, row):
                return Signal.BUY
            if "bear_engulfing" in self.patterns and self._bear_engulfing(prev, row):
                return Signal.SELL

        if "doji_reversal" in self.patterns and self._is_doji(row) and idx >= 3:
            recent   = df.iloc[idx - 3 : idx]
            all_down = all(r.close < r.open for _, r in recent.iterrows())
            all_up   = all(r.close > r.open for _, r in recent.iterrows())
            if all_down: return Signal.BUY
            if all_up:   return Signal.SELL

        return Signal.NONE
