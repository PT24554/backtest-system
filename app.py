"""
app.py
──────
Entry point của Backtest System.

Chạy:
    cd backtest_system
    python app.py

Sau đó mở trình duyệt: http://localhost:8050
"""

import dash
import dash_bootstrap_components as dbc

app = dash.Dash(
    __name__,
    title="Backtest System",
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        # Font tiếng Việt - Be Vietnam Pro
        "https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&display=swap",
    ],
    suppress_callback_exceptions=True,
)
server = app.server  # Expose Flask server nếu cần deploy

# Import layout sau khi app đã được tạo
from ui.layout import create_layout        # noqa: E402
from ui import callbacks  # noqa: E402, F401  (register callbacks)

app.layout = create_layout()


if __name__ == "__main__":
    print("─" * 50)
    print("  Backtest System đang khởi động...")
    print("  Mở trình duyệt: http://localhost:8050")
    print("─" * 50)
    app.run(debug=True, port=8050)
