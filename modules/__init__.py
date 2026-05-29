"""
modules/__init__.py
────────────────────
Điểm vào chung: expose registry và helper của cả 3 nhóm module.

Usage:
    from modules import entry, sl, tp

    # Lấy danh sách tên module (cho UI)
    entry.names()   # ["KC-HT", "Màu nến", "Mô hình nến", ...]
    sl.names()      # ["KC-HT", "SL Pips", "Tròn số"]
    tp.names()      # ["KC-HT", "TP Pips", "TP R:R", "Tròn số"]

    # Khởi tạo module với tham số
    mod = entry.get("Màu nến", min_body_ratio=0.4)
    signal = mod.check(df, idx)
"""

from modules import entry, sl, tp

__all__ = ["entry", "sl", "tp"]
