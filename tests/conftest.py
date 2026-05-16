import os

import pytest

os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pytest-only-32chars")
os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret-key-for-pytest-32ch")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("RATELIMIT_AUTH", "1000 per minute")


@pytest.fixture
def app():
    from backend import create_app
    from backend.extensions import db

    application = create_app()
    application.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        RATELIMIT_AUTH="1000 per minute",
    )

    with application.app_context():
        db.drop_all()
        db.create_all()

    yield application

    with application.app_context():
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()
