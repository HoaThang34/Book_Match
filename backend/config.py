import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")


def _require(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Thiếu biến môi trường bắt buộc: {name}")
    return value


def _resolve_database_uri() -> str:
    """Chuẩn hóa SQLite thành đường dẫn tuyệt đối (tránh Flask-SQLAlchemy gắn instance/)."""
    url = os.getenv("DATABASE_URL")
    if not url:
        db_file = ROOT_DIR / "data" / "app.db"
    elif url.startswith("sqlite:///"):
        if ":memory:" in url:
            return url
        db_file = Path(url.removeprefix("sqlite:///"))
        if not db_file.is_absolute():
            db_file = ROOT_DIR / db_file
    else:
        return url

    db_file = db_file.resolve()
    db_file.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{db_file.as_posix()}"


class Config:
    SECRET_KEY = _require("SECRET_KEY")
    JWT_SECRET_KEY = _require("JWT_SECRET_KEY")

    SQLALCHEMY_DATABASE_URI = _resolve_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        minutes=int(os.getenv("JWT_ACCESS_EXPIRE_MINUTES", "15"))
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        days=int(os.getenv("JWT_REFRESH_EXPIRE_DAYS", "7"))
    )
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_COOKIE_SECURE = os.getenv("JWT_COOKIE_SECURE", "false").lower() == "true"
    JWT_COOKIE_HTTPONLY = True
    JWT_COOKIE_SAMESITE = os.getenv("JWT_COOKIE_SAMESITE", "Lax")
    JWT_CSRF_IN_COOKIES = True
    JWT_CSRF_METHODS = ["POST", "PUT", "PATCH", "DELETE"]

    CORS_ORIGINS = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "http://127.0.0.1:5000,http://localhost:5000").split(",")
        if origin.strip()
    ]

    PASSWORD_MIN_LENGTH = int(os.getenv("PASSWORD_MIN_LENGTH", "8"))
    BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS", "12"))

    RATELIMIT_DEFAULT = os.getenv("RATELIMIT_DEFAULT", "120 per hour")
    RATELIMIT_AUTH = os.getenv("RATELIMIT_AUTH", "10 per minute")

    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", "16384"))
