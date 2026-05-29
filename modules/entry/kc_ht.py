"""
modules/entry/kc_ht.py
───────────────────────
Entry Module: KC-HT (Kháng cự – Hỗ trợ)

Vào lệnh khi giá phản ứng tại vùng kháng cự hoặc hỗ trợ.

Logic:
- Xác định các swing high (kháng cự) và swing low (hỗ trợ)
  trong lookback nến gần nhất.
- BUY  nếu giá đang trong vùng hỗ trợ VÀ nến xác nhận tăng.
- SELL nếu giá đang trong vùng kháng cự VÀ nến xác nhận giảm.
- NONE nếu không rõ hoặc đồng thời ở cả 2 vùng.

Tham số:
- lookback      (int,   mặc định 100):    Số nến nhìn lại.
- zone_pips     (float, mặc định 5.0):    Bề rộng vùng S/R (pips).
- swing_window  (int,   mặc định 5):      Cửa sổ xác định swing high/low.
- pip_size      (float, mặc định 0.0001).
"""

from __future__ import annotations

import pandas as pd

from modules.base import IEntryModule, Signal


class KCHTEntry(IEntryModule):
    MODULE_NAME = "KC-HT"

    def __init__(
        self,
        lookback:     int   = 100,
        zone_pips:    float = 5.0,
        swing_window: int   = 5,
        pip_size:     float = 0.0001,
    ):
        self.lookback     = lookback
        self.zone         = zone_pips * pip_size
        self.swing_window = swing_window

    @property
    def name(self) -> str:
        return self.MODULE_NAME

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _find_levels(
        self, df: pd.DataFrame, idx: int
    ) -> tuple[list[float], list[float]]:
        """Trả (supports, resistances) từ lookback bars trước idx."""
        start = max(0, idx - self.lookback)
        sub   = df.iloc[start:idx]
        w     = self.swing_window

        supports:    list[float] = []
        resistances: list[float] = []
        highs = sub["high"].values
        lows  = sub["low"].values

        for i in range(w, len(sub) - w):
            if all(highs[i] >= highs[j] for j in range(i - w, i + w + 1) if j != i):
                resistances.append(float(highs[i]))
            if all(lows[i] <= lows[j] for j in range(i - w, i + w + 1) if j != i):
                supports.append(float(lows[i]))

        return supports, resistances

    def _near(self, price: float, levels: list[float]) -> bool:
        return any(abs(price - lvl) <= self.zone for lvl in levels)

    # ── Main check ────────────────────────────────────────────────────────────

    def check(self, df: pd.DataFrame, idx: int) -> Signal:
        if idx < self.swing_window * 2 + 2:
            return Signal.NONE

        row   = df.iloc[idx]
        price = row.close

        supports, resistances = self._find_levels(df, idx)

        near_sup = self._near(price, supports)
        near_res = self._near(price, resistances)

        if near_sup and not near_res:
            return Signal.BUY if row.close >= row.open else Signal.NONE
        if near_res and not near_sup:
            return Signal.SELL if row.close <= row.open else Signal.NONE

        return Signal.NONE
