# PDF Tools

Lightweight PDF utilities (Convert to DOCX, Merge PDFs, Remove Pages) built with Flask + PDF.js.  
Runs in the browser **or** as a desktop app (via PyWebView). Ships as a single `.exe`.

---

## Requirements (Windows)

- Python 3.10+ (64-bit recommended)

---

## Quick Start (Browser)

```powershell
# 1) Create and activate a venv
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2) Install deps
pip install -r requirements.txt

# 3) Run Flask (browser mode)
python app.py
````

Open: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## Quick Start (Desktop App)

```powershell
# venv should be active and requirements installed
python run_desktop.py
```

This launches a native window that wraps the local Flask server.
Downloads will prompt you for a save location in the desktop app; in the browser they auto-download.

---

## Build a Single-File EXE (PyInstaller) (PowerShell)

```powershell
pyinstaller `
  --noconfirm `
  --clean `
  --onefile `
  --windowed `
  --name "PDF Tools" `
  --icon "static\img\logo.ico" `
  --add-data "templates;templates" `
  --add-data "static;static" `
  run_desktop.py
```

Output: `dist\PDF Tools.exe`
Share that file, no Python required on the target machine.

---

## Config

Edit `config.py` (or env vars) to tweak limits:

* `MAX_UPLOAD_MB` — default **50**
* Allowed extensions are `[".pdf"]`

