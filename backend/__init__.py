from pathlib import Path

from flask import Flask, abort, render_template
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

from backend.ai_routes import ai_bp
from backend.auth_routes import auth_bp, register_jwt_handlers
from backend.config import ROOT_DIR
from backend.extensions import db, jwt, limiter
from backend.seed_data import seed_catalog
from backend.user_routes import user_bp

ALLOWED_PAGES = {
    "index",
    "welcome",
    "login",
    "signup",
    "home",
    "timer",
    "mission",
    "streak",
}


def create_app() -> Flask:
    from backend.config import Config

    app = Flask(
        __name__,
        template_folder=str(ROOT_DIR / "template"),
        static_folder=str(ROOT_DIR / "static"),
    )
    app.config.from_object(Config)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)

    db.init_app(app)
    jwt.init_app(app)
    register_jwt_handlers(jwt)

    limiter.init_app(app)
    limiter.enabled = True
    limiter.storage_uri = "memory://"

    CORS(
        app,
        origins=app.config["CORS_ORIGINS"],
        supports_credentials=True,
    )

    app.register_blueprint(auth_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(user_bp)

    _register_security_headers(app)
    _register_routes(app)

    with app.app_context():
        from sqlalchemy import event
        @event.listens_for(db.engine, "connect")
        def _set_sqlite_pragma(dbapi_connection, _connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.close()
        db.create_all()
        seed_catalog()

    return app


def _register_security_headers(app: Flask) -> None:
    @app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        if app.config.get("JWT_COOKIE_SECURE"):
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )
        return response


def _register_routes(app: Flask) -> None:
    @app.get("/")
    def index():
        return render_template("welcome.html")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/<page>.html")
    def html_page(page: str):
        if page not in ALLOWED_PAGES:
            abort(404)
        return render_template(f"{page}.html")
