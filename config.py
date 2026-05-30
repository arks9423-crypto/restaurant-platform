import os

def _fix_db_url(url):
    # Railway provides postgres:// but SQLAlchemy requires postgresql+psycopg2://
    if url and url.startswith("postgres://"):
        url = "postgresql+psycopg2://" + url[len("postgres://"):]
    elif url and url.startswith("postgresql://"):
        url = "postgresql+psycopg2://" + url[len("postgresql://"):]
    return url


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    _db_url = os.environ.get("DATABASE_URL",
                              f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'platform.db')}")
    SQLALCHEMY_DATABASE_URI = _fix_db_url(_db_url)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # On Railway: mount a volume at /app/static/uploads and set UPLOAD_FOLDER env var
    UPLOAD_FOLDER = os.environ.get(
        "UPLOAD_FOLDER",
        os.path.join(BASE_DIR, "static", "uploads")
    )
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

    SUPER_ADMIN_USERNAME = os.environ.get("SUPER_ADMIN_USERNAME", "superadmin")
    SUPER_ADMIN_PASSWORD = os.environ.get("SUPER_ADMIN_PASSWORD", "super123")

    VAPID_PRIVATE_KEY = os.environ.get("VAPID_PRIVATE_KEY", "")
    VAPID_PUBLIC_KEY = os.environ.get("VAPID_PUBLIC_KEY", "")
    VAPID_EMAIL = os.environ.get("VAPID_EMAIL", "admin@qrmenu.app")

    PORT = int(os.environ.get("PORT", 5000))
