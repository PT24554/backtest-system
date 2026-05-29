"""
modules/tp/__init__.py
───────────────────────
Auto-discovery: scan thư mục này, import tất cả file .py,
đăng ký mọi class kế thừa ITPModule vào REGISTRY.

👉 Để thêm module mới:
   Chỉ cần tạo file .py mới trong thư mục modules/tp/
   với class kế thừa ITPModule và có thuộc tính MODULE_NAME.
   App sẽ tự động load — không cần sửa bất kỳ file nào khác.
"""

from __future__ import annotations

import importlib
import inspect
import pkgutil
import warnings
from pathlib import Path

from modules.base import ITPModule

# ── Registry: name → class ────────────────────────────────────────────────────
REGISTRY: dict[str, type[ITPModule]] = {}

_pkg_path   = str(Path(__file__).parent)
_pkg_prefix = "modules.tp."

for _info in pkgutil.iter_modules([_pkg_path]):
    try:
        _mod = importlib.import_module(_pkg_prefix + _info.name)
    except Exception as _exc:
        warnings.warn(f"[modules.tp] Không thể load '{_info.name}': {_exc}")
        continue
    for _, _cls in inspect.getmembers(_mod, inspect.isclass):
        if (
            issubclass(_cls, ITPModule)
            and _cls is not ITPModule
            and hasattr(_cls, "MODULE_NAME")
        ):
            REGISTRY[_cls.MODULE_NAME] = _cls


# ── Public helpers ─────────────────────────────────────────────────────────────

def names() -> list[str]:
    """Danh sách tên module TP đã load (dùng cho UI checklist)."""
    return sorted(REGISTRY.keys())


def get(module_name: str, **kwargs) -> ITPModule:
    """Khởi tạo một TP module theo tên với tham số tùy chỉnh."""
    if module_name not in REGISTRY:
        raise KeyError(f"TP module '{module_name}' chưa được đăng ký. "
                       f"Có sẵn: {list(REGISTRY.keys())}")
    return REGISTRY[module_name](**kwargs)
