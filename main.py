"""
CCREC Grant Level Dashboard - Entry Point.
Loads data, initializes the Dash application, and starts the server.
"""

print('- Starting CCREC Dashboard')
print('- A folder selection window may appear. Please select your data folder.')
print('- Please be patient, loading may take a minute or two.')

import socket
import threading
import time

import webview
from dash import Dash

from data_service import DashboardData
from callbacks import register_callbacks
import components

def get_free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]

def wait_for_server(port: int, timeout: float = 10):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                return
        except OSError:
            time.sleep(0.1)
    raise RuntimeError("Dash server failed to start")

def create_app(port):
    data = DashboardData()
    app = Dash(__name__, suppress_callback_exceptions=True)
    app.title = 'CCREC Dashboard'
    app.layout = components.get_app_layout()
    register_callbacks(app, data)
    app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)

if __name__ == "__main__":
    port = get_free_port()
    threading.Thread(target=create_app, args=(port,), daemon=True).start()
    wait_for_server(port)
    webview.create_window(
        "Grant Level Dashboard",
        f"http://127.0.0.1:{port}",
        width=1280,
        height=800,
    )
    webview.start()