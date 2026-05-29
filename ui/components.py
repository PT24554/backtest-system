"""
ui/components.py
─────────────────
Building blocks tái sử dụng. Font tiếng Việt, gradient hiện đại.
Font base: 15px (tăng 2px so với thiết kế cũ).
"""

from dash import html, dcc
import dash_bootstrap_components as dbc

# Auto-load module names từ registry (không cần sửa khi thêm module mới)
from modules import entry as _entry_pkg, sl as _sl_pkg, tp as _tp_pkg

FONT = "'Be Vietnam Pro', 'Inter', 'Segoe UI', sans-serif"

# ── Palette ───────────────────────────────────────────────────────────────────
C = {
    "bg":       "#f0f4ff",
    "white":    "#ffffff",
    "text":     "#0f172a",
    "muted":    "#64748b",
    "border":   "rgba(99,102,241,0.15)",

    # Gradients
    "grad_header":  "linear-gradient(135deg, #1e1b4b 0%, #312e81 55%, #4338ca 100%)",
    "grad_entry":   "linear-gradient(90deg,  #4f46e5, #7c3aed)",
    "grad_sl":      "linear-gradient(90deg,  #0ea5e9, #6366f1)",
    "grad_tp":      "linear-gradient(90deg,  #10b981, #0ea5e9)",
    "grad_risk":    "linear-gradient(90deg,  #f59e0b, #ef4444)",
    "grad_time":    "linear-gradient(90deg,  #8b5cf6, #ec4899)",
    "grad_run":     "linear-gradient(135deg, #10b981, #059669)",
    "grad_results": "linear-gradient(90deg,  #6366f1, #a855f7)",

    # Solid colors
    "must_have": "#4f46e5",
    "must_not":  "#e11d48",
    "sl_color":  "#0ea5e9",
    "tp_color":  "#10b981",
}

CARD_GRADIENT = {
    "entry": C["grad_entry"],
    "sl":    C["grad_sl"],
    "tp":    C["grad_tp"],
    "risk":  C["grad_risk"],
    "time":  C["grad_time"],
}

# ── Module option lists (tự động từ registry — thêm file mới là tự có) ───────
ENTRY_MODULES: list[str] = _entry_pkg.names()   # scan modules/entry/
SL_MODULES:    list[str] = _sl_pkg.names()      # scan modules/sl/
TP_MODULES:    list[str] = _tp_pkg.names()      # scan modules/tp/

TF_OPTIONS  = [{"label": t, "value": t} for t in ["M1","M5","M15","M30","H1","H4","D1"]]
HTF_OPTIONS = [{"label": t, "value": t} for t in ["M15","M30","H1","H4","D1"]]


# ── Card ──────────────────────────────────────────────────────────────────────

def card(key: str, title: str, icon: str, children) -> html.Div:
    """Card với thanh gradient + tiêu đề + nội dung."""
    return html.Div([
        html.Div(style={
            "height": "4px",
            "background": CARD_GRADIENT.get(key, C["grad_entry"]),
            "borderRadius": "14px 14px 0 0",
        }),
        html.Div([
            html.Span(icon, style={"fontSize": "18px", "marginRight": "9px"}),
            html.Span(title, style={
                "fontSize": "13px", "fontWeight": "800",
                "letterSpacing": "1.2px", "textTransform": "uppercase",
                "color": C["text"],
            }),
        ], style={"padding": "14px 20px 10px", "display": "flex", "alignItems": "center"}),
        html.Hr(style={"margin": "0 20px", "borderColor": C["border"]}),
        html.Div(children, style={"padding": "16px 20px 20px"}),
    ], style={
        "background": C["white"],
        "borderRadius": "14px",
        "border": f"1px solid {C['border']}",
        "boxShadow": "0 2px 12px rgba(99,102,241,0.07), 0 1px 3px rgba(0,0,0,0.04)",
        "height": "100%",
        "fontFamily": FONT,
    })


# ── Module checklist ──────────────────────────────────────────────────────────

def module_checklist(check_id: str, modules: list[str], accent_color: str) -> dcc.Checklist:
    """Checklist hiện đại với accentColor theo màu nhóm."""
    return dcc.Checklist(
        id=check_id,
        options=[{"label": f"  {m}", "value": m} for m in modules],
        value=[],
        labelStyle={
            "display": "flex",
            "alignItems": "center",
            "padding": "6px 10px",
            "marginBottom": "3px",
            "borderRadius": "8px",
            "cursor": "pointer",
            "fontSize": "14px",
            "fontFamily": FONT,
        },
        inputStyle={
            "marginRight": "9px",
            "width": "16px",
            "height": "16px",
            "accentColor": accent_color,
            "cursor": "pointer",
            "flexShrink": "0",
        },
    )


# ── Sub label ─────────────────────────────────────────────────────────────────

def sub_label(text: str, color: str = None) -> html.Div:
    return html.Div(text, style={
        "fontSize": "12px", "fontWeight": "700",
        "color": color or C["muted"],
        "textTransform": "uppercase", "letterSpacing": "0.8px",
        "marginBottom": "8px",
        "fontFamily": FONT,
    })


# ── Stat card ─────────────────────────────────────────────────────────────────

def stat_card(label: str, val_id: str, default: str = "—",
              gradient: str = None) -> html.Div:
    return html.Div([
        html.Div(style={
            "height": "3px",
            "background": gradient or C["grad_results"],
            "borderRadius": "8px 8px 0 0",
        }),
        html.Div([
            html.Div(label, style={
                "fontSize": "11px", "fontWeight": "700", "color": C["muted"],
                "textTransform": "uppercase", "letterSpacing": "0.7px",
                "marginBottom": "7px", "fontFamily": FONT,
            }),
            html.Div(default, id=val_id, style={
                "fontSize": "24px", "fontWeight": "800",
                "color": C["text"], "lineHeight": "1.1",
                "fontFamily": FONT,
            }),
        ], style={"padding": "13px 16px 15px"}),
    ], style={
        "background": C["white"],
        "borderRadius": "10px",
        "border": f"1px solid {C['border']}",
        "boxShadow": "0 1px 8px rgba(99,102,241,0.07)",
    })


# ── Number input ──────────────────────────────────────────────────────────────

def num_input(input_id: str, value, prefix: str = "", suffix: str = "",
              width: str = "90px") -> html.Div:
    border = f"1px solid {C['border']}"
    base = {
        "padding": "7px 10px", "fontSize": "14px",
        "border": border, "outline": "none",
        "background": C["white"], "fontFamily": FONT,
    }
    tag = {
        "padding": "7px 10px", "background": "#f8fafc",
        "border": border, "fontSize": "13px",
        "color": C["muted"], "fontFamily": FONT,
    }
    children = []
    if prefix:
        children.append(html.Span(prefix, style={
            **tag, "borderRight": "none", "borderRadius": "8px 0 0 8px",
        }))
    inp_radius = ("0" if prefix and suffix
                  else ("0 8px 8px 0" if prefix else ("8px 0 0 8px" if suffix else "8px")))
    children.append(dcc.Input(id=input_id, type="number", value=value, style={
        **base,
        "width": width,
        "borderRadius": inp_radius,
        "borderLeft":  "none" if prefix else border,
        "borderRight": "none" if suffix else border,
    }))
    if suffix:
        children.append(html.Span(suffix, style={
            **tag, "borderLeft": "none", "borderRadius": "0 8px 8px 0",
        }))
    return html.Div(children, style={"display": "flex", "alignItems": "center"})
