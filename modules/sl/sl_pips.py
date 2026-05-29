"""
modules/sl/sl_pips.py
──────────────────────
SL Module: SL Pips (cố định)

Đặt SL cách entry một số pips cố định.

Logic:
- BUY  → SL = entry − (pips × pip_size)
- SELL → SL = entry + (pips × pip_size)

Tham số:
- pips     (float, mặc định 20.0):    Số pips SL.
- pip_size (float, mặc định 0.0001).
"""

from __future__ import annotations

import pandas as pd

from modules.base import ISLModule, Signal


class SlPips(ISLModule):
    MODULE_NAME = "SL Pips"

    def __init__(self, pips: float = 20.0, pip_size: float = 0.0001):
        self.pips     = pips
        self.pip_size = pip_size

    @property
    def name(self) -> str:
        return self.MODULE_NAME

    def get_sl(self, df: pd.DataFrame, idx: int, direction: Signal) -> float:
        entry = float(df.iloc[idx].close)
        dist  = self.pips * self.pip_size

        if direction == Signal.BUY:
            return round(entry - dist, 6)
        if direction == Signal.SELL:
            return round(entry + dist, 6)
        return 0.0
