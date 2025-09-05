import os
import sys
import base64
import socket
import threading
from contextlib import closing

import webview
from app import app


class Bridge:
    def save_file(self, filename: str, data_url: str):
        """
        Receives a data: URL from the web UI and opens a native Save dialog.
        Saves the bytes to the chosen path. Returns a small result dict.
        """
        try:
            if "," not in data_url:
                return {"ok": False, "error": "Invalid data URL"}
            _, b64 = data_url.split(",", 1)
            data = base64.b64decode(b64)

            ext = (os.path.splitext(filename)[1] or "").lower()
            base_filters = []
            if ext == ".pdf":
                base_filters = [("PDF (*.pdf)", "*.pdf")]
            elif ext == ".docx":
                base_filters = [("Word Document (*.docx)", "*.docx")]
            elif ext == ".png":
                base_filters = [("PNG Image (*.png)", "*.png")]
            elif ext == ".jpg" or ext == ".jpeg":
                base_filters = [("JPEG Image (*.jpg;*.jpeg)", "*.jpg;*.jpeg")]
            base_filters.append(("All files (*.*)", "*.*"))

            if sys.platform == "darwin":
                mac_filters = []
                for desc, pattern in base_filters:
                    if pattern == "*.*":
                        continue
                    first = pattern.split(";")[0].replace("*.", "").replace(".", "")
                    mac_filters.append((desc, first))
                filters = tuple(mac_filters) if mac_filters else None
            else:
                filters = tuple(base_filters)

            win = webview.windows[0]

            try:
                path = win.create_file_dialog(
                    webview.SAVE_DIALOG,
                    save_filename=filename,
                    file_types=filters,
                )
            except Exception:
                path = win.create_file_dialog(
                    webview.SAVE_DIALOG,
                    save_filename=filename,
                )

            if not path:
                return {"ok": False, "cancelled": True}
            if isinstance(path, (list, tuple)):
                path = path[0]

            with open(path, "wb") as f:
                f.write(data)
            return {"ok": True, "path": path}
        except Exception as e:
            return {"ok": False, "error": str(e)}


def get_free_port():
    with closing(socket.socket()) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def run_flask(port):
    app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False, threaded=True)


if __name__ == "__main__":
    port = get_free_port()
    t = threading.Thread(target=run_flask, args=(port,), daemon=True)
    t.start()

    bridge = Bridge()
    webview.create_window(
        "PDF Tools",
        f"http://127.0.0.1:{port}",
        width=1200,
        height=800,
        resizable=True,
        js_api=bridge,
    )
    webview.start()
