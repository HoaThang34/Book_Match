from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies,
)

from backend.auth_service import authenticate_user, register_user
from backend.extensions import db, limiter
from backend.models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

GENERIC_LOGIN_ERROR = "Email hoặc mật khẩu không đúng."


def _json_body() -> dict:
    if not request.is_json:
        return {}
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


def _auth_rate_limit():
    return current_app.config["RATELIMIT_AUTH"]


@auth_bp.post("/register")
@limiter.limit(_auth_rate_limit)
def register():
    data = _json_body()
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""
    full_name = (data.get("full_name") or "").strip()
    confirm_password = data.get("confirm_password") or ""

    if password != confirm_password:
        return jsonify({"error": "Mật khẩu xác nhận không khớp."}), 400

    user, error = register_user(email, password, full_name)
    if error:
        status = 409 if "đã được sử dụng" in error else 400
        return jsonify({"error": error}), status

    response = jsonify({"message": "Đăng ký thành công.", "user": user.to_public_dict()})
    _set_auth_cookies(response, user.id)
    return response, 201


@auth_bp.post("/login")
@limiter.limit(_auth_rate_limit)
def login():
    data = _json_body()
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""

    user = authenticate_user(email, password)
    if not user:
        return jsonify({"error": GENERIC_LOGIN_ERROR}), 401

    response = jsonify({"message": "Đăng nhập thành công.", "user": user.to_public_dict()})
    _set_auth_cookies(response, user.id)
    return response


@auth_bp.post("/logout")
@jwt_required()
def logout():
    response = jsonify({"message": "Đã đăng xuất."})
    unset_jwt_cookies(response)
    return response


@auth_bp.get("/me")
@jwt_required()
def me():
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user or not user.is_active:
        return jsonify({"error": "Phiên đăng nhập không hợp lệ."}), 401
    return jsonify({"user": user.to_public_dict()})


@auth_bp.get("/csrf")
def csrf_token():
    """Trả về CSRF token (đã được Flask-JWT-Extended gắn vào cookie khi cần)."""
    return jsonify({"message": "CSRF cookie đã sẵn sàng."})


def _set_auth_cookies(response, user_id: int):
    access = create_access_token(identity=str(user_id))
    refresh = create_refresh_token(identity=str(user_id))
    set_access_cookies(response, access)
    set_refresh_cookies(response, refresh)


def register_jwt_handlers(jwt_manager):
    @jwt_manager.unauthorized_loader
    def unauthorized_callback(_reason):
        return jsonify({"error": "Yêu cầu đăng nhập."}), 401

    @jwt_manager.invalid_token_loader
    def invalid_token_callback(_reason):
        return jsonify({"error": "Token không hợp lệ."}), 401

    @jwt_manager.expired_token_loader
    def expired_token_callback(_jwt_header, _jwt_payload):
        return jsonify({"error": "Phiên đăng nhập đã hết hạn."}), 401
