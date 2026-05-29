"""
ui/callbacks.py
────────────────
Callbacks sau khi UI chuyển sang checkbox + range slider:
  - Điều hướng màn hình Config ↔ Results
  - Đồng bộ range slider giờ GD → text inputs
  - Tự động bỏ tick nếu cùng module chọn ở cả 2 nhóm Entry
  - Toggle hiện/ẩn các section phụ
"""

from __future__ import annotations

import dash
from dash import Input, Output, State, callback, callback_context
from dash.exceptions import PreventUpdate

from ui.components import C


# ── Screen navigation ─────────────────────────────────────────────────────────

@callback(
    Output("screen-config",  "style"),
    Output("screen-results", "style"),
    Output("header-status",  "children"),
    Input("btn-run",         "n_clicks"),
    Input("btn-back-config", "n_clicks"),
    Input("btn-rerun",       "n_clicks"),
    State("check-entry-must-have", "value"),
    prevent_initial_call=True,
)
def navigate_screens(_, back, rerun, must_have):
    triggered = callback_context.triggered_id

    if triggered in ("btn-back-config", "btn-rerun"):
        return {"display": "block"}, {"display": "none"}, _status("ready")

    if triggered == "btn-run":
        if not must_have:
            return {"display": "block"}, {"display": "none"}, _status("warn")
        return {"display": "none"}, {"display": "block"}, _status("done")

    raise PreventUpdate


@callback(
    Output("run-status-mini", "children"),
    Input("btn-run", "n_clicks"),
    State("check-entry-must-have", "value"),
    prevent_initial_call=True,
)
def run_status_mini(_, must_have):
    if not must_have:
        return dash.html.Span("⚠ Chưa chọn module Entry",
                              style={"color": "#f59e0b", "fontSize": "13px"})
    return ""


def _status(kind: str):
    if kind == "ready":
        return dash.html.Span("● Sẵn sàng",
                              style={"fontSize": "13px", "color": "#86efac", "fontWeight": "600"})
    if kind == "warn":
        return dash.html.Span("⚠ Chưa có module Entry",
                              style={"fontSize": "13px", "color": "#fde68a", "fontWeight": "600"})
    return dash.html.Span("✓ Hoàn thành",
                          style={"fontSize": "13px", "color": "#86efac", "fontWeight": "600"})


# ── Slider → display label (một chiều, không vòng tròn) ──────────────────────

@callback(
    Output("slider-hours-display", "children"),
    Input("slider-hours", "value"),
)
def update_hours_display(value):
    h0, h1 = value or [0, 24]
    return f"{h0:02d}:00  →  {h1:02d}:00"


# ── Slider + text inputs → store-hours (single source of truth) ───────────────
# Không có output ngược lại → không còn cycle.
# Slider kiểm soát giờ; text inputs thêm phút chính xác.

@callback(
    Output("store-hours", "data"),
    Input("slider-hours",    "value"),
    Input("input-hour-from", "value"),
    Input("input-hour-to",   "value"),
)
def update_hours_store(slider_val, from_text, to_text):
    h0, h1 = (slider_val or [0, 24])

    def _parse_min(text: str, default: int) -> int:
        try:
            parts = (text or "").split(":")
            return max(0, min(59, int(parts[1]))) if len(parts) > 1 else default
        except (ValueError, IndexError):
            return default

    m0 = _parse_min(from_text, 0)
    m1 = _parse_min(to_text,   0)
    return {"h0": int(h0), "h1": int(h1), "m0": m0, "m1": m1}


# ── Mutual exclusion: cùng 1 module không được ở cả 2 nhóm Entry ─────────────

@callback(
    Output("check-entry-must-have", "value"),
    Output("check-entry-must-not",  "value"),
    Input("check-entry-must-have",  "value"),
    Input("check-entry-must-not",   "value"),
    prevent_initial_call=True,
)
def entry_mutual_exclusion(must_have, must_not):
    triggered = callback_context.triggered_id
    mh = list(must_have or [])
    mn = list(must_not  or [])
    if triggered == "check-entry-must-have":
        mn = [m for m in mn if m not in mh]   # Bỏ khỏi must-not nếu có trong must-have
    else:
        mh = [m for m in mh if m not in mn]   # Bỏ khỏi must-have nếu có trong must-not
    return mh, mn


# ── Toggle Partial TP ─────────────────────────────────────────────────────────

@callback(
    Output("div-partial-tp", "style"),
    Input("check-partial-tp", "value"),
)
def toggle_partial_tp(checked):
    return {"display": "block", "marginTop": "8px"} if checked else {"display": "none"}


# ── Toggle MTF settings ───────────────────────────────────────────────────────

@callback(
    Output("div-mtf-settings", "style"),
    Input("check-mtf", "value"),
)
def toggle_mtf(checked):
    return {"display": "block"} if checked else {"display": "none"}


# ── Toggle SL fallback input ──────────────────────────────────────────────────

@callback(
    Output("div-sl-fallback-pips", "style"),
    Input("radio-sl-fallback", "value"),
)
def toggle_sl_fallback(value):
    return {"marginTop": "8px"} if value == "pips" else {"display": "none"}


# ── Toggle TP fallback input ──────────────────────────────────────────────────

@callback(
    Output("div-tp-rr",   "style"),
    Output("div-tp-pips", "style"),
    Input("radio-tp-fallback", "value"),
)
def toggle_tp_fallback(value):
    if value == "rr":
        return {"marginTop": "8px"}, {"display": "none"}
    return {"display": "none"}, {"marginTop": "8px"}
