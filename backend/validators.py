import re
from typing import Optional

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
DISALLOWED_NAME = re.compile(r"[<>\"'`;]")

PASSWORD_RULES = [
    (re.compile(r".{8,}"), "Mật khẩu phải có ít nhất 8 ký tự."),
    (re.compile(r"[A-Z]"), "Mật khẩu phải có ít nhất một chữ hoa."),
    (re.compile(r"[a-z]"), "Mật khẩu phải có ít nhất một chữ thường."),
    (re.compile(r"\d"), "Mật khẩu phải có ít nhất một chữ số."),
]


def normalize_email(email: str) -> str:
    return email.strip().lower()


def validate_email(email: str) -> Optional[str]:
    if not email or len(email) > 255:
        return "Email không hợp lệ."
    if not EMAIL_RE.match(email):
        return "Email không hợp lệ."
    return None


def validate_full_name(name: str) -> Optional[str]:
    name = (name or "").strip()
    if len(name) < 2 or len(name) > 120:
        return "Họ tên phải từ 2 đến 120 ký tự."
    if DISALLOWED_NAME.search(name):
        return "Họ tên chứa ký tự không được phép."
    return None


def validate_password(password: str, min_length: int = 8) -> Optional[str]:
    if not password or len(password) > 128:
        return "Mật khẩu không hợp lệ."
    if len(password) < min_length:
        return f"Mật khẩu phải có ít nhất {min_length} ký tự."
    for pattern, message in PASSWORD_RULES:
        if not pattern.search(password):
            return message
    return None
