"""
modules/tp/tp_rr.py
────────────────────
TP Module: TP R:R (Risk-Reward cố định)

Đặt TP theo tỉ lệ R:R so với khoảng cách SL.

Logic:
- tp_distance = |entry − sl_price| × rr_ratio
- BUY  → TP = entry + tp_distance
- SELL → TP = entry − tp_distance

Ví dụ: SL = 20 pips, R:R = 2.0 → TP = 40 pips.

Tham số:
- rr_ratio (float, mặc định 2.0): Tỉ lệ TP / SL distance.
"""

from __future__ import annotations

import pandas as pd

from modules.base import ITPModule, Signal


class TpRR(ITPModule):
    MODULE_NAME = "TP R:R"

    def __init__(self, rr_ratio: float = 2.0):
        self.rr_ratio = rr_ratio

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
        if sl_price == 0.0:
            return 0.0

        entry   = float(df.iloc[idx].close)
        sl_dist = abs(entry - sl_price)

        if sl_dist == 0.0:
            return 0.0

        tp_dist = sl_dist * self.rr_ratio

        if direction == Signal.BUY:
            return round(entry + tp_dist, 6)
        if direction == Signal.SELL:
            return round(entry - tp_dist, 6)
        return 0.0
