# Tổng quan Backend – Book Match

## Mục đích

Backend Python phục vụ xác thực, gamification (nhiệm vụ, chuỗi ngày), và gợi ý sách qua Ollama cho ứng dụng Book Match.

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
  ai_routes.py     # API /api/ai/* (trả về recommendations + comment)
  user_routes.py   # API /api/user/* (missions, timer, streak)
  ollama_service.py
  ai_service.py    # System prompt + build_recommendation (trả dict có comment)
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

| GET | `/api/ai/recommendations` | Gợi ý sách (JWT) – trả `recommendations[]` + `comment` |
| GET/PUT | `/api/user/profile` | Khảo sát người dùng (age, interests, mood) |
| GET | `/api/user/missions` | Nhiệm vụ, thử thách, danh hiệu |
| GET | `/api/user/streak` | Chuỗi ngày + lịch |
| POST | `/api/user/timer/complete` | Hoàn thành phiên Focus |

## Luồng khảo sát & đề xuất AI

```
[index.html] → Điền tuổi/sở thích/tâm trạng → Nhấn "Nhận đề xuất từ AI"
    → PUT /api/user/profile (lưu DB)
    → localStorage: survey_profile + ai_needs_refresh=1
    → Redirect → [home.html]

[home.html] (khởi động):
    → Nếu ai_needs_refresh=1: GET /api/ai/recommendations → lưu cache localStorage
    → Nếu có cache: hiển thị từ cache (không gọi lại AI mỗi lần)
    → Nếu không có gì: hiển thị prompt "Hãy điền khảo sát"
    → Nút "Chỉnh sửa" → quay lại [index.html] (form tự điền từ localStorage)
```

**AI Response mẫu** (`/api/ai/recommendations`):
```json
{
  "comment": "Nhận xét ngắn về hồ sơ đọc của người dùng...",
  "recommendations": [
    {
      "title": "Tên sách",
      "author": "Tác giả",
      "description": "Mô tả 2-3 câu",
      "match_percent": 92,
      "why_fit": "Lý do phù hợp",
      "cover_keyword": "book cover modern"
    }
  ]
}
```

Xem thêm: [auth-api.md](./auth-api.md), [ollama-ai.md](./ollama-ai.md), [security.md](./security.md).
