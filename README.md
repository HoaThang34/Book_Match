# AI Reader

Nền tảng đọc sách thông minh tích hợp AI (Ollama), giúp cá nhân hóa gợi ý sách, xây dựng thói quen đọc qua gamification và duy trì tập trung với Pomodoro timer.

## Tính năng

- **Gợi ý sách AI** — Phân tích sở thích, tâm trạng, thói quen để đề xuất sách phù hợp qua Ollama local
- **Khảo sát người dùng** — Thu thập tuổi, sở thích, tâm trạng để cá nhân hóa
- **Nhiệm vụ & Thử thách** — 10 nhiệm vụ hàng ngày/tuần + 3 thử thách dài hạn + 6 danh hiệu
- **Focus Timer** — Đồng hồ đếm ngược Pomodoro, tự động ghi nhận khi hoàn thành
- **Chuỗi đọc (Streak)** — Lịch đọc theo tháng, thống kê và mốc mục tiêu
- **Xác thực JWT** — Đăng ký/đăng nhập với HttpOnly cookie, CSRF protection
- **Bảo mật** — bcrypt, rate limiting, security headers, generic login errors

## Kiến trúc

```
AI Reader
├── backend/           # Flask API (Python)
│   ├── auth_routes.py, auth_service.py, validators.py
│   ├── ai_routes.py, ai_service.py, ollama_service.py
│   ├── user_routes.py, gamification_service.py
│   ├── models.py, config.py, extensions.py, seed_data.py
├── template/          # 8 giao diện HTML (Tailwind CSS)
├── static/js/         # Vanilla JS (api.js, app.js, auth.js)
├── docs/              # Tài liệu chi tiết
├── tests/             # pytest (conftest.py, test_auth_security.py)
└── data/              # SQLite DB (tự sinh)
```

Chi tiết kiến trúc backend: [docs/backend-overview.md](docs/backend-overview.md)

## Công nghệ

| Thành phần | Công nghệ |
|---|---|
| Framework | Flask 3 |
| CSDL | SQLite (SQLAlchemy) — dùng PostgreSQL cho production |
| Xác thực | JWT trong HttpOnly cookie |
| Mật khẩu | bcrypt (cost 12) |
| Rate limiting | Flask-Limiter (memory, dùng Redis cho production) |
| AI | Ollama API (`/api/chat`) local |
| Frontend | Vanilla JS, Tailwind CSS (CDN), Material Symbols |

## Bắt đầu nhanh

1. **Clone & cài đặt**
   ```
   pip install -r requirements.txt
   ```

2. **Cấu hình môi trường**
   ```
   cp .env.example .env
   ```
   Sửa `SECRET_KEY` và `JWT_SECRET_KEY` thành chuỗi ngẫu nhiên ≥ 32 ký tự.

3. **Chạy Ollama** (nếu dùng AI recommendations)
   ```
   ollama pull <model>   # mặc định: gemma4:31b-cloud
   ollama serve
   ```

4. **Khởi động**
   ```
   python run.py
   ```
   Truy cập `http://127.0.0.1:5000`

## API

### Hệ thống
| Method | Path | Mô tả |
|---|---|---|
| GET | `/health` | Kiểm tra server |
| GET | `/<trang>.html` | Phục vụ giao diện |

### Xác thực
| Method | Path | Mô tả |
|---|---|---|
| POST | `/api/auth/register` | Đăng ký |
| POST | `/api/auth/login` | Đăng nhập |
| POST | `/api/auth/logout` | Đăng xuất |
| GET | `/api/auth/me` | Thông tin user hiện tại |
| POST | `/api/auth/refresh` | Làm mới access token |

Chi tiết: [docs/auth-api.md](docs/auth-api.md)

### Gamification
| Method | Path | Mô tả |
|---|---|---|
| GET | `/api/user/profile` | Khảo sát người dùng |
| PUT | `/api/user/profile` | Cập nhật khảo sát |
| GET | `/api/user/missions` | Nhiệm vụ, thử thách, danh hiệu |
| GET | `/api/user/stats` | Thống kê đọc |
| GET | `/api/user/streak` | Chuỗi ngày + lịch |
| POST | `/api/user/timer/complete` | Hoàn thành phiên Focus |

Chi tiết: [docs/gamification-api.md](docs/gamification-api.md)

### AI Recommendations
| Method | Path | Mô tả |
|---|---|---|
| GET | `/api/ai/recommendations` | 3 đề xuất sách |
| POST | `/api/ai/recommendations/refresh` | Đề xuất mới (tránh sách cũ) |

Chi tiết: [docs/ollama-ai.md](docs/ollama-ai.md)

## Bảo mật

- **Mật khẩu**: bcrypt, không log/trả về plaintext
- **JWT**: HttpOnly cookie, SameSite=Lax, CSRF protection, access token 15 phút
- **Rate limit**: 10 req/phút cho auth endpoints
- **Input validation**: email, password strength, full name sanitize
- **Security headers**: X-Frame-Options, X-Content-Type-Options, HSTS (khi HTTPS)

Chi tiết: [docs/security.md](docs/security.md)

## Kiểm thử

```bash
pytest tests/ -v
```

## Luồng người dùng

```
Welcome → Đăng ký → Khảo sát (tuổi/sở thích/tâm trạng)
  → AI gợi ý 3 cuốn sách → Duyệt nhiệm vụ → Chọn nhiệm vụ
    → Focus Timer → Hoàn thành → Ghi nhận streak + XP → Mở khóa danh hiệu
```

## Biến môi trường

Xem [.env.example](.env.example) cho tất cả biến. Bắt buộc: `SECRET_KEY`, `JWT_SECRET_KEY`.

## Giấy phép

MIT
