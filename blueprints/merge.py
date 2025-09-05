import io
import os
import tempfile
from typing import List

from flask import Blueprint, render_template, request, abort, current_app, send_file
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader, PdfWriter

bp = Blueprint("merge", __name__, template_folder="../templates")

def _is_pdf(filename: str) -> bool:
    return os.path.splitext(filename.lower())[1] == ".pdf"

@bp.get("/")
def merge_page():
    max_files = int(current_app.config.get("MERGE_MAX_FILES", 10))
    max_mb = int(current_app.config.get("MAX_UPLOAD_MB", 50))
    return render_template("merge.html", MAX_FILES=max_files, MAX_MB=max_mb)

@bp.post("/api/merge")
def api_merge():
    files = request.files.getlist("files")
    if not files:
        abort(400, "No files uploaded")

    max_files = int(current_app.config.get("MERGE_MAX_FILES", 10))
    if len(files) > max_files:
        abort(400, f"Too many files. Max is {max_files}.")

    order = request.form.get("order")
    indices: List[int] = list(range(len(files)))
    if order:
        try:
            import json
            indices = list(map(int, json.loads(order)))
            if len(indices) != len(files):
                abort(400, "Order length mismatch")
        except Exception:
            abort(400, "Invalid order payload")

    total_bytes = sum([f.content_length or 0 for f in files])
    max_len = current_app.config.get("MAX_CONTENT_LENGTH", 50 * 1024 * 1024)
    if total_bytes and total_bytes > max_len:
        abort(413, "Total upload too large")

    with tempfile.TemporaryDirectory() as tmpdir:
        saved = []
        for i, f in enumerate(files):
            if f.filename == "" or not _is_pdf(f.filename):
                abort(400, "Only PDF files are supported")
            path = os.path.join(tmpdir, f"{i:03d}_" + secure_filename(f.filename))
            f.save(path)
            saved.append(path)

        writer = PdfWriter()

        for idx in indices:
            path = saved[idx]
            reader = PdfReader(path)
            if reader.is_encrypted:
                try:
                    reader.decrypt("")
                except Exception:
                    abort(400, f"'{os.path.basename(path)}' is encrypted and cannot be merged.")
            for page in reader.pages:
                writer.add_page(page)

        bio = io.BytesIO()
        writer.write(bio)
        bio.seek(0)

        if len(files) == 1:
            base = os.path.splitext(files[0].filename)[0] + "_merged.pdf"
        else:
            base = "merged.pdf"

        return send_file(
            bio,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=base,
            max_age=0,
        )