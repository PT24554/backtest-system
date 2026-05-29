"""
modules/base.py
───────────────
Interface chuẩn cho 3 loại module: Entry, SL, TP.

Mọi module đều phải kế thừa từ đây và implement các method abstract.
Không được sửa file này — chỉ thêm module mới bằng cách tạo file mới.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum

import pandas as pd


# ─── Signal Enum ──────────────────────────────────────────────────────────────

class Signal(Enum):
    """Tín hiệu giao dịch từ Entry module."""
    BUY  = "BUY"
    SELL = "SELL"
    NONE = "NONE"


# ─── Entry Module ─────────────────────────────────────────────────────────────

class IEntryModule(ABC):
    """
    Kiểm tra tín hiệu tại thanh nến idx.

    Parameters
    ----------
    df  : DataFrame OHLCV, index=datetime, columns=[open, high, low, close, volume]
    idx : vị trí thanh nến (0 = bar đầu tiên theo thứ tự thời gian)

    Returns
    -------
    Signal.BUY | Signal.SELL | Signal.NONE
    """

    @abstractmethod
    def check(self, df: pd.DataFrame, idx: int) -> Signal:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Tên hiển thị trên UI và trong CSV output."""
        pass

    def __repr__(self) -> str:
        return f"EntryModule({self.name})"


# ─── SL Module ────────────────────────────────────────────────────────────────

class ISLModule(ABC):
    """
    Tính giá SL dựa trên direction.

    Parameters
    ----------
    df        : DataFrame OHLCV
    idx       : vị trí thanh nến tín hiệu
    direction : Signal.BUY hoặc Signal.SELL

    Returns
    -------
    float — giá SL. Trả 0.0 nếu không xác định được.

    Lưu ý
    -----
    - BUY  → SL phải < entry price (bên dưới)
    - SELL → SL phải > entry price (bên trên)
    - Nếu không thỏa điều kiện trên, sl_engine sẽ bỏ qua giá trị này.
    """

    @abstractmethod
    def get_sl(self, df: pd.DataFrame, idx: int, direction: Signal) -> float:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    def __repr__(self) -> str:
        return f"SLModule({self.name})"


# ─── TP Module ────────────────────────────────────────────────────────────────

class ITPModule(ABC):
    """
    Tính giá TP dựa trên direction và sl_price.

    Parameters
    ----------
    df        : DataFrame OHLCV
    idx       : vị trí thanh nến tín hiệu
    direction : Signal.BUY hoặc Signal.SELL
    sl_price  : giá SL đã xác định (dùng để tính R:R)

    Returns
    -------
    float — giá TP. Trả 0.0 nếu không xác định được.

    Lưu ý
    -----
    - BUY  → TP phải > entry price (bên trên)
    - SELL → TP phải < entry price (bên dưới)
    - Nếu không thỏa điều kiện trên, tp_engine sẽ bỏ qua giá trị này.
    """

    @abstractmethod
    def get_tp(
        self,
        df: pd.DataFrame,
        idx: int,
        direction: Signal,
        sl_price: float,
    ) -> float:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    def __repr__(self) -> str:
        return f"TPModule({self.name})"
