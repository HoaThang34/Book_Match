# Tổng quan Backend – AI Reader

## Mục đích

Backend Python phục vụ xác thực, gamification (nhiệm vụ, chuỗi ngày), và gợi ý sách qua Ollama cho ứng dụng AI Reader.

## Công nghệ

| Thành phần | Công nghệ |
|------------|-----------|
| Framework | Flask 3 |
| CSDL | SQLite (SQLAlchemy) |
| Mật khẩu | bcrypt |
| Phiên đăng nhập | JWT trong HttpOnly cookie |
| Giới hạn tần suất | Flask-Limiter |
| AI gợi ý sách | Ollama (HTTP local) |

## Cấu trúc thư mục

```
backend/
  __init__.py      # Factory ứng dụng, route HTML
  config.py        # Đọc biến môi trường (.env)
  extensions.py    # db, jwt, limiter
  models.py        # User, profile, missions, streak
  auth_routes.py   # API /api/auth/*
  ai_routes.py     # API /api/ai/*
  user_routes.py   # API /api/user/* (missions, timer, streak)
  ollama_service.py
  ai_service.py
  gamification_service.py
  seed_data.py
  auth_service.py
  validators.py
static/js/
  api.js, app.js   # Gọi API từ trang HTML
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

| GET | `/api/ai/recommendations` | Gợi ý sách (JWT) |
| GET/PUT | `/api/user/profile` | Khảo sát người dùng |
| GET | `/api/user/missions` | Nhiệm vụ, thử thách, danh hiệu |
| GET | `/api/user/streak` | Chuỗi ngày + lịch |
| POST | `/api/user/timer/complete` | Hoàn thành phiên Focus |

Xem thêm: [auth-api.md](./auth-api.md), [ollama-ai.md](./ollama-ai.md), [security.md](./security.md).
