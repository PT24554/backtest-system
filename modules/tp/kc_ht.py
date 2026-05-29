"""
modules/tp/kc_ht.py
────────────────────
TP Module: KC-HT (Kháng cự – Hỗ trợ)

Đặt TP tại mức kháng cự / hỗ trợ tiếp theo.

Logic:
- BUY  → TP = resistance gần nhất phía TRÊN entry − buffer
- SELL → TP = support gần nhất phía DƯỚI entry + buffer

Tham số:
- lookback      (int,   mặc định 100):    Số nến nhìn lại.
- swing_window  (int,   mặc định 5):      Cửa sổ xác định swing.
- buffer_pips   (float, mặc định 1.0):    Dừng trước mức S/R (pips).
- pip_size      (float, mặc định 0.0001).
"""

from __future__ import annotations

import pandas as pd

from modules.base import ITPModule, Signal


class KCHTTp(ITPModule):
    MODULE_NAME = "KC-HT"

    def __init__(
        self,
        lookback:     int   = 100,
        swing_window: int   = 5,
        buffer_pips:  float = 1.0,
        pip_size:     float = 0.0001,
    ):
        self.lookback     = lookback
        self.swing_window = swing_window
        self.buffer       = buffer_pips * pip_size

    @property
    def name(self) -> str:
        return self.MODULE_NAME

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _find_levels(
        self, df: pd.DataFrame, idx: int
    ) -> tuple[list[float], list[float]]:
        start = max(0, idx - self.lookback)
        sub   = df.iloc[start:idx]
        w     = self.swing_window
        highs = sub["high"].values
        lows  = sub["low"].values

        supports:    list[float] = []
        resistances: list[float] = []

        for i in range(w, len(sub) - w):
            if all(highs[i] >= highs[j] for j in range(i - w, i + w + 1) if j != i):
                resistances.append(float(highs[i]))
            if all(lows[i] <= lows[j] for j in range(i - w, i + w + 1) if j != i):
                supports.append(float(lows[i]))

        return supports, resistances

    # ── Main ──────────────────────────────────────────────────────────────────

    def get_tp(
        self,
        df: pd.DataFrame,
        idx: int,
        direction: Signal,
        sl_price: float,
    ) -> float:
        if idx < self.swing_window * 2 + 2:
            return 0.0

        entry                 = float(df.iloc[idx].close)
        supports, resistances = self._find_levels(df, idx)

        if direction == Signal.BUY:
            candidates = [r for r in resistances if r > entry]
            if not candidates:
                return 0.0
            return round(min(candidates) - self.buffer, 6)

        if direction == Signal.SELL:
            candidates = [s for s in supports if s < entry]
            if not candidates:
                return 0.0
            return round(max(candidates) + self.buffer, 6)

        return 0.0
