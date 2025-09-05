import io
import os
import tempfile
from typing import List

from flask import Blueprint, render_template, request, abort, current_app, send_file
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader, PdfWriter

bp = Blueprint("remove", __name__, template_folder="../templates")

def _is_pdf(filename: str) -> bool:
    return os.path.splitext(filename.lower())[1] == ".pdf"

@bp.get("/")
def remove_page():
    max_mb = int(current_app.config.get("MAX_UPLOAD_MB", 50))
    return render_template("remove.html", MAX_MB=max_mb)

@bp.post("/api/remove")
def api_remove():
    file = request.files.get("file")
    if not file or file.filename == "":
        abort(400, "No PDF uploaded.")
    if not _is_pdf(file.filename):
        abort(400, "Only PDF files are supported.")

    # Which pages to remove (0-based)
    payload = request.form.get("remove")
    if not payload:
        abort(400, "Missing 'remove' list.")
    try:
        import json
        remove_list: List[int] = list(map(int, json.loads(payload)))
    except Exception:
        abort(400, "Invalid 'remove' payload.")
    remove_set = set(remove_list)

    # Basic size guard
    max_len = current_app.config.get("MAX_CONTENT_LENGTH", 50 * 1024 * 1024)
    if file.content_length and file.content_length > max_len:
        abort(413, "Upload too large.")

    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, secure_filename(file.filename))
        file.save(path)

        reader = PdfReader(path)
        if reader.is_encrypted:
            try:
                reader.decrypt("")  # try empty password
            except Exception:
                abort(400, "This PDF is encrypted and cannot be processed.")

        writer = PdfWriter()
        total = len(reader.pages)
        for i in range(total):
            if i not in remove_set:
                writer.add_page(reader.pages[i])

        if len(writer.pages) == 0:
            abort(400, "All pages would be removed. Please leave at least one page.")

        bio = io.BytesIO()
        writer.write(bio)
        bio.seek(0)

        base = os.path.splitext(os.path.basename(file.filename))[0]
        outname = f"{base}_pages_removed.pdf"
        return send_file(
            bio,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=outname,
            max_age=0,
        )
