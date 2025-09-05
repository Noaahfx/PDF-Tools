import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")
    MAX_UPLOAD_MB = int(os.environ.get("MAX_UPLOAD_MB", 50))
    MAX_CONTENT_LENGTH = MAX_UPLOAD_MB * 1024 * 1024
    ALLOWED_EXTENSIONS = {".pdf"}
