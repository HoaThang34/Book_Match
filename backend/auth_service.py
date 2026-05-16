import bcrypt
from flask import current_app
from sqlalchemy.exc import IntegrityError

from backend.extensions import db
from backend.models import User
from backend.validators import (
    normalize_email,
    validate_email,
    validate_full_name,
    validate_password,
)


def hash_password(password: str) -> str:
    rounds = current_app.config["BCRYPT_ROUNDS"]
    salt = bcrypt.gensalt(rounds=rounds)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(
            password.encode("utf-8"), password_hash.encode("utf-8")
        )
    except (ValueError, TypeError):
        return False


def register_user(email: str, password: str, full_name: str) -> tuple[User | None, str | None]:
    email = normalize_email(email)
    full_name = full_name.strip()

    for validator, value in (
        (validate_email, email),
        (validate_full_name, full_name),
        (lambda p: validate_password(p, current_app.config["PASSWORD_MIN_LENGTH"]), password),
    ):
        error = validator(value)
        if error:
            return None, error

    user = User(
        email=email,
        password_hash=hash_password(password),
        full_name=full_name,
    )
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return None, "Email đã được sử dụng."
    return user, None


def authenticate_user(email: str, password: str) -> User | None:
    email = normalize_email(email)
    if validate_email(email):
        return None

    user = User.query.filter_by(email=email, is_active=True).first()
    if not user or not verify_password(password, user.password_hash):
        return None
    return user
