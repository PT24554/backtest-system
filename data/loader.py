"""
data/loader.py
──────────────
Đọc file Parquet → DataFrame OHLCV chuẩn.

Schema chuẩn của DataFrame:
  Index : datetime64[ns, UTC]  — tên "datetime"
  open  : float64
  high  : float64
  low   : float64
  close : float64
  volume: float64
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

STORAGE_DIR = Path(__file__).parent.parent / "storage" / "parquet"


def load(symbol: str, suffix: str = "") -> pd.DataFrame:
    """
    Đọc file Parquet cho symbol.

    Parameters
    ----------
    symbol : "XAUUSD", "EURUSD", ...
    suffix : "" (production) hoặc "_test" (yfinance 60 ngày)

    Returns
    -------
    DataFrame OHLCV với DatetimeIndex

    Raises
    ------
    FileNotFoundError nếu file chưa được download
    """
    filename = f"{symbol}_M1{suffix}.parquet"
    path = STORAGE_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            f"File không tồn tại: {path}\n"
            f"Chạy data/yfinance_downloader.py hoặc data/mt5_converter.py trước."
        )

    df = pd.read_parquet(path)
    _validate(df, path)
    return df


def load_range(
    symbol: str,
    start: str,
    end: str,
    suffix: str = "",
) -> pd.DataFrame:
    """
    Đọc và lọc theo khoảng thời gian.

    Parameters
    ----------
    start : "2024-01-01"
    end   : "2024-12-31"
    """
    df = load(symbol, suffix)
    return df.loc[start:end]


# ─── Internal ─────────────────────────────────────────────────────────────────

def _validate(df: pd.DataFrame, path: Path) -> None:
    required = {"open", "high", "low", "close", "volume"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"File {path.name} thiếu cột: {missing}")
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError(f"File {path.name}: index phải là DatetimeIndex")


def list_available() -> list[str]:
    """Trả về danh sách symbol đang có dữ liệu."""
    files = sorted(STORAGE_DIR.glob("*_M1*.parquet"))
    return [f.stem for f in files]
