"""
modules/tp/tp_pips.py
──────────────────────
TP Module: TP Pips (cố định)

Đặt TP cách entry một số pips cố định.

Logic:
- BUY  → TP = entry + (pips × pip_size)
- SELL → TP = entry − (pips × pip_size)

Tham số:
- pips     (float, mặc định 30.0):    Số pips TP.
- pip_size (float, mặc định 0.0001).
"""

from __future__ import annotations

import pandas as pd

from modules.base import ITPModule, Signal


class TpPips(ITPModule):
    MODULE_NAME = "TP Pips"

    def __init__(self, pips: float = 30.0, pip_size: float = 0.0001):
        self.pips     = pips
        self.pip_size = pip_size

    @property
    def name(self) -> str:
        return self.MODULE_NAME

    def get_tp(
        self,
        df: pd.DataFrame,
        idx: int,
        direction: Signal,
        sl_price: float,
    ) -> float:
        entry = float(df.iloc[idx].close)
        dist  = self.pips * self.pip_size

        if direction == Signal.BUY:
            return round(entry + dist, 6)
        if direction == Signal.SELL:
            return round(entry - dist, 6)
        return 0.0
