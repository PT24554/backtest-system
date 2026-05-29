"""
data/yfinance_downloader.py
────────────────────────────
Download M1 data từ yfinance → lưu Parquet.

Giới hạn: yfinance chỉ cung cấp tối đa 60 ngày M1.
Dùng cho: test nhanh, development.
Production: dùng mt5_converter.py hoặc histdata_downloader.py.

Chạy:
    python data/yfinance_downloader.py
    python data/yfinance_downloader.py --symbol EURUSD --days 30
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import yfinance as yf

STORAGE_DIR = Path(__file__).parent.parent / "storage" / "parquet"

# Map symbol chuẩn → ticker yfinance
TICKER_MAP: dict[str, str] = {
    "XAUUSD": "GC=F",       # Gold Futures
    "EURUSD": "EURUSD=X",
    "GBPUSD": "GBPUSD=X",
    "USDJPY": "USDJPY=X",
    "AUDUSD": "AUDUSD=X",
    "USDCAD": "USDCAD=X",
    "USDCHF": "USDCHF=X",
    "NZDUSD": "NZDUSD=X",
    "XAGUSD": "SI=F",        # Silver Futures
}

# Giới hạn ngày tối đa mỗi request theo loại ticker
# yfinance giới hạn 8 ngày cho Futures (GC=F, SI=F), 60 ngày cho Forex
MAX_DAYS_PER_REQUEST: dict[str, int] = {
    "GC=F": 7,
    "SI=F": 7,
}


def download(symbol: str, days: int = 60) -> pd.DataFrame:
    """
    Download M1 OHLCV cho symbol, lưu vào storage/parquet/{symbol}_M1_test.parquet

    Parameters
    ----------
    symbol : "XAUUSD", "EURUSD", ... (xem TICKER_MAP)
    days   : số ngày cần lấy, tối đa 60

    Returns
    -------
    DataFrame OHLCV đã chuẩn hóa
    """
    ticker = TICKER_MAP.get(symbol.upper())
    if ticker is None:
        raise ValueError(
            f"Symbol '{symbol}' chưa có trong TICKER_MAP.\n"
            f"Thêm mapping vào TICKER_MAP trong file này."
        )

    days = min(days, 60)
    max_per_req = MAX_DAYS_PER_REQUEST.get(ticker, 60)
    print(f"Downloading {symbol} ({ticker}) — {days} ngày M1 từ yfinance...")

    # Tải từng đợt nếu ticker có giới hạn ngày/request
    raw = _download_chunked(ticker, days, max_per_req)

    if raw.empty:
        raise RuntimeError(f"yfinance trả về DataFrame rỗng cho {ticker}.")

    df = _normalize(raw)

    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    out_path = STORAGE_DIR / f"{symbol}_M1_test.parquet"
    df.to_parquet(out_path, compression="snappy")

    print(f"Saved {len(df):,} bars ({df.index[0]} → {df.index[-1]})")
    print(f"→ {out_path}")
    return df


def _download_chunked(
    ticker: str, total_days: int, max_per_req: int
) -> pd.DataFrame:
    """Tải nhiều đợt nhỏ rồi ghép lại (dùng cho Futures bị giới hạn 7 ngày/req)."""
    import datetime as dt

    chunks: list[pd.DataFrame] = []
    end = dt.datetime.now(dt.timezone.utc)

    remaining = total_days
    while remaining > 0:
        chunk_days = min(remaining, max_per_req)
        start = end - dt.timedelta(days=chunk_days)

        raw = yf.download(
            ticker,
            start=start.strftime("%Y-%m-%d"),
            end=end.strftime("%Y-%m-%d"),
            interval="1m",
            auto_adjust=True,
            progress=False,
        )

        if not raw.empty:
            chunks.append(raw)

        end = start
        remaining -= chunk_days

    if not chunks:
        return pd.DataFrame()

    return pd.concat(chunks[::-1]).sort_index().drop_duplicates()


def _normalize(raw: pd.DataFrame) -> pd.DataFrame:
    """Chuẩn hóa DataFrame về schema chuẩn."""
    df = raw.copy()

    # Flatten MultiIndex columns nếu có (yfinance đôi khi trả MultiIndex)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df.columns = [c.lower() for c in df.columns]

    # Giữ đúng 5 cột cần thiết
    df = df[["open", "high", "low", "close", "volume"]].copy()

    df.index.name = "datetime"
    df = df.sort_index()
    df = df.dropna()

    return df


# ─── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download M1 data từ yfinance")
    parser.add_argument("--symbol", default="XAUUSD", help="Symbol (default: XAUUSD)")
    parser.add_argument("--days",   default=60, type=int, help="Số ngày (max 60)")
    args = parser.parse_args()

    download(args.symbol, args.days)
