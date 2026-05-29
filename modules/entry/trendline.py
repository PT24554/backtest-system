"""
modules/entry/trendline.py
───────────────────────────
Entry Module: Trendline

Vào lệnh khi giá chạm / phá vỡ đường trendline.

Logic:
- Xác định swing highs trong lookback nến → vẽ downtrend line (kháng cự).
- Xác định swing lows trong lookback nến  → vẽ uptrend line (hỗ trợ).
- BUY  nếu giá chạm uptrend line (hỗ trợ) và nến tăng.
- SELL nếu giá chạm downtrend line (kháng cự) và nến giảm.

Tham số:
- lookback        (int,   mặc định 50):    Số nến nhìn lại.
- swing_window    (int,   mặc định 5):     Số nến mỗi bên để xác định swing.
- tolerance_pips  (float, mặc định 3.0):   Vùng chấp nhận quanh trendline (pips).
- pip_size        (float, mặc định 0.0001).
"""

from __future__ import annotations

import pandas as pd

from modules.base import IEntryModule, Signal


class TrendlineEntry(IEntryModule):
    MODULE_NAME = "Trendline"

    def __init__(
        self,
        lookback:       int   = 50,
        swing_window:   int   = 5,
        tolerance_pips: float = 3.0,
        pip_size:       float = 0.0001,
    ):
        self.lookback     = lookback
        self.swing_window = swing_window
        self.tolerance    = tolerance_pips * pip_size

    @property
    def name(self) -> str:
        return self.MODULE_NAME

    # ── Helpers ────────────────────────────────────────────────────────────────

    @staticmethod
    def _is_swing_high(arr: list, i: int, w: int) -> bool:
        if i < w or i >= len(arr) - w:
            return False
        return all(arr[i] >= arr[j] for j in range(i - w, i + w + 1) if j != i)

    @staticmethod
    def _is_swing_low(arr: list, i: int, w: int) -> bool:
        if i < w or i >= len(arr) - w:
            return False
        return all(arr[i] <= arr[j] for j in range(i - w, i + w + 1) if j != i)

    @staticmethod
    def _trendline_at(p1: tuple, p2: tuple, at: int) -> float:
        """Nội suy giá trị trendline tại vị trí at."""
        i1, y1 = p1
        i2, y2 = p2
        if i2 == i1:
            return y1
        return y1 + (y2 - y1) / (i2 - i1) * (at - i1)

    # ── Main check ────────────────────────────────────────────────────────────

    def check(self, df: pd.DataFrame, idx: int) -> Signal:
        start = max(0, idx - self.lookback)
        sub   = df.iloc[start : idx + 1]
        n     = len(sub)
        w     = self.swing_window

        if n < w * 2 + 3:
            return Signal.NONE

        row    = df.iloc[idx]
        price  = row.close
        last_i = n - 1

        highs = sub["high"].values.tolist()
        lows  = sub["low"].values.tolist()

        # ── Downtrend line qua swing highs → tín hiệu SELL ───────────────────
        sh = [(i, highs[i]) for i in range(n) if self._is_swing_high(highs, i, w)]
        if len(sh) >= 2:
            tl_price = self._trendline_at(sh[-2], sh[-1], last_i)
            if abs(price - tl_price) <= self.tolerance and row.close < row.open:
                return Signal.SELL

        # ── Uptrend line qua swing lows → tín hiệu BUY ───────────────────────
        sl = [(i, lows[i]) for i in range(n) if self._is_swing_low(lows, i, w)]
        if len(sl) >= 2:
            tl_price = self._trendline_at(sl[-2], sl[-1], last_i)
            if abs(price - tl_price) <= self.tolerance and row.close > row.open:
                return Signal.BUY

        return Signal.NONE
