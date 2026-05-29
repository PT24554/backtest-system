"""
modules/entry/tron_so.py
─────────────────────────
Entry Module: Tròn số

Vào lệnh khi giá đang ở gần một mức tròn số (số chẵn).

Logic:
- Tìm số tròn gần nhất (bội của round_level).
- Nếu giá close nằm trong vùng ±tolerance_pips:
    → Dùng màu nến để xác định chiều: BUY (nến tăng) / SELL (nến giảm).
- Nếu giá không gần số tròn nào → NONE.

Ví dụ: round_level=0.01, EURUSD → kiểm tra 1.2900, 1.3000, 1.3100, ...

Tham số:
- round_level     (float, mặc định 0.01):   Bước của số tròn (0.01 = mỗi 100 pips).
- tolerance_pips  (float, mặc định 5.0):    Vùng cho phép xung quanh số tròn.
- pip_size        (float, mặc định 0.0001): Giá trị 1 pip.
- min_body_ratio  (float, mặc định 0.2):    Tỉ lệ thân nến tối thiểu.
"""

from __future__ import annotations

import pandas as pd

from modules.base import IEntryModule, Signal


class TronSoEntry(IEntryModule):
    MODULE_NAME = "Tròn số"

    def __init__(
        self,
        round_level:    float = 0.01,
        tolerance_pips: float = 5.0,
        pip_size:       float = 0.0001,
        min_body_ratio: float = 0.2,
    ):
        self.round_level    = round_level
        self.tolerance      = tolerance_pips * pip_size
        self.min_body_ratio = min_body_ratio

    @property
    def name(self) -> str:
        return self.MODULE_NAME

    def check(self, df: pd.DataFrame, idx: int) -> Signal:
        row   = df.iloc[idx]
        price = row.close

        nearest = round(price / self.round_level) * self.round_level
        if abs(price - nearest) > self.tolerance:
            return Signal.NONE

        body = abs(row.close - row.open)
        full = row.high - row.low
        if full > 0 and body / full < self.min_body_ratio:
            return Signal.NONE

        return Signal.BUY if row.close > row.open else Signal.SELL
