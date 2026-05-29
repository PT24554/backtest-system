"""
modules/entry/nen.py
─────────────────────
Entry Module: Nến

Phân tích nến để xác định tín hiệu vào lệnh.

Logic:
- BUY  nếu nến hiện tại là nến tăng (close > open) và thân đủ lớn.
- SELL nếu nến hiện tại là nến giảm (close < open) và thân đủ lớn.
- NONE nếu nến Doji hoặc thân quá nhỏ (thân < min_body_ratio × toàn nến).

Tham số:
- min_body_ratio (float, mặc định 0.3):
    Tỉ lệ tối thiểu |close - open| / (high - low).
    Lọc bỏ nến Doji / nến râu dài thân nhỏ.
"""

from __future__ import annotations

import pandas as pd

from modules.base import IEntryModule, Signal


class NenEntry(IEntryModule):
    MODULE_NAME = "Nến"

    def __init__(self, min_body_ratio: float = 0.3):
        """
        Parameters
        ----------
        min_body_ratio : float
            Tỉ lệ thân / toàn nến tối thiểu [0.0 – 1.0].
            Nến có tỉ lệ thấp hơn được coi là Doji → trả NONE.
        """
        self.min_body_ratio = min_body_ratio

    @property
    def name(self) -> str:
        return self.MODULE_NAME

    def check(self, df: pd.DataFrame, idx: int) -> Signal:
        row  = df.iloc[idx]
        body = abs(row.close - row.open)
        full = row.high - row.low

        if full == 0:
            return Signal.NONE
        if body / full < self.min_body_ratio:
            return Signal.NONE

        return Signal.BUY if row.close > row.open else Signal.SELL
