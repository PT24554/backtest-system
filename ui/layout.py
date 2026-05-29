"""
ui/layout.py
─────────────
Layout mới:
  - Config full màn hình (3 cột: Entry | SL | TP + Risk | Time | Run)
  - Results chỉ hiện sau khi chạy xong backtest
  - Font tiếng Việt, font size base 15px
  - Module chọn bằng checkbox
  - Giờ GD dùng range slider + text input tinh chỉnh
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from ui.components import (
    C, FONT, TF_OPTIONS, HTF_OPTIONS,
    ENTRY_MODULES, SL_MODULES, TP_MODULES,
    card, module_checklist, sub_label, stat_card, num_input,
)
from data.loader import list_available


# ── Public ────────────────────────────────────────────────────────────────────

def create_layout() -> html.Div:
    symbols = list_available() or []
    # Ưu tiên EURUSD, fallback về symbol đầu tiên có sẵn
    default_sym = next((s for s in symbols if "EURUSD" in s.upper()), symbols[0] if symbols else None)

    return html.Div([
        _stores(),
        _header(symbols, default_sym),
        html.Div(id="screen-config",  children=_config_screen()),
        html.Div(id="screen-results", children=_results_screen(), style={"display": "none"}),
    ], style={
        "fontFamily": FONT,
        "fontSize":   "15px",
        "background": C["bg"],
        "minHeight":  "100vh",
    })


# ── Stores ────────────────────────────────────────────────────────────────────

def _stores() -> html.Div:
    return html.Div([
        dcc.Store(id="store-results", data=None),
        dcc.Store(id="app-screen",    data="config"),
        # Giờ giao dịch: slider (giờ) + text inputs (phút) → store
        dcc.Store(id="store-hours",   data={"h0": 0, "h1": 24, "m0": 0, "m1": 0}),
    ])


# ── Header ────────────────────────────────────────────────────────────────────

def _header(symbols: list, default_sym) -> html.Div:
    symbol_opts = [
        {"label": _sym_label(s), "value": s} for s in symbols
    ]
    return html.Div([
        # Logo
        html.Div([
            html.Span("◈", style={"fontSize": "24px", "marginRight": "12px", "opacity": ".9"}),
            html.Div([
                html.Div("BACKTEST SYSTEM", style={
                    "fontSize": "15px", "fontWeight": "800", "letterSpacing": "2.5px",
                }),
                html.Div("Strategy Tester", style={
                    "fontSize": "10px", "opacity": ".5", "letterSpacing": "1px", "marginTop": "2px",
                }),
            ]),
        ], style={"display": "flex", "alignItems": "center"}),

        # Symbol + TF dropdowns
        html.Div([
            html.Div([
                html.Div("DỮ LIỆU", style=_nav_lbl()),
                dcc.Dropdown(
                    id="dd-symbol", options=symbol_opts, value=default_sym,
                    clearable=False, placeholder="Chọn file...",
                    style={"width": "230px", "fontSize": "14px"},
                ),
            ], style={"marginRight": "14px"}),
            html.Div([
                html.Div("TIMEFRAME", style=_nav_lbl()),
                dcc.Dropdown(
                    id="dd-tf", options=TF_OPTIONS, value="H1",
                    clearable=False,
                    style={"width": "95px", "fontSize": "14px"},
                ),
            ]),
        ], style={"display": "flex", "alignItems": "flex-end"}),

        # Status
        html.Div(id="header-status", children=[
            html.Span("● Sẵn sàng", style={"fontSize": "13px", "color": "#86efac", "fontWeight": "600"}),
        ]),
    ], style={
        "background": C["grad_header"],
        "color": "white",
        "padding": "14px 28px",
        "display": "flex",
        "alignItems": "center",
        "justifyContent": "space-between",
        "boxShadow": "0 4px 20px rgba(30,27,75,0.35)",
        "position": "sticky", "top": "0", "zIndex": "100",
        "fontFamily": FONT,
    })


# ── Config screen ─────────────────────────────────────────────────────────────

def _config_screen() -> html.Div:
    return html.Div([
        # Row 1: ENTRY | SL | TP  (mỗi cái 1 cột riêng → tránh bị chèn)
        dbc.Row([
            dbc.Col(_entry_card(), lg=6, style={"marginBottom": "16px"}),
            dbc.Col(_sl_card(),    lg=3, style={"marginBottom": "16px"}),
            dbc.Col(_tp_card(),    lg=3, style={"marginBottom": "16px"}),
        ], className="g-3"),

        # Row 2: RISK | TIME | RUN
        dbc.Row([
            dbc.Col(_risk_card(), lg=4, style={"marginBottom": "16px"}),
            dbc.Col(_time_card(), lg=5, style={"marginBottom": "16px"}),
            dbc.Col(_run_area(),  lg=3, style={"marginBottom": "16px"}),
        ], className="g-3"),
    ], style={"padding": "24px 28px"})


# ── ENTRY card ────────────────────────────────────────────────────────────────

def _entry_card():
    return card("entry", "Entry Conditions", "📥", html.Div([
        # Hai checklist nằm cạnh nhau
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Span("✅", style={"marginRight": "6px"}),
                    html.Span("Bắt buộc CÓ", style={
                        "fontSize": "13px", "fontWeight": "700",
                        "color": C["must_have"], "letterSpacing": "0.5px",
                    }),
                ], style={"marginBottom": "10px", "display": "flex", "alignItems": "center"}),
                module_checklist("check-entry-must-have", ENTRY_MODULES, C["must_have"]),
            ], md=6, style={"paddingRight": "14px"}),

            dbc.Col([
                html.Div([
                    html.Span("❌", style={"marginRight": "6px"}),
                    html.Span("Bắt buộc KHÔNG", style={
                        "fontSize": "13px", "fontWeight": "700",
                        "color": C["must_not"], "letterSpacing": "0.5px",
                    }),
                ], style={"marginBottom": "10px", "display": "flex", "alignItems": "center"}),
                module_checklist("check-entry-must-not", ENTRY_MODULES, C["must_not"]),
            ], md=6, style={
                "paddingLeft": "14px",
                "borderLeft": f"1px solid {C['border']}",
            }),
        ], className="g-0"),

        html.Hr(style={"margin": "16px 0", "borderColor": C["border"]}),

        dbc.Row([
            # Trigger
            dbc.Col([
                sub_label("Trigger"),
                dcc.RadioItems(
                    id="radio-trigger",
                    options=[
                        {"label": "  Đóng nến",       "value": "candle_close"},
                        {"label": "  Tại giờ cụ thể", "value": "specific_time"},
                    ],
                    value="candle_close",
                    inline=True,
                    labelStyle={"marginRight": "18px", "fontSize": "14px"},
                ),
            ], md=12, style={"marginBottom": "16px"}),

            # Giờ giao dịch — range slider + text inputs
            dbc.Col([
                sub_label("Giờ giao dịch (GMT+7)"),
                dcc.RangeSlider(
                    id="slider-hours",
                    min=0, max=24, step=1,
                    value=[0, 24],
                    marks={i: {"label": f"{i:02d}h",
                               "style": {"fontSize": "11px", "color": C["muted"]}}
                           for i in [0, 4, 8, 12, 16, 20, 24]},
                    tooltip={"placement": "bottom", "always_visible": False},
                    allowCross=False,
                ),
                # Display + text fine-tune
                html.Div(id="slider-hours-display", style={
                    "textAlign": "center", "fontSize": "14px",
                    "color": C["must_have"], "fontWeight": "600",
                    "margin": "8px 0 10px",
                }),
                html.Div([
                    html.Span("Tinh chỉnh:", style={
                        "fontSize": "13px", "color": C["muted"], "marginRight": "10px",
                    }),
                    dcc.Input(id="input-hour-from", type="text", value="00:00",
                              style=_time_inp(), debounce=True),
                    html.Span("→", style={"padding": "0 10px", "color": C["muted"],
                                          "fontSize": "16px"}),
                    dcc.Input(id="input-hour-to", type="text", value="23:59",
                              style=_time_inp(), debounce=True),
                ], style={"display": "flex", "alignItems": "center"}),
            ], md=12, style={"marginBottom": "16px"}),

            # Ngày giao dịch
            dbc.Col([
                sub_label("Ngày giao dịch"),
                dcc.Checklist(
                    id="check-days",
                    options=[
                        {"label": " T2", "value": 0},
                        {"label": " T3", "value": 1},
                        {"label": " T4", "value": 2},
                        {"label": " T5", "value": 3},
                        {"label": " T6", "value": 4},
                        {"label": " T7", "value": 5},
                        {"label": " CN", "value": 6},
                    ],
                    value=[0, 1, 2, 3, 4],
                    inline=True,
                    labelStyle={"marginRight": "12px", "fontSize": "14px"},
                    inputStyle={"marginRight": "5px", "accentColor": C["must_have"]},
                ),
            ], md=12),
        ]),
    ]))


# ── SL card ───────────────────────────────────────────────────────────────────

def _sl_card():
    return card("sl", "Stop Loss", "🛡", html.Div([
        sub_label("Chọn module SL", color=C["sl_color"]),
        module_checklist("check-sl", SL_MODULES, C["sl_color"]),

        html.Div(style={
            "fontSize": "12px", "color": C["muted"],
            "fontStyle": "italic", "margin": "6px 0 14px",
        }, children="→ Khi nhiều module: lấy SL gần entry nhất"),

        html.Hr(style={"borderColor": C["border"], "margin": "4px 0 14px"}),

        sub_label("Fallback (khi module không cho kết quả)"),
        dcc.RadioItems(
            id="radio-sl-fallback",
            options=[
                {"label": "  Cố định (pips)", "value": "pips"},
                {"label": "  Nến tín hiệu",   "value": "candle"},
            ],
            value="pips",
            labelStyle={"display": "block", "fontSize": "14px", "marginBottom": "6px"},
            inputStyle={"marginRight": "8px", "accentColor": C["sl_color"]},
        ),
        html.Div(id="div-sl-fallback-pips", style={"marginTop": "8px"},
                 children=[num_input("input-sl-pips", 50, suffix=" pips", width="70px")]),

        html.Hr(style={"borderColor": C["border"], "margin": "14px 0"}),

        sub_label("Buffer SL"),
        num_input("input-sl-buffer", 5, suffix=" pips", width="70px"),
    ]))


# ── TP card ───────────────────────────────────────────────────────────────────

def _tp_card():
    return card("tp", "Take Profit", "🎯", html.Div([
        sub_label("Chọn module TP", color=C["tp_color"]),
        module_checklist("check-tp", TP_MODULES, C["tp_color"]),

        html.Div(style={
            "fontSize": "12px", "color": C["muted"],
            "fontStyle": "italic", "margin": "6px 0 14px",
        }, children="→ Khi nhiều module: lấy TP gần entry nhất"),

        html.Hr(style={"borderColor": C["border"], "margin": "4px 0 14px"}),

        sub_label("Fallback"),
        dcc.RadioItems(
            id="radio-tp-fallback",
            options=[
                {"label": "  R:R cố định",   "value": "rr"},
                {"label": "  Cố định (pips)", "value": "pips"},
            ],
            value="rr",
            labelStyle={"display": "block", "fontSize": "14px", "marginBottom": "6px"},
            inputStyle={"marginRight": "8px", "accentColor": C["tp_color"]},
        ),
        html.Div(id="div-tp-rr",
                 children=[num_input("input-tp-rr", 2.0, prefix="R:R ", width="75px")],
                 style={"marginTop": "8px"}),
        html.Div(id="div-tp-pips",
                 children=[num_input("input-tp-pips", 50, suffix=" pips", width="70px")],
                 style={"display": "none", "marginTop": "8px"}),

        html.Hr(style={"borderColor": C["border"], "margin": "14px 0"}),

        dcc.Checklist(
            id="check-partial-tp",
            options=[{"label": "  Partial TP", "value": "on"}],
            value=[],
            labelStyle={"fontSize": "14px"},
            inputStyle={"marginRight": "8px", "accentColor": C["tp_color"]},
        ),
        html.Div(id="div-partial-tp", style={"display": "none"}, children=[
            html.Div([
                html.Span("Đóng", style={"fontSize": "14px", "color": C["muted"]}),
                html.Div(style={"margin": "0 8px"},
                         children=[num_input("input-partial-pct", 50, suffix="%", width="58px")]),
                html.Span("tại R:R", style={"fontSize": "14px", "color": C["muted"], "marginRight": "8px"}),
                num_input("input-partial-rr", 1.0, width="60px"),
            ], style={"display": "flex", "alignItems": "center",
                      "flexWrap": "wrap", "gap": "6px",
                      "marginTop": "10px", "paddingLeft": "18px"}),
        ]),
    ]))


# ── Risk card ─────────────────────────────────────────────────────────────────

def _risk_card():
    return card("risk", "Risk Management", "💰", html.Div([
        html.Div([
            sub_label("Số dư tài khoản"),
            num_input("input-balance", 10000, prefix="$", width="120px"),
        ], style={"marginBottom": "16px"}),
        html.Div([
            sub_label("Risk mỗi lệnh"),
            num_input("input-risk", 50, prefix="$", width="100px"),
        ], style={"marginBottom": "16px"}),
        html.Div([
            sub_label("Tối đa lệnh đồng thời"),
            num_input("input-max-trades", 3, suffix=" lệnh", width="70px"),
        ]),
    ]))


# ── Time card ─────────────────────────────────────────────────────────────────

def _time_card():
    return card("time", "Thời gian Backtest", "📅", html.Div([
        dbc.Row([
            dbc.Col([
                sub_label("Từ ngày"),
                dcc.DatePickerSingle(id="date-from", display_format="DD/MM/YYYY",
                                     placeholder="dd/mm/yyyy"),
            ], sm=6),
            dbc.Col([
                sub_label("Đến ngày"),
                dcc.DatePickerSingle(id="date-to", display_format="DD/MM/YYYY",
                                     placeholder="dd/mm/yyyy"),
            ], sm=6),
        ], className="g-2", style={"marginBottom": "18px"}),

        dcc.Checklist(
            id="check-mtf",
            options=[{"label": "  Multi-Timeframe filter", "value": "on"}],
            value=[],
            labelStyle={"fontSize": "14px"},
            inputStyle={"marginRight": "8px", "accentColor": C["must_have"]},
        ),
        html.Div(id="div-mtf-settings", style={"display": "none"}, children=[
            html.Div(style={"marginTop": "12px", "paddingLeft": "18px"}, children=[
                html.Div([
                    sub_label("Khung xu hướng"),
                    dcc.Dropdown(id="dd-htf", options=HTF_OPTIONS, value="H4",
                                 clearable=False,
                                 style={"width": "110px", "fontSize": "14px"}),
                ], style={"marginBottom": "12px"}),
                html.Div([
                    sub_label("Hướng cho phép"),
                    dcc.RadioItems(
                        id="radio-htf-dir",
                        options=[
                            {"label": " Cả BUY & SELL", "value": "both"},
                            {"label": " Chỉ BUY",       "value": "buy"},
                            {"label": " Chỉ SELL",      "value": "sell"},
                        ],
                        value="both",
                        labelStyle={"display": "block", "fontSize": "14px",
                                    "marginBottom": "5px"},
                        inputStyle={"marginRight": "8px", "accentColor": C["must_have"]},
                    ),
                ]),
            ]),
        ]),
    ]))


# ── Run area ──────────────────────────────────────────────────────────────────

def _run_area():
    return html.Div([
        html.Div([
            html.Div(style={
                "height": "4px", "background": C["grad_run"],
                "borderRadius": "14px 14px 0 0",
            }),
            html.Div([
                html.Div("▶", style={
                    "fontSize": "44px", "textAlign": "center",
                    "marginBottom": "10px", "opacity": ".75",
                }),
                html.Div("Nhấn để bắt đầu", style={
                    "fontSize": "12px", "fontWeight": "600",
                    "color": C["muted"], "textTransform": "uppercase",
                    "letterSpacing": "1px", "textAlign": "center",
                    "marginBottom": "18px",
                }),
                html.Button(
                    "CHẠY BACKTEST",
                    id="btn-run",
                    n_clicks=0,
                    style={
                        "width": "100%", "padding": "15px",
                        "background": C["grad_run"],
                        "color": "white", "border": "none",
                        "borderRadius": "10px", "fontSize": "14px",
                        "fontWeight": "800", "cursor": "pointer",
                        "letterSpacing": "1.5px",
                        "boxShadow": "0 4px 20px rgba(16,185,129,0.35)",
                        "fontFamily": FONT,
                    },
                ),
                html.Div(id="run-status-mini", style={
                    "marginTop": "12px", "fontSize": "13px",
                    "textAlign": "center", "color": C["muted"],
                    "minHeight": "20px",
                }),
            ], style={"padding": "20px"}),
        ], style={
            "background": C["white"], "borderRadius": "14px",
            "border": f"1px solid {C['border']}",
            "boxShadow": "0 2px 14px rgba(16,185,129,0.1)",
        }),
    ])


# ── Results screen ────────────────────────────────────────────────────────────

def _results_screen() -> html.Div:
    return html.Div([
        # Sub-header
        html.Div([
            html.Button("← Quay lại cấu hình", id="btn-back-config", n_clicks=0,
                        style={
                            "background": "rgba(255,255,255,0.15)",
                            "border": "1px solid rgba(255,255,255,0.3)",
                            "color": "white", "borderRadius": "8px",
                            "padding": "8px 18px", "fontSize": "13px",
                            "cursor": "pointer", "fontWeight": "600",
                            "fontFamily": FONT,
                        }),
            html.Div(id="results-title", style={
                "fontSize": "15px", "fontWeight": "700", "color": "white",
            }),
            html.Button("↻ Chạy lại", id="btn-rerun", n_clicks=0, style={
                "background": C["grad_run"], "border": "none",
                "color": "white", "borderRadius": "8px",
                "padding": "8px 18px", "fontSize": "13px",
                "cursor": "pointer", "fontWeight": "700",
                "boxShadow": "0 2px 10px rgba(16,185,129,0.4)",
                "fontFamily": FONT,
            }),
        ], style={
            "background": C["grad_results"],
            "padding": "13px 28px",
            "display": "flex", "alignItems": "center",
            "justifyContent": "space-between",
            "boxShadow": "0 4px 20px rgba(99,102,241,0.3)",
        }),

        # Results content
        html.Div([
            dbc.Row([
                dbc.Col(stat_card("Tổng lệnh",    "stat-total", "—",
                                  "linear-gradient(90deg,#6366f1,#8b5cf6)"), md=2),
                dbc.Col(stat_card("Win Rate",      "stat-wr",    "—",
                                  "linear-gradient(90deg,#0ea5e9,#6366f1)"), md=2),
                dbc.Col(stat_card("Lãi ròng",      "stat-pnl",   "—",
                                  "linear-gradient(90deg,#10b981,#0ea5e9)"), md=2),
                dbc.Col(stat_card("Profit Factor", "stat-pf",    "—",
                                  "linear-gradient(90deg,#f59e0b,#10b981)"), md=2),
                dbc.Col(stat_card("Max Drawdown",  "stat-dd",    "—",
                                  "linear-gradient(90deg,#ef4444,#f97316)"), md=2),
                dbc.Col(stat_card("Avg R:R đạt",   "stat-rr",    "—",
                                  "linear-gradient(90deg,#8b5cf6,#ec4899)"), md=2),
            ], className="g-2", style={"marginBottom": "20px"}),

            # Equity curve
            html.Div([
                html.Div(style={"height": "4px", "background": C["grad_results"],
                                "borderRadius": "14px 14px 0 0"}),
                html.Div([
                    html.Div("Equity Curve", style={
                        "fontSize": "12px", "fontWeight": "700", "color": C["muted"],
                        "textTransform": "uppercase", "letterSpacing": "1px",
                        "marginBottom": "4px",
                    }),
                    dcc.Graph(id="chart-equity", figure=_empty_chart(),
                              config={"displayModeBar": True, "displaylogo": False,
                                      "modeBarButtonsToRemove": ["select2d", "lasso2d"]},
                              style={"height": "320px"}),
                ], style={"padding": "14px 16px 8px"}),
            ], style={
                "background": C["white"], "borderRadius": "14px",
                "border": f"1px solid {C['border']}",
                "boxShadow": "0 2px 12px rgba(99,102,241,0.06)",
                "marginBottom": "16px",
            }),

            # Trade log
            html.Div([
                html.Div(style={"height": "4px",
                                "background": "linear-gradient(90deg,#64748b,#94a3b8)",
                                "borderRadius": "14px 14px 0 0"}),
                html.Div([
                    html.Div("Trade Log", style={
                        "fontSize": "12px", "fontWeight": "700", "color": C["muted"],
                        "textTransform": "uppercase", "letterSpacing": "1px",
                        "marginBottom": "10px",
                    }),
                    html.Div(id="trade-log", children=[
                        html.Span("Kết quả sẽ hiển thị sau khi chạy backtest.",
                                  style={"color": C["muted"], "fontSize": "14px"}),
                    ]),
                ], style={"padding": "14px 16px 16px"}),
            ], style={
                "background": C["white"], "borderRadius": "14px",
                "border": f"1px solid {C['border']}",
                "boxShadow": "0 2px 12px rgba(99,102,241,0.06)",
            }),
        ], style={"padding": "24px 28px"}),
    ])


# ── Helpers ───────────────────────────────────────────────────────────────────

def _sym_label(s: str) -> str:
    return s.replace("_M1_test", " (test)").replace("_M1", "")

def _nav_lbl() -> dict:
    return {
        "fontSize": "9px", "fontWeight": "700",
        "color": "rgba(000,255,255,0.5)",
        "textTransform": "uppercase", "letterSpacing": "1.2px",
        "marginBottom": "5px", "fontFamily": FONT,
    }

def _time_inp() -> dict:
    return {
        "width": "76px", "padding": "6px 8px", "textAlign": "center",
        "border": f"1px solid {C['border']}", "borderRadius": "8px",
        "fontSize": "14px", "outline": "none", "background": C["white"],
        "fontFamily": FONT,
    }

def _empty_chart():
    fig = go.Figure()
    fig.update_layout(
        paper_bgcolor=C["white"], plot_bgcolor=C["white"],
        xaxis={"visible": False}, yaxis={"visible": False},
        annotations=[{"text": "Equity curve sẽ hiển thị ở đây",
                      "xref": "paper", "yref": "paper",
                      "x": 0.5, "y": 0.5, "showarrow": False,
                      "font": {"size": 14, "color": C["muted"],
                               "family": FONT}}],
        margin={"l": 8, "r": 8, "t": 8, "b": 8},
    )
    return fig
