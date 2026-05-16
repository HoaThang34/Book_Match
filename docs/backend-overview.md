# Tổng quan Backend – AI Reader

## Mục đích

Backend Python phục vụ xác thực người dùng (đăng ký, đăng nhập) cho ứng dụng AI Reader.

## Công nghệ

| Thành phần | Công nghệ |
|------------|-----------|
| Framework | Flask 3 |
| CSDL | SQLite (SQLAlchemy) |
| Mật khẩu | bcrypt |
| Phiên đăng nhập | JWT trong HttpOnly cookie |
| Giới hạn tần suất | Flask-Limiter |

## Cấu trúc thư mục

```
backend/
  __init__.py      # Factory ứng dụng, route HTML
  config.py        # Đọc biến môi trường (.env)
  extensions.py    # db, jwt, limiter
  models.py        # Model User
  auth_routes.py   # API /api/auth/*
  auth_service.py  # Logic đăng ký / đăng nhập
  validators.py    # Kiểm tra email, mật khẩu
run.py             # Điểm chạy chính
static/js/auth.js  # Gọi API từ form HTML
template/          # Giao diện HTML
data/              # File SQLite (tự tạo, gitignore)
docs/              # Tài liệu backend
```

## Chạy cục bộ

1. Sao chép `.env.example` → `.env` và đặt `SECRET_KEY`, `JWT_SECRET_KEY` ngẫu nhiên (≥ 32 ký tự).
2. Cài dependency: `pip install -r requirements.txt`
3. Chạy: `python run.py`
4. Truy cập: `http://127.0.0.1:5000/login.html`

## Biến môi trường

Chi tiết từng biến xem trong file `.env.example`. Các biến bắt buộc:

- `SECRET_KEY` – Flask session / bảo mật chung
- `JWT_SECRET_KEY` – Ký JWT (phải khác `SECRET_KEY`)

## Endpoint hệ thống

| Method | Path | Mô tả |
|--------|------|--------|
| GET | `/health` | Kiểm tra server |
| GET | `/<trang>.html` | Phục vụ giao diện tĩnh qua Flask |

Xem thêm: [auth-api.md](./auth-api.md), [security.md](./security.md).
