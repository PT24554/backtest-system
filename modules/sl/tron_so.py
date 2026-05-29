"""
modules/sl/tron_so.py
──────────────────────
SL Module: Tròn số

Đặt SL tại số tròn gần nhất theo chiều ngược lại.

Logic:
- BUY  → SL = số tròn gần nhất phía DƯỚI entry − buffer
- SELL → SL = số tròn gần nhất phía TRÊN entry + buffer

Tham số:
- round_level  (float, mặc định 0.01):   Bước số tròn.
- buffer_pips  (float, mặc định 2.0):    Khoảng đệm thêm (pips).
- pip_size     (float, mặc định 0.0001).
"""

from __future__ import annotations

import pandas as pd

from modules.base import ISLModule, Signal


class TronSoSl(ISLModule):
    MODULE_NAME = "Tròn số"

    def __init__(
        self,
        round_level: float = 0.01,
        buffer_pips: float = 2.0,
        pip_size:    float = 0.0001,
    ):
        self.round_level = round_level
        self.buffer      = buffer_pips * pip_size

    @property
    def name(self) -> str:
        return self.MODULE_NAME

    def get_sl(self, df: pd.DataFrame, idx: int, direction: Signal) -> float:
        entry   = float(df.iloc[idx].close)
        nearest = round(entry / self.round_level) * self.round_level

        if direction == Signal.BUY:
            sl_round = nearest if nearest < entry else nearest - self.round_level
            return round(sl_round - self.buffer, 6)

        if direction == Signal.SELL:
            sl_round = nearest if nearest > entry else nearest + self.round_level
            return round(sl_round + self.buffer, 6)

        return 0.0
