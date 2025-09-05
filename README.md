# PDF Tools
## Quickstart (Windows • PyCharm)

1. **Open folder** `pdf-tools` in PyCharm (Open > choose this folder).
2. Create & activate a virtual env, then:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   python app.py
   ```
   Then open http://127.0.0.1:8000

### App config (easy to tweak)

Edit `config.py` (or set env vars):

- `MAX_UPLOAD_MB` (default **50**) — request size limit
- Allowed types are currently `{".pdf"}`
