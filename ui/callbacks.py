"""
ui/callbacks.py
────────────────
Callbacks:
  - Điều hướng màn hình Config ↔ Results
  - Range slider giờ GD → store-hours + display label
  - Tự động bỏ tick nếu cùng module chọn ở cả 2 nhóm Entry
  - Toggle hiện/ẩn SL/TP fallback inputs
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


# ── Slider → store-hours ─────────────────────────────────────────────────────

@callback(
    Output("store-hours", "data"),
    Input("slider-hours", "value"),
)
def update_hours_store(slider_val):
    h0, h1 = (slider_val or [0, 24])
    return {"h0": int(h0), "h1": int(h1), "m0": 0, "m1": 0}


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
