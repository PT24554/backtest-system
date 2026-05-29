"""
data/mt5_converter.py
──────────────────────
Convert file CSV export từ MT5 → Parquet chuẩn.

MT5 export format (từ script ExportM1Data.mq5):
    datetime,open,high,low,close,volume
    2024.01.02 00:01,2063.45,2063.89,2063.12,2063.67,120

Chạy:
    python data/mt5_converter.py --csv ~/Downloads/XAUUSD_M1.csv --symbol XAUUSD
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

STORAGE_DIR = Path(__file__).parent.parent / "storage" / "parquet"


def convert(csv_path: str | Path, symbol: str) -> pd.DataFrame:
    """
    Convert CSV từ MT5 → Parquet.

    Parameters
    ----------
    csv_path : đường dẫn file CSV (MT5 export format)
    symbol   : "XAUUSD", "EURUSD", ...

    Returns
    -------
    DataFrame OHLCV đã chuẩn hóa
    """
    csv_path = Path(csv_path).expanduser()
    if not csv_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {csv_path}")

    print(f"Converting {csv_path.name} → {symbol}_M1.parquet ...")

    df = _read_mt5_csv(csv_path)

    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    out_path = STORAGE_DIR / f"{symbol}_M1.parquet"
    df.to_parquet(out_path, compression="snappy")

    size_mb = out_path.stat().st_size / 1024 / 1024
    print(f"Saved {len(df):,} bars ({df.index[0]} → {df.index[-1]})")
    print(f"→ {out_path}  ({size_mb:.1f} MB)")
    return df


def _read_mt5_csv(path: Path) -> pd.DataFrame:
    """Đọc CSV theo format MT5 → DataFrame chuẩn."""
    # Thử detect format: có thể có header hoặc không
    first_line = path.read_text(encoding="utf-8-sig").splitlines()[0]

    if "datetime" in first_line.lower() or "date" in first_line.lower():
        # Có header
        df = pd.read_csv(path, encoding="utf-8-sig")
        # Xử lý trường hợp date và time là 2 cột riêng
        if "date" in df.columns and "time" in df.columns:
            df["datetime"] = pd.to_datetime(
                df["date"].astype(str) + " " + df["time"].astype(str)
            )
            df = df.drop(columns=["date", "time"])
        elif "datetime" in df.columns:
            df["datetime"] = pd.to_datetime(df["datetime"])
    else:
        # Không có header — giả định: datetime,open,high,low,close,volume
        df = pd.read_csv(
            path,
            names=["datetime", "open", "high", "low", "close", "volume"],
            encoding="utf-8-sig",
        )
        df["datetime"] = pd.to_datetime(df["datetime"])

    df = df.set_index("datetime").sort_index()
    df.columns = [c.lower().strip() for c in df.columns]
    df = df[["open", "high", "low", "close", "volume"]].copy()
    df = df.apply(pd.to_numeric, errors="coerce").dropna()
    return df


# ─── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert MT5 CSV → Parquet")
    parser.add_argument("--csv",    required=True, help="Đường dẫn file CSV từ MT5")
    parser.add_argument("--symbol", required=True, help="Tên symbol, vd: XAUUSD")
    args = parser.parse_args()

    convert(args.csv, args.symbol)
