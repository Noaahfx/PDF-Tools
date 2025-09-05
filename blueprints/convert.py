import io
import os
import tempfile
from flask import Blueprint, render_template, request, abort, current_app, send_file
from werkzeug.utils import secure_filename

from PyPDF2 import PdfReader, PdfWriter
from pdf2docx import Converter

bp = Blueprint("convert", __name__, template_folder="../templates")

def _allowed_file(filename: str) -> bool:
    _, ext = os.path.splitext(filename.lower())
    return ext in current_app.config.get("ALLOWED_EXTENSIONS", {".pdf"})

@bp.get("/")
def convert_page():
    return render_template("convert.html")

@bp.post("/api/convert")
def api_convert():
    if "file" not in request.files:
        abort(400, "No file part")

    f = request.files["file"]
    if f.filename == "":
        abort(400, "Empty filename")

    if not _allowed_file(f.filename):
        abort(400, "Only PDF files are supported")

    content_length = request.content_length or 0
    max_len = current_app.config.get("MAX_CONTENT_LENGTH", 50 * 1024 * 1024)
    if content_length > max_len:
        abort(413, "File too large")

    try:
        order = request.form.get("order")
        page_indices = []
        if order:
            import json
            page_indices = list(map(int, json.loads(order)))
    except Exception:
        abort(400, "Invalid page order")

    with tempfile.TemporaryDirectory() as tmpdir:
        pdf_path = os.path.join(tmpdir, secure_filename(f.filename))
        f.save(pdf_path)

        reordered_pdf_path = pdf_path
        if page_indices:
            reader = PdfReader(pdf_path)
            writer = PdfWriter()
            total = len(reader.pages)
            for i in page_indices:
                if i < 0 or i >= total:
                    abort(400, "Page index out of range")
                writer.add_page(reader.pages[i])
            reordered_pdf_path = os.path.join(tmpdir, "reordered.pdf")
            with open(reordered_pdf_path, "wb") as outp:
                writer.write(outp)

        docx_path = os.path.join(tmpdir, os.path.splitext(os.path.basename(pdf_path))[0] + "_converted.docx")
        try:
            cv = Converter(reordered_pdf_path)
            cv.convert(docx_path)
            cv.close()
        except Exception as e:
            abort(500, f"Conversion failed: {e}")

        with open(docx_path, "rb") as docxf:
            data = io.BytesIO(docxf.read())

        base = os.path.splitext(os.path.basename(f.filename))[0]
        download_name = f"{base}_converted.docx"

        return send_file(
            data,
            as_attachment=True,
            download_name=download_name,
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            max_age=0
        )
