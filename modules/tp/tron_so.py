"""
modules/tp/tron_so.py
──────────────────────
TP Module: Tròn số

Đặt TP tại số tròn gần nhất theo chiều lệnh.

Logic:
- BUY  → TP = số tròn gần nhất phía TRÊN entry − buffer
         (dừng trước số tròn vì thường gặp kháng cự ở đó)
- SELL → TP = số tròn gần nhất phía DƯỚI entry + buffer

Tham số:
- round_level  (float, mặc định 0.01):   Bước số tròn.
- buffer_pips  (float, mặc định 1.0):    Dừng trước số tròn (pips).
- pip_size     (float, mặc định 0.0001).
"""

from __future__ import annotations

import pandas as pd

from modules.base import ITPModule, Signal


class TronSoTp(ITPModule):
    MODULE_NAME = "Tròn số"

    def __init__(
        self,
        round_level: float = 0.01,
        buffer_pips: float = 1.0,
        pip_size:    float = 0.0001,
    ):
        self.round_level = round_level
        self.buffer      = buffer_pips * pip_size

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
        entry   = float(df.iloc[idx].close)
        nearest = round(entry / self.round_level) * self.round_level

        if direction == Signal.BUY:
            tp_round = nearest if nearest > entry else nearest + self.round_level
            return round(tp_round - self.buffer, 6)

        if direction == Signal.SELL:
            tp_round = nearest if nearest < entry else nearest - self.round_level
            return round(tp_round + self.buffer, 6)

        return 0.0
